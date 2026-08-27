// ============================================================
// MANTENIMIENTOS PRO - BITÁCORA PROFESIONAL
// Wizard de 3 pasos para creación + tabla con filtros
// ============================================================

import { useCallback, useEffect, useState } from "react";
import {
  Wrench, Search, Edit, Trash2, Eye,
  RefreshCw, ChevronLeft, ChevronRight, X, Plus,
} from "lucide-react";

import AdminLayout from "./AdminLayout";
import API from "../../api/axios";
import { showToast } from "../../utils/toast";
import MaintenanceWizard from "./MaintenanceWizard";
import {
  construirEtiquetaEquipo,
  obtenerEtiquetaUbicacionEquipo,
  obtenerValorUbicacionEquipo,
} from "./mantenimientosEquipoUtils";
import "../../styles/maintenance-wizard.css";
import "./MantenimientosPage.css";

const ESTADOS = {
  PROGRAMADO: { label: "Programado", className: "badge-blue" },
  ASIGNADO: { label: "Asignado", className: "badge-green" },
  EN_PROCESO: { label: "En proceso", className: "badge-orange" },
  PAUSADO: { label: "Pausado", className: "badge-yellow" },
  FINALIZADO: { label: "Finalizado", className: "badge-green" },
  ANULADO: { label: "Anulado", className: "badge-red" },
};

const formInicial = {
  id: null,
  empresa_id: "",
  sede_id: "",
  ubicacion_equipo: "",
  equipo_id: "",
  tecnico_id: "",
  tipo: "PREVENTIVO",
  estado: "PROGRAMADO",
  prioridad: "MEDIA",
  fecha_programada: "",
  fecha_inicio_programada: "",
  fecha_fin_programada: "",
  latitud: "",
  longitud: "",
  estado_inicial_equipo: "",
  acciones_realizadas: "",
  resultado_final: "",
  observaciones: "",
  descripcion: "",
  falla_incidencia: "",
  diagnostico: "",
  trabajo_realizado: "",
  costo: "",
  costo_mano_obra: "",
  costo_repuestos: "",
  costo_total: "",
  solucion: "",
};

