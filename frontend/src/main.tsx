
import { createRoot } from 'react-dom/client'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ReactQueryDevtools } from '@tanstack/react-query-devtools'
import { BrowserRouter } from 'react-router-dom'
import './index.css'
import { App } from './App.tsx'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5,        // 5 minutes
      gcTime: 1000 * 60 * 10,       // 10 minutes
      refetchOnWindowFocus: false,     // Pas de refetch au focus
      retry: 1,               // Combien de fois ?
    },
  },
})
createRoot(document.getElementById('root')!).render(
  // ⚠️ StrictMode désactivé en dev pour éviter double toast
  // En production, réactiver pour meilleure détection de bugs
  // <StrictMode>
  <BrowserRouter>
    <QueryClientProvider client={queryClient}>
      <App />
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  </BrowserRouter>
  // </StrictMode>
)
