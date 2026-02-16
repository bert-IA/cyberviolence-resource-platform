import { Outlet } from 'react-router-dom'
import { AppHeader } from '../ui/AppHeader'
import { Sidebar } from './Sidebar'

export function MainLayout() {
    const userName = "Bert"
    return (
        <div className="min-h-screen bg-gray-50">
            {/* Header toujours visible */}
            <AppHeader userName={userName} />

            {/* Container principal : Sidebar + Contenu */}
            <div className="flex">
                {/* Sidebar gauche */}
                <Sidebar />

                {/* Zone de contenu dynamique */}
                <main className="flex-1 p-6">
                    <Outlet />  {/* ← Les pages enfants s'affichent ICI */}
                </main>
            </div>
        </div>
    )
}