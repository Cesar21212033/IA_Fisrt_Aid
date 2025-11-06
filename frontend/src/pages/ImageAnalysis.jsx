import React, { useState, useEffect } from "react";
import { useNavigate } from 'react-router-dom';
import { FaArrowLeft, FaCamera } from 'react-icons/fa';
import auxiLogo from '../assets/auxi.png';

export default function ImageAnalysis() {
  const navigate = useNavigate();
  const [selectedFile, setSelectedFile] = useState(null);
  const [serverStatus, setServerStatus] = useState("⏳ Verificando conexión...");
  const [loading, setLoading] = useState(false);
  const [numeroControl, setNumeroControl] = useState('');
  const [nombreCompleto, setNombreCompleto] = useState('');

  // ==============================
  //  Verificar conexión con el backend
  // ==============================
  useEffect(() => {
    fetch("http://127.0.0.1:8001/")
      .then((res) => res.json())
      .then((data) => setServerStatus(data.mensaje))
      .catch(() => setServerStatus("No se pudo conectar con el servidor FastAPI."));
  }, []);

  // Agrega esta función dentro del componente ImageAnalysis
const handleReset = () => {
  setSelectedFile(null);
};


  // ==============================
  //  Manejar selección de imagen
  // ==============================
  const handleFileChange = (e) => {
    const file = e.target.files[0];
    setSelectedFile(file);
  };

  // ==============================
  //  Enviar imagen al backend para analizar y entrenar incremental
  // ==============================
  const handleUpload = async () => {
    if (!selectedFile) {
      alert("Selecciona una imagen primero.");
      return;
    }

    // Validar campos obligatorios
    if (!numeroControl.trim()) {
      alert("El número de control es obligatorio.");
      return;
    }
    if (!nombreCompleto.trim()) {
      alert("El nombre completo es obligatorio.");
      return;
    }

    setLoading(true);

    try {
      const formData = new FormData();
      formData.append("file", selectedFile);
      formData.append("clase", "quemaduras"); // o "cortadas", según corresponda
      formData.append("numero_control", numeroControl.trim());
      formData.append("nombre_completo", nombreCompleto.trim());

      const response = await fetch("http://127.0.0.1:8001/predict_and_train/", {
        method: "POST",
        body: formData,
      });

      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || JSON.stringify(data));

      // Crear URL de la imagen para mostrarla en DiagnosisResults
      const imageUrl = URL.createObjectURL(selectedFile);
      
      // Navegar a DiagnosisResults con los datos
      navigate('/diagnosis-results', {
        state: {
          clase: data.clase,
          probabilidad: data.probabilidad,
          instrucciones: data.instrucciones,
          imageUrl: imageUrl,
          tipo: 'imagen'
        }
      });

    } catch (error) {
      console.error("Error al procesar la imagen:", error);
      const message = error.message ? error.message : JSON.stringify(error);
      alert(`Hubo un error al procesar la imagen: ${message}`);
    } finally {
      setLoading(false);
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
                  <img src={auxiLogo} alt="Auxi.ai Logo" className="w-10 h-10 object-contain" />
                </div>
              </div>
              <div className="ml-4">
                <h1 className="text-2xl font-bold text-gray-900">Análisis por Imagen</h1>
                <p className="text-sm text-gray-600">{serverStatus}</p>
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
            
            {/* Campos obligatorios */}
            <div className="mb-6 space-y-4">
              <div>
                <label htmlFor="numero-control" className="block text-sm font-medium text-gray-700 mb-2">
                  Número de Control <span className="text-red-500">*</span>
                </label>
                <input
                  id="numero-control"
                  type="text"
                  value={numeroControl}
                  onChange={(e) => setNumeroControl(e.target.value)}
                  placeholder="Ingrese el número de control"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                  required
                />
              </div>
              <div>
                <label htmlFor="nombre-completo" className="block text-sm font-medium text-gray-700 mb-2">
                  Nombre Completo <span className="text-red-500">*</span>
                </label>
                <input
                  id="nombre-completo"
                  type="text"
                  value={nombreCompleto}
                  onChange={(e) => setNombreCompleto(e.target.value)}
                  placeholder="Ingrese el nombre completo del estudiante"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                  required
                />
              </div>
            </div>
            
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-indigo-400 transition-colors">
              <div className="mb-4">
                <FaCamera className="mx-auto h-12 w-12 text-gray-400" />
              </div>
              <div className="mb-4">
                <label htmlFor="image-upload" className="cursor-pointer">
                  <span className="text-lg font-medium text-indigo-600 hover:text-indigo-500">Haz clic para subir</span>
                  <span className="text-gray-600"> o arrastra y suelta</span>
                </label>
                <input
                  id="image-upload"
                  type="file"
                  accept="image/*"
                  onChange={handleFileChange}
                  className="hidden"
                />
              </div>
              <p className="text-sm text-gray-500">PNG, JPG, GIF hasta 10MB</p>
            </div>

            {/* Vista previa */}
            {selectedFile && (
              <div className="mt-6">
                <h4 className="text-lg font-medium text-gray-900 mb-3">Imagen seleccionada:</h4>
                <div className="relative">
                  <img
                    src={URL.createObjectURL(selectedFile)}
                    alt="Preview"
                    className="w-full h-64 object-cover rounded-lg"
                  />
                </div>
                <button 
                  onClick={handleUpload}
                  disabled={loading || !numeroControl.trim() || !nombreCompleto.trim()}
                  className="mt-4 w-full bg-indigo-600 text-white py-3 px-4 rounded-lg font-medium hover:bg-indigo-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {loading ? (
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
  );
}
