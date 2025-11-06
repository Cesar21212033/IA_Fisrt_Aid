import { useState, useEffect } from 'react'

import { useNavigate, useLocation } from 'react-router-dom'

import { FaArrowLeft, FaSave, FaPlus } from 'react-icons/fa'

import auxiLogo from '../assets/auxi.png'

function DiagnosisResults() {

  const navigate = useNavigate()

  const location = useLocation()

  const analysisData = location.state // { clase, probabilidad }

  if (!analysisData) return <p className="text-center mt-10 text-gray-700">No hay datos de análisis</p>

  const { 
    clase, 
    probabilidad, 
    instrucciones, 
    respuesta, 
    imageUrl, 
    textoIngresado, 
    tipo, 
    numero_control,
    nombre_completo,
    fecha,
    desdeHistorial 
  } = analysisData

  // Limpiar la URL del blob cuando el componente se desmonte
  useEffect(() => {
    return () => {
      if (imageUrl && imageUrl.startsWith('blob:')) {
        URL.revokeObjectURL(imageUrl)
      }
    }
  }, [imageUrl])

  // Mapear clase a severidad

  const mappedSeverity = clase === "quemaduras" ? "moderado" : clase === "cortadas" ? "leve" : "grave"

  const [currentSeverity] = useState(mappedSeverity)

  // Datos dinámicos según severidad

  const getDiagnosisData = (severity) => {

    // Manejar probabilidad (puede ser undefined para análisis de texto)
    const confidence = probabilidad !== undefined && probabilidad !== null 
      ? (probabilidad * 100).toFixed(2) 
      : "N/A"

    switch (severity) {

      case "leve":

        return { injuryType: "Corte Superficial", confidence: confidence, recommendations: [] }

      case "moderado":

        return { injuryType: "Quemadura de Segundo Grado", confidence: confidence, recommendations: [] }

      case "grave":

      default:

        return { injuryType: "Herida Arterial Profunda", confidence: confidence, recommendations: [] }

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

        {/* Información del paciente */}
        {(numero_control || nombre_completo) && (
          <div className="bg-white p-6 rounded-xl shadow-md mb-6">
            <h2 className="text-xl font-semibold text-gray-800 mb-4">Datos del Paciente</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {numero_control && (
                <div>
                  <p className="text-sm text-gray-600 mb-1">Número de Control</p>
                  <p className="text-lg font-semibold text-gray-900">{numero_control}</p>
                </div>
              )}
              {nombre_completo && (
                <div>
                  <p className="text-sm text-gray-600 mb-1">Nombre Completo</p>
                  <p className="text-lg font-semibold text-gray-900">{nombre_completo}</p>
                </div>
              )}
              {fecha && (
                <div>
                  <p className="text-sm text-gray-600 mb-1">Fecha del Diagnóstico</p>
                  <p className="text-lg font-semibold text-gray-900">
                    {new Date(fecha).toLocaleString('es-ES', {
                      day: '2-digit',
                      month: '2-digit',
                      year: 'numeric',
                      hour: '2-digit',
                      minute: '2-digit'
                    })}
                  </p>
                </div>
              )}
              {tipo && (
                <div>
                  <p className="text-sm text-gray-600 mb-1">Tipo de Análisis</p>
                  <p className="text-lg font-semibold text-gray-900">
                    {tipo === 'imagen' ? 'Análisis por Imagen' : 'Análisis por Texto'}
                  </p>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Mostrar imagen si viene de análisis por imagen */}
        {imageUrl && tipo === 'imagen' && (
          <div className="bg-white p-6 rounded-xl shadow-md mb-6">
            <h2 className="text-xl font-semibold text-gray-800 mb-4">Imagen analizada:</h2>
            <div className="relative">
              <img
                src={imageUrl}
                alt="Imagen analizada"
                className="w-full max-w-md mx-auto rounded-lg shadow-lg object-cover"
              />
            </div>
          </div>
        )}

        {/* Mostrar texto ingresado si viene de análisis por texto */}
        {textoIngresado && tipo === 'texto' && (
          <div className="bg-white p-6 rounded-xl shadow-md mb-6">
            <h2 className="text-xl font-semibold text-gray-800 mb-4">Descripción ingresada:</h2>
            <div className="bg-gray-50 p-4 rounded-lg border-l-4 border-blue-500">
              <p className="text-gray-800 whitespace-pre-line">{textoIngresado}</p>
            </div>
          </div>
        )}

        {/* Información del diagnóstico */}
        <div className="bg-white p-6 rounded-xl shadow-md mb-6">
          <h2 className="text-xl font-semibold text-gray-800 mb-4">Información del Diagnóstico</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <p className="text-sm text-gray-600 mb-1">Clase Detectada</p>
              <p className="text-lg font-semibold text-gray-900 capitalize">{clase || 'N/A'}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600 mb-1">Confianza</p>
              <p className="text-lg font-semibold text-gray-900">{diagnosisData.confidence}%</p>
            </div>
          </div>
        </div>

  {/* Recomendación de Gemini */}

  {instrucciones ? (

  <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 mb-6 rounded">

    <h2 className="font-semibold mb-2">Recomendaciones de primeros auxilios:</h2>

    <p className="whitespace-pre-line">{instrucciones}</p>

  </div>

    ) : (

      <p className="text-gray-500 mb-6">No hay recomendaciones disponibles.</p>

    )}

  {/* Action Buttons */}

  <div className="flex gap-4">

    <button onClick={handleNewDiagnosis} className="flex items-center bg-gray-700 text-white py-2 px-4 rounded">

      <FaPlus className="mr-2"/> Nuevo

    </button>

  </div>

</main>

    </div>

  )

}

export default DiagnosisResults

