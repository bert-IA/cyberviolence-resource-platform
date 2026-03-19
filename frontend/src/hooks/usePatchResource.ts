import { useMutation, useQueryClient } from "@tanstack/react-query";
import { updateResource, type Resource } from "../services/api";

export function usePatchResource() {
    const queryClient = useQueryClient()

    return useMutation({
        mutationFn: ({ id, data }: { id: string, data: Partial<Resource> }) => updateResource(id, data),
        onSuccess: () => {
            // Invalider toutes les listes de ressources
            queryClient.invalidateQueries({ queryKey: ['resources'] })
        },
    })
}