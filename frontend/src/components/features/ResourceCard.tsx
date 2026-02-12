import type { Resource } from '../../services/api'

interface ResourceCardProps {
    resource: Resource
    children?: React.ReactNode  // Pour les boutons d'action
}

export function ResourceCard({ resource, children }: ResourceCardProps) {
    return (
        <div className="bg-white rounded-lg shadow-md p-6 mb-4 hover:shadow-lg transition-shadow">
            {/* Header avec nom et badge status */}
            <div className="flex justify-between items-start mb-3">
                <h3 className="text-lg font-semibold text-gray-900">
                    {resource.name}
                </h3>
                {resource.workflow_status && (
                    <span className="px-3 py-1 text-xs font-medium rounded-full bg-blue-100 text-blue-800">
                        {resource.workflow_status}
                    </span>
                )}
            </div>

            {/* Description */}
            {resource.description && (
                <p className="text-gray-600 text-sm mb-3 line-clamp-2">
                    {resource.description}
                </p>
            )}

            {/* Infos contact */}
            <div className="flex flex-wrap gap-3 text-sm text-gray-700 mb-4">
                {resource.country && (
                    <span className="flex items-center gap-1">
                        🌍 {resource.country}
                    </span>
                )}
                {resource.contact_phone && (
                    <span className="flex items-center gap-1">
                        📞 {resource.contact_phone}
                    </span>
                )}
                {resource.contact_email && (
                    <span className="flex items-center gap-1">
                        📧 {resource.contact_email}
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