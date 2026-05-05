// =========================================================
// DASHBOARD ADMIN INTELIGENTE - SGA PRO
// Nivel SaaS vendible
//
// Incluye:
// - Cards clicables
// - Equipos por estado
// - Mantenimientos por mes
// - Mantenimientos atrasados
// - Equipos críticos
// - Técnicos con mayor carga
// - % cumplimiento
// - Tabla dinámica por módulo
// =========================================================

import { useContext, useEffect, useMemo, useState } from "react";
import { AuthContext } from "../context/AuthContext";
import Sidebar from "../components/Sidebar";
import API from "../api/axios";

import {
  Building2,
  MapPin,
  MonitorCog,
  Wrench,
  UserCog,
  CheckCircle,
  Activity,
  RefreshCcw,
  AlertTriangle,
  ShieldAlert,
  CalendarClock,
  TrendingUp,
} from "lucide-react";

import {
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  Tooltip,
  ResponsiveContainer,
  XAxis,
  YAxis,
  CartesianGrid,
  Legend,
} from "recharts";

import "../styles/sidebar.css";
import "./DashboardAdmin.css";

const COLORS = ["#2563eb", "#22c55e", "#f59e0b", "#ef4444", "#6366f1", "#06b6d4"];

export default function DashboardAdmin() {
  const { user, logout } = useContext(AuthContext);

  const [empresas, setEmpresas] = useState([]);
  const [sedes, setSedes] = useState([]);
  const [equipos, setEquipos] = useState([]);
  const [mantenimientos, setMantenimientos] = useState([]);
  const [tecnicos, setTecnicos] = useState([]);

  const [vista, setVista] = useState("resumen");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    cargarDashboard();
  }, []);

  const cargarDashboard = async () => {
    try {
      setLoading(true);

      const [resEmpresas, resSedes, resEquipos, resMantenimientos, resTecnicos] =
        await Promise.all([
          API.get("/empresas/"),
          API.get("/sedes/"),
          API.get("/equipos/"),
          API.get("/mantenimientos/"),
          API.get("/tecnicos/"),
        ]);

      setEmpresas(resEmpresas.data || []);
      setSedes(resSedes.data || []);
      setEquipos(resEquipos.data || []);
      setMantenimientos(resMantenimientos.data || []);
      setTecnicos(resTecnicos.data || []);
    } catch (error) {
      console.error("Error cargando dashboard:", error);
      alert("Error cargando dashboard.");
    } finally {
      setLoading(false);
    }
  };

  // =========================================================
  // MÉTRICAS INTELIGENTES
  // =========================================================

  const equiposPorEstado = useMemo(() => {
    const estados = {};

    equipos.forEach((e) => {
      const estado = e.estado || "SIN_ESTADO";
      estados[estado] = (estados[estado] || 0) + 1;
    });

    return Object.entries(estados).map(([name, value]) => ({ name, value }));
  }, [equipos]);

  const mantenimientosPorMes = useMemo(() => {
    const meses = {};

    mantenimientos.forEach((m) => {
      const fecha = m.fecha_programada || m.creado_en || m.created_at;
      if (!fecha) return;

      const d = new Date(fecha);
      if (Number.isNaN(d.getTime())) return;

      const key = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}`;
      meses[key] = (meses[key] || 0) + 1;
    });

    return Object.entries(meses)
      .sort(([a], [b]) => a.localeCompare(b))
      .map(([mes, total]) => ({ mes, total }));
  }, [mantenimientos]);

  const tecnicosActivos = useMemo(() => {
    return tecnicos.filter((t) => t.activo !== false).length;
  }, [tecnicos]);

  const mantenimientosFinalizados = useMemo(() => {
    return mantenimientos.filter((m) => m.estado === "FINALIZADO").length;
  }, [mantenimientos]);

  const porcentajeCumplimiento = useMemo(() => {
    if (mantenimientos.length === 0) return 0;
    return Math.round((mantenimientosFinalizados / mantenimientos.length) * 100);
  }, [mantenimientos, mantenimientosFinalizados]);

  const mantenimientosAtrasados = useMemo(() => {
    const hoy = new Date();

    return mantenimientos.filter((m) => {
      if (!m.fecha_programada) return false;
      if (["FINALIZADO", "ANULADO"].includes(m.estado)) return false;

      const fecha = new Date(m.fecha_programada);
      return !Number.isNaN(fecha.getTime()) && fecha < hoy;
    });
  }, [mantenimientos]);

  const equiposCriticos = useMemo(() => {
    return equipos.filter((e) =>
      ["ALTA", "CRITICA"].includes(String(e.criticidad || "").toUpperCase())
    );
  }, [equipos]);

  const equiposFueraServicio = useMemo(() => {
    return equipos.filter((e) =>
      ["FUERA_DE_SERVICIO", "BAJA"].includes(String(e.estado || "").toUpperCase())
    );
  }, [equipos]);

  const cargaTecnicos = useMemo(() => {
    const mapa = {};

    mantenimientos.forEach((m) => {
      if (!m.tecnico_id) return;

      mapa[m.tecnico_id] = (mapa[m.tecnico_id] || 0) + 1;
    });

    return Object.entries(mapa)
      .map(([tecnico_id, total]) => ({
        tecnico: obtenerNombreTecnico(tecnico_id, tecnicos),
        total,
      }))
      .sort((a, b) => b.total - a.total)
      .slice(0, 6);
  }, [mantenimientos, tecnicos]);

  const datosVista = {
    empresas,
    sedes,
    equipos,
    mantenimientos,
    tecnicos,
    atrasados: mantenimientosAtrasados,
    criticos: equiposCriticos,
    fuera_servicio: equiposFueraServicio,
  };

  return (
    <div className="dash-shell">
      <Sidebar user={user} onLogout={logout} />

      <main className="dash-main">
        {/* =====================================================
            HEADER
        ===================================================== */}
        <div className="dash-header">
          <div>
            <p className="dash-kicker">SGA PRO · DASHBOARD INTELIGENTE</p>
            <h1>Dashboard Administrador</h1>
            <p>
              Control general de empresas, sedes, inventario, mantenimientos,
              cumplimiento y alertas operativas.
            </p>
          </div>

          <button className="dash-refresh" onClick={cargarDashboard}>
            <RefreshCcw size={17} />
            {loading ? "Cargando..." : "Actualizar"}
          </button>
        </div>

        {/* =====================================================
            CARDS PRINCIPALES
        ===================================================== */}
        <section className="dash-cards">
          <MetricCard
            title="Empresas"
            value={empresas.length}
            icon={<Building2 />}
            onClick={() => setVista("empresas")}
          />

          <MetricCard
            title="Sedes"
            value={sedes.length}
            icon={<MapPin />}
            onClick={() => setVista("sedes")}
          />

          <MetricCard
            title="Equipos"
            value={equipos.length}
            icon={<MonitorCog />}
            onClick={() => setVista("equipos")}
          />

          <MetricCard
            title="Mantenimientos"
            value={mantenimientos.length}
            icon={<Wrench />}
            onClick={() => setVista("mantenimientos")}
          />

          <MetricCard
            title="Técnicos activos"
            value={tecnicosActivos}
            icon={<UserCog />}
            onClick={() => setVista("tecnicos")}
          />

          <MetricCard
            title="% Cumplimiento"
            value={`${porcentajeCumplimiento}%`}
            icon={<CheckCircle />}
            onClick={() => setVista("mantenimientos")}
          />
        </section>

        {/* =====================================================
            ALERTAS INTELIGENTES
        ===================================================== */}
        <section className="dash-alerts">
          <AlertCard
            title="Mantenimientos atrasados"
            value={mantenimientosAtrasados.length}
            icon={<CalendarClock />}
            type="warning"
            onClick={() => setVista("atrasados")}
          />

          <AlertCard
            title="Equipos críticos"
            value={equiposCriticos.length}
            icon={<ShieldAlert />}
            type="danger"
            onClick={() => setVista("criticos")}
          />

          <AlertCard
            title="Fuera de servicio / baja"
            value={equiposFueraServicio.length}
            icon={<AlertTriangle />}
            type="danger"
            onClick={() => setVista("fuera_servicio")}
          />

          <AlertCard
            title="Finalizados"
            value={mantenimientosFinalizados}
            icon={<TrendingUp />}
            type="success"
            onClick={() => setVista("mantenimientos")}
          />
        </section>

        {/* =====================================================
            GRÁFICAS
        ===================================================== */}
        <section className="dash-charts">
          <div className="dash-chart-card">
            <h2>Equipos por estado</h2>

            {equiposPorEstado.length === 0 ? (
              <div className="dash-empty">Sin datos de equipos.</div>
            ) : (
              <ResponsiveContainer width="100%" height={290}>
                <PieChart>
                  <Pie
                    data={equiposPorEstado}
                    dataKey="value"
                    nameKey="name"
                    outerRadius={95}
                    label={({ name, percent }) =>
                      `${name} ${(percent * 100).toFixed(0)}%`
                    }
                  >
                    {equiposPorEstado.map((_, index) => (
                      <Cell key={index} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            )}
          </div>

          <div className="dash-chart-card">
            <h2>Mantenimientos por mes</h2>

            {mantenimientosPorMes.length === 0 ? (
              <div className="dash-empty">Sin datos de mantenimientos.</div>
            ) : (
              <ResponsiveContainer width="100%" height={290}>
                <BarChart data={mantenimientosPorMes}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                  <XAxis dataKey="mes" />
                  <YAxis allowDecimals={false} />
                  <Tooltip />
                  <Bar dataKey="total" fill="#2563eb" radius={[10, 10, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            )}
          </div>
        </section>

        {/* =====================================================
            GRÁFICA DE CARGA TÉCNICA
        ===================================================== */}
        <section className="dash-chart-card dash-full-chart">
          <h2>Carga de mantenimientos por técnico</h2>

          {cargaTecnicos.length === 0 ? (
            <div className="dash-empty">No hay mantenimientos asignados a técnicos.</div>
          ) : (
            <ResponsiveContainer width="100%" height={270}>
              <BarChart data={cargaTecnicos}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                <XAxis dataKey="tecnico" />
                <YAxis allowDecimals={false} />
                <Tooltip />
                <Bar dataKey="total" fill="#06b6d4" radius={[10, 10, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          )}
        </section>

        {/* =====================================================
            TABLA DINÁMICA
        ===================================================== */}
        <section className="dash-detail-card">
          <div className="dash-detail-header">
            <div>
              <h2>
                <Activity size={20} />
                Vista rápida: {vista.toUpperCase()}
              </h2>
              <p>
                Haz clic en una tarjeta superior para consultar los registros.
              </p>
            </div>

            <button className="dash-clear" onClick={() => setVista("resumen")}>
              Resumen
            </button>
          </div>

          {vista === "resumen" ? (
            <div className="dash-empty">
              Selecciona Empresas, Sedes, Equipos, Mantenimientos, Técnicos o Alertas.
            </div>
          ) : (
            <DataTable tipo={vista} data={datosVista[vista] || []} />
          )}
        </section>
      </main>
    </div>
  );
}

// =========================================================
// CARD MÉTRICA PRINCIPAL
// =========================================================

function MetricCard({ title, value, icon, onClick }) {
  return (
    <button className="dash-card" onClick={onClick}>
      <div className="dash-card-icon">{icon}</div>

      <div>
        <span>{title}</span>
        <strong>{value}</strong>
      </div>
    </button>
  );
}

// =========================================================
// CARD ALERTA INTELIGENTE
// =========================================================

function AlertCard({ title, value, icon, type, onClick }) {
  return (
    <button className={`dash-alert-card ${type}`} onClick={onClick}>
      <div className="dash-alert-icon">{icon}</div>

      <div>
        <span>{title}</span>
        <strong>{value}</strong>
      </div>
    </button>
  );
}

// =========================================================
// TABLA DINÁMICA
// =========================================================

function DataTable({ tipo, data }) {
  if (!data.length) {
    return <div className="dash-empty">No hay registros para mostrar.</div>;
  }

  const columnsByType = {
    empresas: ["nombre", "nit", "telefono", "email", "estado"],
    sedes: ["nombre", "direccion", "telefono", "empresa_id"],
    equipos: ["nombre", "marca", "modelo", "estado", "criticidad"],
    mantenimientos: ["tipo", "estado", "fecha_programada", "tecnico_id"],
    tecnicos: ["nombre", "email", "telefono", "activo"],
    atrasados: ["tipo", "estado", "fecha_programada", "tecnico_id"],
    criticos: ["nombre", "marca", "modelo", "estado", "criticidad"],
    fuera_servicio: ["nombre", "marca", "modelo", "estado", "criticidad"],
  };

  const columns = columnsByType[tipo] || Object.keys(data[0]).slice(0, 5);

  return (
    <div className="dash-table-wrap">
      <table className="dash-table">
        <thead>
          <tr>
            {columns.map((c) => (
              <th key={c}>{c.replaceAll("_", " ")}</th>
            ))}
          </tr>
        </thead>

        <tbody>
          {data.slice(0, 10).map((item, index) => (
            <tr key={item.id || index}>
              {columns.map((c) => (
                <td key={c}>{formatValue(item[c])}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

// =========================================================
// HELPERS
// =========================================================

function formatValue(value) {
  if (value === null || value === undefined || value === "") return "—";

  if (typeof value === "boolean") return value ? "Sí" : "No";

  if (typeof value === "string" && value.includes("T")) {
    const d = new Date(value);
    if (!Number.isNaN(d.getTime())) return d.toLocaleDateString();
  }

  return String(value);
}

function obtenerNombreTecnico(tecnicoId, tecnicos) {
  const tecnico = tecnicos.find((t) => String(t.id) === String(tecnicoId));

  return (
    tecnico?.nombre ||
    tecnico?.nombres ||
    tecnico?.nombre_completo ||
    `Técnico ${String(tecnicoId).slice(0, 6)}`
  );
}