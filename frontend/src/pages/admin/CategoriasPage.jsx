// =========================================================
// PÁGINA ADMIN - CATEGORÍAS
// CRUD completo conectado al backend FastAPI
// Endpoint base: /categorias/
// =========================================================

import { useEffect, useState } from "react";
import AdminLayout from "./AdminLayout";
import API from "../../api/axios";
import { Tags, Plus, Save, Trash2, Pencil, X } from "lucide-react";

export default function CategoriasPage() {
  // =======================================================
  // ESTADOS PRINCIPALES
  // =======================================================
  const [categorias, setCategorias] = useState([]);
  const [editandoId, setEditandoId] = useState(null);
  const [cargando, setCargando] = useState(false);

  // =======================================================
  // FORMULARIO
  // =======================================================
  const [form, setForm] = useState({
    nombre: "",
    descripcion: "",
    activo: true,
  });

  // =======================================================
  // CARGA INICIAL
  // =======================================================
  useEffect(() => {
    cargarCategorias();
  }, []);

  // =======================================================
  // LISTAR CATEGORÍAS
  // =======================================================
  const cargarCategorias = async () => {
    try {
      setCargando(true);
      const res = await API.get("/categorias/");
      setCategorias(res.data);
    } catch (error) {
      console.error(error);
      alert("Error cargando categorías");
    } finally {
      setCargando(false);
    }
  };

  // =======================================================
  // CAMBIOS DEL FORMULARIO
  // =======================================================
  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;

    setForm({
      ...form,
      [name]: type === "checkbox" ? checked : value,
    });
  };

  // =======================================================
  // LIMPIAR FORMULARIO
  // =======================================================
  const limpiarFormulario = () => {
    setForm({
      nombre: "",
      descripcion: "",
      activo: true,
    });

    setEditandoId(null);
  };

  // =======================================================
  // CREAR O ACTUALIZAR CATEGORÍA
  // =======================================================
  const guardarCategoria = async (e) => {
    e.preventDefault();

    if (!form.nombre.trim()) {
      alert("El nombre de la categoría es obligatorio");
      return;
    }

    try {
      if (editandoId) {
        await API.put(`/categorias/${editandoId}`, form);
        alert("Categoría actualizada correctamente");
      } else {
        await API.post("/categorias/", form);
        alert("Categoría creada correctamente");
      }

      limpiarFormulario();
      cargarCategorias();
    } catch (error) {
      console.error(error);
      alert(error.response?.data?.detail || "Error guardando categoría");
    }
  };

  // =======================================================
  // CARGAR DATOS PARA EDITAR
  // =======================================================
  const editarCategoria = (categoria) => {
    setEditandoId(categoria.id);

    setForm({
      nombre: categoria.nombre || "",
      descripcion: categoria.descripcion || "",
      activo: categoria.activo,
    });
  };

  // =======================================================
  // ELIMINAR CATEGORÍA
  // =======================================================
  const eliminarCategoria = async (categoriaId) => {
    const confirmar = confirm(
      "¿Seguro que deseas eliminar esta categoría? Si tiene equipos asociados, la base de datos puede impedir eliminarla."
    );

    if (!confirmar) return;

    try {
      await API.delete(`/categorias/${categoriaId}`);
      alert("Categoría eliminada correctamente");
      cargarCategorias();
    } catch (error) {
      console.error(error);
      alert(error.response?.data?.detail || "Error eliminando categoría");
    }
  };

  return (
    <AdminLayout>
      {/* ===================================================
          ENCABEZADO
          =================================================== */}
      <div className="page-header">
        <div className="page-icon">
          <Tags size={26} />
        </div>

        <div>
          <h1>Categorías</h1>
          <p>Clasifica los equipos por tipo, familia o área técnica.</p>
        </div>
      </div>

      <div className="crud-grid">
        {/* =================================================
            FORMULARIO CATEGORÍA
            ================================================= */}
        <section className="page-card">
          <h2>{editandoId ? "Editar categoría" : "Crear categoría"}</h2>

          <form onSubmit={guardarCategoria} className="crud-form">
            <div className="form-group full">
              <label>Nombre *</label>
              <input
                name="nombre"
                value={form.nombre}
                onChange={handleChange}
                placeholder="Ej: Biomédico, Refrigeración, CCTV"
              />
            </div>

            <div className="form-group full">
              <label>Descripción</label>
              <textarea
                name="descripcion"
                value={form.descripcion}
                onChange={handleChange}
                placeholder="Describe el tipo de equipos que pertenecen a esta categoría"
              />
            </div>

            <label className="checkbox-line">
              <input
                type="checkbox"
                name="activo"
                checked={form.activo}
                onChange={handleChange}
              />
              Categoría activa
            </label>

            <div className="form-actions">
              <button type="button" className="btn-secondary" onClick={limpiarFormulario}>
                <X size={17} />
                Limpiar
              </button>

              <button type="submit" className="btn-primary">
                {editandoId ? <Save size={17} /> : <Plus size={17} />}
                {editandoId ? "Actualizar" : "Crear categoría"}
              </button>
            </div>
          </form>
        </section>

        {/* =================================================
            LISTADO CATEGORÍAS
            ================================================= */}
        <section className="page-card">
          <div className="list-header">
            <div>
              <h2>Categorías registradas</h2>
              <p>{categorias.length} registros encontrados</p>
            </div>

            <button className="btn-secondary" onClick={cargarCategorias}>
              Recargar
            </button>
          </div>

          {cargando ? (
            <p>Cargando categorías...</p>
          ) : (
            <div className="table-wrap">
              <table className="sga-table">
                <thead>
                  <tr>
                    <th>Categoría</th>
                    <th>Descripción</th>
                    <th>Estado</th>
                    <th>Acciones</th>
                  </tr>
                </thead>

                <tbody>
                  {categorias.map((categoria) => (
                    <tr key={categoria.id}>
                      <td>
                        <strong>{categoria.nombre}</strong>
                      </td>

                      <td>{categoria.descripcion || "Sin descripción"}</td>

                      <td>
                        <span className={categoria.activo ? "badge active" : "badge inactive"}>
                          {categoria.activo ? "Activo" : "Inactivo"}
                        </span>
                      </td>

                      <td>
                        <div className="table-actions">
                          <button
                            className="icon-btn"
                            onClick={() => editarCategoria(categoria)}
                            title="Editar"
                          >
                            <Pencil size={16} />
                          </button>

                          <button
                            className="icon-btn danger"
                            onClick={() => eliminarCategoria(categoria.id)}
                            title="Eliminar"
                          >
                            <Trash2 size={16} />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}

                  {categorias.length === 0 && (
                    <tr>
                      <td colSpan="4" style={{ textAlign: "center", padding: 30 }}>
                        No hay categorías registradas.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          )}
        </section>
      </div>
    </AdminLayout>
  );
}