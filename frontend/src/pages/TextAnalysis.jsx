import React, { useState, useEffect } from "react";
import { FaArrowLeft, FaSearch, FaRedo } from 'react-icons/fa';
import { useNavigate } from 'react-router-dom';
import auxiLogo from '../assets/auxi.png';

export default function TextWoundAnalysis() {
  const navigate = useNavigate();
  const [description, setDescription] = useState('');
  const [loading, setLoading] = useState(false);
  const [isValid, setIsValid] = useState(false);
  const [numeroControl, setNumeroControl] = useState('');
  const [nombreCompleto, setNombreCompleto] = useState('');

  // Validación en tiempo real del texto ingresado
  useEffect(() => {
    const texto = description.toLowerCase();

    const extremidadValida = /(brazo|pierna)/i.test(texto);
    const tipoValido = /(cortad[ao]|corte|me cort[ée]|quemadur[ao])/i.test(texto);

    setIsValid(extremidadValida && tipoValido);
  }, [description]);

  const handleAnalyze = async () => {
    if (!description.trim() || !isValid) {
      alert("Por favor, describe solo cortadas o quemaduras en brazos o piernas.");
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
      const response = await fetch("http://127.0.0.1:8001/analyze-symptoms", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
          symptoms: description,
          numero_control: numeroControl.trim(),
          nombre_completo: nombreCompleto.trim()
        }),
      });

      const data = await response.json();

      if (data.respuesta) {
        // Determinar la clase basada en el texto
        const texto = description.toLowerCase();
        let clase = "desconocida";
        if (texto.includes("quemadura")) {
          clase = "quemaduras";
        } else if (texto.includes("cortada") || texto.includes("corte")) {
          clase = "cortadas";
        }

        // Navegar a DiagnosisResults con los datos
        navigate('/diagnosis-results', {
          state: {
            clase: clase,
            probabilidad: 1.0, // No hay probabilidad en análisis de texto
            respuesta: data.respuesta,
            instrucciones: data.respuesta, // La respuesta es la recomendación
            textoIngresado: description, // El texto que ingresó el usuario
            tipo: 'texto'
          }
        });
      } else if (data.error) {
        console.error("Error del servidor:", data.error);
        alert("Ocurrió un error al generar la recomendación.");
      }
    } catch (error) {
      console.error("Error al solicitar la recomendación:", error);
      alert("Ocurrió un error al comunicarse con el servidor.");
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setDescription('');
    setIsValid(false);
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
                <h1 className="text-2xl font-bold text-gray-900">Recomendación por Texto</h1>
                <p className="text-sm text-gray-600">Describe la herida y recibe primeros auxilios</p>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="max-w-2xl mx-auto">
          <div className="bg-white rounded-2xl shadow-xl p-8">
            <h3 className="text-2xl font-semibold text-gray-900 mb-6 text-center">
              Describe la herida
            </h3>

            {/* Campos obligatorios */}
            <div className="mb-6 space-y-4">
              <div>
                <label htmlFor="numero-control-text" className="block text-sm font-medium text-gray-700 mb-2">
                  Número de Control <span className="text-red-500">*</span>
                </label>
                <input
                  id="numero-control-text"
                  type="text"
                  value={numeroControl}
                  onChange={(e) => setNumeroControl(e.target.value)}
                  placeholder="Ingrese el número de control"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                  required
                />
              </div>
              <div>
                <label htmlFor="nombre-completo-text" className="block text-sm font-medium text-gray-700 mb-2">
                  Nombre Completo <span className="text-red-500">*</span>
                </label>
                <input
                  id="nombre-completo-text"
                  type="text"
                  value={nombreCompleto}
                  onChange={(e) => setNombreCompleto(e.target.value)}
                  placeholder="Ingrese el nombre completo del estudiante"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                  required
                />
              </div>
            </div>

            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Ejemplo: El estudiante tiene un corte superficial de 2 cm en el brazo..."
              className="w-full h-64 p-4 border border-gray-300 rounded-lg resize-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            />

            {description.trim() && !isValid && (
              <p className="text-red-600 mt-2 text-sm">
                Solo se permiten cortadas o quemaduras en brazos o piernas
              </p>
            )}

            <button
              onClick={handleAnalyze}
              disabled={!description.trim() || !isValid || loading || !numeroControl.trim() || !nombreCompleto.trim()}
              className="mt-4 w-full bg-indigo-600 text-white py-3 px-4 rounded-lg font-medium hover:bg-indigo-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
            >
              {loading ? (
                <div className="flex items-center justify-center">
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                  Generando recomendación...
                </div>
              ) : (
                <>
                  <FaSearch className="w-4 h-4 mr-2" />
                  Obtener recomendación
                </>
              )}
            </button>

          </div>
        </div>
      </main>
    </div>
  );
}
