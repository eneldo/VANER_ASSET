-- ============================================================
-- SQL: Fase 34.1 Configuración Inteligente SaaS
-- Archivo: backend/sql/2026_fase_34_1_configuracion_inteligente_saas.sql
-- Base de datos: PostgreSQL
-- ============================================================

CREATE TABLE IF NOT EXISTS configuracion_saas (
    id INTEGER PRIMARY KEY DEFAULT 1,
    nombre_plataforma VARCHAR(150) NOT NULL DEFAULT 'VANER ASSET',
    logo_url TEXT NULL,
    color_primario VARCHAR(20) NOT NULL DEFAULT '#2563eb',
    color_secundario VARCHAR(20) NOT NULL DEFAULT '#0f172a',
    color_acento VARCHAR(20) NOT NULL DEFAULT '#22c55e',
    smtp JSONB NOT NULL DEFAULT '{}'::jsonb,
    backups JSONB NOT NULL DEFAULT '{}'::jsonb,
    evidencias JSONB NOT NULL DEFAULT '{}'::jsonb,
    mantenimiento JSONB NOT NULL DEFAULT '{}'::jsonb,
    notificaciones JSONB NOT NULL DEFAULT '{}'::jsonb,
    activo BOOLEAN NOT NULL DEFAULT TRUE,
    creado_en TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    actualizado_en TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT configuracion_saas_singleton CHECK (id = 1)
);

INSERT INTO configuracion_saas (
    id,
    nombre_plataforma,
    color_primario,
    color_secundario,
    color_acento,
    smtp,
    backups,
    evidencias,
    mantenimiento,
    notificaciones
)
VALUES (
    1,
    'VANER ASSET',
    '#2563eb',
    '#0f172a',
    '#22c55e',
    '{"host":"","port":587,"username":"","password":"","from_email":"","from_name":"VANER ASSET","use_tls":true,"use_ssl":false}'::jsonb,
    '{"habilitado":true,"frecuencia":"DIARIO","hora":"02:00","retencion_dias":30,"incluir_evidencias":true,"ruta_destino":"app/exports/backups"}'::jsonb,
    '{"max_mb":15,"formatos_permitidos":["jpg","jpeg","png","pdf","webp"],"requiere_descripcion":false,"permitir_pdf":true,"permitir_imagen":true,"compresion_imagen":true,"compresion_pdf":true,"calidad_imagen":82,"max_dimension_imagen":2048}'::jsonb,
    '{"dias_alerta_vencimiento":3,"permitir_reprogramacion":true,"requiere_evidencia_finalizar":true,"requiere_observacion_finalizar":true,"estados_permitidos":["PROGRAMADO","ASIGNADO","EN_PROCESO","PAUSADO","FINALIZADO","ANULADO"]}'::jsonb,
    '{"email_habilitado":true,"whatsapp_habilitado":false,"whatsapp_provider":"","whatsapp_token":"","notificar_asignacion":true,"notificar_vencimiento":true,"notificar_finalizacion":true,"notificar_cliente":true,"correos_copia":[]}'::jsonb
)
ON CONFLICT (id) DO NOTHING;

CREATE OR REPLACE FUNCTION set_configuracion_saas_actualizado_en()
RETURNS TRIGGER AS $$
BEGIN
    NEW.actualizado_en = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_configuracion_saas_actualizado_en ON configuracion_saas;
CREATE TRIGGER trg_configuracion_saas_actualizado_en
BEFORE UPDATE ON configuracion_saas
FOR EACH ROW
EXECUTE FUNCTION set_configuracion_saas_actualizado_en();
