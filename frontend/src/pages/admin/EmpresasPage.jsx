// =========================================================
// PÁGINA ADMIN - EMPRESAS / CLIENTES
// CRUD completo conectado al backend FastAPI.
// Endpoint base: /empresas/
//
// Patrón PRO aplicado:
// - Usa AdminLayout igual que EquiposPage.
// - Usa clases reutilizadas de EquiposPage.
// - Tiene búsqueda local.
// - Tiene paginación.
// - No modifica backend.
// =========================================================

import { useEffect, useMemo, useState } from "react";
import AdminLayout from "./AdminLayout";
import API from "../../api/axios";

import {
  Building2,
  Plus,
  Save,
  Trash2,
  Pencil,
  X,
  RefreshCcw,
} from "lucide-react";

import "../../styles/sidebar.css";

export default function EmpresasPage() {
  // =======================================================
  // ESTADOS PRINCIPALES
  // =======================================================
  const [empresas, setEmpresas] = useState([]);
  const [editandoId, setEditandoId] = useState(null);
  const [cargando, setCargando] = useState(false);

  // =======================================================
  // BÚSQUEDA Y PAGINACIÓN
  // =======================================================
  const [busqueda, setBusqueda] = useState("");
  const [pagina, setPagina] = useState(1);
  const porPagina = 6;

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
  // REINICIA PÁGINA AL BUSCAR
  // =======================================================
  useEffect(() => {
    setPagina(1);
  }, [busqueda]);

  // =======================================================
  // LISTAR EMPRESAS
  // =======================================================
  const cargarEmpresas = async () => {
    try {
      setCargando(true);
      const res = await API.get("/empresas/");
      setEmpresas(Array.isArray(res.data) ? res.data : []);
    } catch (error) {
      console.error(error);
      alert("Error cargando empresas");
    } finally {
      setCargando(false);
    }
  };

  // =======================================================
  // FILTRADO LOCAL
  // =======================================================
  const empresasFiltradas = useMemo(() => {
    const texto = busqueda.trim().toLowerCase();

    if (!texto) return empresas;

    return empresas.filter((empresa) => {
      const contenido = [
        empresa.nombre,
        empresa.nit,
        empresa.telefono,
        empresa.correo,
        empresa.direccion,
      ]
        .filter(Boolean)
        .join(" ")
        .toLowerCase();

      return contenido.includes(texto);
    });
  }, [empresas, busqueda]);

  // =======================================================
  // PAGINACIÓN
  // =======================================================
  const totalPaginas = Math.ceil(empresasFiltradas.length / porPagina) || 1;

  const empresasPaginadas = empresasFiltradas.slice(
    (pagina - 1) * porPagina,
    pagina * porPagina
  );

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
        await API.put(`/empresas/${editandoId}`, form);
        alert("Empresa actualizada correctamente");
      } else {
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
  // EDITAR EMPRESA
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
      activo: empresa.activo ?? true,
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

      {/* ===================================================
          LAYOUT PRO IGUAL A EQUIPOS
      =================================================== */}
      <div className="equipos-pro-layout">
        {/* =================================================
            FORMULARIO
        ================================================= */}
        <section className="equipos-pro-form-card">
          <div className="equipos-card-title">
            <div>
              <h2>{editandoId ? "Editar empresa" : "Crear empresa"}</h2>
              <p>Registra la información principal del cliente.</p>
            </div>
          </div>

          <form onSubmit={guardarEmpresa} className="equipos-pro-form">
            <div className="form-group full">
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

            <div className="form-group full">
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
                {editandoId ? "Actualizar" : "Crear empresa"}
              </button>
            </div>
          </form>
        </section>

        {/* =================================================
            LISTADO
        ================================================= */}
        <section className="equipos-pro-list-card">
          <div className="equipos-toolbar">
            <div>
              <h2>Empresas registradas</h2>
              <p>
                {empresasFiltradas.length} registros encontrados
                {busqueda ? ` de ${empresas.length} empresas` : ""}
              </p>
            </div>

            <button
              className="btn-secondary"
              onClick={cargarEmpresas}
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
            placeholder="Buscar por empresa, NIT, teléfono, correo o dirección..."
          />

          {cargando ? (
            <p>Cargando empresas...</p>
          ) : (
            <>
              <div className="table-wrap equipos-table-wrap">
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
                    {empresasPaginadas.map((empresa) => (
                      <tr key={empresa.id}>
                        <td>
                          <strong className="equipo-title">
                            {empresa.nombre}
                          </strong>
                          <br />
                          <small className="equipo-sub">
                            {empresa.correo || "Sin correo"}
                          </small>
                          <br />
                          <small className="equipo-sub">
                            {empresa.direccion || "Sin dirección"}
                          </small>
                        </td>

                        <td>{empresa.nit || "N/A"}</td>
                        <td>{empresa.telefono || "N/A"}</td>

                        <td>
                          <span
                            className={
                              empresa.activo ? "badge active" : "badge inactive"
                            }
                          >
                            {empresa.activo ? "Activo" : "Inactivo"}
                          </span>
                        </td>

                        <td>
                          <div className="table-actions">
                            <button
                              className="icon-btn"
                              onClick={() => editarEmpresa(empresa)}
                              title="Editar empresa"
                            >
                              <Pencil size={16} />
                            </button>

                            <button
                              className="icon-btn danger"
                              onClick={() => eliminarEmpresa(empresa.id)}
                              title="Eliminar empresa"
                            >
                              <Trash2 size={16} />
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))}

                    {empresasPaginadas.length === 0 && (
                      <tr>
                        <td colSpan="5" style={{ textAlign: "center", padding: 30 }}>
                          No hay empresas registradas.
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>

              {/* ===========================================
                  PAGINACIÓN
              =========================================== */}
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
            </>
          )}
        </section>
      </div>
    </AdminLayout>
  );
}