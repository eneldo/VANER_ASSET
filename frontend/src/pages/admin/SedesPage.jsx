// =========================================================
// PÁGINA ADMIN - SEDES
// CRUD completo de sedes conectado al backend FastAPI
// Endpoints:
// - GET    /sedes/
// - POST   /sedes/
// - PUT    /sedes/{id}
// - DELETE /sedes/{id}
// - GET    /empresas/
// =========================================================

import { useEffect, useState } from "react";
import AdminLayout from "./AdminLayout";
import API from "../../api/axios";
import { MapPin, Plus, Save, Trash2, Pencil, X } from "lucide-react";

export default function SedesPage() {
  // =======================================================
  // ESTADOS PRINCIPALES
  // =======================================================
  const [sedes, setSedes] = useState([]);
  const [empresas, setEmpresas] = useState([]);
  const [editandoId, setEditandoId] = useState(null);
  const [cargando, setCargando] = useState(false);

  // =======================================================
  // FORMULARIO
  // =======================================================
  const [form, setForm] = useState({
    empresa_id: "",
    nombre: "",
    direccion: "",
    telefono: "",
    responsable: "",
    activo: true,
  });

  // =======================================================
  // CARGA INICIAL
  // =======================================================
  useEffect(() => {
    cargarDatos();
  }, []);

  // =======================================================
  // CARGAR EMPRESAS Y SEDES
  // =======================================================
  const cargarDatos = async () => {
    try {
      setCargando(true);

      const [resEmpresas, resSedes] = await Promise.all([
        API.get("/empresas/"),
        API.get("/sedes/"),
      ]);

      setEmpresas(resEmpresas.data);
      setSedes(resSedes.data);
    } catch (error) {
      console.error(error);
      alert("Error cargando datos de sedes");
    } finally {
      setCargando(false);
    }
  };

  // =======================================================
  // OBTENER NOMBRE DE EMPRESA POR ID
  // =======================================================
  const getNombreEmpresa = (empresaId) => {
    const empresa = empresas.find((e) => e.id === empresaId);
    return empresa ? empresa.nombre : "Empresa no encontrada";
  };

  // =======================================================
  // MANEJAR CAMBIOS FORMULARIO
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
      empresa_id: "",
      nombre: "",
      direccion: "",
      telefono: "",
      responsable: "",
      activo: true,
    });

    setEditandoId(null);
  };

  // =======================================================
  // CREAR O ACTUALIZAR SEDE
  // =======================================================
  const guardarSede = async (e) => {
    e.preventDefault();

    if (!form.empresa_id) {
      alert("Debe seleccionar una empresa");
      return;
    }

    if (!form.nombre.trim()) {
      alert("El nombre de la sede es obligatorio");
      return;
    }

    try {
      if (editandoId) {
        // Actualizar sede existente
        await API.put(`/sedes/${editandoId}`, form);
        alert("Sede actualizada correctamente");
      } else {
        // Crear nueva sede
        await API.post("/sedes/", form);
        alert("Sede creada correctamente");
      }

      limpiarFormulario();
      cargarDatos();
    } catch (error) {
      console.error(error);
      alert(error.response?.data?.detail || "Error guardando sede");
    }
  };

  // =======================================================
  // CARGAR SEDE AL FORMULARIO PARA EDITAR
  // =======================================================
  const editarSede = (sede) => {
    setEditandoId(sede.id);

    setForm({
      empresa_id: sede.empresa_id || "",
      nombre: sede.nombre || "",
      direccion: sede.direccion || "",
      telefono: sede.telefono || "",
      responsable: sede.responsable || "",
      activo: sede.activo,
    });
  };

  // =======================================================
  // ELIMINAR SEDE
  // =======================================================
  const eliminarSede = async (sedeId) => {
    const confirmar = confirm(
      "¿Seguro que deseas eliminar esta sede? Esta acción puede afectar equipos asociados."
    );

    if (!confirmar) return;

    try {
      await API.delete(`/sedes/${sedeId}`);
      alert("Sede eliminada correctamente");
      cargarDatos();
    } catch (error) {
      console.error(error);
      alert(error.response?.data?.detail || "Error eliminando sede");
    }
  };

  return (
    <AdminLayout>
      {/* ===================================================
          ENCABEZADO
          =================================================== */}
      <div className="page-header">
        <div className="page-icon">
          <MapPin size={26} />
        </div>

        <div>
          <h1>Sedes</h1>
          <p>Administra las sedes asociadas a cada empresa cliente.</p>
        </div>
      </div>

      <div className="crud-grid">
        {/* =================================================
            FORMULARIO SEDE
            ================================================= */}
        <section className="page-card">
          <h2>{editandoId ? "Editar sede" : "Crear sede"}</h2>

          <form onSubmit={guardarSede} className="crud-form">
            <div className="form-group full">
              <label>Empresa *</label>
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

            <div className="form-group full">
              <label>Nombre de sede *</label>
              <input
                name="nombre"
                value={form.nombre}
                onChange={handleChange}
                placeholder="Ej: Juan Luis Londoño"
              />
            </div>

            <div className="form-group full">
              <label>Dirección</label>
              <input
                name="direccion"
                value={form.direccion}
                onChange={handleChange}
                placeholder="Dirección de la sede"
              />
            </div>

            <div className="form-group">
              <label>Teléfono</label>
              <input
                name="telefono"
                value={form.telefono}
                onChange={handleChange}
                placeholder="Ej: 6080000000"
              />
            </div>

            <div className="form-group">
              <label>Responsable</label>
              <input
                name="responsable"
                value={form.responsable}
                onChange={handleChange}
                placeholder="Responsable de sede"
              />
            </div>

            <label className="checkbox-line">
              <input
                type="checkbox"
                name="activo"
                checked={form.activo}
                onChange={handleChange}
              />
              Sede activa
            </label>

            <div className="form-actions">
              <button type="button" className="btn-secondary" onClick={limpiarFormulario}>
                <X size={17} />
                Limpiar
              </button>

              <button type="submit" className="btn-primary">
                {editandoId ? <Save size={17} /> : <Plus size={17} />}
                {editandoId ? "Actualizar" : "Crear sede"}
              </button>
            </div>
          </form>
        </section>

        {/* =================================================
            LISTADO SEDES
            ================================================= */}
        <section className="page-card">
          <div className="list-header">
            <div>
              <h2>Sedes registradas</h2>
              <p>{sedes.length} registros encontrados</p>
            </div>

            <button className="btn-secondary" onClick={cargarDatos}>
              Recargar
            </button>
          </div>

          {cargando ? (
            <p>Cargando sedes...</p>
          ) : (
            <div className="table-wrap">
              <table className="sga-table">
                <thead>
                  <tr>
                    <th>Sede</th>
                    <th>Empresa</th>
                    <th>Teléfono</th>
                    <th>Responsable</th>
                    <th>Estado</th>
                    <th>Acciones</th>
                  </tr>
                </thead>

                <tbody>
                  {sedes.map((sede) => (
                    <tr key={sede.id}>
                      <td>
                        <strong>{sede.nombre}</strong>
                        <br />
                        <small>{sede.direccion || "Sin dirección"}</small>
                      </td>

                      <td>{getNombreEmpresa(sede.empresa_id)}</td>
                      <td>{sede.telefono || "N/A"}</td>
                      <td>{sede.responsable || "N/A"}</td>

                      <td>
                        <span className={sede.activo ? "badge active" : "badge inactive"}>
                          {sede.activo ? "Activo" : "Inactivo"}
                        </span>
                      </td>

                      <td>
                        <div className="table-actions">
                          <button
                            className="icon-btn"
                            onClick={() => editarSede(sede)}
                            title="Editar"
                          >
                            <Pencil size={16} />
                          </button>

                          <button
                            className="icon-btn danger"
                            onClick={() => eliminarSede(sede.id)}
                            title="Eliminar"
                          >
                            <Trash2 size={16} />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}

                  {sedes.length === 0 && (
                    <tr>
                      <td colSpan="6" style={{ textAlign: "center", padding: 30 }}>
                        No hay sedes registradas.
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