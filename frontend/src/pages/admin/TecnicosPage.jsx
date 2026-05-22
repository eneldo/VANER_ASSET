// ============================================================
// SGA SaaS PRO - TecnicosPage
// Fase 33.3 - Técnicos SaaS PRO
// Módulo responsive para gestión de técnicos de mantenimiento
// ============================================================

import { useEffect, useMemo, useState } from "react";
import {
  BadgeCheck,
  BriefcaseBusiness,
  Edit3,
  Mail,
  Phone,
  Plus,
  RefreshCcw,
  Search,
  Trash2,
  UserCog,
  Users,
  Wrench,
  XCircle,
} from "lucide-react";

import AdminLayout from "./AdminLayout";
import "../../styles/categorias-tecnicos-saas-pro.css";

const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

const initialForm = {
  nombre: "",
  documento: "",
  telefono: "",
  email: "",
  especialidad: "",
  activo: true,
};

function normalizarTecnico(item) {
  return {
    id: item?.id,
    nombre: item?.nombre || item?.name || item?.usuario_nombre || "Sin nombre",
    documento: item?.documento || item?.identificacion || item?.cedula || "",
    telefono: item?.telefono || item?.celular || item?.phone || "",
    email: item?.email || item?.correo || "",
    especialidad: item?.especialidad || item?.cargo || item?.perfil || "Técnico general",
    activo: item?.activo ?? item?.estado ?? true,
  };
}

