import type { DiscoveredResource } from '../../services/api'

interface DiscoveredResourceCardProps {
    resource: DiscoveredResource
    children?: React.ReactNode
}

export function DiscoveredResourceCard({ resource, children }: DiscoveredResourceCardProps) {
    return (
        <div className="bg-white rounded-lg shadow-md p-6 mb-4 hover:shadow-lg transition-shadow">
            {/* Header avec nom et badges */}
            <div className="flex justify-between items-start mb-3">
                <h3 className="text-lg font-semibold text-gray-900">
                    {resource.name}
                </h3>
                <div className="flex gap-2">
                    {/* Badge catégorie */}
                    <span className="px-3 py-1 text-xs font-medium rounded-full bg-purple-100 text-purple-800">
                        {resource.category}
                    </span>
                    {/* Badge nouveau/doublon */}
                    {resource.is_new ? (
                        <span className="px-3 py-1 text-xs font-medium rounded-full bg-green-100 text-green-800">
                            🆕 Nouveau
                        </span>
                    ) : (
                        <span className="px-3 py-1 text-xs font-medium rounded-full bg-yellow-100 text-yellow-800">
                            ⚠️ Doublon possible
                        </span>
                    )}
                </div>
            </div>

            {/* Description */}
            {resource.description && (
                <p className="text-gray-600 text-sm mb-3">
                    {resource.description}
                </p>
            )}

            {/* Infos contact */}
            <div className="flex flex-wrap gap-3 text-sm text-gray-700 mb-3">
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

            {/* Confidence score */}
            <div className="flex items-center gap-2 mb-3">
                <span className="text-xs text-gray-500">Confiance:</span>
                <div className="flex-1 bg-gray-200 rounded-full h-2 max-w-xs">
                    <div
                        className="bg-blue-600 h-2 rounded-full transition-all"
                        style={{ width: `${resource.confidence * 100}%` }}
                    ></div>
                </div>
                <span className="text-xs font-medium text-gray-700">
                    {Math.round(resource.confidence * 100)}%
                </span>
            </div>

            {/* Raison de doublon si applicable */}
            {!resource.is_new && resource.duplicate_reason && (
                <div className="text-xs text-yellow-700 bg-yellow-50 px-3 py-2 rounded mb-3">
                    ℹ️ {resource.duplicate_reason}
                </div>
            )}

            {/* Actions (passées en children) */}
            {children && (
                <div className="flex gap-2 pt-4 border-t border-gray-200">
                    {children}
                </div>
            )}
        </div>
    )
}
