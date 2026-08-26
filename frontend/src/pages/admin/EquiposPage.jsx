import { useEffect, useEffectEvent, useMemo, useRef, useState } from "react";
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
  FileText,
  UploadCloud,
  Download,
  Printer,
  MapPin,
  ChevronDown,
  Check,
  UserPlus,
  RotateCcw,
  ArrowRightLeft,
  Archive,
  History,
} from "lucide-react";

import AdminLayout from "./AdminLayout";
import "../../styles/equipos-saas-pro-enterprise.css";
import { getAccessToken } from "../../utils/authStorage";
import { coincideBusquedaEquipoConContexto } from "./equiposBusquedaUtils";

const API_URL = import.meta.env.VITE_API_URL || "/api";

const ESTADOS = [
  { value: "OPERATIVO", label: "Operativo" },
  { value: "EN_MANTENIMIENTO", label: "En mantenimiento" },
  { value: "FUERA_DE_SERVICIO", label: "Fuera de servicio" },
  { value: "BAJA", label: "Baja" },
];

const CRITICIDADES = [
  { value: "BAJA", label: "Baja" },
  { value: "MEDIA", label: "Media" },
  { value: "ALTA", label: "Alta" },
  { value: "CRITICA", label: "Crítica" },
];

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
  responsable_id: "",
  vida_util_meses: "",
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
  return getAccessToken();
}

function authHeaders(json = true) {
  const token = getToken();
  return {
    ...(json ? { "Content-Type": "application/json" } : {}),
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
    data[key] = value === "" ? null : value;
  });
  return data;
}

function cargarHojaEnFormulario(hoja) {
  return Object.fromEntries(
    Object.entries(hojaInicial).map(([campo, valorInicial]) => {
      const valor = hoja?.[campo];

      if (typeof valorInicial === "boolean") {
        return [campo, Boolean(valor)];
      }

      return [campo, valor ?? ""];
    })
  );
}

function boolText(value) {
  return value ? "Sí" : "No";
}

