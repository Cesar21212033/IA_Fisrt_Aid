import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { FaArrowLeft, FaPlus, FaEye, FaChevronRight } from 'react-icons/fa'
import auxiLogo from '../assets/auxi.png'

function DiagnosticHistory() {
  const navigate = useNavigate()
  const [diagnosticHistory, setDiagnosticHistory] = useState([])
  const [loading, setLoading] = useState(true)

  // ==========================
  // Traer historial desde backend
  // ==========================
  useEffect(() => {
    fetch("http://127.0.0.1:8001/historial/")
      .then(res => res.json())
      .then(data => {
        setDiagnosticHistory(data)
        setLoading(false)
      })
      .catch(err => {
        console.error("Error cargando historial:", err)
        setLoading(false)
      })
  }, [])

  const handleViewDetail = (diagnostic) => {
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
                  <img src={auxiLogo} alt="Auxi.ai Logo" className="w-10 h-10 object-contain" />
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
        <div className="bg-white rounded-3xl shadow-xl p-8">
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-8">
            <h2 className="text-3xl font-bold text-gray-900 mb-4 sm:mb-0">Historial de Diagnósticos</h2>
            <button 
              onClick={handleNewDiagnosis}
              className="flex items-center bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-6 rounded-xl transition-colors duration-200 shadow-lg hover:shadow-xl"
            >
              <FaPlus className="w-5 h-5 mr-2" /> Nuevo Diagnóstico
            </button>
          </div>

          {/* Lista de diagnósticos */}
          {loading ? (
            <p>Cargando historial...</p>
          ) : diagnosticHistory.length === 0 ? (
            <div className="text-center py-12">
              <div className="mb-4">
                <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto">
                  <FaEye className="w-8 h-8 text-gray-400" />
                </div>
              </div>
              <h3 className="text-xl font-medium text-gray-500 mb-2">No hay diagnósticos registrados</h3>
              <p className="text-gray-400 mb-6">Comienza realizando tu primer diagnóstico</p>
            </div>
          ) : (
            <div className="space-y-0">
              {diagnosticHistory.map((diagnostic, index) => (
                <div key={diagnostic.id}>
                  <div className="flex items-center py-6 hover:bg-gray-50 transition-colors">
                    {/* Tipo */}
                    <div className="flex-shrink-0 mr-6">
                      <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-700">
                        {diagnostic.tipo}
                      </span>
                    </div>

                    {/* Fecha */}
                    <div className="flex-shrink-0 mr-6">
                      <p className="text-lg font-semibold text-gray-900">
                        {new Date(diagnostic.fecha).toLocaleString()}
                      </p>
                    </div>

                    {/* Descripción / Instrucciones */}
                    <div className="flex-1 mr-6">
                      <p className="text-gray-800 leading-relaxed">
                        {diagnostic.instrucciones}
                      </p>
                    </div>

                    {/* Ver detalle */}
                    <div className="flex-shrink-0">
                      <button 
                        onClick={() => handleViewDetail(diagnostic)}
                        className="flex items-center text-blue-600 hover:text-blue-800 font-medium transition-colors"
                      >
                        Ver detalle <FaChevronRight className="w-4 h-4 ml-1" />
                      </button>
                    </div>
                  </div>
                  {index < diagnosticHistory.length - 1 && <hr className="border-gray-200" />}
                </div>
              ))}
            </div>
          )}
        </div>
      </main>

      {/* Footer */}
      <footer className="text-center py-8">
        <p className="text-gray-600 font-medium">Auxi.ai - 2025</p>
      </footer>
    </div>
  )
}

export default DiagnosticHistory
