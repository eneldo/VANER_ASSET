// =========================================================
// DASHBOARD ADMIN INTELIGENTE - SGA PRO
// Nivel SaaS PRO
//
// Mejoras:
// - Dashboard compacto usable al 100% de zoom.
// - Scroll vertical interno.
// - Vista rápida dinámica por módulo.
// - Click en Sedes muestra tabla compacta.
// - Click en una sede muestra detalle inteligente.
// - Técnicos completos con nombre, correo, teléfono y carga.
// - Sin tarjetas gigantes repetidas de sedes.
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
  X,
  MapPinned,
  Factory,
  Phone,
  Mail,
  ClipboardList,
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
  const [busqueda, setBusqueda] = useState("");
  const [sedeSeleccionada, setSedeSeleccionada] = useState(null);
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

  const cambiarVista = (nuevaVista) => {
    setVista(nuevaVista);
    setBusqueda("");
    setSedeSeleccionada(null);
  };

  // =========================================================
  // DATOS ENRIQUECIDOS
  // =========================================================

  const sedesEnriquecidas = useMemo(() => {
    return sedes.map((sede) => {
      const empresa = empresas.find((e) => String(e.id) === String(sede.empresa_id));

      const equiposSede = equipos.filter(
        (equipo) => String(equipo.sede_id) === String(sede.id)
      );

      const mantenimientosSede = mantenimientos.filter((m) =>
        equiposSede.some((eq) => String(eq.id) === String(m.equipo_id))
      );

      const pendientes = mantenimientosSede.filter(
        (m) => !["FINALIZADO", "ANULADO"].includes(String(m.estado || "").toUpperCase())
      );

      const finalizados = mantenimientosSede.filter(
        (m) => String(m.estado || "").toUpperCase() === "FINALIZADO"
      );

      return {
        ...sede,
        empresa_nombre: empresa?.nombre || sede.empresa_nombre || "—",
        empresa_nit: empresa?.nit || "—",
        total_equipos: equiposSede.length,
        total_mantenimientos: mantenimientosSede.length,
        pendientes: pendientes.length,
        finalizados: finalizados.length,
        equipos: equiposSede,
        mantenimientos: mantenimientosSede,
      };
    });
  }, [sedes, empresas, equipos, mantenimientos]);

  const tecnicosEnriquecidos = useMemo(() => {
    return tecnicos.map((tecnico) => {
      const usuario = tecnico.usuario || {};
      const asignados = mantenimientos.filter(
        (m) => String(m.tecnico_id) === String(tecnico.id)
      );

      return {
        ...tecnico,
        nombre_visible:
          usuario.nombre_completo ||
          tecnico.nombre_completo ||
          tecnico.nombre ||
          tecnico.nombres ||
          `Técnico ${String(tecnico.id).slice(0, 6)}`,
        email_visible: usuario.email || tecnico.email || "—",
        telefono_visible: tecnico.telefono || usuario.telefono || "—",
        especialidad_visible: tecnico.especialidad || tecnico.cargo || "—",
        total_mantenimientos: asignados.length,
        activos: asignados.filter((m) =>
          ["ASIGNADO", "EN_PROCESO", "PAUSADO"].includes(String(m.estado || "").toUpperCase())
        ).length,
        finalizados: asignados.filter((m) => String(m.estado || "").toUpperCase() === "FINALIZADO").length,
      };
    });
  }, [tecnicos, mantenimientos]);

  const equiposEnriquecidos = useMemo(() => {
    return equipos.map((equipo) => {
      const sede = sedesEnriquecidas.find((s) => String(s.id) === String(equipo.sede_id));
      const empresa = empresas.find((e) => String(e.id) === String(equipo.empresa_id));
      const mantEquipo = mantenimientos.filter((m) => String(m.equipo_id) === String(equipo.id));

      return {
        ...equipo,
        sede_nombre: sede?.nombre || equipo.sede_nombre || "—",
        empresa_nombre: empresa?.nombre || sede?.empresa_nombre || equipo.empresa_nombre || "—",
        total_mantenimientos: mantEquipo.length,
      };
    });
  }, [equipos, empresas, sedesEnriquecidas, mantenimientos]);

  const mantenimientosEnriquecidos = useMemo(() => {
    return mantenimientos.map((m) => {
      const equipo = equiposEnriquecidos.find((e) => String(e.id) === String(m.equipo_id));
      const tecnico = tecnicosEnriquecidos.find((t) => String(t.id) === String(m.tecnico_id));

      return {
        ...m,
        equipo_nombre: m.equipo_nombre || equipo?.nombre || "—",
        empresa_nombre: m.empresa_nombre || equipo?.empresa_nombre || "—",
        sede_nombre: m.sede_nombre || equipo?.sede_nombre || "—",
        tecnico_nombre: m.tecnico_nombre || tecnico?.nombre_visible || "—",
      };
    });
  }, [mantenimientos, equiposEnriquecidos, tecnicosEnriquecidos]);

  // =========================================================
  // MÉTRICAS
  // =========================================================

  const equiposPorEstado = useMemo(() => {
    const estados = {};
    equipos.forEach((e) => {
      const estado = e.estado || "SIN ESTADO";
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

  const tecnicosActivos = tecnicosEnriquecidos.filter((t) => t.activo !== false).length;

  const mantenimientosFinalizados = mantenimientos.filter(
    (m) => String(m.estado || "").toUpperCase() === "FINALIZADO"
  ).length;

  const porcentajeCumplimiento =
    mantenimientos.length === 0
      ? 0
      : Math.round((mantenimientosFinalizados / mantenimientos.length) * 100);

  const mantenimientosAtrasados = useMemo(() => {
    const hoy = new Date();

    return mantenimientosEnriquecidos.filter((m) => {
      if (!m.fecha_programada) return false;
      if (["FINALIZADO", "ANULADO"].includes(String(m.estado || "").toUpperCase())) return false;

      const fecha = new Date(m.fecha_programada);
      return !Number.isNaN(fecha.getTime()) && fecha < hoy;
    });
  }, [mantenimientosEnriquecidos]);

  const equiposCriticos = equiposEnriquecidos.filter((e) =>
    ["ALTA", "CRITICA", "CRÍTICA"].includes(String(e.criticidad || "").toUpperCase())
  );

  const equiposFueraServicio = equiposEnriquecidos.filter((e) =>
    ["FUERA_DE_SERVICIO", "FUERA DE SERVICIO", "BAJA"].includes(
      String(e.estado || "").toUpperCase()
    )
  );

  const cargaTecnicos = tecnicosEnriquecidos
    .filter((t) => t.total_mantenimientos > 0)
    .map((t) => ({
      tecnico: t.nombre_visible,
      total: t.total_mantenimientos,
    }))
    .sort((a, b) => b.total - a.total)
    .slice(0, 6);

  const datosVista = {
    empresas,
    sedes: sedesEnriquecidas,
    equipos: equiposEnriquecidos,
    mantenimientos: mantenimientosEnriquecidos,
    tecnicos: tecnicosEnriquecidos,
    atrasados: mantenimientosAtrasados,
    criticos: equiposCriticos,
    fuera_servicio: equiposFueraServicio,
  };

  const dataFiltrada = useMemo(() => {
    const data = datosVista[vista] || [];
    const q = busqueda.toLowerCase().trim();

    if (!q) return data;

    return data.filter((item) =>
      JSON.stringify(item).toLowerCase().includes(q)
    );
  }, [vista, busqueda, datosVista]);

  return (
    <div className="dash-shell">
      <Sidebar user={user} onLogout={logout} />

      <main className="dash-main">
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
            <RefreshCcw size={16} />
            {loading ? "Cargando..." : "Actualizar"}
          </button>
        </div>

        <section className="dash-cards">
          <MetricCard title="Empresas" value={empresas.length} icon={<Building2 />} onClick={() => cambiarVista("empresas")} />
          <MetricCard title="Sedes" value={sedes.length} icon={<MapPin />} onClick={() => cambiarVista("sedes")} />
          <MetricCard title="Equipos" value={equipos.length} icon={<MonitorCog />} onClick={() => cambiarVista("equipos")} />
          <MetricCard title="Mantenimientos" value={mantenimientos.length} icon={<Wrench />} onClick={() => cambiarVista("mantenimientos")} />
          <MetricCard title="Técnicos activos" value={tecnicosActivos} icon={<UserCog />} onClick={() => cambiarVista("tecnicos")} />
          <MetricCard title="% Cumplimiento" value={`${porcentajeCumplimiento}%`} icon={<CheckCircle />} onClick={() => cambiarVista("mantenimientos")} />
        </section>

        <section className="dash-alerts">
          <AlertCard title="Mantenimientos atrasados" value={mantenimientosAtrasados.length} icon={<CalendarClock />} type="warning" onClick={() => cambiarVista("atrasados")} />
          <AlertCard title="Equipos críticos" value={equiposCriticos.length} icon={<ShieldAlert />} type="danger" onClick={() => cambiarVista("criticos")} />
          <AlertCard title="Fuera de servicio / baja" value={equiposFueraServicio.length} icon={<AlertTriangle />} type="danger" onClick={() => cambiarVista("fuera_servicio")} />
          <AlertCard title="Finalizados" value={mantenimientosFinalizados} icon={<TrendingUp />} type="success" onClick={() => cambiarVista("mantenimientos")} />
        </section>

        <section className="dash-charts">
          <div className="dash-chart-card">
            <h2>Equipos por estado</h2>

            {equiposPorEstado.length === 0 ? (
              <div className="dash-empty">Sin datos de equipos.</div>
            ) : (
              <ResponsiveContainer width="100%" height={220}>
                <PieChart>
                  <Pie
                    data={equiposPorEstado}
                    dataKey="value"
                    nameKey="name"
                    outerRadius={72}
                    label
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
              <ResponsiveContainer width="100%" height={220}>
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

        <section className="dash-chart-card dash-full-chart">
          <h2>Carga por técnico</h2>

          {cargaTecnicos.length === 0 ? (
            <div className="dash-empty">No hay mantenimientos asignados a técnicos.</div>
          ) : (
            <ResponsiveContainer width="100%" height={210}>
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

        <section className="dash-detail-card">
          <div className="dash-detail-header">
            <div>
              <h2>
                <Activity size={19} />
                Vista rápida: {vista.toUpperCase()}
              </h2>
              <p>
                Haz clic en una tarjeta superior. En Sedes puedes seleccionar una sede para ver su detalle.
              </p>
            </div>

            <button className="dash-clear" onClick={() => cambiarVista("resumen")}>
              Resumen
            </button>
          </div>

          {vista === "resumen" ? (
            <div className="dash-empty">
              Selecciona Empresas, Sedes, Equipos, Mantenimientos, Técnicos o Alertas.
            </div>
          ) : (
            <>
              <div className="dash-filter-row">
                <input
                  value={busqueda}
                  onChange={(e) => setBusqueda(e.target.value)}
                  placeholder={`Buscar en ${vista}...`}
                />

                <span>{dataFiltrada.length} registros</span>
              </div>

              <div className={vista === "sedes" ? "dash-master-detail" : ""}>
                <DataTable
                  tipo={vista}
                  data={dataFiltrada}
                  onRowClick={(item) => {
                    if (vista === "sedes") setSedeSeleccionada(item);
                  }}
                />

                {vista === "sedes" && sedeSeleccionada && (
                  <SedeDetalle
                    sede={sedeSeleccionada}
                    onClose={() => setSedeSeleccionada(null)}
                  />
                )}
              </div>
            </>
          )}
        </section>
      </main>
    </div>
  );
}

// =========================================================
// COMPONENTES
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

function DataTable({ tipo, data, onRowClick }) {
  if (!data.length) {
    return <div className="dash-empty">No hay registros para mostrar.</div>;
  }

  const columnsByType = {
    empresas: ["nombre", "nit", "telefono", "email", "estado"],
    sedes: ["nombre", "empresa_nombre", "direccion", "telefono", "total_equipos", "total_mantenimientos"],
    equipos: ["nombre", "empresa_nombre", "sede_nombre", "estado", "criticidad", "total_mantenimientos"],
    mantenimientos: ["equipo_nombre", "empresa_nombre", "sede_nombre", "tipo", "estado", "fecha_programada", "tecnico_nombre"],
    tecnicos: ["nombre_visible", "email_visible", "telefono_visible", "especialidad_visible", "total_mantenimientos", "activos"],
    atrasados: ["equipo_nombre", "empresa_nombre", "sede_nombre", "tipo", "estado", "fecha_programada", "tecnico_nombre"],
    criticos: ["nombre", "empresa_nombre", "sede_nombre", "estado", "criticidad"],
    fuera_servicio: ["nombre", "empresa_nombre", "sede_nombre", "estado", "criticidad"],
  };

  const columns = columnsByType[tipo] || Object.keys(data[0]).slice(0, 6);

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
          {data.slice(0, 15).map((item, index) => (
            <tr
              key={item.id || index}
              className={onRowClick ? "dash-row-clickable" : ""}
              onClick={() => onRowClick && onRowClick(item)}
            >
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

function SedeDetalle({ sede, onClose }) {
  return (
    <aside className="dash-side-detail">
      <div className="dash-side-head">
        <div>
          <p>Detalle de sede</p>
          <h3>{sede.nombre}</h3>
        </div>

        <button onClick={onClose}>
          <X size={16} />
        </button>
      </div>

      <div className="dash-side-info">
        <InfoLine icon={<Factory size={15} />} label="Empresa" value={sede.empresa_nombre} />
        <InfoLine icon={<MapPinned size={15} />} label="Dirección" value={sede.direccion} />
        <InfoLine icon={<Phone size={15} />} label="Teléfono" value={sede.telefono} />
        <InfoLine icon={<Mail size={15} />} label="NIT empresa" value={sede.empresa_nit} />
      </div>

      <div className="dash-side-stats">
        <div>
          <span>Equipos</span>
          <strong>{sede.total_equipos}</strong>
        </div>

        <div>
          <span>Mantenimientos</span>
          <strong>{sede.total_mantenimientos}</strong>
        </div>

        <div>
          <span>Pendientes</span>
          <strong>{sede.pendientes}</strong>
        </div>

        <div>
          <span>Finalizados</span>
          <strong>{sede.finalizados}</strong>
        </div>
      </div>

      <div className="dash-side-list">
        <h4>
          <MonitorCog size={15} />
          Equipos de la sede
        </h4>

        {sede.equipos?.length ? (
          sede.equipos.slice(0, 8).map((equipo) => (
            <div key={equipo.id} className="dash-mini-item">
              <strong>{equipo.nombre}</strong>
              <span>{equipo.estado || "Sin estado"} · {equipo.criticidad || "Sin criticidad"}</span>
            </div>
          ))
        ) : (
          <p className="dash-mini-empty">Sin equipos registrados.</p>
        )}
      </div>

      <div className="dash-side-list">
        <h4>
          <ClipboardList size={15} />
          Últimos mantenimientos
        </h4>

        {sede.mantenimientos?.length ? (
          sede.mantenimientos.slice(0, 6).map((m) => (
            <div key={m.id} className="dash-mini-item">
              <strong>{m.tipo}</strong>
              <span>{m.estado || "Sin estado"} · {formatValue(m.fecha_programada)}</span>
            </div>
          ))
        ) : (
          <p className="dash-mini-empty">Sin mantenimientos registrados.</p>
        )}
      </div>
    </aside>
  );
}

function InfoLine({ icon, label, value }) {
  return (
    <div className="dash-info-line">
      {icon}
      <div>
        <span>{label}</span>
        <strong>{formatValue(value)}</strong>
      </div>
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