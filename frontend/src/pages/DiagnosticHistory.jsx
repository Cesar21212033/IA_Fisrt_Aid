import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { FaArrowLeft, FaPlus, FaExclamationTriangle, FaCheckCircle, FaEye, FaChevronRight, FaSearch } from 'react-icons/fa'
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
  const [diagnosticHistory, setDiagnosticHistory] = useState([])
  const [allDiagnostics, setAllDiagnostics] = useState([]) // Guardar todos los diagnósticos sin filtrar
  const [loading, setLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState('') // Estado para el filtro de búsqueda

  // ==========================
  // Traer historial desde backend
  // ==========================
  useEffect(() => {
    fetch("http://127.0.0.1:8001/historial/")
      .then(res => res.json())
      .then(data => {
        // Mapear datos de la BD al formato del diseño
        const mappedData = data.map(diagnostic => {
          // Determinar severidad basada en clase_detectada
          let severity = "leve"
          let severityLabel = "Leve"
          
          if (diagnostic.clase_detectada === "quemaduras") {
            severity = "moderado"
            severityLabel = "Moderado"
          } else if (diagnostic.clase_detectada === "cortadas") {
            severity = "leve"
            severityLabel = "Leve"
          } else {
            severity = "grave"
            severityLabel = "Grave"
          }

          // Formatear fecha
          const fecha = new Date(diagnostic.fecha)
          const formattedDate = fecha.toLocaleDateString('es-ES', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric'
          })

          // Capitalizar tipo
          const tipoCapitalizado = diagnostic.tipo.charAt(0).toUpperCase() + diagnostic.tipo.slice(1)

          return {
            id: diagnostic.id || Math.random(),
            date: formattedDate,
            fechaCompleta: diagnostic.fecha,
            type: tipoCapitalizado,
            tipo: diagnostic.tipo,
            severity: severity,
            severityLabel: severityLabel,
            status: severity,
            clase: diagnostic.clase_detectada,
            numero_control: diagnostic.numero_control || 'Sin número',
            nombre_completo: diagnostic.nombre_completo || 'Sin nombre',
            instrucciones: diagnostic.instrucciones,
            probabilidad: diagnostic.probabilidad, // Incluir probabilidad desde la BD
            // Datos completos para enviar a DiagnosisResults
            datosCompletos: diagnostic
          }
        })
        
        setAllDiagnostics(mappedData) // Guardar todos los diagnósticos
        setDiagnosticHistory(mappedData) // Mostrar todos inicialmente
        setLoading(false)
      })
      .catch(err => {
        console.error("Error cargando historial:", err)
        setLoading(false)
      })
  }, [])

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
    // Preparar datos para DiagnosisResults
    const stateData = {
      clase: diagnostic.clase,
      probabilidad: diagnostic.probabilidad, // Usar la probabilidad de la BD
      instrucciones: diagnostic.instrucciones,
      numero_control: diagnostic.numero_control,
      nombre_completo: diagnostic.nombre_completo,
      tipo: diagnostic.tipo,
      fecha: diagnostic.fechaCompleta,
      desdeHistorial: true, // Flag para indicar que viene del historial
      diagnostico_id: diagnostic.datosCompletos?.id || diagnostic.id // ID del diagnóstico para hacer preguntas
    }
    
    navigate('/diagnosis-results', { state: stateData })
  }

  const handleNewDiagnosis = () => {
    navigate('/')
  }

  // Filtrar diagnósticos por número de control
  useEffect(() => {
    if (searchQuery.trim() === '') {
      setDiagnosticHistory(allDiagnostics)
    } else {
      const filtered = allDiagnostics.filter(diagnostic => 
        diagnostic.numero_control && 
        diagnostic.numero_control.toLowerCase().includes(searchQuery.toLowerCase().trim())
      )
      setDiagnosticHistory(filtered)
    }
  }, [searchQuery, allDiagnostics])

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
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-6">
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

          {/* Filtro de búsqueda */}
          <div className="mb-6">
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <FaSearch className="h-5 w-5 text-gray-400" />
              </div>
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Buscar por número de control..."
                className="block w-full pl-10 pr-3 py-3 border border-gray-300 rounded-lg leading-5 bg-white placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
            {searchQuery && (
              <p className="mt-2 text-sm text-gray-600">
                {diagnosticHistory.length} resultado{diagnosticHistory.length !== 1 ? 's' : ''} encontrado{diagnosticHistory.length !== 1 ? 's' : ''}
              </p>
            )}
          </div>

          {/* Loading State */}
          {loading ? (
            <div className="text-center py-12">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
              <p className="text-gray-600">Cargando historial...</p>
            </div>
          ) : diagnosticHistory.length === 0 ? (
            /* Empty State */
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
          ) : (
            /* Diagnostic Entries List */
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

                      {/* Información del estudiante */}
                      <div className="flex-1 mr-6">
                        <div className="space-y-1">
                          <p className="text-sm text-gray-600">Estudiante:</p>
                          <p className="text-lg font-semibold text-gray-900">
                            {diagnostic.nombre_completo}
                          </p>
                          <p className="text-sm text-gray-600">
                            Número de Control: <span className="font-medium text-gray-800">{diagnostic.numero_control}</span>
                          </p>
                        </div>
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
