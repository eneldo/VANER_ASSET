-- ============================================================
-- FASE 34.2.2 - Backups Inteligentes SaaS PRO
-- Archivo: backend/sql/2026_fase_34_2_2_backups_inteligentes_saas.sql
-- Base de datos: PostgreSQL
-- ============================================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS backup_historial (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tipo VARCHAR(50) NOT NULL DEFAULT 'MANUAL',
    estado VARCHAR(30) NOT NULL DEFAULT 'PENDIENTE',
    nombre_archivo VARCHAR(255),
    ruta_archivo TEXT,
    tamano_bytes BIGINT DEFAULT 0,
    mensaje TEXT,
    incluye_db BOOLEAN NOT NULL DEFAULT TRUE,
    incluye_uploads BOOLEAN NOT NULL DEFAULT TRUE,
    incluye_codigo BOOLEAN NOT NULL DEFAULT FALSE,
    iniciado_en TIMESTAMPTZ DEFAULT NOW(),
    finalizado_en TIMESTAMPTZ,
    creado_por VARCHAR(120),
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE INDEX IF NOT EXISTS idx_backup_historial_estado ON backup_historial(estado);
CREATE INDEX IF NOT EXISTS idx_backup_historial_iniciado_en ON backup_historial(iniciado_en DESC);

-- Si existe el núcleo 34.2.1, asegura módulo backups.
INSERT INTO automatizaciones (id, modulo, nombre, descripcion, activo, frecuencia_minutos, estado, mensaje, configuracion)
SELECT uuid_generate_v4(),
       'backups',
       'Backups inteligentes SaaS',
       'Backup automático de PostgreSQL, evidencias/uploads y paquete ZIP descargable.',
       false,
       1440,
       'INACTIVO',
       'Fase 34.2.2 instalada. Active desde UI cuando desee ejecutar backups automáticos.',
       '{"hora":"02:00","retencion_dias":15,"incluir_db":true,"incluir_uploads":true,"incluir_codigo":false}'::json
WHERE EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name='automatizaciones')
  AND NOT EXISTS (SELECT 1 FROM automatizaciones WHERE modulo='backups');
