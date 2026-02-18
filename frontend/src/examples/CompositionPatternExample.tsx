/**
 * 📚 GUIDE : Composition Pattern dans React
 * 
 * Ce fichier montre comment utiliser la composition pour créer
 * des composants flexibles et réutilisables.
 * 
 * Pattern: Composant de Base + Actions Injectées
 */

import { DiscoveredResourceCard } from '../components/features/DiscoveredResourceCard'
import { ValidationActions } from '../components/features/ValidationActions'
import { useValidateBatch } from '../hooks/useValidateBatch'
import type { DiscoveredResource } from '../services/api'

// ============================================
// MODE 1 : Affichage Simple (Page Ressources)
// ============================================

export function ResourcesListExample({ resources }: { resources: DiscoveredResource[] }) {
    return (
        <div>
            <h2>Toutes les ressources</h2>
            {resources.map(resource => (
                // ✅ Sans actions : Affichage informatif
                <DiscoveredResourceCard
                    key={resource.id}
                    resource={resource}
                />
            ))}
        </div>
    )
}

// ============================================
// MODE 2 : Avec Actions de Validation
// ============================================

export function ValidationPageExample({ resources }: { resources: DiscoveredResource[] }) {
    const validateBatch = useValidateBatch()

    const handleApprove = (resourceId: string) => {
        validateBatch.mutate({
            source_ids: [resourceId],
            action: 'approve'
        })
    }

    const handleReject = (resourceId: string) => {
        validateBatch.mutate({
            source_ids: [resourceId],
            action: 'reject'
        })
    }

    return (
        <div>
            <h2>Validation des ressources</h2>
            {resources.map(resource => (
                // ✅ Composition : Base + Actions
                <DiscoveredResourceCard
                    key={resource.id}
                    resource={resource}
                >
                    <ValidationActions
                        onApprove={() => handleApprove(resource.id)}
                        onReject={() => handleReject(resource.id)}
                        isProcessing={validateBatch.isPending}
                    />
                </DiscoveredResourceCard>
            ))}
        </div>
    )
}

// ============================================
// MODE 3 : Avec Checkbox (Sélection Multiple)
// ============================================

export function BatchValidationExample({
    resources,
    selectedIds,
    onToggleSelection
}: {
    resources: DiscoveredResource[]
    selectedIds: string[]
    onToggleSelection: (id: string) => void
}) {
    return (
        <div>
            <h2>Validation par lot</h2>
            {resources.map(resource => (
                <DiscoveredResourceCard
                    key={resource.id}
                    resource={resource}
                >
                    {/* ✅ Autre type d'actions : Checkbox */}
                    <label className="flex items-center gap-2 cursor-pointer">
                        <input
                            type="checkbox"
                            checked={selectedIds.includes(resource.id)}
                            onChange={() => onToggleSelection(resource.id)}
                            className="w-4 h-4"
                        />
                        <span className="text-sm">
                            Sélectionner pour validation groupée
                        </span>
                    </label>
                </DiscoveredResourceCard>
            ))}
        </div>
    )
}

// ============================================
// MODE 4 : Avec Actions Personnalisées
// ============================================

export function CustomActionsExample({
    resources,
    onEdit,
    onDelete
}: {
    resources: DiscoveredResource[]
    onEdit: (id: string) => void
    onDelete: (id: string) => void
}) {
    return (
        <div>
            <h2>Gestion des ressources</h2>
            {resources.map(resource => (
                <DiscoveredResourceCard
                    key={resource.id}
                    resource={resource}
                >
                    {/* ✅ Boutons custom */}
                    <button
                        onClick={() => onEdit(resource.id)}
                        className="px-4 py-2 bg-blue-500 text-white rounded"
                    >
                        ✏️ Éditer
                    </button>
                    <button
                        onClick={() => onDelete(resource.id)}
                        className="px-4 py-2 bg-red-500 text-white rounded"
                    >
                        🗑️ Supprimer
                    </button>
                </DiscoveredResourceCard>
            ))}
        </div>
    )
}

/**
 * 🎯 AVANTAGES DE CETTE APPROCHE :
 * 
 * 1. ✅ DRY (Don't Repeat Yourself)
 *    - Le code d'affichage de la carte est écrit UNE SEULE FOIS
 *    - Pas de duplication entre ValidationCard et DisplayCard
 * 
 * 2. ✅ Flexibilité Maximum
 *    - Même composant de base pour tous les cas d'usage
 *    - Actions injectées selon le contexte
 * 
 * 3. ✅ Testabilité
 *    - Tester DiscoveredResourceCard indépendamment
 *    - Tester ValidationActions indépendamment
 *    - Tests unitaires plus simples
 * 
 * 4. ✅ Maintenance
 *    - Changement UI de la carte → 1 seul endroit
 *    - Changement logique validation → 1 seul endroit
 * 
 * 5. ✅ Évolutivité
 *    - Ajouter de nouveaux types d'actions sans toucher la carte
 *    - Pattern "Open/Closed" (ouvert extension, fermé modification)
 */
