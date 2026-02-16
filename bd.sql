create database first_ai;
use first_ai;
-- drop database first_ai;
CREATE TABLE historial_diagnosticos (
    id serial PRIMARY KEY,
    fecha DATE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    tipo VARCHAR(20) NOT NULL,            -- "imagen" o "texto"
    clase_detectada VARCHAR(50) NOT NULL, -- "quemaduras" o "cortadas"
    instrucciones TEXT                    -- recomendaciones de primeros auxilios
);


ALTER TABLE historial_diagnosticos
ADD COLUMN numero_control VARCHAR(50) NOT NULL 
ALTER TABLE historial_diagnosticos
ADD COLUMN nombre_completo VARCHAR(200) NOT NULL ,
ADD COLUMN probabilidad DECIMAL(5,4) NULL;


CREATE TABLE IF NOT EXISTS conversaciones_diagnosticos (
    id serial PRIMARY KEY,
    diagnostico_id INT NOT NULL,
    numero_control VARCHAR(50) NOT NULL,
    pregunta TEXT NOT NULL,
    respuesta TEXT NOT NULL,
    fecha DATE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (diagnostico_id) REFERENCES historial_diagnosticos(id) ON DELETE CASCADE

);