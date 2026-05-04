// =========================================================
// PÁGINA ADMIN - EQUIPOS FULL PRO
// CRUD de datos básicos del equipo + acceso a hoja de vida
// =========================================================

import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import AdminLayout from "./AdminLayout";
import API from "../../api/axios";

import {
  MonitorCog,
  Plus,
  Save,
  Trash2,
  Pencil,
  X,
  RefreshCcw,
  FileText,
} from "lucide-react";

import "../../styles/sidebar.css";

export default function EquiposPage() {
  const navigate = useNavigate();

  const [equipos, setEquipos] = useState([]);
  const [empresas, setEmpresas] = useState([]);
  const [sedes, setSedes] = useState([]);
  const [categorias, setCategorias] = useState([]);

  const [editandoId, setEditandoId] = useState(null);
  const [busqueda, setBusqueda] = useState("");
  const [pagina, setPagina] = useState(1);

  const porPagina = 6;

  const [form, setForm] = useState({
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
  });

  useEffect(() => {
    cargarDatos();
  }, []);

  const cargarDatos = async () => {
    try {
      const [resEquipos, resEmpresas, resSedes, resCategorias] =
        await Promise.all([
          API.get("/equipos/"),
          API.get("/empresas/"),
          API.get("/sedes/"),
          API.get("/categorias/"),
        ]);

      setEquipos(resEquipos.data);
      setEmpresas(resEmpresas.data);
      setSedes(resSedes.data);
      setCategorias(resCategorias.data);
    } catch (error) {
      console.error(error);
      alert("Error cargando datos de equipos");
    }
  };

  const sedesFiltradas = useMemo(() => {
    return sedes.filter((sede) => sede.empresa_id === form.empresa_id);
  }, [sedes, form.empresa_id]);

  const nombreEmpresa = (empresaId) => {
    return empresas.find((e) => e.id === empresaId)?.nombre || "N/A";
  };

  const nombreSede = (sedeId) => {
    return sedes.find((s) => s.id === sedeId)?.nombre || "N/A";
  };

  const nombreCategoria = (categoriaId) => {
    return categorias.find((c) => c.id === categoriaId)?.nombre || "Sin categoría";
  };

  const equiposFiltrados = useMemo(() => {
    const texto = busqueda.toLowerCase();

    return equipos.filter((equipo) =>
      equipo.nombre?.toLowerCase().includes(texto) ||
      equipo.marca?.toLowerCase().includes(texto) ||
      equipo.modelo?.toLowerCase().includes(texto) ||
      equipo.serie?.toLowerCase().includes(texto) ||
      equipo.codigo_id?.toLowerCase().includes(texto) ||
      equipo.inventario?.toLowerCase().includes(texto) ||
      equipo.ubicacion?.toLowerCase().includes(texto) ||
      equipo.estado?.toLowerCase().includes(texto) ||
      equipo.criticidad?.toLowerCase().includes(texto)
    );
  }, [equipos, busqueda]);

  const totalPaginas = Math.ceil(equiposFiltrados.length / porPagina) || 1;

  const equiposPaginados = equiposFiltrados.slice(
    (pagina - 1) * porPagina,
    pagina * porPagina
  );

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;

    if (name === "empresa_id") {
      setForm({
        ...form,
        empresa_id: value,
        sede_id: "",
      });
      return;
    }

    setForm({
      ...form,
      [name]: type === "checkbox" ? checked : value,
    });
  };

  const limpiarFormulario = () => {
    setForm({
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
    });

    setEditandoId(null);
  };

  const guardarEquipo = async (e) => {
    e.preventDefault();

    if (!form.empresa_id) {
      alert("Debe seleccionar una empresa");
      return;
    }

    if (!form.sede_id) {
      alert("Debe seleccionar una sede");
      return;
    }

    if (!form.nombre.trim()) {
      alert("El nombre del equipo es obligatorio");
      return;
    }

    try {
      const payload = {
        ...form,
        categoria_id: form.categoria_id || null,
        codigo_id: form.codigo_id || null,
        inventario: form.inventario || null,
      };

      if (editandoId) {
        await API.put(`/equipos/${editandoId}`, payload);
        alert("Equipo actualizado correctamente");
      } else {
        await API.post("/equipos/", payload);
        alert("Equipo creado correctamente");
      }

      limpiarFormulario();
      cargarDatos();
    } catch (error) {
      console.error(error);
      alert(error.response?.data?.detail || "Error guardando equipo");
    }
  };

  const editarEquipo = (equipo) => {
    setEditandoId(equipo.id);

    setForm({
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
      activo: equipo.activo,
    });
  };

  const eliminarEquipo = async (equipoId) => {
    const confirmar = confirm(
      "¿Seguro que deseas eliminar este equipo? Esta acción puede afectar hoja de vida y mantenimientos asociados."
    );

    if (!confirmar) return;

    try {
      await API.delete(`/equipos/${equipoId}`);
      alert("Equipo eliminado correctamente");
      cargarDatos();
    } catch (error) {
      console.error(error);
      alert(error.response?.data?.detail || "Error eliminando equipo");
    }
  };

  const abrirHojaVida = (equipo) => {
    if (!equipo.id) {
      alert("Este equipo no tiene ID válido. Recarga la página.");
      return;
    }

    navigate(`/admin/equipos/${equipo.id}/hoja-vida`);
  };

  return (
    <AdminLayout>
      <div className="page-header">
        <div className="page-icon">
          <MonitorCog size={26} />
        </div>

        <div>
          <h1>Equipos</h1>
          <p>
            Registra los datos básicos del equipo. Luego completa la hoja de vida técnica.
          </p>
        </div>
      </div>

      <div className="equipos-pro-layout">
        <section className="equipos-pro-form-card">
          <div className="equipos-card-title">
            <div>
              <h2>{editandoId ? "Editar equipo" : "Crear equipo básico"}</h2>
              <p>Paso 1: información básica del activo.</p>
            </div>
          </div>

          <form onSubmit={guardarEquipo} className="equipos-pro-form">
            <div className="form-group full">
              <label>Empresa *</label>
              <select name="empresa_id" value={form.empresa_id} onChange={handleChange}>
                <option value="">Seleccionar empresa</option>
                {empresas.map((empresa) => (
                  <option key={empresa.id} value={empresa.id}>
                    {empresa.nombre}
                  </option>
                ))}
              </select>
            </div>

            <div className="form-group full">
              <label>Sede *</label>
              <select
                name="sede_id"
                value={form.sede_id}
                onChange={handleChange}
                disabled={!form.empresa_id}
              >
                <option value="">
                  {form.empresa_id ? "Seleccionar sede" : "Primero selecciona empresa"}
                </option>
                {sedesFiltradas.map((sede) => (
                  <option key={sede.id} value={sede.id}>
                    {sede.nombre}
                  </option>
                ))}
              </select>
            </div>

            <div className="form-group full">
              <label>Categoría</label>
              <select name="categoria_id" value={form.categoria_id} onChange={handleChange}>
                <option value="">Sin categoría</option>
                {categorias.map((categoria) => (
                  <option key={categoria.id} value={categoria.id}>
                    {categoria.nombre}
                  </option>
                ))}
              </select>
            </div>

            <div className="form-group full">
              <label>Nombre del equipo *</label>
              <input
                name="nombre"
                value={form.nombre}
                onChange={handleChange}
                placeholder="Ej: Monitor de signos vitales"
              />
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
              <label>INVIMA</label>
              <input name="invima" value={form.invima} onChange={handleChange} />
            </div>

            <div className="form-group">
              <label>Código ID</label>
              <input name="codigo_id" value={form.codigo_id} onChange={handleChange} />
            </div>

            <div className="form-group">
              <label>Inventario</label>
              <input name="inventario" value={form.inventario} onChange={handleChange} />
            </div>

            <div className="form-group">
              <label>Estado</label>
              <select name="estado" value={form.estado} onChange={handleChange}>
                <option value="OPERATIVO">Operativo</option>
                <option value="EN_MANTENIMIENTO">En mantenimiento</option>
                <option value="FUERA_DE_SERVICIO">Fuera de servicio</option>
                <option value="BAJA">Baja</option>
              </select>
            </div>

            <div className="form-group">
              <label>Criticidad</label>
              <select name="criticidad" value={form.criticidad} onChange={handleChange}>
                <option value="BAJA">Baja</option>
                <option value="MEDIA">Media</option>
                <option value="ALTA">Alta</option>
                <option value="CRITICA">Crítica</option>
              </select>
            </div>

            <label className="checkbox-line">
              <input type="checkbox" name="activo" checked={form.activo} onChange={handleChange} />
              Equipo activo
            </label>

            <div className="form-actions">
              <button type="button" className="btn-secondary" onClick={limpiarFormulario}>
                <X size={17} />
                Limpiar
              </button>

              <button type="submit" className="btn-primary">
                {editandoId ? <Save size={17} /> : <Plus size={17} />}
                {editandoId ? "Actualizar" : "Crear equipo"}
              </button>
            </div>
          </form>
        </section>

        <section className="equipos-pro-list-card">
          <div className="equipos-toolbar">
            <div>
              <h2>Equipos registrados</h2>
              <p>{equiposFiltrados.length} registros encontrados</p>
            </div>

            <button className="btn-secondary" onClick={cargarDatos}>
              <RefreshCcw size={16} />
              Recargar
            </button>
          </div>

          <input
            className="equipos-search"
            value={busqueda}
            onChange={(e) => {
              setBusqueda(e.target.value);
              setPagina(1);
            }}
            placeholder="Buscar por equipo, marca, modelo, serie, código, inventario, ubicación..."
          />

          <div className="table-wrap equipos-table-wrap">
            <table className="sga-table equipos-pro-table">
              <thead>
                <tr>
                  <th>Equipo</th>
                  <th>Empresa / Sede</th>
                  <th>Categoría</th>
                  <th>Estado</th>
                  <th>Criticidad</th>
                  <th>Acciones</th>
                </tr>
              </thead>

              <tbody>
                {equiposPaginados.map((equipo) => (
                  <tr key={equipo.id}>
                    <td>
                      <strong className="equipo-title">{equipo.nombre}</strong>
                      <br />
                      <small className="equipo-sub">
                        {equipo.marca || "Sin marca"} | {equipo.modelo || "Sin modelo"}
                      </small>
                      <br />
                      <small className="equipo-sub">
                        Código: {equipo.codigo_id || "N/A"} | Inventario: {equipo.inventario || "N/A"}
                      </small>
                    </td>

                    <td>
                      <strong>{nombreEmpresa(equipo.empresa_id)}</strong>
                      <br />
                      <small>{nombreSede(equipo.sede_id)}</small>
                    </td>

                    <td>{nombreCategoria(equipo.categoria_id)}</td>

                    <td>
                      <span className="badge role">{equipo.estado}</span>
                    </td>

                    <td>
                      <span
                        className={
                          equipo.criticidad === "ALTA" || equipo.criticidad === "CRITICA"
                            ? "badge inactive"
                            : "badge active"
                        }
                      >
                        {equipo.criticidad}
                      </span>
                    </td>

                    <td>
                      <div className="table-actions">
                        <button
                          className="icon-btn hv-btn"
                          onClick={() => abrirHojaVida(equipo)}
                          title="Hoja de vida técnica"
                        >
                          <FileText size={16} />
                        </button>

                        <button
                          className="icon-btn"
                          onClick={() => editarEquipo(equipo)}
                          title="Editar equipo"
                        >
                          <Pencil size={16} />
                        </button>

                        <button
                          className="icon-btn danger"
                          onClick={() => eliminarEquipo(equipo.id)}
                          title="Eliminar equipo"
                        >
                          <Trash2 size={16} />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}

                {equiposPaginados.length === 0 && (
                  <tr>
                    <td colSpan="6" style={{ textAlign: "center", padding: 30 }}>
                      No hay equipos registrados.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>

          <div className="pagination">
            <button
              className="btn-secondary"
              disabled={pagina === 1}
              onClick={() => setPagina(pagina - 1)}
            >
              Anterior
            </button>

            <span>
              Página {pagina} de {totalPaginas}
            </span>

            <button
              className="btn-secondary"
              disabled={pagina === totalPaginas}
              onClick={() => setPagina(pagina + 1)}
            >
              Siguiente
            </button>
          </div>
        </section>
      </div>
    </AdminLayout>
  );
}