// ============================================================
// PÁGINA: Notificaciones PRO Admin
// Archivo: frontend/src/pages/admin/NotificacionesPage.jsx
// Fase 29 - Notificaciones y Alertas PRO
// ============================================================
// Funciones:
// - Lista notificaciones del sistema.
// - Filtra por estado, prioridad y tipo.
// - Genera alertas automáticas desde backend.
// - Permite marcar notificaciones como leídas.
// - Mantiene estilo SaaS PRO institucional.
// ============================================================

import { useEffect, useMemo, useState } from "react";
import {
  Bell,
  BellRing,
  CheckCircle2,
  RefreshCw,
  Trash2,
  AlertTriangle,
  Info,
  ShieldAlert,
  Search,
} from "lucide-react";

import API from "../../api/axios";
import Sidebar from "../../components/Sidebar";
import "../../styles/notificaciones.css";

// ============================================================
// Helpers visuales
// ============================================================

function getCurrentUser() {
  try {
    return JSON.parse(localStorage.getItem("user"));
  } catch {
    return null;
  }
}

function formatearFecha(valor) {
  if (!valor) return "Sin fecha";
  try {
    return new Date(valor).toLocaleString("es-CO", {
      year: "numeric",
      month: "2-digit",
      day: "2-digit",
      hour: "2-digit",
      minute: "2-digit",
    });
  } catch {
    return valor;
  }
}

function iconoPorTipo(tipo = "INFO") {
  const tipoUpper = String(tipo).toUpperCase();

  if (tipoUpper.includes("VENCIDO")) return <ShieldAlert size={18} />;
  if (tipoUpper.includes("CRITICO")) return <AlertTriangle size={18} />;
  if (tipoUpper.includes("PROXIMO")) return <BellRing size={18} />;
  return <Info size={18} />;
}

// ============================================================
// Componente principal
// ============================================================

