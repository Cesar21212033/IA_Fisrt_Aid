create database first_ai;
use first_ai;
-- drop database first_ai;
CREATE TABLE historial_diagnosticos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    fecha DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    tipo VARCHAR(20) NOT NULL,            -- "imagen" o "texto"
    clase_detectada VARCHAR(50) NOT NULL, -- "quemaduras" o "cortadas"
    instrucciones TEXT                    -- recomendaciones de primeros auxilios
);


ALTER TABLE historial_diagnosticos
ADD COLUMN numero_control VARCHAR(50) NOT NULL AFTER clase_detectada,
ADD COLUMN nombre_completo VARCHAR(200) NOT NULL AFTER numero_control,
ADD COLUMN probabilidad DECIMAL(5,4) NULL AFTER clase_detectada;


CREATE TABLE IF NOT EXISTS conversaciones_diagnosticos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    diagnostico_id INT NOT NULL,
    numero_control VARCHAR(50) NOT NULL,
    pregunta TEXT NOT NULL,
    respuesta TEXT NOT NULL,
    fecha DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (diagnostico_id) REFERENCES historial_diagnosticos(id) ON DELETE CASCADE,
    INDEX idx_diagnostico_id (diagnostico_id),
    INDEX idx_numero_control (numero_control),
    INDEX idx_fecha (fecha)
);

