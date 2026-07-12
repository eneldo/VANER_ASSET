// ============================================================
// FASE 33.2 - SEDES SAAS PRO
// Archivo: frontend/src/pages/admin/SedesPage.jsx
//
// Objetivo:
// - Optimizar el módulo de Sedes.
// - Mantener compatibilidad con backend actual FastAPI.
// - Mejorar UX, responsive, paginación, estados vacíos y KPIs.
//
// Endpoints usados:
// - GET    /empresas/
// - GET    /sedes/
// - POST   /sedes/
// - PUT    /sedes/{id}
// - DELETE /sedes/{id}
// ============================================================

import { useCallback, useEffect, useMemo, useState } from "react";
import AdminLayout from "./AdminLayout";
import API from "../../api/axios";

import {
  Building2,
  CheckCircle2,
  CircleOff,
  Download,
  MapPin,
  Pencil,
  Phone,
  Plus,
  RefreshCcw,
  Save,
  Search,
  Trash2,
  UserRound,
  X,
} from "lucide-react";

import "../../styles/empresas-sedes-saas-pro.css";

const FORM_INICIAL = {
  empresa_id: "",
  nombre: "",
  direccion: "",
  telefono: "",
  responsable: "",
  activo: true,
};

export default function SedesPage() {
  const [sedes, setSedes] = useState([]);
  const [empresas, setEmpresas] = useState([]);
  const [editandoId, setEditandoId] = useState(null);
  const [cargando, setCargando] = useState(false);
  const [guardando, setGuardando] = useState(false);
  const [busqueda, setBusqueda] = useState("");
  const [filtroEmpresa, setFiltroEmpresa] = useState("TODAS");
  const [pagina, setPagina] = useState(1);
  const [porPagina, setPorPagina] = useState(8);
  const [form, setForm] = useState(FORM_INICIAL);

  useEffect(() => {
    cargarDatos();
  }, []);

  useEffect(() => {
    const timer = window.setTimeout(() => setPagina(1), 0);
    return () => window.clearTimeout(timer);
  }, [busqueda, filtroEmpresa, porPagina]);

  async function cargarDatos() {
    try {
      setCargando(true);

      const [resEmpresas, resSedes] = await Promise.all([
        API.get("/empresas/"),
        API.get("/sedes/"),
      ]);

      setEmpresas(Array.isArray(resEmpresas.data) ? resEmpresas.data : []);
      setSedes(Array.isArray(resSedes.data) ? resSedes.data : []);
    } catch (error) {
      console.error("Error cargando sedes:", error);
      alert(error.response?.data?.detail || "Error cargando datos de sedes");
    } finally {
      setCargando(false);
    }
  };

  const getNombreEmpresa = useCallback((empresaId) => {
    const empresa = empresas.find((item) => String(item.id) === String(empresaId));
    return empresa ? empresa.nombre : "Empresa no encontrada";
  }, [empresas]);

  const estadisticas = useMemo(() => {
    const total = sedes.length;
    const activas = sedes.filter((sede) => sede.activo).length;
    const inactivas = total - activas;
    const empresasConSede = new Set(sedes.map((sede) => sede.empresa_id).filter(Boolean)).size;

    return { total, activas, inactivas, empresasConSede };
  }, [sedes]);

  const sedesFiltradas = useMemo(() => {
    const texto = busqueda.trim().toLowerCase();

    return sedes.filter((sede) => {
      const cumpleEmpresa =
        filtroEmpresa === "TODAS" || String(sede.empresa_id) === String(filtroEmpresa);

      if (!cumpleEmpresa) return false;

      if (!texto) return true;

      const contenido = [
        sede.nombre,
        sede.direccion,
        sede.telefono,
        sede.responsable,
        getNombreEmpresa(sede.empresa_id),
        sede.activo ? "activo" : "inactivo",
      ]
        .filter(Boolean)
        .join(" ")
        .toLowerCase();

      return contenido.includes(texto);
    });
  }, [sedes, busqueda, filtroEmpresa, getNombreEmpresa]);

  const totalPaginas = Math.max(1, Math.ceil(sedesFiltradas.length / porPagina));
  const paginaSegura = Math.min(pagina, totalPaginas);

  const sedesPaginadas = sedesFiltradas.slice(
    (paginaSegura - 1) * porPagina,
    paginaSegura * porPagina
  );

  const rangoInicial = sedesFiltradas.length === 0 ? 0 : (paginaSegura - 1) * porPagina + 1;
  const rangoFinal = Math.min(paginaSegura * porPagina, sedesFiltradas.length);

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

  const guardarSede = async (event) => {
    event.preventDefault();

    if (!form.empresa_id) {
      alert("Debe seleccionar una empresa");
      return;
    }

    if (!form.nombre.trim()) {
      alert("El nombre de la sede es obligatorio");
      return;
    }

    try {
      setGuardando(true);

      const payload = {
        ...form,
        nombre: form.nombre.trim(),
        direccion: form.direccion?.trim() || "",
        telefono: form.telefono?.trim() || "",
        responsable: form.responsable?.trim() || "",
      };

      if (editandoId) {
        await API.put(`/sedes/${editandoId}`, payload);
        alert("Sede actualizada correctamente");
      } else {
        await API.post("/sedes/", payload);
        alert("Sede creada correctamente");
      }

      limpiarFormulario();
      await cargarDatos();
    } catch (error) {
      console.error("Error guardando sede:", error);
      alert(error.response?.data?.detail || "Error guardando sede");
    } finally {
      setGuardando(false);
    }
  };

  const editarSede = (sede) => {
    setEditandoId(sede.id);
    setForm({
      empresa_id: sede.empresa_id || "",
      nombre: sede.nombre || "",
      direccion: sede.direccion || "",
      telefono: sede.telefono || "",
      responsable: sede.responsable || "",
      activo: sede.activo ?? true,
    });

    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  const eliminarSede = async (sedeId) => {
    const confirmar = confirm("¿Seguro que deseas eliminar esta sede?");
    if (!confirmar) return;

    try {
      await API.delete(`/sedes/${sedeId}`);
      alert("Sede eliminada correctamente");
      await cargarDatos();
    } catch (error) {
      console.error("Error eliminando sede:", error);
      alert(error.response?.data?.detail || "Error eliminando sede");
    }
  };

  const exportarVistaCSV = () => {
    const encabezados = ["Sede", "Empresa", "Dirección", "Teléfono", "Responsable", "Estado"];
    const filas = sedesFiltradas.map((sede) => [
      sede.nombre || "",
      getNombreEmpresa(sede.empresa_id),
      sede.direccion || "",
      sede.telefono || "",
      sede.responsable || "",
      sede.activo ? "Activo" : "Inactivo",
    ]);

    const csv = [encabezados, ...filas]
      .map((fila) => fila.map((valor) => `"${String(valor).replaceAll('"', '""')}"`).join(","))
      .join("\n");

    const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "sedes_sga.csv";
    link.click();
    URL.revokeObjectURL(url);
  };

  return (
    <AdminLayout>
      <section className="sga-module-shell">
        <div className="sga-module-hero">
          <div className="sga-module-hero__icon green">
            <MapPin size={30} />
          </div>

          <div className="sga-module-hero__text">
            <span>Infraestructura multiempresa</span>
            <h1>Sedes</h1>
            <p>
              Administra las sedes operativas de cada empresa cliente, responsables
              y datos de ubicación.
            </p>
          </div>

          <div className="sga-module-hero__actions">
            <button className="sga-btn sga-btn--secondary" onClick={cargarDatos} disabled={cargando}>
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
            <span className="sga-kpi-card__icon"><MapPin size={20} /></span>
            <div>
              <small>Total sedes</small>
              <strong>{estadisticas.total}</strong>
            </div>
          </article>

          <article className="sga-kpi-card success">
            <span className="sga-kpi-card__icon"><CheckCircle2 size={20} /></span>
            <div>
              <small>Sedes activas</small>
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
            <span className="sga-kpi-card__icon"><Building2 size={20} /></span>
            <div>
              <small>Empresas con sede</small>
              <strong>{estadisticas.empresasConSede}</strong>
            </div>
          </article>
        </div>

        <div className="sga-crud-layout-pro empresas-sedes-layout">
          <section className="sga-form-panel">
            <div className="sga-panel-title">
              <div>
                <span>{editandoId ? "Modo edición" : "Nuevo registro"}</span>
                <h2>{editandoId ? "Editar sede" : "Crear sede"}</h2>
                <p>Asocia la sede a una empresa y define su responsable operativo.</p>
              </div>
            </div>

            <form onSubmit={guardarSede} className="sga-form-grid-pro">
              <label className="sga-field full">
                <span>Empresa *</span>
                <select name="empresa_id" value={form.empresa_id} onChange={handleChange}>
                  <option value="">Seleccionar empresa</option>
                  {empresas.map((empresa) => (
                    <option key={empresa.id} value={empresa.id}>
                      {empresa.nombre}
                    </option>
                  ))}
                </select>
              </label>

              <label className="sga-field full">
                <span>Nombre de sede *</span>
                <input
                  name="nombre"
                  value={form.nombre}
                  onChange={handleChange}
                  placeholder="Ej: Sede Principal"
                />
              </label>

              <label className="sga-field full">
                <span>Dirección</span>
                <input
                  name="direccion"
                  value={form.direccion}
                  onChange={handleChange}
                  placeholder="Dirección de la sede"
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

              <label className="sga-field">
                <span>Responsable</span>
                <input
                  name="responsable"
                  value={form.responsable}
                  onChange={handleChange}
                  placeholder="Responsable de sede"
                />
              </label>

              <label className="sga-check-line full">
                <input
                  type="checkbox"
                  name="activo"
                  checked={form.activo}
                  onChange={handleChange}
                />
                <span>Sede activa en el sistema</span>
              </label>

              <div className="sga-form-actions full">
                <button type="button" className="sga-btn sga-btn--ghost" onClick={limpiarFormulario}>
                  <X size={16} />
                  Limpiar
                </button>

                <button type="submit" className="sga-btn sga-btn--primary" disabled={guardando}>
                  {editandoId ? <Save size={16} /> : <Plus size={16} />}
                  {guardando ? "Guardando..." : editandoId ? "Actualizar" : "Crear sede"}
                </button>
              </div>
            </form>
          </section>

          <section className="sga-list-panel">
            <div className="sga-list-toolbar sedes-toolbar-pro">
              <div>
                <span>Mapa operativo</span>
                <h2>Sedes registradas</h2>
                <p>
                  Mostrando {rangoInicial}-{rangoFinal} de {sedesFiltradas.length} registros
                </p>
              </div>

              <div className="sga-toolbar-controls">
                <select value={filtroEmpresa} onChange={(event) => setFiltroEmpresa(event.target.value)}>
                  <option value="TODAS">Todas las empresas</option>
                  {empresas.map((empresa) => (
                    <option key={empresa.id} value={empresa.id}>
                      {empresa.nombre}
                    </option>
                  ))}
                </select>

                <div className="sga-search-box">
                  <Search size={17} />
                  <input
                    value={busqueda}
                    onChange={(event) => setBusqueda(event.target.value)}
                    placeholder="Buscar sede, empresa, responsable..."
                  />
                </div>
              </div>
            </div>

            <div className="sga-table-scroll-pro">
              <table className="sga-table-pro sedes-table-pro">
                <thead>
                  <tr>
                    <th>Sede</th>
                    <th>Empresa</th>
                    <th>Contacto</th>
                    <th>Responsable</th>
                    <th>Estado</th>
                    <th>Acciones</th>
                  </tr>
                </thead>

                <tbody>
                  {cargando && (
                    <tr>
                      <td colSpan="6">
                        <div className="sga-loading-state">Cargando sedes...</div>
                      </td>
                    </tr>
                  )}

                  {!cargando && sedesPaginadas.map((sede) => (
                    <tr key={sede.id}>
                      <td>
                        <div className="sga-entity-cell">
                          <div className="sga-avatar-square green">
                            <MapPin size={20} />
                          </div>

                          <div>
                            <strong>{sede.nombre}</strong>
                            <small><MapPin size={13} /> {sede.direccion || "Sin dirección"}</small>
                          </div>
                        </div>
                      </td>

                      <td>
                        <span className="sga-company-pill">
                          <Building2 size={13} />
                          {getNombreEmpresa(sede.empresa_id)}
                        </span>
                      </td>

                      <td>
                        <span className="sga-inline-muted">
                          <Phone size={13} />
                          {sede.telefono || "Sin teléfono"}
                        </span>
                      </td>

                      <td>
                        <span className="sga-inline-muted">
                          <UserRound size={13} />
                          {sede.responsable || "Sin responsable"}
                        </span>
                      </td>

                      <td>
                        <span className={sede.activo ? "sga-status active" : "sga-status inactive"}>
                          {sede.activo ? "Activo" : "Inactivo"}
                        </span>
                      </td>

                      <td>
                        <div className="sga-row-actions">
                          <button className="sga-icon-btn" onClick={() => editarSede(sede)} title="Editar sede">
                            <Pencil size={16} />
                          </button>

                          <button className="sga-icon-btn danger" onClick={() => eliminarSede(sede.id)} title="Eliminar sede">
                            <Trash2 size={16} />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}

                  {!cargando && sedesPaginadas.length === 0 && (
                    <tr>
                      <td colSpan="6">
                        <div className="sga-empty-state">
                          <MapPin size={34} />
                          <strong>No hay sedes para mostrar</strong>
                          <p>Crea una sede nueva, cambia la empresa o ajusta el criterio de búsqueda.</p>
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
