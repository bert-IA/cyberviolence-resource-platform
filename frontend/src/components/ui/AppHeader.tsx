import { LinkButton } from "./LinkButton"


interface AppHeaderProps {

    userName: string

}

export function AppHeader({ userName }: AppHeaderProps) {

    return (
        <header className="bg-green-400 shadow-sm border-b border-gray-200">
            <div className="max-w-7xl mx-auto px-6 py-4">
                <div className="flex justify-between items-center">
                    {/* Partie gauche : Titre + Navigation */}
                    <div className="flex flex-col gap-4">
                        <h1 className="text-3xl font-bold text-gray-900">
                            INTERFACE DE DECOUVERTES DES RESSOURCES RAG
                        </h1>


                        <nav className="flex gap-3">
                            <LinkButton
                                label="🏠Menu"
                                to="/" />
                            <LinkButton
                                label="🗺️Pays"
                                to="/configuration" />
                            <LinkButton
                                label="🔍Ressource"
                                to="/decouverte" />
                            <LinkButton
                                label="✅Validation"
                                to="/validation" />
                            <LinkButton
                                label="🎯RAG"
                                to="/rag" />

                        </nav>
                    </div>


                    <div className="flex items-center gap-2">
                        <span className="text-sm">👤</span>
                        <span>{userName}</span>
                    </div>
                </div>
            </div>
        </header>
    )
}

