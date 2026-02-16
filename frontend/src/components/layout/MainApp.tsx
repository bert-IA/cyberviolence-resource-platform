
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { Routes, Route } from 'react-router-dom'
import { MenuPage } from '../../pages/MenuPage'
import { ConfigurationPage } from '../../pages/ConfigurationPage'
import { AppHeader } from '../ui/AppHeader'
import { DiscoveryPage } from '../../pages/DiscoveryPage'
import { NotFound } from '../../pages/NotFound'


// Configuration TanStack Query
const queryClient = new QueryClient({
    defaultOptions: {
        queries: {
            staleTime: 1000 * 60 * 5, // 5 minutes
            retry: 1,
        },
    },
})


export function MainApp() {
    const userName = "admin"

    return (

        <QueryClientProvider client={queryClient}>
            <div className="min-h-screen bg-gray-50">
                {/* Navigation Tabs */}
                <AppHeader userName={userName} />

                {/* Contenu de la page active */}
                <main>
                    <Routes>
                        <Route path="/" element={<MenuPage />} />
                        <Route path="/configuration" element={<ConfigurationPage />} />
                        <Route path="/decouverte" element={<DiscoveryPage />} />
                        {/* 
                        <Route path="/validation" element={<ValidationPage />} />
                        <Route path="/rag" element={<RagPage />} /> 
                        */}
                        <Route path="/*" element={<NotFound />} />

                    </Routes>
                </main>
            </div>
        </QueryClientProvider>
    )
}



