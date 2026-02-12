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

const LANGUAGE_NAMES: Record<string, string> = {
    'FR': 'Français',
    'EN': 'English',
    'ES': 'Español',
    'IT': 'Italiano',
    'DE': 'Deutsch',
    'PT': 'Português',
}

export function LanguageCard({ languageCode, countries }: LanguageCardProps) {

    return (
        <div className="bg-white rounded-lg shadow-md p-3 hover:shadow-lg transition-shadow">
            {/* Header Langue avec cadre bleuté */}
            <div className="mb-2 bg-purple-50 border border-purple-200 rounded-lg p-3">
                <h3 className="text-xl font-bold text-gray-900">
                    {LANGUAGE_NAMES[languageCode] || languageCode} : {languageCode}
                </h3>
                <div className="text-sm text-bold text-purple-600 mt-1">
                    {countries.length} pays
                </div>
            </div>

            {/* Liste des pays */}
            <div className="space-y-3">
                {countries.map(country => (
                    <div
                        key={country.country_code}
                        className="p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
                    >
                        <p className="font-medium text-gray-900">
                            {country.country_name}
                            <span className="text-xs text-gray-500 ml-2">({country.country_code})</span>
                        </p>
                    </div>
                ))}
            </div>
        </div>
    )
}