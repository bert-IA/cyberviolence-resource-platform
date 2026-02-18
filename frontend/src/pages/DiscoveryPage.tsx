import { useState } from 'react'
import { useDiscoverResources } from '../hooks/useDiscoverResources'
import { DiscoveryForm } from '../components/features/DiscoveryForm'  // Défini dans Étape 3 partie 1
import { DiscoveredResourcesList } from '../components/features/DiscoveredResourcesList'
import { ValidationActions } from '../components/features/ValidationActions'
import { useValidateBatch } from '../hooks/useValidateBatch'
import { LoadingSpinner } from '../components/ui/LoadingSpinner'
import { ErrorMessage } from '../components/ui/ErrorMessage'


export function DiscoveryPage() {
    const discovery = useDiscoverResources()
    const validateBatch = useValidateBatch()

    // 🆕 État local pour masquer les ressources traitées
    const [hiddenIds, setHiddenIds] = useState<Set<string>>(new Set())

    const handleSearch = (filters: any) => {
        setHiddenIds(new Set())
        discovery.mutate(filters)
    }

    const handleApprove = (resourceId: string) => {
        // 🎯 Optimistic update : masquer immédiatement
        setHiddenIds(prev => new Set(prev).add(resourceId))

        validateBatch.mutate({
            resource_ids: [resourceId],
            action: 'approve'
        }, {
            onError: () => {
                // ↩️ Rollback : réafficher en cas d'erreur
                setHiddenIds(prev => {
                    const next = new Set(prev)
                    next.delete(resourceId)
                    return next
                })
            }
        })
    }

    const handleReject = (resourceId: string) => {
        // � Optimistic update : masquer immédiatement
        setHiddenIds(prev => new Set(prev).add(resourceId))

        validateBatch.mutate({
            resource_ids: [resourceId],
            action: 'reject'
        }, {
            onError: () => {
                // ↩️ Rollback : réafficher en cas d'erreur
                setHiddenIds(prev => {
                    const next = new Set(prev)
                    next.delete(resourceId)
                    return next
                })
            }
        })
    }

    // 🆕 Filtrer les ressources visibles
    const visibleResources = discovery.data?.newly_discovered?.filter(
        r => !hiddenIds.has(r.id)
    ) || []

    return (
        <div className="max-w-7xl mx-auto p-6">
            {/* Header */}
            <div className="mb-8">
                <h1 className="text-3xl font-bold text-gray-900">
                    🔍 Découverte de Ressources
                </h1>
                <p className="mt-2 text-gray-600">
                    Recherchez des ressources par langue, pays et catégorie
                </p>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Formulaire (1/3 gauche) */}
                <div className="lg:col-span-1">
                    <DiscoveryForm
                        onSubmit={handleSearch}
                        loading={discovery.isPending}
                    />
                </div>

                {/* Résultats (2/3 droite) */}
                <div className="lg:col-span-2">
                    {/* État : Chargement */}
                    {discovery.isPending && <LoadingSpinner />}

                    {/* État : Erreur */}
                    {discovery.error && (
                        <ErrorMessage
                            error={discovery.error}
                            onRetry={() => discovery.mutate(discovery.variables!)}
                        />
                    )}

                    {/* État : Succès */}
                    {discovery.data && (
                        <>
                            <div className="mb-4 p-4 bg-green-50 border border-green-200 rounded-lg">
                                <p className="text-green-800 font-medium">
                                    ✅ {discovery.data.total_discovered} ressource(s) découverte(s)
                                </p>
                                {discovery.data.estimated_duration && (
                                    <p className="text-sm text-green-700 mt-1">
                                        Durée estimée : {discovery.data.estimated_duration}
                                    </p>
                                )}
                            </div>
                            <DiscoveredResourcesList
                                resources={visibleResources}
                                renderActions={(resource) => (
                                    <ValidationActions
                                        onApprove={() => handleApprove(resource.id)}
                                        onReject={() => handleReject(resource.id)}
                                        isProcessing={validateBatch.isPending}
                                    />
                                )}
                            />
                        </>
                    )}

                    {/* État : Initial (aucune recherche lancée) */}
                    {!discovery.isPending && !discovery.data && !discovery.error && (
                        <div className="text-center py-16 bg-gray-50 rounded-lg">
                            <span className="text-6xl mb-4 block">🔎</span>
                            <p className="text-gray-600 text-lg">
                                Configurez vos filtres et lancez une recherche
                            </p>
                        </div>
                    )}
                </div>
            </div>
        </div>
    )
}