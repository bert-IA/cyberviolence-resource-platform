import { ResourceCard } from './ResourceCard'
import type { Resource } from '../../services/api'

interface ResourcesListProps {
    resources: Resource[]
    renderActions?: (resource: Resource) => React.ReactNode
}

export function ResourcesList({ resources, renderActions }: ResourcesListProps) {
    // Protection contre undefined/null
    if (!resources || resources.length === 0) {
        return (
            <div className="text-center py-12 text-gray-500 bg-gray-50 rounded-lg">
                <span className="text-4xl mb-2 block">📭</span>
                Aucune ressource trouvée
            </div>
        )
    }

    return (
        <div className="space-y-4">
            {resources.map(resource => (
                <ResourceCard key={resource.id} resource={resource}>
                    {renderActions && renderActions(resource)}
                </ResourceCard>
            ))}
        </div>
    )
}
