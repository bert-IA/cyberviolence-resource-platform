import { useQuery } from '@tanstack/react-query'
import { fetchLanguagesConfig } from '../services/api'



export function useCountriesLanguagesConfig() {
    return useQuery({
        queryKey: ['config', 'languages'],
        queryFn: () => fetchLanguagesConfig(),
        staleTime: Infinity
    })
}