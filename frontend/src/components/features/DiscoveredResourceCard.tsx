
import type { DiscoveredResource } from '../../services/api'

const CATEGORY_LABELS: Record<string, string> = {
    service_support: '🏢 Service d\'aide',
    procedure_plateforme: '🌐 Procédure plateforme',
    signalement_autorite: '🏛️ Signalement autorité',
}

const BADGE = {
    blue: 'px-2 py-0.5 text-xs font-medium rounded-full bg-blue-100 text-blue-800',
    yellow: 'px-2 py-0.5 text-xs font-medium rounded-full bg-yellow-100 text-yellow-800',
    purple: 'px-2 py-0.5 text-xs font-medium rounded-full bg-purple-100 text-purple-800',
    gray: 'px-2 py-0.5 text-xs font-medium rounded-full bg-gray-100 text-gray-600',
} as const

interface DiscoveredResourceCardProps {
    resource: DiscoveredResource
}

export function DiscoveredResourceCard({ resource }: DiscoveredResourceCardProps) {
    const isDuplicate = resource.is_new === false

    return (
        <div className={`rounded-lg border px-4 py-2.5 ${isDuplicate
            ? 'bg-yellow-50 border-yellow-200'
            : 'bg-white border-gray-200'
            }`}>

            {/* Ligne 1 : nom + site */}
            <div className="flex items-center gap-2 flex-wrap">
                <span className="font-medium text-gray-900 text-sm break-words">
                    {resource.organization_name}
                </span>
                {resource.website && (
                    <a href={resource.website} target="_blank" rel="noopener noreferrer"
                        className="text-blue-600 hover:text-blue-800 text-xs truncate max-w-[220px]">
                        🔗 {resource.website}
                    </a>
                )}
            </div>

            {/* Ligne 2 : pays + catégorie + statut */}
            <div className="flex items-center gap-2 mt-1.5 flex-wrap">
                {resource.country_name && (
                    <span className={BADGE.gray}>
                        {resource.country_name}
                    </span>
                )}
                <span className={BADGE.purple}>
                    {CATEGORY_LABELS[resource.category] ?? resource.category}
                </span>
                {resource.is_new === true && <span className={BADGE.blue}>🆕 Nouveau</span>}
                {resource.is_new === false && <span className={BADGE.yellow}>⚠️ Doublon</span>}
            </div>

            {/* Raison du doublon — uniquement si doublon */}
            {isDuplicate && resource.duplicate_reason && (
                <p className="text-xs text-yellow-700 mt-1">
                    ↳ Doublon : {resource.duplicate_reason}
                </p>
            )}
        </div>
    )
}
