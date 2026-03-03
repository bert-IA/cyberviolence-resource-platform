import type { Resource } from '../../services/api'
import { ExpandableText } from '../ui/ExpandableText'

interface ResourceCardProps {
    resource: Resource
    children?: React.ReactNode
}

// A) Classes complètes par couleur — Tailwind détecte les strings statiques, pas les templates dynamiques
const BADGE = {
    green: 'px-2 py-0.5 text-xs font-medium rounded-full bg-green-100 text-green-800',
    yellow: 'px-2 py-0.5 text-xs font-medium rounded-full bg-yellow-100 text-yellow-800',
    blue: 'px-2 py-0.5 text-xs font-medium rounded-full bg-blue-100 text-blue-800',
    purple: 'px-2 py-0.5 text-xs font-medium rounded-full bg-purple-100 text-purple-800',
} as const

export function ResourceCard({ resource, children }: ResourceCardProps) {
    return (
        <div className="bg-white rounded-lg shadow-md p-3 mb-2 hover:shadow-lg transition-shadow">

            {/* ── Ligne 1 : Nom + badges ── */}
            <div className="flex justify-between items-start mb-2">
                <h3 className="text-lg font-semibold text-gray-900 break-words min-w-0 mr-3">
                    {resource.organization_name}
                </h3>
                <div className="flex flex-wrap justify-end items-center gap-2 shrink-0">
                    {resource.country_name && (
                        <span className="text-sm text-gray-600">🌍 {resource.country_name}</span>
                    )}
                    <span className={BADGE.purple}>{resource.category}</span>
                    {/* D) Garde === true/false : évite le faux positif pour is_new=null */}
                    {resource.is_new === true && <span className={BADGE.blue}>🆕 Nouveau</span>}
                    {resource.is_new === false && <span className={BADGE.yellow}>⚠️ Doublon</span>}
                </div>
            </div>

            {/* ── Ligne 2 : Contact ── */}
            {(resource.website || resource.phone) && (
                <div className="flex flex-wrap gap-4 text-sm mb-2">
                    {resource.website && (
                        <a href={resource.website} target="_blank" rel="noopener noreferrer"
                            className="text-blue-600 hover:text-blue-800 truncate max-w-xs">
                            🔗 {resource.website}
                        </a>
                    )}
                    {resource.phone && <span className="text-gray-700">📞 {resource.phone}</span>}
                    <span className={resource.is_governmental ? BADGE.green : BADGE.yellow}>
                        {resource.is_governmental ? 'gouvernemental' : 'non gouvernemental'}
                    </span>
                    <span className={resource.scope_anonymous ? BADGE.green : BADGE.yellow}>
                        {resource.scope_anonymous ? 'anonyme' : 'non anonyme'}
                    </span>
                </div>
            )}

            {(resource.scope_audience || resource.scope_violence || resource.scope_signalement) && (
                <div className="flex flex-wrap gap-x-6 gap-y-1 text-sm text-gray-700 mb-2">
                    {resource.scope_audience && (
                        <span><span className="font-semibold">Public : </span>{resource.scope_audience}</span>
                    )}
                    {resource.scope_violence && (
                        <span><span className="font-semibold">Lutte contre : </span>{resource.scope_violence}</span>
                    )}
                    {resource.scope_signalement && (
                        <span><span className="font-semibold">Signalement : </span>{resource.scope_signalement}</span>
                    )}
                </div>
            )}

            {/* Lien direct — uniquement pour signalement_autorite */}
            {resource.category === 'signalement_autorite' && resource.direct_link && (
                <div className="text-sm mb-2">
                    <span className="font-semibold text-gray-700">Lien direct : </span>
                    <a href={resource.direct_link} target="_blank" rel="noopener noreferrer"
                        className="text-blue-600 hover:text-blue-800 break-all">
                        🔗 {resource.direct_link}
                    </a>
                </div>
            )}

            {/* ── Description ── */}
            <div className="text-sm text-gray-700 mt-1">
                <ExpandableText text={resource.description} maxLength={150} />
            </div>

            {/* ── Actions (children) ── */}
            {children && (
                <div className="flex gap-2 pt-3 mt-2 border-t border-gray-200">
                    {children}
                </div>
            )}
        </div>
    )
}