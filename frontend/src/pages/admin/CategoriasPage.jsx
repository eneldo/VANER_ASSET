// ============================================================
// SGA SaaS PRO - CategoríasPage
// Fase 33.3 - Categorías SaaS PRO
// Módulo responsive, profesional y compatible con backend actual
// ============================================================

import { useEffect, useMemo, useState } from "react";
import {
  Boxes,
  CheckCircle2,
  Edit3,
  Layers3,
  Plus,
  RefreshCcw,
  Search,
  Trash2,
  XCircle,
} from "lucide-react";

import AdminLayout from "./AdminLayout";
import "../../styles/categorias-tecnicos-saas-pro.css";

const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

const ESTADO_OPTIONS = [
  { value: true, label: "Activa" },
  { value: false, label: "Inactiva" },
];

const initialForm = {
  nombre: "",
  descripcion: "",
  activo: true,
};

function normalizarCategoria(item) {
  return {
    id: item?.id,
    nombre: item?.nombre || item?.name || "Sin nombre",
    descripcion: item?.descripcion || item?.description || "Sin descripción",
    activo: item?.activo ?? item?.estado ?? true,
  };
}

export default function CategoriasPage() {
  const [categorias, setCategorias] = useState([]);
  const [form, setForm] = useState(initialForm);
  const [editId, setEditId] = useState(null);
  const [busqueda, setBusqueda] = useState("");
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(8);

  const token = localStorage.getItem("access_token") || localStorage.getItem("token");

  const authHeaders = {
    "Content-Type": "application/json",
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };

  const cargarCategorias = async () => {
    setLoading(true);
    setError("");

    try {
      const response = await fetch(`${API_URL}/categorias/`, {
        headers: authHeaders,
      });

      if (!response.ok) {
        throw new Error("No fue posible cargar las categorías.");
      }

      const data = await response.json();
      const lista = Array.isArray(data) ? data : data?.items || data?.data || [];
      setCategorias(lista.map(normalizarCategoria));
    } catch (err) {
      setError(err.message || "Error cargando categorías.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    cargarCategorias();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const filtradas = useMemo(() => {
    const term = busqueda.trim().toLowerCase();
    if (!term) return categorias;

    return categorias.filter((cat) =>
      [cat.nombre, cat.descripcion, cat.activo ? "activa" : "inactiva"]
        .join(" ")
        .toLowerCase()
        .includes(term)
    );
  }, [categorias, busqueda]);

  const totalPages = Math.max(1, Math.ceil(filtradas.length / pageSize));

  const visibles = useMemo(() => {
    const current = Math.min(page, totalPages);
    const start = (current - 1) * pageSize;
    return filtradas.slice(start, start + pageSize);
  }, [filtradas, page, pageSize, totalPages]);

  useEffect(() => {
    setPage(1);
  }, [busqueda, pageSize]);

  const metricas = useMemo(() => {
    const total = categorias.length;
    const activas = categorias.filter((c) => Boolean(c.activo)).length;
    const inactivas = total - activas;
    const conDescripcion = categorias.filter((c) => c.descripcion && c.descripcion !== "Sin descripción").length;

    return { total, activas, inactivas, conDescripcion };
  }, [categorias]);

  const handleChange = (event) => {
    const { name, value } = event.target;
    setForm((prev) => ({
      ...prev,
      [name]: name === "activo" ? value === "true" : value,
    }));
  };

  const limpiarFormulario = () => {
    setForm(initialForm);
    setEditId(null);
  };

  const guardarCategoria = async (event) => {
    event.preventDefault();
    setError("");

    if (!form.nombre.trim()) {
      setError("El nombre de la categoría es obligatorio.");
      return;
    }

    setSaving(true);

    try {
      const method = editId ? "PUT" : "POST";
      const url = editId ? `${API_URL}/categorias/${editId}` : `${API_URL}/categorias/`;

      const response = await fetch(url, {
        method,
        headers: authHeaders,
        body: JSON.stringify({
          nombre: form.nombre.trim(),
          descripcion: form.descripcion.trim(),
          activo: Boolean(form.activo),
        }),
      });

      if (!response.ok) {
        throw new Error(editId ? "No fue posible actualizar la categoría." : "No fue posible crear la categoría.");
      }

      limpiarFormulario();
      await cargarCategorias();
    } catch (err) {
      setError(err.message || "Error guardando categoría.");
    } finally {
      setSaving(false);
    }
  };

  const editarCategoria = (categoria) => {
    setEditId(categoria.id);
    setForm({
      nombre: categoria.nombre || "",
      descripcion: categoria.descripcion || "",
      activo: Boolean(categoria.activo),
    });
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  const eliminarCategoria = async (categoria) => {
    const confirmar = window.confirm(`¿Eliminar la categoría "${categoria.nombre}"?`);
    if (!confirmar) return;

    setError("");

    try {
      const response = await fetch(`${API_URL}/categorias/${categoria.id}`, {
        method: "DELETE",
        headers: authHeaders,
      });

      if (!response.ok) {
        throw new Error("No fue posible eliminar la categoría.");
      }

      await cargarCategorias();
    } catch (err) {
      setError(err.message || "Error eliminando categoría.");
    }
  };

  return (
    <AdminLayout>
      <section className="ct-page">
        <header className="ct-hero">
          <div>
            <span className="ct-eyebrow">Inventario inteligente</span>
            <h1>Categorías de equipos</h1>
            <p>
              Organiza los activos por familias técnicas: aires acondicionados, CCTV,
              plantas eléctricas, ascensores, bombas, tableros y más.
            </p>
          </div>

          <button className="ct-refresh" type="button" onClick={cargarCategorias} disabled={loading}>
            <RefreshCcw size={18} />
            Actualizar
          </button>
        </header>

        <div className="ct-kpi-grid">
          <article className="ct-kpi-card">
            <div className="ct-kpi-icon blue"><Layers3 size={22} /></div>
            <span>Total categorías</span>
            <strong>{metricas.total}</strong>
          </article>

          <article className="ct-kpi-card">
            <div className="ct-kpi-icon green"><CheckCircle2 size={22} /></div>
            <span>Activas</span>
            <strong>{metricas.activas}</strong>
          </article>

          <article className="ct-kpi-card">
            <div className="ct-kpi-icon red"><XCircle size={22} /></div>
            <span>Inactivas</span>
            <strong>{metricas.inactivas}</strong>
          </article>

          <article className="ct-kpi-card">
            <div className="ct-kpi-icon cyan"><Boxes size={22} /></div>
            <span>Con descripción</span>
            <strong>{metricas.conDescripcion}</strong>
          </article>
        </div>

        {error && <div className="ct-alert">{error}</div>}

        <div className="ct-grid">
          <article className="ct-card ct-form-card">
            <div className="ct-card-head">
              <div>
                <h2>{editId ? "Editar categoría" : "Nueva categoría"}</h2>
                <p>Define una categoría técnica para clasificar equipos.</p>
              </div>
            </div>

            <form className="ct-form" onSubmit={guardarCategoria}>
              <label>
                Nombre de categoría
                <input
                  name="nombre"
                  value={form.nombre}
                  onChange={handleChange}
                  placeholder="Ej: Aires acondicionados"
                />
              </label>

              <label>
                Estado
                <select name="activo" value={String(form.activo)} onChange={handleChange}>
                  {ESTADO_OPTIONS.map((option) => (
                    <option key={String(option.value)} value={String(option.value)}>
                      {option.label}
                    </option>
                  ))}
                </select>
              </label>

              <label className="ct-full">
                Descripción
                <textarea
                  name="descripcion"
                  value={form.descripcion}
                  onChange={handleChange}
                  placeholder="Describe el tipo de equipos, alcance y uso de esta categoría."
                />
              </label>

              <div className="ct-form-actions">
                <button className="ct-btn-primary" disabled={saving} type="submit">
                  <Plus size={18} />
                  {saving ? "Guardando..." : editId ? "Actualizar" : "Crear"}
                </button>

                {editId && (
                  <button className="ct-btn-secondary" type="button" onClick={limpiarFormulario}>
                    Cancelar
                  </button>
                )}
              </div>
            </form>
          </article>

          <article className="ct-card ct-list-card">
            <div className="ct-toolbar">
              <div>
                <h2>Listado de categorías</h2>
                <p>{filtradas.length} registros encontrados</p>
              </div>

              <div className="ct-search-box">
                <Search size={18} />
                <input
                  value={busqueda}
                  onChange={(event) => setBusqueda(event.target.value)}
                  placeholder="Buscar categoría..."
                />
              </div>
            </div>

            <div className="ct-table-wrap">
              <table className="ct-table">
                <thead>
                  <tr>
                    <th>Categoría</th>
                    <th>Descripción</th>
                    <th>Estado</th>
                    <th>Acciones</th>
                  </tr>
                </thead>
                <tbody>
                  {loading ? (
                    <tr><td colSpan="4" className="ct-empty">Cargando categorías...</td></tr>
                  ) : visibles.length === 0 ? (
                    <tr><td colSpan="4" className="ct-empty">No hay categorías registradas.</td></tr>
                  ) : (
                    visibles.map((categoria) => (
                      <tr key={categoria.id}>
                        <td>
                          <div className="ct-main-cell">
                            <span className="ct-avatar"><Layers3 size={17} /></span>
                            <div>
                              <strong>{categoria.nombre}</strong>
                              <small>ID: {categoria.id}</small>
                            </div>
                          </div>
                        </td>
                        <td className="ct-description">{categoria.descripcion}</td>
                        <td>
                          <span className={categoria.activo ? "ct-badge success" : "ct-badge danger"}>
                            {categoria.activo ? "Activa" : "Inactiva"}
                          </span>
                        </td>
                        <td>
                          <div className="ct-actions">
                            <button title="Editar" onClick={() => editarCategoria(categoria)}>
                              <Edit3 size={16} />
                            </button>
                            <button title="Eliminar" className="danger" onClick={() => eliminarCategoria(categoria)}>
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

            <div className="ct-pagination">
              <span>Página {Math.min(page, totalPages)} de {totalPages}</span>
              <div>
                <select value={pageSize} onChange={(event) => setPageSize(Number(event.target.value))}>
                  <option value={6}>6</option>
                  <option value={8}>8</option>
                  <option value={12}>12</option>
                </select>
                <button disabled={page <= 1} onClick={() => setPage((prev) => Math.max(1, prev - 1))}>Anterior</button>
                <button disabled={page >= totalPages} onClick={() => setPage((prev) => Math.min(totalPages, prev + 1))}>Siguiente</button>
              </div>
            </div>
          </article>
        </div>
      </section>
    </AdminLayout>
  );
}
