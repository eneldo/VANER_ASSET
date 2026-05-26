-- ============================================================
-- SQL: FASE 34.2.3 SMTP Inteligente SaaS PRO
-- Archivo: backend/sql/2026_fase_34_2_3_smtp_inteligente_saas.sql
-- ============================================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS smtp_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    destinatario VARCHAR(255) NOT NULL,
    asunto VARCHAR(255) NOT NULL,
    plantilla VARCHAR(100),
    modulo_origen VARCHAR(80) NOT NULL DEFAULT 'smtp_inteligente',
    estado VARCHAR(30) NOT NULL DEFAULT 'PENDIENTE',
    mensaje_error TEXT,
    enviado BOOLEAN NOT NULL DEFAULT FALSE,
    intentos INTEGER NOT NULL DEFAULT 0,
    metadata_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    creado_en TIMESTAMPTZ DEFAULT NOW(),
    enviado_en TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS ix_smtp_logs_destinatario ON smtp_logs(destinatario);
CREATE INDEX IF NOT EXISTS ix_smtp_logs_estado ON smtp_logs(estado);
CREATE INDEX IF NOT EXISTS ix_smtp_logs_plantilla ON smtp_logs(plantilla);
CREATE INDEX IF NOT EXISTS ix_smtp_logs_modulo_origen ON smtp_logs(modulo_origen);
CREATE INDEX IF NOT EXISTS ix_smtp_logs_creado_en ON smtp_logs(creado_en);

-- Asegura que el módulo SMTP exista en automatizaciones si la FASE 34.2.1 ya está instalada.
INSERT INTO automatizaciones (id, modulo, nombre, descripcion, activo, frecuencia_minutos, estado, mensaje, configuracion)
SELECT uuid_generate_v4(), 'smtp', 'Correos automáticos SMTP', 'Motor SMTP inteligente para pruebas, plantillas, alertas y notificaciones automáticas.', false, 30, 'INACTIVO', 'Configuración SMTP Inteligente Fase 34.2.3', '{"modo":"cola","plantillas_html":true}'::jsonb
WHERE EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name='automatizaciones')
ON CONFLICT (modulo) DO NOTHING;
