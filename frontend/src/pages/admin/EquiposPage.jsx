import React, { useEffect, useMemo, useState } from "react";
import {
  Search,
  Plus,
  Pencil,
  Trash2,
  MonitorCog,
  ShieldAlert,
  CircleCheckBig,
  RefreshCw,
  Eye,
  X,
  Save,
  ChevronRight,
  ChevronLeft,
} from "lucide-react";

import AdminLayout from "./AdminLayout";
import "../../styles/equipos-saas-pro-enterprise.css";

const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

const equipoInicial = {
  empresa_id: "",
  sede_id: "",
  categoria_id: "",
  nombre: "",
  marca: "",
  modelo: "",
  serie: "",
  ubicacion: "",
  invima: "",
  codigo_id: "",
  inventario: "",
  estado: "OPERATIVO",
  criticidad: "MEDIA",
  activo: true,
};

const hojaInicial = {
  adquisicion: "",
  costo: "",
  fecha_compra: "",
  fecha_instalacion: "",
  proveedor: "",
  pais_fabricacion: "",
  fecha_fabricacion: "",
  vida_util: "",
  requiere_calibracion: false,
  rango_voltaje: "",
  rango_presion: "",
  gas_refrigerante: "",
  capacidad: "",
  rango_corriente: "",
  rango_velocidad: "",
  rango_potencia: "",
  rango_temperatura: "",
  frecuencia: "",
  rango_humedad: "",
  otros: "",
  manual_operacion: false,
  manual_mantenimiento: false,
  manual_partes: false,
  manual_despiece: false,
  plano_electronico: false,
  plano_electrico: false,
  plano_neumatico: false,
  plano_mecanico: false,
  clase_diagnostico: false,
  clase_prevencion: false,
  clase_rehabilitacion: false,
  clase_analisis: false,
  riesgo_bajo: false,
  riesgo_moderado: false,
  riesgo_alto: false,
  riesgo_elevado: false,
};

function getToken() {
  return localStorage.getItem("access_token") || localStorage.getItem("token");
}

