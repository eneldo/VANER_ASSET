// =========================================================
// PÁGINA ADMIN - USUARIOS Y PERMISOS PRO
// Crear, listar, buscar, paginar, editar, eliminar/inactivar,
// activar/inactivar, cambiar contraseña y asignar permisos.
// =========================================================

import { useEffect, useMemo, useState } from "react";
import AdminLayout from "./AdminLayout";
import API from "../../api/axios";
import {
  Users,
  Plus,
  Save,
  Trash2,
  Pencil,
  X,
  Eye,
  KeyRound,
  Power,
  Shield,
  CheckSquare,
} from "lucide-react";

export default function UsuariosPage() {
  const [usuarios, setUsuarios] = useState([]);
  const [empresas, setEmpresas] = useState([]);
  const [editandoId, setEditandoId] = useState(null);
  const [detalle, setDetalle] = useState(null);
  const [busqueda, setBusqueda] = useState("");

  const [permisos, setPermisos] = useState([]);
  const [permisosUsuario, setPermisosUsuario] = useState([]);
  const [usuarioPermisos, setUsuarioPermisos] = useState(null);

  const [usuarioPassword, setUsuarioPassword] = useState(null);
  const [nuevaPassword, setNuevaPassword] = useState("");
  const [confirmarPassword, setConfirmarPassword] = useState("");

  const [pagina, setPagina] = useState(1);
  const porPagina = 6;

  const [form, setForm] = useState({
    nombre_completo: "",
    username: "",
    email: "",
    password: "",
    rol: "TECNICO",
    empresa_id: "",
    activo: true,
  });

  useEffect(() => {
    cargarDatos();
  }, []);

  const cargarDatos = async () => {
    try {
      const [resUsuarios, resEmpresas, resPermisos] = await Promise.all([
        API.get("/usuarios/"),
        API.get("/empresas/"),
        API.get("/permisos/catalogo"),
      ]);

      setUsuarios(resUsuarios.data || []);
      setEmpresas(resEmpresas.data || []);
      setPermisos(resPermisos.data || []);
    } catch (error) {
      console.error(error);
      alert("Error cargando usuarios o permisos");
    }
  };

  const usuariosFiltrados = useMemo(() => {
    const texto = busqueda.toLowerCase();

    return usuarios.filter(
      (u) =>
        u.nombre_completo?.toLowerCase().includes(texto) ||
        u.username?.toLowerCase().includes(texto) ||
        u.email?.toLowerCase().includes(texto) ||
        u.rol?.toLowerCase().includes(texto)
    );
  }, [usuarios, busqueda]);

  const totalPaginas = Math.ceil(usuariosFiltrados.length / porPagina) || 1;

  const usuariosPaginados = usuariosFiltrados.slice(
    (pagina - 1) * porPagina,
    pagina * porPagina
  );

  const permisosAgrupados = useMemo(() => {
    const grupos = {};

    permisos.forEach((permiso) => {
      const modulo = permiso.modulo || "GENERAL";
      if (!grupos[modulo]) grupos[modulo] = [];
      grupos[modulo].push(permiso);
    });

    return grupos;
  }, [permisos]);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;

    setForm({
      ...form,
      [name]: type === "checkbox" ? checked : value,
    });
  };

  const limpiarFormulario = () => {
    setForm({
      nombre_completo: "",
      username: "",
      email: "",
      password: "",
      rol: "TECNICO",
      empresa_id: "",
      activo: true,
    });

    setEditandoId(null);
  };

  const guardarUsuario = async (e) => {
    e.preventDefault();

    if (!form.nombre_completo || !form.username || !form.email) {
      alert("Nombre, usuario y correo son obligatorios");
      return;
    }

    if (!editandoId && !form.password) {
      alert("La contraseña es obligatoria al crear usuario");
      return;
    }

    if (form.rol === "EMPRESA" && !form.empresa_id) {
      alert("Los usuarios EMPRESA deben tener empresa asociada");
      return;
    }

    try {
      const payload = {
        nombre_completo: form.nombre_completo,
        username: form.username,
        email: form.email,
        rol: form.rol,
        empresa_id: form.empresa_id || null,
        activo: form.activo,
      };

      if (editandoId) {
        await API.put(`/usuarios/${editandoId}`, payload);
        alert("Usuario actualizado correctamente");
      } else {
        await API.post("/usuarios/", {
          ...payload,
          password: form.password,
        });
        alert("Usuario creado correctamente");
      }

      limpiarFormulario();
      cargarDatos();
    } catch (error) {
      console.error(error);
      alert(error.response?.data?.detail || "Error guardando usuario");
    }
  };

  const editarUsuario = (usuario) => {
    setEditandoId(usuario.id);

    setForm({
      nombre_completo: usuario.nombre_completo || "",
      username: usuario.username || "",
      email: usuario.email || "",
      password: "",
      rol: usuario.rol || "TECNICO",
      empresa_id: usuario.empresa_id || "",
      activo: usuario.activo,
    });
  };

  const verDetalle = (usuario) => {
    setDetalle(usuario);
  };

  const cambiarEstado = async (usuarioId) => {
    try {
      await API.patch(`/usuarios/${usuarioId}/estado`);
      await cargarDatos();
    } catch (error) {
      console.error(error);
      alert("Error cambiando estado");
    }
  };

  // =======================================================
  // CAMBIAR CONTRASEÑA CON MODAL PRO
  // =======================================================
  const abrirModalPassword = (usuario) => {
    setUsuarioPassword(usuario);
    setNuevaPassword("");
    setConfirmarPassword("");
  };

  const cerrarModalPassword = () => {
    setUsuarioPassword(null);
    setNuevaPassword("");
    setConfirmarPassword("");
  };

  const guardarPassword = async () => {
    if (!usuarioPassword) return;

    if (!nuevaPassword || nuevaPassword.length < 6) {
      alert("La contraseña debe tener mínimo 6 caracteres");
      return;
    }

    if (nuevaPassword !== confirmarPassword) {
      alert("Las contraseñas no coinciden");
      return;
    }

    try {
      await API.patch(`/usuarios/${usuarioPassword.id}/reset-password`, {
        nueva_password: nuevaPassword,
      });

      alert(`Contraseña actualizada para ${usuarioPassword.nombre_completo}`);
      cerrarModalPassword();
    } catch (error) {
      console.error(error);
      alert(error.response?.data?.detail || "Error cambiando contraseña");
    }
  };

  // =======================================================
  // ELIMINAR / INACTIVAR USUARIO PRO
  // =======================================================
  const eliminarUsuario = async (usuario) => {
    if (!usuario?.id) {
      alert("No se encontró el ID del usuario.");
      return;
    }

    const confirmar = window.confirm(
      `¿Deseas eliminar/inactivar el usuario "${usuario.nombre_completo}"?\n\nEl usuario quedará inactivo para proteger el historial del sistema.`
    );

    if (!confirmar) return;

    try {
      await API.delete(`/usuarios/${usuario.id}`);

      alert("Usuario eliminado/inactivado correctamente");

      const nuevaCantidad = usuariosFiltrados.length - 1;
      const nuevaTotalPaginas = Math.ceil(nuevaCantidad / porPagina) || 1;

      if (pagina > nuevaTotalPaginas) {
        setPagina(nuevaTotalPaginas);
      }

      await cargarDatos();
    } catch (error) {
      console.error("Error eliminando/inactivando usuario:", error);

      alert(
        error?.response?.data?.detail ||
          "No fue posible eliminar/inactivar el usuario"
      );
    }
  };

  const cargarPermisosUsuario = async (usuario) => {
    try {
      setUsuarioPermisos(usuario);

      const res = await API.get(`/permisos/usuario/${usuario.id}`);

      setPermisosUsuario(res.data?.permisos_directos || res.data?.permisos_finales || []);
    } catch (error) {
      console.error(error);
      alert("Error cargando permisos del usuario");
    }
  };

  const togglePermiso = (codigo) => {
    setPermisosUsuario((prev) => {
      if (prev.includes(codigo)) {
        return prev.filter((p) => p !== codigo);
      }

      return [...prev, codigo];
    });
  };

  const guardarPermisos = async () => {
    if (!usuarioPermisos) {
      alert("Selecciona un usuario para asignar permisos");
      return;
    }

    try {
      // El backend PRO 31.2 guarda permisos directos por UUID.
      // En la UI manejamos códigos legibles; aquí convertimos código -> id.
      const permisoIds = permisos
        .filter((permiso) => permisosUsuario.includes(permiso.codigo))
        .map((permiso) => permiso.id);

      await API.put(`/permisos/usuario/${usuarioPermisos.id}/directos`, {
        permiso_ids: permisoIds,
      });

      alert("Permisos guardados correctamente");
    } catch (error) {
      console.error(error);
      alert(error.response?.data?.detail || "Error guardando permisos");
    }
  };

  const cerrarPanelPermisos = () => {
    setUsuarioPermisos(null);
    setPermisosUsuario([]);
  };

  const nombreEmpresa = (empresaId) => {
    const emp = empresas.find((e) => e.id === empresaId);
    return emp ? emp.nombre : "N/A";
  };

  return (
    <AdminLayout>
      <div className="page-header">
        <div className="page-icon">
          <Users size={26} />
        </div>

        <div>
          <h1>Usuarios y Permisos</h1>
          <p>Crea, administra y controla los accesos del sistema.</p>
        </div>
      </div>

      <div className="crud-grid">
        <section className="page-card">
          <h2>{editandoId ? "Editar usuario" : "Crear usuario"}</h2>

          <form onSubmit={guardarUsuario} className="crud-form">
            <div className="form-group full">
              <label>Nombre completo *</label>
              <input
                name="nombre_completo"
                value={form.nombre_completo}
                onChange={handleChange}
                placeholder="Ej: Juan Pérez"
              />
            </div>

            <div className="form-group">
              <label>Usuario *</label>
              <input
                name="username"
                value={form.username}
                onChange={handleChange}
                placeholder="juanperez"
              />
            </div>

            <div className="form-group">
              <label>Correo *</label>
              <input
                name="email"
                type="email"
                value={form.email}
                onChange={handleChange}
                placeholder="correo@sga.com"
              />
            </div>

            {!editandoId && (
              <div className="form-group">
                <label>Contraseña *</label>
                <input
                  name="password"
                  type="password"
                  value={form.password}
                  onChange={handleChange}
                  placeholder="123456"
                />
              </div>
            )}

            <div className="form-group">
              <label>Rol *</label>
              <select name="rol" value={form.rol} onChange={handleChange}>
                <option value="ADMIN">Administrador</option>
                <option value="COORDINADOR">Coordinador</option>
                <option value="EMPRESA">Empresa / Cliente</option>
                <option value="TECNICO">Técnico</option>
              </select>
            </div>

            {form.rol === "EMPRESA" && (
              <div className="form-group full">
                <label>Empresa asociada *</label>
                <select
                  name="empresa_id"
                  value={form.empresa_id}
                  onChange={handleChange}
                >
                  <option value="">Seleccionar empresa</option>
                  {empresas.map((empresa) => (
                    <option key={empresa.id} value={empresa.id}>
                      {empresa.nombre}
                    </option>
                  ))}
                </select>
              </div>
            )}

            <label className="checkbox-line">
              <input
                type="checkbox"
                name="activo"
                checked={form.activo}
                onChange={handleChange}
              />
              Usuario activo
            </label>

            <div className="form-actions">
              <button
                type="button"
                className="btn-secondary"
                onClick={limpiarFormulario}
              >
                <X size={17} />
                Limpiar
              </button>

              <button type="submit" className="btn-primary">
                {editandoId ? <Save size={17} /> : <Plus size={17} />}
                {editandoId ? "Actualizar" : "Crear usuario"}
              </button>
            </div>
          </form>
        </section>

        <section className="page-card">
          <div className="list-header">
            <div>
              <h2>Usuarios registrados</h2>
              <p>{usuariosFiltrados.length} registros encontrados</p>
            </div>

            <button className="btn-secondary" onClick={cargarDatos}>
              Recargar
            </button>
          </div>

          <div className="form-group full" style={{ marginBottom: 16 }}>
            <input
              value={busqueda}
              onChange={(e) => {
                setBusqueda(e.target.value);
                setPagina(1);
              }}
              placeholder="Buscar usuario, correo o rol..."
            />
          </div>

          <div className="table-wrap">
            <table className="sga-table">
              <thead>
                <tr>
                  <th>Usuario</th>
                  <th>Correo</th>
                  <th>Rol</th>
                  <th>Empresa</th>
                  <th>Estado</th>
                  <th>Acciones</th>
                </tr>
              </thead>

              <tbody>
                {usuariosPaginados.map((usuario) => (
                  <tr key={usuario.id}>
                    <td>
                      <strong>{usuario.nombre_completo}</strong>
                      <br />
                      <small>{usuario.username}</small>
                    </td>

                    <td>{usuario.email}</td>

                    <td>
                      <span className="badge role">{usuario.rol}</span>
                    </td>

                    <td>
                      {usuario.empresa_id
                        ? nombreEmpresa(usuario.empresa_id)
                        : "N/A"}
                    </td>

                    <td>
                      <span
                        className={
                          usuario.activo ? "badge active" : "badge inactive"
                        }
                      >
                        {usuario.activo ? "Activo" : "Inactivo"}
                      </span>
                    </td>

                    <td>
                      <div className="table-actions">
                        <button
                          className="icon-btn"
                          onClick={() => verDetalle(usuario)}
                          title="Detalle"
                        >
                          <Eye size={16} />
                        </button>

                        <button
                          className="icon-btn"
                          onClick={() => editarUsuario(usuario)}
                          title="Editar"
                        >
                          <Pencil size={16} />
                        </button>

                        <button
                          className="icon-btn"
                          onClick={() => cargarPermisosUsuario(usuario)}
                          title="Permisos"
                        >
                          <Shield size={16} />
                        </button>

                        <button
                          className="icon-btn"
                          onClick={() => abrirModalPassword(usuario)}
                          title="Cambiar contraseña"
                        >
                          <KeyRound size={16} />
                        </button>

                        <button
                          className="icon-btn"
                          onClick={() => cambiarEstado(usuario.id)}
                          title="Activar/Inactivar"
                        >
                          <Power size={16} />
                        </button>

                        <button
                          className="icon-btn danger"
                          onClick={() => eliminarUsuario(usuario)}
                          title="Eliminar/Inactivar"
                        >
                          <Trash2 size={16} />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}

                {usuariosPaginados.length === 0 && (
                  <tr>
                    <td colSpan="6" style={{ textAlign: "center", padding: 30 }}>
                      No hay usuarios registrados.
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

      {usuarioPermisos && (
        <section className="page-card" style={{ marginTop: 22 }}>
          <div className="list-header">
            <div>
              <h2 style={{ display: "flex", alignItems: "center", gap: 8 }}>
                <Shield size={22} />
                Permisos del usuario
              </h2>
              <p>
                Usuario: <strong>{usuarioPermisos.nombre_completo}</strong> · Rol:{" "}
                <strong>{usuarioPermisos.rol}</strong>
              </p>
            </div>

            <div style={{ display: "flex", gap: 10 }}>
              <button className="btn-secondary" onClick={cerrarPanelPermisos}>
                <X size={17} />
                Cerrar
              </button>

              <button className="btn-primary" onClick={guardarPermisos}>
                <Save size={17} />
                Guardar permisos
              </button>
            </div>
          </div>

          <div style={styles.permisosContainer}>
            {Object.entries(permisosAgrupados).map(([modulo, items]) => (
              <div key={modulo} style={styles.permisoGrupo}>
                <h3 style={styles.permisoModulo}>{modulo}</h3>

                <div style={styles.permisosGrid}>
                  {items.map((permiso) => (
                    <label key={permiso.codigo} style={styles.permisoItem}>
                      <input
                        type="checkbox"
                        checked={permisosUsuario.includes(permiso.codigo)}
                        onChange={() => togglePermiso(permiso.codigo)}
                        style={{ marginTop: 5 }}
                      />

                      <div>
                        <strong style={styles.permisoNombre}>
                          <CheckSquare size={15} />
                          {permiso.nombre}
                        </strong>

                        <code style={styles.permisoCodigo}>
                          {permiso.codigo}
                        </code>

                        <p style={styles.permisoDescripcion}>
                          {permiso.descripcion || "Sin descripción"}
                        </p>
                      </div>
                    </label>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </section>
      )}

      {detalle && (
        <div className="modal-backdrop">
          <div className="modal-card">
            <h2>Detalle del usuario</h2>

            <p>
              <strong>Nombre:</strong> {detalle.nombre_completo}
            </p>
            <p>
              <strong>Usuario:</strong> {detalle.username}
            </p>
            <p>
              <strong>Correo:</strong> {detalle.email}
            </p>
            <p>
              <strong>Rol:</strong> {detalle.rol}
            </p>
            <p>
              <strong>Empresa:</strong>{" "}
              {detalle.empresa_id ? nombreEmpresa(detalle.empresa_id) : "N/A"}
            </p>
            <p>
              <strong>Estado:</strong> {detalle.activo ? "Activo" : "Inactivo"}
            </p>
            <p>
              <strong>ID:</strong> {detalle.id}
            </p>

            <button className="btn-primary" onClick={() => setDetalle(null)}>
              Cerrar
            </button>
          </div>
        </div>
      )}

      {usuarioPassword && (
        <div className="modal-backdrop">
          <div className="modal-card">
            <h2>Cambiar contraseña</h2>

            <p>
              Usuario: <strong>{usuarioPassword.nombre_completo}</strong>
            </p>
            <p>
              Rol: <strong>{usuarioPassword.rol}</strong>
            </p>

            <div className="form-group full">
              <label>Nueva contraseña *</label>
              <input
                type="password"
                value={nuevaPassword}
                onChange={(e) => setNuevaPassword(e.target.value)}
                placeholder="Mínimo 6 caracteres"
              />
            </div>

            <div className="form-group full">
              <label>Confirmar contraseña *</label>
              <input
                type="password"
                value={confirmarPassword}
                onChange={(e) => setConfirmarPassword(e.target.value)}
                placeholder="Repite la contraseña"
              />
            </div>

            <div className="form-actions" style={{ marginTop: 18 }}>
              <button className="btn-secondary" onClick={cerrarModalPassword}>
                <X size={17} />
                Cancelar
              </button>

              <button className="btn-primary" onClick={guardarPassword}>
                <Save size={17} />
                Guardar contraseña
              </button>
            </div>
          </div>
        </div>
      )}
    </AdminLayout>
  );
}

const styles = {
  permisosContainer: {
    display: "flex",
    flexDirection: "column",
    gap: 18,
  },

  permisoGrupo: {
    border: "1px solid #e5eef8",
    borderRadius: 18,
    padding: 16,
    background: "#f8fbff",
  },

  permisoModulo: {
    margin: "0 0 12px",
    fontSize: 16,
    fontWeight: 900,
    color: "#172554",
    textTransform: "uppercase",
  },

  permisosGrid: {
    display: "grid",
    gridTemplateColumns: "repeat(2, minmax(260px, 1fr))",
    gap: 12,
  },

  permisoItem: {
    display: "flex",
    gap: 10,
    border: "1px solid #e2e8f0",
    padding: 13,
    borderRadius: 16,
    background: "white",
    cursor: "pointer",
  },

  permisoNombre: {
    display: "flex",
    alignItems: "center",
    gap: 6,
    fontSize: 14,
    color: "#0f172a",
  },

  permisoCodigo: {
    display: "inline-block",
    marginTop: 6,
    background: "#111827",
    color: "white",
    borderRadius: 7,
    padding: "3px 7px",
    fontSize: 11,
  },

  permisoDescripcion: {
    margin: "6px 0 0",
    fontSize: 12,
    color: "#64748b",
  },
};