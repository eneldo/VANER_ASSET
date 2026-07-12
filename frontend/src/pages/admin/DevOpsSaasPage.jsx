// ============================================================
// PÁGINA: DevOps SaaS PRO
// Archivo: frontend/src/pages/admin/DevOpsSaasPage.jsx
// FASE 34.2.6
// ============================================================

import { useEffect, useMemo, useState } from "react";
import {
  Activity,
  Cpu,
  Database,
  HardDrive,
  RefreshCw,
  ServerCog,
  ShieldCheck,
  Terminal,
  Boxes,
  PlayCircle,
} from "lucide-react";

import AdminLayout from "./AdminLayout";
import {
  ejecutarAccionDevOps,
  obtenerEstadoDevOps,
  obtenerLogsServicio,
} from "../../api/devopsApi";

import "../../styles/devops-saas-pro.css";

export default function DevOpsSaasPage() {
  const [data, setData] = useState(null);
  const [logs, setLogs] = useState(null);
  const [servicioLogs, setServicioLogs] = useState("");
  const [cargando, setCargando] = useState(false);
  const [mensaje, setMensaje] = useState("");

  const servicios = data?.servicios || [];
  const resumen = data?.resumen || {};
  const sistema = data?.sistema || {};

  const estadoGlobal = useMemo(() => {
    if (!data) return "Cargando";
    if (!resumen.docker_disponible) return "Limitado";
    return "Operativo";
  }, [data, resumen.docker_disponible]);

  const cargar = async () => {
    setCargando(true);
    setMensaje("");
    try {
      const respuesta = await obtenerEstadoDevOps();
      setData(respuesta);
    } catch {
      setMensaje("No fue posible cargar estado DevOps.");
    } finally {
      setCargando(false);
    }
  };

  const verLogs = async (servicio) => {
    setServicioLogs(servicio);
    setMensaje("");
    try {
      const respuesta = await obtenerLogsServicio(servicio, 100);
      setLogs(respuesta);
    } catch {
      setMensaje("No fue posible cargar logs del servicio.");
    }
  };

  const accion = async (servicio, tipo) => {
    setMensaje("");
    try {
      const respuesta = await ejecutarAccionDevOps(servicio, tipo);
      setMensaje(respuesta.mensaje || "Acción procesada.");
      await cargar();
    } catch {
      setMensaje("Acción DevOps no disponible o no permitida.");
    }
  };

  useEffect(() => {
    const timer = window.setTimeout(() => cargar(), 0);
    return () => window.clearTimeout(timer);
  }, []);

  return (
    <AdminLayout>
      <div className="devops-page">
        <section className="devops-hero">
          <div>
            <span className="devops-badge">FASE 34.2.6</span>
            <h1>DevOps SaaS PRO</h1>
            <p>
              Centro de control de infraestructura: servicios, contenedores,
              estado Docker, backend, frontend, PostgreSQL y logs rápidos.
            </p>
          </div>

          <div className="devops-actions">
            <span className={`devops-status ${estadoGlobal.toLowerCase()}`}>
              {estadoGlobal}
            </span>
            <button onClick={cargar} disabled={cargando}>
              <RefreshCw size={18} /> Actualizar
            </button>
          </div>
        </section>

        {mensaje && <div className="devops-alert">{mensaje}</div>}

        <section className="devops-kpis">
          <Kpi icon={<ServerCog />} label="Backend" value={resumen.backend || "-"} />
          <Kpi icon={<Boxes />} label="Servicios activos" value={`${resumen.servicios_activos || 0}/${resumen.servicios_total || 0}`} />
          <Kpi icon={<Cpu />} label="CPU" value={`${sistema.cpu_pct ?? 0}%`} />
          <Kpi icon={<HardDrive />} label="Disco" value={`${sistema.disco_pct ?? 0}%`} />
          <Kpi icon={<Database />} label="PostgreSQL" value={resumen.postgresql || "-"} />
        </section>

        <section className="devops-grid-two">
          <article className="devops-card">
            <h2><Activity size={20} /> Servidor VPS</h2>
            <div className="devops-info-list">
              <p><strong>Hostname:</strong> {sistema.hostname || "-"}</p>
              <p><strong>Plataforma:</strong> {sistema.plataforma || "-"}</p>
              <p><strong>Uptime:</strong> {sistema.uptime_horas || 0} horas</p>
              <p><strong>RAM:</strong> {sistema.ram_usada_gb || 0} GB / {sistema.ram_total_gb || 0} GB ({sistema.ram_pct || 0}%)</p>
              <p><strong>Disco:</strong> {sistema.disco_usado_gb || 0} GB / {sistema.disco_total_gb || 0} GB ({sistema.disco_pct || 0}%)</p>
            </div>
          </article>

          <article className="devops-card">
            <h2><ShieldCheck size={20} /> Estado servicios clave</h2>
            <div className="devops-status-grid">
              <StatusChip label="Frontend" value={resumen.frontend} />
              <StatusChip label="Backend" value={resumen.backend} />
              <StatusChip label="PostgreSQL" value={resumen.postgresql} />
              <StatusChip label="Traefik" value={resumen.traefik} />
              <StatusChip label="Redis" value={resumen.redis} />
              <StatusChip label="Docker" value={resumen.docker_disponible ? "Disponible" : "No disponible"} />
            </div>
          </article>
        </section>

        <section className="devops-card">
          <div className="devops-section-title">
            <h2><Boxes size={20} /> Contenedores / Servicios</h2>
            <small>{servicios.length} registros</small>
          </div>

          <div className="devops-table-wrap">
            <table className="devops-table">
              <thead>
                <tr>
                  <th>Servicio</th>
                  <th>Imagen</th>
                  <th>Estado</th>
                  <th>Puertos</th>
                  <th>Acciones</th>
                </tr>
              </thead>
              <tbody>
                {servicios.map((servicio, index) => (
                  <tr key={`${servicio.nombre}-${index}`}>
                    <td>{servicio.nombre}</td>
                    <td>{servicio.imagen || "-"}</td>
                    <td>
                      <span className={`service-state ${String(servicio.estado).toLowerCase().includes("up") ? "up" : "down"}`}>
                        {servicio.estado}
                      </span>
                    </td>
                    <td className="devops-ports">{servicio.puertos || "-"}</td>
                    <td>
                      <div className="devops-row-actions">
                        <button onClick={() => verLogs(servicio.nombre)}>
                          <Terminal size={15} /> Logs
                        </button>
                        <button onClick={() => accion(servicio.nombre, "restart")}>
                          <PlayCircle size={15} /> Restart
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}

                {servicios.length === 0 && (
                  <tr>
                    <td colSpan="5" className="devops-empty">
                      No hay servicios detectados.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </section>

        {logs && (
          <section className="devops-card logs-card">
            <div className="devops-section-title">
              <h2><Terminal size={20} /> Logs: {servicioLogs}</h2>
              <small>{logs.lineas?.length || 0} líneas</small>
            </div>
            <pre className="devops-log-viewer">
              {(logs.lineas || []).join("\n")}
            </pre>
          </section>
        )}
      </div>
    </AdminLayout>
  );
}

function Kpi({ icon, label, value }) {
  return (
    <article className="devops-kpi">
      <div className="devops-kpi-icon">{icon}</div>
      <div>
        <span>{label}</span>
        <strong>{value}</strong>
      </div>
    </article>
  );
}

function StatusChip({ label, value }) {
  const online = String(value || "").toLowerCase().includes("online") || String(value || "").toLowerCase().includes("up") || String(value || "").toLowerCase().includes("disponible");
  return (
    <div className={`status-chip ${online ? "online" : "warning"}`}>
      <span>{label}</span>
      <strong>{value || "-"}</strong>
    </div>
  );
}
