import { Routes, Route } from 'react-router-dom'
import { MainApp } from './components/layout/MainApp'
import { DemoTailwind } from './components/demo/DemoTailwind'





export function App() {
  return (
    <div className='min-h-screen bg-gray-50'>

      <Routes>
        <Route path='/*' element={<MainApp />} />
        <Route path='/demo/*' element={<DemoTailwind />} />
      </Routes>
    </div>
  )
}