import { useQuery } from '@tanstack/react-query'

interface Country {
    country_name: string
    country_code: string
    flag: string
    search_terms: string[]
    search_terms_count: number
    organizations_count: number
}

interface CountriesConfig {
    supported_languages: string[]
    total_countries: number
    countries_by_language: Record<string, Country[]>
}

export function useCountriesConfig() {
    return useQuery({
        queryKey: ['config', 'countries'],
        queryFn: async () => {
            const response = await fetch('http://localhost:8000/geographic/countries', {
                headers: { 'Authorization': 'Bearer admin-token-2024' }
            })

            if (!response.ok) {
                throw new Error(`Erreur API: ${response.status}`)
            }

            const data = await response.json()
            return data.data as CountriesConfig
        },
        staleTime: 1000 * 60 * 30, // 30 minutes (config change rarement)
    })
}