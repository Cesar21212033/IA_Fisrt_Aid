import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Home from './pages/Home'
import ImageAnalysis from './pages/ImageAnalysis'
import TextAnalysis from './pages/TextAnalysis'
import DiagnosisResults from './pages/DiagnosisResults'
import DiagnosticHistory from './pages/DiagnosticHistory'
import FirstAidGuide from './pages/FirstAidGuide'

/**
 * NAVEGACIÓN PRINCIPAL - Cómo moverse por la aplicación
 * 
 * Este archivo define todas las "páginas" o "pantallas" de la aplicación.
 * 
 * ¿Qué hace?
 * - Conecta todas las páginas entre sí
 * - Permite navegar de una pantalla a otra
 * - Mantiene el flujo lógico de la aplicación
 * 
 * Rutas disponibles:
 * - / (página principal)
 * - /image-analysis (análisis por imagen)
 * - /text-analysis (análisis por texto)
 * - /diagnosis-results (resultados)
 * - /diagnostic-history (historial)
 * - /first-aid-guide (guía de primeros auxilios)
 */

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/image-analysis" element={<ImageAnalysis />} />
        <Route path="/text-analysis" element={<TextAnalysis />} />
        <Route path="/diagnosis-results" element={<DiagnosisResults />} />
        <Route path="/diagnostic-history" element={<DiagnosticHistory />} />
        <Route path="/first-aid-guide" element={<FirstAidGuide />} />
      </Routes>
    </Router>
  )
}

export default App
