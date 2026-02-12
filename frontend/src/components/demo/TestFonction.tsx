
function TestFonction() {
    return (
        <div className="min-h-screen bg-white p-8">

            <h1 className="text-3xl font-bold mb-8 text-gray-800">
                🧰 Mises en page Tailwind - Les essentiels
            </h1>

            {/* 1. FLEXBOX : Layout horizontal */}
            <div className="mb-12 bg-white p-6 rounded-lg shadow">
                <h2 className="text-xl font-semibold mb-4 text-blue-600">1️⃣ Flexbox - Layout horizontal</h2>

                {/* Flex basique */}
                <div className="mb-4">
                    <p className="text-sm text-gray-600 mb-2">flex + gap-4 (espacement automatique)</p>
                    <div className="flex gap-4 bg-blue-50 p-4 rounded">
                        <div className="bg-blue-500 text-white px-4 py-2 rounded">Item 1</div>
                        <div className="bg-blue-500 text-white px-4 py-2 rounded">Item 2</div>
                        <div className="bg-blue-500 text-white px-4 py-2 rounded">Item 3</div>
                    </div>
                </div>

                {/* Flex avec justify-between */}
                <div className="mb-4">
                    <p className="text-sm text-gray-600 mb-2">flex + justify-between (espace entre items)</p>
                    <div className="flex justify-between bg-green-50 p-4 rounded">
                        <div className="bg-green-500 text-white px-4 py-2 rounded">Gauche</div>
                        <div className="bg-green-500 text-white px-4 py-2 rounded">Droite</div>
                    </div>
                </div>

                {/* Flex avec items-center */}
                <div className="mb-4">
                    <p className="text-sm text-gray-600 mb-2">flex + items-center (centré verticalement)</p>
                    <div className="flex items-center gap-4 bg-purple-50 p-4 rounded h-24">
                        <div className="bg-purple-500 text-white px-4 py-2 rounded">Centré</div>
                        <div className="bg-purple-500 text-white px-4 py-6 rounded">Plus grand</div>
                        <div className="bg-purple-500 text-white px-4 py-2 rounded">Centré</div>
                    </div>
                </div>

                {/* Flex centré complet */}
                <div>
                    <p className="text-sm text-gray-600 mb-2">flex + justify-center + items-center (centré H+V)</p>
                    <div className="flex justify-center items-center bg-orange-50 p-4 rounded h-24">
                        <div className="bg-orange-500 text-white px-6 py-3 rounded">Centré parfait</div>
                    </div>
                </div>
            </div>

            {/* 2. ESPACEMENT : Padding et Margin */}
            <div className="mb-12 bg-white p-6 rounded-lg shadow">
                <h2 className="text-xl font-semibold mb-4 text-green-600">2️⃣ Espacement - Padding & Margin</h2>

                <div className="space-y-4">
                    <div className="bg-red-50 p-4 rounded">
                        <p className="text-sm text-gray-600 mb-2">p-4 = padding de 1rem (16px) sur tous les côtés</p>
                        <div className="bg-red-500 text-white p-4 rounded">Padding uniforme</div>
                    </div>

                    <div className="bg-blue-50 p-4 rounded">
                        <p className="text-sm text-gray-600 mb-2">px-6 py-3 = padding horizontal 1.5rem, vertical 0.75rem</p>
                        <div className="bg-blue-500 text-white px-6 py-3 rounded inline-block">Padding custom</div>
                    </div>

                    <div className="bg-green-50 p-4 rounded">
                        <p className="text-sm text-gray-600 mb-2">mt-4 mb-2 = margin top 1rem, margin bottom 0.5rem</p>
                        <div className="bg-green-500 text-white p-4 rounded mt-4 mb-2">Avec marges</div>
                        <div className="bg-green-500 text-white p-4 rounded">Item suivant</div>
                    </div>
                </div>

                <div className="mt-6 p-4 bg-gray-100 rounded">
                    <p className="text-sm font-semibold mb-1">📐 Échelle d'espacement :</p>
                    <p className="text-xs text-gray-600">1 = 0.25rem (4px) • 2 = 0.5rem (8px) • 4 = 1rem (16px) • 6 = 1.5rem
                        (24px) • 8 = 2rem (32px)</p>
                </div>
            </div>

            {/* 3. BORDURES */}
            <div className="mb-12 bg-white p-6 rounded-lg shadow">
                <h2 className="text-xl font-semibold mb-4 text-purple-600">3️⃣ Bordures - Styles et épaisseurs</h2>

                <div className="grid gap-4 md:grid-cols-2">
                    <div className="border border-gray-300 p-4 rounded">
                        <p className="text-sm font-semibold">border (1px gris par défaut)</p>
                    </div>

                    <div className="border-2 border-blue-500 p-4 rounded">
                        <p className="text-sm font-semibold">border-2 border-blue-500</p>
                    </div>

                    <div className="border-4 border-red-500 p-4 rounded">
                        <p className="text-sm font-semibold">border-4 border-red-500</p>
                    </div>

                    <div className="border-l-4 border-green-500 p-4 bg-green-50">
                        <p className="text-sm font-semibold">border-l-4 (bordure gauche)</p>
                    </div>

                    <div className="border border-dashed border-gray-400 p-4 rounded">
                        <p className="text-sm font-semibold">border-dashed</p>
                    </div>

                    <div className="border-2 border-purple-500 rounded-lg p-4">
                        <p className="text-sm font-semibold">rounded-lg (coins arrondis)</p>
                    </div>
                </div>
            </div>

            {/* 4. ALIGNEMENT DU TEXTE */}
            <div className="mb-12 bg-white p-6 rounded-lg shadow">
                <h2 className="text-xl font-semibold mb-4 text-orange-600">4️⃣ Alignement du texte</h2>

                <div className="space-y-4">
                    <div className="bg-blue-50 p-4 rounded text-left border-l-4 border-blue-500">
                        <p className="font-semibold">text-left (par défaut)</p>
                        <p className="text-sm text-gray-600">Le texte est aligné à gauche.</p>
                    </div>

                    <div className="bg-green-50 p-4 rounded text-center border-l-4 border-green-500">
                        <p className="font-semibold">text-center</p>
                        <p className="text-sm text-gray-600">Le texte est centré.</p>
                    </div>

                    <div className="bg-purple-50 p-4 rounded text-right border-l-4 border-purple-500">
                        <p className="font-semibold">text-right</p>
                        <p className="text-sm text-gray-600">Le texte est aligné à droite.</p>
                    </div>

                    <div className="bg-orange-50 p-4 rounded text-justify border-l-4 border-orange-500">
                        <p className="font-semibold">text-justify</p>
                        <p className="text-sm text-gray-600">Le texte est justifié sur toute la largeur. Lorem ipsum dolor sit
                            amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna
                            aliqua.</p>
                    </div>
                </div>
            </div>

            {/* 5. TAILLES DE TEXTE */}
            <div className="mb-12 bg-white p-6 rounded-lg shadow">
                <h2 className="text-xl font-semibold mb-4 text-red-600">5️⃣ Tailles de texte & Poids</h2>

                <div className="space-y-3">
                    <p className="text-xs text-gray-600">text-xs (0.75rem / 12px) - Très petit</p>
                    <p className="text-sm text-gray-600">text-sm (0.875rem / 14px) - Petit</p>
                    <p className="text-base text-gray-700">text-base (1rem / 16px) - Normal (défaut)</p>
                    <p className="text-lg text-gray-700">text-lg (1.125rem / 18px) - Grand</p>
                    <p className="text-xl text-gray-800">text-xl (1.25rem / 20px) - Très grand</p>
                    <p className="text-2xl font-bold text-gray-800">text-2xl + font-bold - Titre</p>
                    <p className="text-3xl font-bold text-gray-900">text-3xl + font-bold - Grand titre</p>
                </div>

                <div className="mt-6 space-y-2">
                    <p className="font-light">font-light (300)</p>
                    <p className="font-normal">font-normal (400) - Défaut</p>
                    <p className="font-medium">font-medium (500)</p>
                    <p className="font-semibold">font-semibold (600)</p>
                    <p className="font-bold">font-bold (700)</p>
                </div>
            </div>

            {/* 6. OMBRES */}
            <div className="mb-12 bg-white p-6 rounded-lg shadow">
                <h2 className="text-xl font-semibold mb-4 text-indigo-600">6️⃣ Ombres (Shadows)</h2>

                <div className="grid gap-4 md:grid-cols-3">
                    <div className="shadow-sm bg-white p-4 rounded border">
                        <p className="text-sm font-semibold">shadow-sm</p>
                        <p className="text-xs text-gray-600">Ombre légère</p>
                    </div>

                    <div className="shadow bg-white p-4 rounded">
                        <p className="text-sm font-semibold">shadow</p>
                        <p className="text-xs text-gray-600">Ombre standard</p>
                    </div>

                    <div className="shadow-md bg-white p-4 rounded">
                        <p className="text-sm font-semibold">shadow-md</p>
                        <p className="text-xs text-gray-600">Ombre medium</p>
                    </div>

                    <div className="shadow-lg bg-white p-4 rounded">
                        <p className="text-sm font-semibold">shadow-lg</p>
                        <p className="text-xs text-gray-600">Ombre large</p>
                    </div>

                    <div className="shadow-xl bg-white p-4 rounded">
                        <p className="text-sm font-semibold">shadow-xl</p>
                        <p className="text-xs text-gray-600">Ombre extra-large</p>
                    </div>

                    <div className="shadow-2xl bg-white p-4 rounded">
                        <p className="text-sm font-semibold">shadow-2xl</p>
                        <p className="text-xs text-gray-600">Ombre maximale</p>
                    </div>
                </div>
            </div>

            {/* 7. RESPONSIVE DESIGN */}
            <div className="mb-12 bg-white p-6 rounded-lg shadow">
                <h2 className="text-xl font-semibold mb-4 text-pink-600">7️⃣ Responsive - Breakpoints</h2>

                <div className="bg-pink-50 p-6 rounded">
                    <p className="text-base mb-4 md:text-lg lg:text-xl">
                        Ce texte change de taille selon l'écran
                    </p>

                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                        <div className="bg-pink-500 text-white p-4 rounded">1 col mobile</div>
                        <div className="bg-pink-500 text-white p-4 rounded">2 col tablette</div>
                        <div className="bg-pink-500 text-white p-4 rounded">3 col desktop</div>
                    </div>

                    <div className="mt-4 p-3 bg-white rounded">
                        <p className="text-xs font-semibold mb-1">📱 Breakpoints :</p>
                        <p className="text-xs text-gray-600">
                            sm: 640px • md: 768px • lg: 1024px • xl: 1280px • 2xl: 1536px
                        </p>
                    </div>
                </div>
            </div>

            {/* RÉSUMÉ FINAL */}
            <div className="bg-gradient-to-r from-blue-500 to-purple-600 text-white p-8 rounded-lg shadow-xl">
                <h2 className="text-2xl font-bold mb-4">📋 Résumé des essentiels Tailwind</h2>

                <div className="grid md:grid-cols-2 gap-6 text-sm">
                    <div>
                        <h3 className="font-bold mb-2">Layout</h3>
                        <ul className="space-y-1 text-blue-100">
                            <li>• flex = conteneur flexible</li>
                            <li>• justify-between = espacement</li>
                            <li>• items-center = centré vertical</li>
                            <li>• gap-4 = espacement entre items</li>
                        </ul>
                    </div>

                    <div>
                        <h3 className="font-bold mb-2">Espacement</h3>
                        <ul className="space-y-1 text-blue-100">
                            <li>• p-4 = padding uniforme</li>
                            <li>• px-6 py-3 = padding personnalisé</li>
                            <li>• m-4 = margin uniforme</li>
                            <li>• mt-8 mb-4 = margin ciblée</li>
                        </ul>
                    </div>

                    <div>
                        <h3 className="font-bold mb-2">Couleurs</h3>
                        <ul className="space-y-1 text-blue-100">
                            <li>• bg-blue-500 = fond bleu</li>
                            <li>• text-white = texte blanc</li>
                            <li>• border-gray-300 = bordure grise</li>
                            <li>• Toujours un numéro (50-950)</li>
                        </ul>
                    </div>

                    <div>
                        <h3 className="font-bold mb-2">Style</h3>
                        <ul className="space-y-1 text-blue-100">
                            <li>• rounded = coins arrondis</li>
                            <li>• shadow-md = ombre</li>
                            <li>• font-bold = texte gras</li>
                            <li>• hover:bg-blue-700 = effet survol</li>
                        </ul>
                    </div>
                </div>

                <div className="mt-6 p-4 bg-white/10 rounded backdrop-blur">
                    <p className="text-sm">
                        💡 <strong>Conseil pro :</strong> Combine ces classes pour créer des interfaces modernes.
                        Exemple : <code
                            className="bg-black/20 px-2 py-1 rounded">flex items-center gap-4 p-4 bg-white rounded-lg shadow-md</code>
                    </p>
                </div>
            </div>
        </div>
    )
}

export default TestFonction