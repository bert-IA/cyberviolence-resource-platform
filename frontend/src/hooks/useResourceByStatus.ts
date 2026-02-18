import { useQuery } from "@tanstack/react-query";
import { fetchResources, type Resource } from "../services/api";

export function useResourcesByStatus(status: string) {
    return useQuery<Resource[]>({
        queryKey: ['resources', status],
        queryFn: () => fetchResources(status),
        staleTime: 1000 * 60 * 2,
    })
}