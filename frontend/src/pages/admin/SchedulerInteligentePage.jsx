// ============================================================
// SCHEDULER INTELIGENTE PRO
// Archivo: frontend/src/pages/admin/SchedulerInteligentePage.jsx
// Fase 34.2.7
// ============================================================

import { useEffect, useMemo, useState } from "react";
import {
  Activity,
  CalendarClock,
  CheckCircle2,
  Clock,
  Plus,
  RefreshCw,
  Send,
  Trash2,
  XCircle,
} from "lucide-react";

import AdminLayout from "./AdminLayout";
import schedulerInteligenteApi from "../../api/schedulerInteligenteApi";
import "../../styles/scheduler-inteligente-pro.css";

const initialForm = {
  nombre: "",
  descripcion: "",
  equipo_id: "",
  tecnico_id: "",
  tipo_mantenimiento: "PREVENTIVO",
  frecuencia_dias: 30,
  fecha_inicio: "",
  prioridad: "MEDIA",
  estado_inicial: "PROGRAMADO",
  modo: "SEMIAUTOMATICO",
  activo: true,
  configuracion: {},
};

export default function SchedulerInteligentePage() {
  const [dashboard, setDashboard] = useState(null);
  const [reglas, setReglas] = useState([]);
  const [sugerencias, setSugerencias] = useState([]);
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [mensaje, setMensaje] = useState("");
  const [form, setForm] = useState(initialForm);
  const [showForm, setShowForm] = useState(false);

  const cargar = async () => {
    setLoading(true);
    try {
      await schedulerInteligenteApi.inicializar();
      const [dash, reglasRes, sugerenciasRes, logsRes] = await Promise.all([
        schedulerInteligenteApi.dashboard(),
        schedulerInteligenteApi.listarReglas(),
        schedulerInteligenteApi.listarSugerencias(""),
        schedulerInteligenteApi.logs(),
      ]);
      setDashboard(dash.data);
      setReglas(reglasRes.data || []);
      setSugerencias(sugerenciasRes.data || []);
      setLogs(logsRes.data || []);
    } catch (error) {
      console.error(error);
      setMensaje("No fue posible cargar Scheduler Inteligente.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const timer = window.setTimeout(() => cargar(), 0);
    return () => window.clearTimeout(timer);
  }, []);

  const stats = useMemo(() => {
    return {
      total: dashboard?.total_reglas || 0,
      activas: dashboard?.reglas_activas || 0,
      pendientes: dashboard?.sugerencias_pendientes || 0,
      generadas: dashboard?.sugerencias_generadas || 0,
    };
  }, [dashboard]);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setForm((prev) => ({ ...prev, [name]: type === "checkbox" ? checked : value }));
  };

  const crearRegla = async (e) => {
    e.preventDefault();
    setMensaje("");

    if (!form.nombre || !form.equipo_id || !form.fecha_inicio) {
      setMensaje("Completa nombre, equipo y fecha inicial.");
      return;
    }

    try {
      const payload = {
        ...form,
        equipo_id: Number(form.equipo_id),
        tecnico_id: form.tecnico_id ? Number(form.tecnico_id) : null,
        frecuencia_dias: Number(form.frecuencia_dias),
      };
      await schedulerInteligenteApi.crearRegla(payload);
      setForm(initialForm);
      setShowForm(false);
      await cargar();
      setMensaje("Regla creada correctamente.");
    } catch (error) {
      console.error(error);
      setMensaje("No fue posible crear la regla. Verifica IDs de equipo/técnico.");
    }
  };

  const ejecutar = async () => {
    setLoading(true);
    try {
      const res = await schedulerInteligenteApi.ejecutarAhora();
      setMensaje(res.data?.mensaje || "Revisión ejecutada.");
      await cargar();
    } catch (error) {
      console.error(error);
      setMensaje("No fue posible ejecutar la revisión.");
    } finally {
      setLoading(false);
    }
  };

  const toggleRegla = async (regla) => {
    await schedulerInteligenteApi.actualizarRegla(regla.id, { activo: !regla.activo });
    await cargar();
  };

  const eliminarRegla = async (id) => {
    if (!confirm("¿Eliminar esta regla?")) return;
    await schedulerInteligenteApi.eliminarRegla(id);
    await cargar();
  };

  const aprobar = async (id) => {
    await schedulerInteligenteApi.aprobarSugerencia(id);
    await cargar();
  };

  const rechazar = async (id) => {
    await schedulerInteligenteApi.rechazarSugerencia(id);
    await cargar();
  };

  return (
    <AdminLayout>
      <div className="scheduler-pro-page">
        <section className="scheduler-hero">
          <div>
            <span className="scheduler-badge">FASE 34.2.7</span>
            <h1>Scheduler Inteligente PRO</h1>
            <p>
              Motor automático para reglas de mantenimiento, sugerencias operativas,
              ejecución manual, modo semiautomático y generación automática.
            </p>
          </div>
          <div className="scheduler-actions">
            <button className="scheduler-btn secondary" onClick={cargar} disabled={loading}>
              <RefreshCw size={18} /> Actualizar
            </button>
            <button className="scheduler-btn primary" onClick={ejecutar} disabled={loading}>
              <Send size={18} /> Generar ahora
            </button>
            <button className="scheduler-btn dark" onClick={() => setShowForm((v) => !v)}>
              <Plus size={18} /> Nueva regla
            </button>
          </div>
        </section>

        {mensaje && <div className="scheduler-alert">{mensaje}</div>}

        <section className="scheduler-kpis">
          <div className="scheduler-kpi"><CalendarClock /><span>Reglas</span><strong>{stats.total}</strong></div>
          <div className="scheduler-kpi"><CheckCircle2 /><span>Activas</span><strong>{stats.activas}</strong></div>
          <div className="scheduler-kpi"><Clock /><span>Sugeridas</span><strong>{stats.pendientes}</strong></div>
          <div className="scheduler-kpi"><Activity /><span>Generadas</span><strong>{stats.generadas}</strong></div>
        </section>

        {showForm && (
          <form className="scheduler-form" onSubmit={crearRegla}>
            <h2>Nueva regla de mantenimiento</h2>
            <div className="scheduler-form-grid">
              <label>Nombre<input name="nombre" value={form.nombre} onChange={handleChange} placeholder="Preventivo aire acondicionado" /></label>
              <label>Equipo ID<input name="equipo_id" value={form.equipo_id} onChange={handleChange} placeholder="Ej: 1" /></label>
              <label>Técnico ID opcional<input name="tecnico_id" value={form.tecnico_id} onChange={handleChange} placeholder="Ej: 2" /></label>
              <label>Tipo<select name="tipo_mantenimiento" value={form.tipo_mantenimiento} onChange={handleChange}><option>PREVENTIVO</option><option>CORRECTIVO</option><option>INSPECCION</option><option>CALIBRACION</option></select></label>
              <label>Frecuencia días<input type="number" name="frecuencia_dias" value={form.frecuencia_dias} onChange={handleChange} /></label>
              <label>Fecha inicial<input type="date" name="fecha_inicio" value={form.fecha_inicio} onChange={handleChange} /></label>
              <label>Prioridad<select name="prioridad" value={form.prioridad} onChange={handleChange}><option>BAJA</option><option>MEDIA</option><option>ALTA</option><option>CRITICA</option></select></label>
              <label>Modo<select name="modo" value={form.modo} onChange={handleChange}><option value="MANUAL">MANUAL</option><option value="SEMIAUTOMATICO">SEMIAUTOMÁTICO</option><option value="AUTOMATICO">AUTOMÁTICO</option></select></label>
              <label className="scheduler-wide">Descripción<textarea name="descripcion" value={form.descripcion} onChange={handleChange} /></label>
            </div>
            <div className="scheduler-form-footer">
              <label className="scheduler-check"><input type="checkbox" name="activo" checked={form.activo} onChange={handleChange} /> Activa</label>
              <button className="scheduler-btn primary" type="submit">Guardar regla</button>
            </div>
          </form>
        )}

        <section className="scheduler-panel">
          <div className="scheduler-panel-head"><h2>Reglas configuradas</h2><span>{reglas.length} registros</span></div>
          <div className="scheduler-table-wrap">
            <table className="scheduler-table">
              <thead><tr><th>Regla</th><th>Equipo</th><th>Frecuencia</th><th>Modo</th><th>Próxima</th><th>Estado</th><th>Acciones</th></tr></thead>
              <tbody>
                {reglas.length === 0 && <tr><td colSpan="7" className="scheduler-empty">No hay reglas creadas.</td></tr>}
                {reglas.map((r) => (
                  <tr key={r.id}>
                    <td><strong>{r.nombre}</strong><small>{r.tipo_mantenimiento}</small></td>
                    <td>#{r.equipo_id}</td>
                    <td>{r.frecuencia_dias} días</td>
                    <td><span className={`scheduler-pill ${r.modo?.toLowerCase()}`}>{r.modo}</span></td>
                    <td>{r.proxima_fecha || "Sin fecha"}</td>
                    <td>{r.activo ? "Activa" : "Pausada"}</td>
                    <td className="scheduler-row-actions">
                      <button onClick={() => toggleRegla(r)}>{r.activo ? "Pausar" : "Activar"}</button>
                      <button className="danger" onClick={() => eliminarRegla(r.id)}><Trash2 size={14} /></button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

        <section className="scheduler-panel">
          <div className="scheduler-panel-head"><h2>Sugerencias pendientes</h2><span>{sugerencias.length} registros</span></div>
          <div className="scheduler-suggestions">
            {sugerencias.length === 0 && <div className="scheduler-empty-card">No hay sugerencias generadas.</div>}
            {sugerencias.map((s) => (
              <div className="scheduler-suggestion" key={s.id}>
                <div><strong>Equipo #{s.equipo_id}</strong><p>{s.tipo_mantenimiento} · {s.fecha_programada} · {s.prioridad}</p><small>{s.mensaje}</small></div>
                <div className="scheduler-row-actions">
                  {s.estado === "PENDIENTE" && <button onClick={() => aprobar(s.id)}><CheckCircle2 size={15} /> Aprobar</button>}
                  {s.estado === "PENDIENTE" && <button className="danger" onClick={() => rechazar(s.id)}><XCircle size={15} /> Rechazar</button>}
                  <span className="scheduler-pill">{s.estado}</span>
                </div>
              </div>
            ))}
          </div>
        </section>

        <section className="scheduler-panel">
          <div className="scheduler-panel-head"><h2>Logs Scheduler</h2><span>{logs.length} eventos</span></div>
          <div className="scheduler-log-list">
            {logs.length === 0 && <div className="scheduler-empty-card">Sin logs registrados.</div>}
            {logs.map((l) => (
              <div className="scheduler-log" key={l.id}>
                <span>{l.nivel}</span><strong>{l.evento}</strong><p>{l.mensaje}</p><small>{l.creado_en}</small>
              </div>
            ))}
          </div>
        </section>
      </div>
    </AdminLayout>
  );
}
