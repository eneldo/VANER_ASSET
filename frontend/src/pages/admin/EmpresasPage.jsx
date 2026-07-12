// ============================================================
// FASE 33.2 - EMPRESAS SAAS PRO
// Archivo: frontend/src/pages/admin/EmpresasPage.jsx
//
// Objetivo:
// - Optimizar el módulo de Empresas / Clientes.
// - Mantener compatibilidad con backend actual FastAPI.
// - Mejorar UX, responsive, paginación, estados vacíos y KPIs.
//
// Endpoints usados:
// - GET    /empresas/
// - POST   /empresas/
// - PUT    /empresas/{id}
// - DELETE /empresas/{id}
// ============================================================

import { useEffect, useMemo, useState } from "react";
import AdminLayout from "./AdminLayout";
import API from "../../api/axios";

import {
  Building2,
  CheckCircle2,
  CircleOff,
  Download,
  Mail,
  MapPin,
  Pencil,
  Phone,
  Plus,
  RefreshCcw,
  Save,
  Search,
  Trash2,
  Users,
  X,
} from "lucide-react";

import "../../styles/empresas-sedes-saas-pro.css";

const FORM_INICIAL = {
  nombre: "",
  nit: "",
  telefono: "",
  direccion: "",
  correo: "",
  logo_url: "",
  activo: true,
};

