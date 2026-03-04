import { useMutation, useQueryClient } from '@tanstack/react-query'
import { removeCountryFromLanguage, deleteLanguage } from '../../services/api'

interface Country {
    country_name: string
    country_code: string
    flag: string
}

interface LanguageCardProps {
    languageCode: string
    languageName: string
    countries: Country[]
}



export function LanguageCard({ languageCode, countries }: LanguageCardProps) {

    const queryClient = useQueryClient()
    const removeMutation = useMutation({
        mutationFn: (country_code: string) => removeCountryFromLanguage(languageCode, country_code),
        onSuccess: () => queryClient.invalidateQueries({ queryKey: ['config', 'languages'] })

    })
    const deleteMutation = useMutation({
        mutationFn: () => deleteLanguage(languageCode),
        onSuccess: () => queryClient.invalidateQueries({ queryKey: ['config', 'languages'] })

    })

    return (

        <div className="bg-white rounded-lg shadow-md p-3 hover:shadow-lg transition-shadow">
            {/* Header Langue */}
            <div className="mb-2 bg-purple-50 border border-purple-200 rounded-lg p-3">
                <div className="flex justify-between items-center">
                    <div>
                        <h3 className="text-xl font-bold text-purple-900">{languageCode}</h3>
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
            </div>

            {/* Liste des pays */}
            <div className="space-y-4">
                {countries.map(country => (
                    <div
                        key={country.country_code}
                        className="flex justify-between items-center p-2 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
                    >
                        <div>
                            <span className="font-medium text-gray-900">{country.country_name}</span>
                            <span className="text-xs text-gray-500 ml-1">({country.country_code})</span>
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
        </div>
    )
}