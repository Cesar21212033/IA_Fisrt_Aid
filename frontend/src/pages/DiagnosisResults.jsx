import { useState, useEffect } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { FaArrowLeft, FaSave, FaPlus, FaExclamationTriangle, FaHeart, FaUserInjured, FaBandAid, FaBell, FaFileAlt } from 'react-icons/fa'
import auxiLogo from '../assets/auxi.png'

function DiagnosisResults() {
  const navigate = useNavigate()
  const location = useLocation()
  const [currentSeverity, setCurrentSeverity] = useState("grave")

  /**
 * RESULTADOS DEL DIAGNÓSTICO - Lo que encontró la IA
 * 
 * Esta es la página más importante: aquí la IA muestra su diagnóstico y recomendaciones.
 * 
 * ¿Qué hace?
 * - Muestra el tipo de lesión detectada (corte, quemadura, etc.)
 * - Indica la gravedad: Leve, Moderado o Grave
 * - Da recomendaciones específicas de primeros auxilios
 * - Muestra el nivel de confianza de la IA
 * - Permite guardar el resultado o hacer nuevo diagnóstico
 * 
 * ¿Para qué sirve?
 * - La enfermera ve exactamente qué hacer en cada situación
 * - Las recomendaciones son específicas y profesionales
 * - Puede documentar el caso para el historial
 * 
 * Flujo: IA analiza → Muestra diagnóstico → Enfermera sigue recomendaciones → Guarda resultado
 */
  
  // Verificar si hay datos del historial
  const diagnosticFromHistory = location.state?.diagnostic

  useEffect(() => {
    if (diagnosticFromHistory) {
      setCurrentSeverity(diagnosticFromHistory.status)
    }
  }, [diagnosticFromHistory])

  const getDiagnosisData = (severity) => {
    switch (severity) {
      case "leve":
        return {
          injuryType: "Corte Superficial",
          confidence: 92,
          location: "Extremidad Superior",
          diagnosis: "Corte superficial identificado en extremidad superior. Lesión menor sin compromiso vascular significativo. El sangrado es mínimo y controlable.",
          recommendations: [
            {
              icon: FaBandAid,
              color: "text-green-500",
              bgColor: "bg-green-100",
              text: "Limpiar la herida con agua y jabón suave"
            },
            {
              icon: FaHeart,
              color: "text-blue-500",
              bgColor: "bg-blue-100",
              text: "Aplicar presión suave con gasa estéril por 5-10 minutos"
            },
            {
              icon: FaFileAlt,
              color: "text-purple-500",
              bgColor: "bg-purple-100",
              text: "Cubrir con apósito estéril y cambiar diariamente"
            },
            {
              icon: FaBell,
              color: "text-orange-500",
              bgColor: "bg-orange-100",
              text: "Monitorear por signos de infección en las próximas 24-48 horas"
            },
            {
              icon: FaUserInjured,
              color: "text-gray-500",
              bgColor: "bg-gray-100",
              text: "Mantener la zona elevada si hay hinchazón leve"
            }
          ]
        }
      case "moderado":
        return {
          injuryType: "Quemadura de Segundo Grado",
          confidence: 87,
          location: "Torso/Extremidades",
          diagnosis: "Quemadura de segundo grado superficial detectada. Área afectada muestra enrojecimiento, ampollas pequeñas y dolor moderado. Requiere atención médica profesional.",
          recommendations: [
            {
              icon: FaHeart,
              color: "text-blue-500",
              bgColor: "bg-blue-100",
              text: "Enfriar la zona con agua fría (no hielo) por 15-20 minutos"
            },
            {
              icon: FaBandAid,
              color: "text-yellow-500",
              bgColor: "bg-yellow-100",
              text: "NO romper las ampollas - cubrir con gasa estéril"
            },
            {
              icon: FaBell,
              color: "text-orange-500",
              bgColor: "bg-orange-100",
              text: "Contactar servicio médico no urgente o acudir a centro de salud"
            },
            {
              icon: FaUserInjured,
              color: "text-purple-500",
              bgColor: "bg-purple-100",
              text: "Mantener al estudiante en reposo y monitorear constantemente"
            },
            {
              icon: FaFileAlt,
              color: "text-gray-500",
              bgColor: "bg-gray-100",
              text: "Documentar tamaño y ubicación de la quemadura"
            }
          ]
        }
      case "grave":
        return {
          injuryType: "Herida Arterial Profunda",
          confidence: 95,
          location: "Extremidades/Área Vascular",
          diagnosis: "EMERGENCIA MÉDICA: Herida profunda con sangrado arterial activo identificada. Pérdida significativa de sangre y posible compromiso vascular. Requiere intervención inmediata.",
          recommendations: [
            {
              icon: FaHeart,
              color: "text-red-500",
              bgColor: "bg-red-100",
              text: "LLAMAR INMEDIATAMENTE AL 911 - EMERGENCIA MÉDICA"
            },
            {
              icon: FaUserInjured,
              color: "text-red-500",
              bgColor: "bg-red-100",
              text: "Aplicar presión directa con ambas manos sobre la herida"
            },
            {
              icon: FaBandAid,
              color: "text-red-500",
              bgColor: "bg-red-100",
              text: "Elevar la extremidad por encima del nivel del corazón"
            },
            {
              icon: FaBell,
              color: "text-red-500",
              bgColor: "bg-red-100",
              text: "Evacuar inmediatamente al estudiante del área y preparar llegada de ambulancia"
            },
            {
              icon: FaFileAlt,
              color: "text-red-500",
              bgColor: "bg-red-100",
              text: "Mantener al estudiante acostado y alerta hasta llegada de personal médico"
            }
          ]
        }
      default:
        return getDiagnosisData("grave")
    }
  }

  const diagnosisData = getDiagnosisData(currentSeverity)

  const getSeverityConfig = (severity) => {
    switch (severity) {
      case "leve":
        return {
          icon: FaBandAid,
          iconBg: "bg-green-500",
          iconColor: "text-green-500",
          iconBgColor: "bg-green-100",
          borderColor: "border-green-200",
          bgColor: "bg-green-50",
          title: "Diagnóstico de Gravedad Leve",
          description: "Lesión menor identificada. Requiere atención básica de primeros auxilios."
        }
      case "moderado":
        return {
          icon: FaUserInjured,
          iconBg: "bg-yellow-500",
          iconColor: "text-yellow-500",
          iconBgColor: "bg-yellow-100",
          borderColor: "border-yellow-200",
          bgColor: "bg-yellow-50",
          title: "Diagnóstico de Gravedad Moderada",
          description: "Lesión de gravedad moderada identificada. Requiere atención médica profesional."
        }
      case "grave":
        return {
          icon: FaExclamationTriangle,
          iconBg: "bg-red-500",
          iconColor: "text-red-500",
          iconBgColor: "bg-red-100",
          borderColor: "border-red-200",
          bgColor: "bg-red-50",
          title: "Diagnóstico de Gravedad Grave",
          description: "Emergencia médica de alta gravedad identificada. Se requiere atención inmediata."
        }
      default:
        return getSeverityConfig("grave")
    }
  }

  const severityConfig = getSeverityConfig(diagnosisData.severity)

  const handleSaveResult = () => {
    // Lógica para guardar el resultado
    console.log("Guardando resultado del diagnóstico...")
  }

  const handleNewDiagnosis = () => {
    navigate('/')
  }

  return (
    <div className="min-h-screen bg-blue-50">
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
                <h1 className="text-2xl font-bold text-gray-900">Centro de Diagnóstico IA Escolar</h1>
                <p className="text-sm text-gray-600">Resultados del análisis médico</p>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Results Card */}
        <div className="bg-white rounded-3xl shadow-xl p-8">
          
          {/* Title */}
          <h2 className="text-3xl font-bold text-gray-900 text-center mb-4">
            Resultados del Diagnóstico
          </h2>

          {/* Demo Buttons - Solo para demostración (ocultos si viene del historial) */}
          {!diagnosticFromHistory && (
            <div className="flex justify-center gap-2 mb-6">
              <button 
                onClick={() => setCurrentSeverity("leve")}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  currentSeverity === "leve" 
                    ? "bg-green-500 text-white" 
                    : "bg-green-100 text-green-700 hover:bg-green-200"
                }`}
              >
                Leve
              </button>
              <button 
                onClick={() => setCurrentSeverity("moderado")}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  currentSeverity === "moderado" 
                    ? "bg-yellow-500 text-white" 
                    : "bg-yellow-100 text-yellow-700 hover:bg-yellow-200"
                }`}
              >
                Moderado
              </button>
              <button 
                onClick={() => setCurrentSeverity("grave")}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  currentSeverity === "grave" 
                    ? "bg-red-500 text-white" 
                    : "bg-red-100 text-red-700 hover:bg-red-200"
                }`}
              >
                Grave
              </button>
            </div>
          )}

          {/* Severity Icon */}
          <div className="flex justify-center mb-6">
            <div className={`w-20 h-20 ${severityConfig.iconBg} rounded-full flex items-center justify-center`}>
              <severityConfig.icon className="w-10 h-10 text-white" />
            </div>
          </div>

          {/* Severity Title */}
          <div className="text-center mb-4">
            <h3 className="text-2xl font-bold text-gray-900 mb-2">
              {severityConfig.title}
            </h3>
            <p className="text-gray-600">
              {severityConfig.description}
            </p>
          </div>

          {/* Injury Details */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            <div className="bg-gray-50 rounded-lg p-4 text-center">
              <h4 className="text-sm font-medium text-gray-500 mb-1">Tipo de Lesión</h4>
              <p className="text-lg font-semibold text-gray-900">{diagnosisData.injuryType}</p>
            </div>
            <div className="bg-gray-50 rounded-lg p-4 text-center">
              <h4 className="text-sm font-medium text-gray-500 mb-1">Ubicación</h4>
              <p className="text-lg font-semibold text-gray-900">{diagnosisData.location}</p>
            </div>
            <div className="bg-gray-50 rounded-lg p-4 text-center">
              <h4 className="text-sm font-medium text-gray-500 mb-1">Confianza IA</h4>
              <p className="text-lg font-semibold text-gray-900">{diagnosisData.confidence}%</p>
            </div>
          </div>

          {/* Diagnosis Message */}
          <div className={`${severityConfig.bgColor} border-2 ${severityConfig.borderColor} rounded-2xl p-6 mb-8`}>
            <p className="text-lg text-gray-800 leading-relaxed text-center">
              {diagnosisData.diagnosis}
            </p>
          </div>

          {/* Recommendations Section */}
          <div className="mb-8">
            <div className="flex items-center mb-6">
              <div className="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center mr-3">
                <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
                </svg>
              </div>
              <h3 className="text-2xl font-bold text-gray-900">Recomendaciones</h3>
            </div>

            {/* Recommendations List */}
            <div className="space-y-4">
              {diagnosisData.recommendations.map((recommendation, index) => (
                <div key={index} className="flex items-start space-x-4 p-4 bg-gray-50 rounded-xl hover:bg-gray-100 transition-colors">
                  <div className={`w-12 h-12 ${recommendation.bgColor} rounded-full flex items-center justify-center flex-shrink-0`}>
                    <recommendation.icon className={`w-6 h-6 ${recommendation.color}`} />
                  </div>
                  <p className="text-gray-800 leading-relaxed pt-2">
                    {recommendation.text}
                  </p>
                </div>
              ))}
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <button 
              onClick={handleSaveResult}
              className="flex items-center justify-center bg-blue-600 hover:bg-blue-700 text-white font-bold py-4 px-8 rounded-xl transition-colors duration-200 shadow-lg hover:shadow-xl"
            >
              <FaSave className="w-5 h-5 mr-3" />
              Guardar Resultado
            </button>
            
            <button 
              onClick={handleNewDiagnosis}
              className="flex items-center justify-center bg-gray-700 hover:bg-gray-800 text-white font-bold py-4 px-8 rounded-xl transition-colors duration-200 shadow-lg hover:shadow-xl"
            >
              <FaPlus className="w-5 h-5 mr-3" />
              Nuevo Diagnóstico
            </button>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="text-center py-8">
        <p className="text-gray-600 font-medium">
          Auxi.ai - 2025
        </p>
      </footer>
    </div>
  )
}

export default DiagnosisResults
