import { useState } from 'react'
import { MainApp } from './components/layout/MainApp'
import { DemoTailwind } from './components/demo/DemoTailwind'


/**
 * 🎓 CONCEPT REACT : State-driven UI
 * 
 * Ce composant est le "chef d'orchestre" de l'application.
 * Il gère quel composant afficher via un state 'view'.
 * 
 * Flow :
 * 1. User clique "Démo Tailwind" dans Header
 * 2. handleShowDemo() est appelé (callback prop)
 * 3. setView('demo') change le state
 * 4. React re-rend et affiche DemoTailwind
 * 5. User clique "Retour" dans la démo
 * 6. handleShowApp() remet view à 'app'
 */

type View = 'app' | 'demo'

function App() {
  // 🎯 State qui contrôle quelle vue afficher
  const [view, setView] = useState<View>('app')

  // 📝 Fonction pour afficher la démo (passée à MainApp)
  const handleShowDemo = () => {
    setView('demo')
  }

  // 📝 Fonction pour revenir à l'app (passée à DemoTailwind)
  const handleShowApp = () => {
    setView('app')
  }

  // 🔀 Conditional Rendering : affiche le bon composant selon le state
  if (view === 'demo') {
    return <DemoTailwind onAppClick={handleShowApp} />
  }

  return <MainApp onDemoClick={handleShowDemo} />
}

export default App