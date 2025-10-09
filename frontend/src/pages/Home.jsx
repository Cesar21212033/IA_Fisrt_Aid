import { useNavigate } from 'react-router-dom'
import { FaKitMedical } from 'react-icons/fa6'
import { FaCamera, FaPencilAlt, FaBookMedical } from 'react-icons/fa'
import auxiLogo from '../assets/auxi.png'


/**
 * PÁGINA PRINCIPAL - Asistente IA para Enfermeras Escolares
 * 
 * Esta es la página de entrada donde las enfermeras pueden elegir qué tipo de diagnóstico quieren hacer.
 * 
 * ¿Qué hace?
 * - Muestra el logo y nombre del sistema
 * - Tiene un botón "Historial" para ver diagnósticos anteriores
 * - Permite elegir entre análisis por imagen (subir foto de la lesión) o por texto (describir síntomas)
 * - Incluye un acceso discreto a la "Guía de Primeros Auxilios" en la esquina
 * 
 * ¿Para quién es?
 * - Enfermeras escolares que necesitan ayuda rápida para diagnosticar lesiones de estudiantes
 * - Personal educativo que quiere consultar el historial de casos anteriores
 * 
 * Flujo: La enfermera llega aquí y decide si subir una foto o escribir lo que ve
 */

function Home() {
  const navigate = useNavigate()

  const handleImageAnalysis = () => {
    navigate('/image-analysis')
  }

  const handleTextAnalysis = () => {
    navigate('/text-analysis')
  }

  const handleViewHistory = () => {
    navigate('/diagnostic-history')
  }

  const handleFirstAidGuide = () => {
    navigate('/first-aid-guide')
  }
  return (
    <div className="min-h-screen bg-blue-50 flex items-center justify-center p-4 relative">
      {/* First Aid Guide Link - Discreto en esquina superior derecha */}
      <button 
        onClick={handleFirstAidGuide}
        className="absolute top-4 right-4 flex items-center bg-white hover:bg-gray-50 text-gray-600 hover:text-blue-600 px-4 py-2 rounded-lg shadow-md transition-colors duration-200 border border-gray-200 hover:border-blue-300"
        title="Guía de Primeros Auxilios"
      >
        <FaBookMedical className="w-4 h-4 mr-2" />
        <span className="text-sm font-medium">Guía</span>
      </button>

      {/* Main Card */}
      <div className="bg-white rounded-3xl shadow-xl p-8 max-w-4xl w-full">
        
        {/* Header Section */}
        <div className="text-center mb-8">
          {/* Auxi.ai Logo */}
          <div className="inline-flex items-center justify-center w-28 h-28 bg-blue-100 rounded-xl mb-6">
            <img 
              src={auxiLogo} 
              alt="Auxi.ai Logo" 
              className="w-24 h-24 object-contain"
            />
          </div>
          
          {/* Main Title */}
          <h1 className="text-4xl font-bold text-gray-800 mb-4 leading-tight">
            Asistente Inteligente de Primeros Auxilios
            <br />
            <span className="text-4xl font-bold text-gray-800">Escolares</span>
          </h1>
          
          {/* Welcome Message */}
          <p className="text-lg text-gray-600 max-w-2xl mx-auto leading-relaxed">
            Bienvenido a tu asistente de primeros auxilios. Puedes iniciar un diagnóstico mediante imagen o texto para obtener recomendaciones médicas inmediatas.
          </p>
        </div>

        {/* Main Action Button */}
        <div className="text-center mb-8">
          <button 
            onClick={handleViewHistory}
            className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-4 px-8 rounded-xl text-lg transition-colors duration-200 shadow-lg hover:shadow-xl"
          >
            Historial
          </button>
        </div>

        {/* Two-Column Action Section */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          
          {/* Left Card - Analizar por imagen */}
          <div 
            onClick={handleImageAnalysis}
            className="bg-white border border-gray-100 rounded-2xl shadow-lg p-6 hover:shadow-xl transition-shadow duration-200 cursor-pointer hover:border-blue-300"
          >
            <div className="text-center">
              {/* Camera Icon */}
              <div className="inline-flex items-center justify-center w-16 h-16 bg-blue-100 rounded-full mb-4">
                <FaCamera className="w-8 h-8 text-white bg-blue-500 rounded-full p-2" />
              </div>
              
              {/* Title */}
              <h3 className="text-xl font-bold text-gray-800 mb-3">
                Analizar por imagen
              </h3>
              
              {/* Description */}
              <p className="text-gray-600 leading-relaxed">
                Sube una foto del incidente para un diagnóstico visual rápido
              </p>
            </div>
          </div>

          {/* Right Card - Analizar por texto */}
          <div 
            onClick={handleTextAnalysis}
            className="bg-white border border-gray-100 rounded-2xl shadow-lg p-6 hover:shadow-xl transition-shadow duration-200 cursor-pointer hover:border-blue-300"
          >
            <div className="text-center">
              {/* Pencil Icon */}
              <div className="inline-flex items-center justify-center w-16 h-16 bg-blue-100 rounded-full mb-4">
                <FaPencilAlt className="w-8 h-8 text-white bg-blue-500 rounded-full p-2" />
              </div>
              
              {/* Title */}
              <h3 className="text-xl font-bold text-gray-800 mb-3">
                Analizar por texto
              </h3>
              
              {/* Description */}
              <p className="text-gray-600 leading-relaxed">
                Describe los síntomas para obtener un diagnóstico detallado
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Home
