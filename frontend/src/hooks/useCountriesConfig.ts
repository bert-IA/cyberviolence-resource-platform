import { useQuery } from '@tanstack/react-query'
import { API_BASE_URL, AUTH_TOKEN } from '../services/api'

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
            const response = await fetch(`${API_BASE_URL}/geographic/countries`, {
                headers: { 'Authorization': AUTH_TOKEN }
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