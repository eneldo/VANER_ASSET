-- ============================================================
-- FASE 18.1 - MANTENIMIENTOS PRO
-- Proyecto: SGA Empresarial
-- Motor: PostgreSQL
-- Objetivo:
--   1. Normalizar estados reales de mantenimiento.
--   2. Agregar técnico asignado.
--   3. Crear historial de cambios de estado.
--   4. Preparar trazabilidad PRO.
-- ============================================================

-- ============================================================
-- 1. Agregar columnas PRO a mantenimientos
-- ============================================================

ALTER TABLE mantenimientos
ADD COLUMN IF NOT EXISTS estado VARCHAR(30) DEFAULT 'PROGRAMADO';

ALTER TABLE mantenimientos
ADD COLUMN IF NOT EXISTS tecnico_id INTEGER NULL;

ALTER TABLE mantenimientos
ADD COLUMN IF NOT EXISTS fecha_asignacion TIMESTAMP NULL;

ALTER TABLE mantenimientos
ADD COLUMN IF NOT EXISTS fecha_inicio TIMESTAMP NULL;

ALTER TABLE mantenimientos
ADD COLUMN IF NOT EXISTS fecha_pausa TIMESTAMP NULL;

ALTER TABLE mantenimientos
ADD COLUMN IF NOT EXISTS fecha_finalizacion TIMESTAMP NULL;

ALTER TABLE mantenimientos
ADD COLUMN IF NOT EXISTS motivo_anulacion TEXT NULL;

ALTER TABLE mantenimientos
ADD COLUMN IF NOT EXISTS observacion_estado TEXT NULL;

ALTER TABLE mantenimientos
ADD COLUMN IF NOT EXISTS actualizado_en TIMESTAMP DEFAULT NOW();

-- ============================================================
-- 2. Relación con técnicos
-- ============================================================

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM information_schema.table_constraints
        WHERE constraint_name = 'fk_mantenimientos_tecnico'
    ) THEN
        ALTER TABLE mantenimientos
        ADD CONSTRAINT fk_mantenimientos_tecnico
        FOREIGN KEY (tecnico_id)
        REFERENCES tecnicos(id)
        ON DELETE SET NULL;
    END IF;
END $$;

-- ============================================================
-- 3. Validación de estados permitidos
-- ============================================================

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM information_schema.table_constraints
        WHERE constraint_name = 'chk_mantenimientos_estado_pro'
    ) THEN
        ALTER TABLE mantenimientos
        ADD CONSTRAINT chk_mantenimientos_estado_pro
        CHECK (
            estado IN (
                'PROGRAMADO',
                'ASIGNADO',
                'EN_PROCESO',
                'PAUSADO',
                'FINALIZADO',
                'ANULADO'
            )
        );
    END IF;
END $$;

-- ============================================================
-- 4. Tabla historial de mantenimiento
-- ============================================================

CREATE TABLE IF NOT EXISTS hist_mantenimiento (
    id SERIAL PRIMARY KEY,

    mantenimiento_id INTEGER NOT NULL,
    estado_anterior VARCHAR(30),
    estado_nuevo VARCHAR(30) NOT NULL,

    tecnico_id INTEGER NULL,

    observacion TEXT NULL,
    creado_por VARCHAR(120) NULL,

    fecha_evento TIMESTAMP DEFAULT NOW(),

    CONSTRAINT fk_hist_mantenimiento_mantenimiento
        FOREIGN KEY (mantenimiento_id)
        REFERENCES mantenimientos(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_hist_mantenimiento_tecnico
        FOREIGN KEY (tecnico_id)
        REFERENCES tecnicos(id)
        ON DELETE SET NULL
);

-- ============================================================
-- 5. Índices recomendados
-- ============================================================

CREATE INDEX IF NOT EXISTS idx_mantenimientos_estado
ON mantenimientos(estado);

CREATE INDEX IF NOT EXISTS idx_mantenimientos_tecnico_id
ON mantenimientos(tecnico_id);

CREATE INDEX IF NOT EXISTS idx_hist_mantenimiento_mantenimiento_id
ON hist_mantenimiento(mantenimiento_id);

CREATE INDEX IF NOT EXISTS idx_hist_mantenimiento_fecha_evento
ON hist_mantenimiento(fecha_evento);

-- ============================================================
-- 6. Actualizar registros antiguos
-- ============================================================

UPDATE mantenimientos
SET estado = 'PROGRAMADO'
WHERE estado IS NULL OR estado = '';