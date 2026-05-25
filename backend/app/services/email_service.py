# ============================================================
# SERVICIO: Envío de correos SMTP
# Archivo: backend/app/services/email_service.py
# Fase 34.1 - Configuración Inteligente SaaS PRO
# ============================================================

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict


def send_test_email(smtp_config: Dict, to_email: str, subject: str, message: str) -> None:
    """
    Envía un correo de prueba usando los parámetros SMTP guardados en PostgreSQL.
    Lanza excepción si la conexión o autenticación falla para devolver error claro al frontend.
    """

    host = smtp_config.get("host", "")
    port = int(smtp_config.get("port", 587) or 587)
    username = smtp_config.get("username", "")
    password = smtp_config.get("password", "")
    from_email = smtp_config.get("from_email") or username
    from_name = smtp_config.get("from_name", "SGA SaaS PRO")
    use_tls = bool(smtp_config.get("use_tls", True))
    use_ssl = bool(smtp_config.get("use_ssl", False))

    if not host or not from_email:
        raise ValueError("Configura host SMTP y correo remitente antes de probar el envío.")

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"{from_name} <{from_email}>"
    msg["To"] = to_email

    html = f"""
    <html>
      <body style="font-family: Arial, sans-serif; background:#f8fafc; padding:24px;">
        <div style="max-width:640px;margin:auto;background:white;border-radius:16px;padding:24px;border:1px solid #e5e7eb;">
          <h2 style="color:#2563eb;margin-top:0;">SGA SaaS PRO</h2>
          <p>{message}</p>
          <p style="color:#64748b;font-size:13px;">Este mensaje confirma que la configuración SMTP corporativa está funcionando.</p>
        </div>
      </body>
    </html>
    """

    msg.attach(MIMEText(message, "plain", "utf-8"))
    msg.attach(MIMEText(html, "html", "utf-8"))

    if use_ssl:
        server = smtplib.SMTP_SSL(host, port, timeout=20)
    else:
        server = smtplib.SMTP(host, port, timeout=20)

    try:
        server.ehlo()
        if use_tls and not use_ssl:
            server.starttls()
            server.ehlo()
        if username and password:
            server.login(username, password)
        server.sendmail(from_email, [to_email], msg.as_string())
    finally:
        server.quit()
