import { useQuery } from '@tanstack/react-query'
import { fetchResourceById } from '../services/api'

export function useRuseesourceById(id: string) {
    return useQuery({
        queryKey: ['resource', id],
        queryFn: () => fetchResourceById(id),
        enabled: !!id,  // Ne fetch que si ID fourni
    })
}