export default function EmpresasPage() {
  const [empresas, setEmpresas] = useState([]);
  const [editandoId, setEditandoId] = useState(null);
  const [cargando, setCargando] = useState(false);
  const [guardando, setGuardando] = useState(false);
  const [busqueda, setBusqueda] = useState("");
  const [pagina, setPagina] = useState(1);
  const [porPagina, setPorPagina] = useState(8);
  const [form, setForm] = useState(FORM_INICIAL);

  useEffect(() => {
    const timer = window.setTimeout(() => setPagina(1), 0);
    return () => window.clearTimeout(timer);
  }, [busqueda, porPagina]);

  const cargarEmpresas = async () => {
    try {
      setCargando(true);
      const res = await API.get("/empresas/");
      setEmpresas(Array.isArray(res.data) ? res.data : []);
    } catch (error) {
      console.error("Error cargando empresas:", error);
      alert(error.response?.data?.detail || "Error cargando empresas");
    } finally {
      setCargando(false);
    }
  };

  useEffect(() => {
    const timer = window.setTimeout(() => cargarEmpresas(), 0);
    return () => window.clearTimeout(timer);
  }, []);

  const estadisticas = useMemo(() => {
    const total = empresas.length;
    const activas = empresas.filter((empresa) => empresa.activo).length;
    const inactivas = total - activas;
    const conCorreo = empresas.filter((empresa) => Boolean(empresa.correo)).length;

    return { total, activas, inactivas, conCorreo };
  }, [empresas]);

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
        empresa.activo ? "activo" : "inactivo",
      ]
        .filter(Boolean)
        .join(" ")
        .toLowerCase();

      return contenido.includes(texto);
    });
  }, [empresas, busqueda]);

  const totalPaginas = Math.max(1, Math.ceil(empresasFiltradas.length / porPagina));

  const paginaSegura = Math.min(pagina, totalPaginas);

  const empresasPaginadas = empresasFiltradas.slice(
    (paginaSegura - 1) * porPagina,
    paginaSegura * porPagina
  );

  const rangoInicial = empresasFiltradas.length === 0 ? 0 : (paginaSegura - 1) * porPagina + 1;
  const rangoFinal = Math.min(paginaSegura * porPagina, empresasFiltradas.length);

  const handleChange = (event) => {
    const { name, value, type, checked } = event.target;
    setForm((prev) => ({
      ...prev,
      [name]: type === "checkbox" ? checked : value,
    }));
  };

  const limpiarFormulario = () => {
    setForm(FORM_INICIAL);
    setEditandoId(null);
  };

  const guardarEmpresa = async (event) => {
    event.preventDefault();

    if (!form.nombre.trim()) {
      alert("El nombre de la empresa es obligatorio");
      return;
    }

    try {
      setGuardando(true);

      const payload = {
        ...form,
        nombre: form.nombre.trim(),
        nit: form.nit?.trim() || "",
        telefono: form.telefono?.trim() || "",
        direccion: form.direccion?.trim() || "",
        correo: form.correo?.trim() || "",
        logo_url: form.logo_url?.trim() || "",
      };

      if (editandoId) {
        await API.put(`/empresas/${editandoId}`, payload);
        alert("Empresa actualizada correctamente");
      } else {
        await API.post("/empresas/", payload);
        alert("Empresa creada correctamente");
      }

      limpiarFormulario();
      await cargarEmpresas();
    } catch (error) {
      console.error("Error guardando empresa:", error);
      alert(error.response?.data?.detail || "Error guardando empresa");
    } finally {
      setGuardando(false);
    }
  };

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

    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  const eliminarEmpresa = async (empresaId) => {
    const confirmar = confirm(
      "¿Seguro que deseas eliminar esta empresa? Esta acción puede afectar sedes, equipos y mantenimientos asociados."
    );

    if (!confirmar) return;

    try {
      await API.delete(`/empresas/${empresaId}`);
      alert("Empresa eliminada correctamente");
      await cargarEmpresas();
    } catch (error) {
      console.error("Error eliminando empresa:", error);
      alert(error.response?.data?.detail || "Error eliminando empresa");
    }
  };

  const exportarVistaCSV = () => {
    const encabezados = ["Nombre", "NIT", "Teléfono", "Correo", "Dirección", "Estado"];
    const filas = empresasFiltradas.map((empresa) => [
      empresa.nombre || "",
      empresa.nit || "",
      empresa.telefono || "",
      empresa.correo || "",
      empresa.direccion || "",
      empresa.activo ? "Activo" : "Inactivo",
    ]);

    const csv = [encabezados, ...filas]
      .map((fila) => fila.map((valor) => `"${String(valor).replaceAll('"', '""')}"`).join(","))
      .join("\n");

    const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "empresas_sga.csv";
    link.click();
    URL.revokeObjectURL(url);
  };

  return (
    <AdminLayout>
      <section className="sga-module-shell">
        <div className="sga-module-hero">
          <div className="sga-module-hero__icon">
            <Building2 size={30} />
          </div>

          <div className="sga-module-hero__text">
            <span>Administración SaaS</span>
            <h1>Empresas / Clientes</h1>
            <p>
              Gestiona las empresas cliente, datos de contacto y estado operativo
              dentro del ecosistema SGA.
            </p>
          </div>

          <div className="sga-module-hero__actions">
            <button className="sga-btn sga-btn--secondary" onClick={cargarEmpresas} disabled={cargando}>
              <RefreshCcw size={16} />
              {cargando ? "Actualizando..." : "Actualizar"}
            </button>

            <button className="sga-btn sga-btn--primary" onClick={exportarVistaCSV}>
              <Download size={16} />
              Exportar CSV
            </button>
          </div>
        </div>

        <div className="sga-kpi-grid">
          <article className="sga-kpi-card">
            <span className="sga-kpi-card__icon"><Users size={20} /></span>
            <div>
              <small>Total empresas</small>
              <strong>{estadisticas.total}</strong>
            </div>
          </article>

          <article className="sga-kpi-card success">
            <span className="sga-kpi-card__icon"><CheckCircle2 size={20} /></span>
            <div>
              <small>Empresas activas</small>
              <strong>{estadisticas.activas}</strong>
            </div>
          </article>

          <article className="sga-kpi-card danger">
            <span className="sga-kpi-card__icon"><CircleOff size={20} /></span>
            <div>
              <small>Inactivas</small>
              <strong>{estadisticas.inactivas}</strong>
            </div>
          </article>

          <article className="sga-kpi-card info">
            <span className="sga-kpi-card__icon"><Mail size={20} /></span>
            <div>
              <small>Con correo</small>
              <strong>{estadisticas.conCorreo}</strong>
            </div>
          </article>
        </div>

        <div className="sga-crud-layout-pro empresas-sedes-layout">
          <section className="sga-form-panel">
            <div className="sga-panel-title">
              <div>
                <span>{editandoId ? "Modo edición" : "Nuevo registro"}</span>
                <h2>{editandoId ? "Editar empresa" : "Crear empresa"}</h2>
                <p>Completa los datos corporativos principales del cliente.</p>
              </div>
            </div>

            <form onSubmit={guardarEmpresa} className="sga-form-grid-pro">
              <label className="sga-field full">
                <span>Nombre de empresa *</span>
                <input
                  name="nombre"
                  value={form.nombre}
                  onChange={handleChange}
                  placeholder="Ej: ESE Salud Yopal"
                />
              </label>

              <label className="sga-field">
                <span>NIT</span>
                <input
                  name="nit"
                  value={form.nit}
                  onChange={handleChange}
                  placeholder="Ej: 844000000-1"
                />
              </label>

              <label className="sga-field">
                <span>Teléfono</span>
                <input
                  name="telefono"
                  value={form.telefono}
                  onChange={handleChange}
                  placeholder="Ej: 6080000000"
                />
              </label>

              <label className="sga-field full">
                <span>Correo corporativo</span>
                <input
                  name="correo"
                  type="email"
                  value={form.correo}
                  onChange={handleChange}
                  placeholder="contacto@empresa.com"
                />
              </label>

              <label className="sga-field full">
                <span>Dirección</span>
                <input
                  name="direccion"
                  value={form.direccion}
                  onChange={handleChange}
                  placeholder="Dirección principal"
                />
              </label>

              <label className="sga-field full">
                <span>Logo URL</span>
                <input
                  name="logo_url"
                  value={form.logo_url}
                  onChange={handleChange}
                  placeholder="/uploads/logos/logo.png"
                />
              </label>

              <label className="sga-check-line full">
                <input
                  type="checkbox"
                  name="activo"
                  checked={form.activo}
                  onChange={handleChange}
                />
                <span>Empresa activa en el sistema</span>
              </label>

              <div className="sga-form-actions full">
                <button type="button" className="sga-btn sga-btn--ghost" onClick={limpiarFormulario}>
                  <X size={16} />
                  Limpiar
                </button>

                <button type="submit" className="sga-btn sga-btn--primary" disabled={guardando}>
                  {editandoId ? <Save size={16} /> : <Plus size={16} />}
                  {guardando ? "Guardando..." : editandoId ? "Actualizar" : "Crear empresa"}
                </button>
              </div>
            </form>
          </section>

          <section className="sga-list-panel">
            <div className="sga-list-toolbar">
              <div>
                <span>Inventario empresarial</span>
                <h2>Empresas registradas</h2>
                <p>
                  Mostrando {rangoInicial}-{rangoFinal} de {empresasFiltradas.length} registros
                </p>
              </div>

              <div className="sga-search-box">
                <Search size={17} />
                <input
                  value={busqueda}
                  onChange={(event) => setBusqueda(event.target.value)}
                  placeholder="Buscar empresa, NIT, correo, teléfono..."
                />
              </div>
            </div>

            <div className="sga-table-scroll-pro">
              <table className="sga-table-pro empresas-table-pro">
                <thead>
                  <tr>
                    <th>Empresa</th>
                    <th>Contacto</th>
                    <th>Identificación</th>
                    <th>Estado</th>
                    <th>Acciones</th>
                  </tr>
                </thead>

                <tbody>
                  {cargando && (
                    <tr>
                      <td colSpan="5">
                        <div className="sga-loading-state">Cargando empresas...</div>
                      </td>
                    </tr>
                  )}

                  {!cargando && empresasPaginadas.map((empresa) => (
                    <tr key={empresa.id}>
                      <td>
                        <div className="sga-entity-cell">
                          <div className="sga-avatar-square">
                            {empresa.logo_url ? (
                              <img src={empresa.logo_url} alt={empresa.nombre} />
                            ) : (
                              <Building2 size={20} />
                            )}
                          </div>

                          <div>
                            <strong>{empresa.nombre}</strong>
                            <small><MapPin size={13} /> {empresa.direccion || "Sin dirección"}</small>
                          </div>
                        </div>
                      </td>

                      <td>
                        <div className="sga-stack-cell">
                          <span><Phone size={13} /> {empresa.telefono || "Sin teléfono"}</span>
                          <span><Mail size={13} /> {empresa.correo || "Sin correo"}</span>
                        </div>
                      </td>

                      <td>
                        <span className="sga-code-pill">{empresa.nit || "N/A"}</span>
                      </td>

                      <td>
                        <span className={empresa.activo ? "sga-status active" : "sga-status inactive"}>
                          {empresa.activo ? "Activo" : "Inactivo"}
                        </span>
                      </td>

                      <td>
                        <div className="sga-row-actions">
                          <button className="sga-icon-btn" onClick={() => editarEmpresa(empresa)} title="Editar empresa">
                            <Pencil size={16} />
                          </button>

                          <button className="sga-icon-btn danger" onClick={() => eliminarEmpresa(empresa.id)} title="Eliminar empresa">
                            <Trash2 size={16} />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}

                  {!cargando && empresasPaginadas.length === 0 && (
                    <tr>
                      <td colSpan="5">
                        <div className="sga-empty-state">
                          <Building2 size={34} />
                          <strong>No hay empresas para mostrar</strong>
                          <p>Crea una empresa nueva o cambia el criterio de búsqueda.</p>
                        </div>
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>

            <div className="sga-pagination-pro">
              <div className="sga-pagination-info">
                Página {paginaSegura} de {totalPaginas}
              </div>

              <div className="sga-pagination-actions">
                <select value={porPagina} onChange={(event) => setPorPagina(Number(event.target.value))}>
                  <option value={6}>6 por página</option>
                  <option value={8}>8 por página</option>
                  <option value={12}>12 por página</option>
                  <option value={20}>20 por página</option>
                </select>

                <button disabled={paginaSegura === 1} onClick={() => setPagina(1)}>Primera</button>
                <button disabled={paginaSegura === 1} onClick={() => setPagina((prev) => Math.max(1, prev - 1))}>Anterior</button>
                <button disabled={paginaSegura === totalPaginas} onClick={() => setPagina((prev) => Math.min(totalPaginas, prev + 1))}>Siguiente</button>
                <button disabled={paginaSegura === totalPaginas} onClick={() => setPagina(totalPaginas)}>Última</button>
              </div>
            </div>
          </section>
        </div>
      </section>
    </AdminLayout>
  );
}
