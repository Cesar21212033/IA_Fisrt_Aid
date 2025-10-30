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