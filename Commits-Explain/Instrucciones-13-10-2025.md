# Bitácora de Avance – 13/10/2025

**Proyecto:** IA First Aid – Diagnóstico de lesiones escolares
**Equipo:** Desarrollo Frontend + Backend

---

## 1. Resumen del día

Durante la jornada de hoy se avanzó en la integración entre el frontend y el backend, permitiendo que la enfermera o el usuario pueda subir imágenes de lesiones y recibir un diagnóstico generado por la IA. Además, se ajustó la estructura de componentes React para mostrar los resultados dinámicamente respecto al modelo_quemarudas_cortadas.h5 (modelo entrenado)

---

## 2. Backend – FastAPI (`app.py`)

Se configuró un **API REST** usando FastAPI para procesar imágenes y realizar predicciones con el modelo de IA.

**Principales funciones implementadas:**

* **CORS habilitado:** Permite que el frontend en React pueda hacer peticiones al backend sin restricciones de origen.
* **Carga del modelo:** Se utiliza `modelo_quemaduras_cortadas.h5` para clasificar lesiones en "quemaduras" y "cortadas".
* **Endpoint `/predict/`:**

  * Recibe imágenes vía `POST`.
  * Convierte la imagen a array y la normaliza para el modelo.
  * Retorna la clase detectada y la probabilidad de confianza.
  * Borra la imagen temporal después del análisis.

**Beneficio:** Esto permite que cualquier imagen subida desde la interfaz sea procesada automáticamente por el modelo de IA y devuelva un resultado listo para mostrar al usuario.

---

## 3. Frontend – React

### 3.1 Subida y análisis de imagen (`ImageAnalysis.js`)

* Permite a el usuario **subir imágenes** (PNG, JPG, GIF).
* Muestra **vista previa de la imagen** seleccionada.
* Envía la imagen al backend (`http://localhost:8000/predict/`) para su análisis mediante `fetch` y `FormData`.
* Redirige a la página de resultados pasando la predicción obtenida.

**Flujo:**
`usuario → Subida de imagen → IA analiza → Resultados dinámicos`

### 3.2 Visualización de resultados (`DiagnosisResults.js`)

* Recibe la predicción (`clase` y `probabilidad`) desde el backend.
* Muestra **tipo de lesión, confianza**
(Haría  falta agregar las recomendaciones a la herida previda analizada)

* Incluye botones de acción:

  * **Guardar resultado** (simulado, sin función)
  * **Nuevo diagnóstico** (redirige a la página de subida de imágenes)

**Nota:** Todos los datos mostrados son dinámicos y dependen directamente del resultado de la predicción de la IA.

---

## 4. Ejecución de la aplicación

Para ejecutar correctamente la aplicación se requieren **dos terminales** abiertas al mismo tiempo:

1. **Servidor del frontend (React + Vite)**

```bash
npm run dev
```

* Sirve la interfaz en `http://localhost:5173`.
* Refleja cambios en tiempo real al modificar los archivos de React.

2. **Servidor del backend (FastAPI)**

```bash
uvicorn app:app --reload
```
Para este paso de la inicialización del API, es necesario ejecutarlo desde IA-Convolucional

* Levanta la API en `http://localhost:8000` con el endpoint `/predict/`.
* El flag `--reload` permite aplicar cambios automáticamente sin reiniciar.

**Importante:** Ambos servidores deben estar corriendo simultáneamente para que el flujo completo de análisis de imágenes funcione correctamente.
## IMPORTANTE A INSTALAR 
pip install fastapi
pip install fastapi uvicorn
pip install python-multipart


---

## 5. Próximos pasos

* Implementar la funcionalidad de **guardar resultados en base de datos**.
* Agregar las recomendaciones según la severidad y tipo de herida.
* Agregar validaciones de imagen (tamaño máximo, formato permitido).
* Integrar alertas para emergencias (lesiones graves) en tiempo real.
