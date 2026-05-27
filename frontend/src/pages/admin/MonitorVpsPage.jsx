// ============================================================
// MONITOR VPS + POSTGRESQL PRO
// Archivo: frontend/src/pages/admin/MonitorVpsPage.jsx
// Fase 34.2.4
// ============================================================

import { useEffect, useMemo, useState } from "react";
import {
  Activity,
  AlertTriangle,
  Cpu,
  Database,
  HardDrive,
  RefreshCw,
  Server,
  ShieldCheck,
} from "lucide-react";

import AdminLayout from "./AdminLayout";
import { monitorVpsApi } from "../../api/monitorVpsApi";
import "../../styles/monitor-vps-pro.css";

function formatPct(value) {
  const number = Number(value || 0);
  return `${number.toFixed(1)}%`;
}

function StatusBadge({ estado }) {
  const ok = String(estado || "").toUpperCase() === "OK";
  return <span className={`monitor-badge ${ok ? "ok" : "warn"}`}>{ok ? "Operativo" : "Alerta"}</span>;
}

function MetricCard({ icon, title, value, subtitle, danger }) {
  return (
    <div className={`monitor-card ${danger ? "danger" : ""}`}>
      <div className="monitor-card-icon">{icon}</div>
      <div>
        <p>{title}</p>
        <h3>{value}</h3>
        <span>{subtitle}</span>
      </div>
    </div>
  );
}

export default function MonitorVpsPage() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const cargar = async () => {
    try {
      setLoading(true);
      setError("");
      const res = await monitorVpsApi.resumen();
      setData(res);
    } catch (err) {
      console.error(err);
      setError("No fue posible cargar el monitor VPS + PostgreSQL.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    cargar();
  }, []);

  const vps = data?.vps || {};
  const pg = data?.postgresql || {};
  const docker = data?.docker || {};
  const alertas = data?.alertas || [];

  const updatedAt = useMemo(() => {
    if (!data?.timestamp) return "Sin actualización";
    try {
      return new Date(data.timestamp).toLocaleString();
    } catch {
      return data.timestamp;
    }
  }, [data]);

  return (
    <AdminLayout>
      <div className="monitor-page">
        <section className="monitor-hero">
          <div>
            <span className="monitor-chip">FASE 34.2.4</span>
            <h1>Monitor VPS + PostgreSQL PRO</h1>
            <p>
              Centro de observabilidad para CPU, RAM, disco, PostgreSQL, Docker y estado general del sistema SGA SaaS.
            </p>
          </div>

          <div className="monitor-actions">
            <StatusBadge estado={data?.estado_general || "OK"} />
            <button onClick={cargar} disabled={loading}>
              <RefreshCw size={18} className={loading ? "spin" : ""} />
              Actualizar
            </button>
          </div>
        </section>

        {error && (
          <div className="monitor-alert error">
            <AlertTriangle size={18} />
            {error}
          </div>
        )}

        {alertas.length > 0 && (
          <div className="monitor-alert warning">
            <AlertTriangle size={18} />
            <div>
              <strong>Alertas activas:</strong> {alertas.join(", ")}
            </div>
          </div>
        )}

        <section className="monitor-grid">
          <MetricCard
            icon={<Cpu size={24} />}
            title="CPU"
            value={formatPct(vps.cpu_percent)}
            subtitle={`${vps.cpu_cores_logicos || 0} núcleos lógicos`}
            danger={Number(vps.cpu_percent || 0) >= 85}
          />

          <MetricCard
            icon={<Activity size={24} />}
            title="RAM"
            value={formatPct(vps.ram_percent)}
            subtitle={`${vps.ram_usada_gb || 0} GB / ${vps.ram_total_gb || 0} GB`}
            danger={Number(vps.ram_percent || 0) >= 90}
          />

          <MetricCard
            icon={<HardDrive size={24} />}
            title="Disco"
            value={formatPct(vps.disco_percent)}
            subtitle={`${vps.disco_usado_gb || 0} GB / ${vps.disco_total_gb || 0} GB`}
            danger={Number(vps.disco_percent || 0) >= 85}
          />

          <MetricCard
            icon={<Database size={24} />}
            title="PostgreSQL"
            value={pg.ok ? "Online" : "Error"}
            subtitle={`${pg.tamano_gb || 0} GB · ${pg.conexiones_total || 0} conexiones`}
            danger={!pg.ok}
          />
        </section>

        <section className="monitor-panels">
          <div className="monitor-panel">
            <div className="monitor-panel-title">
              <Server size={20} />
              <h2>Servidor VPS</h2>
            </div>
            <div className="monitor-list">
              <p><strong>Hostname:</strong> {vps.hostname || "-"}</p>
              <p><strong>Sistema:</strong> {vps.plataforma || "-"}</p>
              <p><strong>Uptime:</strong> {vps.uptime_horas || 0} horas</p>
              <p><strong>Red recibida:</strong> {vps.red_bytes_recibidos_gb || 0} GB</p>
              <p><strong>Red enviada:</strong> {vps.red_bytes_enviados_gb || 0} GB</p>
            </div>
          </div>

          <div className="monitor-panel">
            <div className="monitor-panel-title">
              <Database size={20} />
              <h2>PostgreSQL</h2>
            </div>
            <div className="monitor-list">
              <p><strong>Base:</strong> {pg.base_datos || "-"}</p>
              <p><strong>Usuario:</strong> {pg.usuario || "-"}</p>
              <p><strong>Tablas:</strong> {pg.total_tablas || 0}</p>
              <p><strong>Conexiones activas:</strong> {pg.conexiones_activas || 0}</p>
              <p><strong>Conexiones idle:</strong> {pg.conexiones_idle || 0}</p>
            </div>
          </div>
        </section>

        <section className="monitor-panel docker-panel">
          <div className="monitor-panel-title">
            <ShieldCheck size={20} />
            <h2>Docker / Contenedores</h2>
          </div>

          {!docker.ok ? (
            <p className="monitor-muted">{docker.mensaje || "Docker CLI no disponible dentro del contenedor backend."}</p>
          ) : (
            <div className="monitor-table-wrap">
              <table className="monitor-table">
                <thead>
                  <tr>
                    <th>Contenedor</th>
                    <th>Estado</th>
                    <th>Imagen</th>
                    <th>Puertos</th>
                  </tr>
                </thead>
                <tbody>
                  {(docker.containers || []).map((item, idx) => (
                    <tr key={idx}>
                      <td>{item.nombre}</td>
                      <td>{item.estado}</td>
                      <td>{item.imagen}</td>
                      <td>{item.puertos || "-"}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>

        <div className="monitor-footer">
          Última actualización: {updatedAt}
        </div>
      </div>
    </AdminLayout>
  );
}
