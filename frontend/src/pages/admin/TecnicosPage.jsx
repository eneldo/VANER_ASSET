// ============================================================
// SGA SaaS PRO - TecnicosPage
// Archivo: frontend/src/pages/admin/TecnicosPage.jsx
//
// Flujo correcto:
// 1. Crear usuario con rol TECNICO en Usuarios.
// 2. Ir a Técnicos.
// 3. Seleccionar usuario técnico.
// 4. Crear perfil técnico.
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
  X,
  XCircle,
  Power,
} from "lucide-react";

import AdminLayout from "./AdminLayout";
import "../../styles/categorias-tecnicos-saas-pro.css";

const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

const initialForm = {
  usuario_id: "",
  documento: "",
  telefono: "",
  especialidad: "",
  cargo: "",
  activo: true,
};

function getToken() {
  return localStorage.getItem("access_token") || localStorage.getItem("token");
}

function normalizarTecnico(item) {
  const usuario = item?.usuario || {};

  return {
    id: item?.id,
    usuario_id: item?.usuario_id,
    documento: item?.documento || "",
    telefono: item?.telefono || "",
    especialidad: item?.especialidad || "Técnico general",
    cargo: item?.cargo || "Técnico de mantenimiento",
    activo: item?.activo ?? true,

    nombre:
      usuario?.nombre_completo ||
      item?.nombre_completo ||
      item?.nombre ||
      "Sin nombre",

    username: usuario?.username || "",
    email: usuario?.email || item?.email || "",
  };
}

