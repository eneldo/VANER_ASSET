// =========================================================
// PÁGINA ADMIN - EMPRESAS / CLIENTES
// CRUD completo conectado al backend FastAPI
// Endpoint base: /empresas/
// =========================================================

import { useEffect, useState } from "react";
import AdminLayout from "./AdminLayout";
import API from "../../api/axios";
import { Building2, Plus, Save, Trash2, Pencil, X } from "lucide-react";

export default function EmpresasPage() {
  // =======================================================
  // ESTADOS PRINCIPALES
  // =======================================================
  const [empresas, setEmpresas] = useState([]);
  const [editandoId, setEditandoId] = useState(null);
  const [cargando, setCargando] = useState(false);

  // =======================================================
  // FORMULARIO
  // =======================================================
  const [form, setForm] = useState({
    nombre: "",
    nit: "",
    telefono: "",
    direccion: "",
    correo: "",
    logo_url: "",
    activo: true,
  });

  // =======================================================
  // CARGA INICIAL
  // =======================================================
  useEffect(() => {
    cargarEmpresas();
  }, []);

  // =======================================================
  // LISTAR EMPRESAS
  // =======================================================
  const cargarEmpresas = async () => {
    try {
      setCargando(true);
      const res = await API.get("/empresas/");
      setEmpresas(res.data);
    } catch (error) {
      console.error(error);
      alert("Error cargando empresas");
    } finally {
      setCargando(false);
    }
  };

  // =======================================================
  // MANEJAR CAMBIOS DEL FORMULARIO
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
      nit: "",
      telefono: "",
      direccion: "",
      correo: "",
      logo_url: "",
      activo: true,
    });

    setEditandoId(null);
  };

  // =======================================================
  // CREAR O ACTUALIZAR EMPRESA
  // =======================================================
  const guardarEmpresa = async (e) => {
    e.preventDefault();

    if (!form.nombre.trim()) {
      alert("El nombre de la empresa es obligatorio");
      return;
    }

    try {
      if (editandoId) {
        // Actualizar empresa existente
        await API.put(`/empresas/${editandoId}`, form);
        alert("Empresa actualizada correctamente");
      } else {
        // Crear nueva empresa
        await API.post("/empresas/", form);
        alert("Empresa creada correctamente");
      }

      limpiarFormulario();
      cargarEmpresas();
    } catch (error) {
      console.error(error);
      alert(error.response?.data?.detail || "Error guardando empresa");
    }
  };

  // =======================================================
  // CARGAR EMPRESA AL FORMULARIO PARA EDITAR
  // =======================================================
  const editarEmpresa = (empresa) => {
    setEditandoId(empresa.id);

    setForm({
      nombre: empresa.nombre || "",
      nit: empresa.nit || "",
      telefono: empresa.telefono || "",
      direccion: empresa.direccion || "",
      correo: empresa.correo || "",
      logo_url: empresa.logo_url || "",
      activo: empresa.activo,
    });
  };

  // =======================================================
  // ELIMINAR EMPRESA
  // =======================================================
  const eliminarEmpresa = async (empresaId) => {
    const confirmar = confirm(
      "¿Seguro que deseas eliminar esta empresa? Esta acción puede afectar sedes y equipos asociados."
    );

    if (!confirmar) return;

    try {
      await API.delete(`/empresas/${empresaId}`);
      alert("Empresa eliminada correctamente");
      cargarEmpresas();
    } catch (error) {
      console.error(error);
      alert(error.response?.data?.detail || "Error eliminando empresa");
    }
  };

  return (
    <AdminLayout>
      {/* ===================================================
          ENCABEZADO
          =================================================== */}
      <div className="page-header">
        <div className="page-icon">
          <Building2 size={26} />
        </div>

        <div>
          <h1>Empresas / Cliente</h1>
          <p>Crea, administra y controla las empresas cliente del sistema.</p>
        </div>
      </div>

      <div className="crud-grid">
        {/* =================================================
            FORMULARIO EMPRESA
            ================================================= */}
        <section className="page-card">
          <h2>{editandoId ? "Editar empresa" : "Crear empresa"}</h2>

          <form onSubmit={guardarEmpresa} className="crud-form">
            <div className="form-group">
              <label>Nombre de empresa *</label>
              <input
                name="nombre"
                value={form.nombre}
                onChange={handleChange}
                placeholder="Ej: ESE Salud Yopal"
              />
            </div>

            <div className="form-group">
              <label>NIT</label>
              <input
                name="nit"
                value={form.nit}
                onChange={handleChange}
                placeholder="Ej: 844000000-1"
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
              <label>Correo</label>
              <input
                name="correo"
                type="email"
                value={form.correo}
                onChange={handleChange}
                placeholder="contacto@empresa.com"
              />
            </div>

            <div className="form-group full">
              <label>Dirección</label>
              <input
                name="direccion"
                value={form.direccion}
                onChange={handleChange}
                placeholder="Dirección principal"
              />
            </div>

            <div className="form-group full">
              <label>Logo URL</label>
              <input
                name="logo_url"
                value={form.logo_url}
                onChange={handleChange}
                placeholder="/uploads/logos/logo.png"
              />
            </div>

            <label className="checkbox-line">
              <input
                type="checkbox"
                name="activo"
                checked={form.activo}
                onChange={handleChange}
              />
              Empresa activa
            </label>

            <div className="form-actions">
              <button type="button" className="btn-secondary" onClick={limpiarFormulario}>
                <X size={17} />
                Limpiar
              </button>

              <button type="submit" className="btn-primary">
                {editandoId ? <Save size={17} /> : <Plus size={17} />}
                {editandoId ? "Actualizar" : "Crear empresa"}
              </button>
            </div>
          </form>
        </section>

        {/* =================================================
            LISTADO EMPRESAS
            ================================================= */}
        <section className="page-card">
          <div className="list-header">
            <div>
              <h2>Empresas registradas</h2>
              <p>{empresas.length} registros encontrados</p>
            </div>

            <button className="btn-secondary" onClick={cargarEmpresas}>
              Recargar
            </button>
          </div>

          {cargando ? (
            <p>Cargando empresas...</p>
          ) : (
            <div className="table-wrap">
              <table className="sga-table">
                <thead>
                  <tr>
                    <th>Empresa</th>
                    <th>NIT</th>
                    <th>Teléfono</th>
                    <th>Estado</th>
                    <th>Acciones</th>
                  </tr>
                </thead>

                <tbody>
                  {empresas.map((empresa) => (
                    <tr key={empresa.id}>
                      <td>
                        <strong>{empresa.nombre}</strong>
                        <br />
                        <small>{empresa.correo || "Sin correo"}</small>
                      </td>

                      <td>{empresa.nit || "N/A"}</td>
                      <td>{empresa.telefono || "N/A"}</td>

                      <td>
                        <span className={empresa.activo ? "badge active" : "badge inactive"}>
                          {empresa.activo ? "Activo" : "Inactivo"}
                        </span>
                      </td>

                      <td>
                        <div className="table-actions">
                          <button
                            className="icon-btn"
                            onClick={() => editarEmpresa(empresa)}
                            title="Editar"
                          >
                            <Pencil size={16} />
                          </button>

                          <button
                            className="icon-btn danger"
                            onClick={() => eliminarEmpresa(empresa.id)}
                            title="Eliminar"
                          >
                            <Trash2 size={16} />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}

                  {empresas.length === 0 && (
                    <tr>
                      <td colSpan="5" style={{ textAlign: "center", padding: 30 }}>
                        No hay empresas registradas.
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