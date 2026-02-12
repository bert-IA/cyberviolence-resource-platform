import TestColor from './TestColor'
import TestFonction from './TestFonction'
import { useState } from 'react'
import { Header, type NavigationItem } from '../ui/Header'

interface DemoTailwindProps {
    onAppClick: () => void  // 💡 Fonction pour revenir à l'app principale
}

type DemoPageType = 'colors' | 'functions'


export function DemoTailwind({ onAppClick }: DemoTailwindProps) {
    const [currentPage, setCurrentPage] = useState<DemoPageType>('colors')

    const navigationItems: NavigationItem<DemoPageType>[] = [
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
                onNavigate={setCurrentPage}
            />
            <main>
                {currentPage === 'colors' && <TestColor />}
                {currentPage === 'functions' && <TestFonction />}

            </main>
        </div>
    )
}


