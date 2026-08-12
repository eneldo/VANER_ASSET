// ============================================================
// PÁGINA: Automatización SaaS PRO
// Archivo: frontend/src/pages/admin/AutomatizacionPage.jsx
// Fase 34.2.1
// ============================================================

import { useEffect, useMemo, useState } from "react";
import {
  Activity,
  Bell,
  Bot,
  Clock3,
  DatabaseBackup,
  HardDrive,
  Mail,
  MessageCircle,
  PlayCircle,
  RefreshCw,
  ServerCog,
  ShieldCheck,
  TimerReset,
  Wrench,
} from "lucide-react";

import automatizacionApi from "../../api/automatizacionApi";
import AdminLayout from "./AdminLayout";
import "../../styles/automatizacion-saas-pro.css";

const ICONOS = {
  backups: DatabaseBackup,
  smtp: Mail,
  whatsapp: MessageCircle,
  monitor: Activity,
  mantenimientos: Wrench,
  limpieza_logs: TimerReset,
  devops: ServerCog,
};

const etiquetasEstado = {
  OK: "ok",
  ACTIVO: "ok",
  INACTIVO: "off",
  ERROR: "error",
};

export default function AutomatizacionPage() {
  const [items, setItems] = useState([]);
  const [scheduler, setScheduler] = useState(null);
  const [monitor, setMonitor] = useState(null);
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  const cargar = async () => {
    setLoading(true);
    setError("");
    try {
      await automatizacionApi.inicializar();
      const [lista, status, mon, historial] = await Promise.all([
        automatizacionApi.listar(),
        automatizacionApi.schedulerStatus(),
        automatizacionApi.monitor(),
        automatizacionApi.logs(80),
      ]);
      setItems(lista || []);
      setScheduler(status);
      setMonitor(mon);
      setLogs(historial || []);
    } catch (err) {
      console.error(err);
      setError("No fue posible cargar Automatización SaaS. Verifica backend, router /automatizacion y dependencias apscheduler/psutil.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const timer = window.setTimeout(() => cargar(), 0);
    return () => window.clearTimeout(timer);
  }, []);

  const resumen = useMemo(() => {
    const activos = items.filter((i) => i.activo).length;
    const errores = items.filter((i) => String(i.estado).toUpperCase() === "ERROR").length;
    return { total: items.length, activos, inactivos: items.length - activos, errores };
  }, [items]);

  const toggle = async (modulo) => {
    setSaving(true);
    try {
      await automatizacionApi.toggle(modulo);
      await cargar();
    } catch (err) {
      console.error(err);
      setError("No fue posible actualizar el switch de automatización.");
    } finally {
      setSaving(false);
    }
  };

  const cambiarFrecuencia = async (item, frecuencia) => {
    const valor = Number(frecuencia);
    if (!Number.isFinite(valor) || valor < 1) return;
    setSaving(true);
    try {
      await automatizacionApi.actualizar(item.modulo, { frecuencia_minutos: valor });
      await cargar();
    } catch (err) {
      console.error(err);
      setError("No fue posible actualizar la frecuencia.");
    } finally {
      setSaving(false);
    }
  };

  const reiniciarScheduler = async () => {
    setSaving(true);
    try {
      await automatizacionApi.reiniciarScheduler();
      await cargar();
    } catch (err) {
      console.error(err);
      setError("No fue posible reiniciar/sincronizar el scheduler.");
    } finally {
      setSaving(false);
    }
  };

  return (
    <AdminLayout contentClassName="admin-content-pro--flush">
      <div className="auto-saas-page">
      <section className="auto-hero">
        <div>
          <span className="auto-eyebrow">FASE 34.2.1 · SGA SaaS PRO</span>
          <h1>Automatización Inteligente SaaS</h1>
          <p>
            Núcleo seguro para backups, correos, WhatsApp, monitor, logs, tareas recurrentes,
            mantenimiento automatizado y DevOps SaaS sin afectar módulos actuales.
          </p>
        </div>

        <div className="auto-hero-actions">
          <button className="auto-btn ghost" onClick={cargar} disabled={loading || saving}>
            <RefreshCw size={17} /> Actualizar
          </button>
          <button className="auto-btn primary" onClick={reiniciarScheduler} disabled={loading || saving}>
            <PlayCircle size={17} /> Sincronizar jobs
          </button>
        </div>
      </section>

      {error && <div className="auto-alert error"><Bell size={18} /> {error}</div>}

      <section className="auto-kpis">
        <article className="auto-kpi">
          <Bot size={24} />
          <div><span>Total módulos</span><strong>{resumen.total}</strong></div>
        </article>
        <article className="auto-kpi ok">
          <ShieldCheck size={24} />
          <div><span>Activos</span><strong>{resumen.activos}</strong></div>
        </article>
        <article className="auto-kpi off">
          <Clock3 size={24} />
          <div><span>Inactivos</span><strong>{resumen.inactivos}</strong></div>
        </article>
        <article className="auto-kpi error">
          <Bell size={24} />
          <div><span>Errores</span><strong>{resumen.errores}</strong></div>
        </article>
      </section>

      <section className="auto-grid-main">
        <div className="auto-panel modules">
          <div className="auto-panel-head">
            <div>
              <h2>Módulos automatizables</h2>
              <p>Activa solo lo que deseas usar. Las funciones reales se ampliarán por subfase.</p>
            </div>
          </div>

          {loading ? (
            <div className="auto-empty">Cargando automatizaciones...</div>
          ) : (
            <div className="auto-modules-list">
              {items.map((item) => {
                const Icon = ICONOS[item.modulo] || Bot;
                const estadoClass = etiquetasEstado[String(item.estado || "").toUpperCase()] || "off";
                return (
                  <article className="auto-module-card" key={item.id || item.modulo}>
                    <div className="auto-module-icon"><Icon size={22} /></div>
                    <div className="auto-module-body">
                      <div className="auto-module-title-row">
                        <h3>{item.nombre}</h3>
                        <span className={`auto-state ${estadoClass}`}>{item.estado}</span>
                      </div>
                      <p>{item.descripcion}</p>

                      <div className="auto-module-controls">
                        <label className="auto-switch">
                          <input
                            type="checkbox"
                            checked={Boolean(item.activo)}
                            onChange={() => toggle(item.modulo)}
                            disabled={saving}
                          />
                          <span />
                          <b>{item.activo ? "Habilitado" : "Deshabilitado"}</b>
                        </label>

                        <label className="auto-frequency">
                          Frecuencia
                          <select
                            value={item.frecuencia_minutos}
                            onChange={(e) => cambiarFrecuencia(item, e.target.value)}
                            disabled={saving}
                          >
                            <option value={5}>5 min</option>
                            <option value={10}>10 min</option>
                            <option value={30}>30 min</option>
                            <option value={60}>1 hora</option>
                            <option value={360}>6 horas</option>
                            <option value={720}>12 horas</option>
                            <option value={1440}>Diario</option>
                          </select>
                        </label>
                      </div>

                      <div className="auto-module-meta">
                        <span>Última: {item.ultima_ejecucion ? new Date(item.ultima_ejecucion).toLocaleString() : "Sin ejecutar"}</span>
                        <span>Próxima: {item.proxima_ejecucion ? new Date(item.proxima_ejecucion).toLocaleString() : "No programada"}</span>
                      </div>
                    </div>
                  </article>
                );
              })}
            </div>
          )}
        </div>

        <aside className="auto-side">
          <div className="auto-panel compact">
            <h2>Scheduler</h2>
            <div className={`auto-big-status ${scheduler?.activo ? "ok" : "off"}`}>
              {scheduler?.estado || "CONSULTANDO"}
            </div>
            <p>{scheduler?.jobs?.length || 0} jobs cargados</p>
            <ul className="auto-jobs">
              {(scheduler?.jobs || []).map((job) => (
                <li key={job.id}>
                  <strong>{job.nombre}</strong>
                  <span>{job.proxima_ejecucion || "Sin próxima ejecución"}</span>
                </li>
              ))}
            </ul>
          </div>

          <div className="auto-panel compact">
            <h2>Monitor Sistema</h2>
            <div className="auto-meter"><span>CPU</span><b>{monitor?.cpu_percent ?? 0}%</b></div>
            <div className="auto-meter"><span>RAM</span><b>{monitor?.ram_percent ?? 0}%</b></div>
            <div className="auto-meter"><span>Disco</span><b>{monitor?.disco_percent ?? 0}%</b></div>
            <div className="auto-disk"><HardDrive size={18} /> {monitor?.disco_usado_gb ?? 0} GB / {monitor?.disco_total_gb ?? 0} GB</div>
          </div>
        </aside>
      </section>

      <section className="auto-panel logs">
        <div className="auto-panel-head">
          <div>
            <h2>Logs inteligentes</h2>
            <p>Historial de eventos del núcleo de automatización.</p>
          </div>
        </div>

        <div className="auto-table-wrap">
          <table className="auto-table">
            <thead>
              <tr>
                <th>Fecha</th>
                <th>Módulo</th>
                <th>Nivel</th>
                <th>Evento</th>
                <th>Mensaje</th>
                <th>Duración</th>
              </tr>
            </thead>
            <tbody>
              {logs.length === 0 ? (
                <tr><td colSpan="6" className="auto-empty-row">Sin logs todavía.</td></tr>
              ) : logs.map((log) => (
                <tr key={log.id}>
                  <td>{log.creado_en ? new Date(log.creado_en).toLocaleString() : "—"}</td>
                  <td>{log.modulo}</td>
                  <td><span className={`auto-level ${String(log.nivel).toLowerCase()}`}>{log.nivel}</span></td>
                  <td>{log.evento}</td>
                  <td>{log.mensaje}</td>
                  <td>{log.duracion_ms ?? 0} ms</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        </section>
      </div>
    </AdminLayout>
  );
}
