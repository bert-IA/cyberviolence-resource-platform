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
                            Plateforme de resources RAG
                        </h1>
                        <p className="text-md text-gray-500">
                            Interface d'administration
                        </p>
                    </div>

                    <div className="flex items-center gap-3">
                        <div className="text-right">
                            <div className="text-md font-medium text-gray-900">{userName}</div>
                            <div className="text-xs text-gray-500">Administrateur</div>
                        </div>
                        <div className="w-10 h-10 rounded-full bg-purple-500 flex items-center justify-center text-white font-semibold">
                            {userName.charAt(0).toUpperCase()}
                        </div>
                    </div>
                </div>
            </div>
        </header>
    )
}

