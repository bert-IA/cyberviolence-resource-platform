import { useMutation } from '@tanstack/react-query'
import { discoverResources } from '../services/api'
import type { DiscoveryFilters } from '../services/api'

export function useDiscoverResources() {
    return useMutation({
        mutationFn: async (filters: DiscoveryFilters) => {
            console.log('🔍 [useDiscoverResources] Envoi requête avec:', filters)
            const result = await discoverResources(filters)
            console.log('✅ [useDiscoverResources] Résultat reçu:', result)
            return result
        },
        onError: (error) => {
            console.error('❌ [useDiscoverResources] Erreur:', error)
        },
    })
}