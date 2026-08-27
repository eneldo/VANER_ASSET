// ============================================================
// ÓRDENES DE MANTENIMIENTO - Ejecución de intervenciones
// Gestiona cada intervención concreta: solicitud, asignación,
// ejecución, repuestos, evidencias, costos y cierre.
// ============================================================

import { useCallback, useEffect, useState } from "react";
import {
  ClipboardList, Search, Eye, RefreshCw, ChevronLeft, ChevronRight,
  X, UserPlus, CheckCircle2, AlertTriangle, Wrench, Clock,
  Package, Plus, DollarSign, History,
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

const ESTADO_SOLICITUD = {
  SOLICITADO: { label: "Solicitado", className: "badge-blue" },
  APROBADO: { label: "Aprobado", className: "badge-green" },
  RESERVADO: { label: "Reservado", className: "badge-orange" },
  ENTREGADO: { label: "Entregado", className: "badge-green" },
  CONSUMIDO: { label: "Consumido", className: "badge-green" },
  DEVUELTO_PARCIAL: { label: "Dev. parcial", className: "badge-yellow" },
  DEVUELTO: { label: "Devuelto", className: "badge-green" },
  RECHAZADO: { label: "Rechazado", className: "badge-red" },
  CANCELADO: { label: "Cancelado", className: "badge-red" },
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
  const [tabDetalle, setTabDetalle] = useState("info");
  const [repuestosOt, setRepuestosOt] = useState(null);
  const [trazabilidad, setTrazabilidad] = useState(null);
  const [costosOt, setCostosOt] = useState(null);
  const [repuestos, setRepuestos] = useState([]);
  const [bodegas, setBodegas] = useState([]);
  const [formRepuesto, setFormRepuesto] = useState(null);
  const porPagina = 20;

  useEffect(() => { cargarDatos(); }, []); // eslint-disable-line react-hooks/exhaustive-deps
  useEffect(() => { cargarOrdenes(); }, [pagina, filtroEstado]); // eslint-disable-line react-hooks/exhaustive-deps

  async function cargarDatos() {
    try {
      setLoading(true);
      const [resEq, resTec, resSedes, resRep, resBod] = await Promise.all([
        API.get("/equipos/"),
        API.get("/tecnicos/"),
        API.get("/sedes/"),
        API.get("/repuestos/", { params: { per_page: 200 } }),
        API.get("/repuestos/bodegas"),
      ]);
      setEquipos(resEq.data || []);
      setTecnicos(resTec.data || []);
      setSedes(resSedes.data || []);
      setRepuestos(resRep.data || []);
      setBodegas(resBod.data || []);
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

  const cargarRepuestosOt = async (mantId) => {
    try {
      const res = await API.get(`/repuestos/ot/${mantId}`);
      setRepuestosOt(res.data);
    } catch {
      setRepuestosOt({ repuestos: [], costo_total_repuestos: 0 });
    }
  };

  const cargarTrazabilidad = async (mantId) => {
    try {
      const res = await API.get(`/repuestos/ot/${mantId}/trazabilidad`);
      setTrazabilidad(res.data);
    } catch {
      setTrazabilidad({ movimientos: [] });
    }
  };

  const cargarCostos = async (mantId) => {
    try {
      const res = await API.get(`/repuestos/ot/${mantId}/costos`);
      setCostosOt(res.data);
    } catch {
      setCostosOt({ detalle: [], costo_total_repuestos: 0 });
    }
  };

  const abrirDetalle = async (orden) => {
    setDetalle(orden);
    setTabDetalle("info");
    setRepuestosOt(null);
    setTrazabilidad(null);
    setCostosOt(null);
    await Promise.all([
      cargarRepuestosOt(orden.id),
      cargarTrazabilidad(orden.id),
      cargarCostos(orden.id),
    ]);
  };

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

  const solicitarRepuesto = async (datos) => {
    try {
      await API.post(`/repuestos/ot/${detalle.id}/solicitar`, datos);
      showToast("Solicitud creada", "success");
      setFormRepuesto(null);
      await cargarRepuestosOt(detalle.id);
      await cargarTrazabilidad(detalle.id);
    } catch (err) {
      showToast(err?.response?.data?.detail || "Error al solicitar", "error");
    }
  };

  const ejecutarAccionRepuesto = async (accion, solicitudId) => {
    const mensajes = {
      aprobar: "¿Aprobar solicitud?",
      reservar: "¿Reservar stock para esta solicitud?",
      entregar: "¿Entregar material al técnico?",
      consumir: "¿Confirmar consumo del material?",
      devolver: "¿Devolver material sobrante a bodega?",
    };
    if (!window.confirm(mensajes[accion] || "Confirmar acción")) return;
    try {
      const urlBase = `/repuestos/ot/solicitudes/${solicitudId}`;
      if (accion === "aprobar") await API.post(`${urlBase}/aprobar`);
      else if (accion === "reservar") await API.post(`${urlBase}/reservar`);
      else if (accion === "entregar") await API.post(`${urlBase}/entregar`);
      else if (accion === "consumir") {
        const cant = window.prompt("Cantidad utilizada:");
        if (!cant) return;
        await API.post(`${urlBase}/consumir?cantidad=${cant}`);
      }
      else if (accion === "devolver") {
        const cant = window.prompt("Cantidad a devolver:");
        if (!cant) return;
        const bod = bodegas[0]?.id;
        if (!bod) { showToast("No hay bodegas configuradas", "error"); return; }
        await API.post(`${urlBase}/devolver?cantidad=${cant}&bodega_id=${bod}`);
      }
      showToast("Acción ejecutada", "success");
      await cargarRepuestosOt(detalle.id);
      await cargarTrazabilidad(detalle.id);
      await cargarCostos(detalle.id);
    } catch (err) {
      showToast(err?.response?.data?.detail || "Error al ejecutar acción", "error");
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
                            <button className="mant-view-btn" onClick={() => abrirDetalle(o)} title="Ver detalle">
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
            <div className="mant-modal" onClick={(e) => e.stopPropagation()} style={{ maxWidth: 800 }}>
              <div className="mant-modal-header">
                <h2>Detalle de orden</h2>
                <button onClick={() => setDetalle(null)}><X size={18} /></button>
              </div>

              <div className="mant-filter-chips" style={{ marginBottom: 16 }}>
                <button className={`mant-chip ${tabDetalle === "info" ? "active" : ""}`} onClick={() => setTabDetalle("info")}>
                  <ClipboardList size={13} style={{ marginRight: 4 }} /> Información
                </button>
                <button className={`mant-chip ${tabDetalle === "repuestos" ? "active" : ""}`} onClick={() => setTabDetalle("repuestos")}>
                  <Package size={13} style={{ marginRight: 4 }} /> Repuestos ({repuestosOt?.total_repuestos || 0})
                </button>
                <button className={`mant-chip ${tabDetalle === "costos" ? "active" : ""}`} onClick={() => setTabDetalle("costos")}>
                  <DollarSign size={13} style={{ marginRight: 4 }} /> Costos
                </button>
                <button className={`mant-chip ${tabDetalle === "trazabilidad" ? "active" : ""}`} onClick={() => setTabDetalle("trazabilidad")}>
                  <History size={13} style={{ marginRight: 4 }} /> Trazabilidad
                </button>
              </div>

              {tabDetalle === "info" && (
                <>
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
                </>
              )}

              {tabDetalle === "repuestos" && (
                <RepuestosOTPanel
                  data={repuestosOt}
                  repuestos={repuestos}
                  bodegas={bodegas}
                  formRepuesto={formRepuesto}
                  setFormRepuesto={setFormRepuesto}
                  onSolicitar={solicitarRepuesto}
                  onAccion={ejecutarAccionRepuesto}
                />
              )}

              {tabDetalle === "costos" && (
                <CostosOTPanel data={costosOt} />
              )}

              {tabDetalle === "trazabilidad" && (
                <TrazabilidadOTPanel data={trazabilidad} />
              )}
            </div>
          </div>
        )}
      </div>
    </AdminLayout>
  );
}

// ============================================================
// PANEL DE REPUESTOS POR OT
// ============================================================

function RepuestosOTPanel({ data, repuestos, bodegas, formRepuesto, setFormRepuesto, onSolicitar, onAccion }) {
  if (!data) return <div className="mant-empty">Cargando repuestos...</div>;

  const items = data.repuestos || [];

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 12 }}>
        <h3 style={{ margin: 0, fontSize: 14, fontWeight: 600 }}>Repuestos de esta orden</h3>
        <button className="mant-save-btn" onClick={() => setFormRepuesto({ repuesto_id: "", cantidad_solicitada: 1, bodega_id: "" })}>
          <Plus size={14} /> Solicitar repuesto
        </button>
      </div>

      <div className="mant-table-wrap">
        <table className="mant-table">
          <thead>
            <tr>
              <th>Repuesto</th>
              <th>Cód.</th>
              <th>Solicitada</th>
              <th>Entregada</th>
              <th>Devuelta</th>
              <th>Estado</th>
              <th>Costo U.</th>
              <th>Costo Línea</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            {items.map((r) => {
              const est = ESTADO_SOLICITUD[r.estado] || { label: r.estado, className: "badge-blue" };
              return (
                <tr key={r.solicitud_id}>
                  <td>{r.repuesto_nombre}</td>
                  <td><strong>{r.repuesto_codigo}</strong></td>
                  <td>{r.cantidad_solicitada}</td>
                  <td>{r.cantidad_entregada || "—"}</td>
                  <td>{r.cantidad_devuelta || "—"}</td>
                  <td><span className={`mant-badge ${est.className}`}>{est.label}</span></td>
                  <td>{r.costo_unitario ? `$${r.costo_unitario.toLocaleString()}` : "—"}</td>
                  <td>{r.costo_linea ? `$${r.costo_linea.toLocaleString()}` : "—"}</td>
                  <td>
                    <div className="mant-actions">
                      {r.estado === "SOLICITADO" && (
                        <button className="mant-save-btn" onClick={() => onAccion("aprobar", r.solicitud_id)} style={{ padding: "3px 6px", fontSize: 10 }}>Aprobar</button>
                      )}
                      {r.estado === "APROBADO" && (
                        <button className="mant-save-btn" onClick={() => onAccion("reservar", r.solicitud_id)} style={{ padding: "3px 6px", fontSize: 10 }}>Reservar</button>
                      )}
                      {r.estado === "RESERVADO" && (
                        <button className="mant-save-btn" onClick={() => onAccion("entregar", r.solicitud_id)} style={{ padding: "3px 6px", fontSize: 10 }}>Entregar</button>
                      )}
                      {r.estado === "ENTREGADO" && (
                        <>
                          <button className="mant-save-btn" onClick={() => onAccion("consumir", r.solicitud_id)} style={{ padding: "3px 6px", fontSize: 10 }}>Consumir</button>
                          <button className="mant-edit-btn" onClick={() => onAccion("devolver", r.solicitud_id)} style={{ padding: "3px 6px", fontSize: 10 }}>Devolver</button>
                        </>
                      )}
                      {r.estado === "DEVUELTO_PARCIAL" && (
                        <button className="mant-save-btn" onClick={() => onAccion("consumir", r.solicitud_id)} style={{ padding: "3px 6px", fontSize: 10 }}>Consumir</button>
                      )}
                    </div>
                  </td>
                </tr>
              );
            })}
            {items.length === 0 && (
              <tr><td colSpan="9" className="mant-empty">No hay repuestos solicitados para esta orden.</td></tr>
            )}
          </tbody>
        </table>
      </div>

      {items.length > 0 && (
        <div style={{ textAlign: "right", marginTop: 8, fontWeight: 600, fontSize: 13 }}>
          Costo total repuestos: ${data.costo_total_repuestos?.toLocaleString() || "0"}
        </div>
      )}

      {formRepuesto && (
        <div className="mant-overlay" onClick={() => setFormRepuesto(null)}>
          <div className="mant-modal" onClick={(e) => e.stopPropagation()} style={{ maxWidth: 450 }}>
            <div className="mant-modal-header">
              <h2>Solicitar repuesto</h2>
              <button onClick={() => setFormRepuesto(null)}><X size={18} /></button>
            </div>
            <div className="mant-detail-grid" style={{ gridTemplateColumns: "1fr" }}>
              <div className="mant-detail">
                <span>Repuesto *</span>
                <select className="mant-input" value={formRepuesto.repuesto_id} onChange={(e) => setFormRepuesto({ ...formRepuesto, repuesto_id: e.target.value })}>
                  <option value="">Seleccionar repuesto...</option>
                  {repuestos.map((r) => <option key={r.id} value={r.id}>{r.codigo} - {r.nombre}</option>)}
                </select>
              </div>
              <div className="mant-detail">
                <span>Cantidad *</span>
                <input className="mant-input" type="number" min="0.001" step="0.001" value={formRepuesto.cantidad_solicitada} onChange={(e) => setFormRepuesto({ ...formRepuesto, cantidad_solicitada: Number(e.target.value) })} />
              </div>
              <div className="mant-detail">
                <span>Bodega</span>
                <select className="mant-input" value={formRepuesto.bodega_id} onChange={(e) => setFormRepuesto({ ...formRepuesto, bodega_id: e.target.value })}>
                  <option value="">Seleccionar bodega...</option>
                  {bodegas.map((b) => <option key={b.id} value={b.id}>{b.nombre}</option>)}
                </select>
              </div>
              <div className="mant-detail">
                <span>Observaciones</span>
                <textarea className="mant-input" rows={2} value={formRepuesto.observaciones || ""} onChange={(e) => setFormRepuesto({ ...formRepuesto, observaciones: e.target.value })} />
              </div>
            </div>
            <div className="mant-form-actions">
              <button className="mant-save-btn" onClick={() => onSolicitar(formRepuesto)}>
                <Package size={14} /> Solicitar
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// ============================================================
// PANEL DE COSTOS POR OT
// ============================================================

function CostosOTPanel({ data }) {
  if (!data) return <div className="mant-empty">Cargando costos...</div>;

  const items = data.detalle || [];

  return (
    <div>
      <h3 style={{ margin: "0 0 12px", fontSize: 14, fontWeight: 600 }}>Costo de repuestos por orden</h3>
      {items.length === 0 ? (
        <div className="mant-empty">No hay costos de repuestos registrados.</div>
      ) : (
        <>
          <div className="mant-table-wrap">
            <table className="mant-table">
              <thead>
                <tr>
                  <th>Repuesto</th>
                  <th>Código</th>
                  <th>Cantidad</th>
                  <th>Costo Unitario</th>
                  <th>Costo Línea</th>
                </tr>
              </thead>
              <tbody>
                {items.map((c, i) => (
                  <tr key={i}>
                    <td>{c.repuesto}</td>
                    <td><strong>{c.codigo}</strong></td>
                    <td>{c.cantidad_consumida}</td>
                    <td>${c.costo_unitario.toLocaleString()}</td>
                    <td><strong>${c.costo_linea.toLocaleString()}</strong></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div style={{ textAlign: "right", marginTop: 12, padding: "8px 16px", background: "#f0fdf4", borderRadius: 8, border: "1px solid #bbf7d0" }}>
            <span style={{ fontSize: 13, color: "#166534" }}>Costo total repuestos: </span>
            <strong style={{ fontSize: 16, color: "#166534" }}>${data.costo_total_repuestos?.toLocaleString() || "0"}</strong>
          </div>
        </>
      )}
    </div>
  );
}

// ============================================================
// PANEL DE TRAZABILIDAD
// ============================================================

function TrazabilidadOTPanel({ data }) {
  if (!data) return <div className="mant-empty">Cargando trazabilidad...</div>;

  const movs = data.movimientos || [];

  return (
    <div>
      <h3 style={{ margin: "0 0 12px", fontSize: 14, fontWeight: 600 }}>Trazabilidad de movimientos</h3>
      {movs.length === 0 ? (
        <div className="mant-empty">No hay movimientos registrados para esta orden.</div>
      ) : (
        <div className="mant-table-wrap">
          <table className="mant-table">
            <thead>
              <tr>
                <th>Fecha</th>
                <th>Tipo</th>
                <th>Repuesto</th>
                <th>Cantidad</th>
                <th>Costo U.</th>
                <th>Costo T.</th>
                <th>Motivo</th>
              </tr>
            </thead>
            <tbody>
              {movs.map((m, i) => (
                <tr key={i}>
                  <td>{m.fecha ? new Date(m.fecha).toLocaleString("es-CO") : "—"}</td>
                  <td><span className="mant-type-badge">{m.tipo?.replace(/_/g, " ")}</span></td>
                  <td>{m.repuesto}</td>
                  <td>{m.cantidad}</td>
                  <td>{m.costo_unitario ? `$${m.costo_unitario.toLocaleString()}` : "—"}</td>
                  <td>{m.costo_total ? `$${m.costo_total.toLocaleString()}` : "—"}</td>
                  <td>{m.motivo || "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

// ============================================================
// DETAIL HELPER
// ============================================================

function Detail({ label, value }) {
  return (
    <div className="mant-detail">
      <span>{label}</span>
      <strong>{value || "—"}</strong>
    </div>
  );
}
