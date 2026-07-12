import { useCallback, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  BarChart3, CheckCircle, Clock, Gauge, MapPin, MonitorCog, RefreshCcw,
} from "lucide-react";
import {
  Bar, BarChart, CartesianGrid, Cell, Legend, Pie, PieChart,
  ResponsiveContainer, Tooltip, XAxis, YAxis,
} from "recharts";

import API from "../../api/axios";
import { getEmpresaId } from "../../utils/multiempresa";

const COLORS = {
  PENDIENTE: "#f59e0b",
  EN_PROCESO: "#0284c7",
  COMPLETADO: "#16a34a",
  RETRASADO: "#dc2626",
};

export default function ClienteDashboard() {
  const navigate = useNavigate();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const cargar = useCallback(async (silencioso = false) => {
    const empresaId = getEmpresaId();
    if (!empresaId) {
      setError("Este usuario no tiene empresa asociada.");
      setLoading(false);
      return;
    }
    if (!silencioso) setLoading(true);
    try {
      const res = await API.get(`/cliente/${empresaId}/dashboard`);
      setData(res.data);
      setError("");
    } catch (requestError) {
      console.error(requestError);
      setError("No fue posible actualizar el dashboard.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    const inicial = window.setTimeout(() => cargar(), 0);
    const interval = window.setInterval(() => cargar(true), 60000);
    return () => {
      window.clearTimeout(inicial);
      window.clearInterval(interval);
    };
  }, [cargar]);

  const distribucion = data?.distribucion_estados || [];
  const barras = data?.mantenimientos_por_sede || [];
  const actividad = data?.actividad_hoy || [];

  return (
    <>
      <div className="cliente-header cliente-header-flex">
        <div>
          <h1>Dashboard ejecutivo</h1>
          <p>Estado operativo en tiempo real de tu empresa y sus sedes.</p>
        </div>
        <button className="cliente-btn-secondary" onClick={() => cargar()} disabled={loading}>
          <RefreshCcw size={16} className={loading ? "spin" : ""} /> Actualizar
        </button>
      </div>

      {error && <div className="cliente-dashboard-error">{error}</div>}

      <section className="cliente-kpi-grid">
        <Kpi title="Total de equipos" value={data?.total_equipos || 0} icon={<MonitorCog />} onClick={() => navigate("/cliente/equipos")} />
        <Kpi title="OTs ejecutadas este mes" value={data?.ots_ejecutadas_mes || 0} icon={<CheckCircle />} onClick={() => navigate("/cliente/mantenimientos?estado=REALIZADOS")} />
        <Kpi title="OTs pendientes" value={data?.mantenimientos_pendientes || 0} icon={<Clock />} onClick={() => navigate("/cliente/mantenimientos?estado=PENDIENTES")} />
        <Kpi title="Cumplimiento preventivo" value={`${data?.cumplimiento_preventivo ?? 0}%`} icon={<Gauge />} accent="success" />
      </section>

      <section className="cliente-dashboard-charts">
        <article className="cliente-panel cliente-chart-card">
          <header><div><h2>Estado de mantenimientos</h2><p>Distribución operativa actual</p></div><BarChart3 size={20} /></header>
          <div className="cliente-chart-area">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={distribucion} dataKey="cantidad" nameKey="estado" innerRadius={62} outerRadius={92} paddingAngle={3}>
                  {distribucion.map((item) => <Cell key={item.estado} fill={COLORS[item.estado] || "#64748b"} />)}
                </Pie>
                <Tooltip formatter={(value, name) => [value, etiquetaEstado(name)]} />
                <Legend formatter={etiquetaEstado} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </article>

        <article className="cliente-panel cliente-chart-card">
          <header><div><h2>Preventivos vs. correctivos</h2><p>Cantidad de OTs por sede</p></div><MapPin size={20} /></header>
          <div className="cliente-chart-area">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={barras} margin={{ top: 12, right: 10, left: -18, bottom: 8 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} />
                <XAxis dataKey="sede" tick={{ fontSize: 11 }} />
                <YAxis allowDecimals={false} />
                <Tooltip />
                <Legend />
                <Bar dataKey="preventivos" name="Preventivos" fill="#2563eb" radius={[6, 6, 0, 0]} />
                <Bar dataKey="correctivos" name="Correctivos" fill="#f97316" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </article>
      </section>

      <section className="cliente-panel cliente-today-panel">
        <header><div><h2>Mantenimientos ejecutándose hoy</h2><p>Actividad en curso en tus sedes</p></div><span className="cliente-live-dot">EN VIVO</span></header>
        <div className="cliente-timeline">
          {actividad.length === 0 && <div className="cliente-empty-live">No hay mantenimientos en ejecución en este momento.</div>}
          {actividad.map((item) => (
            <article key={item.id}>
              <span className="cliente-timeline-dot" />
              <div>
                <strong>{item.equipo}</strong>
                <p><MapPin size={14} /> {item.sede}{item.direccion ? ` · ${item.direccion}` : ""}</p>
                <small>{item.tipo} · iniciado {formatearHora(item.fecha_inicio)}</small>
              </div>
              {item.latitud && item.longitud && (
                <a href={`https://www.openstreetmap.org/?mlat=${item.latitud}&mlon=${item.longitud}#map=17/${item.latitud}/${item.longitud}`} target="_blank" rel="noreferrer">Ver ubicación</a>
              )}
            </article>
          ))}
        </div>
        <footer>Actualizado: {data?.actualizado_en ? new Date(data.actualizado_en).toLocaleString() : "—"}</footer>
      </section>
    </>
  );
}

function Kpi({ title, value, icon, onClick, accent = "" }) {
  return (
    <button className={`cliente-kpi ${accent}`} onClick={onClick} disabled={!onClick}>
      <span>{icon}</span><div><small>{title}</small><strong>{value}</strong></div>
    </button>
  );
}

function etiquetaEstado(value) {
  return String(value || "").replaceAll("_", " ").toLowerCase().replace(/^./, (c) => c.toUpperCase());
}

function formatearHora(value) {
  if (!value) return "sin hora registrada";
  return new Date(value).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}
