import { Button } from '../ui/Button'

interface ValidationActionsProps {
    onApprove: () => void
    onReject: () => void
    isProcessing: boolean
}

/**
 * Composant réutilisable pour les actions de validation (Garder/Rejeter).
 * 
 * Pattern Composition :
 * Utilisé comme children de DiscoveredResourceCard pour ajouter
 * des boutons de validation sans dupliquer le code d'affichage.
 * 
 * @example
 * <DiscoveredResourceCard resource={resource}>
 *   <ValidationActions
 *     onApprove={() => validate('approve')}
 *     onReject={() => validate('reject')}
 *     isProcessing={isPending}
 *   />
 * </DiscoveredResourceCard>
 */
export function ValidationActions({
    onApprove,
    onReject,
    isProcessing
}: ValidationActionsProps) {
    return (
        <>
            <Button
                label="✅ Garder"
                variant="primary"
                onClick={onApprove}
                disabled={isProcessing}

            />
            <Button
                label="❌ Rejeter"
                variant="secondary"
                onClick={onReject}
                disabled={isProcessing}

            />
        </>
    )
}
