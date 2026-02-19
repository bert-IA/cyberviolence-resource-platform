import type { Resource } from '../../services/api'
import { ExpandableText } from '../ui/ExpandableText'

interface ResourceCardProps {
    resource: Resource
    children?: React.ReactNode  // Pour les boutons d'action
}

export function ResourceCard({ resource, children }: ResourceCardProps) {
    return (
        <div className="bg-white rounded-lg shadow-md p-6 mb-4 hover:shadow-lg transition-shadow">
            {/* Header avec nom et badge status */}
            <div className="flex justify-between items-start">
                <h3 className="text-lg font-semibold text-gray-900">
                    {resource.name}
                </h3>

                <span className="px-3 py-1 text-xs font-medium rounded-full bg-purple-100 text-purple-800">
                    {resource.category}
                </span>
            </div>
            <div className="flex justify-between items-start mb-4">
                {resource.url && (
                    <a href={resource.url} target="_blank" rel="noopener noreferrer"
                        className="text-blue-600 hover:text-blue-800 text-sm">
                        🔗 Voir le site officiel ({resource.url})
                    </a>
                )}
            </div>

            {/* Description */}
            {resource.description && (
                <ExpandableText text={resource.description} maxLength={150} />
            )}

            {/* Infos contact */}
            <div className="flex flex-wrap gap-3 text-sm text-gray-700 mb-4">
                {resource.country && (
                    <span className="flex items-center gap-1">
                        🌍 {resource.country}
                    </span>
                )}
                {resource.phone && (
                    <span className="flex items-center gap-1">
                        📞 {resource.phone}
                    </span>
                )}
                {resource.email && (
                    <span className="flex items-center gap-1">
                        📧 {resource.email}
                    </span>
                )}
            </div>

            {/* Actions (passées en children) */}
            {children && (
                <div className="flex gap-2 pt-4 border-t border-gray-200">
                    {children}
                </div>
            )}
        </div>
    )
}