import { DiscoveredResourceCard } from './DiscoveredResourceCard'
import type { DiscoveredResource } from '../../services/api'

interface DiscoveredResourcesListProps {
    resources: DiscoveredResource[]
    renderActions?: (resource: DiscoveredResource) => React.ReactNode
}

export function DiscoveredResourcesList({ resources, renderActions }: DiscoveredResourcesListProps) {

    // Protection contre undefined/null
    if (!resources || resources.length === 0) {
        return (
            <div className="text-center py-12 text-gray-500 bg-gray-50 rounded-lg">
                <span className="text-4xl mb-2 block">📭</span>
                <p className="text-lg font-medium">Aucune nouvelle ressource trouvée</p>
                <p className="text-sm mt-2">Essayez de modifier vos filtres de recherche</p>
            </div>
        )
    }
    function groupedByCategory(resources: DiscoveredResource[]) {
        const grouped = resources.reduce((acc, resource) => {
            if (!acc[resource.category]) {
                acc[resource.category] = []
            }
            acc[resource.category].push(resource)
            return acc
        }, {} as Record<string, DiscoveredResource[]>)
        return grouped
    }

    const categoryOrder = [
        'association_locale',   // 🏢 
        'contact_urgence',      // 📞 
        'procedure_plateforme',  // 🌐 
        'signalement_autorite' // 🏛️ 
    ]

    function sortByCategory(resources: DiscoveredResource[]) {
        const grouped = groupedByCategory(resources)
        return (categoryOrder
            .map(category => ({
                category,
                resources: grouped[category] || []
            }))
            .filter(group => group.resources.length > 0)
        )
    }

    // Séparer nouvelles ressources et doublons
    const newResources = resources.filter(r => r.is_new)
    const duplicates = resources.filter(r => !r.is_new)

    const sortedNew = sortByCategory(newResources)
    const sortedDuplicates = sortByCategory(duplicates)

    return (
        <div className="space-y-6">
            {/* Statistiques */}
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <div className="flex items-center justify-between">
                    <div>
                        <p className="text-blue-900 font-medium">
                            📊 {resources.length} ressource(s) trouvée(s)
                        </p>
                        <p className="text-sm text-blue-700 mt-1">
                            {newResources.length} nouvelle(s) · {duplicates.length} doublon(s) détecté(s)
                        </p>
                    </div>
                </div>
            </div>

            {/* Nouvelles ressources */}
            {newResources.length > 0 && (
                <div>
                    <h3 className="text-lg font-bold text-blue-500 mb-3 flex items-center gap-2">
                        <span>🆕</span>
                        NOUVELLES RESSOURCES ({newResources.length})
                    </h3>
                    <div className="space-y-4">
                        {sortedNew.map(group => (
                            <div key={group.category}>
                                <h4 className="text-lg  text-blue-900 mb-3 flex items-center gap-2">{group.category}</h4>
                                {group.resources.map(resource => (
                                    <DiscoveredResourceCard key={resource.id} resource={resource}>
                                        {renderActions && renderActions(resource)}
                                    </DiscoveredResourceCard>
                                ))}
                            </div>
                        ))}
                    </div>
                </div>

            )}
            {/* Doublons détectés */}
            {sortedDuplicates.length > 0 && (
                <div>
                    <h3 className="text-lg font-semibold text-red-600 mb-3 flex items-center gap-2">
                        <span>⚠️</span>
                        Doublons possibles ({duplicates.length})
                    </h3>
                    <div className="space-y-4">
                        {sortedDuplicates.map(group => (
                            <div key={group.category}>
                                <h4 className="text-lg  text-red-900 mb-3 flex items-center gap-2">{group.category}</h4>
                                {group.resources.map(resource => (
                                    <DiscoveredResourceCard key={resource.id} resource={resource}>
                                        {renderActions && renderActions(resource)}
                                    </DiscoveredResourceCard>
                                ))}
                            </div>
                        ))}
                    </div>
                </div>

            )}
        </div>
    )
}



