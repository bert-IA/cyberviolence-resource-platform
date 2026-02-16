import { TestColor } from './TestColor'
import { TestFonction } from './TestFonction'
import { LinkButton } from '../ui/LinkButton'
import { Routes, Route } from "react-router-dom"



export function DemoTailwind() {

    return (
        <>
            <header className="bg-green-400 shadow-sm border-b border-gray-200">
                <div className="max-w-7xl mx-auto px-6 py-4">
                    <div className="flex justify-between items-center">
                        {/* Partie gauche : Titre + Navigation */}
                        <div className="flex flex-col gap-4">
                            <h1 className="text-3xl font-bold text-gray-900">
                                🎨 Démos Tailwind CSS
                            </h1>

                            <nav>
                                <LinkButton
                                    to="/demo/colors"
                                    label="Couleurs"
                                />
                                <LinkButton
                                    to="/demo"
                                    label="Pagination"
                                />
                            </nav>
                        </div>


                        <div className="flex items-center gap-2">
                            <span className="text-sm">👤</span>
                            <span>Visiteur</span>
                        </div>
                    </div>
                </div>
            </header >

            <main>
                <Routes>
                    <Route path='/colors' element={<TestColor />} />
                    <Route path='/' element={<TestFonction />} />
                </Routes>
            </main>
        </>


    )
}


