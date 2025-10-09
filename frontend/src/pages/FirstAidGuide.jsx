import { useNavigate } from 'react-router-dom'
import { FaArrowLeft, FaHeart, FaBandAid, FaFire, FaBone, FaAllergies, FaUserInjured } from 'react-icons/fa'
import auxiLogo from '../assets/auxi.png'

function FirstAidGuide() {
  const navigate = useNavigate()

  /**
 * GUÍA DE PRIMEROS AUXILIOS - Manual de referencia rápida
 * 
 * Esta es una guía de consulta rápida con las 6 categorías más importantes de primeros auxilios.
 * 
 * ¿Qué hace?
 * - Muestra 6 categorías: RCP, Hemorragias, Quemaduras, Fracturas, Alergias, Heridas
 * - Cada categoría tiene icono, título y descripción
 * - Diseño fácil de leer en emergencias
 * - Acceso rápido desde cualquier parte de la aplicación
 * 
 * ¿Para qué sirve?
 * - Consulta rápida en situaciones de emergencia
 * - Refrescar conocimientos de primeros auxilios
 * - Guía paso a paso para situaciones críticas
 * - Complemento al diagnóstico de la IA
 * 
 * Flujo: Emergencia → Consulta guía → Aplica técnicas
 * tenia pensado que aqui se use la ia tambien para la guia
 */

  // Datos de las categorías de primeros auxilios
  const firstAidCategories = [
    {
      id: 1,
      icon: FaHeart,
      iconColor: "text-red-500",
      bgColor: "bg-red-50",
      borderColor: "border-red-200",
      title: "RCP - Reanimación Cardiopulmonar",
      description: "Procedimiento vital para mantener la circulación cuando alguien sufre un paro cardiaco."
    },
    {
      id: 2,
      icon: FaBandAid,
      iconColor: "text-blue-500",
      bgColor: "bg-blue-50",
      borderColor: "border-blue-200",
      title: "Hemorragias",
      description: "Técnicas para controlar sangrados externos y aplicar presión directa correctamente."
    },
    {
      id: 3,
      icon: FaFire,
      iconColor: "text-orange-500",
      bgColor: "bg-orange-50",
      borderColor: "border-orange-200",
      title: "Quemaduras",
      description: "Manejo adecuado de quemaduras leves y severas según su grado."
    },
    {
      id: 4,
      icon: FaBone,
      iconColor: "text-gray-700",
      bgColor: "bg-gray-50",
      borderColor: "border-gray-200",
      title: "Fracturas",
      description: "Inmovilización y manejo de extremidades rotas hasta atención médica."
    },
    {
      id: 5,
      icon: FaAllergies,
      iconColor: "text-green-600",
      bgColor: "bg-green-50",
      borderColor: "border-green-200",
      title: "Reacciones Alérgicas",
      description: "Identificación y tratamiento de reacciones alérgicas graves como anafilaxia."
    },
    {
      id: 6,
      icon: FaUserInjured,
      iconColor: "text-gray-700",
      bgColor: "bg-gray-50",
      borderColor: "border-gray-200",
      title: "Heridas Abiertas",
      description: "Limpieza y cierre de heridas para prevenir infecciones y promover cicatrización."
    }
  ]

  const handleBackToDiagnosis = () => {
    navigate('/')
  }

  return (
    <div className="min-h-screen bg-blue-50">
      {/* Header */}
      <header className="bg-white shadow-lg">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between py-6">
            <div className="flex items-center">
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
                <p className="text-sm text-gray-600">Guía de primeros auxilios médicos</p>
              </div>
            </div>
            </div>
            <div className="text-right">
              <p className="text-lg font-semibold text-gray-900">Guía de primeros auxilios</p>
              <p className="text-sm text-gray-500">2025</p>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Guide Card */}
        <div className="bg-white rounded-3xl shadow-xl p-8">
          
          {/* Title */}
          <h2 className="text-4xl font-bold text-gray-900 text-center mb-12">
            Guía de Primeros Auxilios
          </h2>

          {/* Categories Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 mb-12">
            {firstAidCategories.map((category) => (
              <div 
                key={category.id}
                className={`${category.bgColor} border-2 ${category.borderColor} rounded-2xl p-6 hover:shadow-lg transition-shadow duration-200 cursor-pointer`}
              >
                {/* Icon */}
                <div className="flex justify-center mb-4">
                  <div className={`w-16 h-16 bg-white rounded-full flex items-center justify-center shadow-md`}>
                    <category.icon className={`w-8 h-8 ${category.iconColor}`} />
                  </div>
                </div>

                {/* Title */}
                <h3 className="text-xl font-bold text-gray-900 text-center mb-3">
                  {category.title}
                </h3>

                {/* Description */}
                <p className="text-gray-700 text-center leading-relaxed">
                  {category.description}
                </p>
              </div>
            ))}
          </div>

          {/* Back Button */}
          <div className="text-center">
            <button 
              onClick={handleBackToDiagnosis}
              className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-4 px-8 rounded-xl transition-colors duration-200 shadow-lg hover:shadow-xl"
            >
              Volver al diagnóstico
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

export default FirstAidGuide
