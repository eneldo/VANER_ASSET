/*
===========================================================
COORDINADOR — INVENTARIO / EQUIPOS PRO
Archivo: frontend/src/pages/coordinador/CoordinadorEquipos.jsx
Permisos usados:
- EQUIPOS_VER / INVENTARIO_VER
- EQUIPOS_CREAR
- EQUIPOS_EDITAR
===========================================================
*/

import React, { useEffect, useMemo, useState } from "react";
import API from "../../api/axios";
import { PackageSearch, Plus, Pencil, Save, X, RefreshCw, Search } from "lucide-react";
import "../../styles/coordinador.css";

const ESTADOS = ["ACTIVO", "INACTIVO", "MANTENIMIENTO", "FUERA_DE_SERVICIO"];
const CRITICIDADES = ["BAJA", "MEDIA", "ALTA", "CRITICA"];

const formInicial = {
  id: null,
  codigo_inventario: "",
  nombre: "",
  marca: "",
  modelo: "",
  serie: "",
  ubicacion: "",
  estado: "ACTIVO",
  criticidad: "MEDIA",
  empresa_id: "",
  sede_id: "",
  categoria_id: "",
};

export default function CoordinadorEquipos() {
  const [equipos, setEquipos] = useState([]);
  const [catalogos, setCatalogos] = useState({ empresas: [], sedes: [], equipos: [] });
  const [permisos, setPermisos] = useState([]);
  const [busqueda, setBusqueda] = useState("");
  const [form, setForm] = useState(formInicial);
  const [modal, setModal] = useState(false);
  const [editando, setEditando] = useState(false);
  const [cargando, setCargando] = useState(true);
  const [mensaje, setMensaje] = useState(null);

  useEffect(() => {
    cargarDatos();
  }, []);

  const cargarDatos = async () => {
    try {
      setCargando(true);
      const [resCatalogos, resPermisos] = await Promise.all([
        API.get("/coordinador/catalogos"),
        API.get("/permisos/me"),
      ]);

      const dataCatalogos = resCatalogos.data || { equipos: [], empresas: [], sedes: [] };
      setCatalogos(dataCatalogos);
      setEquipos(dataCatalogos.equipos || []);
      setPermisos(resPermisos.data?.permisos_finales || []);
    } catch (error) {
      console.error("Error cargando equipos coordinador:", error);
      mostrarMensaje("error", "No se pudo cargar el inventario de equipos.");
    } finally {
      setCargando(false);
    }
  };

  const tienePermiso = (...codigos) => codigos.some((c) => permisos.includes(c));

  const puedeVer = tienePermiso("EQUIPOS_VER", "INVENTARIO_VER");
  const puedeCrear = tienePermiso("EQUIPOS_CREAR");
  const puedeEditar = tienePermiso("EQUIPOS_EDITAR");

  const mostrarMensaje = (tipo, texto) => {
    setMensaje({ tipo, texto });
    setTimeout(() => setMensaje(null), 3500);
  };

  const nombreSede = (id) => {
    const sede = catalogos.sedes?.find((s) => String(s.id) === String(id));
    return sede?.nombre || "Sin sede";
  };

  const equiposFiltrados = useMemo(() => {
    const texto = busqueda.toLowerCase();
    return equipos.filter((e) =>
      `${e.nombre || ""} ${e.codigo || ""} ${e.codigo_inventario || ""} ${e.serie || ""} ${e.marca || ""} ${e.modelo || ""}`
        .toLowerCase()
        .includes(texto)
    );
  }, [equipos, busqueda]);

  const abrirCrear = () => {
    setEditando(false);
    const empresaId = catalogos.empresas?.[0]?.id || "";
    setForm({ ...formInicial, empresa_id: empresaId });
    setModal(true);
  };

  const abrirEditar = (equipo) => {
    setEditando(true);
    setForm({
      id: equipo.id,
      codigo_inventario: equipo.codigo_inventario || equipo.codigo || "",
      nombre: equipo.nombre || equipo.nombre_completo || "",
      marca: equipo.marca || "",
      modelo: equipo.modelo || "",
      serie: equipo.serie || "",
      ubicacion: equipo.ubicacion || "",
      estado: equipo.estado || "ACTIVO",
      criticidad: equipo.criticidad || "MEDIA",
      empresa_id: equipo.empresa_id || catalogos.empresas?.[0]?.id || "",
      sede_id: equipo.sede_id || "",
      categoria_id: equipo.categoria_id || "",
    });
    setModal(true);
  };

  const cerrarModal = () => {
    setModal(false);
    setEditando(false);
    setForm(formInicial);
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const guardarEquipo = async (e) => {
    e.preventDefault();

    if (!form.nombre) {
      mostrarMensaje("error", "El nombre del equipo es obligatorio.");
      return;
    }

    try {
      const payload = {
        codigo_inventario: form.codigo_inventario,
        nombre: form.nombre,
        marca: form.marca,
        modelo: form.modelo,
        serie: form.serie,
        ubicacion: form.ubicacion,
        estado: form.estado,
        criticidad: form.criticidad,
        empresa_id: form.empresa_id || null,
        sede_id: form.sede_id || null,
        categoria_id: form.categoria_id || null,
      };

      if (editando) {
        await API.put(`/equipos/${form.id}`, payload);
        mostrarMensaje("success", "Equipo actualizado correctamente.");
      } else {
        await API.post("/equipos/", payload);
        mostrarMensaje("success", "Equipo creado correctamente.");
      }

      cerrarModal();
      cargarDatos();
    } catch (error) {
      console.error("Error guardando equipo:", error);
      mostrarMensaje("error", error.response?.data?.detail || "No se pudo guardar el equipo.");
    }
  };

  if (!puedeVer) {
    return <div className="coord-alert error">No tienes permiso para ver inventario/equipos.</div>;
  }

  return (
    <div className="coord-page">
      <div className="coord-page-header">
        <div>
          <span className="coord-eyebrow">Inventario</span>
          <h2>Equipos de la empresa</h2>
          <p>Consulta, crea o edita equipos según permisos asignados al coordinador.</p>
        </div>

        <div className="coord-actions">
          <button className="coord-secondary-btn" onClick={cargarDatos}>
            <RefreshCw size={17} /> Actualizar
          </button>
          {puedeCrear && (
            <button className="coord-primary-btn" onClick={abrirCrear}>
              <Plus size={17} /> Crear equipo
            </button>
          )}
        </div>
      </div>

      {mensaje && <div className={`coord-alert ${mensaje.tipo === "error" ? "error" : "success"}`}>{mensaje.texto}</div>}

      <div className="coord-filters">
        <div className="coord-search">
          <Search size={18} />
          <input value={busqueda} onChange={(e) => setBusqueda(e.target.value)} placeholder="Buscar por nombre, código, serie, marca o modelo..." />
        </div>
      </div>

      <div className="coord-card">
        <div className="coord-card-header">
          <div>
            <h3>Inventario registrado</h3>
            <p>{equiposFiltrados.length} equipos encontrados.</p>
          </div>
          <PackageSearch size={26} />
        </div>

        <div className="coord-table-wrap">
          <table className="coord-table">
            <thead>
              <tr>
                <th>Código</th>
                <th>Equipo</th>
                <th>Marca / Modelo</th>
                <th>Serie</th>
                <th>Sede</th>
                <th>Estado</th>
                <th>Criticidad</th>
                <th>Acciones</th>
              </tr>
            </thead>
            <tbody>
              {cargando ? (
                <tr><td colSpan="8" className="coord-empty">Cargando equipos...</td></tr>
              ) : equiposFiltrados.length === 0 ? (
                <tr><td colSpan="8" className="coord-empty">No hay equipos para mostrar.</td></tr>
              ) : (
                equiposFiltrados.map((equipo) => (
                  <tr key={equipo.id}>
                    <td>{equipo.codigo_inventario || equipo.codigo || "N/A"}</td>
                    <td><strong>{equipo.nombre || equipo.nombre_completo || "Equipo"}</strong></td>
                    <td>{equipo.marca || "N/A"} {equipo.modelo || ""}</td>
                    <td>{equipo.serie || "N/A"}</td>
                    <td>{nombreSede(equipo.sede_id)}</td>
                    <td><span className="coord-status asignado">{equipo.estado || "ACTIVO"}</span></td>
                    <td>{equipo.criticidad || "MEDIA"}</td>
                    <td>
                      {puedeEditar ? (
                        <button className="btn-table btn-edit" onClick={() => abrirEditar(equipo)}>
                          <Pencil size={15} /> Editar
                        </button>
                      ) : "Sin permiso"}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {modal && (
        <div className="modal-overlay-pro">
          <div className="modal-pro">
            <div className="modal-header-pro">
              <div>
                <h2>{editando ? "Editar equipo" : "Crear equipo"}</h2>
                <p>La empresa queda controlada por la empresa asignada al coordinador.</p>
              </div>
              <button className="modal-close" onClick={cerrarModal}>×</button>
            </div>

            <form className="form-pro" onSubmit={guardarEquipo}>
              <div className="form-grid">
                <div className="form-group">
                  <label>Código inventario</label>
                  <input name="codigo_inventario" value={form.codigo_inventario} onChange={handleChange} />
                </div>
                <div className="form-group">
                  <label>Nombre equipo *</label>
                  <input name="nombre" value={form.nombre} onChange={handleChange} required />
                </div>
                <div className="form-group">
                  <label>Marca</label>
                  <input name="marca" value={form.marca} onChange={handleChange} />
                </div>
                <div className="form-group">
                  <label>Modelo</label>
                  <input name="modelo" value={form.modelo} onChange={handleChange} />
                </div>
                <div className="form-group">
                  <label>Serie</label>
                  <input name="serie" value={form.serie} onChange={handleChange} />
                </div>
                <div className="form-group">
                  <label>Ubicación</label>
                  <input name="ubicacion" value={form.ubicacion} onChange={handleChange} />
                </div>
                <div className="form-group">
                  <label>Sede</label>
                  <select name="sede_id" value={form.sede_id} onChange={handleChange}>
                    <option value="">Sin sede</option>
                    {catalogos.sedes?.map((s) => <option key={s.id} value={s.id}>{s.nombre}</option>)}
                  </select>
                </div>
                <div className="form-group">
                  <label>Estado</label>
                  <select name="estado" value={form.estado} onChange={handleChange}>
                    {ESTADOS.map((e) => <option key={e} value={e}>{e}</option>)}
                  </select>
                </div>
                <div className="form-group">
                  <label>Criticidad</label>
                  <select name="criticidad" value={form.criticidad} onChange={handleChange}>
                    {CRITICIDADES.map((c) => <option key={c} value={c}>{c}</option>)}
                  </select>
                </div>
              </div>

              <div className="modal-actions-pro">
                <button type="button" className="btn-secondary-pro" onClick={cerrarModal}><X size={16} /> Cancelar</button>
                <button type="submit" className="btn-primary-pro"><Save size={16} /> Guardar</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
