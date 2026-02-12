import TestColor from './TestColor'
import TestFonction from './TestFonction'
import { useState } from 'react'
import { Header, type NavigationItem } from '../ui/Header'

interface DemoTailwindProps {
    onAppClick: () => void  // 💡 Fonction pour revenir à l'app principale
}

type PageType = 'colors' | 'functions'


export function DemoTailwind({ onAppClick }: DemoTailwindProps) {
    const [currentPage, setCurrentPage] = useState<PageType>('colors')

    const navigationItems: NavigationItem<PageType>[] = [
        { label: 'gestion couleurs', value: 'colors' },
        { label: 'gestion mise en page', value: 'functions' }
    ]



    return (
        <div className="min-h-screen bg-gray-50">
            {/* Navigation Tabs */}
            <Header
                title="🎨 Démos Tailwind CSS"
                userName='Visiteur'
                buttonLabel='Retour Application'
                onDemoClick={onAppClick}
                navigationItems={navigationItems}
                currentPage={currentPage}
                onNavigate={(page: PageType) => setCurrentPage(page)}
            />
            <main>
                {currentPage === 'colors' && <TestColor />}
                {currentPage === 'functions' && <TestFonction />}

            </main>
        </div>
    )
}


