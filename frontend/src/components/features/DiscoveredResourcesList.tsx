import { DiscoveredResourceCard } from './DiscoveredResourceCard'
import type { DiscoveredResource } from '../../services/api'

// Labels lisibles — même dictionnaire que DiscoveryResultCard
// (à extraire dans un fichier partagé si d'autres composants en ont besoin)
const CATEGORY_LABELS: Record<string, string> = {
    service_support: '🏢 Service d\'aide',
    procedure_plateforme: '🌐 Procédure plateforme',
    signalement_autorite: '🏛️ Signalement autorité',
}

const CATEGORY_ORDER = ['service_support', 'procedure_plateforme', 'signalement_autorite']

interface DiscoveredResourcesListProps {
    resources: DiscoveredResource[]
    // Décision : renderActions supprimé — les actions appartiennent à ValidationPage
}

export function DiscoveredResourcesList({ resources }: DiscoveredResourcesListProps) {

    if (!resources || resources.length === 0) {
        return (
            <div className="text-center py-12 text-gray-500 bg-gray-50 rounded-lg">
                <span className="text-4xl mb-2 block">📭</span>
                <p className="text-lg font-medium">Aucune nouvelle ressource trouvée</p>
                <p className="text-sm mt-2">Essayez de modifier vos filtres de recherche</p>
            </div>
        )
    }

    // Grouper par catégorie dans l'ordre défini
    const grouped = resources.reduce((acc, r) => {
        if (!acc[r.category]) acc[r.category] = []
        acc[r.category].push(r)
        return acc
    }, {} as Record<string, DiscoveredResource[]>)

    const sortedGroups = CATEGORY_ORDER
        .map(cat => ({ category: cat, resources: grouped[cat] || [] }))
        .filter(g => g.resources.length > 0)

    // Séparer pour le résumé statistique
    const newCount = resources.filter(r => r.is_new === true).length
    const dupCount = resources.filter(r => r.is_new === false).length

    return (
        <div className="space-y-4">

            {/* Résumé du lot */}
            <div className="bg-blue-50 border border-blue-200 rounded-lg px-4 py-3">
                <p className="text-blue-900 font-medium text-sm">
                    📊 {resources.length} ressource(s) analysée(s)
                </p>
                <p className="text-xs text-blue-700 mt-0.5">
                    {newCount} nouvelle(s) ajoutée(s) en attente de validation
                    {dupCount > 0 && ` · ${dupCount} doublon(s) ignoré(s)`}
                </p>
            </div>

            {/* Groupes par catégorie — nouvelles + doublons mélangés, distingués par la couleur de carte */}
            {sortedGroups.map(group => (
                <div key={group.category}>
                    <h4 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-2">
                        {CATEGORY_LABELS[group.category] ?? group.category}
                    </h4>
                    <div className="space-y-1.5">
                        {group.resources.map(resource => (
                            <DiscoveredResourceCard key={resource.id} resource={resource} />
                        ))}
                    </div>
                </div>
            ))}
        </div>
    )
}



