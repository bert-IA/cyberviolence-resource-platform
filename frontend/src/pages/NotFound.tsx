
import { LinkButton } from "../components/ui/LinkButton"

export function NotFound() {
    return (
        <div className="flex flex-col items-center justify-center min-h-screen bg-gradient-to-br from-green-50 to-purple-50">
            <div className="text-center max-w-md p-8">
                {/* Icône 404 stylisée */}
                <div className="text-9xl font-bold bg-gradient-to-r from-green-500 to-purple-600 bg-clip-text text-transparent">
                    404
                </div>

                {/* Message clair */}
                <h2 className="text-3xl font-bold text-gray-800 mt-4">
                    Page introuvable
                </h2>
                <p className="text-gray-600 mt-2 mb-8">
                    Cette page n'existe pas dans l'application.<br />
                    Vérifiez l'URL ou retournez au menu.
                </p>

                {/* Actions multiples */}
                <div className="flex gap-3 justify-center">
                    <LinkButton
                        to="/"
                        label="🏠 Menu"
                        variant="secondary"
                    />
                    <LinkButton
                        to="/configuration"
                        label="⚙️ Configuration"
                        variant="secondary"
                    />
                </div>
            </div>
        </div>
    )
}
