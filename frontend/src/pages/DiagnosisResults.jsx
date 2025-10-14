import { useState } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { FaArrowLeft, FaSave, FaPlus, FaExclamationTriangle, FaHeart, FaUserInjured, FaBandAid, FaBell, FaFileAlt } from 'react-icons/fa'
import auxiLogo from '../assets/auxi.png'

function DiagnosisResults() {
  const navigate = useNavigate()
  const location = useLocation()
  const analysisData = location.state // { clase, probabilidad }

  if (!analysisData) return <p className="text-center mt-10 text-gray-700">No hay datos de análisis</p>

  const { clase, probabilidad } = analysisData

  // Mapear clase a severidad
  const mappedSeverity = clase === "quemaduras" ? "moderado" : clase === "cortadas" ? "leve" : "grave"
  const [currentSeverity] = useState(mappedSeverity)

  // Datos dinámicos según severidad
  const getDiagnosisData = (severity) => {
    switch (severity) {
      case "leve":
        return { injuryType: "Corte Superficial", confidence: (probabilidad*100).toFixed(2), recommendations: [] }
      case "moderado":
        return { injuryType: "Quemadura de Segundo Grado", confidence: (probabilidad*100).toFixed(2), recommendations: [] }
      case "grave":
      default:
        return { injuryType: "Herida Arterial Profunda", confidence: (probabilidad*100).toFixed(2), recommendations: [] }
    }
  }

  const diagnosisData = getDiagnosisData(currentSeverity)

  const handleSaveResult = () => console.log("Guardando resultado del diagnóstico...")
  const handleNewDiagnosis = () => navigate('/')

  return (
    <div className="min-h-screen bg-blue-50">
      {/* Header */}
      <header className="bg-white shadow-lg">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex items-center py-6">
          <button onClick={() => navigate('/')} className="mr-4 p-2 hover:bg-gray-100 rounded-lg">
            <FaArrowLeft className="w-6 h-6 text-gray-600" />
          </button>
          <img src={auxiLogo} alt="Auxi.ai Logo" className="w-10 h-10 object-contain mr-4"/>
          <h1 className="text-2xl font-bold text-gray-900">Resultados del análisis</h1>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <p className="text-lg mb-2">Clase detectada: <span className="font-semibold">{clase}</span></p>
        <p className="text-lg mb-6">Confianza: <span className="font-semibold">{diagnosisData.confidence}%</span></p>

        {/* Action Buttons */}
        <div className="flex gap-4">
          <button onClick={handleSaveResult} className="flex items-center bg-blue-600 text-white py-2 px-4 rounded">
            <FaSave className="mr-2"/> Guardar
          </button>
          <button onClick={handleNewDiagnosis} className="flex items-center bg-gray-700 text-white py-2 px-4 rounded">
            <FaPlus className="mr-2"/> Nuevo
          </button>
        </div>
      </main>
    </div>
  )
}

export default DiagnosisResults
