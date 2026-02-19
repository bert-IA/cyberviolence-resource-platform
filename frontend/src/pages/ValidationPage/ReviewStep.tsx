import { useResources } from '../../hooks/useResources'
import { useValidateBatch } from '../../hooks/useValidateBatch'
import { Button } from '../../components/ui/Button'
import { ResourceCard } from '../../components/features/ResourceCard'
import type { ValidationStepProps } from '../../hooks/useValidationWorkflow'


export function ReviewStep({ state, dispatch }: ValidationStepProps) {
    // 1️⃣ Charger TOUTES les ressources discovered
    const resources = useResources('geo_pending')
    console.log('Resources data:', resources.data)


    // 2️⃣ Hook validation batch
    const validateBatch = useValidateBatch()

    // 3️⃣ Filtrer côté client selon state.filter
    const filtered = resources.data?.filter(r => {
        if (state.filter.country) return r.country_code === state.filter.country
        if (state.filter.category) return r.category === state.filter.category
        return true
    }) || []

    // 4️⃣ Fonction : Retour overview
    const handleBack = () => {
        dispatch({ type: 'BACK_TO_OVERVIEW' })
    }

    // 5️⃣ Fonction : Toggle checkbox individuel
    const handleToggle = (id: string) => {
        dispatch({ type: 'TOGGLE_SELECTION', id })
    }

    // 6️⃣ Fonction : Sélectionner tout
    const handleSelectAll = () => {
        const allIds = filtered.map(r => r.id)
        dispatch({ type: 'SELECT_ALL', ids: allIds })
    }

    // 7️⃣ Fonction : Désélectionner tout
    const handleClearSelection = () => {
        dispatch({ type: 'CLEAR_SELECTION' })
    }

    // 8️⃣ Fonction : Valider sélection
    const handleValidate = () => {
        validateBatch.mutate(
            {
                resource_ids: state.selectedIds as string[],
                action: 'approve'
            },
            {

                onSuccess: () => {
                    dispatch({ type: 'CLEAR_SELECTION' })
                    // Si on a traité TOUTES les ressources → retour overview
                    if (state.selectedIds.length === filtered.length) {
                        dispatch({ type: 'BACK_TO_OVERVIEW' })
                    } else {
                        // Sinon → recharger les données (les ressources validées disparaissent)
                        resources.refetch()
                    }
                }
            }
        )
    }

    // 9️⃣ Fonction : Rejeter sélection
    const handleReject = () => {
        validateBatch.mutate(
            {
                resource_ids: state.selectedIds as string[],
                action: 'reject'
            },
            {
                onSuccess: () => {
                    dispatch({ type: 'CLEAR_SELECTION' })
                    // Si on a traité TOUTES les ressources → retour overview
                    if (state.selectedIds.length === filtered.length) {
                        dispatch({ type: 'BACK_TO_OVERVIEW' })
                    } else {
                        // Sinon → recharger les données (les ressources validées disparaissent)
                        resources.refetch()
                    }
                }

            }
        )
    }

    // 🔟 Titre dynamique selon groupBy
    const getTitle = () => {
        if (state.groupBy === 'country') {
            const countryLabel = filtered[0]?.country || state.filter.country
            return `🌍 ${countryLabel} (${filtered.length} ressources)`
        }
        if (state.groupBy === 'category') {
            return `🏷️ ${state.filter.category} (${filtered.length} ressources)`
        }
        return `📋 Toutes les ressources (${filtered.length})`
    }

    // État : Chargement
    if (resources.isLoading) {
        return (
            <div className="p-6">
                <div className="text-center py-16">
                    <div className="text-2xl">⏳</div>
                    <p className="text-gray-600 mt-2">Chargement des ressources...</p>
                </div>
            </div>
        )
    }

    // État : Erreur
    if (resources.error) {
        return (
            <div className="p-6">
                <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                    <p className="text-red-800 font-medium">❌ Erreur de chargement</p>
                    <p className="text-red-600 text-sm mt-1">{resources.error.message}</p>
                </div>
            </div>
        )
    }

    // État : Aucune ressource (vérifier que les données existent vraiment)
    if (resources.data && filtered.length === 0) {
        return (
            <div className="p-6">
                <Button label="← Retour" onClick={handleBack} variant="secondary" />
                <div className="text-center py-16">
                    <div className="text-4xl mb-4">🎉</div>
                    <p className="text-gray-600">Aucune ressource à traiter ici !</p>
                </div>
            </div>
        )
    }

    // État : Succès - Afficher la liste
    return (
        <div className="p-6">
            {/* En-tête avec bouton retour */}
            <div className="mb-6 flex items-center justify-between">
                <div>
                    <Button label="← Retour" onClick={handleBack} variant="secondary" />
                    <h2 className="text-2xl font-bold text-gray-900 mt-4">
                        {getTitle()}
                    </h2>
                </div>
            </div>

            {/* Actions bulk */}
            <div className="mb-4 flex gap-4">
                <Button
                    label="☑️ Tout sélectionner"
                    onClick={handleSelectAll}
                    variant="secondary"
                />
                <Button
                    label="❌ Tout désélectionner"
                    onClick={handleClearSelection}
                    variant="secondary"
                    disabled={state.selectedIds.length === 0}
                />
            </div>

            {/* Liste des ressources */}
            <div className="space-y-3 mb-6">
                {filtered.map(resource => (
                    <ResourceCard key={resource.id} resource={resource}>
                        <label className="flex items-center gap-2 cursor-pointer">
                            <input
                                type="checkbox"
                                checked={state.selectedIds.includes(resource.id)}
                                onChange={() => handleToggle(resource.id)}
                                className="w-4 h-4 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
                            />
                            <span className="text-sm text-gray-700">
                                Sélectionner cette ressource
                            </span>
                        </label>
                    </ResourceCard>
                ))}
            </div>

            {/* Barre d'actions */}
            <div className="sticky bottom-0 bg-white border-t pt-4 flex gap-4">
                <Button
                    label={`✅ Valider (${state.selectedIds.length})`}
                    onClick={handleValidate}
                    variant="primary"
                    disabled={state.selectedIds.length === 0 || validateBatch.isPending}
                />
                <Button
                    label={`🗑️ Rejeter (${state.selectedIds.length})`}
                    onClick={handleReject}
                    variant="secondary"
                    disabled={state.selectedIds.length === 0 || validateBatch.isPending}
                />
            </div>
        </div>
    )
}