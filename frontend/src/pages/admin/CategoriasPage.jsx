// =========================================================
// CATEGORÍAS PAGE - SGA PRO
// Mantiene diseño en tarjetas como Técnicos / Equipos.
// Incluye:
// - AdminLayout con barra lateral
// - CRUD categorías
// - Búsqueda
// - Paginación
// - Tabla compacta
// =========================================================

import { useEffect, useMemo, useState } from "react";
import AdminLayout from "./AdminLayout";
import API from "../../api/axios";

import {
  Tags,
  Plus,
  Save,
  Trash2,
  Pencil,
  X,
  RefreshCcw,
} from "lucide-react";

import "../../styles/sidebar.css";

export default function CategoriasPage() {
  const [categorias, setCategorias] = useState([]);
  const [editandoId, setEditandoId] = useState(null);
  const [cargando, setCargando] = useState(false);

  const [busqueda, setBusqueda] = useState("");
  const [pagina, setPagina] = useState(1);
  const porPagina = 7;

  const [form, setForm] = useState({
    nombre: "",
    descripcion: "",
    activo: true,
  });

  useEffect(() => {
    cargarCategorias();
  }, []);

  useEffect(() => {
    setPagina(1);
  }, [busqueda]);

  const cargarCategorias = async () => {
    try {
      setCargando(true);
      const res = await API.get("/categorias/");
      setCategorias(Array.isArray(res.data) ? res.data : []);
    } catch (error) {
      console.error(error);
      alert("Error cargando categorías");
    } finally {
      setCargando(false);
    }
  };

  const categoriasFiltradas = useMemo(() => {
    const texto = busqueda.trim().toLowerCase();

    if (!texto) return categorias;

    return categorias.filter((categoria) =>
      [categoria.nombre, categoria.descripcion]
        .filter(Boolean)
        .join(" ")
        .toLowerCase()
        .includes(texto)
    );
  }, [categorias, busqueda]);

  const totalPaginas = Math.ceil(categoriasFiltradas.length / porPagina) || 1;

  const categoriasPaginadas = categoriasFiltradas.slice(
    (pagina - 1) * porPagina,
    pagina * porPagina
  );

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;

    setForm({
      ...form,
      [name]: type === "checkbox" ? checked : value,
    });
  };

  const limpiarFormulario = () => {
    setEditandoId(null);

    setForm({
      nombre: "",
      descripcion: "",
      activo: true,
    });
  };

  const guardarCategoria = async (e) => {
    e.preventDefault();

    if (!form.nombre.trim()) {
      alert("El nombre es obligatorio");
      return;
    }

    try {
      if (editandoId) {
        await API.put(`/categorias/${editandoId}`, form);
        alert("Categoría actualizada");
      } else {
        await API.post("/categorias/", form);
        alert("Categoría creada");
      }

      limpiarFormulario();
      cargarCategorias();
    } catch (error) {
      console.error(error);
      alert(error.response?.data?.detail || "Error guardando categoría");
    }
  };

  const editarCategoria = (categoria) => {
    setEditandoId(categoria.id);

    setForm({
      nombre: categoria.nombre || "",
      descripcion: categoria.descripcion || "",
      activo: categoria.activo ?? true,
    });
  };

  const eliminarCategoria = async (categoriaId) => {
    const confirmar = confirm("¿Seguro que deseas eliminar esta categoría?");
    if (!confirmar) return;

    try {
      await API.delete(`/categorias/${categoriaId}`);
      alert("Categoría eliminada");
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

      {/* ===================================================
          LAYOUT EN TARJETAS PRO
      =================================================== */}
      <div className="equipos-pro-layout categorias-layout-pro">
        {/* =================================================
            FORMULARIO
        ================================================= */}
        <section className="equipos-pro-form-card categorias-form-card">
          <div className="equipos-card-title">
            <h2>{editandoId ? "Editar categoría" : "Crear categoría"}</h2>
            <p>Gestiona tipos y clasificaciones técnicas.</p>
          </div>

          <form onSubmit={guardarCategoria} className="equipos-pro-form">
            <div className="form-group full">
              <label>Nombre *</label>
              <input
                name="nombre"
                value={form.nombre}
                onChange={handleChange}
                placeholder="Ej: Biomédico, CCTV..."
              />
            </div>

            <div className="form-group full">
              <label>Descripción</label>
              <textarea
                name="descripcion"
                value={form.descripcion}
                onChange={handleChange}
                placeholder="Describe esta categoría..."
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
              <button
                type="button"
                className="btn-secondary"
                onClick={limpiarFormulario}
              >
                <X size={16} />
                Limpiar
              </button>

              <button type="submit" className="btn-primary">
                {editandoId ? <Save size={16} /> : <Plus size={16} />}
                {editandoId ? "Actualizar" : "Crear categoría"}
              </button>
            </div>
          </form>
        </section>

        {/* =================================================
            LISTADO
        ================================================= */}
        <section className="equipos-pro-list-card categorias-list-card">
          <div className="equipos-toolbar">
            <div>
              <h2>Categorías registradas</h2>
              <p>{categoriasFiltradas.length} registros encontrados</p>
            </div>

            <button
              className="btn-secondary"
              onClick={cargarCategorias}
              disabled={cargando}
            >
              <RefreshCcw size={16} />
              {cargando ? "Cargando..." : "Recargar"}
            </button>
          </div>

          <input
            className="equipos-search"
            value={busqueda}
            onChange={(e) => setBusqueda(e.target.value)}
            placeholder="Buscar categoría..."
          />

          <div className="table-wrap categorias-table-wrap">
            <table className="sga-table categorias-table">
              <thead>
                <tr>
                  <th>Categoría</th>
                  <th>Descripción</th>
                  <th>Estado</th>
                  <th>Acciones</th>
                </tr>
              </thead>

              <tbody>
                {categoriasPaginadas.map((categoria) => (
                  <tr key={categoria.id}>
                    <td>
                      <strong className="equipo-title">
                        {categoria.nombre}
                      </strong>
                    </td>

                    <td>{categoria.descripcion || "Sin descripción"}</td>

                    <td>
                      <span
                        className={
                          categoria.activo ? "badge active" : "badge inactive"
                        }
                      >
                        {categoria.activo ? "Activo" : "Inactivo"}
                      </span>
                    </td>

                    <td>
                      <div className="table-actions">
                        <button
                          className="icon-btn"
                          onClick={() => editarCategoria(categoria)}
                          title="Editar categoría"
                        >
                          <Pencil size={16} />
                        </button>

                        <button
                          className="icon-btn danger"
                          onClick={() => eliminarCategoria(categoria.id)}
                          title="Eliminar categoría"
                        >
                          <Trash2 size={16} />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}

                {categoriasPaginadas.length === 0 && (
                  <tr>
                    <td colSpan="4" style={{ textAlign: "center", padding: 30 }}>
                      No hay categorías registradas.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>

          {/* =================================================
              PAGINACIÓN
          ================================================= */}
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