export default function TecnicosPage() {
  const [tecnicos, setTecnicos] = useState([]);
  const [usuariosTecnicos, setUsuariosTecnicos] = useState([]);

  const [form, setForm] = useState(initialForm);
  const [editId, setEditId] = useState(null);

  const [busqueda, setBusqueda] = useState("");
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);

  const [mensaje, setMensaje] = useState("");
  const [error, setError] = useState("");

  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(8);

  const authHeaders = {
    "Content-Type": "application/json",
    ...(getToken() ? { Authorization: `Bearer ${getToken()}` } : {}),
  };

  const cargarTecnicos = async () => {
    const response = await fetch(`${API_URL}/tecnicos/`, {
      headers: authHeaders,
    });

    if (!response.ok) {
      throw new Error("No fue posible cargar los técnicos.");
    }

    const data = await response.json();
    const lista = Array.isArray(data) ? data : data?.items || data?.data || [];

    setTecnicos(lista.map(normalizarTecnico));
    return lista;
  };

  const cargarUsuariosTecnicos = async (tecnicosActuales = []) => {
    const [usuariosRes, tecnicosRes] = await Promise.all([
      fetch(`${API_URL}/usuarios/`, { headers: authHeaders }),
      tecnicosActuales.length
        ? Promise.resolve({
            ok: true,
            json: async () => tecnicosActuales,
          })
        : fetch(`${API_URL}/tecnicos/`, { headers: authHeaders }),
    ]);

    if (!usuariosRes.ok) {
      throw new Error("No fue posible cargar usuarios técnicos.");
    }

    if (!tecnicosRes.ok) {
      throw new Error("No fue posible validar perfiles técnicos existentes.");
    }

    const usuariosData = await usuariosRes.json();
    const tecnicosData = await tecnicosRes.json();

    const usuarios = Array.isArray(usuariosData)
      ? usuariosData
      : usuariosData?.items || usuariosData?.data || [];

    const tecnicosLista = Array.isArray(tecnicosData)
      ? tecnicosData
      : tecnicosData?.items || tecnicosData?.data || [];

    const usuariosConPerfil = tecnicosLista.map((t) => String(t.usuario_id));

    const disponibles = usuarios.filter((usuario) => {
      return (
        usuario.rol === "TECNICO" &&
        usuario.activo === true &&
        !usuariosConPerfil.includes(String(usuario.id))
      );
    });

    setUsuariosTecnicos(disponibles);
  };

  const cargarTodo = async () => {
    try {
      setLoading(true);
      setError("");
      setMensaje("");

      const tecnicosActuales = await cargarTecnicos();
      await cargarUsuariosTecnicos(tecnicosActuales);
    } catch (err) {
      console.error(err);
      setError(err.message || "Error cargando información.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const timer = window.setTimeout(() => cargarTodo(), 0);
    return () => window.clearTimeout(timer);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const filtrados = useMemo(() => {
    const term = busqueda.trim().toLowerCase();

    if (!term) return tecnicos;

    return tecnicos.filter((tec) =>
      [
        tec.nombre,
        tec.username,
        tec.documento,
        tec.telefono,
        tec.email,
        tec.especialidad,
        tec.cargo,
        tec.activo ? "activo" : "inactivo",
      ]
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
    const timer = window.setTimeout(() => setPage(1), 0);
    return () => window.clearTimeout(timer);
  }, [busqueda, pageSize]);

  const metricas = useMemo(() => {
    const total = tecnicos.length;
    const activos = tecnicos.filter((t) => Boolean(t.activo)).length;
    const inactivos = total - activos;
    const especialidades = new Set(
      tecnicos.map((t) => t.especialidad).filter(Boolean)
    ).size;

    return { total, activos, inactivos, especialidades };
  }, [tecnicos]);

  const usuarioSeleccionado = useMemo(() => {
    return usuariosTecnicos.find(
      (usuario) => String(usuario.id) === String(form.usuario_id)
    );
  }, [usuariosTecnicos, form.usuario_id]);

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
    setMensaje("");
    setError("");
  };

  const validarFormulario = () => {
    if (!editId && !form.usuario_id) {
      setError("Debes seleccionar un usuario con rol TECNICO.");
      return false;
    }

    if (!form.documento.trim()) {
      setError("El documento del técnico es obligatorio.");
      return false;
    }

    if (!form.especialidad.trim()) {
      setError("La especialidad del técnico es obligatoria.");
      return false;
    }

    return true;
  };

  const guardarTecnico = async (event) => {
    event.preventDefault();

    if (saving) return;
    if (!validarFormulario()) return;

    try {
      setSaving(true);
      setError("");
      setMensaje("");

      const payload = {
        documento: form.documento.trim(),
        telefono: form.telefono.trim(),
        especialidad: form.especialidad.trim(),
        cargo: form.cargo.trim() || "Técnico de mantenimiento",
        activo: Boolean(form.activo),
      };

      const method = editId ? "PUT" : "POST";
      const url = editId
        ? `${API_URL}/tecnicos/${editId}`
        : `${API_URL}/tecnicos/`;

      const body = editId
        ? payload
        : {
            ...payload,
            usuario_id: form.usuario_id,
          };

      const response = await fetch(url, {
        method,
        headers: authHeaders,
        body: JSON.stringify(body),
      });

      if (!response.ok) {
        const data = await response.json().catch(() => null);
        throw new Error(
          data?.detail ||
            (editId
              ? "No fue posible actualizar el técnico."
              : "No fue posible crear el técnico.")
        );
      }

      setMensaje(
        editId
          ? "Técnico actualizado correctamente."
          : "Perfil técnico creado correctamente."
      );

      limpiarFormulario();
      await cargarTodo();
    } catch (err) {
      console.error(err);
      setError(err.message || "Error guardando técnico.");
    } finally {
      setSaving(false);
    }
  };

  const editarTecnico = (tecnico) => {
    setEditId(tecnico.id);

    setForm({
      usuario_id: tecnico.usuario_id || "",
      documento: tecnico.documento || "",
      telefono: tecnico.telefono || "",
      especialidad: tecnico.especialidad || "",
      cargo: tecnico.cargo || "",
      activo: Boolean(tecnico.activo),
    });

    setMensaje("Modo edición activo.");
    setError("");

    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  const cambiarEstadoTecnico = async (tecnico) => {
    try {
      setSaving(true);
      setError("");
      setMensaje("");

      const response = await fetch(`${API_URL}/tecnicos/${tecnico.id}/estado`, {
        method: "PATCH",
        headers: authHeaders,
      });

      if (!response.ok) {
        const data = await response.json().catch(() => null);
        throw new Error(data?.detail || "No fue posible cambiar el estado.");
      }

      setMensaje("Estado del técnico actualizado correctamente.");
      await cargarTodo();
    } catch (err) {
      console.error(err);
      setError(err.message || "Error cambiando estado.");
    } finally {
      setSaving(false);
    }
  };

  const eliminarTecnico = async (tecnico) => {
    const confirmar = window.confirm(
      `¿Eliminar el perfil técnico de "${tecnico.nombre}"?\n\nNo se elimina el usuario, solo el perfil técnico.`
    );

    if (!confirmar) return;

    try {
      setSaving(true);
      setError("");
      setMensaje("");

      const response = await fetch(`${API_URL}/tecnicos/${tecnico.id}`, {
        method: "DELETE",
        headers: authHeaders,
      });

      if (!response.ok) {
        const data = await response.json().catch(() => null);
        throw new Error(data?.detail || "No fue posible eliminar el técnico.");
      }

      setMensaje("Perfil técnico eliminado correctamente.");
      await cargarTodo();
    } catch (err) {
      console.error(err);
      setError(err.message || "Error eliminando técnico.");
    } finally {
      setSaving(false);
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
              Administra perfiles técnicos vinculados a usuarios con rol TECNICO.
            </p>
          </div>

          <button
            className="ct-refresh"
            type="button"
            onClick={cargarTodo}
            disabled={loading || saving}
          >
            <RefreshCcw size={18} />
            Recargar
          </button>
        </header>

        <div className="ct-kpi-grid">
          <article className="ct-kpi-card">
            <div className="ct-kpi-icon blue">
              <Users size={22} />
            </div>
            <span>Total técnicos</span>
            <strong>{metricas.total}</strong>
          </article>

          <article className="ct-kpi-card">
            <div className="ct-kpi-icon green">
              <BadgeCheck size={22} />
            </div>
            <span>Activos</span>
            <strong>{metricas.activos}</strong>
          </article>

          <article className="ct-kpi-card">
            <div className="ct-kpi-icon red">
              <XCircle size={22} />
            </div>
            <span>Inactivos</span>
            <strong>{metricas.inactivos}</strong>
          </article>

          <article className="ct-kpi-card">
            <div className="ct-kpi-icon cyan">
              <BriefcaseBusiness size={22} />
            </div>
            <span>Especialidades</span>
            <strong>{metricas.especialidades}</strong>
          </article>
        </div>

        {mensaje && <div className="ct-alert success">{mensaje}</div>}
        {error && <div className="ct-alert">{error}</div>}

        <div className="ct-grid">
          <article className="ct-card ct-form-card">
            <div className="ct-card-head">
              <div>
                <h2>{editId ? "Editar perfil técnico" : "Crear perfil técnico"}</h2>
                <p>
                  Primero crea el usuario en Usuarios con rol TECNICO. Luego
                  selecciónalo aquí.
                </p>
              </div>
            </div>

            <form className="ct-form" onSubmit={guardarTecnico}>
              <label>
                Usuario técnico *
                <select
                  name="usuario_id"
                  value={form.usuario_id}
                  onChange={handleChange}
                  disabled={Boolean(editId) || saving}
                >
                  <option value="">
                    {editId
                      ? "Usuario ya vinculado"
                      : "Seleccionar usuario técnico"}
                  </option>

                  {usuariosTecnicos.map((usuario) => (
                    <option key={usuario.id} value={usuario.id}>
                      {usuario.nombre_completo} - {usuario.username} -{" "}
                      {usuario.email}
                    </option>
                  ))}
                </select>
              </label>

              {usuarioSeleccionado && !editId && (
                <div
                  style={{
                    gridColumn: "1 / -1",
                    padding: "12px 14px",
                    borderRadius: 16,
                    background: "#eff6ff",
                    border: "1px solid #bfdbfe",
                    color: "#1e3a8a",
                    fontWeight: 800,
                  }}
                >
                  Usuario seleccionado: {usuarioSeleccionado.nombre_completo} ·{" "}
                  {usuarioSeleccionado.email}
                </div>
              )}

              <label>
                Documento *
                <input
                  name="documento"
                  value={form.documento}
                  onChange={handleChange}
                  placeholder="CC / ID"
                  disabled={saving}
                />
              </label>

              <label>
                Teléfono
                <input
                  name="telefono"
                  value={form.telefono}
                  onChange={handleChange}
                  placeholder="Celular"
                  disabled={saving}
                />
              </label>

              <label>
                Especialidad *
                <input
                  name="especialidad"
                  value={form.especialidad}
                  onChange={handleChange}
                  placeholder="Ej: Aire acondicionado"
                  disabled={saving}
                />
              </label>

              <label>
                Cargo
                <input
                  name="cargo"
                  value={form.cargo}
                  onChange={handleChange}
                  placeholder="Ej: Técnico de mantenimiento"
                  disabled={saving}
                />
              </label>

              <label>
                Estado
                <select
                  name="activo"
                  value={String(form.activo)}
                  onChange={handleChange}
                  disabled={saving}
                >
                  <option value="true">Activo</option>
                  <option value="false">Inactivo</option>
                </select>
              </label>

              <div className="ct-form-actions">
                <button
                  className="ct-btn-secondary"
                  type="button"
                  onClick={limpiarFormulario}
                  disabled={saving}
                >
                  <X size={18} />
                  Limpiar
                </button>

                <button className="ct-btn-primary" disabled={saving} type="submit">
                  <Plus size={18} />
                  {saving
                    ? "Guardando..."
                    : editId
                    ? "Actualizar"
                    : "Crear técnico"}
                </button>
              </div>
            </form>
          </article>

          <article className="ct-card ct-list-card">
            <div className="ct-toolbar">
              <div>
                <h2>Técnicos registrados</h2>
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
                    <th>Documento</th>
                    <th>Especialidad</th>
                    <th>Cargo</th>
                    <th>Estado</th>
                    <th>Acciones</th>
                  </tr>
                </thead>

                <tbody>
                  {loading ? (
                    <tr>
                      <td colSpan="7" className="ct-empty">
                        Cargando técnicos...
                      </td>
                    </tr>
                  ) : visibles.length === 0 ? (
                    <tr>
                      <td colSpan="7" className="ct-empty">
                        No hay técnicos registrados.
                      </td>
                    </tr>
                  ) : (
                    visibles.map((tecnico) => (
                      <tr key={tecnico.id}>
                        <td>
                          <div className="ct-main-cell">
                            <span className="ct-avatar tech">
                              <UserCog size={17} />
                            </span>

                            <div>
                              <strong>{tecnico.nombre}</strong>
                              <small>{tecnico.username || "Sin username"}</small>
                            </div>
                          </div>
                        </td>

                        <td>
                          <div className="ct-contact-list">
                            <span>
                              <Phone size={14} />{" "}
                              {tecnico.telefono || "Sin teléfono"}
                            </span>

                            <span>
                              <Mail size={14} /> {tecnico.email || "Sin correo"}
                            </span>
                          </div>
                        </td>

                        <td>{tecnico.documento || "N/A"}</td>

                        <td>
                          <span className="ct-specialty">
                            <Wrench size={14} /> {tecnico.especialidad}
                          </span>
                        </td>

                        <td>{tecnico.cargo || "N/A"}</td>

                        <td>
                          <span
                            className={
                              tecnico.activo
                                ? "ct-badge success"
                                : "ct-badge danger"
                            }
                          >
                            {tecnico.activo ? "Activo" : "Inactivo"}
                          </span>
                        </td>

                        <td>
                          <div className="ct-actions">
                            <button
                              title="Editar"
                              onClick={() => editarTecnico(tecnico)}
                              disabled={saving}
                            >
                              <Edit3 size={16} />
                            </button>

                            <button
                              title="Activar / Inactivar"
                              onClick={() => cambiarEstadoTecnico(tecnico)}
                              disabled={saving}
                            >
                              <Power size={16} />
                            </button>

                            <button
                              title="Eliminar perfil técnico"
                              className="danger"
                              onClick={() => eliminarTecnico(tecnico)}
                              disabled={saving}
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

            <div className="ct-pagination">
              <span>
                Página {Math.min(page, totalPages)} de {totalPages}
              </span>

              <div>
                <select
                  value={pageSize}
                  onChange={(event) => setPageSize(Number(event.target.value))}
                >
                  <option value={6}>6</option>
                  <option value={8}>8</option>
                  <option value={12}>12</option>
                </select>

                <button
                  disabled={page <= 1}
                  onClick={() => setPage((prev) => Math.max(1, prev - 1))}
                >
                  Anterior
                </button>

                <button
                  disabled={page >= totalPages}
                  onClick={() =>
                    setPage((prev) => Math.min(totalPages, prev + 1))
                  }
                >
                  Siguiente
                </button>
              </div>
            </div>
          </article>
        </div>
      </section>
    </AdminLayout>
  );
}
