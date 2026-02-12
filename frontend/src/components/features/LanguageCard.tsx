interface Country {
    country_name: string
    country_code: string
    flag: string
    organizations_count: number
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
    const totalOrgs = countries.reduce((sum, c) => sum + c.organizations_count, 0)

    return (
        <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
            {/* Header Langue */}
            <div className="flex items-center justify-between mb-4">
                <div>
                    <h3 className="text-xl font-bold text-gray-900">
                        {LANGUAGE_NAMES[languageCode] || languageCode}
                    </h3>
                    <p className="text-sm text-gray-600 mt-1">
                        Code : <span className="font-mono bg-gray-100 px-2 py-0.5 rounded">{languageCode}</span>
                    </p>
                </div>
                <div className="text-right">
                    <div className="text-2xl font-bold text-blue-600">{countries.length}</div>
                    <div className="text-xs text-gray-600">Pays</div>
                </div>
            </div>

            {/* Liste des pays */}
            <div className="space-y-3">
                {countries.map(country => (
                    <div
                        key={country.country_code}
                        className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
                    >
                        <div className="flex items-center gap-3">
                            <span className="text-3xl">{country.flag}</span>
                            <div>
                                <p className="font-medium text-gray-900">{country.country_name}</p>
                                <p className="text-xs text-gray-600">Code : {country.country_code}</p>
                            </div>
                        </div>
                        <div className="text-right">
                            <div className="text-lg font-semibold text-green-600">
                                {country.organizations_count}
                            </div>
                            <div className="text-xs text-gray-600">Organisations</div>
                        </div>
                    </div>
                ))}
            </div>

            {/* Footer Stats */}
            <div className="mt-4 pt-4 border-t border-gray-200">
                <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Total organisations</span>
                    <span className="font-bold text-blue-600">{totalOrgs}</span>
                </div>
            </div>
        </div>
    )
}