export default function TecnicosPage() {
  const [tecnicos, setTecnicos] = useState([]);
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

  const cargarTecnicos = async () => {
    setLoading(true);
    setError("");

    try {
      const response = await fetch(`${API_URL}/tecnicos/`, {
        headers: authHeaders,
      });

      if (!response.ok) {
        throw new Error("No fue posible cargar los técnicos.");
      }

      const data = await response.json();
      const lista = Array.isArray(data) ? data : data?.items || data?.data || [];
      setTecnicos(lista.map(normalizarTecnico));
    } catch (err) {
      setError(err.message || "Error cargando técnicos.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    cargarTecnicos();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const filtrados = useMemo(() => {
    const term = busqueda.trim().toLowerCase();
    if (!term) return tecnicos;

    return tecnicos.filter((tec) =>
      [tec.nombre, tec.documento, tec.telefono, tec.email, tec.especialidad, tec.activo ? "activo" : "inactivo"]
        .join(" ")
        .toLowerCase()
        .includes(term)
    );
  }, [tecnicos, busqueda]);

  const totalPages = Math.max(1, Math.ceil(filtrados.length / pageSize));

  const visibles = useMemo(() => {
    const current = Math.min(page, totalPages);
    const start = (current - 1) * pageSize;
    return filtrados.slice(start, start + pageSize);
  }, [filtrados, page, pageSize, totalPages]);

  useEffect(() => {
    setPage(1);
  }, [busqueda, pageSize]);

  const metricas = useMemo(() => {
    const total = tecnicos.length;
    const activos = tecnicos.filter((t) => Boolean(t.activo)).length;
    const inactivos = total - activos;
    const especialidades = new Set(tecnicos.map((t) => t.especialidad).filter(Boolean)).size;

    return { total, activos, inactivos, especialidades };
  }, [tecnicos]);

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

  const guardarTecnico = async (event) => {
    event.preventDefault();
    setError("");

    if (!form.nombre.trim()) {
      setError("El nombre del técnico es obligatorio.");
      return;
    }

    setSaving(true);

    try {
      const method = editId ? "PUT" : "POST";
      const url = editId ? `${API_URL}/tecnicos/${editId}` : `${API_URL}/tecnicos/`;

      const response = await fetch(url, {
        method,
        headers: authHeaders,
        body: JSON.stringify({
          nombre: form.nombre.trim(),
          documento: form.documento.trim(),
          telefono: form.telefono.trim(),
          email: form.email.trim(),
          especialidad: form.especialidad.trim(),
          activo: Boolean(form.activo),
        }),
      });

      if (!response.ok) {
        throw new Error(editId ? "No fue posible actualizar el técnico." : "No fue posible crear el técnico.");
      }

      limpiarFormulario();
      await cargarTecnicos();
    } catch (err) {
      setError(err.message || "Error guardando técnico.");
    } finally {
      setSaving(false);
    }
  };

  const editarTecnico = (tecnico) => {
    setEditId(tecnico.id);
    setForm({
      nombre: tecnico.nombre || "",
      documento: tecnico.documento || "",
      telefono: tecnico.telefono || "",
      email: tecnico.email || "",
      especialidad: tecnico.especialidad || "",
      activo: Boolean(tecnico.activo),
    });
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  const eliminarTecnico = async (tecnico) => {
    const confirmar = window.confirm(`¿Eliminar el técnico "${tecnico.nombre}"?`);
    if (!confirmar) return;

    setError("");

    try {
      const response = await fetch(`${API_URL}/tecnicos/${tecnico.id}`, {
        method: "DELETE",
        headers: authHeaders,
      });

      if (!response.ok) {
        throw new Error("No fue posible eliminar el técnico.");
      }

      await cargarTecnicos();
    } catch (err) {
      setError(err.message || "Error eliminando técnico.");
    }
  };

  return (
    <AdminLayout>
      <section className="ct-page">
        <header className="ct-hero technician">
          <div>
            <span className="ct-eyebrow">Talento técnico</span>
            <h1>Técnicos de mantenimiento</h1>
            <p>
              Administra el equipo técnico disponible para asignaciones, bitácoras,
              evidencias y cumplimiento de mantenimientos.
            </p>
          </div>

          <button className="ct-refresh" type="button" onClick={cargarTecnicos} disabled={loading}>
            <RefreshCcw size={18} />
            Actualizar
          </button>
        </header>

        <div className="ct-kpi-grid">
          <article className="ct-kpi-card">
            <div className="ct-kpi-icon blue"><Users size={22} /></div>
            <span>Total técnicos</span>
            <strong>{metricas.total}</strong>
          </article>

          <article className="ct-kpi-card">
            <div className="ct-kpi-icon green"><BadgeCheck size={22} /></div>
            <span>Activos</span>
            <strong>{metricas.activos}</strong>
          </article>

          <article className="ct-kpi-card">
            <div className="ct-kpi-icon red"><XCircle size={22} /></div>
            <span>Inactivos</span>
            <strong>{metricas.inactivos}</strong>
          </article>

          <article className="ct-kpi-card">
            <div className="ct-kpi-icon cyan"><BriefcaseBusiness size={22} /></div>
            <span>Especialidades</span>
            <strong>{metricas.especialidades}</strong>
          </article>
        </div>

        {error && <div className="ct-alert">{error}</div>}

        <div className="ct-grid">
          <article className="ct-card ct-form-card">
            <div className="ct-card-head">
              <div>
                <h2>{editId ? "Editar técnico" : "Nuevo técnico"}</h2>
                <p>Registra técnicos para asignar mantenimientos.</p>
              </div>
            </div>

            <form className="ct-form" onSubmit={guardarTecnico}>
              <label>
                Nombre completo
                <input name="nombre" value={form.nombre} onChange={handleChange} placeholder="Ej: Carlos Ramírez" />
              </label>

              <label>
                Documento
                <input name="documento" value={form.documento} onChange={handleChange} placeholder="CC / ID" />
              </label>

              <label>
                Teléfono
                <input name="telefono" value={form.telefono} onChange={handleChange} placeholder="Celular" />
              </label>

              <label>
                Correo
                <input name="email" value={form.email} onChange={handleChange} placeholder="correo@empresa.com" />
              </label>

              <label>
                Especialidad
                <input name="especialidad" value={form.especialidad} onChange={handleChange} placeholder="Ej: Aire acondicionado" />
              </label>

              <label>
                Estado
                <select name="activo" value={String(form.activo)} onChange={handleChange}>
                  <option value="true">Activo</option>
                  <option value="false">Inactivo</option>
                </select>
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
                <h2>Listado de técnicos</h2>
                <p>{filtrados.length} registros encontrados</p>
              </div>

              <div className="ct-search-box">
                <Search size={18} />
                <input
                  value={busqueda}
                  onChange={(event) => setBusqueda(event.target.value)}
                  placeholder="Buscar técnico..."
                />
              </div>
            </div>

            <div className="ct-table-wrap">
              <table className="ct-table ct-tech-table">
                <thead>
                  <tr>
                    <th>Técnico</th>
                    <th>Contacto</th>
                    <th>Especialidad</th>
                    <th>Estado</th>
                    <th>Acciones</th>
                  </tr>
                </thead>
                <tbody>
                  {loading ? (
                    <tr><td colSpan="5" className="ct-empty">Cargando técnicos...</td></tr>
                  ) : visibles.length === 0 ? (
                    <tr><td colSpan="5" className="ct-empty">No hay técnicos registrados.</td></tr>
                  ) : (
                    visibles.map((tecnico) => (
                      <tr key={tecnico.id}>
                        <td>
                          <div className="ct-main-cell">
                            <span className="ct-avatar tech"><UserCog size={17} /></span>
                            <div>
                              <strong>{tecnico.nombre}</strong>
                              <small>{tecnico.documento ? `Doc: ${tecnico.documento}` : `ID: ${tecnico.id}`}</small>
                            </div>
                          </div>
                        </td>
                        <td>
                          <div className="ct-contact-list">
                            <span><Phone size={14} /> {tecnico.telefono || "Sin teléfono"}</span>
                            <span><Mail size={14} /> {tecnico.email || "Sin correo"}</span>
                          </div>
                        </td>
                        <td>
                          <span className="ct-specialty"><Wrench size={14} /> {tecnico.especialidad}</span>
                        </td>
                        <td>
                          <span className={tecnico.activo ? "ct-badge success" : "ct-badge danger"}>
                            {tecnico.activo ? "Activo" : "Inactivo"}
                          </span>
                        </td>
                        <td>
                          <div className="ct-actions">
                            <button title="Editar" onClick={() => editarTecnico(tecnico)}>
                              <Edit3 size={16} />
                            </button>
                            <button title="Eliminar" className="danger" onClick={() => eliminarTecnico(tecnico)}>
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
