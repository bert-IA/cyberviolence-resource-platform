export function MenuPage() {
    return (
        <div className="min-h-screen bg-gradient-to-br from-purple-50 to-blue-50 flex items-center justify-center p-6">
            <div className="max-w-3xl text-center">
                <h1 className="text-5xl font-bold text-gray-900 mb-4">
                    🌍 Resource Discovery Platform
                </h1>
                <p className="text-xl text-gray-600 mb-8">
                    Interface d'administration pour gérer les ressources critiques
                </p>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-w-2xl mx-auto">
                    <div className="bg-white p-6 rounded-lg shadow-md hover:shadow-xl transition-shadow">
                        <div className="text-4xl mb-3">🗺️</div>
                        <h3 className="text-lg font-semibold text-gray-900 mb-2">
                            Pays
                        </h3>
                        <p className="text-sm text-gray-600">
                            Gérer les langues et pays supportés
                        </p>
                    </div>

                    <div className="bg-white p-6 rounded-lg shadow-md hover:shadow-xl transition-shadow">
                        <div className="text-4xl mb-3">🔍</div>
                        <h3 className="text-lg font-semibold text-gray-900 mb-2">
                            Ressource
                        </h3>
                        <p className="text-sm text-gray-600">
                            Rechercher de nouvelles ressources
                        </p>
                    </div>

                    <div className="bg-white p-6 rounded-lg shadow-md hover:shadow-xl transition-shadow">
                        <div className="text-4xl mb-3">✅</div>
                        <h3 className="text-lg font-semibold text-gray-900 mb-2">
                            Validation
                        </h3>
                        <p className="text-sm text-gray-600">
                            Valider et enrichir les ressources par pays et par catégories
                        </p>
                    </div>

                    <div className="bg-white p-6 rounded-lg shadow-md hover:shadow-xl transition-shadow">
                        <div className="text-4xl mb-3">🎯</div>
                        <h3 className="text-lg font-semibold text-gray-900 mb-2">
                            RAG
                        </h3>
                        <p className="text-sm text-gray-600">
                            Préparer les ressources pour l'indexation vectorielle
                        </p>
                    </div>
                </div>
            </div>
        </div>
    )
}