export default function MantenimientosPage({
  mode = "admin",
  embedded = false,
  coordinatorCompanies = [],
}) {
  const esCoordinador = mode === "coordinador";
  const [mantenimientos, setMantenimientos] = useState([]);
  const [empresas, setEmpresas] = useState([]);
  const [sedes, setSedes] = useState([]);
  const [equipos, setEquipos] = useState([]);
  const [tecnicos, setTecnicos] = useState([]);

  const [form, setForm] = useState(formInicial);
  const [busqueda, setBusqueda] = useState("");
  const [pagina, setPagina] = useState(1);
  const [porPagina] = useState(20);
  const [totalRegistros, setTotalRegistros] = useState(0);
  const [loading, setLoading] = useState(false);
  const [detalle, setDetalle] = useState(null);
  const [showWizard, setShowWizard] = useState(false);

  const [filtroEstado, setFiltroEstado] = useState("");
  const [filtroTipo, setFiltroTipo] = useState("");

  useEffect(() => { cargarTodo(); }, []); // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => { cargarMantenimientos(); }, [pagina, filtroEstado, filtroTipo]); // eslint-disable-line react-hooks/exhaustive-deps

  async function cargarTodo() {
    try {
      setLoading(true);
      if (esCoordinador) {
        const [resMant, resCatalogos] = await Promise.all([
          API.get("/coordinador/mantenimientos"),
          API.get("/coordinador/catalogos"),
        ]);
        const catalogos = resCatalogos.data || {};
        const empresasCoordinador = coordinatorCompanies.length
          ? coordinatorCompanies
          : catalogos.empresas || [];
        setMantenimientos(resMant.data || []);
        setEmpresas(empresasCoordinador);
        setSedes(catalogos.sedes || []);
        setEquipos(catalogos.equipos || []);
        setTecnicos(catalogos.tecnicos || []);
      } else {
        const [resEmp, resSedes, resEquipos, resTec] = await Promise.all([
          API.get("/empresas/"),
          API.get("/sedes/"),
          API.get("/equipos/"),
          API.get("/tecnicos/"),
        ]);
        setEmpresas(resEmp.data || []);
        setSedes(resSedes.data || []);
        setEquipos(resEquipos.data || []);
        setTecnicos(resTec.data || []);
        await cargarMantenimientos();
      }
    } catch (error) {
      console.error("Error cargando módulo:", error);
      showToast("Error cargando datos del módulo", "error");
    } finally {
      setLoading(false);
    }
  }

  async function cargarMantenimientos() {
    try {
      if (esCoordinador) return;
      const params = { page: pagina, per_page: porPagina };
      if (filtroEstado) params.estado = filtroEstado;
      if (filtroTipo) params.tipo = filtroTipo;
      if (busqueda.trim()) params.buscar = busqueda.trim();
      const res = await API.get("/mantenimientos/", { params });
      const data = res.data;
      if (data?.items) {
        setMantenimientos(data.items);
        setTotalRegistros(data.total);
      } else {
        setMantenimientos(Array.isArray(data) ? data : []);
        setTotalRegistros(Array.isArray(data) ? data.length : 0);
      }
    } catch (error) {
      console.error("Error listando mantenimientos:", error);
    }
  }

  const reabrirMantenimiento = async (m) => {
    const motivo = window.prompt("Indica el motivo de la reapertura (mín. 10 caracteres):");
    if (motivo === null) return;
    if (motivo.trim().length < 10) {
      showToast("El motivo debe tener al menos 10 caracteres", "warning");
      return;
    }
    try {
      setLoading(true);
      if (esCoordinador) {
        await API.put(`/coordinador/mantenimientos/${m.id}/estado`, null, {
          params: { estado: "EN_PROCESO", observacion: motivo },
        });
      } else {
        await API.patch(`/mantenimientos/${m.id}/cambiar-estado`, {
          estado_nuevo: "EN_PROCESO",
          observacion: motivo,
          creado_por: "Administrador",
        });
      }
      setDetalle(null);
      await cargarMantenimientos();
      showToast("Mantenimiento reabierto correctamente", "success");
    } catch (error) {
      showToast(error?.response?.data?.detail || "No se pudo reabrir", "error");
    } finally {
      setLoading(false);
    }
  };

  const editarMantenimiento = (m) => {
    const equipo = equipos.find((eq) => String(eq.id) === String(m.equipo_id));
    setForm({
      id: m.id,
      empresa_id: m.empresa_id || equipo?.empresa_id || "",
      sede_id: m.sede_id || equipo?.sede_id || "",
      ubicacion_equipo: equipo
        ? obtenerEtiquetaUbicacionEquipo(obtenerValorUbicacionEquipo(equipo))
        : "",
      equipo_id: m.equipo_id || "",
      tecnico_id: m.tecnico_id || "",
      tipo: m.tipo || "PREVENTIVO",
      estado: m.estado || "PROGRAMADO",
      prioridad: m.prioridad || "MEDIA",
      fecha_programada: convertirFechaInput(m.fecha_programada),
      fecha_inicio_programada: convertirFechaInput(m.fecha_inicio_programada),
      fecha_fin_programada: convertirFechaInput(m.fecha_fin_programada),
      latitud: m.latitud || "",
      longitud: m.longitud || "",
      estado_inicial_equipo: m.estado_inicial_equipo || "",
      acciones_realizadas: m.acciones_realizadas || "",
      resultado_final: m.resultado_final || "",
      observaciones: m.observaciones || "",
      descripcion: m.descripcion || "",
      falla_incidencia: m.falla_incidencia || "",
      diagnostico: m.diagnostico || "",
      trabajo_realizado: m.trabajo_realizado || "",
      costo: m.costo || "",
      costo_mano_obra: m.costo_mano_obra || "",
      costo_repuestos: m.costo_repuestos || "",
      costo_total: m.costo_total || "",
      solucion: m.solucion || "",
    });
    setShowWizard(false);
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  const eliminarMantenimiento = async (m) => {
    if (!window.confirm(`¿Eliminar el mantenimiento del equipo "${getEquipo(m.equipo_id, m.equipo_nombre)}"?`)) return;
    try {
      if (esCoordinador) {
        await API.delete(`/coordinador/mantenimientos/${m.id}`);
      } else {
        await API.delete(`/mantenimientos/${m.id}`);
      }
      showToast("Mantenimiento eliminado", "success");
      await cargarMantenimientos();
    } catch (error) {
      showToast(error?.response?.data?.detail || "No se pudo eliminar", "error");
    }
  };

  const guardarEdicion = async () => {
    if (!form.equipo_id) return showToast("Seleccione un equipo", "warning");
    const payload = {
      equipo_id: form.equipo_id,
      tipo: form.tipo,
      descripcion: form.descripcion || "Mantenimiento registrado.",
      prioridad: form.prioridad || "MEDIA",
      fecha_programada: form.fecha_programada || null,
      fecha_inicio_programada: form.fecha_inicio_programada || null,
      fecha_fin_programada: form.fecha_fin_programada || null,
      observaciones: form.observaciones,
      latitud: form.latitud || null,
      longitud: form.longitud || null,
      costo: form.costo ? Number(form.costo) : null,
      costo_mano_obra: form.costo_mano_obra ? Number(form.costo_mano_obra) : null,
      costo_repuestos: form.costo_repuestos ? Number(form.costo_repuestos) : null,
      costo_total: form.costo_total ? Number(form.costo_total) : null,
      solucion: form.solucion || null,
    };
    try {
      setLoading(true);
      await API.put(`/mantenimientos/${form.id}`, payload);
      if (form.tecnico_id) {
        await API.patch(`/mantenimientos/${form.id}/asignar-tecnico`, {
          tecnico_id: form.tecnico_id,
          observacion: "Técnico actualizado.",
          creado_por: "Administrador",
        });
      }
      showToast("Mantenimiento actualizado", "success");
      setForm(formInicial);
      await cargarMantenimientos();
    } catch (error) {
      showToast(error?.response?.data?.detail || "No se pudo guardar", "error");
    } finally {
      setLoading(false);
    }
  };

  const convertirFechaInput = (value) => {
    if (!value) return "";
    const d = new Date(value);
    if (Number.isNaN(d.getTime())) return "";
    return d.toISOString().slice(0, 16);
  };

  const formatearFecha = (value) => {
    if (!value) return "—";
    const d = new Date(value);
    if (Number.isNaN(d.getTime())) return value;
    return d.toLocaleString();
  };

  const getEmpresa = useCallback((id) => {
    return empresas.find((e) => String(e.id) === String(id))?.nombre || "—";
  }, [empresas]);

  const getSede = useCallback((id) => {
    return sedes.find((s) => String(s.id) === String(id))?.nombre || "—";
  }, [sedes]);

  const getEquipo = useCallback((id, fallback = "") => {
    const eq = equipos.find((e) => String(e.id) === String(id));
    return eq ? construirEtiquetaEquipo(eq) : fallback || "—";
  }, [equipos]);

  const getTecnicoNombre = (tecnico) => {
    if (!tecnico) return "—";
    return tecnico.usuario?.nombre_completo || tecnico.nombre_completo || tecnico.nombre || `Técnico ${tecnico.id}`;
  };

  const getTecnico = useCallback((id) => {
    const t = tecnicos.find((tc) => String(tc.id) === String(id));
    return getTecnicoNombre(t);
  }, [tecnicos]);

  const getEstado = (estado) => ESTADOS[estado] || { label: estado || "—", className: "badge-blue" };

  const totalPaginas = Math.max(1, Math.ceil(totalRegistros / porPagina));

  const equipoDetalle = detalle ? equipos.find((e) => String(e.id) === String(detalle.equipo_id)) : null;

  const handleWizardSuccess = () => {
    setShowWizard(false);
    setPagina(1);
    cargarMantenimientos();
  };

  const contenido = (
    <div className="mant-page">
      <div className="sga-module-hero">
        <div className="sga-module-hero__icon">
          <Wrench size={24} />
        </div>
        <div className="sga-module-hero__text">
          <span>Administración SaaS</span>
          <h1>Gestión de Mantenimientos</h1>
          <p>Planifica y supervisa el mantenimiento general: planes preventivos, frecuencias, calendario, próximos, vencidos, historial e indicadores.</p>
        </div>
      </div>

      <div className="mant-pro-layout">
        {showWizard || form.id ? (
          <section className="mant-card mant-form-card">
            {showWizard ? (
              <MaintenanceWizard
                equipos={equipos}
                sedes={sedes}
                tecnicos={tecnicos}
                onSuccess={handleWizardSuccess}
                onCancel={() => setShowWizard(false)}
              />
            ) : (
              <>
                <div className="mant-section-header">
                  <div>
                    <h2>Editar mantenimiento</h2>
                    <p>Modifica los datos del mantenimiento existente.</p>
                  </div>
                  <button className="mant-reload-btn" onClick={() => { setForm(formInicial); }}>
                    <X size={16} /> Cancelar edición
                  </button>
                </div>
                <div className="mant-grid-3">
                  <label className="mant-field">
                    <span>Tipo</span>
                    <select value={form.tipo} onChange={(e) => setForm({ ...form, tipo: e.target.value })}>
                      <option value="PREVENTIVO">Preventivo</option>
                      <option value="CORRECTIVO">Correctivo</option>
                      <option value="CALIBRACION">Calibración</option>
                      <option value="INSPECCION">Inspección</option>
                    </select>
                  </label>
                  <label className="mant-field">
                    <span>Prioridad</span>
                    <select value={form.prioridad} onChange={(e) => setForm({ ...form, prioridad: e.target.value })}>
                      <option value="BAJA">Baja</option>
                      <option value="MEDIA">Media</option>
                      <option value="ALTA">Alta</option>
                      <option value="CRITICA">Crítica</option>
                    </select>
                  </label>
                  <label className="mant-field">
                    <span>Descripción</span>
                    <textarea rows={2} value={form.descripcion} onChange={(e) => setForm({ ...form, descripcion: e.target.value })} />
                  </label>
                  <label className="mant-field">
                    <span>Fecha programada</span>
                    <input type="datetime-local" value={form.fecha_programada} onChange={(e) => setForm({ ...form, fecha_programada: e.target.value })} />
                  </label>
                  <label className="mant-field">
                    <span>Observaciones</span>
                    <textarea rows={2} value={form.observaciones} onChange={(e) => setForm({ ...form, observaciones: e.target.value })} />
                  </label>
                </div>
                <div className="mant-form-actions">
                  <button className="mant-save-btn" onClick={guardarEdicion} disabled={loading}>
                    Guardar cambios
                  </button>
                </div>
              </>
            )}
          </section>
        ) : (
          <section className="mant-card mant-form-card">
            <div className="mant-section-header">
              <div>
                <h2>Crear mantenimiento</h2>
                <p>Inicia una nueva orden de mantenimiento en 3 pasos.</p>
              </div>
              <button className="mant-save-btn" onClick={() => setShowWizard(true)}>
                <Plus size={16} /> Nueva orden
              </button>
            </div>
          </section>
        )}

        <section className="mant-card mant-list-card">
          <div className="mant-section-header">
            <div>
              <h2>Historial de mantenimientos</h2>
              <p>Consulta, búsqueda, edición y eliminación segura.</p>
            </div>
            <span className="mant-counter">{totalRegistros} registros</span>
          </div>

          <div className="mant-filters-row">
            <select className="mant-filter-select" value={filtroEstado} onChange={(e) => { setFiltroEstado(e.target.value); setPagina(1); }}>
              <option value="">Todos los estados</option>
              {Object.entries(ESTADOS).map(([k, v]) => <option key={k} value={k}>{v.label}</option>)}
            </select>
            <select className="mant-filter-select" value={filtroTipo} onChange={(e) => { setFiltroTipo(e.target.value); setPagina(1); }}>
              <option value="">Todos los tipos</option>
              <option value="PREVENTIVO">Preventivo</option>
              <option value="CORRECTIVO">Correctivo</option>
              <option value="CALIBRACION">Calibración</option>
              <option value="INSPECCION">Inspección</option>
            </select>
            <div className="mant-search-box">
              <Search size={16} />
              <input
                placeholder="Buscar por equipo, código, serie..."
                value={busqueda}
                onChange={(e) => { setBusqueda(e.target.value); setPagina(1); }}
                onKeyDown={(e) => { if (e.key === "Enter") cargarMantenimientos(); }}
              />
            </div>
            <button className="mant-reload-btn" onClick={cargarMantenimientos} disabled={loading}>
              <RefreshCw size={14} />
            </button>
          </div>

          <div className="mant-table-wrap">
            <table className="mant-table">
              <thead>
                <tr>
                  <th>Equipo</th>
                  <th>Técnico</th>
                  <th>Tipo</th>
                  <th>Prioridad</th>
                  <th>Estado</th>
                  <th>Inicio</th>
                  <th>Fin</th>
                  <th>Acciones</th>
                </tr>
              </thead>
              <tbody>
                {mantenimientos.map((m) => {
                  const estado = getEstado(m.estado);
                  return (
                    <tr key={m.id}>
                      <td className="mant-equipment-cell">
                        <div>
                          <strong>{getEquipo(m.equipo_id, m.equipo_nombre)}</strong>
                          <small>{m.empresa_nombre || getEmpresa(m.empresa_id)} · {m.sede_nombre || getSede(m.sede_id)}</small>
                        </div>
                      </td>
                      <td>{m.tecnico_nombre || getTecnico(m.tecnico_id)}</td>
                      <td><span className="mant-type-badge">{m.tipo}</span></td>
                      <td>{m.prioridad}</td>
                      <td><span className={`mant-badge ${estado.className}`}>{estado.label}</span></td>
                      <td>{formatearFecha(m.fecha_inicio || m.fecha_programada)}</td>
                      <td>{formatearFecha(m.fecha_finalizacion)}</td>
                      <td>
                        <div className="mant-actions">
                          <button className="mant-view-btn" onClick={() => setDetalle(m)}>
                            <Eye size={14} /> Ver
                          </button>
                          <button className="mant-edit-btn" onClick={() => editarMantenimiento(m)}>
                            <Edit size={14} />
                          </button>
                          {String(m.estado || "").toUpperCase() === "FINALIZADO" && (
                            <button className="mant-edit-btn" onClick={() => reabrirMantenimiento(m)} disabled={loading}>
                              <RefreshCw size={14} />
                            </button>
                          )}
                          <button className="mant-delete-btn" onClick={() => eliminarMantenimiento(m)}>
                            <Trash2 size={14} />
                          </button>
                        </div>
                      </td>
                    </tr>
                  );
                })}
                {mantenimientos.length === 0 && (
                  <tr><td colSpan="8" className="mant-empty">No hay mantenimientos registrados.</td></tr>
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
              <h2>Detalle del mantenimiento</h2>
              <button onClick={() => setDetalle(null)}><X size={18} /></button>
            </div>
            <div className="mant-detail-grid">
              <Detail label="Equipo" value={equipoDetalle?.nombre || detalle.equipo_nombre} />
              <Detail label="Empresa" value={detalle.empresa_nombre || getEmpresa(detalle.empresa_id)} />
              <Detail label="Sede" value={detalle.sede_nombre || getSede(detalle.sede_id)} />
              <Detail label="Ubicación" value={equipoDetalle?.ubicacion} />
              <Detail label="Código" value={equipoDetalle?.codigo_id || equipoDetalle?.codigo} />
              <Detail label="Serie" value={equipoDetalle?.serie} />
              <Detail label="Técnico" value={detalle.tecnico_nombre || getTecnico(detalle.tecnico_id)} />
              <Detail label="Tipo" value={detalle.tipo} />
              <Detail label="Prioridad" value={detalle.prioridad} />
              <Detail label="Estado" value={detalle.estado} />
              <Detail label="Fecha programada" value={formatearFecha(detalle.fecha_programada)} />
              <Detail label="Falla" value={detalle.falla_incidencia} />
              <Detail label="Diagnóstico" value={detalle.diagnostico} />
              <Detail label="Trabajo" value={detalle.trabajo_realizado} />
              <Detail label="Solución" value={detalle.solucion} />
              <Detail label="Costo total" value={detalle.costo_total} />
              <Detail label="Observaciones" value={detalle.observaciones} />
            </div>
          </div>
        </div>
      )}
    </div>
  );

  return embedded ? contenido : <AdminLayout>{contenido}</AdminLayout>;
}

function Detail({ label, value }) {
  return (
    <div className="mant-detail">
      <span>{label}</span>
      <strong>{value || "—"}</strong>
    </div>
  );
}
