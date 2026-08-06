// ============================================================
// DASHBOARD ADMIN SaaS PRO - SGA Empresarial
// Fase 33.1
// Archivo: frontend/src/pages/DashboardAdmin.jsx
//
// Objetivo:
// - Dashboard ejecutivo para ADMIN.
// - KPIs SaaS, alertas, grÃ¡ficas, acciones rÃ¡pidas y vista rÃ¡pida.
// - Responsive PC / tablet / celular.
// - Compatible con backend actual: empresas, sedes, equipos,
//   mantenimientos y técnicos.
// ============================================================

import { useContext, useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { AuthContext } from "../context/auth-context";
import Sidebar from "../components/Sidebar";
import API from "../api/axios";

import {
  Activity,
  AlertTriangle,
  ArrowRight,
  BarChart3,
  Building2,
  CalendarClock,
  CheckCircle2,
  ClipboardList,
  Download,
  Factory,
  Gauge,
  LayoutDashboard,
  Mail,
  MapPin,
  MapPinned,
  MonitorCog,
  Phone,
  Plus,
  RefreshCcw,
  Search,
  ShieldAlert,
  Sparkles,
  UserCog,
  Wrench,
  X,
} from "lucide-react";

import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import "../styles/sidebar.css";
import "./DashboardAdmin.css";

const COLORS = ["#2563eb", "#06b6d4", "#22c55e", "#f59e0b", "#ef4444", "#7c3aed"];

const ESTADOS_ACTIVOS = ["PROGRAMADO", "ASIGNADO", "EN_PROCESO", "PAUSADO"];
const ESTADOS_CERRADOS = ["FINALIZADO", "ANULADO"];

const initialState = {
  empresas: [],
  sedes: [],
  equipos: [],
  mantenimientos: [],
  tecnicos: [],
};

export default function DashboardAdmin() {
  const { user, logout } = useContext(AuthContext);
  const navigate = useNavigate();

  const [data, setData] = useState(initialState);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState("");
  const [vista, setVista] = useState("mantenimientos");
  const [busqueda, setBusqueda] = useState("");
  const [paginaActual, setPaginaActual] = useState(1);
  const [registrosPorPagina, setRegistrosPorPagina] = useState(10);
  const [sedeSeleccionada, setSedeSeleccionada] = useState(null);

  useEffect(() => {
    cargarDashboard(true);

  }, []);

  useEffect(() => {
    const timer = window.setTimeout(() => setPaginaActual(1), 0);
    return () => window.clearTimeout(timer);
  }, [vista, busqueda, registrosPorPagina]);

  async function cargarDashboard(firstLoad = false) {
    try {
      if (firstLoad) setLoading(true);
      setRefreshing(true);
      setError("");

      // Promise.allSettled evita que todo el dashboard se caiga si un módulo falla.
      const results = await Promise.allSettled([
        API.get("/empresas/"),
        API.get("/sedes/"),
        API.get("/equipos/"),
        API.get("/mantenimientos/"),
        API.get("/tecnicos/"),
      ]);

      const [empresas, sedes, equipos, mantenimientos, tecnicos] = results.map((result) => {
        if (result.status === "fulfilled") return Array.isArray(result.value.data) ? result.value.data : [];
        return [];
      });

      const fallos = results.filter((result) => result.status === "rejected").length;
      if (fallos > 0) {
        setError(`Se cargó el dashboard, pero ${fallos} módulo(s) no respondieron correctamente.`);
      }

      setData({ empresas, sedes, equipos, mantenimientos, tecnicos });
    } catch (err) {
      console.error("Error cargando Dashboard Admin:", err);
      setError("No fue posible cargar el dashboard. Verifica backend, sesión o conexión.");
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }

  const empresas = data.empresas;
  const sedes = data.sedes;
  const equipos = data.equipos;
  const mantenimientos = data.mantenimientos;
  const tecnicos = data.tecnicos;

  // =========================================================
  // DATOS ENRIQUECIDOS
  // =========================================================

  const sedesEnriquecidas = useMemo(() => {
    return sedes.map((sede) => {
      const empresa = empresas.find((e) => sameId(e.id, sede.empresa_id));
      const equiposSede = equipos.filter((equipo) => sameId(equipo.sede_id, sede.id));
      const mantenimientosSede = mantenimientos.filter((m) =>
        equiposSede.some((eq) => sameId(eq.id, m.equipo_id))
      );

      const pendientes = mantenimientosSede.filter(
        (m) => !ESTADOS_CERRADOS.includes(normalizeEstado(m.estado))
      );
      const finalizados = mantenimientosSede.filter(
        (m) => normalizeEstado(m.estado) === "FINALIZADO"
      );

      return {
        ...sede,
        empresa_nombre: empresa?.nombre || sede.empresa_nombre || "â€”",
        empresa_nit: empresa?.nit || "â€”",
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
      const asignados = mantenimientos.filter((m) => sameId(m.tecnico_id, tecnico.id));
      const activos = asignados.filter((m) => ESTADOS_ACTIVOS.includes(normalizeEstado(m.estado)));
      const finalizados = asignados.filter((m) => normalizeEstado(m.estado) === "FINALIZADO");

      return {
        ...tecnico,
        nombre_visible:
          usuario.nombre_completo ||
          tecnico.nombre_completo ||
          tecnico.nombre ||
          tecnico.nombres ||
          `Técnico ${String(tecnico.id || "").slice(0, 6)}`,
        email_visible: usuario.email || tecnico.email || "â€”",
        telefono_visible: tecnico.telefono || usuario.telefono || "â€”",
        especialidad_visible: tecnico.especialidad || tecnico.cargo || "â€”",
        total_mantenimientos: asignados.length,
        activos: activos.length,
        finalizados: finalizados.length,
      };
    });
  }, [tecnicos, mantenimientos]);

  const equiposEnriquecidos = useMemo(() => {
    return equipos.map((equipo) => {
      const sede = sedesEnriquecidas.find((s) => sameId(s.id, equipo.sede_id));
      const empresa = empresas.find((e) => sameId(e.id, equipo.empresa_id));
      const mantEquipo = mantenimientos.filter((m) => sameId(m.equipo_id, equipo.id));

      return {
        ...equipo,
        sede_nombre: sede?.nombre || equipo.sede_nombre || "â€”",
        empresa_nombre: empresa?.nombre || sede?.empresa_nombre || equipo.empresa_nombre || "â€”",
        total_mantenimientos: mantEquipo.length,
      };
    });
  }, [equipos, empresas, sedesEnriquecidas, mantenimientos]);

  const mantenimientosEnriquecidos = useMemo(() => {
    return mantenimientos.map((m) => {
      const equipo = equiposEnriquecidos.find((e) => sameId(e.id, m.equipo_id));
      const tecnico = tecnicosEnriquecidos.find((t) => sameId(t.id, m.tecnico_id));

      return {
        ...m,
        estado_normalizado: normalizeEstado(m.estado),
        equipo_nombre: m.equipo_nombre || equipo?.nombre || "â€”",
        empresa_nombre: m.empresa_nombre || equipo?.empresa_nombre || "â€”",
        sede_nombre: m.sede_nombre || equipo?.sede_nombre || "â€”",
        tecnico_nombre: m.tecnico_nombre || tecnico?.nombre_visible || "â€”",
      };
    });
  }, [mantenimientos, equiposEnriquecidos, tecnicosEnriquecidos]);

  // =========================================================
  // MÉTRICAS EJECUTIVAS
  // =========================================================

  const metricas = useMemo(() => {
    const finalizados = mantenimientosEnriquecidos.filter((m) => m.estado_normalizado === "FINALIZADO").length;
    const activos = mantenimientosEnriquecidos.filter((m) => ESTADOS_ACTIVOS.includes(m.estado_normalizado)).length;
    const anulados = mantenimientosEnriquecidos.filter((m) => m.estado_normalizado === "ANULADO").length;
    const cumplimiento = mantenimientos.length === 0 ? 0 : Math.round((finalizados / mantenimientos.length) * 100);

    const hoy = startOfDay(new Date());
    const atrasados = mantenimientosEnriquecidos.filter((m) => {
      if (!m.fecha_programada) return false;
      if (ESTADOS_CERRADOS.includes(m.estado_normalizado)) return false;
      const fecha = startOfDay(new Date(m.fecha_programada));
      return !Number.isNaN(fecha.getTime()) && fecha < hoy;
    });

    const proximos7Dias = mantenimientosEnriquecidos.filter((m) => {
      if (!m.fecha_programada) return false;
      if (ESTADOS_CERRADOS.includes(m.estado_normalizado)) return false;
      const fecha = startOfDay(new Date(m.fecha_programada));
      if (Number.isNaN(fecha.getTime())) return false;
      const diff = Math.ceil((fecha - hoy) / (1000 * 60 * 60 * 24));
      return diff >= 0 && diff <= 7;
    });

    const criticos = equiposEnriquecidos.filter((e) =>
      ["ALTA", "CRITICA", "CRÃTICA"].includes(normalizeEstado(e.criticidad))
    );

    const fueraServicio = equiposEnriquecidos.filter((e) =>
      ["FUERA_DE_SERVICIO", "FUERA DE SERVICIO", "BAJA"].includes(normalizeEstado(e.estado))
    );

    const tecnicosActivos = tecnicosEnriquecidos.filter((t) => t.activo !== false).length;

    return {
      finalizados,
      activos,
      anulados,
      cumplimiento,
      atrasados,
      proximos7Dias,
      criticos,
      fueraServicio,
      tecnicosActivos,
    };
  }, [mantenimientos, mantenimientosEnriquecidos, equiposEnriquecidos, tecnicosEnriquecidos]);

  const saludOperativa = useMemo(() => {
    let score = 100;
    score -= Math.min(metricas.atrasados.length * 5, 35);
    score -= Math.min(metricas.fueraServicio.length * 4, 25);
    score -= Math.min(metricas.criticos.length * 2, 20);
    score += Math.min(metricas.cumplimiento * 0.1, 10);
    return Math.max(0, Math.min(100, Math.round(score)));
  }, [metricas]);

  const equiposPorEstado = useMemo(() => {
    const estados = {};
    equiposEnriquecidos.forEach((e) => {
      const estado = e.estado || "SIN ESTADO";
      estados[estado] = (estados[estado] || 0) + 1;
    });
    return Object.entries(estados).map(([name, value]) => ({ name, value }));
  }, [equiposEnriquecidos]);

  const mantenimientosPorEstado = useMemo(() => {
    const estados = {};
    mantenimientosEnriquecidos.forEach((m) => {
      const estado = m.estado || "SIN ESTADO";
      estados[estado] = (estados[estado] || 0) + 1;
    });
    return Object.entries(estados).map(([name, value]) => ({ name, value }));
  }, [mantenimientosEnriquecidos]);

  const mantenimientosPorMes = useMemo(() => {
    const meses = {};
    mantenimientosEnriquecidos.forEach((m) => {
      const fecha = m.fecha_programada || m.creado_en || m.created_at;
      if (!fecha) return;
      const d = new Date(fecha);
      if (Number.isNaN(d.getTime())) return;
      const key = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}`;
      meses[key] = (meses[key] || 0) + 1;
    });

    return Object.entries(meses)
      .sort(([a], [b]) => a.localeCompare(b))
      .slice(-8)
      .map(([mes, total]) => ({ mes, total }));
  }, [mantenimientosEnriquecidos]);

  const cargaTecnicos = useMemo(() => {
    return tecnicosEnriquecidos
      .filter((t) => t.total_mantenimientos > 0)
      .map((t) => ({ tecnico: shortName(t.nombre_visible), total: t.total_mantenimientos, activos: t.activos }))
      .sort((a, b) => b.total - a.total)
      .slice(0, 8);
  }, [tecnicosEnriquecidos]);

  const rankingSedes = useMemo(() => {
    return sedesEnriquecidas
      .map((s) => ({ sede: shortName(s.nombre), equipos: s.total_equipos, pendientes: s.pendientes }))
      .sort((a, b) => b.equipos - a.equipos)
      .slice(0, 7);
  }, [sedesEnriquecidas]);

  const datosVista = useMemo(
    () => ({
      empresas,
      sedes: sedesEnriquecidas,
      equipos: equiposEnriquecidos,
      mantenimientos: mantenimientosEnriquecidos,
      tecnicos: tecnicosEnriquecidos,
      atrasados: metricas.atrasados,
      proximos: metricas.proximos7Dias,
      criticos: metricas.criticos,
      fuera_servicio: metricas.fueraServicio,
    }),
    [
      empresas,
      sedesEnriquecidas,
      equiposEnriquecidos,
      mantenimientosEnriquecidos,
      tecnicosEnriquecidos,
      metricas,
    ]
  );

  const dataFiltrada = useMemo(() => {
    const base = datosVista[vista] || [];
    const q = busqueda.toLowerCase().trim();
    if (!q) return base;
    return base.filter((item) => JSON.stringify(item).toLowerCase().includes(q));
  }, [datosVista, vista, busqueda]);

  function cambiarVista(nuevaVista) {
    setVista(nuevaVista);
    setBusqueda("");
    setSedeSeleccionada(null);
  }

  function goTo(path) {
    navigate(path);
  }

  if (loading) {
    return (
      <div className="dadmin-pro-shell">
        <Sidebar user={user} onLogout={logout} />
        <main className="dadmin-pro-main">
          <DashboardSkeleton />
        </main>
      </div>
    );
  }

  return (
    <div className="dadmin-pro-shell">
      <Sidebar user={user} onLogout={logout} />

      <main className="dadmin-pro-main">
        <section className="dadmin-hero">
          <div className="dadmin-hero-copy">
                        <h1>Dashboard General</h1>
            <p>
              Monitorea empresas, sedes, equipos, mantenimientos, técnicos, alertas críticas
              desde una vista ejecutiva.
            </p>
          </div>

          <div className="dadmin-hero-actions">
            <button type="button" className="dadmin-btn ghost" onClick={() => cargarDashboard(false)}>
              <RefreshCcw size={16} className={refreshing ? "dadmin-spin" : ""} />
              {refreshing ? "Actualizando" : "Actualizar"}
            </button>
            <button type="button" className="dadmin-btn primary" onClick={() => goTo("/admin/mantenimientos")}>
              <Plus size={16} />
              Nuevo control
            </button>
          </div>
        </section>

        {error && (
          <div className="dadmin-warning-banner">
            <AlertTriangle size={17} />
            <span>{error}</span>
          </div>
        )}

        <section className="dadmin-executive-grid">
          <HealthCard score={saludOperativa} />

          <KpiCard title="Empresas" value={empresas.length} icon={<Building2 />} tone="blue" onClick={() => cambiarVista("empresas")} />
          <KpiCard title="Sedes" value={sedes.length} icon={<MapPin />} tone="cyan" onClick={() => cambiarVista("sedes")} />
          <KpiCard title="Equipos" value={equipos.length} icon={<MonitorCog />} tone="indigo" onClick={() => cambiarVista("equipos")} />
          <KpiCard title="Mantenimientos" value={mantenimientos.length} icon={<Wrench />} tone="violet" onClick={() => cambiarVista("mantenimientos")} />
          <KpiCard title="Técnicos activos" value={metricas.tecnicosActivos} icon={<UserCog />} tone="green" onClick={() => cambiarVista("tecnicos")} />
        </section>

        <section className="dadmin-alert-grid">
          <AlertTile title="Atrasados" value={metricas.atrasados.length} icon={<CalendarClock />} tone="warning" onClick={() => cambiarVista("atrasados")} />
          <AlertTile title="Próximos 7 días" value={metricas.proximos7Dias.length} icon={<ClipboardList />} tone="info" onClick={() => cambiarVista("proximos")} />
          <AlertTile title="Equipos críticos" value={metricas.criticos.length} icon={<ShieldAlert />} tone="danger" onClick={() => cambiarVista("criticos")} />
          <AlertTile title="Fuera de servicio" value={metricas.fueraServicio.length} icon={<AlertTriangle />} tone="danger" onClick={() => cambiarVista("fuera_servicio")} />
          <AlertTile title="Finalizados" value={metricas.finalizados} icon={<CheckCircle2 />} tone="success" onClick={() => cambiarVista("mantenimientos")} />
        </section>

        <section className="dadmin-quick-actions">
          <QuickAction icon={<Building2 />} title="Empresas" text="Crear o administrar clientes" onClick={() => goTo("/admin/empresas")} />
          <QuickAction icon={<MapPin />} title="Sedes" text="Ubicaciones por empresa" onClick={() => goTo("/admin/sedes")} />
          <QuickAction icon={<MonitorCog />} title="Inventario" text="Equipos y hoja de vida" onClick={() => goTo("/admin/equipos")} />
          <QuickAction icon={<Wrench />} title="Mantenimientos" text="Programar y asignar" onClick={() => goTo("/admin/mantenimientos")} />
          <QuickAction icon={<BarChart3 />} title="Reportes" text="Indicadores y exportación" onClick={() => goTo("/admin/reportes")} />
        </section>

        <section className="dadmin-charts-grid">
          <ChartCard title="Mantenimientos por mes" subtitle="Tendencia operacional reciente">
            {mantenimientosPorMes.length ? (
              <ResponsiveContainer width="100%" height={260}>
                <AreaChart data={mantenimientosPorMes}>
                  <defs>
                    <linearGradient id="mantGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#2563eb" stopOpacity={0.35} />
                      <stop offset="95%" stopColor="#2563eb" stopOpacity={0.02} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                  <XAxis dataKey="mes" tick={{ fontSize: 11 }} />
                  <YAxis allowDecimals={false} tick={{ fontSize: 11 }} />
                  <Tooltip />
                  <Area type="monotone" dataKey="total" stroke="#2563eb" fill="url(#mantGradient)" strokeWidth={3} />
                </AreaChart>
              </ResponsiveContainer>
            ) : (
              <EmptyState text="Sin datos suficientes para la tendencia mensual." />
            )}
          </ChartCard>

          <ChartCard title="Equipos por estado" subtitle="Distribución del inventario">
            {equiposPorEstado.length ? (
              <ResponsiveContainer width="100%" height={260}>
                <PieChart>
                  <Pie data={equiposPorEstado} dataKey="value" nameKey="name" outerRadius={82} innerRadius={44} paddingAngle={3}>
                    {equiposPorEstado.map((_, index) => (
                      <Cell key={index} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <EmptyState text="Sin equipos registrados." />
            )}
          </ChartCard>
        </section>

        <section className="dadmin-charts-grid three">
          <ChartCard title="Estados de mantenimiento" subtitle="Control por ciclo operativo">
            {mantenimientosPorEstado.length ? (
              <ResponsiveContainer width="100%" height={235}>
                <BarChart data={mantenimientosPorEstado}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                  <XAxis dataKey="name" tick={{ fontSize: 10 }} />
                  <YAxis allowDecimals={false} tick={{ fontSize: 11 }} />
                  <Tooltip />
                  <Bar dataKey="value" radius={[10, 10, 0, 0]} fill="#06b6d4" />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <EmptyState text="Sin mantenimientos registrados." />
            )}
          </ChartCard>

          <ChartCard title="Carga por técnico" subtitle="Top técnicos por asignaciones">
            {cargaTecnicos.length ? (
              <ResponsiveContainer width="100%" height={235}>
                <BarChart data={cargaTecnicos}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                  <XAxis dataKey="tecnico" tick={{ fontSize: 10 }} />
                  <YAxis allowDecimals={false} tick={{ fontSize: 11 }} />
                  <Tooltip />
                  <Bar dataKey="total" radius={[10, 10, 0, 0]} fill="#7c3aed" />
                  <Bar dataKey="activos" radius={[10, 10, 0, 0]} fill="#22c55e" />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <EmptyState text="Sin asignaciones a técnicos." />
            )}
          </ChartCard>

          <ChartCard title="Sedes con más equipos" subtitle="Capacidad instalada">
            {rankingSedes.length ? (
              <ResponsiveContainer width="100%" height={235}>
                <BarChart data={rankingSedes} layout="vertical" margin={{ left: 18, right: 10 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                  <XAxis type="number" allowDecimals={false} tick={{ fontSize: 11 }} />
                  <YAxis type="category" dataKey="sede" tick={{ fontSize: 10 }} width={80} />
                  <Tooltip />
                  <Bar dataKey="equipos" radius={[0, 10, 10, 0]} fill="#2563eb" />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <EmptyState text="Sin sedes registradas." />
            )}
          </ChartCard>
        </section>

        <section className="dadmin-table-panel">
          <div className="dadmin-panel-head">
            <div>
              <span className="dadmin-section-tag">
                <Activity size={15} />
                Vista rÃ¡pida inteligente
              </span>
              <h2>{labelVista(vista)}</h2>
              <p>Consulta, filtra y navega registros operativos sin salir del dashboard.</p>
            </div>

            <div className="dadmin-panel-actions">
              <button type="button" className="dadmin-mini-btn" onClick={() => cambiarVista("mantenimientos")}>
                <LayoutDashboard size={15} />
                Resumen operativo
              </button>
              <button type="button" className="dadmin-mini-btn" onClick={() => window.print()}>
                <Download size={15} />
                Imprimir
              </button>
            </div>
          </div>

          <div className="dadmin-search-row">
            <div className="dadmin-search-box">
              <Search size={17} />
              <input
                value={busqueda}
                onChange={(e) => setBusqueda(e.target.value)}
                placeholder={`Buscar en ${labelVista(vista).toLowerCase()}...`}
              />
            </div>
            <span>{dataFiltrada.length} registro(s)</span>
          </div>

          <div className={vista === "sedes" ? "dadmin-master-detail" : ""}>
            <DataTable
              tipo={vista}
              data={dataFiltrada}
              paginaActual={paginaActual}
              setPaginaActual={setPaginaActual}
              registrosPorPagina={registrosPorPagina}
              setRegistrosPorPagina={setRegistrosPorPagina}
              onRowClick={(item) => {
                if (vista === "sedes") setSedeSeleccionada(item);
              }}
            />

            {vista === "sedes" && sedeSeleccionada && (
              <SedeDetalle sede={sedeSeleccionada} onClose={() => setSedeSeleccionada(null)} />
            )}
          </div>
        </section>
      </main>
    </div>
  );
}

// ============================================================
// COMPONENTES VISUALES
// ============================================================

function KpiCard({ title, value, icon, tone, onClick }) {
  return (
    <button type="button" className={`dadmin-kpi ${tone}`} onClick={onClick}>
      <div className="dadmin-kpi-row"><span>{title}</span><strong>{value}</strong></div>
      <div className="dadmin-kpi-icon">{icon}</div>
      <ArrowRight className="dadmin-kpi-arrow" size={17} />
    </button>
  );
}

function HealthCard({ score }) {
  const estado = score >= 80 ? "Excelente" : score >= 60 ? "Controlado" : score >= 40 ? "Atención" : "Crítico";

  return (
    <article className="dadmin-health-card">
      <div className="dadmin-health-top">
        <div>
          <span>Salud operativa</span>
          <strong>{estado}</strong>
        </div>
        <Gauge size={26} />
      </div>

      <div className="dadmin-health-score">
        <div className="dadmin-health-ring" style={{ "--score": `${score}%` }}>
          <b>{score}</b>
        </div>
        <div>
          
        </div>
      </div>
    </article>
  );
}

function AlertTile({ title, value, icon, tone, onClick }) {
  return (
    <button type="button" className={`dadmin-alert ${tone}`} onClick={onClick}>
      <div>{icon}</div>
      <span>{title}</span>
      <strong>{value}</strong>
    </button>
  );
}

function QuickAction({ icon, title, text, onClick }) {
  return (
    <button type="button" className="dadmin-action" onClick={onClick}>
      <div>{icon}</div>
      <span>{title}</span>
      <p>{text}</p>
    </button>
  );
}

function ChartCard({ title, subtitle, children }) {
  return (
    <article className="dadmin-chart-card">
      <div className="dadmin-chart-head">
        <div>
          <h3>{title}</h3>
          <p>{subtitle}</p>
        </div>
      </div>
      {children}
    </article>
  );
}

function EmptyState({ text }) {
  return (
    <div className="dadmin-empty">
      <Sparkles size={20} />
      <span>{text}</span>
    </div>
  );
}

function DashboardSkeleton() {
  return (
    <div className="dadmin-skeleton-page">
      <div className="dadmin-skeleton hero" />
      <div className="dadmin-skeleton-grid">
        {Array.from({ length: 6 }).map((_, i) => (
          <div key={i} className="dadmin-skeleton card" />
        ))}
      </div>
      <div className="dadmin-skeleton chart" />
      <div className="dadmin-skeleton table" />
    </div>
  );
}

function DataTable({
  tipo,
  data,
  onRowClick,
  paginaActual,
  setPaginaActual,
  registrosPorPagina,
  setRegistrosPorPagina,
}) {
  const columnsByType = {
    empresas: ["nombre", "nit", "telefono", "email", "estado"],
    sedes: ["nombre", "empresa_nombre", "direccion", "telefono", "total_equipos", "total_mantenimientos"],
    equipos: ["nombre", "empresa_nombre", "sede_nombre", "estado", "criticidad", "total_mantenimientos"],
    mantenimientos: ["equipo_nombre", "empresa_nombre", "sede_nombre", "tipo", "estado", "fecha_programada", "tecnico_nombre"],
    tecnicos: ["nombre_visible", "email_visible", "telefono_visible", "especialidad_visible", "total_mantenimientos", "activos"],
    atrasados: ["equipo_nombre", "empresa_nombre", "sede_nombre", "tipo", "estado", "fecha_programada", "tecnico_nombre"],
    proximos: ["equipo_nombre", "empresa_nombre", "sede_nombre", "tipo", "estado", "fecha_programada", "tecnico_nombre"],
    criticos: ["nombre", "empresa_nombre", "sede_nombre", "estado", "criticidad"],
    fuera_servicio: ["nombre", "empresa_nombre", "sede_nombre", "estado", "criticidad"],
  };

  if (!data.length) return <EmptyState text="No hay registros para mostrar en esta vista." />;

  const columns = columnsByType[tipo] || Object.keys(data[0]).slice(0, 7);
  const totalRegistros = data.length;
  const totalPaginas = Math.max(1, Math.ceil(totalRegistros / registrosPorPagina));
  const paginaSegura = Math.min(Math.max(paginaActual, 1), totalPaginas);
  const inicio = (paginaSegura - 1) * registrosPorPagina;
  const fin = inicio + registrosPorPagina;
  const dataPaginada = data.slice(inicio, fin);

  return (
    <div className="dadmin-table-section">
      <div className="dadmin-table-toolbar">
        <div>
          <strong>Listado SaaS PRO</strong>
          <span>
            Mostrando {inicio + 1} - {Math.min(fin, totalRegistros)} de {totalRegistros}
          </span>
        </div>

        <label>
          Filas
          <select value={registrosPorPagina} onChange={(e) => setRegistrosPorPagina(Number(e.target.value))}>
            <option value={10}>10</option>
            <option value={15}>15</option>
            <option value={25}>25</option>
            <option value={50}>50</option>
          </select>
        </label>
      </div>

      <div className="dadmin-table-wrap">
        <table className="dadmin-table">
          <thead>
            <tr>
              {columns.map((column) => (
                <th key={column}>{column.replaceAll("_", " ")}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {dataPaginada.map((item, index) => (
              <tr
                key={item.id || `${tipo}-${inicio + index}`}
                className={onRowClick ? "clickable" : ""}
                onClick={() => onRowClick && onRowClick(item)}
              >
                {columns.map((column) => (
                  <td key={column}>{renderCell(column, item[column])}</td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {totalPaginas > 1 && (
        <div className="dadmin-pagination">
          <button type="button" disabled={paginaSegura === 1} onClick={() => setPaginaActual(1)}>
            Â« Primero
          </button>
          <button type="button" disabled={paginaSegura === 1} onClick={() => setPaginaActual((p) => Math.max(1, p - 1))}>
            â€¹ Anterior
          </button>
          <span>
            PÃ¡gina <b>{paginaSegura}</b> de <b>{totalPaginas}</b>
          </span>
          <button type="button" disabled={paginaSegura === totalPaginas} onClick={() => setPaginaActual((p) => Math.min(totalPaginas, p + 1))}>
            Siguiente â€º
          </button>
          <button type="button" disabled={paginaSegura === totalPaginas} onClick={() => setPaginaActual(totalPaginas)}>
            Ãšltimo Â»
          </button>
        </div>
      )}
    </div>
  );
}

function SedeDetalle({ sede, onClose }) {
  return (
    <aside className="dadmin-side-detail">
      <div className="dadmin-side-head">
        <div>
          <p>Detalle de sede</p>
          <h3>{sede.nombre}</h3>
        </div>
        <button type="button" onClick={onClose}>
          <X size={16} />
        </button>
      </div>

      <div className="dadmin-side-info">
        <InfoLine icon={<Factory size={15} />} label="Empresa" value={sede.empresa_nombre} />
        <InfoLine icon={<MapPinned size={15} />} label="DirecciÃ³n" value={sede.direccion} />
        <InfoLine icon={<Phone size={15} />} label="TelÃ©fono" value={sede.telefono} />
        <InfoLine icon={<Mail size={15} />} label="NIT empresa" value={sede.empresa_nit} />
      </div>

      <div className="dadmin-side-stats">
        <div><span>Equipos</span><strong>{sede.total_equipos}</strong></div>
        <div><span>Mantenimientos</span><strong>{sede.total_mantenimientos}</strong></div>
        <div><span>Pendientes</span><strong>{sede.pendientes}</strong></div>
        <div><span>Finalizados</span><strong>{sede.finalizados}</strong></div>
      </div>

      <MiniList
        title="Equipos de la sede"
        icon={<MonitorCog size={15} />}
        items={(sede.equipos || []).slice(0, 8).map((e) => ({ title: e.nombre, text: `${e.estado || "Sin estado"} Â· ${e.criticidad || "Sin criticidad"}` }))}
      />
      <MiniList
        title="Ãšltimos mantenimientos"
        icon={<ClipboardList size={15} />}
        items={(sede.mantenimientos || []).slice(0, 6).map((m) => ({ title: m.tipo, text: `${m.estado || "Sin estado"} Â· ${formatValue(m.fecha_programada)}` }))}
      />
    </aside>
  );
}

function InfoLine({ icon, label, value }) {
  return (
    <div className="dadmin-info-line">
      {icon}
      <div>
        <span>{label}</span>
        <strong>{formatValue(value)}</strong>
      </div>
    </div>
  );
}

function MiniList({ title, icon, items }) {
  return (
    <div className="dadmin-mini-list">
      <h4>{icon}{title}</h4>
      {items.length ? items.map((item, index) => (
        <div key={`${item.title}-${index}`} className="dadmin-mini-item">
          <strong>{item.title}</strong>
          <span>{item.text}</span>
        </div>
      )) : <p>Sin registros.</p>}
    </div>
  );
}

// ============================================================
// HELPERS
// ============================================================

function sameId(a, b) {
  return String(a ?? "") === String(b ?? "");
}

function normalizeEstado(value) {
  return String(value || "")
    .trim()
    .toUpperCase()
    .replaceAll("-", "_")
    .replaceAll(" ", "_");
}

function startOfDay(date) {
  const d = new Date(date);
  d.setHours(0, 0, 0, 0);
  return d;
}

function shortName(value) {
  const text = String(value || "â€”");
  return text.length > 18 ? `${text.slice(0, 18)}â€¦` : text;
}

function labelVista(vista) {
  const labels = {
    empresas: "Empresas",
    sedes: "Sedes",
    equipos: "Equipos",
    mantenimientos: "Mantenimientos",
    tecnicos: "Técnicos",
    atrasados: "Mantenimientos atrasados",
    proximos: "Próximos 7 días",
    criticos: "Equipos críticos",
    fuera_servicio: "Equipos fuera de servicio",
  };
  return labels[vista] || "Vista rÃ¡pida";
}

function renderCell(column, value) {
  if (["estado", "criticidad", "estado_normalizado"].includes(column)) {
    return <span className={`dadmin-status ${normalizeEstado(value).toLowerCase()}`}>{formatValue(value)}</span>;
  }
  return formatValue(value);
}

function formatValue(value) {
  if (value === null || value === undefined || value === "") return "â€”";
  if (typeof value === "boolean") return value ? "SÃ­" : "No";

  if (typeof value === "string" && (value.includes("T") || /^\d{4}-\d{2}-\d{2}/.test(value))) {
    const d = new Date(value);
    if (!Number.isNaN(d.getTime())) return d.toLocaleDateString("es-CO");
  }

  return String(value);
}
