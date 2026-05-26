# ============================================================
# SERVICIO: SMTP Inteligente SaaS PRO
# Archivo: backend/app/services/smtp_inteligente_service.py
# FASE 34.2.3
# ============================================================

import smtplib
from datetime import datetime, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any, Dict, Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.configuracion_saas import ConfiguracionSaaS
from app.models.smtp_log import SMTPLog

try:
    from app.models.automatizacion import Automatizacion
except Exception:  # pragma: no cover - compatible si la fase 34.2.1 no está aplicada
    Automatizacion = None


DEFAULT_FROM_NAME = "SGA SaaS PRO"


def obtener_configuracion_smtp(db: Session) -> Dict[str, Any]:
    """Obtiene el bloque SMTP guardado en Configuración Inteligente SaaS."""

    config = db.query(ConfiguracionSaaS).filter(ConfiguracionSaaS.id == 1).first()
    if not config:
        return {}

    return config.smtp or {}


def smtp_configurado(smtp: Dict[str, Any]) -> bool:
    host = smtp.get("host") or smtp.get("smtp_host")
    from_email = smtp.get("from_email") or smtp.get("username") or smtp.get("correo")
    return bool(host and from_email)


def obtener_estado_smtp(db: Session) -> Dict[str, Any]:
    smtp = obtener_configuracion_smtp(db)

    automatizacion_activa = False
    if Automatizacion is not None:
        auto = db.query(Automatizacion).filter(Automatizacion.modulo == "smtp").first()
        automatizacion_activa = bool(auto and auto.activo)

    host = smtp.get("host") or smtp.get("smtp_host")
    port = int(smtp.get("port") or smtp.get("puerto") or 587)
    from_email = smtp.get("from_email") or smtp.get("username") or smtp.get("correo")
    from_name = smtp.get("from_name") or smtp.get("nombre_remitente") or DEFAULT_FROM_NAME

    configurado = smtp_configurado(smtp)

    return {
        "activo": bool(smtp.get("activo", configurado)),
        "configurado": configurado,
        "host": host,
        "port": port,
        "from_email": from_email,
        "from_name": from_name,
        "use_tls": bool(smtp.get("use_tls", True)),
        "use_ssl": bool(smtp.get("use_ssl", False)),
        "automatizacion_activa": automatizacion_activa,
        "mensaje": "SMTP configurado" if configurado else "Configura SMTP en Configuración Inteligente antes de enviar correos.",
    }


def render_template_base(titulo: str, mensaje: str, subtitulo: Optional[str] = None) -> str:
    subtitulo_html = f"<p style='color:#64748b;margin-top:-6px'>{subtitulo}</p>" if subtitulo else ""
    return f"""
    <!doctype html>
    <html lang="es">
      <body style="margin:0;background:#f1f5f9;font-family:Arial,Helvetica,sans-serif;color:#0f172a;">
        <table width="100%" cellpadding="0" cellspacing="0" style="padding:28px;background:#f1f5f9;">
          <tr><td align="center">
            <table width="100%" cellpadding="0" cellspacing="0" style="max-width:680px;background:#ffffff;border:1px solid #e2e8f0;border-radius:18px;overflow:hidden;">
              <tr>
                <td style="background:linear-gradient(135deg,#0f172a,#2563eb);padding:26px 30px;color:#fff;">
                  <h1 style="margin:0;font-size:24px;">{titulo}</h1>
                  {subtitulo_html}
                </td>
              </tr>
              <tr>
                <td style="padding:28px 30px;font-size:15px;line-height:1.65;">
                  {mensaje}
                </td>
              </tr>
              <tr>
                <td style="padding:18px 30px;background:#f8fafc;color:#64748b;font-size:12px;">
                  SGA SaaS PRO · Notificación automática empresarial
                </td>
              </tr>
            </table>
          </td></tr>
        </table>
      </body>
    </html>
    """


def enviar_correo_smtp(
    db: Session,
    destinatario: str,
    asunto: str,
    mensaje: str,
    plantilla: str = "manual",
    metadata: Optional[Dict[str, Any]] = None,
    html: Optional[str] = None,
) -> SMTPLog:
    """Envía correo real y registra log. No toca otros módulos existentes."""

    smtp = obtener_configuracion_smtp(db)
    if not smtp_configurado(smtp):
        raise HTTPException(status_code=400, detail="SMTP no configurado. Configúralo en Configuración Inteligente SaaS.")

    host = smtp.get("host") or smtp.get("smtp_host")
    port = int(smtp.get("port") or smtp.get("puerto") or 587)
    username = smtp.get("username") or smtp.get("correo") or ""
    password = smtp.get("password") or smtp.get("clave") or ""
    from_email = smtp.get("from_email") or username
    from_name = smtp.get("from_name") or smtp.get("nombre_remitente") or DEFAULT_FROM_NAME
    use_tls = bool(smtp.get("use_tls", True))
    use_ssl = bool(smtp.get("use_ssl", False))

    log = SMTPLog(
        destinatario=destinatario,
        asunto=asunto,
        plantilla=plantilla,
        modulo_origen="smtp_inteligente",
        estado="ENVIANDO",
        enviado=False,
        intentos=1,
        metadata_json=metadata or {},
    )
    db.add(log)
    db.commit()
    db.refresh(log)

    msg = MIMEMultipart("alternative")
    msg["Subject"] = asunto
    msg["From"] = f"{from_name} <{from_email}>"
    msg["To"] = destinatario

    html_body = html or render_template_base(asunto, mensaje, "SGA SaaS PRO")
    msg.attach(MIMEText(mensaje, "plain", "utf-8"))
    msg.attach(MIMEText(html_body, "html", "utf-8"))

    try:
        if use_ssl:
            server = smtplib.SMTP_SSL(host, port, timeout=25)
        else:
            server = smtplib.SMTP(host, port, timeout=25)

        try:
            server.ehlo()
            if use_tls and not use_ssl:
                server.starttls()
                server.ehlo()
            if username and password:
                server.login(username, password)
            server.sendmail(from_email, [destinatario], msg.as_string())
        finally:
            server.quit()

        log.estado = "ENVIADO"
        log.enviado = True
        log.enviado_en = datetime.now(timezone.utc)
        log.mensaje_error = None
        db.commit()
        db.refresh(log)
        return log

    except Exception as exc:
        log.estado = "ERROR"
        log.enviado = False
        log.mensaje_error = str(exc)
        db.commit()
        db.refresh(log)
        raise HTTPException(status_code=500, detail=f"No se pudo enviar el correo: {exc}")


def crear_plantillas_disponibles() -> Dict[str, str]:
    return {
        "manual": "Correo manual desde panel SMTP",
        "prueba": "Prueba de configuración SMTP",
        "mantenimiento_asignado": "Aviso de mantenimiento asignado",
        "mantenimiento_vencido": "Alerta de mantenimiento vencido",
        "evidencia_cargada": "Aviso de evidencia cargada",
        "backup_generado": "Aviso de backup generado",
    }
