import { useEffect, useEffectEvent, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  Download,
  Eye,
  FileText,
  Pencil,
  Plus,
  RefreshCw,
  Save,
  Search,
  Wrench,
  X,
} from "lucide-react";

import API from "../../api/axios";
import "../../styles/coordinador.css";

const ESTADOS = ["OPERATIVO", "EN_MANTENIMIENTO", "FUERA_DE_SERVICIO", "BAJA"];
const CRITICIDADES = ["BAJA", "MEDIA", "ALTA", "CRITICA"];

const formInicial = {
  id: null,
  nombre: "",
  marca: "",
  modelo: "",
  serie: "",
  ubicacion: "",
  codigo_id: "",
  inventario: "",
  estado: "OPERATIVO",
  criticidad: "MEDIA",
  sede_id: "",
  categoria_id: "",
};

export default function CoordinadorEquipos() {
  const navigate = useNavigate();
  const [equipos, setEquipos] = useState([]);
  const [catalogos, setCatalogos] = useState({ sedes: [], categorias: [] });
  const [busqueda, setBusqueda] = useState("");
  const [filtroSede, setFiltroSede] = useState("");
  const [filtroCategoria, setFiltroCategoria] = useState("");
  const [filtroEstado, setFiltroEstado] = useState("");
  const [filtroCriticidad, setFiltroCriticidad] = useState("");
  const [form, setForm] = useState(formInicial);
  const [modal, setModal] = useState(false);
  const [detalle, setDetalle] = useState(null);
  const [editando, setEditando] = useState(false);
  const [cargando, setCargando] = useState(true);
  const [exportando, setExportando] = useState(false);
  const [mensaje, setMensaje] = useState(null);
  const [pagina, setPagina] = useState(1);
  const [totalEquipos, setTotalEquipos] = useState(0);
  const registrosPorPagina = 10;

  const cargarDatosAlCambiarFiltros = useEffectEvent(() => cargarDatos());

  useEffect(() => {
    const timer = window.setTimeout(cargarDatosAlCambiarFiltros, 250);
    return () => window.clearTimeout(timer);
  }, [busqueda, filtroSede, filtroCategoria, filtroEstado, filtroCriticidad, pagina]);

  const mostrarMensaje = (tipo, texto) => {
    setMensaje({ tipo, texto });
    window.setTimeout(() => setMensaje(null), 3500);
  };

  async function cargarDatos() {
    try {
      setCargando(true);
      const [resEquipos, resCatalogos] = await Promise.all([
        API.get("/coordinador/equipos", {
          params: {
            busqueda: busqueda || undefined,
            sede_id: filtroSede || undefined,
            categoria_id: filtroCategoria || undefined,
            estado: filtroEstado || undefined,
            criticidad: filtroCriticidad || undefined,
            limit: registrosPorPagina,
            offset: (pagina - 1) * registrosPorPagina,
          },
        }),
        API.get("/coordinador/catalogos"),
      ]);
      setEquipos(resEquipos.data || []);
      setTotalEquipos(Number(resEquipos.headers?.["x-total-count"] || resEquipos.data?.length || 0));
      setCatalogos(resCatalogos.data || { sedes: [], categorias: [] });
    } catch (error) {
      console.error("Error cargando inventario:", error);
      mostrarMensaje("error", "No se pudo cargar el inventario.");
    } finally {
      setCargando(false);
    }
  }

  async function exportarInventario() {
    try {
      setExportando(true);
      const response = await API.get("/coordinador/equipos/exportar", {
        responseType: "blob",
        params: {
          busqueda: busqueda || undefined,
          sede_id: filtroSede || undefined,
          categoria_id: filtroCategoria || undefined,
          estado: filtroEstado || undefined,
          criticidad: filtroCriticidad || undefined,
        },
      });
      const disposition = response.headers["content-disposition"] || "";
      const match = disposition.match(/filename="?([^";]+)"?/i);
      const url = URL.createObjectURL(response.data);
      const link = document.createElement("a");
      link.href = url;
      link.download = match?.[1] || "inventario_equipos_coordinador.xlsx";
      document.body.appendChild(link);
      link.click();
      link.remove();
      URL.revokeObjectURL(url);
      mostrarMensaje("success", "Inventario exportado correctamente.");
    } catch (error) {
      console.error("Error exportando inventario:", error);
      mostrarMensaje("error", "No se pudo exportar el inventario.");
    } finally {
      setExportando(false);
    }
  }

  const abrirCrear = () => {
    setForm(formInicial);
    setEditando(false);
    setModal(true);
  };

  const abrirEditar = (equipo) => {
    setDetalle(null);
    setForm({
      id: equipo.id,
      nombre: equipo.nombre || "",
      marca: equipo.marca || "",
      modelo: equipo.modelo || "",
      serie: equipo.serie || "",
      ubicacion: equipo.ubicacion || "",
      codigo_id: equipo.codigo_id || "",
      inventario: equipo.inventario || equipo.codigo_inventario || "",
      estado: equipo.estado || "OPERATIVO",
      criticidad: equipo.criticidad || "MEDIA",
      sede_id: equipo.sede_id || "",
      categoria_id: equipo.categoria_id || "",
    });
    setEditando(true);
    setModal(true);
  };

  const cerrarModal = () => {
    setModal(false);
    setForm(formInicial);
    setEditando(false);
  };

  const guardar = async (event) => {
    event.preventDefault();
    if (!form.nombre || !form.sede_id || !form.categoria_id) {
      mostrarMensaje("error", "Nombre, sede y categoria son obligatorios.");
      return;
    }

    try {
      setCargando(true);
      const payload = {
        nombre: form.nombre,
        marca: form.marca || null,
        modelo: form.modelo || null,
        serie: form.serie || null,
        ubicacion: form.ubicacion || null,
        codigo_id: form.codigo_id || null,
        inventario: form.inventario || null,
        estado: form.estado,
        criticidad: form.criticidad,
        sede_id: form.sede_id,
        categoria_id: form.categoria_id,
      };

      if (editando && form.id) {
        await API.put(`/coordinador/equipos/${form.id}`, payload);
        mostrarMensaje("success", "Equipo actualizado correctamente.");
      } else {
        await API.post("/coordinador/equipos", payload);
        mostrarMensaje("success", "Equipo creado correctamente.");
      }
      cerrarModal();
      await cargarDatos();
    } catch (error) {
      console.error("Error guardando equipo:", error);
      mostrarMensaje("error", error?.response?.data?.detail || "No se pudo guardar el equipo.");
    } finally {
      setCargando(false);
    }
  };

  const totalPaginas = Math.max(1, Math.ceil(totalEquipos / registrosPorPagina));
  const visibles = equipos;

  return (
    <div className="coord-page">
      <div className="coord-hero">
        <div>
          <span className="coord-eyebrow">INVENTARIO - EQUIPOS</span>
          <h2>Inventario de Equipos</h2>
          <p>Listado profesional, filtros, edicion y acceso directo a la hoja de vida.</p>
        </div>
        <div className="coord-actions">
          <button type="button" className="coord-btn secondary" onClick={exportarInventario} disabled={exportando}>
            <Download size={17} />{exportando ? "Exportando..." : "Exportar filtrado"}
          </button>
          <button type="button" className="coord-btn secondary" onClick={cargarDatos}><RefreshCw size={17} />Actualizar</button>
          <button className="coord-btn primary" onClick={abrirCrear}><Plus size={17} />Nuevo equipo</button>
        </div>
      </div>

      {mensaje && <div className={`coord-alert ${mensaje.tipo}`}>{mensaje.texto}</div>}

      <div className="coord-filters coord-inventory-filters">
        <div className="coord-search">
          <Search size={18} />
          <input
            placeholder="Buscar nombre, inventario, codigo, serie, marca o ubicacion"
            value={busqueda}
            onChange={(event) => { setBusqueda(event.target.value); setPagina(1); }}
          />
        </div>
        <select value={filtroSede} onChange={(event) => { setFiltroSede(event.target.value); setPagina(1); }}>
          <option value="">Todas las sedes</option>
          {catalogos.sedes?.map((sede) => <option key={sede.id} value={sede.id}>{sede.nombre}</option>)}
        </select>
        <select value={filtroCategoria} onChange={(event) => { setFiltroCategoria(event.target.value); setPagina(1); }}>
          <option value="">Todas las categorias</option>
          {catalogos.categorias?.map((categoria) => <option key={categoria.id} value={categoria.id}>{categoria.nombre}</option>)}
        </select>
        <select value={filtroEstado} onChange={(event) => { setFiltroEstado(event.target.value); setPagina(1); }}>
          <option value="">Todos los estados</option>
          {ESTADOS.map((estado) => <option key={estado} value={estado}>{estado}</option>)}
        </select>
        <select value={filtroCriticidad} onChange={(event) => { setFiltroCriticidad(event.target.value); setPagina(1); }}>
          <option value="">Todas las criticidades</option>
          {CRITICIDADES.map((criticidad) => <option key={criticidad} value={criticidad}>{criticidad}</option>)}
        </select>
      </div>

      <section className="coord-card coord-inventory-table-card">
        <div className="coord-table-wrap">
          <table className="coord-table coord-inventory-table">
            <thead><tr><th>Inventario</th><th>Equipo</th><th>Categoria</th><th>Sede / ubicacion</th><th>Marca / modelo</th><th>Serie</th><th>Estado</th><th>Criticidad</th><th>Acciones</th></tr></thead>
            <tbody>
              {cargando ? (
                <tr><td colSpan="9" className="coord-empty">Cargando inventario...</td></tr>
              ) : visibles.length === 0 ? (
                <tr><td colSpan="9" className="coord-empty">No hay equipos disponibles.</td></tr>
              ) : visibles.map((equipo) => (
                <tr key={equipo.id}>
                  <td><strong>{equipo.inventario || equipo.codigo_inventario || "N/A"}</strong><small>{equipo.codigo_id || "Sin codigo"}</small></td>
                  <td><strong>{equipo.nombre || "Equipo sin nombre"}</strong></td>
                  <td>{equipo.categoria_nombre || "N/A"}</td>
                  <td><strong>{equipo.sede_nombre || "N/A"}</strong><small>{equipo.ubicacion || "Sin ubicacion"}</small></td>
                  <td><strong>{equipo.marca || "N/A"}</strong><small>{equipo.modelo || "Sin modelo"}</small></td>
                  <td>{equipo.serie || "N/A"}</td>
                  <td><span className={`coord-badge ${String(equipo.estado || "").toLowerCase()}`}>{equipo.estado || "N/A"}</span></td>
                  <td><span className={`coord-badge ${String(equipo.criticidad || "media").toLowerCase()}`}>{equipo.criticidad || "MEDIA"}</span></td>
                  <td><div className="coord-table-actions">
                    <button type="button" onClick={() => setDetalle(equipo)} title="Ver detalle" aria-label={"Ver detalle de " + equipo.nombre}><Eye size={16} /></button>
                    <button type="button" onClick={() => abrirEditar(equipo)} title="Editar" aria-label={"Editar " + equipo.nombre}><Pencil size={16} /></button>
                    <button type="button" onClick={() => navigate(`/coordinador/hoja-vida/${equipo.id}`)} title="Hoja de vida" aria-label={"Ver hoja de vida de " + equipo.nombre}><FileText size={16} /></button>
                    <button type="button" onClick={() => navigate(`/coordinador/mantenimientos?equipo_id=${equipo.id}`)} title="Mantenimientos" aria-label={"Ver mantenimientos de " + equipo.nombre}><Wrench size={16} /></button>
                  </div></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <div className="coord-pagination">
        <button type="button" disabled={pagina <= 1} onClick={() => setPagina((valor) => valor - 1)}>Anterior</button>
        <span>Página {pagina} de {totalPaginas} - {totalEquipos} equipos</span>
        <button type="button" disabled={pagina >= totalPaginas} onClick={() => setPagina((valor) => valor + 1)}>Siguiente</button>
      </div>

      {modal && <EquipoModal form={form} setForm={setForm} editando={editando} cargando={cargando} catalogos={catalogos} guardar={guardar} cerrar={cerrarModal} />}
      {detalle && <DetalleEquipo equipo={detalle} cerrar={() => setDetalle(null)} editar={abrirEditar} abrirHoja={() => navigate(`/coordinador/hoja-vida/${detalle.id}`)} />}
    </div>
  );
}

function EquipoModal({ form, setForm, editando, cargando, catalogos, guardar, cerrar }) {
  return (
    <div className="coord-modal-backdrop">
      <div className="coord-modal large">
        <div className="coord-modal-header"><div><h3>{editando ? "Editar equipo" : "Nuevo equipo"}</h3><p>Datos básicos del inventario.</p></div><button type="button" onClick={cerrar} aria-label="Cerrar formulario de equipo"><X size={18} /></button></div>
        <form onSubmit={guardar} className="coord-form-grid">
          <label>Nombre del equipo<input value={form.nombre} onChange={(event) => setForm({ ...form, nombre: event.target.value })} required /></label>
          <label>Sede<select value={form.sede_id} onChange={(event) => setForm({ ...form, sede_id: event.target.value })} required><option value="">Seleccionar sede</option>{catalogos.sedes?.map((sede) => <option key={sede.id} value={sede.id}>{sede.nombre}</option>)}</select></label>
          <label>Categoria<select value={form.categoria_id} onChange={(event) => setForm({ ...form, categoria_id: event.target.value })} required><option value="">Seleccionar categoria</option>{catalogos.categorias?.map((categoria) => <option key={categoria.id} value={categoria.id}>{categoria.nombre}</option>)}</select></label>
          <label>Marca<input value={form.marca} onChange={(event) => setForm({ ...form, marca: event.target.value })} /></label>
          <label>Modelo<input value={form.modelo} onChange={(event) => setForm({ ...form, modelo: event.target.value })} /></label>
          <label>Serie<input value={form.serie} onChange={(event) => setForm({ ...form, serie: event.target.value })} /></label>
          <label>Codigo ID<input value={form.codigo_id} onChange={(event) => setForm({ ...form, codigo_id: event.target.value })} /></label>
          <label>Inventario<input value={form.inventario} onChange={(event) => setForm({ ...form, inventario: event.target.value })} /></label>
          <label>Estado<select value={form.estado} onChange={(event) => setForm({ ...form, estado: event.target.value })}>{ESTADOS.map((estado) => <option key={estado} value={estado}>{estado}</option>)}</select></label>
          <label>Criticidad<select value={form.criticidad} onChange={(event) => setForm({ ...form, criticidad: event.target.value })}>{CRITICIDADES.map((criticidad) => <option key={criticidad} value={criticidad}>{criticidad}</option>)}</select></label>
          <label className="span-2">Ubicacion<input value={form.ubicacion} onChange={(event) => setForm({ ...form, ubicacion: event.target.value })} /></label>
          <div className="coord-modal-actions span-2"><button type="button" className="coord-btn secondary" onClick={cerrar}><X size={17} />Cancelar</button><button type="submit" className="coord-btn primary" disabled={cargando}><Save size={17} />Guardar</button></div>
        </form>
      </div>
    </div>
  );
}

function DetalleEquipo({ equipo, cerrar, editar, abrirHoja }) {
  const campos = [
    ["Inventario", equipo.inventario], ["Codigo", equipo.codigo_id], ["Categoria", equipo.categoria_nombre],
    ["Sede", equipo.sede_nombre], ["Ubicacion", equipo.ubicacion], ["Marca", equipo.marca],
    ["Modelo", equipo.modelo], ["Serie", equipo.serie], ["Estado", equipo.estado], ["Criticidad", equipo.criticidad],
  ];
  return (
    <div className="coord-modal-backdrop"><div className="coord-modal"><div className="coord-modal-header"><div><h3>{equipo.nombre}</h3><p>Detalle completo del activo.</p></div><button type="button" onClick={cerrar} aria-label="Cerrar detalle del equipo"><X size={18} /></button></div><div className="coord-detail-grid">{campos.map(([label, value]) => <div key={label}><span>{label}</span><strong>{value || "N/A"}</strong></div>)}</div><div className="coord-modal-actions"><button type="button" className="coord-btn secondary" onClick={() => editar(equipo)}><Pencil size={16} />Editar</button><button type="button" className="coord-btn primary" onClick={abrirHoja}><FileText size={16} />Hoja de vida</button></div></div></div>
  );
}
