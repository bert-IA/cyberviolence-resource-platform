import { useQuery } from '@tanstack/react-query'
import { fetchResources } from '../services/api'

export function useResources(status?: string) {
    return useQuery({
        queryKey: ['resources', status],  // Cache différent par status
        queryFn: () => fetchResources(status),
        staleTime: 1000 * 60 * 2,  // 2 minutes (plus court que défaut)
    })
}