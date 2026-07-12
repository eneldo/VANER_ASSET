"""Tablas operativas administradas previamente con create_all

Revision ID: i59e7a2a0001
Revises: h48d6f190001
"""

from alembic import op

from app.models.automatizacion import Automatizacion, AutomatizacionLog
from app.models.backup_historial import BackupHistorial
from app.models.configuracion import ConfiguracionSistema
from app.models.configuracion_saas import ConfiguracionSaaS
from app.models.devops_evento import DevOpsEvento
from app.models.log_sistema import LogSistema
from app.models.monitor_estado import MonitorEstado
from app.models.scheduler_inteligente import SchedulerLog, SchedulerRegla, SchedulerSugerencia
from app.models.smtp_log import SMTPLog


revision = "i59e7a2a0001"
down_revision = "h48d6f190001"
branch_labels = None
depends_on = None


TABLAS = (
    Automatizacion.__table__,
    AutomatizacionLog.__table__,
    BackupHistorial.__table__,
    ConfiguracionSistema.__table__,
    ConfiguracionSaaS.__table__,
    DevOpsEvento.__table__,
    LogSistema.__table__,
    MonitorEstado.__table__,
    SMTPLog.__table__,
    SchedulerRegla.__table__,
    SchedulerSugerencia.__table__,
    SchedulerLog.__table__,
)

# Estas dos tablas existían antes de incorporarlas a Alembic. Se adoptan en
# upgrade y se preservan en downgrade para no destruir datos históricos.
TABLAS_ADOPTADAS = {"automatizaciones", "automatizacion_logs"}


def upgrade() -> None:
    bind = op.get_bind()
    for tabla in TABLAS:
        tabla.create(bind=bind, checkfirst=True)


def downgrade() -> None:
    bind = op.get_bind()
    for tabla in reversed(TABLAS):
        if tabla.name not in TABLAS_ADOPTADAS:
            tabla.drop(bind=bind, checkfirst=True)
