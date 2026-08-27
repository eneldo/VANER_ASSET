// ============================================================
// ÓRDENES DE MANTENIMIENTO - Ejecución de intervenciones
// Gestiona cada intervención concreta: solicitud, asignación,
// ejecución, repuestos, evidencias, costos y cierre.
// ============================================================

import { useCallback, useEffect, useState } from "react";
import {
  ClipboardList, Search, Eye, RefreshCw, ChevronLeft, ChevronRight,
  X, UserPlus, CheckCircle2, AlertTriangle, Wrench, Clock,
} from "lucide-react";

import AdminLayout from "./AdminLayout";
import API from "../../api/axios";
import { showToast } from "../../utils/toast";
import { construirEtiquetaEquipo } from "./mantenimientosEquipoUtils";
import "../../styles/maintenance-wizard.css";
import "./MantenimientosPage.css";

const ESTADOS = {
  PROGRAMADO: { label: "Programado", className: "badge-blue", icon: Clock },
  ASIGNADO: { label: "Asignado", className: "badge-green", icon: UserPlus },
  EN_PROCESO: { label: "En proceso", className: "badge-orange", icon: Wrench },
  PAUSADO: { label: "Pausado", className: "badge-yellow", icon: AlertTriangle },
  FINALIZADO: { label: "Finalizado", className: "badge-green", icon: CheckCircle2 },
  ANULADO: { label: "Anulado", className: "badge-red", icon: X },
};

const FILTROS_ESTADO = [
  { value: "", label: "Todos" },
  { value: "PROGRAMADO", label: "Programados" },
  { value: "ASIGNADO", label: "Asignados" },
  { value: "EN_PROCESO", label: "En proceso" },
  { value: "PAUSADO", label: "Pausados" },
  { value: "FINALIZADO", label: "Finalizados" },
];

