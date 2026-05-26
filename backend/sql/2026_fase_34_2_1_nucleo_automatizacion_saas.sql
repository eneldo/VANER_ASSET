-- ============================================================
-- FASE 34.2.1 - NÚCLEO AUTOMATIZACIÓN SaaS PRO
-- Archivo: backend/sql/2026_fase_34_2_1_nucleo_automatizacion_saas.sql
-- ============================================================
-- Ejecutar opcionalmente en pgAdmin si quieres crear tablas antes
-- del deploy. El backend también puede crearlas automáticamente.
-- ============================================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS automatizaciones (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    modulo VARCHAR(80) NOT NULL UNIQUE,
    nombre VARCHAR(150) NOT NULL,
    descripcion TEXT NULL,
    activo BOOLEAN NOT NULL DEFAULT FALSE,
    frecuencia_minutos INTEGER NOT NULL DEFAULT 60,
    estado VARCHAR(30) NOT NULL DEFAULT 'INACTIVO',
    mensaje TEXT NULL,
    ultima_ejecucion TIMESTAMPTZ NULL,
    proxima_ejecucion TIMESTAMPTZ NULL,
    configuracion JSONB NULL DEFAULT '{}'::jsonb,
    creado_en TIMESTAMPTZ DEFAULT NOW(),
    actualizado_en TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS automatizacion_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    automatizacion_id UUID NULL REFERENCES automatizaciones(id) ON DELETE SET NULL,
    modulo VARCHAR(80) NOT NULL,
    nivel VARCHAR(20) NOT NULL DEFAULT 'INFO',
    evento VARCHAR(120) NOT NULL,
    mensaje TEXT NULL,
    duracion_ms INTEGER NULL,
    metadata_json JSONB NULL DEFAULT '{}'::jsonb,
    creado_en TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_automatizaciones_modulo ON automatizaciones(modulo);
CREATE INDEX IF NOT EXISTS idx_automatizacion_logs_modulo ON automatizacion_logs(modulo);
CREATE INDEX IF NOT EXISTS idx_automatizacion_logs_creado ON automatizacion_logs(creado_en DESC);
