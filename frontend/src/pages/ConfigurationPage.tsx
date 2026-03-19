import { useCountriesLanguagesConfig } from '../hooks/useCountriesLanguagesConfig'
import { getLanguageName, getCountryName } from '../utils/formatters'
import { LanguageCard } from '../components/features/LanguageCard'
import { LoadingSpinner } from '../components/ui/LoadingSpinner'
import { ErrorMessage } from '../components/ui/ErrorMessage'
import { addLanguage } from '../services/api'
import { useState } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import toast from 'react-hot-toast'
import { Button } from '../components/ui/Button'

export function ConfigurationPage() {
    const { data: config, isLoading, error, refetch } = useCountriesLanguagesConfig()

    const [newLanguageCode, setNewLanguageCode] = useState('')
    const [showForm, setShowForm] = useState(false)

    const queryClient = useQueryClient()


    const addLanguageMutation = useMutation({
        mutationFn: () => addLanguage(newLanguageCode, {
            name: getLanguageName(newLanguageCode),
            code: newLanguageCode,
            countries: [],
            search_terms: []
        }),
        onSuccess: () => {
            toast.success(`${getLanguageName(newLanguageCode)} ajouté`)
            queryClient.invalidateQueries({ queryKey: ['config', 'languages'] })
            setNewLanguageCode('')
            setShowForm(false)
        }

    })

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
                {config && (
                    <div className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div className="bg-blue-50 rounded-lg p-4">
                            <div className='flex justify-between items-center'>
                                <div>
                                    <div className="text-sm text-blue-700 mb-1">Langues Supportées</div>
                                    <div className="text-3xl font-bold text-blue-900">
                                        {Object.keys(config.languages).length}
                                    </div>
                                    <span className="text-xs text-blue-600 mt-1">
                                        {Object.keys(config?.languages ?? {}).map(getLanguageName).join(', ')}
                                    </span>
                                </div>
                                <div>
                                    <button
                                        onClick={() => setShowForm(true)}
                                        className="text-purple-800 hover:text-purple-600 transition-colors"
                                    >
                                        ➕ Ajouter une Langue
                                    </button>
                                </div>
                            </div>
                        </div>

                        <div className="bg-green-50 rounded-lg p-4">
                            <div className="text-sm text-green-700 mb-1">Pays Configurés</div>
                            <div className="text-3xl font-bold text-green-900">
                                {Object.values(config.languages).flatMap(lang => lang.countries).length}
                            </div>
                            <div className="text-xs text-green-600 mt-1">
                                Répartis sur {Object.keys(config?.languages ?? {}).length} langues
                            </div>

                        </div>

                    </div>
                )}
                {showForm && (<div className="mt-8 p-4 bg-blue-50 border border-blue-200 rounded-lg">

                    <div>
                        <h3 className="font-semibold text-center text-blue-900 mb-1">
                            Ajout d'un language par son code
                        </h3>
                        <div className="space-y-4">
                            <input
                                type="text"
                                placeholder="Code Langage (ode ISO 639-1 (ex: JA, AR, ZH...).."

                                value={newLanguageCode}
                                onChange={(e) => setNewLanguageCode(e.target.value)}
                                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-purple-400"
                            />
                            <a href="https://en.wikipedia.org/wiki/List_of_ISO_639_language_codes"
                                target="_blank"
                                className="text-xs text-blue-600 underline">
                                Trouver mon code langue
                            </a>
                            {newLanguageCode.length >= 2 && (
                                <p className="text-sm text-green-600">
                                    → {getLanguageName(newLanguageCode)}
                                </p>
                            )}

                            <div className="flex gap-3 mt-6">
                                <Button
                                    type="button"
                                    label="Annuler"
                                    onClick={() => {
                                        setShowForm(false)
                                        setNewLanguageCode('')
                                    }}
                                    variant="secondary"
                                    disabled={addLanguageMutation.isPending}
                                />
                                <Button
                                    type="button"
                                    label="Valider"
                                    onClick={() => addLanguageMutation.mutate()}
                                    variant="primary"
                                    disabled={addLanguageMutation.isPending}
                                />
                            </div>
                        </div>


                    </div>
                </div>)
                }
            </div>

            {/* États : Loading / Error / Success */}
            {isLoading && <LoadingSpinner />}

            {error && (
                <ErrorMessage
                    error={error}
                    onRetry={() => refetch()}
                />
            )}

            {config && (
                <>
                    {/* Grille des cartes langues */}
                    <div className="grid grid-cols-1 lg:grid-cols-6 gap-3">
                        {Object.keys(config.languages).map(langCode => {
                            const countries = config.languages[langCode].countries
                            return (
                                <LanguageCard
                                    key={langCode}
                                    languageCode={langCode}
                                    searchTerms={config.languages[langCode].search_terms}
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

                            </div>
                        </div>
                    </div>
                </>
            )}
        </div>
    )
}
