

function TestColor() {
    return (
        <div className="min-h-screen bg-white p-8">

            <h1 className="text-3xl font-bold mb-8 text-gray-800">
                🎨 Test des couleurs Tailwind
            </h1>

            {/* Explication échelle */}
            <div className="mb-8 bg-blue-50 border-l-4 border-blue-500 p-4">
                <p className="text-sm text-gray-700">
                    <strong>💡 Échelle Tailwind :</strong> 50 (très clair) → 500 (standard) → 950 (très foncé)
                </p>
            </div>

            {/* Boutons bleus (nuances) */}
            <div className="mb-8">
                <h2 className="text-xl font-semibold mb-4 text-gray-700">Bleus (3 nuances)</h2>
                <div className="flex gap-2 flex-wrap">
                    <button className="bg-blue-300 text-white px-4 py-2 rounded shadow">blue-300</button>
                    <button className="bg-blue-500 text-white px-4 py-2 rounded shadow">blue-500 ⭐</button>
                    <button className="bg-blue-700 text-white px-4 py-2 rounded shadow">blue-700</button>
                </div>
            </div>

            {/* Boutons gris (nuances) */}
            <div className="mb-8">
                <h2 className="text-xl font-semibold mb-4 text-gray-700">Gris (3 nuances)</h2>
                <div className="flex gap-2 flex-wrap">
                    <button className="bg-gray-200 text-gray-700 px-4 py-2 rounded shadow">gray-200</button>
                    <button className="bg-gray-500 text-white px-4 py-2 rounded shadow">gray-500 ⭐</button>
                    <button className="bg-gray-800 text-white px-4 py-2 rounded shadow">gray-800</button>
                </div>
            </div>

            {/* Palette complète */}
            <div className="mb-8">
                <h2 className="text-xl font-semibold mb-4 text-gray-700">Palette arc-en-ciel (niveau 500)</h2>
                <div className="flex gap-2 flex-wrap">
                    <button className="bg-red-500 text-white px-4 py-2 rounded shadow hover:shadow-lg transition">Rouge</button>
                    <button className="bg-orange-500 text-white px-4 py-2 rounded shadow hover:shadow-lg transition">Orange</button>
                    <button className="bg-yellow-500 text-gray-800 px-4 py-2 rounded shadow hover:shadow-lg transition">Jaune</button>
                    <button className="bg-green-500 text-white px-4 py-2 rounded shadow hover:shadow-lg transition">Vert</button>
                    <button className="bg-blue-500 text-white px-4 py-2 rounded shadow hover:shadow-lg transition">Bleu</button>
                    <button className="bg-purple-500 text-white px-4 py-2 rounded shadow hover:shadow-lg transition">Violet</button>
                    <button className="bg-pink-500 text-white px-4 py-2 rounded shadow hover:shadow-lg transition">Rose</button>
                </div>
            </div>

            {/* Hover effects */}
            <div className="mb-8">
                <h2 className="text-xl font-semibold mb-4 text-gray-700">Effet hover interactif</h2>
                <button className="bg-blue-500 hover:bg-blue-700 text-white px-6 py-3 rounded shadow-md hover:shadow-xl transition-all duration-300 transform hover:scale-105">
                    🖱️ Survole-moi avec la souris !
                </button>
            </div>

            {/* Légende */}
            <div className="mt-8 p-4 bg-gray-100 rounded">
                <h3 className="font-semibold mb-2">📝 À retenir :</h3>
                <ul className="text-sm text-gray-700 space-y-1">
                    <li>• 500 = couleur standard (recommandé)</li>
                    <li>• 600-700 = pour effets hover</li>
                    <li>• 200-300 = pour fonds clairs</li>
                    <li>• Toujours utiliser un numéro (❌ bg-blue → ✅ bg-blue-500)</li>
                </ul>
            </div>
        </div>
    )
}

export default TestColor