export default function NotificacionesPage() {
  const [notificaciones, setNotificaciones] = useState([]);
  const [resumen, setResumen] = useState({ total: 0, no_leidas: 0, alta: 0, media: 0, baja: 0 });
  const [cargando, setCargando] = useState(false);
  const [mensaje, setMensaje] = useState("");

  // Filtros UI
  const [busqueda, setBusqueda] = useState("");
  const [filtroLeida, setFiltroLeida] = useState("TODAS");
  const [filtroPrioridad, setFiltroPrioridad] = useState("TODAS");
  const [filtroTipo, setFiltroTipo] = useState("TODAS");

  const user = getCurrentUser();

  // ==========================================================
  // Cargar resumen y listado
  // ==========================================================
  const cargarDatos = async () => {
    setCargando(true);
    setMensaje("");

    try {
      const params = new URLSearchParams();
      params.append("rol_destino", "ADMIN");
      params.append("limite", "300");

      if (filtroLeida !== "TODAS") {
        params.append("leida", filtroLeida === "LEIDAS" ? "true" : "false");
      }

      if (filtroPrioridad !== "TODAS") {
        params.append("prioridad", filtroPrioridad);
      }

      if (filtroTipo !== "TODAS") {
        params.append("tipo", filtroTipo);
      }

      const [notificacionesResp, resumenResp] = await Promise.all([
        API.get(`/notificaciones/?${params.toString()}`),
        API.get("/notificaciones/resumen?rol_destino=ADMIN"),
      ]);

      setNotificaciones(notificacionesResp.data || []);
      setResumen(resumenResp.data || { total: 0, no_leidas: 0, alta: 0, media: 0, baja: 0 });
    } catch (error) {
      console.error("Error cargando notificaciones", error);
      setMensaje("No fue posible cargar las notificaciones. Verifica backend y ruta /notificaciones.");
    } finally {
      setCargando(false);
    }
  };

  useEffect(() => {
    const timer = window.setTimeout(() => cargarDatos(), 0);
    return () => window.clearTimeout(timer);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [filtroLeida, filtroPrioridad, filtroTipo]);

  // ==========================================================
  // Acciones
  // ==========================================================
  const generarAlertas = async () => {
    setCargando(true);
    setMensaje("");

    try {
      const resp = await API.post("/notificaciones/generar-alertas");
      setMensaje(`${resp.data?.mensaje || "Alertas generadas"}. Nuevas: ${resp.data?.creadas ?? 0}`);
      await cargarDatos();
    } catch (error) {
      console.error("Error generando alertas", error);
      setMensaje("No fue posible generar alertas automáticas.");
    } finally {
      setCargando(false);
    }
  };

  const marcarLeida = async (id) => {
    try {
      await API.put(`/notificaciones/${id}/leer`);
      await cargarDatos();
    } catch (error) {
      console.error("Error marcando notificación como leída", error);
      setMensaje("No fue posible marcar la notificación como leída.");
    }
  };

  const marcarTodas = async () => {
    try {
      await API.put("/notificaciones/leer-todas?rol_destino=ADMIN");
      setMensaje("Todas las notificaciones fueron marcadas como leídas.");
      await cargarDatos();
    } catch (error) {
      console.error("Error marcando todas como leídas", error);
      setMensaje("No fue posible marcar todas como leídas.");
    }
  };

  const eliminarNotificacion = async (id) => {
    const confirmar = window.confirm("¿Deseas eliminar esta notificación?");
    if (!confirmar) return;

    try {
      await API.delete(`/notificaciones/${id}`);
      await cargarDatos();
    } catch (error) {
      console.error("Error eliminando notificación", error);
      setMensaje("No fue posible eliminar la notificación.");
    }
  };

  // ==========================================================
  // Filtro local por búsqueda
  // ==========================================================
  const notificacionesFiltradas = useMemo(() => {
    const texto = busqueda.trim().toLowerCase();
    if (!texto) return notificaciones;

    return notificaciones.filter((item) => {
      return [item.titulo, item.mensaje, item.tipo, item.prioridad]
        .filter(Boolean)
        .join(" ")
        .toLowerCase()
        .includes(texto);
    });
  }, [notificaciones, busqueda]);

  const tiposDisponibles = useMemo(() => {
    const setTipos = new Set(notificaciones.map((n) => n.tipo).filter(Boolean));
    return Array.from(setTipos);
  }, [notificaciones]);

  // ==========================================================
  // Render
  // ==========================================================
  return (
    <div className="sga-layout-pro">
      <Sidebar user={user} />

      <main className="notificaciones-main">
        <section className="notificaciones-header">
          <div>
            <span className="notificaciones-eyebrow">Fase 29 · Centro de alertas</span>
            <h1>Notificaciones PRO</h1>
            <p>
              Controla alertas de mantenimientos vencidos, próximos, equipos críticos
              y eventos importantes del sistema.
            </p>
          </div>

          <div className="notificaciones-actions">
            <button className="btn-secundario" onClick={cargarDatos} disabled={cargando}>
              <RefreshCw size={17} />
              Actualizar
            </button>

            <button className="btn-principal" onClick={generarAlertas} disabled={cargando}>
              <BellRing size={17} />
              Generar alertas
            </button>
          </div>
        </section>

        {mensaje && <div className="notificaciones-message">{mensaje}</div>}

        <section className="notificaciones-kpis">
          <article className="noti-kpi">
            <Bell size={21} />
            <div>
              <strong>{resumen.total}</strong>
              <span>Total</span>
            </div>
          </article>

          <article className="noti-kpi pendiente">
            <BellRing size={21} />
            <div>
              <strong>{resumen.no_leidas}</strong>
              <span>No leídas</span>
            </div>
          </article>

          <article className="noti-kpi alta">
            <ShieldAlert size={21} />
            <div>
              <strong>{resumen.alta}</strong>
              <span>Alta prioridad</span>
            </div>
          </article>

          <article className="noti-kpi media">
            <AlertTriangle size={21} />
            <div>
              <strong>{resumen.media}</strong>
              <span>Prioridad media</span>
            </div>
          </article>
        </section>

        <section className="notificaciones-panel">
          <div className="notificaciones-toolbar">
            <div className="noti-search">
              <Search size={18} />
              <input
                value={busqueda}
                onChange={(e) => setBusqueda(e.target.value)}
                placeholder="Buscar por título, mensaje, tipo o prioridad..."
              />
            </div>

            <select value={filtroLeida} onChange={(e) => setFiltroLeida(e.target.value)}>
              <option value="TODAS">Todas</option>
              <option value="NO_LEIDAS">No leídas</option>
              <option value="LEIDAS">Leídas</option>
            </select>

            <select value={filtroPrioridad} onChange={(e) => setFiltroPrioridad(e.target.value)}>
              <option value="TODAS">Todas las prioridades</option>
              <option value="ALTA">Alta</option>
              <option value="MEDIA">Media</option>
              <option value="BAJA">Baja</option>
            </select>

            <select value={filtroTipo} onChange={(e) => setFiltroTipo(e.target.value)}>
              <option value="TODAS">Todos los tipos</option>
              {tiposDisponibles.map((tipo) => (
                <option key={tipo} value={tipo}>{tipo}</option>
              ))}
            </select>

            <button className="btn-link" onClick={marcarTodas}>
              <CheckCircle2 size={16} />
              Marcar todas
            </button>
          </div>

          <div className="notificaciones-lista">
            {cargando && <div className="notificaciones-empty">Cargando notificaciones...</div>}

            {!cargando && notificacionesFiltradas.length === 0 && (
              <div className="notificaciones-empty">
                No hay notificaciones para los filtros seleccionados.
              </div>
            )}

            {!cargando && notificacionesFiltradas.map((item) => (
              <article
                key={item.id}
                className={`notificacion-card ${item.leida ? "leida" : "no-leida"} prioridad-${String(item.prioridad).toLowerCase()}`}
              >
                <div className="notificacion-icono">
                  {iconoPorTipo(item.tipo)}
                </div>

                <div className="notificacion-body">
                  <div className="notificacion-top">
                    <div>
                      <h3>{item.titulo}</h3>
                      <p>{item.mensaje || "Sin mensaje adicional."}</p>
                    </div>

                    <span className={`badge-prioridad ${String(item.prioridad).toLowerCase()}`}>
                      {item.prioridad}
                    </span>
                  </div>

                  <div className="notificacion-meta">
                    <span>Tipo: {item.tipo}</span>
                    <span>Creada: {formatearFecha(item.creado_en)}</span>
                    {item.mantenimiento_id && <span>Mantenimiento: #{item.mantenimiento_id}</span>}
                    {item.equipo_id && <span>Equipo: #{item.equipo_id}</span>}
                  </div>
                </div>

                <div className="notificacion-actions">
                  {!item.leida && (
                    <button title="Marcar como leída" onClick={() => marcarLeida(item.id)}>
                      <CheckCircle2 size={17} />
                    </button>
                  )}

                  {item.enlace && (
                    <button title="Abrir enlace" onClick={() => window.location.href = item.enlace}>
                      <Bell size={17} />
                    </button>
                  )}

                  <button title="Eliminar" onClick={() => eliminarNotificacion(item.id)}>
                    <Trash2 size={17} />
                  </button>
                </div>
              </article>
            ))}
          </div>
        </section>
      </main>
    </div>
  );
}
