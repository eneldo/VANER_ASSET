-- ============================================================
-- MIGRACIÓN SQL: Configuración PRO SaaS
-- Archivo: backend/sql/2026_configuracion_pro.sql
-- Ejecutar en PostgreSQL sobre la base de datos de SGA.
-- ============================================================

CREATE TABLE IF NOT EXISTS configuracion_sistema (
    id INTEGER PRIMARY KEY,

    nombre_plataforma VARCHAR(150) NOT NULL DEFAULT 'VANER ASSET',
    empresa_propietaria VARCHAR(180),
    nit VARCHAR(50),
    correo_soporte VARCHAR(160),
    telefono_soporte VARCHAR(80),
    url_plataforma VARCHAR(255),
    logo_url VARCHAR(500),
    color_primario VARCHAR(20) NOT NULL DEFAULT '#2563eb',
    color_secundario VARCHAR(20) NOT NULL DEFAULT '#0f172a',

    intentos_login INTEGER NOT NULL DEFAULT 5,
    minutos_bloqueo INTEGER NOT NULL DEFAULT 15,
    expiracion_token_min INTEGER NOT NULL DEFAULT 60,
    exigir_password_seguro BOOLEAN NOT NULL DEFAULT TRUE,
    doble_factor_activo BOOLEAN NOT NULL DEFAULT FALSE,
    auditoria_activa BOOLEAN NOT NULL DEFAULT TRUE,

    max_tamano_evidencia_mb INTEGER NOT NULL DEFAULT 10,
    permitir_pdf BOOLEAN NOT NULL DEFAULT TRUE,
    permitir_imagenes BOOLEAN NOT NULL DEFAULT TRUE,
    ruta_evidencias VARCHAR(500) NOT NULL DEFAULT 'app/uploads/evidencias',
    retencion_evidencias_dias INTEGER NOT NULL DEFAULT 365,

    backups_activos BOOLEAN NOT NULL DEFAULT TRUE,
    frecuencia_backup VARCHAR(50) NOT NULL DEFAULT 'DIARIO',
    hora_backup VARCHAR(10) NOT NULL DEFAULT '02:00',
    ruta_backup VARCHAR(500) NOT NULL DEFAULT 'app/backups',
    retencion_backups_dias INTEGER NOT NULL DEFAULT 30,

    dias_alerta_mantenimiento INTEGER NOT NULL DEFAULT 7,
    permitir_mantenimiento_vencido BOOLEAN NOT NULL DEFAULT TRUE,
    requiere_evidencia_cierre BOOLEAN NOT NULL DEFAULT TRUE,
    requiere_observacion_cierre BOOLEAN NOT NULL DEFAULT TRUE,
    estados_mantenimiento TEXT NOT NULL DEFAULT 'PROGRAMADO,ASIGNADO,EN_PROCESO,PAUSADO,FINALIZADO,ANULADO',

    notificaciones_activas BOOLEAN NOT NULL DEFAULT TRUE,
    notificar_email BOOLEAN NOT NULL DEFAULT TRUE,
    notificar_whatsapp BOOLEAN NOT NULL DEFAULT FALSE,
    dias_antes_notificar INTEGER NOT NULL DEFAULT 3,
    email_remitente VARCHAR(160),
    smtp_host VARCHAR(160),
    smtp_puerto INTEGER,
    smtp_usuario VARCHAR(160),
    smtp_password VARCHAR(255),

    creado_en TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    actualizado_en TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

INSERT INTO configuracion_sistema (id)
VALUES (1)
ON CONFLICT (id) DO NOTHING;
