/*
===========================================================
DASHBOARD COORDINADOR PRO
Archivo: frontend/src/pages/coordinador/CoordinadorDashboard.jsx
===========================================================
*/

import { useCallback, useEffect, useMemo, useState } from "react";
import API from "../../api/axios";
import { useNavigate } from "react-router-dom";
import {
  ClipboardList,
  Clock,
  UserCheck,
  PlayCircle,
  CheckCircle2,
  XCircle,
  Wrench,
  Users,
  RefreshCw,
  PackageSearch,
  AlertTriangle,
} from "lucide-react";
import "../../styles/coordinador.css";

const estadoClass = (estado) => `coord-badge ${String(estado || "sin").toLowerCase()}`;

const fmtFecha = (fecha) => {
  if (!fecha) return "Sin fecha";
  try {
    return new Date(fecha).toLocaleDateString("es-CO", {
      year: "numeric",
      month: "short",
      day: "2-digit",
    });
  } catch {
    return "Sin fecha";
  }
};

export default function CoordinadorDashboard() {
  const navigate = useNavigate();

  const [mantenimientos, setMantenimientos] = useState([]);
  const [dashboard, setDashboard] = useState(null);
  const [catalogos, setCatalogos] = useState({ equipos: [], tecnicos: [] });
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState("");
  const [ultimaActualizacion, setUltimaActualizacion] = useState(null);
  const [actualizacionAutomaticaOk, setActualizacionAutomaticaOk] = useState(true);

  const cargarDashboard = useCallback(async ({ silencioso = false } = {}) => {
    try {
      if (!silencioso) setCargando(true);

      const [resDashboard, resMantenimientos, resCatalogos] = await Promise.all([
        API.get("/coordinador/dashboard"),
        API.get("/coordinador/mantenimientos"),
        API.get("/coordinador/catalogos"),
      ]);

      setDashboard(resDashboard.data || null);
      setMantenimientos(resMantenimientos.data || []);
      setCatalogos(resCatalogos.data || { equipos: [], tecnicos: [] });
      setUltimaActualizacion(new Date());
      setActualizacionAutomaticaOk(true);
      setError("");
    } catch (err) {
      console.error("Error dashboard coordinador:", err);
      setActualizacionAutomaticaOk(false);
      setError("No se pudo cargar el dashboard del coordinador.");
    } finally {
      if (!silencioso) setCargando(false);
    }
  }, []);

  useEffect(() => {
    const cargaInicial = window.setTimeout(() => cargarDashboard(), 0);
    const intervalo = window.setInterval(() => {
      if (document.visibilityState === "visible") {
        cargarDashboard({ silencioso: true });
      }
    }, 15000);

    return () => {
      window.clearTimeout(cargaInicial);
      window.clearInterval(intervalo);
    };
  }, [cargarDashboard]);

  const metricas = useMemo(() => {
    const m = dashboard?.metricas || {};
    return {
      total: m.total_mantenimientos ?? mantenimientos.length,
      programados: m.programados ?? mantenimientos.filter((x) => x.estado === "PROGRAMADO").length,
      asignados: m.asignados ?? mantenimientos.filter((x) => x.estado === "ASIGNADO").length,
      enProceso: m.en_proceso ?? mantenimientos.filter((x) => x.estado === "EN_PROCESO").length,
      finalizados: m.finalizados ?? mantenimientos.filter((x) => x.estado === "FINALIZADO").length,
      anulados: m.anulados ?? mantenimientos.filter((x) => x.estado === "ANULADO").length,
      equipos: m.equipos ?? catalogos.equipos.length,
      tecnicos: m.tecnicos ?? catalogos.tecnicos.length,
    };
  }, [dashboard, mantenimientos, catalogos]);

  const recientes = useMemo(() => mantenimientos.slice(0, 8), [mantenimientos]);

  const kpis = [
    { label: "Total mantenimientos", value: metricas.total, icon: ClipboardList, to: "/coordinador/mantenimientos", tone: "blue" },
    { label: "Programados", value: metricas.programados, icon: Clock, to: "/coordinador/mantenimientos?estado=PROGRAMADO", tone: "amber" },
    { label: "Asignados", value: metricas.asignados, icon: UserCheck, to: "/coordinador/mantenimientos?estado=ASIGNADO", tone: "cyan" },
    { label: "En proceso", value: metricas.enProceso, icon: PlayCircle, to: "/coordinador/mantenimientos?estado=EN_PROCESO", tone: "indigo" },
    { label: "Finalizados", value: metricas.finalizados, icon: CheckCircle2, to: "/coordinador/mantenimientos?estado=FINALIZADO", tone: "green" },
    { label: "Anulados", value: metricas.anulados, icon: XCircle, to: "/coordinador/mantenimientos?estado=ANULADO", tone: "red" },
    { label: "Equipos", value: metricas.equipos, icon: PackageSearch, to: "/coordinador/equipos", tone: "violet" },
    { label: "Técnicos", value: metricas.tecnicos, icon: Users, to: "/coordinador/mantenimientos", tone: "slate" },
  ];

  return (
    <div className="coord-page">
      <div className="coord-hero">
        <div>
          <span className="coord-eyebrow">SGAHolding · PANEL OPERATIVO</span>
          <h2>Dashboard Coordinador</h2>
          <p>Control centralizado de mantenimientos, técnicos, estados, inventario y operación diaria.</p>
        </div>

        <div className="coord-live-controls">
          <span
            className={`coord-live-status ${actualizacionAutomaticaOk ? "online" : "offline"}`}
            role="status"
          >
            <i aria-hidden="true" />
            {actualizacionAutomaticaOk ? "Actualización automática cada 15 s" : "Conexión interrumpida"}
            {ultimaActualizacion && ` · ${ultimaActualizacion.toLocaleTimeString("es-CO", { hour: "2-digit", minute: "2-digit", second: "2-digit" })}`}
          </span>
          <button className="coord-btn secondary" onClick={() => cargarDashboard()} disabled={cargando}>
            <RefreshCw size={17} className={cargando ? "coord-spin" : ""} />
            Actualizar
          </button>
        </div>
      </div>

      {error && (
        <div className="coord-alert error">
          <AlertTriangle size={18} />
          {error}
        </div>
      )}

      <div className="coord-kpi-grid">
        {kpis.map((kpi) => {
          const Icon = kpi.icon;
          return (
            <button
              key={kpi.label}
              className={`coord-kpi ${kpi.tone}`}
              onClick={() => navigate(kpi.to)}
            >
              <div className="coord-kpi-icon">
                <Icon size={22} />
              </div>
              <div>
                <strong>{cargando ? "..." : kpi.value}</strong>
                <span>{kpi.label}</span>
              </div>
            </button>
          );
        })}
      </div>

      <div className="coord-grid two">
        <section className="coord-card">
          <div className="coord-card-header">
            <div>
              <h3>Mantenimientos recientes</h3>
              <p>Últimos registros operativos del módulo coordinador.</p>
            </div>
            <Wrench size={22} />
          </div>

          <div className="coord-table-wrap compact">
            <table className="coord-table">
              <thead>
                <tr>
                  <th>Equipo</th>
                  <th>Técnico</th>
                  <th>Tipo</th>
                  <th>Estado</th>
                  <th>Fecha</th>
                </tr>
              </thead>
              <tbody>
                {recientes.length === 0 ? (
                  <tr>
                    <td colSpan="5" className="coord-empty">No hay mantenimientos registrados.</td>
                  </tr>
                ) : (
                  recientes.map((m) => (
                    <tr key={m.id}>
                      <td>{m.equipo_nombre || "Sin equipo"}</td>
                      <td>{m.tecnico_nombre || "Sin técnico"}</td>
                      <td>{m.tipo || "N/A"}</td>
                      <td><span className={estadoClass(m.estado)}>{m.estado || "N/A"}</span></td>
                      <td>{fmtFecha(m.fecha_programada)}</td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </section>

        <section className="coord-card">
          <div className="coord-card-header">
            <div>
              <h3>Accesos rápidos</h3>
              <p>Operaciones frecuentes del coordinador.</p>
            </div>
            <PackageSearch size={22} />
          </div>

          <div className="coord-quick-actions">
            <button onClick={() => navigate("/coordinador/mantenimientos")}>Crear / editar mantenimientos</button>
            <button onClick={() => navigate("/coordinador/equipos")}>Ver inventario de equipos</button>
            <button onClick={() => navigate("/coordinador/hoja-vida")}>Consultar hojas de vida</button>
            <button onClick={() => navigate("/coordinador/evidencias")}>Revisar evidencias</button>
            <button onClick={() => navigate("/coordinador/informes")}>Generar reportes</button>
          </div>
        </section>
      </div>
    </div>
  );
}