export default function OrdenesMantenimientoPage() {
  const [ordenes, setOrdenes] = useState([]);
  const [equipos, setEquipos] = useState([]);
  const [tecnicos, setTecnicos] = useState([]);
  const [sedes, setSedes] = useState([]);
  const [loading, setLoading] = useState(false);
  const [filtroEstado, setFiltroEstado] = useState("EN_PROCESO");
  const [busqueda, setBusqueda] = useState("");
  const [pagina, setPagina] = useState(1);
  const [totalRegistros, setTotalRegistros] = useState(0);
  const [detalle, setDetalle] = useState(null);
  const porPagina = 20;

  useEffect(() => { cargarDatos(); }, []); // eslint-disable-line react-hooks/exhaustive-deps
  useEffect(() => { cargarOrdenes(); }, [pagina, filtroEstado]); // eslint-disable-line react-hooks/exhaustive-deps

  async function cargarDatos() {
    try {
      setLoading(true);
      const [resEq, resTec, resSedes] = await Promise.all([
        API.get("/equipos/"),
        API.get("/tecnicos/"),
        API.get("/sedes/"),
      ]);
      setEquipos(resEq.data || []);
      setTecnicos(resTec.data || []);
      setSedes(resSedes.data || []);
      await cargarOrdenes();
    } catch (err) {
      console.error("Error cargando datos:", err);
      showToast("Error cargando datos", "error");
    } finally {
      setLoading(false);
    }
  }

  async function cargarOrdenes() {
    try {
      setLoading(true);
      const params = { page: pagina, per_page: porPagina };
      if (filtroEstado) params.estado = filtroEstado;
      if (busqueda.trim()) params.buscar = busqueda.trim();
      const res = await API.get("/mantenimientos/", { params });
      const data = res.data;
      if (data?.items) {
        setOrdenes(data.items);
        setTotalRegistros(data.total);
      } else {
        setOrdenes(Array.isArray(data) ? data : []);
        setTotalRegistros(Array.isArray(data) ? data.length : 0);
      }
    } catch (err) {
      console.error("Error cargando órdenes:", err);
    } finally {
      setLoading(false);
    }
  }

  const asignarTecnico = async (orden) => {
    const tecnicosDisp = tecnicos.filter((t) => t.activo !== false);
    if (tecnicosDisp.length === 0) {
      showToast("No hay técnicos disponibles", "warning");
      return;
    }
    const lista = tecnicosDisp.map((t, i) => {
      const nombre = t.usuario?.nombre_completo || t.nombre_completo || `Técnico ${i + 1}`;
      return `${i + 1}. ${nombre}`;
    }).join("\n");
    const idx = window.prompt(`Asignar técnico (ingresa número):\n\n${lista}`);
    if (idx === null) return;
    const seleccion = tecnicosDisp[Number(idx) - 1];
    if (!seleccion) {
      showToast("Selección inválida", "warning");
      return;
    }
    try {
      await API.patch(`/mantenimientos/${orden.id}/asignar-tecnico`, {
        tecnico_id: seleccion.id,
        observacion: "Técnico asignado desde Órdenes de Mantenimiento.",
        creado_por: "Administrador",
      });
      showToast("Técnico asignado correctamente", "success");
      await cargarOrdenes();
    } catch (err) {
      showToast(err?.response?.data?.detail || "No se pudo asignar", "error");
    }
  };

  const cambiarEstado = async (orden, nuevoEstado) => {
    const confirmaciones = {
      EN_PROCESO: "¿Iniciar ejecución de esta orden?",
      PAUSADO: "¿Pausar esta orden?",
      FINALIZADO: "¿Marcar esta orden como finalizada?",
    };
    if (!window.confirm(confirmaciones[nuevoEstado] || `Cambiar estado a ${nuevoEstado}?`)) return;
    try {
      await API.patch(`/mantenimientos/${orden.id}/cambiar-estado`, {
        estado_nuevo: nuevoEstado,
        observacion: `Estado cambiado a ${nuevoEstado} desde Órdenes.`,
        creado_por: "Administrador",
      });
      showToast(`Orden ${nuevoEstado.toLowerCase()}`, "success");
      setDetalle(null);
      await cargarOrdenes();
    } catch (err) {
      showToast(err?.response?.data?.detail || "No se pudo cambiar estado", "error");
    }
  };

  const getEquipo = useCallback((id, fallback = "") => {
    const eq = equipos.find((e) => String(e.id) === String(id));
    return eq ? construirEtiquetaEquipo(eq) : fallback || "—";
  }, [equipos]);

  const getTecnico = useCallback((id) => {
    const t = tecnicos.find((tc) => String(tc.id) === String(id));
    if (!t) return "Sin asignar";
    return t.usuario?.nombre_completo || t.nombre_completo || t.nombre || `Técnico`;
  }, [tecnicos]);

  const getSede = useCallback((id) => {
    return sedes.find((s) => String(s.id) === String(id))?.nombre || "—";
  }, [sedes]);

  const formatearFecha = (v) => {
    if (!v) return "—";
    const d = new Date(v);
    return Number.isNaN(d.getTime()) ? v : d.toLocaleDateString("es-CO", { day: "2-digit", month: "short", year: "numeric" });
  };

  const totalPaginas = Math.max(1, Math.ceil(totalRegistros / porPagina));
  const ordenConEquipo = detalle ? equipos.find((e) => String(e.id) === String(detalle.equipo_id)) : null;

  return (
    <AdminLayout>
      <div className="mant-page">
        <div className="sga-module-hero">
          <div className="sga-module-hero__icon">
            <ClipboardList size={24} />
          </div>
          <div className="sga-module-hero__text">
            <span>Operaciones</span>
            <h1>Órdenes de Mantenimiento</h1>
            <p>Gestiona cada intervención: solicitud, asignación, ejecución, repuestos, evidencias, costos y cierre.</p>
          </div>
          <div className="sga-module-hero__actions">
            <button className="sga-btn sga-btn--secondary" onClick={() => window.location.href = "/admin/dashboard"}>
              <ChevronLeft size={16} /> Dashboard
            </button>
          </div>
        </div>

        <div className="mant-pro-layout">
          <section className="mant-card mant-list-card">
            <div className="mant-section-header">
              <div>
                <h2>Órdenes activas</h2>
                <p>Intervenciones en curso, asignadas o pendientes de ejecución.</p>
              </div>
              <span className="mant-counter">{totalRegistros} órdenes</span>
            </div>

            <div className="mant-filters-row">
              <div className="mant-filter-chips">
                {FILTROS_ESTADO.map((f) => (
                  <button
                    key={f.value}
                    className={`mant-chip ${filtroEstado === f.value ? "active" : ""}`}
                    onClick={() => { setFiltroEstado(f.value); setPagina(1); }}
                  >
                    {f.label}
                  </button>
                ))}
              </div>
              <div className="mant-search-box">
                <Search size={16} />
                <input
                  placeholder="Buscar por equipo, código, técnico..."
                  value={busqueda}
                  onChange={(e) => { setBusqueda(e.target.value); setPagina(1); }}
                  onKeyDown={(e) => { if (e.key === "Enter") cargarOrdenes(); }}
                />
              </div>
              <button className="mant-reload-btn" onClick={cargarOrdenes} disabled={loading}>
                <RefreshCw size={14} />
              </button>
            </div>

            <div className="mant-table-wrap">
              <table className="mant-table">
                <thead>
                  <tr>
                    <th>Equipo / Ubicación</th>
                    <th>Técnico</th>
                    <th>Tipo</th>
                    <th>Prioridad</th>
                    <th>Estado</th>
                    <th>Programada</th>
                    <th>Acciones</th>
                  </tr>
                </thead>
                <tbody>
                  {ordenes.map((o) => {
                    const est = ESTADOS[o.estado] || { label: o.estado, className: "badge-blue" };
                    return (
                      <tr key={o.id} className={o.estado === "EN_PROCESO" ? "row-active" : ""}>
                        <td className="mant-equipment-cell">
                          <div>
                            <strong>{getEquipo(o.equipo_id, o.equipo_nombre)}</strong>
                            <small>{getSede(o.sede_id)}</small>
                          </div>
                        </td>
                        <td>
                          <span className={o.tecnico_id ? "" : "text-muted"}>
                            {o.tecnico_nombre || getTecnico(o.tecnico_id)}
                          </span>
                        </td>
                        <td><span className="mant-type-badge">{o.tipo}</span></td>
                        <td>{o.prioridad}</td>
                        <td><span className={`mant-badge ${est.className}`}>{est.label}</span></td>
                        <td>{formatearFecha(o.fecha_programada)}</td>
                        <td>
                          <div className="mant-actions">
                            <button className="mant-view-btn" onClick={() => setDetalle(o)} title="Ver detalle">
                              <Eye size={14} />
                            </button>
                            {(!o.tecnico_id || o.estado === "PROGRAMADO") && (
                              <button className="mant-edit-btn" onClick={() => asignarTecnico(o)} title="Asignar técnico">
                                <UserPlus size={14} />
                              </button>
                            )}
                            {o.estado === "ASIGNADO" && (
                              <button className="mant-save-btn" onClick={() => cambiarEstado(o, "EN_PROCESO")} title="Iniciar ejecución" style={{ padding: "4px 8px", fontSize: 11 }}>
                                <Wrench size={13} /> Iniciar
                              </button>
                            )}
                            {o.estado === "EN_PROCESO" && (
                              <button className="mant-save-btn" onClick={() => cambiarEstado(o, "FINALIZADO")} title="Finalizar orden" style={{ padding: "4px 8px", fontSize: 11 }}>
                                <CheckCircle2 size={13} /> Cerrar
                              </button>
                            )}
                          </div>
                        </td>
                      </tr>
                    );
                  })}
                  {ordenes.length === 0 && (
                    <tr><td colSpan="7" className="mant-empty">No hay órdenes con este filtro.</td></tr>
                  )}
                </tbody>
              </table>
            </div>

            <div className="mant-pagination">
              <button disabled={pagina === 1} onClick={() => setPagina(pagina - 1)}>
                <ChevronLeft size={16} /> Anterior
              </button>
              <span>Página {pagina} de {totalPaginas}</span>
              <button disabled={pagina === totalPaginas} onClick={() => setPagina(pagina + 1)}>
                Siguiente <ChevronRight size={16} />
              </button>
            </div>
          </section>
        </div>

        {detalle && (
          <div className="mant-overlay" onClick={() => setDetalle(null)}>
            <div className="mant-modal" onClick={(e) => e.stopPropagation()}>
              <div className="mant-modal-header">
                <h2>Detalle de orden</h2>
                <button onClick={() => setDetalle(null)}><X size={18} /></button>
              </div>
              <div className="mant-detail-grid">
                <Detail label="Equipo" value={ordenConEquipo?.nombre || detalle.equipo_nombre} />
                <Detail label="Sede" value={detalle.sede_nombre || getSede(detalle.sede_id)} />
                <Detail label="Ubicación" value={ordenConEquipo?.ubicacion} />
                <Detail label="Técnico" value={detalle.tecnico_nombre || getTecnico(detalle.tecnico_id)} />
                <Detail label="Tipo" value={detalle.tipo} />
                <Detail label="Prioridad" value={detalle.prioridad} />
                <Detail label="Estado" value={detalle.estado} />
                <Detail label="Fecha programada" value={formatearFecha(detalle.fecha_programada)} />
                <Detail label="Descripción" value={detalle.descripcion} />
                <Detail label="Falla / Incidencia" value={detalle.falla_incidencia} />
                <Detail label="Diagnóstico" value={detalle.diagnostico} />
                <Detail label="Trabajo realizado" value={detalle.trabajo_realizado} />
                <Detail label="Solución" value={detalle.solucion} />
                <Detail label="Costo mano de obra" value={detalle.costo_mano_obra ? `$${Number(detalle.costo_mano_obra).toLocaleString()}` : null} />
                <Detail label="Costo repuestos" value={detalle.costo_repuestos ? `$${Number(detalle.costo_repuestos).toLocaleString()}` : null} />
                <Detail label="Costo total" value={detalle.costo_total ? `$${Number(detalle.costo_total).toLocaleString()}` : null} />
                <Detail label="Observaciones" value={detalle.observaciones} />
              </div>
              <div className="mant-form-actions" style={{ marginTop: 16 }}>
                {detalle.estado === "PROGRAMADO" && (
                  <button className="mant-save-btn" onClick={() => { asignarTecnico(detalle); setDetalle(null); }}>
                    <UserPlus size={14} /> Asignar técnico
                  </button>
                )}
                {detalle.estado === "ASIGNADO" && (
                  <button className="mant-save-btn" onClick={() => { cambiarEstado(detalle, "EN_PROCESO"); }}>
                    <Wrench size={14} /> Iniciar ejecución
                  </button>
                )}
                {detalle.estado === "EN_PROCESO" && (
                  <button className="mant-save-btn" onClick={() => { cambiarEstado(detalle, "FINALIZADO"); }}>
                    <CheckCircle2 size={14} /> Finalizar orden
                  </button>
                )}
                {detalle.estado === "FINALIZADO" && (
                  <button className="mant-edit-btn" onClick={() => { cambiarEstado(detalle, "EN_PROCESO"); setDetalle(null); }} style={{ padding: "8px 16px" }}>
                    <RefreshCw size={14} /> Reabrir
                  </button>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </AdminLayout>
  );
}

function Detail({ label, value }) {
  return (
    <div className="mant-detail">
      <span>{label}</span>
      <strong>{value || "—"}</strong>
    </div>
  );
}
