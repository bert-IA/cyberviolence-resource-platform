import { useState } from 'react'
import { Button } from '../ui/Button'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { removeCountryFromLanguage, deleteLanguage, addCountryToLanguage, autoPopulateCountriesByLanguage } from '../../services/api'
import toast from 'react-hot-toast'

interface Country {
    country_name: string
    country_code: string
    flag: string
}

interface LanguageCardProps {
    languageCode: string
    countries: Country[]
    searchTerms: string[]
}

function getFlagEmoji(countryCode: string): string {
    return countryCode
        .toUpperCase()
        .split('')
        .map(char => String.fromCodePoint(127397 + char.charCodeAt(0)))
        .join('')
}

export function LanguageCard({ languageCode, countries, searchTerms }: LanguageCardProps) {

    const [newCountry, setNewCountry] = useState<Country>({ country_name: '', country_code: '', flag: '' })

    const [showForm, setShowForm] = useState(false)

    const queryClient = useQueryClient()

    const removeMutation = useMutation({
        mutationFn: (country_code: string) => removeCountryFromLanguage(languageCode, country_code),
        onSuccess: (data, variables) => {
            toast.success(`${variables} supprimé`)
            queryClient.invalidateQueries({ queryKey: ['config', 'languages'] })
        }

    })
    const deleteMutation = useMutation({
        mutationFn: () => deleteLanguage(languageCode),
        onSuccess: () => {
            toast.success(`${languageCode} supprimé`)
            queryClient.invalidateQueries({ queryKey: ['config', 'languages'] })
        }

    })

    const addCountryMutation = useMutation({
        mutationFn: () => addCountryToLanguage(languageCode, {
            ...newCountry,
            flag: getFlagEmoji(newCountry.country_code)
        }),
        onSuccess: () => {
            toast.success(`${newCountry.country_name} ajouté`)
            queryClient.invalidateQueries({ queryKey: ['config', 'languages'] })
            setNewCountry({ country_name: '', country_code: '', flag: '' })
            setShowForm(false)
        }

    })

    const autoPopulateCountriesMutation = useMutation({
        mutationFn: () => autoPopulateCountriesByLanguage(languageCode),
        onSuccess: (data) => {
            toast.success(`${data.countries_added} pays ajoutés pour ${languageCode}`)
            queryClient.invalidateQueries({ queryKey: ['config', 'languages'] })
        }

    })

    return (

        <div className="bg-white rounded-lg shadow-md p-3 hover:shadow-lg transition-shadow flex flex-col h-full">
            {/* Header Langue */}
            <div className="mb-2 bg-purple-50 border border-purple-200 rounded-lg p-3">

                <div className="flex justify-between items-center">
                    <div>
                        {/* Tooltip sur le titre */}
                        <div className="relative group inline-block">
                            <h3 className="text-xl font-bold text-purple-900 cursor-help">
                                {languageCode}
                            </h3>
                            <div className="invisible group-hover:visible absolute bottom-full left-0 
                            bg-gray-400 text-white text-x1 rounded-lg p-2 w-48 z-10">
                                <p className='text-center font-bold mb-1'>Mots-clés de recherche</p>
                                <ul>
                                    {searchTerms.map(term => <li key={term}>• {term}</li>)}
                                </ul>
                            </div>
                        </div>
                        <p className="text-sm text-purple-600 mt-1">{countries.length} pays</p>
                    </div>
                    <button
                        onClick={() => deleteMutation.mutate()}
                        disabled={deleteMutation.isPending}
                        className="text-red-400 hover:text-red-600 transition-colors text-xl"
                    >
                        🗑️
                    </button>
                </div>
                <button
                    onClick={() => autoPopulateCountriesMutation.mutate()}
                    disabled={autoPopulateCountriesMutation.isPending}
                    className="text-red-400 hover:text-red-600 transition-colors text-l mt-3"
                >
                    ✨ Rechercher Pays
                </button>
            </div>

            {/* Liste des pays */}

            <div className="space-y-4">
                {countries.map(country => (
                    <div
                        key={country.country_code}
                        className="flex justify-between items-center p-2 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
                    >
                        <div className="flex items-center gap-2">
                            <span className="text-lg">{country.flag}</span>
                            <span className="font-medium text-gray-900">{country.country_name}</span>
                        </div>
                        <button
                            onClick={() => removeMutation.mutate(country.country_code)}
                            disabled={removeMutation.isPending}
                            className="text-red-400 hover:text-red-600 transition-colors"
                        >
                            🗑️
                        </button>
                    </div>


                ))}
            </div>
            {showForm && (
                <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center">
                    <div className="bg-white rounded-lg shadow-xl p-6 w-full max-w-md mx-4">
                        <h2 className="text-xl font-bold text-purple-900 text-center mb-6">
                            Ajouter un pays pour {languageCode}
                        </h2>
                        <div className="space-y-4">
                            <input
                                type="text"
                                placeholder="Nom du pays"
                                value={newCountry.country_name}
                                onChange={(e) => setNewCountry({ ...newCountry, country_name: e.target.value })}
                                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-purple-400"
                            />
                            <input
                                type="text"
                                placeholder="Code du pays (ex: FR)"
                                value={newCountry.country_code}
                                onChange={(e) => setNewCountry({ ...newCountry, country_code: e.target.value })}
                                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-purple-400"
                            />
                        </div>
                        <div className="flex gap-3 mt-6">
                            <Button
                                type="button"
                                label="Annuler"
                                onClick={() => {
                                    setShowForm(false)
                                    setNewCountry({ country_name: '', country_code: '', flag: '' })
                                }}
                                variant="secondary"
                                disabled={addCountryMutation.isPending}
                            />
                            <Button
                                type="button"
                                label="Valider"
                                onClick={() => addCountryMutation.mutate()}
                                variant="primary"
                                disabled={addCountryMutation.isPending}
                            />
                        </div>
                    </div>
                </div>
            )}

            <button
                onClick={() => setShowForm(true)}
                className="text-green-700 hover:text-green-600 transition-colors mt-auto pt-3"
            >
                ➕ Ajouter un pays
            </button>
        </div>
    )
}