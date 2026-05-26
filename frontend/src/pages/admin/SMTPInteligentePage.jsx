// ============================================================
// PÁGINA: SMTP Inteligente SaaS PRO
// Archivo: frontend/src/pages/admin/SMTPInteligentePage.jsx
// FASE 34.2.3
// ============================================================

import { useEffect, useMemo, useState } from "react";
import {
  AlertCircle,
  CheckCircle2,
  Clock,
  Mail,
  RefreshCw,
  Send,
  Server,
  ShieldCheck,
} from "lucide-react";

import "../../styles/smtp-inteligente-saas-pro.css";

import {
  enviarCorreoManual,
  inicializarSMTP,
  listarLogsSMTP,
  obtenerEstadoSMTP,
  obtenerPlantillasSMTP,
  probarSMTP,
} from "../../api/smtpInteligenteApi";

export default function SMTPInteligentePage() {
  const [estado, setEstado] = useState(null);
  const [logs, setLogs] = useState([]);
  const [plantillas, setPlantillas] = useState({});
  const [loading, setLoading] = useState(false);
  const [mensaje, setMensaje] = useState("");
  const [error, setError] = useState("");

  const [testForm, setTestForm] = useState({
    destinatario: "",
    asunto: "Prueba SMTP SGA SaaS PRO",
    mensaje: "Correo de prueba enviado desde SGA SaaS PRO.",
  });

  const [manualForm, setManualForm] = useState({
    destinatario: "",
    asunto: "",
    mensaje: "",
    plantilla: "manual",
  });

  const stats = useMemo(() => {
    const total = logs.length;
    const enviados = logs.filter((item) => item.estado === "ENVIADO").length;
    const errores = logs.filter((item) => item.estado === "ERROR").length;
    const pendientes = logs.filter((item) => item.estado === "PENDIENTE" || item.estado === "ENVIANDO").length;
    return { total, enviados, errores, pendientes };
  }, [logs]);

  const cargarDatos = async () => {
    setLoading(true);
    setError("");
    setMensaje("");

    try {
      await inicializarSMTP();
      const [estadoData, plantillasData, logsData] = await Promise.all([
        obtenerEstadoSMTP(),
        obtenerPlantillasSMTP(),
        listarLogsSMTP(80),
      ]);
      setEstado(estadoData);
      setPlantillas(plantillasData || {});
      setLogs(Array.isArray(logsData) ? logsData : []);
    } catch (err) {
      setError(err?.response?.data?.detail || "No fue posible cargar SMTP Inteligente.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    cargarDatos();
  }, []);

  const handleTest = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    setMensaje("");

    try {
      await probarSMTP(testForm);
      setMensaje("Correo de prueba enviado correctamente.");
      await cargarDatos();
    } catch (err) {
      setError(err?.response?.data?.detail || "No se pudo enviar la prueba SMTP.");
    } finally {
      setLoading(false);
    }
  };

  const handleManual = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    setMensaje("");

    try {
      await enviarCorreoManual({ ...manualForm, metadata: { origen: "panel_smtp" } });
      setMensaje("Correo manual enviado correctamente.");
      setManualForm({ destinatario: "", asunto: "", mensaje: "", plantilla: "manual" });
      await cargarDatos();
    } catch (err) {
      setError(err?.response?.data?.detail || "No se pudo enviar el correo manual.");
    } finally {
      setLoading(false);
    }
  };

  const statusClass = estado?.configurado ? "ok" : "warn";

  return (
    <div className="smtp-pro-page">
      <section className="smtp-hero">
        <div>
          <p className="smtp-kicker">FASE 34.2.3 · SMTP</p>
          <h1>SMTP Inteligente SaaS</h1>
          <p>
            Centro profesional para correos corporativos, pruebas SMTP, plantillas HTML,
            logs y automatización de notificaciones.
          </p>
        </div>

        <button className="smtp-btn secondary" onClick={cargarDatos} disabled={loading}>
          <RefreshCw size={18} />
          Actualizar
        </button>
      </section>

      {error && (
        <div className="smtp-alert error">
          <AlertCircle size={18} />
          {error}
        </div>
      )}

      {mensaje && (
        <div className="smtp-alert success">
          <CheckCircle2 size={18} />
          {mensaje}
        </div>
      )}

      <section className="smtp-grid-cards">
        <article className="smtp-card">
          <Mail size={24} />
          <span>Estado SMTP</span>
          <strong className={statusClass}>{estado?.configurado ? "Configurado" : "Pendiente"}</strong>
        </article>

        <article className="smtp-card">
          <Server size={24} />
          <span>Servidor</span>
          <strong>{estado?.host || "Sin host"}</strong>
          <small>{estado?.port ? `Puerto ${estado.port}` : "Configura en Configuración Inteligente"}</small>
        </article>

        <article className="smtp-card">
          <ShieldCheck size={24} />
          <span>Automatización</span>
          <strong className={estado?.automatizacion_activa ? "ok" : "warn"}>
            {estado?.automatizacion_activa ? "Activa" : "Inactiva"}
          </strong>
        </article>

        <article className="smtp-card">
          <Clock size={24} />
          <span>Logs</span>
          <strong>{stats.total}</strong>
          <small>{stats.enviados} enviados · {stats.errores} errores</small>
        </article>
      </section>

      <section className="smtp-panels">
        <form className="smtp-panel" onSubmit={handleTest}>
          <div className="smtp-panel-head">
            <div>
              <h2>Prueba SMTP</h2>
              <p>Valida host, puerto, TLS/SSL, usuario y contraseña configurados.</p>
            </div>
            <Send size={22} />
          </div>

          <label>Destinatario</label>
          <input
            type="email"
            value={testForm.destinatario}
            onChange={(e) => setTestForm({ ...testForm, destinatario: e.target.value })}
            placeholder="correo@empresa.com"
            required
          />

          <label>Asunto</label>
          <input
            value={testForm.asunto}
            onChange={(e) => setTestForm({ ...testForm, asunto: e.target.value })}
            required
          />

          <label>Mensaje</label>
          <textarea
            value={testForm.mensaje}
            onChange={(e) => setTestForm({ ...testForm, mensaje: e.target.value })}
            rows={4}
            required
          />

          <button className="smtp-btn primary" type="submit" disabled={loading}>
            <Send size={18} />
            Enviar prueba
          </button>
        </form>

        <form className="smtp-panel" onSubmit={handleManual}>
          <div className="smtp-panel-head">
            <div>
              <h2>Correo manual</h2>
              <p>Envía mensajes operativos sin afectar módulos existentes.</p>
            </div>
            <Mail size={22} />
          </div>

          <label>Destinatario</label>
          <input
            type="email"
            value={manualForm.destinatario}
            onChange={(e) => setManualForm({ ...manualForm, destinatario: e.target.value })}
            placeholder="cliente@empresa.com"
            required
          />

          <label>Plantilla</label>
          <select
            value={manualForm.plantilla}
            onChange={(e) => setManualForm({ ...manualForm, plantilla: e.target.value })}
          >
            {Object.entries(plantillas).map(([key, label]) => (
              <option key={key} value={key}>{label}</option>
            ))}
          </select>

          <label>Asunto</label>
          <input
            value={manualForm.asunto}
            onChange={(e) => setManualForm({ ...manualForm, asunto: e.target.value })}
            required
          />

          <label>Mensaje</label>
          <textarea
            value={manualForm.mensaje}
            onChange={(e) => setManualForm({ ...manualForm, mensaje: e.target.value })}
            rows={4}
            required
          />

          <button className="smtp-btn primary" type="submit" disabled={loading}>
            <Send size={18} />
            Enviar correo
          </button>
        </form>
      </section>

      <section className="smtp-history">
        <div className="smtp-panel-head">
          <div>
            <h2>Historial SMTP</h2>
            <p>Últimos correos enviados desde el motor SMTP inteligente.</p>
          </div>
        </div>

        <div className="smtp-table-wrap">
          <table>
            <thead>
              <tr>
                <th>Fecha</th>
                <th>Destinatario</th>
                <th>Asunto</th>
                <th>Plantilla</th>
                <th>Estado</th>
                <th>Error</th>
              </tr>
            </thead>
            <tbody>
              {logs.length === 0 ? (
                <tr>
                  <td colSpan="6" className="smtp-empty">No hay correos registrados.</td>
                </tr>
              ) : (
                logs.map((log) => (
                  <tr key={log.id}>
                    <td>{log.creado_en ? new Date(log.creado_en).toLocaleString() : "-"}</td>
                    <td>{log.destinatario}</td>
                    <td>{log.asunto}</td>
                    <td>{log.plantilla || "-"}</td>
                    <td><span className={`smtp-badge ${String(log.estado).toLowerCase()}`}>{log.estado}</span></td>
                    <td>{log.mensaje_error || "-"}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}
