
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
                <div className="mb-6">
                    <div className="bg-gray-800 text-green-400 p-3 rounded-t font-mono text-sm">
                        className="flex gap-4"
                    </div>
                    <div className="flex gap-4 bg-blue-50 p-4 rounded-b border-2 border-gray-800">
                        <div className="bg-blue-500 text-white px-4 py-2 rounded">Item 1</div>
                        <div className="bg-blue-500 text-white px-4 py-2 rounded">Item 2</div>
                        <div className="bg-blue-500 text-white px-4 py-2 rounded">Item 3</div>
                    </div>
                    <p className="text-xs text-gray-600 mt-2 ml-2">
                        • <strong>flex</strong> : active le layout flexible (éléments côte à côte)<br />
                        • <strong>gap-4</strong> : espacement de 1rem (16px) entre les items
                    </p>
                </div>

                {/* Flex avec justify-between */}
                <div className="mb-6">
                    <div className="bg-gray-800 text-green-400 p-3 rounded-t font-mono text-sm">
                        className="flex justify-between"
                    </div>
                    <div className="flex justify-between bg-green-50 p-4 rounded-b border-2 border-gray-800">
                        <div className="bg-green-500 text-white px-4 py-2 rounded">Gauche</div>
                        <div className="bg-green-500 text-white px-4 py-2 rounded">Droite</div>
                    </div>
                    <p className="text-xs text-gray-600 mt-2 ml-2">
                        • <strong>justify-between</strong> : répartit l'espace entre les items (premier à gauche, dernier à droite)
                    </p>
                </div>

                {/* Flex avec items-center */}
                <div className="mb-6">
                    <div className="bg-gray-800 text-green-400 p-3 rounded-t font-mono text-sm">
                        className="flex items-center gap-4"
                    </div>
                    <div className="flex items-center gap-4 bg-purple-50 p-4 rounded-b border-2 border-gray-800 h-24">
                        <div className="bg-purple-500 text-white px-4 py-2 rounded">Centré</div>
                        <div className="bg-purple-500 text-white px-4 py-6 rounded">Plus grand</div>
                        <div className="bg-purple-500 text-white px-4 py-2 rounded">Centré</div>
                    </div>
                    <p className="text-xs text-gray-600 mt-2 ml-2">
                        • <strong>items-center</strong> : aligne verticalement au centre (peu importe la hauteur des items)
                    </p>
                </div>

                {/* Flex centré complet */}
                <div className="mb-6">
                    <div className="bg-gray-800 text-green-400 p-3 rounded-t font-mono text-sm">
                        className="flex justify-center items-center"
                    </div>
                    <div className="flex justify-center items-center bg-orange-50 p-4 rounded-b border-2 border-gray-800 h-24">
                        <div className="bg-orange-500 text-white px-6 py-3 rounded">Centré parfait</div>
                    </div>
                    <p className="text-xs text-gray-600 mt-2 ml-2">
                        • <strong>justify-center</strong> : centre horizontalement<br />
                        • <strong>items-center</strong> : centre verticalement<br />
                        → Combinaison = centrage parfait dans les deux directions
                    </p>
                </div>
            </div>

            {/* 2. ESPACEMENT : Padding et Margin */}
            <div className="mb-12 bg-white p-6 rounded-lg shadow">
                <h2 className="text-xl font-semibold mb-4 text-green-600">2️⃣ Espacement - Padding & Margin</h2>

                <div className="space-y-6">
                    <div>
                        <div className="bg-gray-800 text-green-400 p-3 rounded-t font-mono text-sm">
                            className="p-4"
                        </div>
                        <div className="bg-red-50 p-4 rounded-b border-2 border-gray-800">
                            <div className="bg-red-500 text-white p-4 rounded">Padding uniforme</div>
                        </div>
                        <p className="text-xs text-gray-600 mt-2 ml-2">
                            • <strong>p-4</strong> : padding de 1rem (16px) sur <strong>tous les côtés</strong> (top, right, bottom, left)
                        </p>
                    </div>

                    <div>
                        <div className="bg-gray-800 text-green-400 p-3 rounded-t font-mono text-sm">
                            className="px-6 py-3"
                        </div>
                        <div className="bg-blue-50 p-4 rounded-b border-2 border-gray-800">
                            <div className="bg-blue-500 text-white px-6 py-3 rounded inline-block">Padding personnalisé</div>
                        </div>
                        <p className="text-xs text-gray-600 mt-2 ml-2">
                            • <strong>px-6</strong> : padding horizontal (left + right) = 1.5rem (24px)<br />
                            • <strong>py-3</strong> : padding vertical (top + bottom) = 0.75rem (12px)
                        </p>
                    </div>

                    <div>
                        <div className="bg-gray-800 text-green-400 p-3 rounded-t font-mono text-sm">
                            className="mt-4 mb-2"
                        </div>
                        <div className="bg-green-50 p-4 rounded-b border-2 border-gray-800">
                            <div className="bg-green-500 text-white p-4 rounded mt-4 mb-2">Avec marges</div>
                            <div className="bg-green-500 text-white p-4 rounded">Item suivant</div>
                        </div>
                        <p className="text-xs text-gray-600 mt-2 ml-2">
                            • <strong>mt-4</strong> : margin-top de 1rem (16px)<br />
                            • <strong>mb-2</strong> : margin-bottom de 0.5rem (8px)<br />
                            → Crée un espacement de 16px au-dessus et 8px en-dessous
                        </p>
                    </div>
                </div>

                <div className="mt-6 p-4 bg-gray-100 rounded">
                    <p className="text-sm font-semibold mb-2">📐 Échelle d'espacement Tailwind :</p>
                    <div className="font-mono text-xs space-y-1">
                        <div className="flex gap-2"><span className="text-blue-600">0</span> = 0rem (0px)</div>
                        <div className="flex gap-2"><span className="text-blue-600">1</span> = 0.25rem (4px)</div>
                        <div className="flex gap-2"><span className="text-blue-600">2</span> = 0.5rem (8px)</div>
                        <div className="flex gap-2"><span className="text-blue-600">3</span> = 0.75rem (12px)</div>
                        <div className="flex gap-2"><span className="text-blue-600">4</span> = 1rem (16px)</div>
                        <div className="flex gap-2"><span className="text-blue-600">6</span> = 1.5rem (24px)</div>
                        <div className="flex gap-2"><span className="text-blue-600">8</span> = 2rem (32px)</div>
                    </div>
                </div>
            </div>

            {/* 3. BORDURES */}
            <div className="mb-12 bg-white p-6 rounded-lg shadow">
                <h2 className="text-xl font-semibold mb-4 text-purple-600">3️⃣ Bordures - Styles et épaisseurs</h2>

                <div className="space-y-6">
                    <div>
                        <div className="bg-gray-800 text-green-400 p-3 rounded-t font-mono text-sm">
                            className="border border-gray-300"
                        </div>
                        <div className="border border-gray-300 p-4 rounded-b border-t-2 border-t-gray-800">
                            <p className="text-sm font-semibold">Bordure simple (1px)</p>
                        </div>
                        <p className="text-xs text-gray-600 mt-2 ml-2">
                            • <strong>border</strong> : bordure de 1px sur tous les côtés<br />
                            • <strong>border-gray-300</strong> : couleur grise claire
                        </p>
                    </div>

                    <div>
                        <div className="bg-gray-800 text-green-400 p-3 rounded-t font-mono text-sm">
                            className="border-2 border-blue-500"
                        </div>
                        <div className="border-2 border-blue-500 p-4 rounded-b border-t-[3px] border-t-gray-800">
                            <p className="text-sm font-semibold">Bordure épaisse (2px) bleue</p>
                        </div>
                        <p className="text-xs text-gray-600 mt-2 ml-2">
                            • <strong>border-2</strong> : épaisseur de bordure 2px<br />
                            • <strong>border-blue-500</strong> : couleur bleue
                        </p>
                    </div>

                    <div>
                        <div className="bg-gray-800 text-green-400 p-3 rounded-t font-mono text-sm">
                            className="border-l-4 border-green-500"
                        </div>
                        <div className="border-l-4 border-green-500 p-4 bg-green-50 rounded-r border-gray-300">
                            <p className="text-sm font-semibold">Bordure gauche uniquement (4px)</p>
                        </div>
                        <p className="text-xs text-gray-600 mt-2 ml-2">
                            • <strong>border-l-4</strong> : bordure <strong>left</strong> (gauche) de 4px<br />
                            → Aussi dispo : border-t (top), border-r (right), border-b (bottom)
                        </p>
                    </div>

                    <div>
                        <div className="bg-gray-800 text-green-400 p-3 rounded-t font-mono text-sm">
                            className="border border-dashed rounded-lg"
                        </div>
                        <div className="border border-dashed border-gray-400 p-4 rounded-b border-t-2 border-t-gray-800">
                            <p className="text-sm font-semibold">Bordure en pointillés avec coins arrondis</p>
                        </div>
                        <p className="text-xs text-gray-600 mt-2 ml-2">
                            • <strong>border-dashed</strong> : style pointillé (au lieu de solide)<br />
                            • <strong>rounded-lg</strong> : coins arrondis de 0.5rem (8px)<br />
                            → Aussi dispo : rounded-sm, rounded-md, rounded-xl, rounded-full
                        </p>
                    </div>
                </div>
            </div>

            {/* 4. ALIGNEMENT DU TEXTE */}
            <div className="mb-12 bg-white p-6 rounded-lg shadow">
                <h2 className="text-xl font-semibold mb-4 text-orange-600">4️⃣ Alignement du texte</h2>

                <div className="space-y-6">
                    <div>
                        <div className="bg-gray-800 text-green-400 p-3 rounded-t font-mono text-sm">
                            className="text-left"
                        </div>
                        <div className="bg-blue-50 p-4 rounded-b border-2 border-gray-800 text-left">
                            <p className="font-semibold">text-left (par défaut)</p>
                            <p className="text-sm text-gray-600">Le texte est aligné à gauche.</p>
                        </div>
                    </div>

                    <div>
                        <div className="bg-gray-800 text-green-400 p-3 rounded-t font-mono text-sm">
                            className="text-center"
                        </div>
                        <div className="bg-green-50 p-4 rounded-b border-2 border-gray-800 text-center">
                            <p className="font-semibold">text-center</p>
                            <p className="text-sm text-gray-600">Le texte est centré horizontalement.</p>
                        </div>
                    </div>

                    <div>
                        <div className="bg-gray-800 text-green-400 p-3 rounded-t font-mono text-sm">
                            className="text-right"
                        </div>
                        <div className="bg-purple-50 p-4 rounded-b border-2 border-gray-800 text-right">
                            <p className="font-semibold">text-right</p>
                            <p className="text-sm text-gray-600">Le texte est aligné à droite.</p>
                        </div>
                    </div>

                    <div>
                        <div className="bg-gray-800 text-green-400 p-3 rounded-t font-mono text-sm">
                            className="text-justify"
                        </div>
                        <div className="bg-orange-50 p-4 rounded-b border-2 border-gray-800 text-justify">
                            <p className="font-semibold mb-2">text-justify</p>
                            <p className="text-sm text-gray-600">Le texte est justifié sur toute la largeur du conteneur. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.</p>
                        </div>
                    </div>
                </div>
            </div>

            {/* 5. TAILLES DE TEXTE */}
            <div className="mb-12 bg-white p-6 rounded-lg shadow">
                <h2 className="text-xl font-semibold mb-4 text-red-600">5️⃣ Tailles de texte & Poids</h2>

                <div className="space-y-4">
                    <h3 className="text-lg font-semibold text-gray-800 mb-2">📏 Tailles de texte</h3>
                    <div className="bg-gray-800 text-green-400 p-2 rounded font-mono text-xs mb-2">
                        text-xs | text-sm | text-base | text-lg | text-xl | text-2xl | text-3xl
                    </div>
                    <div className="space-y-3 bg-gray-50 p-4 rounded">
                        <div className="flex items-center gap-3">
                            <span className="font-mono text-xs text-blue-600 w-20">text-xs</span>
                            <p className="text-xs text-gray-600">0.75rem / 12px - Très petit</p>
                        </div>
                        <div className="flex items-center gap-3">
                            <span className="font-mono text-xs text-blue-600 w-20">text-sm</span>
                            <p className="text-sm text-gray-600">0.875rem / 14px - Petit</p>
                        </div>
                        <div className="flex items-center gap-3">
                            <span className="font-mono text-xs text-blue-600 w-20">text-base</span>
                            <p className="text-base text-gray-700">1rem / 16px - Normal (défaut)</p>
                        </div>
                        <div className="flex items-center gap-3">
                            <span className="font-mono text-xs text-blue-600 w-20">text-lg</span>
                            <p className="text-lg text-gray-700">1.125rem / 18px - Grand</p>
                        </div>
                        <div className="flex items-center gap-3">
                            <span className="font-mono text-xs text-blue-600 w-20">text-xl</span>
                            <p className="text-xl text-gray-800">1.25rem / 20px - Très grand</p>
                        </div>
                        <div className="flex items-center gap-3">
                            <span className="font-mono text-xs text-blue-600 w-20">text-2xl</span>
                            <p className="text-2xl text-gray-800">1.5rem / 24px - Titre</p>
                        </div>
                        <div className="flex items-center gap-3">
                            <span className="font-mono text-xs text-blue-600 w-20">text-3xl</span>
                            <p className="text-3xl text-gray-900">1.875rem / 30px - Grand titre</p>
                        </div>
                    </div>
                </div>

                <div className="mt-6">
                    <h3 className="text-lg font-semibold text-gray-800 mb-2">💪 Poids de police</h3>
                    <div className="bg-gray-800 text-green-400 p-2 rounded font-mono text-xs mb-2">
                        font-light | font-normal | font-medium | font-semibold | font-bold
                    </div>
                    <div className="space-y-2 bg-gray-50 p-4 rounded">
                        <div className="flex items-center gap-3">
                            <span className="font-mono text-xs text-blue-600 w-32">font-light</span>
                            <p className="font-light">Texte léger (300)</p>
                        </div>
                        <div className="flex items-center gap-3">
                            <span className="font-mono text-xs text-blue-600 w-32">font-normal</span>
                            <p className="font-normal">Texte normal (400 - défaut)</p>
                        </div>
                        <div className="flex items-center gap-3">
                            <span className="font-mono text-xs text-blue-600 w-32">font-medium</span>
                            <p className="font-medium">Texte moyen (500)</p>
                        </div>
                        <div className="flex items-center gap-3">
                            <span className="font-mono text-xs text-blue-600 w-32">font-semibold</span>
                            <p className="font-semibold">Texte semi-gras (600)</p>
                        </div>
                        <div className="flex items-center gap-3">
                            <span className="font-mono text-xs text-blue-600 w-32">font-bold</span>
                            <p className="font-bold">Texte gras (700)</p>
                        </div>
                    </div>
                </div>
            </div>

            {/* 6. OMBRES */}
            <div className="mb-12 bg-white p-6 rounded-lg shadow">
                <h2 className="text-xl font-semibold mb-4 text-indigo-600">6️⃣ Ombres (Shadows)</h2>

                <div className="bg-gray-800 text-green-400 p-2 rounded font-mono text-xs mb-4">
                    shadow-sm | shadow | shadow-md | shadow-lg | shadow-xl | shadow-2xl
                </div>

                <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3 bg-gray-100 p-6 rounded">
                    <div>
                        <div className="bg-gray-700 text-yellow-400 px-2 py-1 rounded-t text-xs font-mono">shadow-sm</div>
                        <div className="shadow-sm bg-white p-4 rounded-b">
                            <p className="text-sm font-semibold">Ombre très légère</p>
                            <p className="text-xs text-gray-600">Subtile, presque invisible</p>
                        </div>
                    </div>

                    <div>
                        <div className="bg-gray-700 text-yellow-400 px-2 py-1 rounded-t text-xs font-mono">shadow</div>
                        <div className="shadow bg-white p-4 rounded-b">
                            <p className="text-sm font-semibold">Ombre standard</p>
                            <p className="text-xs text-gray-600">Légère élévation</p>
                        </div>
                    </div>

                    <div>
                        <div className="bg-gray-700 text-yellow-400 px-2 py-1 rounded-t text-xs font-mono">shadow-md</div>
                        <div className="shadow-md bg-white p-4 rounded-b">
                            <p className="text-sm font-semibold">Ombre medium</p>
                            <p className="text-xs text-gray-600">Élévation modérée</p>
                        </div>
                    </div>

                    <div>
                        <div className="bg-gray-700 text-yellow-400 px-2 py-1 rounded-t text-xs font-mono">shadow-lg</div>
                        <div className="shadow-lg bg-white p-4 rounded-b">
                            <p className="text-sm font-semibold">Ombre large</p>
                            <p className="text-xs text-gray-600">Forte élévation</p>
                        </div>
                    </div>

                    <div>
                        <div className="bg-gray-700 text-yellow-400 px-2 py-1 rounded-t text-xs font-mono">shadow-xl</div>
                        <div className="shadow-xl bg-white p-4 rounded-b">
                            <p className="text-sm font-semibold">Ombre extra-large</p>
                            <p className="text-xs text-gray-600">Très marquée</p>
                        </div>
                    </div>

                    <div>
                        <div className="bg-gray-700 text-yellow-400 px-2 py-1 rounded-t text-xs font-mono">shadow-2xl</div>
                        <div className="shadow-2xl bg-white p-4 rounded-b">
                            <p className="text-sm font-semibold">Ombre maximale</p>
                            <p className="text-xs text-gray-600">Effet dramatique</p>
                        </div>
                    </div>
                </div>

                <p className="text-xs text-gray-600 mt-4 ml-2">
                    💡 <strong>Astuce :</strong> Les ombres donnent de la profondeur et aident à créer une hiérarchie visuelle. Plus l'ombre est grande, plus l'élément semble "flotter" au-dessus de la page.
                </p>
            </div>

            {/* 7. RESPONSIVE DESIGN */}
            <div className="mb-12 bg-white p-6 rounded-lg shadow">
                <h2 className="text-xl font-semibold mb-4 text-pink-600">7️⃣ Responsive - Breakpoints</h2>

                <div className="space-y-6">
                    {/* Breakpoints table */}
                    <div className="bg-gray-800 text-white p-4 rounded">
                        <h3 className="font-mono text-green-400 text-sm mb-3">📱 Breakpoints Tailwind</h3>
                        <div className="space-y-2 text-xs">
                            <div className="flex items-center justify-between border-b border-gray-600 pb-2">
                                <span className="font-mono text-yellow-400">Par défaut</span>
                                <span className="text-gray-400">0px → Tous les écrans (mobile first)</span>
                            </div>
                            <div className="flex items-center justify-between border-b border-gray-600 pb-2">
                                <span className="font-mono text-yellow-400">sm:</span>
                                <span className="text-gray-400">≥ 640px → Petite tablette</span>
                            </div>
                            <div className="flex items-center justify-between border-b border-gray-600 pb-2">
                                <span className="font-mono text-yellow-400">md:</span>
                                <span className="text-gray-400">≥ 768px → Tablette</span>
                            </div>
                            <div className="flex items-center justify-between border-b border-gray-600 pb-2">
                                <span className="font-mono text-yellow-400">lg:</span>
                                <span className="text-gray-400">≥ 1024px → Desktop</span>
                            </div>
                            <div className="flex items-center justify-between border-b border-gray-600 pb-2">
                                <span className="font-mono text-yellow-400">xl:</span>
                                <span className="text-gray-400">≥ 1280px → Large desktop</span>
                            </div>
                            <div className="flex items-center justify-between">
                                <span className="font-mono text-yellow-400">2xl:</span>
                                <span className="text-gray-400">≥ 1536px → Extra large</span>
                            </div>
                        </div>
                    </div>

                    {/* Example 1: Responsive text */}
                    <div>
                        <div className="bg-gray-800 text-green-400 p-3 rounded-t font-mono text-sm">
                            className="text-base md:text-lg lg:text-xl"
                        </div>
                        <div className="bg-pink-50 p-4 rounded-b border-2 border-gray-800">
                            <p className="text-base md:text-lg lg:text-xl font-semibold">
                                Ce texte s'agrandit avec la taille de l'écran
                            </p>
                        </div>
                        <p className="text-xs text-gray-600 mt-2 ml-2">
                            • <strong>text-base</strong> : 16px sur mobile (par défaut)<br />
                            • <strong>md:text-lg</strong> : 18px sur tablette (≥ 768px)<br />
                            • <strong>lg:text-xl</strong> : 20px sur desktop (≥ 1024px)
                        </p>
                    </div>

                    {/* Example 2: Responsive grid */}
                    <div>
                        <div className="bg-gray-800 text-green-400 p-3 rounded-t font-mono text-sm">
                            className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4"
                        </div>
                        <div className="p-4 rounded-b border-2 border-gray-800 bg-gradient-to-br from-pink-50 to-purple-50">
                            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                                <div className="bg-pink-500 text-white p-4 rounded text-center font-semibold">
                                    Carte 1
                                </div>
                                <div className="bg-pink-500 text-white p-4 rounded text-center font-semibold">
                                    Carte 2
                                </div>
                                <div className="bg-pink-500 text-white p-4 rounded text-center font-semibold">
                                    Carte 3
                                </div>
                            </div>
                        </div>
                        <p className="text-xs text-gray-600 mt-2 ml-2">
                            • <strong>grid-cols-1</strong> : 1 colonne sur mobile (100% de largeur)<br />
                            • <strong>md:grid-cols-2</strong> : 2 colonnes sur tablette<br />
                            • <strong>lg:grid-cols-3</strong> : 3 colonnes sur desktop<br />
                            💡 <em>Redimensionne ta fenêtre pour voir le changement !</em>
                        </p>
                    </div>

                    {/* Example 3: Hidden/visible */}
                    <div>
                        <div className="bg-gray-800 text-green-400 p-3 rounded-t font-mono text-sm">
                            className="hidden md:block" ou "block md:hidden"
                        </div>
                        <div className="p-4 rounded-b border-2 border-gray-800 bg-blue-50">
                            <div className="space-y-3">
                                <div className="hidden md:block bg-green-500 text-white p-3 rounded">
                                    <span className="font-semibold">✅ Visible uniquement sur tablette/desktop</span>
                                    <span className="text-xs ml-2">(hidden md:block)</span>
                                </div>
                                <div className="block md:hidden bg-orange-500 text-white p-3 rounded">
                                    <span className="font-semibold">📱 Visible uniquement sur mobile</span>
                                    <span className="text-xs ml-2">(block md:hidden)</span>
                                </div>
                            </div>
                        </div>
                        <p className="text-xs text-gray-600 mt-2 ml-2">
                            • <strong>hidden</strong> : masque l'élément<br />
                            • <strong>block</strong> : affiche l'élément<br />
                            • <strong>md:block</strong> : affiche à partir de 768px<br />
                            • <strong>md:hidden</strong> : masque à partir de 768px
                        </p>
                    </div>

                    {/* Mobile first principle */}
                    <div className="bg-gradient-to-r from-purple-100 to-pink-100 p-4 rounded border-2 border-purple-300">
                        <h3 className="font-bold text-purple-800 mb-2 flex items-center gap-2">
                            📱 Principe "Mobile First"
                        </h3>
                        <p className="text-sm text-gray-700 mb-2">
                            Avec Tailwind, tu codes d'abord pour mobile, puis tu ajoutes les breakpoints pour les grands écrans :
                        </p>
                        <div className="bg-white p-3 rounded font-mono text-xs text-gray-800 border border-purple-200">
                            <span className="text-blue-600">text-sm</span> → Mobile (défaut)<br />
                            <span className="text-green-600">md:text-base</span> → Tablette<br />
                            <span className="text-purple-600">lg:text-lg</span> → Desktop
                        </div>
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