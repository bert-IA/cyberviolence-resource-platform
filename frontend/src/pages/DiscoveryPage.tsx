import { useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { useDiscoverResources } from '../hooks/useDiscoverResources'
import { DiscoveryForm } from '../components/features/DiscoveryForm'
import { DiscoveredResourcesList } from '../components/features/DiscoveredResourcesList'
import { LoadingSpinner } from '../components/ui/LoadingSpinner'
import { ErrorMessage } from '../components/ui/ErrorMessage'
import type { DiscoveryFilters } from '../services/api'

// Décision : useValidateBatch, ValidationActions et hiddenIds supprimés.
// Les actions (approuver/rejeter) appartiennent à ValidationPage.
// DiscoveryPage est désormais une page de rapport de mission — lecture seule.

export function DiscoveryPage() {
    const discovery = useDiscoverResources()
    const navigate  = useNavigate()

    // Mesure de la durée réelle côté frontend
    // useRef car on n'a pas besoin de déclencher un re-render au démarrage
    const startTimeRef = useRef<number | null>(null)
    const elapsedRef   = useRef<string | null>(null)

    const handleSearch = (filters: DiscoveryFilters) => {
        startTimeRef.current = Date.now()
        elapsedRef.current   = null
        discovery.mutate(filters, {
            onSuccess: () => {
                if (startTimeRef.current) {
                    const seconds = Math.round((Date.now() - startTimeRef.current) / 1000)
                    elapsedRef.current = `${seconds}s`
                }
            }
        })
    }

    const allResources = discovery.data?.newly_discovered || []
    const newCount     = allResources.filter(r => r.is_new === true).length

    return (
        <div className="p-6">
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
                        <div className="space-y-4">
                            {/* Bandeau de résumé */}
                            <div className="p-4 bg-green-50 border border-green-200 rounded-lg flex items-center justify-between gap-4">
                                <div>
                                    <p className="text-green-800 font-medium">
                                        ✅ Découverte terminée — {allResources.length} ressource(s) analysée(s)
                                    </p>
                                    {/* Durée RÉELLE mesurée côté frontend, pas l'estimation du backend */}
                                    {elapsedRef.current && (
                                        <p className="text-sm text-green-700 mt-0.5">
                                            Durée : {elapsedRef.current}
                                        </p>
                                    )}
                                </div>
                                {/* Bouton de redirection vers ValidationPage si nouvelles ressources */}
                                {newCount > 0 && (
                                    <button
                                        onClick={() => navigate('/validation')}
                                        className="shrink-0 px-4 py-2 bg-green-600 hover:bg-green-700 text-white text-sm font-medium rounded-lg transition-colors"
                                    >
                                        Valider {newCount} ressource(s) →
                                    </button>
                                )}
                            </div>

                            {/* Liste compacte */}
                            <DiscoveredResourcesList resources={allResources} />
                        </div>
                    )}

                    {/* État : Initial */}
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