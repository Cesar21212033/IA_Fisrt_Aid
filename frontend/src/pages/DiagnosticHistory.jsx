import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { FaArrowLeft, FaPlus, FaExclamationTriangle, FaCheckCircle, FaEye, FaChevronRight } from 'react-icons/fa'
import auxiLogo from '../assets/auxi.png'

/**
 * HISTORIAL DE DIAGNÓSTICOS - Casos anteriores
 * 
 * Aquí la enfermera puede ver todos los diagnósticos que se han hecho anteriormente.
 * 
 * ¿Qué hace?
 * - Lista todos los casos anteriores con fecha
 * - Muestra si fue análisis por imagen o texto
 * - Indica la gravedad de cada caso
 * - Permite ver los detalles de cualquier caso anterior
 * - Tiene botón para hacer nuevo diagnóstico
 * 
 * ¿Para qué sirve?
 * - Consultar casos similares anteriores
 * - Seguimiento de estudiantes con problemas recurrentes
 * - Documentación para reportes a padres/administración
 * - Aprendizaje de patrones comunes en la escuela
 * 
 * Flujo: Enfermera consulta historial → Ve caso similar → Aplica misma solución
 */


function DiagnosticHistory() {
  const navigate = useNavigate()

  // Datos de ejemplo para el historial
  const diagnosticHistory = [
    {
      id: 1,
      date: "15/03/2025",
      type: "Texto",
      severity: "baja",
      severityLabel: "Leve",
      description: "Corte superficial en brazo izquierdo con sangrado mínimo",
      status: "leve"
    },
    {
      id: 2,
      date: "14/03/2025",
      type: "imagen",
      severity: "Media",
      severityLabel: "Moderado",
      description: "Quemadura de segundo grado en mano derecha",
      status: "moderado"
    },
    {
      id: 3,
      date: "13/03/2025",
      type: "Texto",
      severity: "Alta",
      severityLabel: "Grave",
      description: "Herida profunda con sangrado arterial en pierna",
      status: "grave"
    },
    {
      id: 4,
      date: "12/03/2025",
      type: "imagen",
      severity: "baja",
      severityLabel: "Leve",
      description: "Arañazo superficial en rostro",
      status: "leve"
    },
    {
      id: 5,
      date: "11/03/2025",
      type: "Texto",
      severity: "Media",
      severityLabel: "Moderado",
      description: "Esguince de tobillo con inflamación moderada",
      status: "moderado"
    }
  ]

  const getSeverityConfig = (severity) => {
    switch (severity) {
      case "leve":
        return {
          icon: FaCheckCircle,
          bgColor: "bg-green-500",
          textColor: "text-green-700",
          bgTagColor: "bg-green-100"
        }
      case "moderado":
        return {
          icon: FaExclamationTriangle,
          bgColor: "bg-yellow-500",
          textColor: "text-yellow-700",
          bgTagColor: "bg-yellow-100"
        }
      case "grave":
        return {
          icon: FaExclamationTriangle,
          bgColor: "bg-red-500",
          textColor: "text-red-700",
          bgTagColor: "bg-red-100"
        }
      default:
        return getSeverityConfig("leve")
    }
  }

  const handleViewDetail = (diagnostic) => {
    // Navegar a la página de resultados con los datos específicos
    navigate('/diagnosis-results', { state: { diagnostic } })
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
                <p className="text-sm text-gray-600">Historial de diagnósticos médicos</p>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* History Card */}
        <div className="bg-white rounded-3xl shadow-xl p-8">
          
          {/* Header Section */}
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-8">
            <h2 className="text-3xl font-bold text-gray-900 mb-4 sm:mb-0">
              Historial de Diagnósticos
            </h2>
            
            <button 
              onClick={handleNewDiagnosis}
              className="flex items-center bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-6 rounded-xl transition-colors duration-200 shadow-lg hover:shadow-xl"
            >
              <FaPlus className="w-5 h-5 mr-2" />
              Nuevo Diagnóstico
            </button>
          </div>

          {/* Diagnostic Entries List */}
          <div className="space-y-0">
            {diagnosticHistory.map((diagnostic, index) => {
              const severityConfig = getSeverityConfig(diagnostic.status)
              
              return (
                <div key={diagnostic.id}>
                  <div className="flex items-center py-6 hover:bg-gray-50 transition-colors">
                    
                    {/* Status Indicator */}
                    <div className="flex-shrink-0 mr-6">
                      <div className={`w-12 h-12 ${severityConfig.bgColor} rounded-xl flex items-center justify-center`}>
                        <severityConfig.icon className="w-6 h-6 text-white" />
                      </div>
                    </div>

                    {/* Date */}
                    <div className="flex-shrink-0 mr-6">
                      <p className="text-lg font-semibold text-gray-900">
                        {diagnostic.date}
                      </p>
                    </div>

                    {/* Tags */}
                    <div className="flex-shrink-0 mr-6">
                      <div className="flex gap-2">
                        <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-700">
                          {diagnostic.type}
                        </span>
                        <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${severityConfig.bgTagColor} ${severityConfig.textColor}`}>
                          {diagnostic.severityLabel}
                        </span>
                      </div>
                    </div>

                    {/* Description */}
                    <div className="flex-1 mr-6">
                      <p className="text-gray-800 leading-relaxed">
                        {diagnostic.description}
                      </p>
                    </div>

                    {/* View Detail Link */}
                    <div className="flex-shrink-0">
                      <button 
                        onClick={() => handleViewDetail(diagnostic)}
                        className="flex items-center text-blue-600 hover:text-blue-800 font-medium transition-colors"
                      >
                        Ver detalle
                        <FaChevronRight className="w-4 h-4 ml-1" />
                      </button>
                    </div>
                  </div>
                  
                  {/* Separator Line */}
                  {index < diagnosticHistory.length - 1 && (
                    <hr className="border-gray-200" />
                  )}
                </div>
              )
            })}
          </div>

          {/* Empty State (si no hay diagnósticos) */}
          {diagnosticHistory.length === 0 && (
            <div className="text-center py-12">
              <div className="mb-4">
                <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto">
                  <FaEye className="w-8 h-8 text-gray-400" />
                </div>
              </div>
              <h3 className="text-xl font-medium text-gray-500 mb-2">
                No hay diagnósticos registrados
              </h3>
              <p className="text-gray-400 mb-6">
                Comienza realizando tu primer diagnóstico
              </p>
              <button 
                onClick={handleNewDiagnosis}
                className="inline-flex items-center bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-6 rounded-xl transition-colors duration-200"
              >
                <FaPlus className="w-5 h-5 mr-2" />
                Nuevo Diagnóstico
              </button>
            </div>
          )}
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

export default DiagnosticHistory
