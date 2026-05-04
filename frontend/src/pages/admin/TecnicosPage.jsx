// =========================================================
// PÁGINA ADMIN - TÉCNICOS PRO
// Selector de usuarios TECNICO, crear, listar, buscar,
// paginar, editar, eliminar y activar/inactivar.
// =========================================================

import { useEffect, useMemo, useState } from "react";
import AdminLayout from "./AdminLayout";
import API from "../../api/axios";
import {
  UserCog,
  Plus,
  Save,
  X,
  Trash2,
  Pencil,
  Power,
  RefreshCcw,
} from "lucide-react";

export default function TecnicosPage() {
  // =======================================================
  // ESTADOS PRINCIPALES
  // =======================================================
  const [usuarios, setUsuarios] = useState([]);
  const [tecnicos, setTecnicos] = useState([]);
  const [editandoId, setEditandoId] = useState(null);
  const [busqueda, setBusqueda] = useState("");

  // Paginación frontend
  const [pagina, setPagina] = useState(1);
  const porPagina = 6;

  // =======================================================
  // FORMULARIO
  // =======================================================
  const [form, setForm] = useState({
    usuario_id: "",
    documento: "",
    telefono: "",
    especialidad: "",
    cargo: "",
    activo: true,
  });

  // =======================================================
  // CARGA INICIAL
  // =======================================================
  useEffect(() => {
    cargarDatos();
  }, []);

  // =======================================================
  // CARGAR USUARIOS Y TÉCNICOS
  // =======================================================
  const cargarDatos = async () => {
    try {
      const [resUsuarios, resTecnicos] = await Promise.all([
        API.get("/usuarios/"),
        API.get("/tecnicos/"),
      ]);

      setUsuarios(resUsuarios.data);
      setTecnicos(resTecnicos.data);
    } catch (error) {
      console.error(error);
      alert("Error cargando datos de técnicos");
    }
  };

  // =======================================================
  // USUARIOS DISPONIBLES CON ROL TECNICO
  // Excluye usuarios que ya tienen perfil técnico
  // =======================================================
  const usuariosTecnicosDisponibles = useMemo(() => {
    const usuariosConPerfil = tecnicos.map((t) => t.usuario_id);

    return usuarios.filter(
      (u) =>
        u.rol === "TECNICO" &&
        u.activo &&
        (!usuariosConPerfil.includes(u.id) || u.id === form.usuario_id)
    );
  }, [usuarios, tecnicos, form.usuario_id]);

  // =======================================================
  // BUSCADOR Y PAGINACIÓN
  // =======================================================
  const tecnicosFiltrados = useMemo(() => {
    const texto = busqueda.toLowerCase();

    return tecnicos.filter((t) =>
      t.usuario?.nombre_completo?.toLowerCase().includes(texto) ||
      t.usuario?.username?.toLowerCase().includes(texto) ||
      t.usuario?.email?.toLowerCase().includes(texto) ||
      t.documento?.toLowerCase().includes(texto) ||
      t.especialidad?.toLowerCase().includes(texto) ||
      t.cargo?.toLowerCase().includes(texto)
    );
  }, [tecnicos, busqueda]);

  const totalPaginas = Math.ceil(tecnicosFiltrados.length / porPagina) || 1;

  const tecnicosPaginados = tecnicosFiltrados.slice(
    (pagina - 1) * porPagina,
    pagina * porPagina
  );

  // =======================================================
  // MANEJAR FORMULARIO
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
      usuario_id: "",
      documento: "",
      telefono: "",
      especialidad: "",
      cargo: "",
      activo: true,
    });

    setEditandoId(null);
  };

  // =======================================================
  // CREAR O ACTUALIZAR TÉCNICO
  // =======================================================
  const guardarTecnico = async (e) => {
    e.preventDefault();

    if (!form.usuario_id && !editandoId) {
      alert("Debe seleccionar un usuario con rol TÉCNICO");
      return;
    }

    try {
      if (editandoId) {
        await API.put(`/tecnicos/${editandoId}`, {
          documento: form.documento,
          telefono: form.telefono,
          especialidad: form.especialidad,
          cargo: form.cargo,
          activo: form.activo,
        });

        alert("Técnico actualizado correctamente");
      } else {
        await API.post("/tecnicos/", form);
        alert("Perfil técnico creado correctamente");
      }

      limpiarFormulario();
      cargarDatos();
    } catch (error) {
      console.error(error);
      alert(error.response?.data?.detail || "Error guardando técnico");
    }
  };

  // =======================================================
  // EDITAR TÉCNICO
  // =======================================================
  const editarTecnico = (tecnico) => {
    setEditandoId(tecnico.id);

    setForm({
      usuario_id: tecnico.usuario_id || "",
      documento: tecnico.documento || "",
      telefono: tecnico.telefono || "",
      especialidad: tecnico.especialidad || "",
      cargo: tecnico.cargo || "",
      activo: tecnico.activo,
    });
  };

  // =======================================================
  // ACTIVAR / INACTIVAR TÉCNICO
  // =======================================================
  const cambiarEstado = async (tecnicoId) => {
    try {
      await API.patch(`/tecnicos/${tecnicoId}/estado`);
      cargarDatos();
    } catch (error) {
      console.error(error);
      alert("Error cambiando estado del técnico");
    }
  };

  // =======================================================
  // ELIMINAR TÉCNICO
  // =======================================================
  const eliminarTecnico = async (tecnicoId) => {
    const confirmar = confirm(
      "¿Seguro que deseas eliminar este perfil técnico? El usuario no será eliminado."
    );

    if (!confirmar) return;

    try {
      await API.delete(`/tecnicos/${tecnicoId}`);
      alert("Técnico eliminado correctamente");
      cargarDatos();
    } catch (error) {
      console.error(error);
      alert(error.response?.data?.detail || "Error eliminando técnico");
    }
  };

  return (
    <AdminLayout>
      {/* ===================================================
          ENCABEZADO
          =================================================== */}
      <div className="page-header">
        <div className="page-icon">
          <UserCog size={26} />
        </div>

        <div>
          <h1>Técnicos</h1>
          <p>Administra perfiles técnicos y sus datos profesionales.</p>
        </div>
      </div>

      <div className="crud-grid">
        {/* =================================================
            FORMULARIO TÉCNICO
            ================================================= */}
        <section className="page-card">
          <h2>{editandoId ? "Editar técnico" : "Crear perfil técnico"}</h2>

          <form onSubmit={guardarTecnico} className="crud-form">
            <div className="form-group full">
              <label>Usuario técnico *</label>

              <select
                name="usuario_id"
                value={form.usuario_id}
                onChange={handleChange}
                disabled={!!editandoId}
              >
                <option value="">Seleccionar usuario técnico</option>

                {usuariosTecnicosDisponibles.map((u) => (
                  <option key={u.id} value={u.id}>
                    {u.nombre_completo} - {u.username} - {u.email}
                  </option>
                ))}
              </select>

              {editandoId && (
                <small style={{ color: "#64748b" }}>
                  El usuario asociado no se cambia durante edición.
                </small>
              )}
            </div>

            <div className="form-group">
              <label>Documento</label>
              <input
                name="documento"
                value={form.documento}
                onChange={handleChange}
                placeholder="123456789"
              />
            </div>

            <div className="form-group">
              <label>Teléfono</label>
              <input
                name="telefono"
                value={form.telefono}
                onChange={handleChange}
                placeholder="3000000000"
              />
            </div>

            <div className="form-group">
              <label>Especialidad</label>
              <input
                name="especialidad"
                value={form.especialidad}
                onChange={handleChange}
                placeholder="Biomédico"
              />
            </div>

            <div className="form-group">
              <label>Cargo</label>
              <input
                name="cargo"
                value={form.cargo}
                onChange={handleChange}
                placeholder="Técnico de mantenimiento"
              />
            </div>

            <label className="checkbox-line">
              <input
                type="checkbox"
                name="activo"
                checked={form.activo}
                onChange={handleChange}
              />
              Técnico activo
            </label>

            <div className="form-actions">
              <button type="button" className="btn-secondary" onClick={limpiarFormulario}>
                <X size={17} />
                Limpiar
              </button>

              <button type="submit" className="btn-primary">
                {editandoId ? <Save size={17} /> : <Plus size={17} />}
                {editandoId ? "Actualizar" : "Crear técnico"}
              </button>
            </div>
          </form>
        </section>

        {/* =================================================
            LISTADO TÉCNICOS
            ================================================= */}
        <section className="page-card">
          <div className="list-header">
            <div>
              <h2>Técnicos registrados</h2>
              <p>{tecnicosFiltrados.length} registros encontrados</p>
            </div>

            <button className="btn-secondary" onClick={cargarDatos}>
              <RefreshCcw size={16} />
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
              placeholder="Buscar técnico por nombre, correo, documento, especialidad..."
            />
          </div>

          <div className="table-wrap">
            <table className="sga-table">
              <thead>
                <tr>
                  <th>Técnico</th>
                  <th>Documento</th>
                  <th>Teléfono</th>
                  <th>Especialidad</th>
                  <th>Cargo</th>
                  <th>Estado</th>
                  <th>Acciones</th>
                </tr>
              </thead>

              <tbody>
                {tecnicosPaginados.map((t) => (
                  <tr key={t.id}>
                    <td>
                      <strong>{t.usuario?.nombre_completo || "Sin usuario"}</strong>
                      <br />
                      <small>
                        {t.usuario?.username || "N/A"} | {t.usuario?.email || "N/A"}
                      </small>
                    </td>

                    <td>{t.documento || "N/A"}</td>
                    <td>{t.telefono || "N/A"}</td>
                    <td>{t.especialidad || "N/A"}</td>
                    <td>{t.cargo || "N/A"}</td>

                    <td>
                      <span className={t.activo ? "badge active" : "badge inactive"}>
                        {t.activo ? "Activo" : "Inactivo"}
                      </span>
                    </td>

                    <td>
                      <div className="table-actions">
                        <button
                          className="icon-btn"
                          onClick={() => editarTecnico(t)}
                          title="Editar"
                        >
                          <Pencil size={16} />
                        </button>

                        <button
                          className="icon-btn"
                          onClick={() => cambiarEstado(t.id)}
                          title="Activar/Inactivar"
                        >
                          <Power size={16} />
                        </button>

                        <button
                          className="icon-btn danger"
                          onClick={() => eliminarTecnico(t.id)}
                          title="Eliminar"
                        >
                          <Trash2 size={16} />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}

                {tecnicosPaginados.length === 0 && (
                  <tr>
                    <td colSpan="7" style={{ textAlign: "center", padding: 30 }}>
                      No hay técnicos registrados.
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