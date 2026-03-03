import React, { useState } from 'react'
import type { DiscoveryFilters } from '../../services/api'
import { Button } from '../ui/Button'

interface DiscoveryFormProps {
    onSubmit: (filters: DiscoveryFilters) => void
    loading: boolean
}

const LANGUAGES = [
    { code: 'FR', name: 'Français', countries: ['France', 'Belgique', 'Suisse', 'Canada', 'Sénégal'] },
    { code: 'EN', name: 'English', countries: ['UK', 'USA', 'Australia', 'Canada', 'New Zealand'] },
    { code: 'ES', name: 'Español', countries: ['España', 'México', 'Argentina', 'Colombia', 'Perú'] },
    { code: 'DE', name: 'Deutsch', countries: ['Deutschland', 'Österreich', 'Schweiz', 'Liechtenstein', 'Belgique'] },
    { code: 'PT', name: 'Português', countries: ['Portugal', 'Brasil', 'Angola', 'Moçambique', 'Cabo Verde'] },
]

const CATEGORIES = [
    { value: 'service_support', label: 'Service d\'aides' },
    { value: 'procedure_plateforme', label: 'Procédures plateformes' },
    { value: 'signalement_autorite', label: 'Signalement autorités' },

]

export function DiscoveryForm({ onSubmit, loading }: DiscoveryFormProps) {
    const [language, setLanguage] = useState('FR')
    const [selectedCategories, setSelectedCategories] = useState<string[]>([])
    const [selectedCountries, setSelectedCountries] = useState<string[]>([])
    const [maxPerCategory, setMaxPerCategory] = useState(3)

    const currentLanguage = LANGUAGES.find(l => l.code === language)

    const handleCategoryToggle = (category: string) => {
        setSelectedCategories(prev =>
            prev.includes(category)
                ? prev.filter(c => c !== category)
                : [...prev, category]
        )
    }

    const handleCountryToggle = (country: string) => {
        setSelectedCountries(prev =>
            prev.includes(country)
                ? prev.filter(c => c !== country)
                : [...prev, country]
        )
    }

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault()
        onSubmit({
            language,
            categories: selectedCategories,
            countries: selectedCountries,
            max_per_category: maxPerCategory,
        })
    }

    return (
        <form onSubmit={handleSubmit} className="bg-white rounded-lg shadow-md p-6 space-y-6">
            {/* Sélection Langue */}
            <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                    🌍 Langue
                </label>
                <select
                    value={language}
                    onChange={(e) => {
                        setLanguage(e.target.value)
                        setSelectedCountries([])  // Reset pays quand langue change
                    }}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
                >
                    {LANGUAGES.map(lang => (
                        <option key={lang.code} value={lang.code}>
                            {lang.name}
                        </option>
                    ))}
                </select>
            </div>

            {/* Sélection Catégories */}
            <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                    📁 Catégories ({selectedCategories.length} sélectionnées)
                </label>
                <div className="space-y-2">
                    {CATEGORIES.map(cat => (
                        <label key={cat.value} className="flex items-center gap-2 p-2 hover:bg-gray-50 rounded cursor-pointer">
                            <input
                                type="checkbox"
                                checked={selectedCategories.includes(cat.value)}
                                onChange={() => handleCategoryToggle(cat.value)}
                                className="w-4 h-4 text-blue-600"
                            />
                            <span className="text-sm">{cat.label}</span>
                        </label>
                    ))}
                </div>
            </div>

            {/* Sélection Pays */}
            <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                    🗺️ Pays ({selectedCountries.length} sélectionnés)
                </label>
                <div className="space-y-2">
                    {currentLanguage?.countries.map(country => (
                        <label key={country} className="flex items-center gap-2 p-2 hover:bg-gray-50 rounded cursor-pointer">
                            <input
                                type="checkbox"
                                checked={selectedCountries.includes(country)}
                                onChange={() => handleCountryToggle(country)}
                                className="w-4 h-4 text-blue-600"
                            />
                            <span className="text-sm">{country}</span>
                        </label>
                    ))}
                </div>
            </div>

            {/* Nombre max par catégorie */}
            <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                    🔢 Max par catégorie : {maxPerCategory}
                </label>
                <input
                    type="range"
                    min="1"
                    max="10"
                    value={maxPerCategory}
                    onChange={(e) => setMaxPerCategory(Number(e.target.value))}
                    className="w-full"
                />
            </div>

            {/* Bouton Submit avec composant Button */}
            <div className="w-full">
                <Button
                    type="submit"
                    label={loading ? '⏳ Recherche en cours...' : '🔍 Lancer la découverte'}
                    onClick={() => { }}  // Géré par le type="submit"
                    variant="primary"
                    disabled={loading || selectedCategories.length === 0}
                />
            </div>
        </form>
    )
}