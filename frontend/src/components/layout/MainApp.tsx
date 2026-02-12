import { useState } from 'react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ConfigurationPage } from '../../pages/ConfigurationPage'
import { DiscoveryPage } from '../../pages/DiscoveryPage'

import { Header, type NavigationItem } from '../ui/Header'

// Configuration TanStack Query
const queryClient = new QueryClient({
    defaultOptions: {
        queries: {
            staleTime: 1000 * 60 * 5, // 5 minutes
            retry: 1,
        },
    },
})
interface MainAppProps {
    onDemoClick: () => void
}

type PageType = 'configuration' | 'discovery'

export function MainApp({ onDemoClick }: MainAppProps) {

    const [currentPage, setCurrentPage] = useState<PageType>('configuration')
    const navigationItems: NavigationItem<PageType>[] = [
        { label: 'Configuration Pays', value: 'configuration' },
        { label: 'Découverte Ressource', value: 'discovery' }
    ]

    return (
        <QueryClientProvider client={queryClient}>
            <div className="min-h-screen bg-gray-50">
                {/* Navigation Tabs */}
                <Header
                    title="Interface de découvertes des ressources"
                    userName='Admin'
                    buttonLabel='Démo Tailwind'
                    onDemoClick={onDemoClick}
                    navigationItems={navigationItems}
                    currentPage={currentPage}
                    onNavigate={(page: PageType) => setCurrentPage(page)}
                />

                {/* Contenu de la page active */}
                <main>
                    {currentPage === 'configuration' && <ConfigurationPage />}
                    {currentPage === 'discovery' && <DiscoveryPage />}
                </main>
            </div>
        </QueryClientProvider>
    )
}



