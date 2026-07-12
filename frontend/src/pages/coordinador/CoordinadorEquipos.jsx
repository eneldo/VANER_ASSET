/*
===========================================================
COORDINADOR — INVENTARIO / EQUIPOS PRO
Archivo: frontend/src/pages/coordinador/CoordinadorEquipos.jsx
===========================================================
*/

import { useEffect, useEffectEvent, useMemo, useState } from "react";
import API from "../../api/axios";
import { PackageSearch, Plus, Pencil, Save, X, RefreshCw, Search, FileText } from "lucide-react";
import { useNavigate } from "react-router-dom";
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
  const [form, setForm] = useState(formInicial);
  const [modal, setModal] = useState(false);
  const [editando, setEditando] = useState(false);
  const [cargando, setCargando] = useState(true);
  const [mensaje, setMensaje] = useState(null);
  const [pagina, setPagina] = useState(1);

  const registrosPorPagina = 9;

  const cargarDatosAlMontar = useEffectEvent(() => cargarDatos());

  useEffect(() => {
    cargarDatosAlMontar();
  }, []);

  const mostrarMensaje = (tipo, texto) => {
    setMensaje({ tipo, texto });
    setTimeout(() => setMensaje(null), 3500);
  };

  async function cargarDatos() {
    try {
      setCargando(true);
      const [resEquipos, resCatalogos] = await Promise.all([
        API.get("/coordinador/equipos"),
        API.get("/coordinador/catalogos"),
      ]);

      setEquipos(resEquipos.data || []);
      setCatalogos(resCatalogos.data || { sedes: [], categorias: [] });
    } catch (error) {
      console.error("Error cargando equipos coordinador:", error);
      mostrarMensaje("error", "No se pudo cargar el inventario.");
    } finally {
      setCargando(false);
    }
  };

  const abrirCrear = () => {
    setForm(formInicial);
    setEditando(false);
    setModal(true);
  };

  const abrirEditar = (equipo) => {
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

  const guardar = async (e) => {
    e.preventDefault();

    if (!form.nombre || !form.sede_id) {
      mostrarMensaje("error", "Nombre y sede son obligatorios.");
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
        categoria_id: form.categoria_id || null,
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

  const equiposFiltrados = useMemo(() => {
    const texto = busqueda.toLowerCase();
    return equipos.filter((e) =>
      `${e.nombre || ""} ${e.marca || ""} ${e.modelo || ""} ${e.serie || ""} ${e.ubicacion || ""} ${e.codigo_id || ""} ${e.inventario || ""}`
        .toLowerCase()
        .includes(texto)
    );
  }, [equipos, busqueda]);

  const totalPaginas = Math.max(1, Math.ceil(equiposFiltrados.length / registrosPorPagina));
  const visibles = equiposFiltrados.slice((pagina - 1) * registrosPorPagina, pagina * registrosPorPagina);

  return (
    <div className="coord-page">
      <div className="coord-hero">
        <div>
          <span className="coord-eyebrow">INVENTARIO · EQUIPOS</span>
          <h2>Inventario de Equipos</h2>
          <p>Consulta, creación y actualización de equipos asociados a la empresa del coordinador.</p>
        </div>

        <div className="coord-actions">
          <button className="coord-btn secondary" onClick={cargarDatos}>
            <RefreshCw size={17} />
            Actualizar
          </button>
          <button className="coord-btn primary" onClick={abrirCrear}>
            <Plus size={17} />
            Nuevo equipo
          </button>
        </div>
      </div>

      {mensaje && <div className={`coord-alert ${mensaje.tipo}`}>{mensaje.texto}</div>}

      <div className="coord-filters">
        <div className="coord-search">
          <Search size={18} />
          <input
            placeholder="Buscar por nombre, marca, modelo, serie, ubicación o inventario..."
            value={busqueda}
            onChange={(e) => { setBusqueda(e.target.value); setPagina(1); }}
          />
        </div>
      </div>

      <div className="coord-card-grid">
        {visibles.length === 0 ? (
          <div className="coord-card">
            <p className="coord-empty">No hay equipos disponibles.</p>
          </div>
        ) : (
          visibles.map((equipo) => (
            <article className="coord-equipo-card" key={equipo.id}>
              <div className="coord-equipo-top">
                <div className="coord-equipo-icon"><PackageSearch size={24} /></div>
                <span className={`coord-badge ${String(equipo.criticidad || "media").toLowerCase()}`}>
                  {equipo.criticidad || "MEDIA"}
                </span>
              </div>

              <h3>{equipo.nombre || "Equipo sin nombre"}</h3>
              <p>{equipo.marca || "Sin marca"} · {equipo.modelo || "Sin modelo"}</p>

              <div className="coord-equipo-meta">
                <span>Serie: <strong>{equipo.serie || "N/A"}</strong></span>
                <span>Inventario: <strong>{equipo.inventario || equipo.codigo_inventario || "N/A"}</strong></span>
                <span>Ubicación: <strong>{equipo.ubicacion || "N/A"}</strong></span>
                <span>Sede: <strong>{equipo.sede_nombre || "N/A"}</strong></span>
              </div>

              <div className="coord-equipo-actions">
                <button onClick={() => abrirEditar(equipo)}>
                  <Pencil size={16} />
                  Editar
                </button>
                <button onClick={() => navigate(`/coordinador/equipos/${equipo.id}/hoja-vida`)}>
                  <FileText size={16} />
                  Hoja de vida
                </button>
              </div>
            </article>
          ))
        )}
      </div>

      <div className="coord-pagination">
        <button disabled={pagina <= 1} onClick={() => setPagina((p) => p - 1)}>Anterior</button>
        <span>Página {pagina} de {totalPaginas}</span>
        <button disabled={pagina >= totalPaginas} onClick={() => setPagina((p) => p + 1)}>Siguiente</button>
      </div>

      {modal && (
        <div className="coord-modal-backdrop">
          <div className="coord-modal large">
            <div className="coord-modal-header">
              <div>
                <h3>{editando ? "Editar equipo" : "Nuevo equipo"}</h3>
                <p>Datos básicos del inventario.</p>
              </div>
              <button onClick={cerrarModal}><X size={18} /></button>
            </div>

            <form onSubmit={guardar} className="coord-form-grid">
              <label>
                Nombre del equipo
                <input value={form.nombre} onChange={(e) => setForm({ ...form, nombre: e.target.value })} required />
              </label>

              <label>
                Sede
                <select value={form.sede_id} onChange={(e) => setForm({ ...form, sede_id: e.target.value })} required>
                  <option value="">Seleccionar sede</option>
                  {catalogos.sedes?.map((s) => <option key={s.id} value={s.id}>{s.nombre}</option>)}
                </select>
              </label>

              <label>
                Categoría
                <select required value={form.categoria_id} onChange={(e) => setForm({ ...form, categoria_id: e.target.value })}>
                  <option value="">Sin categoría</option>
                  {catalogos.categorias?.map((c) => <option key={c.id} value={c.id}>{c.nombre}</option>)}
                </select>
              </label>

              <label>
                Marca
                <input value={form.marca} onChange={(e) => setForm({ ...form, marca: e.target.value })} />
              </label>

              <label>
                Modelo
                <input value={form.modelo} onChange={(e) => setForm({ ...form, modelo: e.target.value })} />
              </label>

              <label>
                Serie
                <input value={form.serie} onChange={(e) => setForm({ ...form, serie: e.target.value })} />
              </label>

              <label>
                Código ID
                <input value={form.codigo_id} onChange={(e) => setForm({ ...form, codigo_id: e.target.value })} />
              </label>

              <label>
                Inventario
                <input value={form.inventario} onChange={(e) => setForm({ ...form, inventario: e.target.value })} />
              </label>

              <label>
                Estado
                <select value={form.estado} onChange={(e) => setForm({ ...form, estado: e.target.value })}>
                  {ESTADOS.map((estado) => <option key={estado} value={estado}>{estado}</option>)}
                </select>
              </label>

              <label>
                Criticidad
                <select value={form.criticidad} onChange={(e) => setForm({ ...form, criticidad: e.target.value })}>
                  {CRITICIDADES.map((c) => <option key={c} value={c}>{c}</option>)}
                </select>
              </label>

              <label className="span-2">
                Ubicación
                <input value={form.ubicacion} onChange={(e) => setForm({ ...form, ubicacion: e.target.value })} />
              </label>

              <div className="coord-modal-actions span-2">
                <button type="button" className="coord-btn secondary" onClick={cerrarModal}>
                  <X size={17} />
                  Cancelar
                </button>
                <button type="submit" className="coord-btn primary" disabled={cargando}>
                  <Save size={17} />
                  Guardar
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
