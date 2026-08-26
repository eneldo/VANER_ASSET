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

import { useCallback, useEffect, useEffectEvent, useMemo, useState } from "react";
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
import {
  construirEtiquetaEquipo,
  encontrarUbicacionDisponible,
  filtrarEquiposPorUbicacion,
  listarUbicacionesEquipos,
  obtenerEtiquetaUbicacionEquipo,
  obtenerValorUbicacionEquipo,
} from "./mantenimientosEquipoUtils";
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
  activeCompanyId = "",
  onCompanyChange,
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
  const [porPagina] = useState(6);
  const [loading, setLoading] = useState(false);
  const [detalle, setDetalle] = useState(null);
  const cargarTodoAlMontar = useEffectEvent(() => cargarTodo());

  useEffect(() => {
    cargarTodoAlMontar();
  }, []);

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
        const empresaPredeterminada = activeCompanyId
          || (empresasCoordinador.length === 1 ? empresasCoordinador[0].id : "");
        setForm((actual) => (
          actual.id || actual.empresa_id || !empresaPredeterminada
            ? actual
            : { ...actual, empresa_id: empresaPredeterminada }
        ));
      } else {
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
      }
    } catch (error) {
      console.error("Error cargando módulo mantenimientos:", error);
      alert("Error cargando datos del módulo de mantenimientos.");
    } finally {
      setLoading(false);
    }
  };

  async function reabrirMantenimiento(mantenimiento) {
    const motivoIngresado = window.prompt(
      "Indica el motivo de la reapertura. El mantenimiento volverá a EN PROCESO:",
    );
    if (motivoIngresado === null) return;

    const motivo = motivoIngresado.trim();
    if (motivo.length < 10) {
      alert("El motivo debe tener al menos 10 caracteres.");
      return;
    }

    try {
      setLoading(true);
      if (esCoordinador) {
        await API.put(`/coordinador/mantenimientos/${mantenimiento.id}/estado`, null, {
          params: { estado: "EN_PROCESO", observacion: motivo },
        });
      } else {
        await API.patch("/mantenimientos/" + mantenimiento.id + "/cambiar-estado", {
          estado_nuevo: "EN_PROCESO",
          observacion: motivo,
          creado_por: "Administrador",
        });
      }
      setDetalle(null);
      await cargarTodo();
      alert("Mantenimiento reabierto correctamente.");
    } catch (error) {
      console.error("Error reabriendo mantenimiento:", error);
      alert(error?.response?.data?.detail || "No se pudo reabrir el mantenimiento.");
    } finally {
      setLoading(false);
    }
  }

  const sedesFiltradas = useMemo(() => {
    if (!form.empresa_id) return [];
    return sedes.filter((s) => String(s.empresa_id) === String(form.empresa_id));
  }, [sedes, form.empresa_id]);

  const ubicacionesEquipos = useMemo(
    () => listarUbicacionesEquipos(equipos, form.sede_id),
    [equipos, form.sede_id]
  );

  const ubicacionSeleccionada = useMemo(
    () => encontrarUbicacionDisponible(ubicacionesEquipos, form.ubicacion_equipo),
    [ubicacionesEquipos, form.ubicacion_equipo]
  );

  const equiposFiltrados = useMemo(
    () =>
      filtrarEquiposPorUbicacion(
        equipos,
        form.sede_id,
        ubicacionSeleccionada?.value || ""
      ),
    [equipos, form.sede_id, ubicacionSeleccionada]
  );

  const equipoSeleccionado = useMemo(
    () => equipos.find((equipo) => String(equipo.id) === String(form.equipo_id)) || null,
    [equipos, form.equipo_id]
  );

  const getEmpresa = useCallback((id) => {
    const empresa = empresas.find((e) => String(e.id) === String(id));
    return empresa?.nombre || empresa?.razon_social || "—";
  }, [empresas]);

  const getSede = useCallback((id) => {
    const sede = sedes.find((s) => String(s.id) === String(id));
    return sede?.nombre || "—";
  }, [sedes]);

  const getEquipoData = useCallback((id) => {
    return equipos.find((equipo) => String(equipo.id) === String(id)) || null;
  }, [equipos]);

  const getEquipo = useCallback((id, fallback = "") => {
    const equipo = equipos.find((item) => String(item.id) === String(id));
    return equipo ? construirEtiquetaEquipo(equipo) : fallback || "—";
  }, [equipos]);

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

  const getTecnico = useCallback((id) => {
    const tecnico = tecnicos.find((t) => String(t.id) === String(id));
    return getTecnicoNombre(tecnico);
  }, [tecnicos]);

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

  const asignarTecnicoMantenimiento = (mantenimientoId, data) => {
    if (esCoordinador) {
      return API.put(`/coordinador/mantenimientos/${mantenimientoId}/asignar`, null, {
        params: { tecnico_id: data.tecnico_id },
      });
    }

    return API.patch(`/mantenimientos/${mantenimientoId}/asignar-tecnico`, data);
  };

  const guardarMantenimiento = async () => {
    if (!form.empresa_id) return alert("Seleccione empresa.");
    if (!form.sede_id) return alert("Seleccione sede.");
    if (!ubicacionSeleccionada) {
      return alert("Escriba o seleccione una ubicación disponible de la lista.");
    }
    if (!form.equipo_id) return alert("Seleccione equipo.");
    if (!form.tecnico_id) return alert("Seleccione técnico responsable.");

    const payload = {
      equipo_id: form.equipo_id,
      tipo: form.tipo,
      descripcion:
        form.descripcion ||
        form.acciones_realizadas ||
        "Mantenimiento registrado desde bitácora profesional.",
      prioridad: form.prioridad || "MEDIA",
      fecha_programada: form.fecha_programada || null,
      fecha_inicio_programada: form.fecha_inicio_programada || null,
      fecha_fin_programada: form.fecha_fin_programada || null,
      observaciones: form.observaciones,
      estado_inicial_equipo: form.estado_inicial_equipo || null,
      acciones_realizadas: form.acciones_realizadas || null,
      resultado_final: form.resultado_final || null,
      falla_incidencia: form.falla_incidencia || null,
      diagnostico: form.diagnostico || null,
      trabajo_realizado: form.trabajo_realizado || null,
      latitud: form.latitud || null,
      longitud: form.longitud || null,
      costo: form.costo ? Number(form.costo) : null,
      costo_mano_obra: form.costo_mano_obra ? Number(form.costo_mano_obra) : null,
      costo_repuestos: form.costo_repuestos ? Number(form.costo_repuestos) : null,
      costo_total: form.costo_total ? Number(form.costo_total) : null,
      solucion: form.solucion || null,
    };

    try {
      if (form.id) {
        await API.put(
          esCoordinador
            ? `/coordinador/mantenimientos/${form.id}`
            : `/mantenimientos/${form.id}`,
          payload,
        );

        if (form.tecnico_id) {
          await asignarTecnicoMantenimiento(form.id, {
            tecnico_id: form.tecnico_id,
            observacion: "Técnico actualizado desde bitácora profesional.",
            creado_por: "Administrador SGA",
          });
        }

        alert("Mantenimiento actualizado correctamente.");
      } else {
        const creado = await API.post(
          esCoordinador ? "/coordinador/mantenimientos" : "/mantenimientos/",
          payload,
        );

        if (form.tecnico_id && creado?.data?.id) {
          await asignarTecnicoMantenimiento(creado.data.id, {
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

    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  const eliminarMantenimiento = async (m) => {
    const ok = window.confirm(
      `¿Deseas eliminar definitivamente el mantenimiento #${m.id}?\n\nEsta acción quitará el registro del historial de mantenimientos.`
    );

    if (!ok) return;

    try {
      await API.delete(
        esCoordinador
          ? `/coordinador/mantenimientos/${m.id}`
          : `/mantenimientos/${m.id}`,
      );
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
        ${getEquipo(m.equipo_id, m.equipo_nombre)}
        ${m.tecnico_nombre || getTecnico(m.tecnico_id)}
        ${m.tipo || ""}
        ${m.estado || ""}
        ${m.resultado_final || ""}
      `.toLowerCase();

      return texto.includes(q);
    });
  }, [mantenimientos, busqueda, getEmpresa, getSede, getEquipo, getTecnico]);

  const totalPaginas = Math.max(
    1,
    Math.ceil(mantenimientosFiltrados.length / porPagina)
  );

  const visibles = mantenimientosFiltrados.slice(
    (pagina - 1) * porPagina,
    pagina * porPagina
  );

  const equipoDetalle = detalle ? getEquipoData(detalle.equipo_id) : null;

  const contenido = (
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
            onClick={() => (
              window.location.href = esCoordinador
                ? "/coordinador/dashboard"
                : "/admin/dashboard"
            )}
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
                  onChange={(e) => {
                    const empresaId = e.target.value;
                    if (esCoordinador && onCompanyChange) {
                      onCompanyChange(empresaId);
                      return;
                    }
                    setForm({
                      ...form,
                      empresa_id: empresaId,
                      sede_id: "",
                      ubicacion_equipo: "",
                      equipo_id: "",
                    });
                  }}
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
                    setForm({
                      ...form,
                      sede_id: e.target.value,
                      ubicacion_equipo: "",
                      equipo_id: "",
                    })
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

              <Field label="Ubicación del equipo">
                <input
                  type="search"
                  list="mant-ubicaciones-equipo"
                  value={form.ubicacion_equipo}
                  placeholder={
                    form.sede_id
                      ? "Escriba o seleccione una ubicación *"
                      : "Primero seleccione sede"
                  }
                  onChange={(e) =>
                    setForm({
                      ...form,
                      ubicacion_equipo: e.target.value,
                      equipo_id: "",
                    })
                  }
                  disabled={!form.sede_id}
                  autoComplete="off"
                />
                <datalist id="mant-ubicaciones-equipo">
                  {ubicacionesEquipos.map((ubicacion) => (
                    <option key={ubicacion.value} value={ubicacion.label} />
                  ))}
                </datalist>
                <small
                  className={`mant-field-help ${
                    form.ubicacion_equipo && !ubicacionSeleccionada ? "is-error" : ""
                  }`}
                >
                  {!form.sede_id
                    ? "Seleccione primero una sede."
                    : ubicacionesEquipos.length === 0
                      ? "Esta sede no tiene ubicaciones de equipos registradas."
                      : form.ubicacion_equipo && !ubicacionSeleccionada
                        ? "Seleccione una ubicación disponible de la lista."
                        : "Escriba para buscar o abra la lista para seleccionar."}
                </small>
              </Field>

              <Field label="Equipo específico">
                <select
                  value={form.equipo_id}
                  onChange={(e) => setForm({ ...form, equipo_id: e.target.value })}
                  disabled={!ubicacionSeleccionada}
                >
                  <option value="">
                    {ubicacionSeleccionada
                      ? "Seleccione equipo *"
                      : "Primero seleccione ubicación"}
                  </option>
                  {equiposFiltrados.map((eq) => (
                    <option key={eq.id} value={eq.id}>
                      {construirEtiquetaEquipo(eq)}
                    </option>
                  ))}
                </select>
              </Field>

              <div className={`mant-equipment-preview ${equipoSeleccionado ? "" : "is-empty"}`}>
                {equipoSeleccionado ? (
                  <>
                    <div className="mant-equipment-preview-title">
                      <span>Equipo seleccionado</span>
                      <strong>{equipoSeleccionado.nombre || "Equipo sin nombre"}</strong>
                    </div>
                    <div className="mant-equipment-preview-data">
                      <span><b>Ubicación:</b> {equipoSeleccionado.ubicacion || "Sin registrar"}</span>
                      <span><b>Inventario:</b> {equipoSeleccionado.inventario || "Sin inventario"}</span>
                      <span><b>Código:</b> {equipoSeleccionado.codigo_id || equipoSeleccionado.codigo || "Sin código"}</span>
                      <span><b>Serie:</b> {equipoSeleccionado.serie || "Sin serie"}</span>
                    </div>
                  </>
                ) : (
                  <span>Seleccione una ubicación y un equipo para confirmar el activo exacto.</span>
                )}
              </div>

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

              <Field label="Prioridad">
                <select
                  value={form.prioridad}
                  onChange={(e) => setForm({ ...form, prioridad: e.target.value })}
                >
                  <option value="BAJA">Baja</option>
                  <option value="MEDIA">Media</option>
                  <option value="ALTA">Alta</option>
                  <option value="CRITICA">Crítica</option>
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

              {!esCoordinador && (
                <>
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
                </>
              )}
            </div>

            {esCoordinador && (
              <details className="mant-optional-panel">
                <summary>Datos administrativos opcionales</summary>
                <Field label="Costo estimado">
                  <input
                    type="number"
                    placeholder="0"
                    value={form.costo}
                    onChange={(e) => setForm({ ...form, costo: e.target.value })}
                  />
                </Field>
              </details>
            )}

            {!esCoordinador && (
            <div className="mant-grid-3 mant-textarea-row">
              <Field label="Estado inicial del equipo / cómo se encontró">
                <textarea
                  value={form.estado_inicial_equipo}
                  onChange={(e) =>
                    setForm({ ...form, estado_inicial_equipo: e.target.value })
                  }
                />
              </Field>

              <Field label="Falla / incidencia reportada">
                <textarea
                  value={form.falla_incidencia}
                  onChange={(e) =>
                    setForm({ ...form, falla_incidencia: e.target.value })
                  }
                />
              </Field>

              <Field label="Diagnóstico técnico">
                <textarea
                  value={form.diagnostico}
                  onChange={(e) =>
                    setForm({ ...form, diagnostico: e.target.value })
                  }
                />
              </Field>
            </div>
            )}

            {!esCoordinador && (
            <div className="mant-grid-3 mant-textarea-row">
              <Field label="Trabajo realizado">
                <textarea
                  value={form.trabajo_realizado}
                  onChange={(e) =>
                    setForm({ ...form, trabajo_realizado: e.target.value })
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
            )}

            {!esCoordinador && (
              <div className="mant-grid-3 mant-textarea-row">
                <Field label="Costo mano de obra">
                  <input
                    type="number"
                    placeholder="0"
                    value={form.costo_mano_obra}
                    onChange={(e) => setForm({ ...form, costo_mano_obra: e.target.value })}
                  />
                </Field>

                <Field label="Costo repuestos">
                  <input
                    type="number"
                    placeholder="0"
                    value={form.costo_repuestos}
                    onChange={(e) => setForm({ ...form, costo_repuestos: e.target.value })}
                  />
                </Field>

                <Field label="Costo total">
                  <input
                    type="number"
                    placeholder="0"
                    value={form.costo_total}
                    onChange={(e) => setForm({ ...form, costo_total: e.target.value })}
                  />
                </Field>
              </div>
            )}

            {!esCoordinador && (
              <div className="mant-textarea-row">
                <Field label="Solución aplicada">
                  <textarea
                    value={form.solucion}
                    onChange={(e) =>
                      setForm({ ...form, solucion: e.target.value })
                    }
                  />
                </Field>
              </div>
            )}

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
                placeholder="Buscar por empresa, sede, ubicación, inventario, equipo o técnico"
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
                        <td className="mant-equipment-cell">
                          {getEquipo(m.equipo_id, m.equipo_nombre)}
                        </td>
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

                            {String(m.estado || "").toUpperCase() === "FINALIZADO" && (
                              <button
                                className="mant-edit-btn"
                                onClick={() => reabrirMantenimiento(m)}
                                disabled={loading}
                              >
                                <RefreshCw size={14} /> Reabrir
                              </button>
                            )}

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
                <Detail label="Equipo" value={equipoDetalle?.nombre || detalle.equipo_nombre} />
                <Detail label="Ubicación del equipo" value={equipoDetalle?.ubicacion} />
                <Detail
                  label="Inventario"
                  value={equipoDetalle?.inventario || "Sin inventario registrado"}
                />
                <Detail
                  label="Código interno"
                  value={equipoDetalle?.codigo_id || equipoDetalle?.codigo}
                />
                <Detail label="Serie" value={equipoDetalle?.serie} />
                <Detail label="Técnico" value={detalle.tecnico_nombre || getTecnico(detalle.tecnico_id)} />
                <Detail label="Tipo" value={detalle.tipo} />
                <Detail label="Prioridad" value={detalle.prioridad} />
                <Detail label="Estado" value={detalle.estado} />
                <Detail label="Cerrado" value={detalle.cerrado ? "Sí" : "No"} />
                <Detail label="Fecha programada" value={formatearFecha(detalle.fecha_programada)} />
                <Detail label="Fecha cierre" value={formatearFecha(detalle.fecha_cierre)} />
                <Detail label="Falla / incidencia" value={detalle.falla_incidencia} />
                <Detail label="Diagnóstico" value={detalle.diagnostico} />
                <Detail label="Trabajo realizado" value={detalle.trabajo_realizado} />
                <Detail label="Solución" value={detalle.solucion} />
                <Detail label="Costo mano de obra" value={detalle.costo_mano_obra} />
                <Detail label="Costo repuestos" value={detalle.costo_repuestos} />
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
