import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { FaArrowLeft, FaPencilAlt, FaSearch } from 'react-icons/fa'
import auxiLogo from '../assets/auxi.png'

/**
 * ANÁLISIS POR TEXTO - Describir síntomas
 * 
 * Esta página es para cuando no se puede tomar foto o se prefiere describir los síntomas.
 * 
 * ¿Qué hace?
 * - Tiene un área de texto grande para describir la situación
 * - Incluye consejos sobre qué información incluir
 * - Simula el análisis basado en la descripción
 * - Lleva a los resultados del diagnóstico
 * 
 * ¿Para qué sirve?
 * - Para síntomas no visibles (dolor, mareos, dificultad respiratoria)
 * - Cuando no se puede tomar foto por privacidad o ubicación
 * - Para casos donde la descripción es más importante que la imagen
 * 
 * Flujo: Enfermera describe síntomas → IA analiza texto → Ve resultados
 */

function TextAnalysis() {
  const navigate = useNavigate()
  const [symptoms, setSymptoms] = useState('')
  const [isAnalyzing, setIsAnalyzing] = useState(false)

  const handleAnalyze = () => {
    if (symptoms.trim()) {
      setIsAnalyzing(true)
      // Simular análisis (aquí irá la lógica del backend jiji)
      setTimeout(() => {
        setIsAnalyzing(false)
        // Navegar a la página de resultados
        navigate('/diagnosis-results')
      }, 2000)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Header */}
      <header className="bg-white shadow-lg">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center py-6">
            <button 
              onClick={() => navigate('/')}
              className="mr-4 p-2 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <FaArrowLeft className="w-6 h-6 text-gray-600" />
            </button>
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="h-12 w-12 bg-blue-100 rounded-lg flex items-center justify-center">
                  <img 
                    src={auxiLogo} 
                    alt="Auxi.ai Logo" 
                    className="w-10 h-10 object-contain"
                  />
                </div>
              </div>
              <div className="ml-4">
                <h1 className="text-2xl font-bold text-gray-900">Análisis por Texto</h1>
                <p className="text-sm text-gray-600">Diagnóstico basado en síntomas</p>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="max-w-2xl mx-auto">
          
          {/* Input Section */}
          <div className="bg-white rounded-2xl shadow-xl p-8">
            <h3 className="text-2xl font-semibold text-gray-900 mb-6 text-center">
              Describir Síntomas
            </h3>
            
            <div className="space-y-4">
              <div className="flex items-center mb-4">
                <FaPencilAlt className="w-6 h-6 text-indigo-600 mr-3" />
                <span className="text-lg font-medium text-gray-700">Describe los síntomas observados</span>
              </div>
              
              <textarea
                value={symptoms}
                onChange={(e) => setSymptoms(e.target.value)}
                placeholder="Ejemplo: El estudiante tiene una herida en el brazo que está sangrando, parece ser un corte superficial de aproximadamente 2 cm..."
                className="w-full h-64 p-4 border border-gray-300 rounded-lg resize-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              />
              
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <h4 className="text-sm font-medium text-blue-800 mb-2">Consejos para una mejor descripción:</h4>
                <ul className="text-sm text-blue-700 space-y-1">
                  <li>• Describe la ubicación de la lesión</li>
                  <li>• Menciona el tamaño y apariencia</li>
                  <li>• Incluye síntomas como dolor, hinchazón, sangrado</li>
                  <li>• Describe cómo ocurrió el incidente</li>
                </ul>
              </div>
              
              <button 
                onClick={handleAnalyze}
                disabled={!symptoms.trim() || isAnalyzing}
                className="w-full bg-indigo-600 text-white py-3 px-4 rounded-lg font-medium hover:bg-indigo-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
              >
                {isAnalyzing ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                    Analizando síntomas...
                  </>
                ) : (
                  <>
                    <FaSearch className="w-4 h-4 mr-2" />
                    Analizar Síntomas
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}

export default TextAnalysis