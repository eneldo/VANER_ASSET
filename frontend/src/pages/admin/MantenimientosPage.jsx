// ============================================================
// MANTENIMIENTOS PRO - BITÁCORA PROFESIONAL
// Archivo: frontend/src/pages/admin/MantenimientosPage.jsx
//
// Ajustes aplicados:
// - Usa AdminLayout para conservar sidebar y estructura Admin PRO.
// - Usa API global con interceptor de token.
// - Formulario y tabla quedan en layout tipo Equipos.
// - Scroll interno elegante en historial.
// - Edición conserva empresa/sede/equipo.
// ============================================================

import { useEffect, useMemo, useState } from "react";
import {
  ArrowLeft,
  Wrench,
  Save,
  Search,
  Edit,
  Trash2,
  Eye,
  RefreshCw,
  ChevronLeft,
  ChevronRight,
  X,
} from "lucide-react";

import AdminLayout from "./AdminLayout";
import API from "../../api/axios";
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
  equipo_id: "",
  tecnico_id: "",
  tipo: "PREVENTIVO",
  estado: "PROGRAMADO",
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
  costo: "",
};

export default function MantenimientosPage() {
  const [mantenimientos, setMantenimientos] = useState([]);
  const [empresas, setEmpresas] = useState([]);
  const [sedes, setSedes] = useState([]);
  const [equipos, setEquipos] = useState([]);
  const [tecnicos, setTecnicos] = useState([]);

  const [form, setForm] = useState(formInicial);
  const [busqueda, setBusqueda] = useState("");
  const [pagina, setPagina] = useState(1);
  const [porPagina] = useState(6);
  const [loading, setLoading] = useState(false);
  const [detalle, setDetalle] = useState(null);

  useEffect(() => {
    cargarTodo();
  }, []);

  const cargarTodo = async () => {
    try {
      setLoading(true);

      const [resMant, resEmp, resSedes, resEquipos, resTec] =
        await Promise.all([
          API.get("/mantenimientos/"),
          API.get("/empresas/"),
          API.get("/sedes/"),
          API.get("/equipos/"),
          API.get("/tecnicos/"),
        ]);

      setMantenimientos(resMant.data || []);
      setEmpresas(resEmp.data || []);
      setSedes(resSedes.data || []);
      setEquipos(resEquipos.data || []);
      setTecnicos(resTec.data || []);
    } catch (error) {
      console.error("Error cargando módulo mantenimientos:", error);
      alert("Error cargando datos del módulo de mantenimientos.");
    } finally {
      setLoading(false);
    }
  };

  const sedesFiltradas = useMemo(() => {
    if (!form.empresa_id) return [];
    return sedes.filter((s) => String(s.empresa_id) === String(form.empresa_id));
  }, [sedes, form.empresa_id]);

  const equiposFiltrados = useMemo(() => {
    if (!form.sede_id) return [];
    return equipos.filter((e) => String(e.sede_id) === String(form.sede_id));
  }, [equipos, form.sede_id]);

  const getEmpresa = (id) => {
    const empresa = empresas.find((e) => String(e.id) === String(id));
    return empresa?.nombre || empresa?.razon_social || "—";
  };

  const getSede = (id) => {
    const sede = sedes.find((s) => String(s.id) === String(id));
    return sede?.nombre || "—";
  };

  const getEquipo = (id) => {
    const equipo = equipos.find((e) => String(e.id) === String(id));
    return equipo?.nombre || equipo?.codigo_id || equipo?.codigo || "—";
  };

  const getTecnicoNombre = (tecnico) => {
    if (!tecnico) return "—";

    return (
      tecnico.usuario?.nombre_completo ||
      tecnico.nombre_completo ||
      tecnico.nombre ||
      tecnico.nombres ||
      tecnico.username ||
      tecnico.usuario?.username ||
      `Técnico ${tecnico.id}`
    );
  };

  const getTecnico = (id) => {
    const tecnico = tecnicos.find((t) => String(t.id) === String(id));
    return getTecnicoNombre(tecnico);
  };

  const getEstado = (estado) =>
    ESTADOS[estado] || { label: estado || "—", className: "badge-blue" };

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

  const limpiarFormulario = () => {
    setForm(formInicial);
  };

  const guardarMantenimiento = async () => {
    if (!form.empresa_id) return alert("Seleccione empresa.");
    if (!form.sede_id) return alert("Seleccione sede.");
    if (!form.equipo_id) return alert("Seleccione equipo.");
    if (!form.tecnico_id) return alert("Seleccione técnico responsable.");

    const payload = {
      equipo_id: form.equipo_id,
      tipo: form.tipo,
      descripcion:
        form.descripcion ||
        form.acciones_realizadas ||
        "Mantenimiento registrado desde bitácora profesional.",
      fecha_programada: form.fecha_programada || null,
      observaciones: form.observaciones,
      costo: form.costo ? Number(form.costo) : null,
    };

    try {
      if (form.id) {
        await API.put(`/mantenimientos/${form.id}`, payload);

        if (form.tecnico_id) {
          await API.patch(`/mantenimientos/${form.id}/asignar-tecnico`, {
            tecnico_id: form.tecnico_id,
            observacion: "Técnico actualizado desde bitácora profesional.",
            creado_por: "Administrador SGA",
          });
        }

        alert("Mantenimiento actualizado correctamente.");
      } else {
        const creado = await API.post("/mantenimientos/", payload);

        if (form.tecnico_id && creado?.data?.id) {
          await API.patch(`/mantenimientos/${creado.data.id}/asignar-tecnico`, {
            tecnico_id: form.tecnico_id,
            observacion: "Técnico asignado desde bitácora profesional.",
            creado_por: "Administrador SGA",
          });
        }

        alert("Mantenimiento creado correctamente.");
      }

      limpiarFormulario();
      await cargarTodo();
    } catch (error) {
      console.error("Error guardando mantenimiento:", error);
      alert(error?.response?.data?.detail || "No se pudo guardar.");
    }
  };

  const editarMantenimiento = (m) => {
    const equipo = equipos.find((eq) => String(eq.id) === String(m.equipo_id));

    setForm({
      id: m.id,
      empresa_id: m.empresa_id || equipo?.empresa_id || "",
      sede_id: m.sede_id || equipo?.sede_id || "",
      equipo_id: m.equipo_id || "",
      tecnico_id: m.tecnico_id || "",
      tipo: m.tipo || "PREVENTIVO",
      estado: m.estado || "PROGRAMADO",
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
      costo: m.costo || "",
    });

    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  const eliminarMantenimiento = async (m) => {
    const ok = window.confirm(
      `¿Deseas eliminar definitivamente el mantenimiento #${m.id}?\n\nEsta acción quitará el registro del historial de mantenimientos.`
    );

    if (!ok) return;

    try {
      await API.delete(`/mantenimientos/${m.id}`);
      alert("Mantenimiento eliminado correctamente.");

      const nuevaCantidad = mantenimientosFiltrados.length - 1;
      const nuevasPaginas = Math.max(1, Math.ceil(nuevaCantidad / porPagina));
      if (pagina > nuevasPaginas) setPagina(nuevasPaginas);

      await cargarTodo();
    } catch (error) {
      console.error("Error eliminando mantenimiento:", error);
      alert(error?.response?.data?.detail || "No se pudo eliminar el mantenimiento.");
    }
  };

  const mantenimientosFiltrados = useMemo(() => {
    const q = busqueda.toLowerCase();

    return mantenimientos.filter((m) => {
      const texto = `
        ${m.id}
        ${m.empresa_nombre || getEmpresa(m.empresa_id)}
        ${m.sede_nombre || getSede(m.sede_id)}
        ${m.equipo_nombre || getEquipo(m.equipo_id)}
        ${m.tecnico_nombre || getTecnico(m.tecnico_id)}
        ${m.tipo || ""}
        ${m.estado || ""}
        ${m.resultado_final || ""}
      `.toLowerCase();

      return texto.includes(q);
    });
  }, [mantenimientos, busqueda, empresas, sedes, equipos, tecnicos]);

  const totalPaginas = Math.max(
    1,
    Math.ceil(mantenimientosFiltrados.length / porPagina)
  );

  const visibles = mantenimientosFiltrados.slice(
    (pagina - 1) * porPagina,
    pagina * porPagina
  );

  return (
    <AdminLayout>
      <div className="mant-page">
        <div className="mant-header">
          <div className="mant-header-icon">
            <Wrench size={26} />
          </div>

          <div>
            <h1 className="mant-title">Mantenimientos</h1>
            <p className="mant-subtitle">
              Registra programación, asignación, ejecución y trazabilidad técnica.
            </p>
          </div>

          <button
            className="mant-dashboard-btn"
            onClick={() => (window.location.href = "/admin/dashboard")}
          >
            <ArrowLeft size={16} />
            Dashboard
          </button>
        </div>

        <div className="mant-pro-layout">
          <section className="mant-card mant-form-card">
            <div className="mant-section-header">
              <div>
                <h2>{form.id ? "Editar mantenimiento" : "Crear mantenimiento"}</h2>
                <p>Formulario técnico para mantenimiento preventivo o correctivo.</p>
              </div>

              <button className="mant-reload-btn" onClick={cargarTodo}>
                <RefreshCw size={16} />
                Actualizar
              </button>
            </div>

            <div className="mant-grid-3">
              <Field label="Empresa">
                <select
                  value={form.empresa_id}
                  onChange={(e) =>
                    setForm({
                      ...form,
                      empresa_id: e.target.value,
                      sede_id: "",
                      equipo_id: "",
                    })
                  }
                >
                  <option value="">Seleccione empresa *</option>
                  {empresas.map((e) => (
                    <option key={e.id} value={e.id}>
                      {e.nombre || e.razon_social || `Empresa ${e.id}`}
                    </option>
                  ))}
                </select>
              </Field>

              <Field label="Sede">
                <select
                  value={form.sede_id}
                  onChange={(e) =>
                    setForm({ ...form, sede_id: e.target.value, equipo_id: "" })
                  }
                  disabled={!form.empresa_id}
                >
                  <option value="">
                    {form.empresa_id ? "Seleccione sede *" : "Primero seleccione empresa"}
                  </option>
                  {sedesFiltradas.map((s) => (
                    <option key={s.id} value={s.id}>
                      {s.nombre}
                    </option>
                  ))}
                </select>
              </Field>

              <Field label="Equipo">
                <select
                  value={form.equipo_id}
                  onChange={(e) => setForm({ ...form, equipo_id: e.target.value })}
                  disabled={!form.sede_id}
                >
                  <option value="">
                    {form.sede_id ? "Seleccione equipo *" : "Primero seleccione sede"}
                  </option>
                  {equiposFiltrados.map((eq) => (
                    <option key={eq.id} value={eq.id}>
                      {eq.nombre || eq.codigo_id || eq.codigo || `Equipo ${eq.id}`}
                    </option>
                  ))}
                </select>
              </Field>

              <Field label="Técnico responsable">
                <select
                  value={form.tecnico_id}
                  onChange={(e) => setForm({ ...form, tecnico_id: e.target.value })}
                >
                  <option value="">Seleccione técnico responsable *</option>
                  {tecnicos.map((t) => (
                    <option key={t.id} value={t.id}>
                      {getTecnicoNombre(t)}
                    </option>
                  ))}
                </select>
              </Field>

              <Field label="Tipo de mantenimiento">
                <select
                  value={form.tipo}
                  onChange={(e) => setForm({ ...form, tipo: e.target.value })}
                >
                  <option value="PREVENTIVO">Preventivo</option>
                  <option value="CORRECTIVO">Correctivo</option>
                  <option value="CALIBRACION">Calibración</option>
                  <option value="INSPECCION">Inspección</option>
                </select>
              </Field>

              <Field label="Estado">
                <select
                  value={form.estado}
                  onChange={(e) => setForm({ ...form, estado: e.target.value })}
                >
                  <option value="PROGRAMADO">Programado</option>
                  <option value="ASIGNADO">Asignado</option>
                  <option value="EN_PROCESO">En proceso</option>
                  <option value="PAUSADO">Pausado</option>
                  <option value="FINALIZADO">Finalizado</option>
                  <option value="ANULADO">Anulado</option>
                </select>
              </Field>

              <Field label="Fecha programada">
                <input
                  type="datetime-local"
                  value={form.fecha_programada}
                  onChange={(e) =>
                    setForm({ ...form, fecha_programada: e.target.value })
                  }
                />
              </Field>

              <Field label="Fecha y hora inicio">
                <input
                  type="datetime-local"
                  value={form.fecha_inicio_programada}
                  onChange={(e) =>
                    setForm({ ...form, fecha_inicio_programada: e.target.value })
                  }
                />
              </Field>

              <Field label="Fecha y hora fin">
                <input
                  type="datetime-local"
                  value={form.fecha_fin_programada}
                  onChange={(e) =>
                    setForm({ ...form, fecha_fin_programada: e.target.value })
                  }
                />
              </Field>

              <Field label="Latitud">
                <input
                  placeholder="Latitud"
                  value={form.latitud}
                  onChange={(e) => setForm({ ...form, latitud: e.target.value })}
                />
              </Field>

              <Field label="Longitud">
                <input
                  placeholder="Longitud"
                  value={form.longitud}
                  onChange={(e) => setForm({ ...form, longitud: e.target.value })}
                />
              </Field>

              <Field label="Costo">
                <input
                  type="number"
                  placeholder="0"
                  value={form.costo}
                  onChange={(e) => setForm({ ...form, costo: e.target.value })}
                />
              </Field>
            </div>

            <div className="mant-grid-3 mant-textarea-row">
              <Field label="Estado inicial del equipo / cómo se encontró">
                <textarea
                  value={form.estado_inicial_equipo}
                  onChange={(e) =>
                    setForm({ ...form, estado_inicial_equipo: e.target.value })
                  }
                />
              </Field>

              <Field label="Acciones realizadas">
                <textarea
                  value={form.acciones_realizadas}
                  onChange={(e) =>
                    setForm({ ...form, acciones_realizadas: e.target.value })
                  }
                />
              </Field>

              <Field label="Resultado final">
                <textarea
                  value={form.resultado_final}
                  onChange={(e) =>
                    setForm({ ...form, resultado_final: e.target.value })
                  }
                />
              </Field>
            </div>

            <div className="mant-textarea-row">
              <Field label="Observaciones">
                <textarea
                  value={form.observaciones}
                  onChange={(e) =>
                    setForm({ ...form, observaciones: e.target.value })
                  }
                />
              </Field>
            </div>

            <div className="mant-form-actions">
              <button
                className="mant-save-btn"
                onClick={guardarMantenimiento}
                disabled={loading}
              >
                <Save size={16} />
                {form.id ? "Actualizar mantenimiento" : "Guardar mantenimiento"}
              </button>

              <button className="mant-clear-btn" onClick={limpiarFormulario}>
                Limpiar
              </button>
            </div>
          </section>

          <section className="mant-card mant-list-card">
            <div className="mant-section-header">
              <div>
                <h2>Historial de mantenimientos</h2>
                <p>Consulta, búsqueda, edición y eliminación segura.</p>
              </div>

              <span className="mant-counter">
                {mantenimientosFiltrados.length} registros
              </span>
            </div>

            <div className="mant-search-box">
              <Search size={16} />
              <input
                placeholder="Buscar por empresa, sede, equipo, técnico, tipo o resultado"
                value={busqueda}
                onChange={(e) => {
                  setBusqueda(e.target.value);
                  setPagina(1);
                }}
              />
            </div>

            <div className="mant-table-wrap">
              <table className="mant-table">
                <thead>
                  <tr>
                    <th>Empresa</th>
                    <th>Sede</th>
                    <th>Equipo</th>
                    <th>Técnico</th>
                    <th>Tipo</th>
                    <th>Estado</th>
                    <th>Inicio</th>
                    <th>Fin</th>
                    <th>Resultado</th>
                    <th>Acciones</th>
                  </tr>
                </thead>

                <tbody>
                  {visibles.map((m) => {
                    const estado = getEstado(m.estado);

                    return (
                      <tr key={m.id}>
                        <td>{m.empresa_nombre || getEmpresa(m.empresa_id)}</td>
                        <td>{m.sede_nombre || getSede(m.sede_id)}</td>
                        <td>{m.equipo_nombre || getEquipo(m.equipo_id)}</td>
                        <td>{m.tecnico_nombre || getTecnico(m.tecnico_id)}</td>
                        <td>
                          <span className="mant-type-badge">{m.tipo}</span>
                        </td>
                        <td>
                          <span className={`mant-badge ${estado.className}`}>
                            {estado.label}
                          </span>
                        </td>
                        <td>{formatearFecha(m.fecha_inicio || m.fecha_programada)}</td>
                        <td>{formatearFecha(m.fecha_finalizacion)}</td>
                        <td>{m.resultado_final || m.observacion_estado || "—"}</td>
                        <td>
                          <div className="mant-actions">
                            <button
                              className="mant-view-btn"
                              onClick={() => setDetalle(m)}
                            >
                              <Eye size={14} /> Ver
                            </button>

                            <button
                              className="mant-edit-btn"
                              onClick={() => editarMantenimiento(m)}
                            >
                              <Edit size={14} /> Editar
                            </button>

                            <button
                              className="mant-delete-btn"
                              onClick={() => eliminarMantenimiento(m)}
                            >
                              <Trash2 size={14} /> Eliminar
                            </button>
                          </div>
                        </td>
                      </tr>
                    );
                  })}

                  {visibles.length === 0 && (
                    <tr>
                      <td colSpan="10" className="mant-empty">
                        No hay mantenimientos registrados.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>

            <div className="mant-pagination">
              <button disabled={pagina === 1} onClick={() => setPagina(pagina - 1)}>
                <ChevronLeft size={16} /> Anterior
              </button>

              <span>
                Página {pagina} de {totalPaginas}
              </span>

              <button
                disabled={pagina === totalPaginas}
                onClick={() => setPagina(pagina + 1)}
              >
                Siguiente <ChevronRight size={16} />
              </button>
            </div>
          </section>
        </div>

        {detalle && (
          <div className="mant-overlay">
            <div className="mant-modal">
              <div className="mant-modal-header">
                <h2>Detalle del mantenimiento</h2>
                <button onClick={() => setDetalle(null)}>
                  <X size={18} />
                </button>
              </div>

              <div className="mant-detail-grid">
                <Detail label="Empresa" value={detalle.empresa_nombre || getEmpresa(detalle.empresa_id)} />
                <Detail label="Sede" value={detalle.sede_nombre || getSede(detalle.sede_id)} />
                <Detail label="Equipo" value={detalle.equipo_nombre || getEquipo(detalle.equipo_id)} />
                <Detail label="Técnico" value={detalle.tecnico_nombre || getTecnico(detalle.tecnico_id)} />
                <Detail label="Tipo" value={detalle.tipo} />
                <Detail label="Estado" value={detalle.estado} />
                <Detail label="Fecha programada" value={formatearFecha(detalle.fecha_programada)} />
                <Detail label="Observaciones" value={detalle.observaciones} />
              </div>
            </div>
          </div>
        )}
      </div>
    </AdminLayout>
  );
}

function Field({ label, children }) {
  return (
    <label className="mant-field">
      <span>{label}</span>
      {children}
    </label>
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