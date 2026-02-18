import { useQuery } from "@tanstack/react-query";
import { getResourceStats, type ResourceStats } from "../services/api";

export function useResourceStats(status: string = 'discovered') {
    return useQuery<ResourceStats>({
        queryKey: ['resources', 'stats', status],
        queryFn: () => getResourceStats(status),
        staleTime: 1000 * 60,
        refetchOnWindowFocus: true, // Refetch quand user revient sur l'onglet
    })

}