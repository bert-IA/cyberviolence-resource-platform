import { useMutation, useQueryClient } from '@tanstack/react-query'
import { validateResource } from '../services/api'

export function useValidateResource() {
    const queryClient = useQueryClient()

    return useMutation({
        mutationFn: (id: string) => validateResource(id),
        onSuccess: () => {
            // Invalider TOUTES les listes de ressources
            queryClient.invalidateQueries({ queryKey: ['resources'] })
        },
    })
}