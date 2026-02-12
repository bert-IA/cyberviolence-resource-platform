import { useCountriesConfig } from '../hooks/useCountriesConfig'
import { LanguageCard } from '../components/features/LanguageCard'
import { LoadingSpinner } from '../components/ui/LoadingSpinner'
import { ErrorMessage } from '../components/ui/ErrorMessage'

export function ConfigurationPage() {
    const { data, isLoading, error, refetch } = useCountriesConfig()

    // 🔍 DEBUG : Affiche les données dans la console
    console.log('📊 Countries config:', data)
    if (data && data.countries_by_language.FR) {
        console.log('🇫🇷 Premier pays FR:', data.countries_by_language.FR[0])
    }

    return (
        <div className="max-w-7xl mx-auto p-6">
            {/* Header avec Stats Globales */}
            <div className="mb-4">
                <h1 className="text-3xl font-bold text-gray-900 mb-2">
                    ⚙️ Configuration Pays & Langues
                </h1>
                <p className="text-gray-600">
                    Configuration active pour la découverte de ressources
                </p>

                {/* Stats globales */}
                {data && (
                    <div className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div className="bg-blue-50 rounded-lg p-4">
                            <div className="text-sm text-blue-700 mb-1">Langues Supportées</div>
                            <div className="text-3xl font-bold text-blue-900">
                                {data.supported_languages.length}
                            </div>
                            <span className="text-xs text-blue-600 mt-1">
                                {data.supported_languages.join(', ')}
                            </span>
                        </div>

                        <div className="bg-green-50 rounded-lg p-4">
                            <div className="text-sm text-green-700 mb-1">Pays Configurés</div>
                            <div className="text-3xl font-bold text-green-900">
                                {data.total_countries}
                            </div>
                            <div className="text-xs text-green-600 mt-1">
                                Répartis sur {data.supported_languages.length} langues
                            </div>
                        </div>
                    </div>
                )}
            </div>

            {/* États : Loading / Error / Success */}
            {isLoading && <LoadingSpinner />}

            {error && (
                <ErrorMessage
                    error={error}
                    onRetry={() => refetch()}
                />
            )}

            {data && (
                <>
                    {/* Grille des cartes langues */}
                    <div className="grid grid-cols-1 lg:grid-cols-6 gap-3">
                        {data.supported_languages.map(langCode => {
                            console.log('🔍 Langue du backend:', langCode)  // ← DEBUG
                            const countries = data.countries_by_language[langCode] || []
                            return (
                                <LanguageCard
                                    key={langCode}
                                    languageCode={langCode}
                                    languageName={langCode}
                                    countries={countries}
                                />
                            )
                        })}
                    </div>

                    {/* Info Footer */}
                    <div className="mt-8 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                        <div className="flex items-start gap-3">
                            <span className="text-2xl">ℹ️</span>
                            <div>
                                <h3 className="font-semibold text-blue-900 mb-1">
                                    À propos de cette configuration
                                </h3>
                                <p className="text-sm text-blue-800">
                                    Cette configuration définit les pays ciblés pour chaque langue lors de la
                                    découverte de ressources. Les organisations estimées représentent le nombre
                                    d'entités référencées dans la base de données pour chaque pays.
                                </p>
                                <p className="text-sm text-blue-800 mt-2">
                                    <strong>Note</strong> : Cette configuration est actuellement en lecture seule.
                                    Les modifications nécessitent une mise à jour du fichier de configuration backend.
                                </p>
                            </div>
                        </div>
                    </div>
                </>
            )}
        </div>
    )
}
