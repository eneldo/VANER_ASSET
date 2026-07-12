// ============================================================
// PÁGINA: Logs Inteligentes SaaS PRO
// Archivo: frontend/src/pages/admin/LogsInteligentesPage.jsx
// FASE 34.2.5
// ============================================================

import { useEffect, useMemo, useState } from "react";
import {
  Activity,
  AlertTriangle,
  Bug,
  Download,
  Eraser,
  FileText,
  RefreshCw,
  Search,
  ShieldCheck,
} from "lucide-react";

import AdminLayout from "./AdminLayout";
import {
  crearLogDemo,
  getLogs,
  getLogsExportUrl,
  getLogsResumen,
  limpiarLogs,
} from "../../api/logsInteligentesApi";
import "../../styles/logs-inteligentes-pro.css";

const niveles = ["", "INFO", "WARNING", "ERROR", "CRITICAL", "DEBUG"];

function formatDate(value) {
  if (!value) return "Sin fecha";
  try {
    return new Date(value).toLocaleString("es-CO");
  } catch {
    return value;
  }
}

export default function LogsInteligentesPage() {
  const [resumen, setResumen] = useState({ total: 0, info: 0, warning: 0, error: 0, critical: 0, modulos: [] });
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [mensaje, setMensaje] = useState("");
  const [filtros, setFiltros] = useState({ modulo: "", nivel: "", texto: "", limite: 100 });

  const exportUrl = useMemo(() => getLogsExportUrl(filtros), [filtros]);

  async function cargar() {
    setLoading(true);
    setMensaje("");
    try {
      const [r, l] = await Promise.all([getLogsResumen(), getLogs(filtros)]);
      setResumen(r || {});
      setLogs(Array.isArray(l) ? l : []);
    } catch (error) {
      console.error(error);
      setMensaje("No fue posible cargar los logs inteligentes.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    const timer = window.setTimeout(() => cargar(), 0);
    return () => window.clearTimeout(timer);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function handleDemo() {
    setLoading(true);
    try {
      await crearLogDemo();
      await cargar();
    } catch (error) {
      console.error(error);
      setMensaje("No fue posible crear logs de prueba.");
    } finally {
      setLoading(false);
    }
  }

  async function handleLimpiar() {
    const confirmar = window.confirm("¿Deseas eliminar logs antiguos mayores a 30 días?");
    if (!confirmar) return;
    setLoading(true);
    try {
      await limpiarLogs(30);
      await cargar();
    } catch (error) {
      console.error(error);
      setMensaje("No fue posible limpiar logs antiguos.");
    } finally {
      setLoading(false);
    }
  }

  const cards = [
    { label: "Total logs", value: resumen.total || 0, icon: FileText },
    { label: "Info", value: resumen.info || 0, icon: ShieldCheck },
    { label: "Warnings", value: resumen.warning || 0, icon: AlertTriangle },
    { label: "Errores", value: (resumen.error || 0) + (resumen.critical || 0), icon: Bug },
  ];

  return (
    <AdminLayout>
      <div className="logs-page">
        <section className="logs-hero">
          <div>
            <span className="logs-badge">FASE 34.2.5</span>
            <h1>Logs Inteligentes SaaS PRO</h1>
            <p>
              Centro de trazabilidad para eventos del sistema, automatizaciones,
              errores, auditoría técnica y monitoreo operativo.
            </p>
          </div>

          <div className="logs-actions">
            <button className="logs-btn ghost" onClick={cargar} disabled={loading}>
              <RefreshCw size={17} /> Actualizar
            </button>
            <a className="logs-btn ghost" href={exportUrl} target="_blank" rel="noreferrer">
              <Download size={17} /> Exportar CSV
            </a>
            <button className="logs-btn danger" onClick={handleLimpiar} disabled={loading}>
              <Eraser size={17} /> Limpiar antiguos
            </button>
          </div>
        </section>

        {mensaje && <div className="logs-alert">{mensaje}</div>}

        <section className="logs-kpis">
          {cards.map((item) => {
            const Icon = item.icon;
            return (
              <article className="logs-kpi" key={item.label}>
                <div className="logs-kpi-icon"><Icon size={22} /></div>
                <div>
                  <span>{item.label}</span>
                  <strong>{item.value}</strong>
                </div>
              </article>
            );
          })}
        </section>

        <section className="logs-filters">
          <div className="logs-search">
            <Search size={18} />
            <input
              value={filtros.texto}
              onChange={(e) => setFiltros({ ...filtros, texto: e.target.value })}
              placeholder="Buscar por evento, mensaje, ruta o usuario..."
            />
          </div>

          <select value={filtros.modulo} onChange={(e) => setFiltros({ ...filtros, modulo: e.target.value })}>
            <option value="">Todos los módulos</option>
            {(resumen.modulos || []).map((modulo) => (
              <option key={modulo} value={modulo}>{modulo}</option>
            ))}
          </select>

          <select value={filtros.nivel} onChange={(e) => setFiltros({ ...filtros, nivel: e.target.value })}>
            {niveles.map((nivel) => (
              <option key={nivel || "todos"} value={nivel}>{nivel || "Todos los niveles"}</option>
            ))}
          </select>

          <button className="logs-btn primary" onClick={cargar} disabled={loading}>
            <Activity size={17} /> Filtrar
          </button>

          <button className="logs-btn ghost" onClick={handleDemo} disabled={loading}>
            Crear logs demo
          </button>
        </section>

        <section className="logs-table-card">
          <div className="logs-table-head">
            <h2>Historial de eventos</h2>
            <span>{loading ? "Cargando..." : `${logs.length} registros`}</span>
          </div>

          <div className="logs-table-wrap">
            <table className="logs-table">
              <thead>
                <tr>
                  <th>Fecha</th>
                  <th>Nivel</th>
                  <th>Módulo</th>
                  <th>Evento</th>
                  <th>Mensaje</th>
                  <th>Ruta</th>
                </tr>
              </thead>
              <tbody>
                {logs.length === 0 ? (
                  <tr>
                    <td colSpan="6" className="logs-empty">No hay logs registrados.</td>
                  </tr>
                ) : (
                  logs.map((log) => (
                    <tr key={log.id}>
                      <td>{formatDate(log.creado_en)}</td>
                      <td><span className={`logs-level ${String(log.nivel).toLowerCase()}`}>{log.nivel}</span></td>
                      <td>{log.modulo}</td>
                      <td>{log.evento}</td>
                      <td>{log.mensaje || "—"}</td>
                      <td>{log.ruta || "—"}</td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </section>
      </div>
    </AdminLayout>
  );
}