export default function EquiposPage() {
  const [equipos, setEquipos] = useState([]);
  const [empresas, setEmpresas] = useState([]);
  const [sedes, setSedes] = useState([]);
  const [categorias, setCategorias] = useState([]);
  const [usuarios, setUsuarios] = useState([]);

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  const [busqueda, setBusqueda] = useState("");
  const [sedeFiltro, setSedeFiltro] = useState("");
  const [estadoFiltro, setEstadoFiltro] = useState("");
  const [criticidadFiltro, setCriticidadFiltro] = useState("");
  const [categoriaFiltro, setCategoriaFiltro] = useState("");
  const [responsableFiltro, setResponsableFiltro] = useState("");
  const [soloActivosFiltro, setSoloActivosFiltro] = useState(true);
  const [menuSedesAbierto, setMenuSedesAbierto] = useState(false);
  const [paginaActual, setPaginaActual] = useState(1);
  const [equiposPorPagina, setEquiposPorPagina] = useState(20);
  const menuSedesRef = useRef(null);

  const [modalAbierto, setModalAbierto] = useState(false);
  const [paso, setPaso] = useState(1);
  const [equipoForm, setEquipoForm] = useState(equipoInicial);
  const [hojaForm, setHojaForm] = useState(hojaInicial);
  const [equipoCreadoId, setEquipoCreadoId] = useState(null);
  const [editandoId, setEditandoId] = useState(null);
  const [hojaExistente, setHojaExistente] = useState(false);
  const [cargandoHojaEdicion, setCargandoHojaEdicion] = useState(false);
  const solicitudHojaEdicion = useRef(0);

  const [detalle, setDetalle] = useState(null);
  const [hojaCompleta, setHojaCompleta] = useState(null);
  const [cargandoHoja, setCargandoHoja] = useState(false);

  const [modalImportar, setModalImportar] = useState(false);
  const [archivoImportar, setArchivoImportar] = useState(null);
  const [resultadoImportacion, setResultadoImportacion] = useState(null);
  const [exportando, setExportando] = useState(false);
  const archivoImportarRef = useRef(null);

  const [mensaje, setMensaje] = useState("");
  const [error, setError] = useState("");

  const cargarCatalogos = async () => {
    const [empresasRes, sedesRes, categoriasRes, usuariosRes] = await Promise.all([
      fetch(`${API_URL}/empresas/`, { headers: authHeaders() }),
      fetch(`${API_URL}/sedes/`, { headers: authHeaders() }),
      fetch(`${API_URL}/categorias/`, { headers: authHeaders() }),
      fetch(`${API_URL}/usuarios/`, { headers: authHeaders() }),
    ]);

    if (!empresasRes.ok || !sedesRes.ok || !categoriasRes.ok || !usuariosRes.ok) {
      throw new Error("No fue posible cargar catálogos.");
    }

    setEmpresas(await empresasRes.json());
    setSedes(await sedesRes.json());
    setCategorias(await categoriasRes.json());
    setUsuarios(await usuariosRes.json());
  };

  const cargarEquipos = async ({
    estado = estadoFiltro,
    criticidad = criticidadFiltro,
    categoriaId = categoriaFiltro,
    responsableId = responsableFiltro,
    sedeId = sedeFiltro,
    soloActivos = soloActivosFiltro,
  } = {}) => {
    const params = new URLSearchParams();
    if (estado) params.append("estado", estado);
    if (criticidad) params.append("criticidad", criticidad);
    if (categoriaId) params.append("categoria_id", categoriaId);
    if (responsableId) params.append("responsable_id", responsableId);
    if (sedeId) params.append("sede_id", sedeId);
    if (soloActivos) params.append("solo_activos", "true");

    const query = params.toString();
    const url = `${API_URL}/equipos/${query ? `?${query}` : ""}`;
    const response = await fetch(url, { headers: authHeaders() });

    if (!response.ok) throw new Error("Error cargando equipos.");
    setEquipos(await response.json());
  };

  const cargarTodo = async () => {
    try {
      setLoading(true);
      setError("");
      await Promise.all([cargarCatalogos(), cargarEquipos()]);
    } catch (err) {
      console.error(err);
      setError(err.message || "Error cargando información.");
    } finally {
      setLoading(false);
    }
  };

  const cargarTodoAlMontar = useEffectEvent(cargarTodo);

  useEffect(() => {
    const timer = window.setTimeout(() => cargarTodoAlMontar(), 0);
    return () => window.clearTimeout(timer);
  }, []);

  useEffect(() => {
    if (!menuSedesAbierto) return undefined;

    const cerrarMenu = (event) => {
      if (!menuSedesRef.current?.contains(event.target)) {
        setMenuSedesAbierto(false);
      }
    };
    const cerrarConEscape = (event) => {
      if (event.key === "Escape") setMenuSedesAbierto(false);
    };

    document.addEventListener("mousedown", cerrarMenu);
    document.addEventListener("keydown", cerrarConEscape);
    return () => {
      document.removeEventListener("mousedown", cerrarMenu);
      document.removeEventListener("keydown", cerrarConEscape);
    };
  }, [menuSedesAbierto]);

  const sedesFiltradas = useMemo(() => {
    if (!equipoForm.empresa_id) return [];
    return sedes.filter(
      (sede) => String(sede.empresa_id) === String(equipoForm.empresa_id)
    );
  }, [sedes, equipoForm.empresa_id]);

  const sedesOrdenadas = useMemo(
    () => [...sedes].sort((a, b) => String(a.nombre || "").localeCompare(
      String(b.nombre || ""),
      "es",
      { sensitivity: "base" },
    )),
    [sedes],
  );

  const sedesPorId = useMemo(
    () => new Map(sedes.map((sede) => [String(sede.id), sede.nombre || ""])),
    [sedes],
  );
  const empresasPorId = useMemo(
    () => new Map(empresas.map((empresa) => [String(empresa.id), empresa.nombre || ""])),
    [empresas],
  );
  const categoriasPorId = useMemo(
    () => new Map(categorias.map((categoria) => [String(categoria.id), categoria.nombre || ""])),
    [categorias],
  );
  const usuariosPorId = useMemo(
    () => new Map(usuarios.map((usuario) => [
      String(usuario.id),
      usuario.nombre_completo || usuario.username || "N/A",
    ])),
    [usuarios],
  );

  const seleccionarSedeFiltro = (sedeId) => {
    setSedeFiltro(sedeId);
    setPaginaActual(1);
    setMenuSedesAbierto(false);
  };

  const equiposFiltrados = useMemo(() => {
    return equipos.filter((equipo) => {
      const sedeNombre = sedesPorId.get(String(equipo.sede_id)) || "";
      const coincideBusqueda = coincideBusquedaEquipoConContexto([
        equipo.nombre,
        equipo.marca,
        equipo.modelo,
        equipo.serie,
        equipo.codigo_id,
        equipo.inventario,
        equipo.ubicacion,
        sedeNombre,
        empresasPorId.get(String(equipo.empresa_id)) || "",
        usuariosPorId.get(String(equipo.responsable_id)) || "",
      ], [
        categoriasPorId.get(String(equipo.categoria_id)) || "",
      ], busqueda);

      const coincideSede = !sedeFiltro || String(equipo.sede_id) === sedeFiltro;
      const coincideEstado = !estadoFiltro || equipo.estado === estadoFiltro;
      const coincideCriticidad = !criticidadFiltro || equipo.criticidad === criticidadFiltro;
      const coincideCategoria = !categoriaFiltro || String(equipo.categoria_id) === categoriaFiltro;
      const coincideResponsable = !responsableFiltro
        || String(equipo.responsable_id) === responsableFiltro;
      const coincideActivo = !soloActivosFiltro || equipo.activo !== false;

      return coincideBusqueda
        && coincideSede
        && coincideEstado
        && coincideCriticidad
        && coincideCategoria
        && coincideResponsable
        && coincideActivo;
    });
  }, [
    equipos,
    busqueda,
    sedeFiltro,
    estadoFiltro,
    criticidadFiltro,
    categoriaFiltro,
    responsableFiltro,
    soloActivosFiltro,
    sedesPorId,
    empresasPorId,
    categoriasPorId,
    usuariosPorId,
  ]);
  const totalPaginas = Math.max(1, Math.ceil(equiposFiltrados.length / equiposPorPagina));
  const paginaVisible = Math.min(paginaActual, totalPaginas);

  const equiposPaginados = equiposFiltrados.slice(
    (paginaVisible - 1) * equiposPorPagina,
    paginaVisible * equiposPorPagina
  );
  const sedeFiltroNombre = sedeFiltro ? sedesPorId.get(sedeFiltro) || "la sede seleccionada" : "";
  const inicioPagina = equiposFiltrados.length ? (paginaVisible - 1) * equiposPorPagina + 1 : 0;
  const finPagina = Math.min(paginaVisible * equiposPorPagina, equiposFiltrados.length);
  const detalleResultados = [
    busqueda.trim() ? `para “${busqueda.trim()}”` : "",
    sedeFiltroNombre ? `en ${sedeFiltroNombre}` : "",
  ].filter(Boolean).join(" ") || "en todo el inventario";

  const inventarioDuplicado = useMemo(() => {
    const numero = equipoForm.inventario.trim().toLowerCase();
    if (!numero) return false;

    return equipos.some((equipo) => (
      String(equipo.id) !== String(editandoId || "")
      && [equipo.inventario, equipo.codigo_id].some(
        (valor) => String(valor || "").trim().toLowerCase() === numero,
      )
    ));
  }, [equipos, equipoForm.inventario, editandoId]);

  const totalEquipos = equipos.length;
  const operativos = equipos.filter((e) => e.estado === "OPERATIVO").length;
  const mantenimiento = equipos.filter((e) => e.estado === "EN_MANTENIMIENTO").length;
  const fueraServicio = equipos.filter((e) => e.estado === "FUERA_DE_SERVICIO").length;

  const abrirNuevoEquipo = () => {
    solicitudHojaEdicion.current += 1;
    setModalAbierto(true);
    setPaso(1);
    setEquipoForm(equipoInicial);
    setHojaForm(hojaInicial);
    setEquipoCreadoId(null);
    setEditandoId(null);
    setHojaExistente(false);
    setCargandoHojaEdicion(false);
    setMensaje("");
    setError("");
  };

  const cerrarModal = () => {
    solicitudHojaEdicion.current += 1;
    setModalAbierto(false);
    setPaso(1);
    setEquipoForm(equipoInicial);
    setHojaForm(hojaInicial);
    setEquipoCreadoId(null);
    setEditandoId(null);
    setHojaExistente(false);
    setCargandoHojaEdicion(false);
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
    if (inventarioDuplicado) {
      return "Equipo ya existe: el número de inventario está registrado.";
    }
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

      const payload = {
        ...limpiarPayload(equipoForm),
        vida_util_meses: equipoForm.vida_util_meses === ""
          ? null
          : Number(equipoForm.vida_util_meses),
      };
      const url = editandoId ? `${API_URL}/equipos/${editandoId}` : `${API_URL}/equipos/`;

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

      const datosHoja = {
        ...limpiarPayload(hojaForm),
        costo: hojaForm.costo === "" ? null : Number(hojaForm.costo),
      };
      const payload = hojaExistente
        ? datosHoja
        : { equipo_id: idEquipo, ...datosHoja };
      const url = hojaExistente
        ? API_URL + "/equipo-hoja-vida/equipo/" + idEquipo
        : API_URL + "/equipo-hoja-vida/";

      const response = await fetch(url, {
        method: hojaExistente ? "PUT" : "POST",
        headers: authHeaders(),
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        const data = await response.json().catch(() => null);

        throw new Error(data?.detail || "No fue posible guardar la hoja de vida.");
      }

      setMensaje(
        hojaExistente
          ? "Equipo y hoja de vida actualizados correctamente."
          : "Equipo y hoja de vida creados correctamente."
      );
      cerrarModal();
      await cargarEquipos();
    } catch (err) {
      console.error(err);
      setError(err.message || "Error guardando hoja de vida.");
    } finally {
      setSaving(false);
    }
  };

  const editarEquipo = async (equipo) => {
    const solicitudActual = solicitudHojaEdicion.current + 1;
    solicitudHojaEdicion.current = solicitudActual;
    setEditandoId(equipo.id);
    setEquipoCreadoId(equipo.id);
    setPaso(1);
    setModalAbierto(true);
    setMensaje("");
    setError("");
    setHojaForm(hojaInicial);
    setHojaExistente(false);
    setCargandoHojaEdicion(true);

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
      responsable_id: equipo.responsable_id || "",
      vida_util_meses: equipo.vida_util_meses ?? "",
      activo: equipo.activo ?? true,
    });

    try {
      const response = await fetch(
        API_URL + "/equipo-hoja-vida/equipo/" + equipo.id,
        { headers: authHeaders() }
      );

      if (solicitudActual !== solicitudHojaEdicion.current) return;

      if (response.status === 404) {
        setHojaForm(hojaInicial);
        setHojaExistente(false);
        return;
      }

      if (!response.ok) {
        const data = await response.json().catch(() => null);
        throw new Error(data?.detail || "No fue posible cargar la hoja de vida para editar.");
      }

      const hoja = await response.json();
      setHojaForm(cargarHojaEnFormulario(hoja));
      setHojaExistente(true);
    } catch (err) {
      if (solicitudActual !== solicitudHojaEdicion.current) return;
      console.error(err);
      setError(err.message || "Error cargando la hoja de vida para editar.");
    } finally {
      if (solicitudActual === solicitudHojaEdicion.current) {
        setCargandoHojaEdicion(false);
      }
    }
  };

  const eliminarEquipo = async (equipo) => {
    const confirmar = window.confirm(
      `¿Eliminar el equipo "${equipo.nombre}"?\n\nSolo se eliminará si no tiene mantenimientos asociados.`
    );

    if (!confirmar) return;

    try {
      setSaving(true);
      setError("");

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

  const verHojaVidaCompleta = async (equipo) => {
    try {
      setCargandoHoja(true);
      setError("");
      setHojaCompleta(null);

      const response = await fetch(`${API_URL}/equipo-hoja-vida/equipo/${equipo.id}/completa`, {
        headers: authHeaders(),
      });

      if (!response.ok) {
        const data = await response.json().catch(() => null);
        throw new Error(data?.detail || "No fue posible cargar la hoja de vida.");
      }

      setHojaCompleta(await response.json());
    } catch (err) {
      console.error(err);
      setError(err.message || "Error cargando hoja de vida.");
    } finally {
      setCargandoHoja(false);
    }
  };

  const imprimirHojaVida = () => {
    window.print();
  };

  const importarInventario = async () => {
    if (!archivoImportar) {
      setError("Selecciona un archivo Excel o CSV.");
      return;
    }

    try {
      setSaving(true);
      setError("");
      setMensaje("");
      setResultadoImportacion(null);

      const formData = new FormData();
      formData.append("archivo", archivoImportar);

      const response = await fetch(`${API_URL}/equipos/importar`, {
        method: "POST",
        headers: authHeaders(false),
        body: formData,
      });

      const data = await response.json().catch(() => null);

      if (!response.ok) {
        const detail = data?.detail;
        const mensajeDetalle = Array.isArray(detail)
          ? detail.map((item) => item?.msg || String(item)).join(". ")
          : typeof detail === "object" && detail
            ? JSON.stringify(detail)
            : detail;
        throw new Error(mensajeDetalle || "No fue posible importar el inventario.");
      }

      const omitidos = data.omitidos ?? data.errores?.length ?? 0;
      setResultadoImportacion(data);
      setMensaje(
        "Importación procesada. Equipos creados: "
        + (data.creados || 0)
        + ". Filas omitidas: "
        + omitidos
        + ".",
      );
      setBusqueda("");
      seleccionarSedeFiltro("");
      setArchivoImportar(null);
      if (archivoImportarRef.current) archivoImportarRef.current.value = "";
      await cargarEquipos();
    } catch (err) {
      console.error(err);
      setError(err.message || "Error importando inventario.");
    } finally {
      setSaving(false);
    }
  };
  const exportarInventario = async () => {
    try {
      setExportando(true);
      setError("");
      setMensaje("");

      const response = await fetch(
        `${API_URL}/equipos/exportar`,
        { headers: authHeaders(false) },
      );

      if (!response.ok) {
        const data = await response.json().catch(() => null);
        throw new Error(data?.detail || "No fue posible exportar el inventario.");
      }

      const disposition = response.headers.get("content-disposition") || "";
      const filenameMatch = disposition.match(/filename="?([^";]+)"?/i);
      const filename = filenameMatch?.[1] || "inventario_equipos_vaner_asset.xlsx";
      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");

      link.href = url;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      link.remove();
      URL.revokeObjectURL(url);

      setMensaje("Inventario exportado correctamente.");
    } catch (err) {
      console.error(err);
      setError(err.message || "Error exportando inventario.");
    } finally {
      setExportando(false);
    }
  };

  const ejecutarMovimiento = async (equipoId, endpoint, payload) => {
    try {
      setSaving(true);
      setError("");
      setMensaje("");

      const response = await fetch(`${API_URL}/equipos/${equipoId}/${endpoint}`, {
        method: "POST",
        headers: authHeaders(),
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        const data = await response.json().catch(() => null);
        throw new Error(data?.detail || `Error en movimiento ${endpoint}`);
      }

      setMensaje(`Movimiento ${endpoint} realizado correctamente.`);
      await cargarEquipos();
      return true;
    } catch (err) {
      console.error(err);
      setError(err.message || `Error en movimiento ${endpoint}`);
      return false;
    } finally {
      setSaving(false);
    }
  };

  const verHistorial = async (equipo) => {
    try {
      setLoading(true);
      const response = await fetch(`${API_URL}/equipos/${equipo.id}/historial`, {
        headers: authHeaders(),
      });

      if (!response.ok) {
        throw new Error("Error cargando historial");
      }

      const historial = await response.json();
      setDetalle({ ...equipo, historial_cambios: historial.historial_cambios || [] });
    } catch (err) {
      console.error(err);
      setError(err.message || "Error cargando historial");
    } finally {
      setLoading(false);
    }
  };

  const [movimientoModal, setMovimientoModal] = useState(null);
  const [movimientoTipo, setMovimientoTipo] = useState("");
  const [movimientoEquipo, setMovimientoEquipo] = useState(null);
  const [movimientoForm, setMovimientoForm] = useState({});

  const abrirMovimiento = (equipo, tipo) => {
    setMovimientoEquipo(equipo);
    setMovimientoTipo(tipo);
    setMovimientoForm({
      observacion: "",
      ...(tipo === 'asignar' ? { responsable_id: "", ubicacion: "" } : {}),
      ...(tipo === 'devolver' ? { ubicacion: "" } : {}),
      ...(tipo === 'transferir' ? { nuevo_responsable_id: "", nueva_sede_id: "", nueva_ubicacion: "" } : {}),
      ...(tipo === 'baja' ? { motivo: "", estado_final: "BAJA" } : {}),
    });
    setMovimientoModal(tipo);
  };

  const cerrarMovimientoModal = () => {
    setMovimientoModal(null);
    setMovimientoTipo("");
    setMovimientoEquipo(null);
    setMovimientoForm({});
  };

  const handleMovimientoChange = (e) => {
    const { name, value, type, checked } = e.target;
    setMovimientoForm((prev) => ({
      ...prev,
      [name]: type === "checkbox" ? checked : value,
    }));
  };

  const ejecutarMovimientoConfirmado = async () => {
    if (!movimientoEquipo || !movimientoTipo) return;

    const payload = { ...movimientoForm };

    if (movimientoTipo === 'asignar' && !payload.responsable_id) {
      setError("Debe seleccionar un responsable.");
      return;
    }
    if (movimientoTipo === 'baja' && !payload.motivo) {
      setError("Debe ingresar un motivo para la baja.");
      return;
    }

    const exitoso = await ejecutarMovimiento(movimientoEquipo.id, movimientoTipo, payload);
    if (exitoso) cerrarMovimientoModal();
  };

  const nombreEmpresa = (id) =>
    empresas.find((e) => String(e.id) === String(id))?.nombre || "N/A";

  const nombreSede = (id) =>
    sedes.find((s) => String(s.id) === String(id))?.nombre || "N/A";

  const nombreCategoria = (id) =>
    categorias.find((c) => String(c.id) === String(id))?.nombre || "Sin categoría";

  const nombreResponsable = (id) => usuariosPorId.get(String(id)) || "Sin responsable";

  const equipoHV = hojaCompleta?.equipo_basico || {};
  const encabezadoHV = hojaCompleta?.encabezado || {};
  const tecnicaHV = hojaCompleta?.hoja_vida_tecnica || {};

  return (
    <AdminLayout>
      <div className="equipos-enterprise-page">
        <div className="enterprise-header">
          <div>
            <h1>Inventario de Equipos</h1>
            <p>Gestión empresarial de activos, hoja de vida, mantenimiento, importación y exportación.</p>
          </div>

          <div className="enterprise-header-actions">
            <button
              className="btn-secondary-enterprise"
              onClick={exportarInventario}
              disabled={exportando}
              type="button"
            >
              <Download size={18} />
              {exportando ? "Exportando..." : "Exportar Excel"}
            </button>

            <button className="btn-secondary-enterprise" onClick={() => setModalImportar(true)}>
              <UploadCloud size={18} />
              Importar Excel/CSV
            </button>

            <button className="btn-primary-enterprise" onClick={abrirNuevoEquipo}>
              <Plus size={18} />
              Nuevo Equipo
            </button>
          </div>
        </div>

        {mensaje && <div className="enterprise-alert success">{mensaje}</div>}
        {error && <div className="enterprise-alert error">{error}</div>}

        <div className="enterprise-kpis">
          <div className="enterprise-kpi-card">
            <div className="kpi-icon blue"><MonitorCog size={28} /></div>
            <div><h3>Total Equipos</h3><h2>{totalEquipos}</h2></div>
          </div>

          <div className="enterprise-kpi-card">
            <div className="kpi-icon green"><CircleCheckBig size={28} /></div>
            <div><h3>Operativos</h3><h2>{operativos}</h2></div>
          </div>

          <div className="enterprise-kpi-card">
            <div className="kpi-icon orange"><RefreshCw size={28} /></div>
            <div><h3>Mantenimiento</h3><h2>{mantenimiento}</h2></div>
          </div>

          <div className="enterprise-kpi-card">
            <div className="kpi-icon red"><ShieldAlert size={28} /></div>
            <div><h3>Fuera Servicio</h3><h2>{fueraServicio}</h2></div>
          </div>
        </div>

        <div className="enterprise-toolbar">
          <div className="search-enterprise">
            <Search size={18} />
            <input
              type="text"
              placeholder="Buscar equipos, cámaras, inventario o sede..."
              value={busqueda}
              onChange={(e) => {
                setBusqueda(e.target.value);
                setPaginaActual(1);
              }}
            />
          </div>

          <div className="filters-enterprise">
            <label className="filter-enterprise">
              <span>Estado</span>
              <select
                value={estadoFiltro}
                onChange={(e) => {
                  const estado = e.target.value;
                  setEstadoFiltro(estado);
                  setPaginaActual(1);
                  cargarEquipos({ estado });
                }}
              >
                <option value="">Todos</option>
                {ESTADOS.map((e) => <option key={e.value} value={e.value}>{e.label}</option>)}
              </select>
            </label>

            <label className="filter-enterprise">
              <span>Criticidad</span>
              <select
                value={criticidadFiltro}
                onChange={(e) => {
                  const criticidad = e.target.value;
                  setCriticidadFiltro(criticidad);
                  setPaginaActual(1);
                  cargarEquipos({ criticidad });
                }}
              >
                <option value="">Todas</option>
                {CRITICIDADES.map((c) => <option key={c.value} value={c.value}>{c.label}</option>)}
              </select>
            </label>

            <label className="filter-enterprise">
              <span>Categoría</span>
              <select
                value={categoriaFiltro}
                onChange={(e) => {
                  const categoriaId = e.target.value;
                  setCategoriaFiltro(categoriaId);
                  setPaginaActual(1);
                  cargarEquipos({ categoriaId });
                }}
              >
                <option value="">Todas</option>
                {categorias.map((cat) => <option key={cat.id} value={cat.id}>{cat.nombre}</option>)}
              </select>
            </label>

            <label className="filter-enterprise">
              <span>Responsable</span>
              <select
                aria-label="Filtrar por responsable"
                value={responsableFiltro}
                onChange={(e) => {
                  const responsableId = e.target.value;
                  setResponsableFiltro(responsableId);
                  setPaginaActual(1);
                  cargarEquipos({ responsableId });
                }}
              >
                <option value="">Todos</option>
                {usuarios.map((usuario) => (
                  <option key={usuario.id} value={usuario.id}>
                    {usuario.nombre_completo || usuario.username}
                  </option>
                ))}
              </select>
            </label>

            <label className="filter-enterprise">
              <span>Sede</span>
              <div className="sede-filter-control">
                <MapPin size={18} />
                <select
                  aria-label="Filtrar por sede"
                  value={sedeFiltro}
                  onChange={(e) => {
                    const sedeId = e.target.value;
                    seleccionarSedeFiltro(sedeId);
                    cargarEquipos({ sedeId });
                  }}
                >
                  <option value="">Todas las sedes</option>
                  {sedesOrdenadas.map((sede) => (
                    <option key={sede.id} value={sede.id}>{sede.nombre}</option>
                  ))}
                </select>
                <ChevronDown size={16} aria-hidden="true" />
              </div>
            </label>

            <label className="filter-enterprise checkbox-filter">
              <input
                type="checkbox"
                checked={soloActivosFiltro}
                onChange={(e) => {
                  const soloActivos = e.target.checked;
                  setSoloActivosFiltro(soloActivos);
                  setPaginaActual(1);
                  cargarEquipos({ soloActivos });
                }}
              />
              <span>Solo activos</span>
            </label>
          </div>
        </div>

        <div className="enterprise-results-summary" role="status" aria-live="polite">
          <div>
            <strong>{equiposFiltrados.length}</strong>
            <span>{equiposFiltrados.length === 1 ? "equipo encontrado" : "equipos encontrados"}</span>
          </div>
          <p>{detalleResultados}</p>
        </div>

        <div className="enterprise-table-wrapper">
          <table className="enterprise-table">
            <thead>
              <tr>
                <th>Código</th>
                <th>Equipo</th>
                <th>Empresa</th>
                <th className="sede-filter-header" ref={menuSedesRef}>
                  <button
                    type="button"
                    className={sedeFiltro ? "sede-filter-trigger active" : "sede-filter-trigger"}
                    aria-label="Abrir filtro de sedes"
                    aria-expanded={menuSedesAbierto}
                    onClick={() => setMenuSedesAbierto((abierto) => !abierto)}
                  >
                    <span>Sede</span>
                    <ChevronDown size={15} aria-hidden="true" />
                  </button>

                  {menuSedesAbierto && (
                    <div className="sede-filter-menu" role="menu" aria-label="Sedes disponibles">
                      <button
                        type="button"
                        role="menuitem"
                        className={!sedeFiltro ? "selected" : ""}
                        onClick={() => seleccionarSedeFiltro("")}
                      >
                        <span>Todas las sedes</span>
                        {!sedeFiltro && <Check size={16} />}
                      </button>
                      {sedesOrdenadas.map((sede) => {
                        const seleccionada = String(sede.id) === sedeFiltro;
                        return (
                          <button
                            key={sede.id}
                            type="button"
                            role="menuitem"
                            className={seleccionada ? "selected" : ""}
                            onClick={() => seleccionarSedeFiltro(String(sede.id))}
                          >
                            <span>{sede.nombre}</span>
                            {seleccionada && <Check size={16} />}
                          </button>
                        );
                      })}
                    </div>
                  )}
                </th>
                <th>Marca</th>
                <th>Modelo</th>
                <th>Serie</th>
                <th>Responsable</th>
                <th>Estado</th>
                <th>Criticidad</th>
                <th>Acciones</th>
              </tr>
            </thead>

            <tbody>
              {loading ? (
                <tr><td colSpan="11"><div className="loading-enterprise">Cargando equipos...</div></td></tr>
              ) : equiposPaginados.length === 0 ? (
                <tr>
                  <td colSpan="11">
                    <div className="empty-enterprise">
                      {equipos.length > 0
                        ? "No hay equipos que coincidan con la búsqueda o la sede seleccionada."
                        : "No existen equipos registrados."}
                    </div>
                  </td>
                </tr>
              ) : (
                equiposPaginados.map((equipo) => (
                  <tr key={equipo.id}>
                    <td>{equipo.codigo_id || equipo.inventario || "N/A"}</td>

                    <td>
                      <div className="equipo-cell">
                        <div className="equipo-avatar"><MonitorCog size={18} /></div>
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
                    <td>{nombreResponsable(equipo.responsable_id)}</td>

                    <td>
                      <span className={`estado-badge ${estadoClass(equipo.estado)}`}>
                        {textoEstado(equipo.estado)}
                      </span>
                    </td>

                    <td>
                      <span className={`criticidad-badge ${criticidadClass(equipo.criticidad)}`}>
                        {equipo.criticidad || "MEDIA"}
                      </span>
                    </td>

                    <td>
                      <div className="acciones-enterprise">
                        <button className="btn-action blue" onClick={() => setDetalle(equipo)} title="Ver detalle">
                          <Eye size={16} />
                        </button>

                        <button className="btn-action purple" onClick={() => verHojaVidaCompleta(equipo)} title="Hoja de vida completa">
                          <FileText size={16} />
                        </button>

                        <button className="btn-action orange" onClick={() => editarEquipo(equipo)} title="Editar">
                          <Pencil size={16} />
                        </button>

                        <button className="btn-action green" onClick={() => abrirMovimiento(equipo, 'asignar')} title="Asignar">
                          <UserPlus size={16} />
                        </button>

                        <button className="btn-action teal" onClick={() => abrirMovimiento(equipo, 'devolver')} title="Devolver">
                          <RotateCcw size={16} />
                        </button>

                        <button className="btn-action cyan" onClick={() => abrirMovimiento(equipo, 'transferir')} title="Transferir">
                          <ArrowRightLeft size={16} />
                        </button>

                        <button className="btn-action amber" onClick={() => abrirMovimiento(equipo, 'baja')} title="Dar de baja">
                          <Archive size={16} />
                        </button>

                        <button className="btn-action indigo" onClick={() => verHistorial(equipo)} title="Ver historial">
                          <History size={16} />
                        </button>

                        <button className="btn-action red" onClick={() => eliminarEquipo(equipo)} title="Eliminar">
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
          <div className="enterprise-pagination-meta">
            <span>Mostrando {inicioPagina}-{finPagina} de {equiposFiltrados.length}</span>
            <label>
              Equipos por página
              <select
                aria-label="Equipos por página"
                value={equiposPorPagina}
                onChange={(event) => {
                  setEquiposPorPagina(Number(event.target.value));
                  setPaginaActual(1);
                }}
              >
                <option value={20}>20</option>
                <option value={50}>50</option>
                <option value={100}>100</option>
              </select>
            </label>
          </div>

          <div className="enterprise-pagination-actions">
            <button disabled={paginaVisible === 1} onClick={() => setPaginaActual(Math.max(1, paginaVisible - 1))}>
              Anterior
            </button>

            <span>Página {paginaVisible} de {totalPaginas}</span>

            <button disabled={paginaVisible === totalPaginas} onClick={() => setPaginaActual(Math.min(totalPaginas, paginaVisible + 1))}>
              Siguiente
            </button>
          </div>
        </div>

        {modalAbierto && (
          <div className="enterprise-modal-backdrop">
            <div className="enterprise-modal">
              <div className="enterprise-modal-header">
                <div>
                  <span>Registro en dos pasos</span>
                  <h2>{editandoId ? "Editar equipo" : "Nuevo equipo"}</h2>
                  <p>Paso {paso} de 2 · {paso === 1 ? "Datos básicos" : "Hoja de vida técnica"}</p>
                </div>

                <button className="modal-close" onClick={cerrarModal}><X size={22} /></button>
              </div>

              <div className="enterprise-steps">
                <button className={paso === 1 ? "active" : ""} onClick={() => setPaso(1)}>1. Datos básicos</button>
                <button
                  className={paso === 2 ? "active" : ""}
                  disabled={(!equipoCreadoId && !editandoId) || cargandoHojaEdicion}
                  onClick={() => setPaso(2)}
                >
                  2. Hoja de vida
                </button>
              </div>

              {paso === 1 && (
                <div className="enterprise-form-grid">
                  <label>Empresa *
                    <select name="empresa_id" value={equipoForm.empresa_id} onChange={handleEquipoChange}>
                      <option value="">Seleccionar empresa</option>
                      {empresas.map((empresa) => <option key={empresa.id} value={empresa.id}>{empresa.nombre}</option>)}
                    </select>
                  </label>

                  <label>Sede *
                    <select name="sede_id" value={equipoForm.sede_id} onChange={handleEquipoChange} disabled={!equipoForm.empresa_id}>
                      <option value="">Seleccionar sede</option>
                      {sedesFiltradas.map((sede) => <option key={sede.id} value={sede.id}>{sede.nombre}</option>)}
                    </select>
                  </label>

                  <label>Categoría
                    <select name="categoria_id" value={equipoForm.categoria_id} onChange={handleEquipoChange} required>
                      <option value="">Sin categoría</option>
                      {categorias.map((categoria) => <option key={categoria.id} value={categoria.id}>{categoria.nombre}</option>)}
                    </select>
                  </label>

                  <label>Nombre del equipo *
                    <input name="nombre" value={equipoForm.nombre} onChange={handleEquipoChange} placeholder="Ej: Aire acondicionado Habitación 201" />
                  </label>

                  <label>Código ID
                    <input name="codigo_id" value={equipoForm.codigo_id} onChange={handleEquipoChange} placeholder="Código interno" />
                  </label>

                  <label>Inventario
                    <input
                      name="inventario"
                      value={equipoForm.inventario}
                      onChange={handleEquipoChange}
                      placeholder="Código físico/institucional"
                      className={inventarioDuplicado ? "input-error" : ""}
                      aria-invalid={inventarioDuplicado}
                      aria-describedby={inventarioDuplicado ? "inventario-duplicado" : undefined}
                    />
                    {inventarioDuplicado && (
                      <small id="inventario-duplicado" className="field-error" role="alert">
                        Equipo ya existe: el número de inventario está registrado.
                      </small>
                    )}
                  </label>

                  <label>Marca
                    <input name="marca" value={equipoForm.marca} onChange={handleEquipoChange} />
                  </label>

                  <label>Modelo
                    <input name="modelo" value={equipoForm.modelo} onChange={handleEquipoChange} />
                  </label>

                  <label>Serie
                    <input name="serie" value={equipoForm.serie} onChange={handleEquipoChange} />
                  </label>

                  <label>Ubicación
                    <input name="ubicacion" value={equipoForm.ubicacion} onChange={handleEquipoChange} />
                  </label>

                  <label>INVIMA
                    <input name="invima" value={equipoForm.invima} onChange={handleEquipoChange} />
                  </label>

                  <label>Responsable actual
                    <select name="responsable_id" value={equipoForm.responsable_id} onChange={handleEquipoChange}>
                      <option value="">Sin responsable</option>
                      {usuarios.map((usuario) => (
                        <option key={usuario.id} value={usuario.id}>
                          {usuario.nombre_completo || usuario.username}
                        </option>
                      ))}
                    </select>
                  </label>

                  <label>Vida útil (meses)
                    <input
                      type="number"
                      min="1"
                      step="1"
                      name="vida_util_meses"
                      value={equipoForm.vida_util_meses}
                      onChange={handleEquipoChange}
                    />
                  </label>

                  <label>Estado
                    <select name="estado" value={equipoForm.estado} onChange={handleEquipoChange}>
                      <option value="OPERATIVO">Operativo</option>
                      <option value="EN_MANTENIMIENTO">En mantenimiento</option>
                      <option value="FUERA_DE_SERVICIO">Fuera de servicio</option>
                      <option value="BAJA">Baja</option>
                    </select>
                  </label>

                  <label>Criticidad
                    <select name="criticidad" value={equipoForm.criticidad} onChange={handleEquipoChange}>
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
                  <label>Adquisición
                    <input name="adquisicion" value={hojaForm.adquisicion} onChange={handleHojaChange} />
                  </label>

                  <label>Costo
                    <input type="number" name="costo" value={hojaForm.costo} onChange={handleHojaChange} />
                  </label>

                  <label>Fecha compra
                    <input type="date" name="fecha_compra" value={hojaForm.fecha_compra} onChange={handleHojaChange} />
                  </label>

                  <label>Fecha instalación
                    <input type="date" name="fecha_instalacion" value={hojaForm.fecha_instalacion} onChange={handleHojaChange} />
                  </label>

                  <label>Proveedor
                    <input name="proveedor" value={hojaForm.proveedor} onChange={handleHojaChange} />
                  </label>

                  <label>País fabricación
                    <input name="pais_fabricacion" value={hojaForm.pais_fabricacion} onChange={handleHojaChange} />
                  </label>

                  <label>Fecha fabricación
                    <input type="date" name="fecha_fabricacion" value={hojaForm.fecha_fabricacion} onChange={handleHojaChange} />
                  </label>

                  <label>Vida útil
                    <input name="vida_util" value={hojaForm.vida_util} onChange={handleHojaChange} placeholder="Ej: 10 años" />
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
                    <label key={name}>{label}
                      <input name={name} value={hojaForm[name]} onChange={handleHojaChange} />
                    </label>
                  ))}

                  <label className="full">Otros
                    <textarea name="otros" value={hojaForm.otros} onChange={handleHojaChange} />
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
                          <input type="checkbox" name={name} checked={Boolean(hojaForm[name])} onChange={handleHojaChange} />
                          {label}
                        </label>
                      ))}
                    </div>
                  </div>
                </div>
              )}

              <div className="enterprise-modal-actions">
                <button className="btn-secondary-enterprise" onClick={cerrarModal}><X size={18} />Cancelar</button>

                {paso === 2 && (
                  <button className="btn-secondary-enterprise" onClick={() => setPaso(1)}>
                    <ChevronLeft size={18} />Atrás
                  </button>
                )}

                {paso === 1 ? (
                  <button
                    className="btn-primary-enterprise"
                    onClick={guardarPaso1}
                    disabled={saving || cargandoHojaEdicion || inventarioDuplicado}
                  >
                    <ChevronRight size={18} />
                    {cargandoHojaEdicion
                      ? "Cargando hoja de vida..."
                      : saving
                        ? "Guardando..."
                        : "Guardar y continuar"}
                  </button>
                ) : (
                  <button className="btn-primary-enterprise" onClick={guardarHojaVida} disabled={saving}>
                    <Save size={18} />{saving ? "Guardando..." : "Finalizar hoja de vida"}
                  </button>
                )}
              </div>
            </div>
          </div>
        )}

        {modalImportar && (
          <div className="enterprise-modal-backdrop">
            <div className="enterprise-modal small">
              <div className="enterprise-modal-header">
                <div>
                  <span>Importación masiva</span>
                  <h2>Importar inventario Excel/CSV</h2>
                  <p>Columnas requeridas: codigo_inventario, nombre, empresa, sede, categoria, marca, modelo, serie, ubicacion, estado, criticidad.</p>
                </div>

                <button className="modal-close" onClick={() => setModalImportar(false)}>
                  <X size={22} />
                </button>
              </div>

              <div className="import-box">
                <UploadCloud size={42} />
                <strong>Selecciona un archivo .xlsx, .xls o .csv</strong>
                <input
                  ref={archivoImportarRef}
                  type="file"
                  accept=".xlsx,.xls,.csv"
                  onChange={(e) => {
                    setArchivoImportar(e.target.files?.[0] || null);
                    setResultadoImportacion(null);
                  }}
                />
                {archivoImportar && <span>{archivoImportar.name}</span>}
              </div>

              {resultadoImportacion && (
                <div className="import-result">
                  <h3>Resultado</h3>
                  <p><strong>Creados:</strong> {resultadoImportacion.creados || 0}</p>
                  <p>
                    <strong>Omitidos:</strong>{" "}
                    {resultadoImportacion.omitidos ?? resultadoImportacion.errores?.length ?? 0}
                  </p>

                  {resultadoImportacion.errores?.length > 0 && (
                    <div>
                      <strong>Errores:</strong>
                      <ul>
                        {resultadoImportacion.errores.map((err, index) => (
                          <li key={index}>Fila {err.fila}: {err.error}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              )}

              <div className="enterprise-modal-actions">
                <button className="btn-secondary-enterprise" onClick={() => setModalImportar(false)}>
                  <X size={18} />Cerrar
                </button>

                <button className="btn-primary-enterprise" onClick={importarInventario} disabled={saving}>
                  <UploadCloud size={18} />{saving ? "Importando..." : "Importar inventario"}
                </button>
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

                <button className="modal-close" aria-label="Cerrar" onClick={() => setDetalle(null)}>
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
                <p><strong>Responsable actual:</strong> {nombreResponsable(detalle.responsable_id)}</p>
                <p><strong>Vida útil:</strong> {detalle.vida_util_meses ? `${detalle.vida_util_meses} meses` : "N/A"}</p>
                <p><strong>Estado:</strong> {textoEstado(detalle.estado)}</p>
                <p><strong>Criticidad:</strong> {detalle.criticidad}</p>
              </div>

              {detalle.historial_cambios && (
                <div className="enterprise-table-wrapper">
                  <table className="enterprise-table">
                    <thead>
                      <tr>
                        <th>Fecha</th>
                        <th>Tipo</th>
                        <th>Campo</th>
                        <th>Anterior</th>
                        <th>Nuevo</th>
                        <th>Observación</th>
                      </tr>
                    </thead>
                    <tbody>
                      {detalle.historial_cambios.length ? detalle.historial_cambios.map((item, index) => (
                        <tr key={`${item.timestamp}-${item.campo}-${index}`}>
                          <td>{new Date(item.timestamp).toLocaleString("es-CO")}</td>
                          <td>{item.tipo_movimiento || "N/A"}</td>
                          <td>{item.campo || "N/A"}</td>
                          <td>{item.anterior ?? "N/A"}</td>
                          <td>{item.nuevo ?? "N/A"}</td>
                          <td>{item.observacion || "N/A"}</td>
                        </tr>
                      )) : (
                        <tr><td colSpan="6">Sin movimientos registrados.</td></tr>
                      )}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </div>
        )}

        {movimientoModal && (
          <div className="enterprise-modal-backdrop">
            <div className="enterprise-modal small">
              <div className="enterprise-modal-header">
                <div>
                  <span>Movimiento de activo</span>
                  <h2>{movimientoTipo === 'asignar' ? 'Asignar equipo' : movimientoTipo === 'devolver' ? 'Devolver equipo' : movimientoTipo === 'transferir' ? 'Transferir equipo' : 'Dar de baja'}</h2>
                  <p>Equipo: {movimientoEquipo?.nombre}</p>
                </div>
                <button className="modal-close" onClick={cerrarMovimientoModal}><X size={22} /></button>
              </div>

              <div className="enterprise-form-grid">
                {movimientoTipo === 'asignar' && (
                  <>
                    <label>Responsable *
                      <select name="responsable_id" value={movimientoForm.responsable_id} onChange={handleMovimientoChange} required>
                        <option value="">Seleccionar responsable</option>
                        {usuarios?.map((u) => <option key={u.id} value={u.id}>{u.nombre_completo || u.username} ({u.rol})</option>)}
                      </select>
                    </label>
                    <label>Ubicación
                      <input name="ubicacion" value={movimientoForm.ubicacion} onChange={handleMovimientoChange} placeholder="Nueva ubicación" />
                    </label>
                  </>
                )}

                {movimientoTipo === 'devolver' && (
                  <>
                    <label>Ubicación de devolución
                      <input name="ubicacion" value={movimientoForm.ubicacion} onChange={handleMovimientoChange} placeholder="Ubicación donde se devuelve" />
                    </label>
                  </>
                )}

                {movimientoTipo === 'transferir' && (
                  <>
                    <label>Nuevo responsable
                      <select name="nuevo_responsable_id" value={movimientoForm.nuevo_responsable_id} onChange={handleMovimientoChange}>
                        <option value="">Mantener actual</option>
                        {usuarios?.map((u) => <option key={u.id} value={u.id}>{u.nombre_completo || u.username} ({u.rol})</option>)}
                      </select>
                    </label>
                    <label>Nueva sede
                      <select name="nueva_sede_id" value={movimientoForm.nueva_sede_id} onChange={handleMovimientoChange}>
                        <option value="">Mantener actual</option>
                        {sedesOrdenadas.map((sede) => <option key={sede.id} value={sede.id}>{sede.nombre}</option>)}
                      </select>
                    </label>
                    <label>Nueva ubicación
                      <input name="nueva_ubicacion" value={movimientoForm.nueva_ubicacion} onChange={handleMovimientoChange} placeholder="Nueva ubicación" />
                    </label>
                  </>
                )}

                {movimientoTipo === 'baja' && (
                  <>
                    <label>Motivo *
                      <textarea name="motivo" value={movimientoForm.motivo} onChange={handleMovimientoChange} placeholder="Motivo de la baja" required />
                    </label>
                    <label>Estado final
                      <select name="estado_final" value={movimientoForm.estado_final} onChange={handleMovimientoChange}>
                        <option value="BAJA">Baja</option>
                        <option value="FUERA_DE_SERVICIO">Fuera de servicio</option>
                      </select>
                    </label>
                  </>
                )}

                <label className="full">Observación
                  <textarea name="observacion" value={movimientoForm.observacion} onChange={handleMovimientoChange} placeholder="Observaciones adicionales" />
                </label>
              </div>

              <div className="enterprise-modal-actions">
                <button className="btn-secondary-enterprise" onClick={cerrarMovimientoModal}><X size={18} />Cancelar</button>
                <button className="btn-primary-enterprise" onClick={ejecutarMovimientoConfirmado} disabled={saving}>
                  <Save size={18} />{saving ? "Ejecutando..." : "Ejecutar movimiento"}
                </button>
              </div>
            </div>
          </div>
        )}

        {(hojaCompleta || cargandoHoja) && (
          <div className="enterprise-modal-backdrop hoja-modal-wrap">
            <div className="enterprise-modal hoja-modal">
              <div className="enterprise-modal-header no-print">
                <div>
                  <span>Hoja de vida completa</span>
                  <h2>{cargandoHoja ? "Cargando..." : equipoHV.nombre}</h2>
                  <p>Vista profesional para impresión o descarga PDF desde el navegador.</p>
                </div>

                <div className="hoja-actions">
                  <button className="btn-secondary-enterprise" onClick={imprimirHojaVida}>
                    <Printer size={18} />Imprimir / PDF
                  </button>

                  <button className="btn-primary-enterprise" onClick={imprimirHojaVida}>
                    <Download size={18} />Descargar PDF
                  </button>

                  <button className="modal-close" onClick={() => setHojaCompleta(null)}>
                    <X size={22} />
                  </button>
                </div>
              </div>

              {cargandoHoja ? (
                <div className="loading-enterprise">Cargando hoja de vida...</div>
              ) : (
                <div className="hoja-print-area">
                  <div className="hoja-header">
                    <div>
                      <h1>HOJA DE VIDA TÉCNICA DEL EQUIPO</h1>
                      <p>{encabezadoHV.empresa_nombre || "Empresa no registrada"}</p>
                      <p>Sede: {encabezadoHV.sede_nombre || "N/A"}</p>
                    </div>

                    {encabezadoHV.empresa_logo_url ? (
                      <img src={encabezadoHV.empresa_logo_url} alt="Logo empresa" />
                    ) : (
                      <div className="hoja-logo-placeholder">VANER ASSET</div>
                    )}
                  </div>

                  <section className="hoja-section">
                    <h2>1. Datos básicos</h2>
                    <div className="hoja-grid">
                      <p><strong>Equipo:</strong> {equipoHV.nombre || "N/A"}</p>
                      <p><strong>Categoría:</strong> {equipoHV.categoria || "N/A"}</p>
                      <p><strong>Marca:</strong> {equipoHV.marca || "N/A"}</p>
                      <p><strong>Modelo:</strong> {equipoHV.modelo || "N/A"}</p>
                      <p><strong>Serie:</strong> {equipoHV.serie || "N/A"}</p>
                      <p><strong>Ubicación:</strong> {equipoHV.ubicacion || "N/A"}</p>
                      <p><strong>INVIMA:</strong> {equipoHV.invima || "N/A"}</p>
                      <p><strong>Código ID:</strong> {equipoHV.codigo_id || "N/A"}</p>
                      <p><strong>Inventario:</strong> {equipoHV.inventario || "N/A"}</p>
                      <p><strong>Estado:</strong> {textoEstado(equipoHV.estado)}</p>
                       <p><strong>Criticidad:</strong> {equipoHV.criticidad || "N/A"}</p>
                       <p><strong>Responsable actual:</strong> {nombreResponsable(equipoHV.responsable_id)}</p>
                       <p><strong>Vida útil:</strong> {equipoHV.vida_util_meses ? `${equipoHV.vida_util_meses} meses` : "N/A"}</p>
                    </div>
                  </section>

                  <section className="hoja-section">
                    <h2>2. Registro histórico</h2>
                    <div className="hoja-grid">
                      <p><strong>Adquisición:</strong> {tecnicaHV.adquisicion || "N/A"}</p>
                      <p><strong>Costo:</strong> {tecnicaHV.costo || "N/A"}</p>
                      <p><strong>Fecha compra:</strong> {tecnicaHV.fecha_compra || "N/A"}</p>
                      <p><strong>Fecha instalación:</strong> {tecnicaHV.fecha_instalacion || "N/A"}</p>
                      <p><strong>Proveedor:</strong> {tecnicaHV.proveedor || "N/A"}</p>
                      <p><strong>País fabricación:</strong> {tecnicaHV.pais_fabricacion || "N/A"}</p>
                      <p><strong>Fecha fabricación:</strong> {tecnicaHV.fecha_fabricacion || "N/A"}</p>
                      <p><strong>Vida útil:</strong> {tecnicaHV.vida_util || "N/A"}</p>
                      <p><strong>Requiere calibración:</strong> {boolText(tecnicaHV.requiere_calibracion)}</p>
                    </div>
                  </section>

                  <section className="hoja-section">
                    <h2>3. Registro técnico de funcionamiento</h2>
                    <div className="hoja-grid">
                      <p><strong>Voltaje:</strong> {tecnicaHV.rango_voltaje || "N/A"}</p>
                      <p><strong>Presión:</strong> {tecnicaHV.rango_presion || "N/A"}</p>
                      <p><strong>Gas refrigerante:</strong> {tecnicaHV.gas_refrigerante || "N/A"}</p>
                      <p><strong>Capacidad:</strong> {tecnicaHV.capacidad || "N/A"}</p>
                      <p><strong>Corriente:</strong> {tecnicaHV.rango_corriente || "N/A"}</p>
                      <p><strong>Velocidad:</strong> {tecnicaHV.rango_velocidad || "N/A"}</p>
                      <p><strong>Potencia:</strong> {tecnicaHV.rango_potencia || "N/A"}</p>
                      <p><strong>Temperatura:</strong> {tecnicaHV.rango_temperatura || "N/A"}</p>
                      <p><strong>Frecuencia:</strong> {tecnicaHV.frecuencia || "N/A"}</p>
                      <p><strong>Humedad:</strong> {tecnicaHV.rango_humedad || "N/A"}</p>
                    </div>
                    <p className="hoja-observacion"><strong>Otros:</strong> {tecnicaHV.otros || "N/A"}</p>
                  </section>

                  <section className="hoja-section">
                    <h2>4. Soporte técnico y clasificación</h2>
                    <div className="hoja-grid">
                      <p><strong>Manual operación:</strong> {boolText(tecnicaHV.manual_operacion)}</p>
                      <p><strong>Manual mantenimiento:</strong> {boolText(tecnicaHV.manual_mantenimiento)}</p>
                      <p><strong>Manual partes:</strong> {boolText(tecnicaHV.manual_partes)}</p>
                      <p><strong>Manual despiece:</strong> {boolText(tecnicaHV.manual_despiece)}</p>
                      <p><strong>Plano electrónico:</strong> {boolText(tecnicaHV.plano_electronico)}</p>
                      <p><strong>Plano eléctrico:</strong> {boolText(tecnicaHV.plano_electrico)}</p>
                      <p><strong>Plano neumático:</strong> {boolText(tecnicaHV.plano_neumatico)}</p>
                      <p><strong>Plano mecánico:</strong> {boolText(tecnicaHV.plano_mecanico)}</p>
                      <p><strong>Diagnóstico:</strong> {boolText(tecnicaHV.clase_diagnostico)}</p>
                      <p><strong>Prevención:</strong> {boolText(tecnicaHV.clase_prevencion)}</p>
                      <p><strong>Rehabilitación:</strong> {boolText(tecnicaHV.clase_rehabilitacion)}</p>
                      <p><strong>Análisis:</strong> {boolText(tecnicaHV.clase_analisis)}</p>
                      <p><strong>Riesgo bajo:</strong> {boolText(tecnicaHV.riesgo_bajo)}</p>
                      <p><strong>Riesgo moderado:</strong> {boolText(tecnicaHV.riesgo_moderado)}</p>
                      <p><strong>Riesgo alto:</strong> {boolText(tecnicaHV.riesgo_alto)}</p>
                      <p><strong>Riesgo elevado:</strong> {boolText(tecnicaHV.riesgo_elevado)}</p>
                    </div>
                  </section>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </AdminLayout>
  );
}
