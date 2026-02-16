import { useState, useEffect } from 'react'

import { useNavigate, useLocation } from 'react-router-dom'

import { FaArrowLeft, FaPlus, FaPaperPlane, FaUser, FaRobot, FaCheckCircle, FaExclamationTriangle, FaExclamationCircle } from 'react-icons/fa'

import auxiLogo from '../assets/auxi.png'

function DiagnosisResults() {

  const navigate = useNavigate()

  const location = useLocation()

  const analysisData = location.state // { clase, probabilidad }

  // Estados para el chat de preguntas (deben estar antes del early return)
  const [pregunta, setPregunta] = useState('')
  const [conversaciones, setConversaciones] = useState([])
  const [loadingPregunta, setLoadingPregunta] = useState(false)

  // Extraer datos con valores por defecto para evitar errores
  const { 
    clase = '', 
    probabilidad, 
    gravedad,  // Gravedad viene del backend
    instrucciones, 
    respuesta, 
    imageUrl, 
    textoIngresado, 
    tipo, 
    numero_control,
    nombre_completo,
    fecha,
    diagnostico_id 
  } = analysisData || {}

  // Usar gravedad del backend, o calcular si no viene (lógica conservadora)
  const calcularGravedad = () => {
    // SIEMPRE priorizar la gravedad del backend si está disponible
    if (gravedad) return gravedad;
    
    // Si no viene del backend, calcular con lógica conservadora
    // IMPORTANTE: La probabilidad solo indica confianza en el TIPO, NO en la severidad
    if (!clase) return "urgente";
    
    if (clase === "quemaduras") {
      if (probabilidad !== undefined && probabilidad < 0.6) return "urgente";
      return "moderado"; // Quemaduras siempre requieren atención
    } else if (clase === "cortadas") {
      // Lógica conservadora: las cortadas profundas pueden tener alta probabilidad pero ser graves
      if (probabilidad !== undefined && probabilidad < 0.6) return "urgente";
      if (probabilidad !== undefined && probabilidad < 0.85) return "moderado";
      // Incluso con alta confianza (>= 0.85), ser conservador
      // Las cortadas profundas requieren atención médica
      return "moderado"; // CAMBIADO: nunca retornar "leve" por seguridad
    }
    
    return "urgente"; // Por defecto, ser cauteloso
  };
  
  const [currentSeverity] = useState(calcularGravedad())

  // Limpiar la URL del blob cuando el componente se desmonte
  useEffect(() => {
    return () => {
      if (imageUrl && imageUrl.startsWith('blob:')) {
        URL.revokeObjectURL(imageUrl)
      }
    }
  }, [imageUrl])

  // Cargar conversaciones previas si hay diagnostico_id
  useEffect(() => {
    if (diagnostico_id) {
      fetch(`http://127.0.0.1:8001/conversaciones/${diagnostico_id}`)
        .then(res => res.json())
        .then(data => {
          if (Array.isArray(data)) {
            setConversaciones(data)
          }
        })
        .catch(err => console.error("Error cargando conversaciones:", err))
    }
  }, [diagnostico_id])

  // Early return después de todos los hooks
  if (!analysisData) return <p className="text-center mt-10 text-gray-700">No hay datos de análisis</p>

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
        return { injuryType: "Herida Arterial Profunda", confidence: confidence, recommendations: [] }

      default:
        return { injuryType: "Lesión Desconocida", confidence: confidence, recommendations: [] }

    }

  }

  const diagnosisData = getDiagnosisData(currentSeverity)

  const handlePregunta = async () => {
    if (!pregunta.trim() || !diagnostico_id) {
      alert("Por favor ingresa una pregunta válida.")
      return
    }

    setLoadingPregunta(true)
    const preguntaEnviar = pregunta.trim()
    setPregunta('') // Limpiar el input

    try {
      const response = await fetch("http://127.0.0.1:8001/preguntar-diagnostico/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          diagnostico_id: diagnostico_id,
          pregunta: preguntaEnviar,
          numero_control: numero_control || '',
          clase_detectada: clase,
          instrucciones_originales: instrucciones || respuesta || ''
        }),
      })

      const data = await response.json()
      
      if (data.respuesta) {
        // Agregar la nueva conversación al estado
        const nuevaConversacion = {
          pregunta: preguntaEnviar,
          respuesta: data.respuesta,
          fecha: new Date().toISOString()
        }
        setConversaciones([...conversaciones, nuevaConversacion])
      } else {
        alert("Error al generar la respuesta. Intenta nuevamente.")
      }
    } catch (error) {
      console.error("Error al hacer la pregunta:", error)
      alert("Ocurrió un error al comunicarse con el servidor.")
    } finally {
      setLoadingPregunta(false)
    }
  }

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

        {/* Alerta de gravedad urgente */}
        {currentSeverity === "urgente" && (
          <div className="bg-red-50 border-l-4 border-red-500 p-6 mb-6 rounded-lg shadow-lg animate-pulse">
            <div className="flex items-center">
              <FaExclamationCircle className="w-8 h-8 text-red-600 mr-4 flex-shrink-0" />
              <div>
                <h3 className="text-xl font-bold text-red-800 mb-2">⚠️ CASO URGENTE</h3>
                <p className="text-red-700 font-semibold">
                  Esta lesión requiere atención médica inmediata. Después de aplicar primeros auxilios básicos, 
                  busque asistencia médica de emergencia de inmediato.
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Información del diagnóstico con icono de gravedad */}
        <div className="bg-white p-6 rounded-xl shadow-md mb-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold text-gray-800">Información del Diagnóstico</h2>
            <div className="flex items-center gap-2">
              {currentSeverity === "leve" && (
                <div className="flex items-center gap-2 bg-green-100 px-4 py-2 rounded-full">
                  <FaCheckCircle className="w-5 h-5 text-green-600" />
                  <span className="text-green-700 font-semibold">LEVE</span>
                </div>
              )}
              {currentSeverity === "moderado" && (
                <div className="flex items-center gap-2 bg-yellow-100 px-4 py-2 rounded-full">
                  <FaExclamationTriangle className="w-5 h-5 text-yellow-600" />
                  <span className="text-yellow-700 font-semibold">MODERADO</span>
                </div>
              )}
              {currentSeverity === "urgente" && (
                <div className="flex items-center gap-2 bg-red-100 px-4 py-2 rounded-full">
                  <FaExclamationCircle className="w-5 h-5 text-red-600" />
                  <span className="text-red-700 font-semibold">URGENTE</span>
                </div>
              )}
            </div>
          </div>
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
    <div className="bg-gradient-to-r from-yellow-50 to-amber-50 border-l-4 border-yellow-500 p-6 mb-6 rounded-lg shadow-md">
      <div className="flex items-center mb-4">
        <div className="bg-yellow-100 rounded-full p-2 mr-3">
          <svg className="w-6 h-6 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <h2 className="text-xl font-bold text-gray-800">Recomendaciones de Primeros Auxilios</h2>
      </div>
      <div className="prose prose-sm max-w-none">
        <div className="text-gray-700 whitespace-pre-line leading-relaxed font-medium">
          {instrucciones.split('\n').map((line, index) => {
            // Función para limpiar markdown residual de una línea
            const limpiarLinea = (texto) => {
              if (!texto) return texto;
              // Remover **texto**
              texto = texto.replace(/\*\*(.*?)\*\*/g, '$1');
              // Remover __texto__
              texto = texto.replace(/__(.*?)__/g, '$1');
              // Remover *texto* (cursiva, pero no si es parte de una lista)
              texto = texto.replace(/(?<!\*)\*([^*]+)\*(?!\*)/g, '$1');
              // Remover _texto_ (cursiva)
              texto = texto.replace(/(?<!_)_([^_]+)_(?!_)/g, '$1');
              // Remover `texto`
              texto = texto.replace(/`([^`]+)`/g, '$1');
              // Remover ### encabezados
              texto = texto.replace(/^#{1,6}\s+/g, '');
              return texto.trim();
            };

            const lineaLimpia = limpiarLinea(line);
            
            // Detectar títulos (líneas que terminan con :)
            if (lineaLimpia.endsWith(':') && (lineaLimpia.includes('DESCRIPCIÓN') || lineaLimpia.includes('PASOS') || lineaLimpia.includes('ADVERTENCIAS') || lineaLimpia.includes('EVALUACIÓN'))) {
              return (
                <h3 key={index} className="text-lg font-bold text-gray-900 mt-4 mb-2 first:mt-0">
                  {lineaLimpia}
                </h3>
              );
            }
            // Detectar pasos numerados (a), b), c))
            if (/^[a-c]\)/.test(lineaLimpia)) {
              return (
                <p key={index} className="ml-4 mb-2 text-gray-800">
                  <span className="font-semibold text-indigo-600">{lineaLimpia.substring(0, 2)}</span>
                  {lineaLimpia.substring(2)}
                </p>
              );
            }
            // Detectar listas con guiones, asteriscos o números
            if (/^[0-9]+\./.test(lineaLimpia) || /^[-•*]\s/.test(lineaLimpia)) {
              const contenido = lineaLimpia.replace(/^[0-9]+\.\s*/, '').replace(/^[-•*]\s*/, '');
              return (
                <p key={index} className="ml-4 mb-2 text-gray-800 flex items-start">
                  <span className="mr-2 text-yellow-600">•</span>
                  <span>{contenido}</span>
                </p>
              );
            }
            // Detectar características con asteriscos (***Enrojecimiento:**)
            if (/^\*{2,3}/.test(lineaLimpia)) {
              const contenido = lineaLimpia.replace(/^\*{2,3}/, '').replace(/\*{2,3}/g, '');
              return (
                <p key={index} className="ml-4 mb-2 text-gray-800">
                  <span className="font-semibold text-gray-900">{contenido.split(':')[0]}:</span>
                  {contenido.split(':').slice(1).join(':')}
                </p>
              );
            }
            // Líneas normales
            if (lineaLimpia) {
              return (
                <p key={index} className="mb-2 text-gray-800">
                  {lineaLimpia}
                </p>
              );
            }
            // Líneas vacías
            return <br key={index} />;
          })}
        </div>
      </div>
    </div>
  ) : (
    <div className="bg-gray-50 border border-gray-200 p-4 mb-6 rounded-lg">
      <p className="text-gray-500 text-center">No hay recomendaciones disponibles.</p>
    </div>
  )}

        {/* Sección de Preguntas sobre el Diagnóstico */}
        {diagnostico_id && (
          <div className="bg-white p-6 rounded-xl shadow-md mb-6">
            <h2 className="text-xl font-semibold text-gray-800 mb-4">
              ¿Tienes preguntas sobre este diagnóstico?
            </h2>
            <p className="text-sm text-gray-600 mb-4">
              Puedes hacer preguntas sobre las recomendaciones o el análisis realizado.
            </p>

            {/* Historial de conversaciones */}
            {conversaciones.length > 0 && (
              <div className="mb-4 space-y-4 max-h-96 overflow-y-auto pr-2">
                {conversaciones.map((conv, index) => (
                  <div key={index} className="space-y-3">
                    {/* Pregunta del usuario */}
                    <div className="flex items-start gap-2">
                      <div className="flex-shrink-0 w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                        <FaUser className="w-4 h-4 text-blue-600" />
                      </div>
                      <div className="flex-1 bg-blue-50 rounded-lg p-3">
                        <p className="text-sm font-medium text-gray-700 mb-1">Tú:</p>
                        <p className="text-gray-800 whitespace-pre-line">{conv.pregunta}</p>
                      </div>
                    </div>
                    {/* Respuesta de Gemini */}
                    <div className="flex items-start gap-2">
                      <div className="flex-shrink-0 w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
                        <FaRobot className="w-4 h-4 text-green-600" />
                      </div>
                      <div className="flex-1 bg-green-50 rounded-lg p-3">
                        <p className="text-sm font-medium text-gray-700 mb-2">Asistente IA:</p>
                        <div className="text-gray-800 leading-relaxed">
                          {conv.respuesta.split('\n').map((line, index) => {
                            // Función para limpiar markdown residual de una línea
                            const limpiarLinea = (texto) => {
                              if (!texto) return texto;
                              // Remover **texto**
                              texto = texto.replace(/\*\*(.*?)\*\*/g, '$1');
                              // Remover __texto__
                              texto = texto.replace(/__(.*?)__/g, '$1');
                              // Remover *texto* (cursiva, pero no si es parte de una lista)
                              texto = texto.replace(/(?<!\*)\*([^*]+)\*(?!\*)/g, '$1');
                              // Remover _texto_ (cursiva)
                              texto = texto.replace(/(?<!_)_([^_]+)_(?!_)/g, '$1');
                              // Remover `texto`
                              texto = texto.replace(/`([^`]+)`/g, '$1');
                              // Remover ### encabezados
                              texto = texto.replace(/^#{1,6}\s+/g, '');
                              return texto.trim();
                            };

                            const lineaLimpia = limpiarLinea(line);
                            
                            // Detectar listas numeradas (1. 2. 3.)
                            if (/^[0-9]+\./.test(lineaLimpia)) {
                              const contenido = lineaLimpia.replace(/^[0-9]+\.\s*/, '');
                              return (
                                <p key={index} className="mb-2 ml-4 flex items-start">
                                  <span className="mr-2 text-green-600 font-semibold">{lineaLimpia.match(/^[0-9]+\./)?.[0]}</span>
                                  <span>{contenido}</span>
                                </p>
                              );
                            }
                            // Detectar listas con guiones o asteriscos
                            if (/^[-•*]\s/.test(lineaLimpia)) {
                              const contenido = lineaLimpia.replace(/^[-•*]\s*/, '');
                              return (
                                <p key={index} className="mb-2 ml-4 flex items-start">
                                  <span className="mr-2 text-green-600">•</span>
                                  <span>{contenido}</span>
                                </p>
                              );
                            }
                            // Detectar texto en negrita (aunque ya lo limpiamos, por si acaso)
                            if (lineaLimpia.includes('**') || lineaLimpia.includes('__')) {
                              const limpio = lineaLimpia.replace(/\*\*/g, '').replace(/__/g, '');
                              return (
                                <p key={index} className="mb-2">
                                  {limpio}
                                </p>
                              );
                            }
                            // Líneas normales
                            if (lineaLimpia) {
                              return (
                                <p key={index} className="mb-2">
                                  {lineaLimpia}
                                </p>
                              );
                            }
                            // Líneas vacías
                            return <br key={index} />;
                          })}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {/* Input para nueva pregunta */}
            <div className="flex gap-2">
              <input
                type="text"
                value={pregunta}
                onChange={(e) => setPregunta(e.target.value)}
                onKeyPress={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault()
                    handlePregunta()
                  }
                }}
                placeholder="Escribe tu pregunta aquí..."
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                disabled={loadingPregunta}
              />
              <button
                onClick={handlePregunta}
                disabled={!pregunta.trim() || loadingPregunta}
                className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
              >
                {loadingPregunta ? (
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                ) : (
                  <>
                    <FaPaperPlane className="mr-2" />
                    Enviar
                  </>
                )}
              </button>
            </div>
          </div>
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

