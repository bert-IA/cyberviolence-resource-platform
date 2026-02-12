import { useMutation, useQueryClient } from '@tanstack/react-query'
import { rejectResource } from '../services/api'

export function useRejectResource() {
    const queryClient = useQueryClient()

    return useMutation({
        mutationFn: (id: string) => rejectResource(id),
        onSuccess: () => {
            // Invalider toutes les listes de ressources
            queryClient.invalidateQueries({ queryKey: ['resources'] })
        },
    })
}