import { Routes, Route } from 'react-router-dom'
import { DemoTailwind } from './components/demo/DemoTailwind'
import { MainLayout } from './components/layout/MainLayout'
import { MenuPage } from './pages/MenuPage'
import { ConfigurationPage } from './pages/ConfigurationPage'
import { DiscoveryPage } from './pages/DiscoveryPage'
import { NotFound } from './pages/NotFound'

export function App() {
  return (
    <div className="min-h-screen bg-gray-50">
      <Routes>
        <Route path="/demo/*" element={<DemoTailwind />} />
        {/* Routes avec layout (Sidebar + Header) */}
        <Route element={<MainLayout />}>
          <Route path="/" element={<MenuPage />} />
          <Route path="/configuration" element={<ConfigurationPage />} />
          <Route path="/decouverte" element={<DiscoveryPage />} />

          {/* Pages futures (décommente quand prêt) */}
          {/* <Route path="/validation" element={<ValidationPage />} /> */}
          {/* <Route path="/rag" element={<RagPage />} /> */}
        </Route>

        {/* Route 404 */}
        <Route path="*" element={<NotFound />} />
      </Routes>
    </div>
  )
}