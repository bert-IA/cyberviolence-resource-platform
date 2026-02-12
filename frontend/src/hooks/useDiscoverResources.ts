import { useMutation } from '@tanstack/react-query'
import { discoverResources } from '../services/api'
import type { DiscoveryFilters } from '../services/api'

export function useDiscoverResources() {
    return useMutation({
        mutationFn: (filters: DiscoveryFilters) => discoverResources(filters),
    })
}