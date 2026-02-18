import { useMutation, useQueryClient } from "@tanstack/react-query"
import { validateBatch, type ValidationRequest } from '../services/api'
import toast from 'react-hot-toast'

/**
 * Hook pour valider ou rejeter des ressources en batch (lot)
 * 
 * Utilise useMutation car c'est une opération de MODIFICATION (POST)
 * Contrairement à useQuery qui est pour la LECTURE (GET)
 * 
 * ✅ BONNE PRATIQUE : Le hook gère la logique métier complète,
 * y compris le feedback utilisateur (toasts). Les composants gèrent
 * uniquement l'état UI local (optimistic updates, etc.)
 */

export function useValidateBatch() {
    const queryClient = useQueryClient()

    return useMutation({
        // 🎯 MUTATION FUNCTION : La fonction qui fait l'appel API
        // Reçoit ValidationRequest = { source_ids: string[], action: 'approve'|'reject' }
        // Retourne ValidationResponse = { approved: number, rejected: number }
        mutationFn: (request: ValidationRequest) => validateBatch(request),

        // ✅ ON SUCCESS : Exécuté si l'API retourne succès (status 200)
        onSuccess: (response, variables) => {
            // 🔄 Invalide le cache → Force useQuery à refetch
            queryClient.invalidateQueries({ queryKey: ['resources'] })

            // 🍞 Toast de succès selon l'action
            if (variables.action === 'approve') {
                toast.success(`✅ ${response.approved} ressource(s) validée(s)`, {
                    duration: 3000,
                })
            } else {
                toast.success(`🗑️ ${response.rejected} ressource(s) rejetée(s)`, {
                    duration: 3000,
                })
            }
        },

        // ❌ ON ERROR : Exécuté si l'API retourne erreur (status 4xx/5xx)
        onError: (error) => {
            console.error('Validation error:', error)
            toast.error('❌ Erreur lors de la validation', {
                duration: 4000,
            })
        },
    })
}

