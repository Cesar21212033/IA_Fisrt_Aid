import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { FaArrowLeft, FaCamera } from 'react-icons/fa'
import auxiLogo from '../assets/auxi.png'

/**
 * ANÁLISIS POR IMAGEN - Subir foto de la lesión
 * 
 * Esta página es para cuando la enfermera puede tomar una foto de la lesión del estudiante.
 * 
 * ¿Qué hace?
 * - Permite subir una imagen (PNG, JPG, GIF)
 * - Muestra una vista previa de la imagen seleccionada
 * - Simula el análisis de la IA (por ahora solo muestra "Analizando...")
 * - Al terminar, lleva a la página de resultados
 * 
 * ¿Para qué sirve?
 * - Para lesiones visibles como cortes, quemaduras, golpes, etc.
 * - La IA puede "ver" la imagen y dar recomendaciones específicas
 * 
 * Flujo: Enfermera toma foto → Sube imagen → IA analiza → Ve resultados
 */

function ImageAnalysis() {
  const navigate = useNavigate()
  const [selectedImage, setSelectedImage] = useState(null)
  const [isAnalyzing, setIsAnalyzing] = useState(false)

  const handleImageUpload = (event) => {
    const file = event.target.files[0]
    if (file) {
      setSelectedImage(file)
    }
  }

  const handleAnalyze = async () => {
  if (!selectedImage) return;
  setIsAnalyzing(true);

  try {
    // Preparar FormData con la imagen
    const formData = new FormData();
    formData.append("file", selectedImage);

    // Enviar al backend
    const response = await fetch("http://localhost:8000/predict/", {
      method: "POST",
      body: formData,
    });

    const data = await response.json();
    setIsAnalyzing(false);

    if (data.error) {
      alert(data.error);
      return;
    }

    // Redirigir a la página de resultados y pasar la predicción
    navigate("/diagnosis-results", { state: data });

  } catch (err) {
    setIsAnalyzing(false);
    alert("Error al analizar la imagen. Revisa que el backend esté corriendo.");
  }
};



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
                <h1 className="text-2xl font-bold text-gray-900">Análisis por Imagen</h1>
                <p className="text-sm text-gray-600">Diagnóstico visual de lesiones</p>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="max-w-2xl mx-auto">
          
          {/* Upload Section */}
          <div className="bg-white rounded-2xl shadow-xl p-8">
            <h3 className="text-2xl font-semibold text-gray-900 mb-6 text-center">
              Subir Imagen de la Lesión
            </h3>
            
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-indigo-400 transition-colors">
              <div className="mb-4">
                <FaCamera className="mx-auto h-12 w-12 text-gray-400" />
              </div>
              <div className="mb-4">
                <label htmlFor="image-upload" className="cursor-pointer">
                  <span className="text-lg font-medium text-indigo-600 hover:text-indigo-500">
                    Haz clic para subir
                  </span>
                  <span className="text-gray-600"> o arrastra y suelta</span>
                </label>
                <input
                  id="image-upload"
                  type="file"
                  accept="image/*"
                  onChange={handleImageUpload}
                  className="hidden"
                />
              </div>
              <p className="text-sm text-gray-500">
                PNG, JPG, GIF hasta 10MB
              </p>
            </div>

            {selectedImage && (
              <div className="mt-6">
                <h4 className="text-lg font-medium text-gray-900 mb-3">Imagen seleccionada:</h4>
                <div className="relative">
                  <img
                    src={URL.createObjectURL(selectedImage)}
                    alt="Preview"
                    className="w-full h-64 object-cover rounded-lg"
                  />
                </div>
                <button 
                  onClick={handleAnalyze}
                  disabled={isAnalyzing}
                  className="mt-4 w-full bg-indigo-600 text-white py-3 px-4 rounded-lg font-medium hover:bg-indigo-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isAnalyzing ? (
                    <div className="flex items-center justify-center">
                      <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                      Analizando imagen...
                    </div>
                  ) : (
                    'Analizar Imagen'
                  )}
                </button>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  )
}

export default ImageAnalysis