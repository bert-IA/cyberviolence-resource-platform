import { Button } from "./Button"
interface ErrorMessageProps {
    error: Error | unknown
    onRetry?: () => void
}

export function ErrorMessage({ error, onRetry }: ErrorMessageProps) {
    const message = error instanceof Error
        ? error.message
        : 'Une erreur est survenue'

    return (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
            <div className="flex items-start">
                <span className="text-2xl mr-3">❌</span>
                <div className="flex-1">
                    <h3 className="text-sm font-medium text-red-800">Erreur</h3>
                    <p className="mt-1 text-sm text-red-700">{message}</p>
                    {onRetry && (
                        <div className="mt-3">
                            <Button
                                label="🔄 Réessayer"
                                onClick={onRetry}
                                variant="secondary"
                            />
                        </div>
                    )}
                </div>
            </div>
        </div>
    )
}