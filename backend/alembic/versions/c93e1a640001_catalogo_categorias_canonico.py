"""catálogo canónico de cuatro categorías

Revision ID: c93e1a640001
Revises: b82d0f530001
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "c93e1a640001"
down_revision: str | Sequence[str] | None = "b82d0f530001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("categorias", sa.Column("code", sa.String(50), nullable=True))
    op.execute("""
        UPDATE categorias SET code = CASE
          WHEN lower(nombre) ~ '(aire|clima|refrig)' THEN 'AIRES_ACONDICIONADOS'
          WHEN lower(nombre) ~ '(camara|cámara|cctv|video|seguridad)' THEN 'CAMARAS_SEGURIDAD'
          WHEN lower(nombre) ~ '(incend|extint|contra.?incend)' THEN 'PROTECCION_CONTRA_INCENDIOS'
          ELSE 'EQUIPOS_INDUSTRIALES'
        END
    """)
    # Si no existía alguna familia, se crea antes de consolidar duplicados.
    op.execute("""
        INSERT INTO categorias (id, code, nombre, descripcion, activo, created_at, updated_at)
        SELECT v.id::uuid, v.code, v.nombre, v.descripcion, true, now(), now()
        FROM (VALUES
          ('10000000-0000-4000-8000-000000000001', 'EQUIPOS_INDUSTRIALES', 'Equipos Industriales', 'Maquinaria, plantas, bombas, tableros y equipos de operación industrial.'),
          ('10000000-0000-4000-8000-000000000002', 'AIRES_ACONDICIONADOS', 'Aires Acondicionados', 'Sistemas de climatización, ventilación y refrigeración.'),
          ('10000000-0000-4000-8000-000000000003', 'CAMARAS_SEGURIDAD', 'Cámaras de Seguridad', 'CCTV, grabadores, cámaras y componentes de videovigilancia.'),
          ('10000000-0000-4000-8000-000000000004', 'PROTECCION_CONTRA_INCENDIOS', 'Sistemas de Protección Contra Incendios', 'Detección, alarma, extinción y redes contra incendio.')
        ) AS v(id, code, nombre, descripcion)
        WHERE NOT EXISTS (SELECT 1 FROM categorias c WHERE c.code = v.code)
    """)
    # Conserva una fila por código y mueve todas las referencias de equipos.
    op.execute("""
        WITH ranked AS (
          SELECT id, code, first_value(id) OVER (PARTITION BY code ORDER BY created_at NULLS LAST, id::text) canonical_id,
                 row_number() OVER (PARTITION BY code ORDER BY created_at NULLS LAST, id::text) rn
          FROM categorias
        )
        UPDATE equipos e SET categoria_id = r.canonical_id
        FROM ranked r WHERE e.categoria_id = r.id AND r.rn > 1
    """)
    op.execute("""
        DELETE FROM categorias c USING (
          SELECT id, row_number() OVER (PARTITION BY code ORDER BY created_at NULLS LAST, id::text) rn
          FROM categorias
        ) d WHERE c.id = d.id AND d.rn > 1
    """)
    op.execute("""
        UPDATE categorias SET
          nombre = CASE code
            WHEN 'EQUIPOS_INDUSTRIALES' THEN 'Equipos Industriales'
            WHEN 'AIRES_ACONDICIONADOS' THEN 'Aires Acondicionados'
            WHEN 'CAMARAS_SEGURIDAD' THEN 'Cámaras de Seguridad'
            WHEN 'PROTECCION_CONTRA_INCENDIOS' THEN 'Sistemas de Protección Contra Incendios'
          END,
          activo = true
    """)
    op.execute("""
        UPDATE equipos SET categoria_id = (
          SELECT id FROM categorias WHERE code = 'EQUIPOS_INDUSTRIALES' LIMIT 1
        ) WHERE categoria_id IS NULL
    """)
    op.alter_column("categorias", "code", nullable=False)
    op.create_unique_constraint("uq_categorias_code", "categorias", ["code"])
    op.alter_column("equipos", "categoria_id", nullable=False)


def downgrade() -> None:
    op.alter_column("equipos", "categoria_id", nullable=True)
    op.drop_constraint("uq_categorias_code", "categorias", type_="unique")
    op.drop_column("categorias", "code")
