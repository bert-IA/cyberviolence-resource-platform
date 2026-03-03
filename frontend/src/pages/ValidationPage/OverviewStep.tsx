import { useResourceStats } from '../../hooks/useResourceStats'
import { Button } from '../../components/ui/Button'
import type { ValidationStepProps } from '../../hooks/useValidationWorkflow'


export function OverviewStep({ state, dispatch }: ValidationStepProps) {
    // 1️⃣ Charger les statistiques groupées
    const stats = useResourceStats('geo_pending')

    // 2️⃣ Fonction : clic sur un pays
    const handleCountryClick = (countryCode: string) => {
        dispatch({
            type: 'SELECT_COUNTRY',
            country: countryCode
        })
    }

    // 3️⃣ Fonction : clic sur une catégorie
    const handleCategoryClick = (category: string) => {
        dispatch({
            type: 'SELECT_CATEGORY',
            category: category
        })
    }

    // 4️⃣ État : Chargement
    if (stats.isLoading) {
        return (
            <div className="p-6">
                <div className="text-center py-16">
                    <div className="text-2xl">⏳</div>
                    <p className="text-gray-600 mt-2">Chargement des statistiques...</p>
                </div>
            </div>
        )
    }

    // 5️⃣ État : Erreur
    if (stats.error) {
        return (
            <div className="p-6">
                <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                    <p className="text-red-800 font-medium">❌ Erreur de chargement</p>
                    <p className="text-red-600 text-sm mt-1">{stats.error.message}</p>
                </div>
            </div>
        )
    }

    // 6️⃣ État : Succès - Afficher les stats
    return (
        <div className="p-6">
            {/* En-tête */}
            <div className="mb-8">
                <h2 className="text-3xl font-bold text-gray-900 mb-2">
                    📊 Ressources en attente de validation
                </h2>
                <p className="text-gray-600">
                    {stats.data?.total_pending || 0} ressource(s) à traiter
                </p>
            </div>

            {/* Section : Par Pays */}
            <div className="mb-8">
                <h3 className="text-xl font-semibold text-gray-800 mb-4">
                    🌍 Par Pays
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    {Object.entries(stats.data?.by_country || {}).filter(([code, info]) => code !== 'INTER').map(([code, info]) => {
                        // Type assertion pour info
                        const countryInfo = info as { count: number; label: string }
                        return (
                            <Button
                                key={code}
                                label={`${countryInfo.label} (${countryInfo.count})`}
                                onClick={() => handleCountryClick(code)}
                                variant="secondary"
                            />
                        )
                    })}
                </div>
            </div>

            {/* Section : Par Catégorie */}
            <div>
                <h3 className="text-xl font-semibold text-gray-800 mb-4">
                    🏷️ Par Catégorie
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {Object.entries(stats.data?.by_category || {}).map(([category, count]) => (
                        <Button
                            key={category}
                            label={`${category} (${count})`}
                            onClick={() => handleCategoryClick(category)}
                            variant="secondary"
                        />
                    ))}
                </div>
            </div>
        </div>
    )
}