function authHeaders() {
  const token = getToken();
  return {
    "Content-Type": "application/json",
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
}

function textoEstado(estado) {
  const map = {
    OPERATIVO: "Operativo",
    EN_MANTENIMIENTO: "En mantenimiento",
    FUERA_DE_SERVICIO: "Fuera de servicio",
    BAJA: "Baja",
  };
  return map[estado] || estado || "N/A";
}

function estadoClass(estado) {
  if (estado === "OPERATIVO") return "operativo";
  if (estado === "EN_MANTENIMIENTO") return "mantenimiento";
  if (estado === "FUERA_DE_SERVICIO") return "fuera_servicio";
  if (estado === "BAJA") return "baja";
  return "default";
}

function criticidadClass(valor) {
  return String(valor || "media").toLowerCase();
}

function limpiarPayload(obj) {
  const data = {};

  Object.entries(obj).forEach(([key, value]) => {
    if (value === "") data[key] = null;
    else data[key] = value;
  });

  return data;
}

export default function EquiposPage() {
  const [equipos, setEquipos] = useState([]);
  const [empresas, setEmpresas] = useState([]);
  const [sedes, setSedes] = useState([]);
  const [categorias, setCategorias] = useState([]);

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  const [busqueda, setBusqueda] = useState("");
  const [paginaActual, setPaginaActual] = useState(1);
  const equiposPorPagina = 10;

  const [modalAbierto, setModalAbierto] = useState(false);
  const [paso, setPaso] = useState(1);
  const [equipoForm, setEquipoForm] = useState(equipoInicial);
  const [hojaForm, setHojaForm] = useState(hojaInicial);
  const [equipoCreadoId, setEquipoCreadoId] = useState(null);
  const [editandoId, setEditandoId] = useState(null);
  const [detalle, setDetalle] = useState(null);

  const [mensaje, setMensaje] = useState("");
  const [error, setError] = useState("");

  const cargarCatalogos = async () => {
    const [empresasRes, sedesRes, categoriasRes] = await Promise.all([
      fetch(`${API_URL}/empresas/`, { headers: authHeaders() }),
      fetch(`${API_URL}/sedes/`, { headers: authHeaders() }),
      fetch(`${API_URL}/categorias/`, { headers: authHeaders() }),
    ]);

    if (!empresasRes.ok || !sedesRes.ok || !categoriasRes.ok) {
      throw new Error("No fue posible cargar empresas, sedes o categorías.");
    }

    setEmpresas(await empresasRes.json());
    setSedes(await sedesRes.json());
    setCategorias(await categoriasRes.json());
  };

  const cargarEquipos = async () => {
    try {
      setLoading(true);
      setError("");

      const response = await fetch(`${API_URL}/equipos/`, {
        headers: authHeaders(),
      });

      if (!response.ok) throw new Error("Error cargando equipos.");

      setEquipos(await response.json());
    } catch (err) {
      console.error(err);
      setError(err.message || "Error cargando equipos.");
    } finally {
      setLoading(false);
    }
  };

  const cargarTodo = async () => {
    try {
      setLoading(true);
      await Promise.all([cargarCatalogos(), cargarEquipos()]);
    } catch (err) {
      console.error(err);
      setError(err.message || "Error cargando información.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    cargarTodo();
  }, []);

  const sedesFiltradas = useMemo(() => {
    if (!equipoForm.empresa_id) return [];
    return sedes.filter(
      (sede) => String(sede.empresa_id) === String(equipoForm.empresa_id)
    );
  }, [sedes, equipoForm.empresa_id]);

  const equiposFiltrados = useMemo(() => {
    const term = busqueda.toLowerCase();

    return equipos.filter((equipo) => {
      const texto = `
        ${equipo.nombre || ""}
        ${equipo.marca || ""}
        ${equipo.modelo || ""}
        ${equipo.serie || ""}
        ${equipo.codigo_id || ""}
        ${equipo.inventario || ""}
        ${equipo.ubicacion || ""}
      `.toLowerCase();

      return texto.includes(term);
    });
  }, [equipos, busqueda]);

  const totalPaginas = Math.max(
    1,
    Math.ceil(equiposFiltrados.length / equiposPorPagina)
  );

  const equiposPaginados = equiposFiltrados.slice(
    (paginaActual - 1) * equiposPorPagina,
    paginaActual * equiposPorPagina
  );

  const totalEquipos = equipos.length;
  const operativos = equipos.filter((e) => e.estado === "OPERATIVO").length;
  const mantenimiento = equipos.filter(
    (e) => e.estado === "EN_MANTENIMIENTO"
  ).length;
  const fueraServicio = equipos.filter(
    (e) => e.estado === "FUERA_DE_SERVICIO"
  ).length;

  const abrirNuevoEquipo = () => {
    setModalAbierto(true);
    setPaso(1);
    setEquipoForm(equipoInicial);
    setHojaForm(hojaInicial);
    setEquipoCreadoId(null);
    setEditandoId(null);
    setMensaje("");
    setError("");
  };

  const cerrarModal = () => {
    setModalAbierto(false);
    setPaso(1);
    setEquipoForm(equipoInicial);
    setHojaForm(hojaInicial);
    setEquipoCreadoId(null);
    setEditandoId(null);
  };

  const handleEquipoChange = (e) => {
    const { name, value, type, checked } = e.target;

    setEquipoForm((prev) => ({
      ...prev,
      [name]: type === "checkbox" ? checked : value,
      ...(name === "empresa_id" ? { sede_id: "" } : {}),
    }));
  };

  const handleHojaChange = (e) => {
    const { name, value, type, checked } = e.target;

    setHojaForm((prev) => ({
      ...prev,
      [name]: type === "checkbox" ? checked : value,
    }));
  };

  const validarPaso1 = () => {
    if (!equipoForm.empresa_id) return "Selecciona una empresa.";
    if (!equipoForm.sede_id) return "Selecciona una sede.";
    if (!equipoForm.nombre.trim()) return "El nombre del equipo es obligatorio.";
    return null;
  };

  const guardarPaso1 = async () => {
    const validacion = validarPaso1();
    if (validacion) {
      setError(validacion);
      return;
    }

    try {
      setSaving(true);
      setError("");
      setMensaje("");

      const payload = limpiarPayload(equipoForm);

      const url = editandoId
        ? `${API_URL}/equipos/${editandoId}`
        : `${API_URL}/equipos/`;

      const response = await fetch(url, {
        method: editandoId ? "PUT" : "POST",
        headers: authHeaders(),
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        const data = await response.json().catch(() => null);
        throw new Error(data?.detail || "No fue posible guardar el equipo.");
      }

      const equipoGuardado = await response.json();

      setEquipoCreadoId(equipoGuardado.id);
      setMensaje("Paso 1 guardado correctamente. Continúa con la hoja de vida.");
      setPaso(2);

      await cargarEquipos();
    } catch (err) {
      console.error(err);
      setError(err.message || "Error guardando equipo.");
    } finally {
      setSaving(false);
    }
  };

  const guardarHojaVida = async () => {
    const idEquipo = equipoCreadoId || editandoId;

    if (!idEquipo) {
      setError("Primero debes guardar los datos básicos del equipo.");
      return;
    }

    try {
      setSaving(true);
      setError("");
      setMensaje("");

      const payload = {
        equipo_id: idEquipo,
        ...limpiarPayload(hojaForm),
        costo: hojaForm.costo === "" ? null : Number(hojaForm.costo),
      };

      const response = await fetch(`${API_URL}/equipo-hoja-vida/`, {
        method: "POST",
        headers: authHeaders(),
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        const data = await response.json().catch(() => null);

        if (
          response.status === 400 &&
          String(data?.detail || "").includes("ya tiene hoja")
        ) {
          setMensaje("El equipo ya tenía hoja de vida técnica registrada.");
          cerrarModal();
          await cargarEquipos();
          return;
        }

        throw new Error(data?.detail || "No fue posible guardar la hoja de vida.");
      }

      setMensaje("Equipo y hoja de vida creados correctamente.");
      cerrarModal();
      await cargarEquipos();
    } catch (err) {
      console.error(err);
      setError(err.message || "Error guardando hoja de vida.");
    } finally {
      setSaving(false);
    }
  };

  const editarEquipo = (equipo) => {
    setEditandoId(equipo.id);
    setEquipoCreadoId(equipo.id);
    setPaso(1);
    setModalAbierto(true);
    setMensaje("");
    setError("");

    setEquipoForm({
      empresa_id: equipo.empresa_id || "",
      sede_id: equipo.sede_id || "",
      categoria_id: equipo.categoria_id || "",
      nombre: equipo.nombre || "",
      marca: equipo.marca || "",
      modelo: equipo.modelo || "",
      serie: equipo.serie || "",
      ubicacion: equipo.ubicacion || "",
      invima: equipo.invima || "",
      codigo_id: equipo.codigo_id || "",
      inventario: equipo.inventario || "",
      estado: equipo.estado || "OPERATIVO",
      criticidad: equipo.criticidad || "MEDIA",
      activo: equipo.activo ?? true,
    });
  };

  const eliminarEquipo = async (equipo) => {
    const confirmar = window.confirm(
      `¿Eliminar el equipo "${equipo.nombre}"?\n\nEsta acción puede afectar mantenimientos e historial.`
    );

    if (!confirmar) return;

    try {
      setSaving(true);

      const response = await fetch(`${API_URL}/equipos/${equipo.id}`, {
        method: "DELETE",
        headers: authHeaders(),
      });

      if (!response.ok) {
        const data = await response.json().catch(() => null);
        throw new Error(data?.detail || "No fue posible eliminar el equipo.");
      }

      setMensaje("Equipo eliminado correctamente.");
      await cargarEquipos();
    } catch (err) {
      console.error(err);
      setError(err.message || "Error eliminando equipo.");
    } finally {
      setSaving(false);
    }
  };

  const nombreEmpresa = (id) =>
    empresas.find((e) => String(e.id) === String(id))?.nombre || "N/A";

  const nombreSede = (id) =>
    sedes.find((s) => String(s.id) === String(id))?.nombre || "N/A";

  const nombreCategoria = (id) =>
    categorias.find((c) => String(c.id) === String(id))?.nombre || "Sin categoría";

  return (
    <AdminLayout>
      <div className="equipos-enterprise-page">
        <div className="enterprise-header">
          <div>
            <h1>Inventario de Equipos</h1>
            <p>Gestión empresarial de activos, mantenimiento y criticidad.</p>
          </div>

          <button className="btn-primary-enterprise" onClick={abrirNuevoEquipo}>
            <Plus size={18} />
            Nuevo Equipo
          </button>
        </div>

        {mensaje && <div className="enterprise-alert success">{mensaje}</div>}
        {error && <div className="enterprise-alert error">{error}</div>}

        <div className="enterprise-kpis">
          <div className="enterprise-kpi-card">
            <div className="kpi-icon blue">
              <MonitorCog size={28} />
            </div>
            <div>
              <h3>Total Equipos</h3>
              <h2>{totalEquipos}</h2>
            </div>
          </div>

          <div className="enterprise-kpi-card">
            <div className="kpi-icon green">
              <CircleCheckBig size={28} />
            </div>
            <div>
              <h3>Operativos</h3>
              <h2>{operativos}</h2>
            </div>
          </div>

          <div className="enterprise-kpi-card">
            <div className="kpi-icon orange">
              <RefreshCw size={28} />
            </div>
            <div>
              <h3>Mantenimiento</h3>
              <h2>{mantenimiento}</h2>
            </div>
          </div>

          <div className="enterprise-kpi-card">
            <div className="kpi-icon red">
              <ShieldAlert size={28} />
            </div>
            <div>
              <h3>Fuera Servicio</h3>
              <h2>{fueraServicio}</h2>
            </div>
          </div>
        </div>

        <div className="enterprise-toolbar">
          <div className="search-enterprise">
            <Search size={18} />
            <input
              type="text"
              placeholder="Buscar equipo..."
              value={busqueda}
              onChange={(e) => {
                setBusqueda(e.target.value);
                setPaginaActual(1);
              }}
            />
          </div>
        </div>

        <div className="enterprise-table-wrapper">
          <table className="enterprise-table">
            <thead>
              <tr>
                <th>Código</th>
                <th>Equipo</th>
                <th>Empresa</th>
                <th>Sede</th>
                <th>Marca</th>
                <th>Modelo</th>
                <th>Serie</th>
                <th>Estado</th>
                <th>Criticidad</th>
                <th>Acciones</th>
              </tr>
            </thead>

            <tbody>
              {loading ? (
                <tr>
                  <td colSpan="10">
                    <div className="loading-enterprise">Cargando equipos...</div>
                  </td>
                </tr>
              ) : equiposPaginados.length === 0 ? (
                <tr>
                  <td colSpan="10">
                    <div className="empty-enterprise">
                      No existen equipos registrados.
                    </div>
                  </td>
                </tr>
              ) : (
                equiposPaginados.map((equipo) => (
                  <tr key={equipo.id}>
                    <td>{equipo.codigo_id || equipo.inventario || "N/A"}</td>

                    <td>
                      <div className="equipo-cell">
                        <div className="equipo-avatar">
                          <MonitorCog size={18} />
                        </div>
                        <div>
                          <strong>{equipo.nombre}</strong>
                          <span>{equipo.ubicacion || "Sin ubicación"}</span>
                        </div>
                      </div>
                    </td>

                    <td>{nombreEmpresa(equipo.empresa_id)}</td>
                    <td>{nombreSede(equipo.sede_id)}</td>
                    <td>{equipo.marca || "N/A"}</td>
                    <td>{equipo.modelo || "N/A"}</td>
                    <td>{equipo.serie || "N/A"}</td>

                    <td>
                      <span className={`estado-badge ${estadoClass(equipo.estado)}`}>
                        {textoEstado(equipo.estado)}
                      </span>
                    </td>

                    <td>
                      <span
                        className={`criticidad-badge ${criticidadClass(
                          equipo.criticidad
                        )}`}
                      >
                        {equipo.criticidad || "MEDIA"}
                      </span>
                    </td>

                    <td>
                      <div className="acciones-enterprise">
                        <button
                          className="btn-action blue"
                          onClick={() => setDetalle(equipo)}
                          title="Ver"
                        >
                          <Eye size={16} />
                        </button>

                        <button
                          className="btn-action orange"
                          onClick={() => editarEquipo(equipo)}
                          title="Editar"
                        >
                          <Pencil size={16} />
                        </button>

                        <button
                          className="btn-action red"
                          onClick={() => eliminarEquipo(equipo)}
                          title="Eliminar"
                        >
                          <Trash2 size={16} />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        <div className="enterprise-pagination">
          <button
            disabled={paginaActual === 1}
            onClick={() => setPaginaActual((prev) => Math.max(1, prev - 1))}
          >
            Anterior
          </button>

          <span>
            Página {paginaActual} de {totalPaginas}
          </span>

          <button
            disabled={paginaActual === totalPaginas}
            onClick={() =>
              setPaginaActual((prev) => Math.min(totalPaginas, prev + 1))
            }
          >
            Siguiente
          </button>
        </div>

        {modalAbierto && (
          <div className="enterprise-modal-backdrop">
            <div className="enterprise-modal">
              <div className="enterprise-modal-header">
                <div>
                  <span>Registro en dos pasos</span>
                  <h2>{editandoId ? "Editar equipo" : "Nuevo equipo"}</h2>
                  <p>
                    Paso {paso} de 2 ·{" "}
                    {paso === 1 ? "Datos básicos" : "Hoja de vida técnica"}
                  </p>
                </div>

                <button className="modal-close" onClick={cerrarModal}>
                  <X size={22} />
                </button>
              </div>

              <div className="enterprise-steps">
                <button className={paso === 1 ? "active" : ""} onClick={() => setPaso(1)}>
                  1. Datos básicos
                </button>
                <button
                  className={paso === 2 ? "active" : ""}
                  disabled={!equipoCreadoId && !editandoId}
                  onClick={() => setPaso(2)}
                >
                  2. Hoja de vida
                </button>
              </div>

              {paso === 1 && (
                <div className="enterprise-form-grid">
                  <label>
                    Empresa *
                    <select
                      name="empresa_id"
                      value={equipoForm.empresa_id}
                      onChange={handleEquipoChange}
                    >
                      <option value="">Seleccionar empresa</option>
                      {empresas.map((empresa) => (
                        <option key={empresa.id} value={empresa.id}>
                          {empresa.nombre}
                        </option>
                      ))}
                    </select>
                  </label>

                  <label>
                    Sede *
                    <select
                      name="sede_id"
                      value={equipoForm.sede_id}
                      onChange={handleEquipoChange}
                      disabled={!equipoForm.empresa_id}
                    >
                      <option value="">Seleccionar sede</option>
                      {sedesFiltradas.map((sede) => (
                        <option key={sede.id} value={sede.id}>
                          {sede.nombre}
                        </option>
                      ))}
                    </select>
                  </label>

                  <label>
                    Categoría
                    <select
                      name="categoria_id"
                      value={equipoForm.categoria_id}
                      onChange={handleEquipoChange}
                    >
                      <option value="">Sin categoría</option>
                      {categorias.map((categoria) => (
                        <option key={categoria.id} value={categoria.id}>
                          {categoria.nombre}
                        </option>
                      ))}
                    </select>
                  </label>

                  <label>
                    Nombre del equipo *
                    <input
                      name="nombre"
                      value={equipoForm.nombre}
                      onChange={handleEquipoChange}
                      placeholder="Ej: Aire acondicionado Habitación 201"
                    />
                  </label>

                  <label>
                    Código ID
                    <input
                      name="codigo_id"
                      value={equipoForm.codigo_id}
                      onChange={handleEquipoChange}
                      placeholder="Código interno"
                    />
                  </label>

                  <label>
                    Inventario
                    <input
                      name="inventario"
                      value={equipoForm.inventario}
                      onChange={handleEquipoChange}
                      placeholder="Código físico/institucional"
                    />
                  </label>

                  <label>
                    Marca
                    <input
                      name="marca"
                      value={equipoForm.marca}
                      onChange={handleEquipoChange}
                    />
                  </label>

                  <label>
                    Modelo
                    <input
                      name="modelo"
                      value={equipoForm.modelo}
                      onChange={handleEquipoChange}
                    />
                  </label>

                  <label>
                    Serie
                    <input
                      name="serie"
                      value={equipoForm.serie}
                      onChange={handleEquipoChange}
                    />
                  </label>

                  <label>
                    Ubicación
                    <input
                      name="ubicacion"
                      value={equipoForm.ubicacion}
                      onChange={handleEquipoChange}
                    />
                  </label>

                  <label>
                    INVIMA
                    <input
                      name="invima"
                      value={equipoForm.invima}
                      onChange={handleEquipoChange}
                    />
                  </label>

                  <label>
                    Estado
                    <select
                      name="estado"
                      value={equipoForm.estado}
                      onChange={handleEquipoChange}
                    >
                      <option value="OPERATIVO">Operativo</option>
                      <option value="EN_MANTENIMIENTO">En mantenimiento</option>
                      <option value="FUERA_DE_SERVICIO">Fuera de servicio</option>
                      <option value="BAJA">Baja</option>
                    </select>
                  </label>

                  <label>
                    Criticidad
                    <select
                      name="criticidad"
                      value={equipoForm.criticidad}
                      onChange={handleEquipoChange}
                    >
                      <option value="BAJA">Baja</option>
                      <option value="MEDIA">Media</option>
                      <option value="ALTA">Alta</option>
                      <option value="CRITICA">Crítica</option>
                    </select>
                  </label>
                </div>
              )}

              {paso === 2 && (
                <div className="enterprise-form-grid">
                  <label>
                    Adquisición
                    <input
                      name="adquisicion"
                      value={hojaForm.adquisicion}
                      onChange={handleHojaChange}
                      placeholder="Compra, donación, comodato..."
                    />
                  </label>

                  <label>
                    Costo
                    <input
                      type="number"
                      name="costo"
                      value={hojaForm.costo}
                      onChange={handleHojaChange}
                    />
                  </label>

                  <label>
                    Fecha compra
                    <input
                      type="date"
                      name="fecha_compra"
                      value={hojaForm.fecha_compra}
                      onChange={handleHojaChange}
                    />
                  </label>

                  <label>
                    Fecha instalación
                    <input
                      type="date"
                      name="fecha_instalacion"
                      value={hojaForm.fecha_instalacion}
                      onChange={handleHojaChange}
                    />
                  </label>

                  <label>
                    Proveedor
                    <input
                      name="proveedor"
                      value={hojaForm.proveedor}
                      onChange={handleHojaChange}
                    />
                  </label>

                  <label>
                    País fabricación
                    <input
                      name="pais_fabricacion"
                      value={hojaForm.pais_fabricacion}
                      onChange={handleHojaChange}
                    />
                  </label>

                  <label>
                    Fecha fabricación
                    <input
                      type="date"
                      name="fecha_fabricacion"
                      value={hojaForm.fecha_fabricacion}
                      onChange={handleHojaChange}
                    />
                  </label>

                  <label>
                    Vida útil
                    <input
                      name="vida_util"
                      value={hojaForm.vida_util}
                      onChange={handleHojaChange}
                      placeholder="Ej: 10 años"
                    />
                  </label>

                  {[
                    ["rango_voltaje", "Rango voltaje"],
                    ["rango_presion", "Rango presión"],
                    ["gas_refrigerante", "Gas refrigerante"],
                    ["capacidad", "Capacidad"],
                    ["rango_corriente", "Rango corriente"],
                    ["rango_velocidad", "Rango velocidad"],
                    ["rango_potencia", "Rango potencia"],
                    ["rango_temperatura", "Rango temperatura"],
                    ["frecuencia", "Frecuencia"],
                    ["rango_humedad", "Rango humedad"],
                  ].map(([name, label]) => (
                    <label key={name}>
                      {label}
                      <input
                        name={name}
                        value={hojaForm[name]}
                        onChange={handleHojaChange}
                      />
                    </label>
                  ))}

                  <label className="full">
                    Otros
                    <textarea
                      name="otros"
                      value={hojaForm.otros}
                      onChange={handleHojaChange}
                    />
                  </label>

                  <div className="check-section full">
                    <h3>Manuales, planos y clasificación</h3>

                    <div className="check-grid">
                      {[
                        ["requiere_calibracion", "Requiere calibración"],
                        ["manual_operacion", "Manual operación"],
                        ["manual_mantenimiento", "Manual mantenimiento"],
                        ["manual_partes", "Manual partes"],
                        ["manual_despiece", "Manual despiece"],
                        ["plano_electronico", "Plano electrónico"],
                        ["plano_electrico", "Plano eléctrico"],
                        ["plano_neumatico", "Plano neumático"],
                        ["plano_mecanico", "Plano mecánico"],
                        ["clase_diagnostico", "Diagnóstico"],
                        ["clase_prevencion", "Prevención"],
                        ["clase_rehabilitacion", "Rehabilitación"],
                        ["clase_analisis", "Análisis"],
                        ["riesgo_bajo", "Riesgo bajo"],
                        ["riesgo_moderado", "Riesgo moderado"],
                        ["riesgo_alto", "Riesgo alto"],
                        ["riesgo_elevado", "Riesgo elevado"],
                      ].map(([name, label]) => (
                        <label key={name} className="check-item">
                          <input
                            type="checkbox"
                            name={name}
                            checked={Boolean(hojaForm[name])}
                            onChange={handleHojaChange}
                          />
                          {label}
                        </label>
                      ))}
                    </div>
                  </div>
                </div>
              )}

              <div className="enterprise-modal-actions">
                <button className="btn-secondary-enterprise" onClick={cerrarModal}>
                  <X size={18} />
                  Cancelar
                </button>

                {paso === 2 && (
                  <button
                    className="btn-secondary-enterprise"
                    onClick={() => setPaso(1)}
                  >
                    <ChevronLeft size={18} />
                    Atrás
                  </button>
                )}

                {paso === 1 ? (
                  <button
                    className="btn-primary-enterprise"
                    onClick={guardarPaso1}
                    disabled={saving}
                  >
                    <ChevronRight size={18} />
                    {saving ? "Guardando..." : "Guardar y continuar"}
                  </button>
                ) : (
                  <button
                    className="btn-primary-enterprise"
                    onClick={guardarHojaVida}
                    disabled={saving}
                  >
                    <Save size={18} />
                    {saving ? "Guardando..." : "Finalizar hoja de vida"}
                  </button>
                )}
              </div>
            </div>
          </div>
        )}

        {detalle && (
          <div className="enterprise-modal-backdrop">
            <div className="enterprise-modal small">
              <div className="enterprise-modal-header">
                <div>
                  <span>Detalle del equipo</span>
                  <h2>{detalle.nombre}</h2>
                  <p>{nombreCategoria(detalle.categoria_id)}</p>
                </div>

                <button className="modal-close" onClick={() => setDetalle(null)}>
                  <X size={22} />
                </button>
              </div>

              <div className="detail-grid">
                <p><strong>Empresa:</strong> {nombreEmpresa(detalle.empresa_id)}</p>
                <p><strong>Sede:</strong> {nombreSede(detalle.sede_id)}</p>
                <p><strong>Marca:</strong> {detalle.marca || "N/A"}</p>
                <p><strong>Modelo:</strong> {detalle.modelo || "N/A"}</p>
                <p><strong>Serie:</strong> {detalle.serie || "N/A"}</p>
                <p><strong>Ubicación:</strong> {detalle.ubicacion || "N/A"}</p>
                <p><strong>Estado:</strong> {textoEstado(detalle.estado)}</p>
                <p><strong>Criticidad:</strong> {detalle.criticidad}</p>
              </div>
            </div>
          </div>
        )}
      </div>
    </AdminLayout>
  );
}