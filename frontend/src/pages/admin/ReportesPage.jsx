// ============================================================
// PÁGINA: Reportes PRO
// Archivo: frontend/src/pages/admin/ReportesPage.jsx
// Función:
// - Interfaz PRO con sidebar, menú hamburguesa, topbar
// - Filtros por empresa, sede, estado y fechas
// - Exportar mantenimientos en Excel y PDF
// - Tabla con scroll horizontal/vertical y paginación
// ============================================================

import { useEffect, useEffectEvent, useMemo, useState } from "react";
import {
  Menu,
  Bell,
  LogOut,
  FileText,
  FileSpreadsheet,
  Search,
  RefreshCcw,
  Building2,
  MapPin,
  Wrench,
  Download,
  Inbox,
  ChevronLeft,
  ChevronRight,
  ChevronsLeft,
  ChevronsRight,
} from "lucide-react";

import Sidebar from "../../components/Sidebar";
import api from "../../api/axios";
import { clearSession } from "../../utils/authStorage";
import "../../styles/reportes.css";

const API_URL = import.meta.env.VITE_API_URL || "/api";

export default function ReportesPage() {
  const [sidebarOpen, setSidebarOpen] = useState(true);

  const [empresas, setEmpresas] = useState([]);
  const [sedes, setSedes] = useState([]);
  const [items, setItems] = useState([]);

  const [empresaId, setEmpresaId] = useState("");
  const [sedeId, setSedeId] = useState("");
  const [estado, setEstado] = useState("");
  const [fechaInicio, setFechaInicio] = useState("");
  const [fechaFin, setFechaFin] = useState("");

  const [loading, setLoading] = useState(false);

  // Paginación
  const [paginaActual, setPaginaActual] = useState(1);
  const [filasPorPagina, setFilasPorPagina] = useState(10);

  const user = useMemo(() => {
    try {
      return JSON.parse(localStorage.getItem("user")) || null;
    } catch {
      return null;
    }
  }, []);

  const estados = [
    "PROGRAMADO",
    "ASIGNADO",
    "EN_PROCESO",
    "PAUSADO",
    "FINALIZADO",
    "ANULADO",
  ];

  const queryParams = useMemo(() => {
    const params = new URLSearchParams();

    if (empresaId) params.append("empresa_id", empresaId);
    if (sedeId) params.append("sede_id", sedeId);
    if (estado) params.append("estado", estado);
    if (fechaInicio) params.append("fecha_inicio", fechaInicio);
    if (fechaFin) params.append("fecha_fin", fechaFin);

    return params.toString();
  }, [empresaId, sedeId, estado, fechaInicio, fechaFin]);

  const totalPaginas = Math.max(1, Math.ceil(items.length / filasPorPagina));

  const itemsPaginados = useMemo(() => {
    const inicio = (paginaActual - 1) * filasPorPagina;
    const fin = inicio + filasPorPagina;
    return items.slice(inicio, fin);
  }, [items, paginaActual, filasPorPagina]);

  const inicioRegistro = items.length === 0 ? 0 : (paginaActual - 1) * filasPorPagina + 1;
  const finRegistro = Math.min(paginaActual * filasPorPagina, items.length);

  const cargarInicial = useEffectEvent(() => {
    cargarEmpresas();
    cargarReporte();
  });
  const cargarSedesAlCambiarEmpresa = useEffectEvent(() => cargarSedes());

  useEffect(() => {
    cargarInicial();
  }, []);

  useEffect(() => {
    cargarSedesAlCambiarEmpresa();
  }, [empresaId]);

  useEffect(() => {
    const timer = window.setTimeout(() => setPaginaActual(1), 0);
    return () => window.clearTimeout(timer);
  }, [items, filasPorPagina]);

  const getHeaders = () => {
    const token = localStorage.getItem("token") || localStorage.getItem("access_token");

    return {
      Authorization: token ? `Bearer ${token}` : "",
    };
  };

  async function cargarEmpresas() {
    try {
      const res = await fetch(`${API_URL}/reportes/filtros/empresas`, {
        headers: getHeaders(),
      });

      const data = await res.json();
      setEmpresas(Array.isArray(data) ? data : []);
    } catch (error) {
      console.error("Error cargando empresas:", error);
    }
  };

  async function cargarSedes() {
    try {
      const url = empresaId
        ? `${API_URL}/reportes/filtros/sedes?empresa_id=${empresaId}`
        : `${API_URL}/reportes/filtros/sedes`;

      const res = await fetch(url, {
        headers: getHeaders(),
      });

      const data = await res.json();
      setSedes(Array.isArray(data) ? data : []);
      setSedeId("");
    } catch (error) {
      console.error("Error cargando sedes:", error);
    }
  };

  async function cargarReporte() {
    setLoading(true);

    try {
      const url = `${API_URL}/reportes/mantenimientos${
        queryParams ? `?${queryParams}` : ""
      }`;

      const res = await fetch(url, {
        headers: getHeaders(),
      });

      const data = await res.json();
      setItems(data.items || []);
    } catch (error) {
      console.error("Error cargando reporte:", error);
      setItems([]);
    } finally {
      setLoading(false);
    }
  };

  const limpiarFiltros = () => {
    setEmpresaId("");
    setSedeId("");
    setEstado("");
    setFechaInicio("");
    setFechaFin("");

    setTimeout(() => {
      cargarReporte();
    }, 150);
  };

  const descargarArchivo = async (tipo) => {
    try {
      const endpoint = tipo === "excel" ? "mantenimientos/excel" : "mantenimientos/pdf";

      const url = `${API_URL}/reportes/${endpoint}${queryParams ? `?${queryParams}` : ""}`;

      const res = await fetch(url, {
        headers: getHeaders(),
      });

      if (!res.ok) {
        alert("No se pudo generar el reporte.");
        return;
      }

      const blob = await res.blob();
      const fileURL = window.URL.createObjectURL(blob);

      const link = document.createElement("a");
      link.href = fileURL;
      link.download =
        tipo === "excel" ? "reporte_mantenimientos.xlsx" : "reporte_mantenimientos.pdf";

      document.body.appendChild(link);
      link.click();
      link.remove();

      window.URL.revokeObjectURL(fileURL);
    } catch (error) {
      console.error("Error descargando archivo:", error);
      alert("Error generando el archivo.");
    }
  };

  const logout = async () => {
    try {
      await api.post("/auth/logout", {});
    } finally {
      clearSession();
      localStorage.removeItem("token");
      window.location.href = "/";
    }
  };

  const irPrimeraPagina = () => setPaginaActual(1);
  const irPaginaAnterior = () => setPaginaActual((prev) => Math.max(1, prev - 1));
  const irPaginaSiguiente = () => setPaginaActual((prev) => Math.min(totalPaginas, prev + 1));
  const irUltimaPagina = () => setPaginaActual(totalPaginas);

  return (
    <div className={`reportes-shell ${sidebarOpen ? "sidebar-open" : "sidebar-closed"}`}>
      <div className="reportes-sidebar-wrap">
        <Sidebar user={user} onLogout={logout} />
      </div>

      <main className="reportes-main">
        <header className="reportes-topbar">
          <div className="reportes-topbar-left">
            <button
              className="reportes-menu-btn"
              onClick={() => setSidebarOpen((prev) => !prev)}
              title="Abrir / cerrar menú"
            >
              <Menu size={24} />
            </button>

            <h2>Reportes PRO</h2>
          </div>

          <div className="reportes-topbar-actions">
            <button className="reportes-icon-btn">
              <Bell size={22} />
              <span>3</span>
            </button>

            <button className="reportes-icon-btn" onClick={logout}>
              <LogOut size={22} />
            </button>
          </div>
        </header>

        <section className="reportes-pro-page">
          <div className="reportes-pro-header">
            <div>
              <span className="reportes-pro-badge">SGAHolding</span>
              <h1>Reportes PRO</h1>
              <p>
                Genera reportes profesionales de mantenimientos por empresa, sede,
                estado y rango de fechas.
              </p>
            </div>

            <div className="reportes-pro-header-icon">
              <FileText size={38} />
            </div>
          </div>

          <div className="reportes-pro-kpis">
            <div className="reportes-pro-card">
              <Building2 size={25} />
              <div>
                <span>Empresas</span>
                <strong>{empresas.length}</strong>
              </div>
            </div>

            <div className="reportes-pro-card">
              <MapPin size={25} />
              <div>
                <span>Sedes</span>
                <strong>{sedes.length}</strong>
              </div>
            </div>

            <div className="reportes-pro-card">
              <Wrench size={25} />
              <div>
                <span>Mantenimientos</span>
                <strong>{items.length}</strong>
              </div>
            </div>
          </div>

          <div className="reportes-pro-panel">
            <div className="reportes-pro-panel-title">
              <h2>Filtros del reporte</h2>
              <p>Selecciona los parámetros antes de generar Excel o PDF.</p>
            </div>

            <div className="reportes-pro-filtros">
              <div className="reportes-pro-field">
                <label>Empresa</label>
                <select value={empresaId} onChange={(e) => setEmpresaId(e.target.value)}>
                  <option value="">Todas las empresas</option>
                  {empresas.map((empresa) => (
                    <option key={empresa.id} value={empresa.id}>
                      {empresa.nombre}
                    </option>
                  ))}
                </select>
              </div>

              <div className="reportes-pro-field">
                <label>Sede</label>
                <select value={sedeId} onChange={(e) => setSedeId(e.target.value)}>
                  <option value="">Todas las sedes</option>
                  {sedes.map((sede) => (
                    <option key={sede.id} value={sede.id}>
                      {sede.nombre}
                    </option>
                  ))}
                </select>
              </div>

              <div className="reportes-pro-field">
                <label>Estado</label>
                <select value={estado} onChange={(e) => setEstado(e.target.value)}>
                  <option value="">Todos los estados</option>
                  {estados.map((item) => (
                    <option key={item} value={item}>
                      {item}
                    </option>
                  ))}
                </select>
              </div>

              <div className="reportes-pro-field">
                <label>Fecha inicio</label>
                <input
                  type="date"
                  value={fechaInicio}
                  onChange={(e) => setFechaInicio(e.target.value)}
                />
              </div>

              <div className="reportes-pro-field">
                <label>Fecha fin</label>
                <input
                  type="date"
                  value={fechaFin}
                  onChange={(e) => setFechaFin(e.target.value)}
                />
              </div>
            </div>

            <div className="reportes-pro-actions">
              <button className="btn-pro primary" onClick={cargarReporte}>
                <Search size={18} />
                Consultar
              </button>

              <button className="btn-pro secondary" onClick={limpiarFiltros}>
                <RefreshCcw size={18} />
                Limpiar
              </button>

              <button className="btn-pro excel" onClick={() => descargarArchivo("excel")}>
                <FileSpreadsheet size={18} />
                Excel
              </button>

              <button className="btn-pro pdf" onClick={() => descargarArchivo("pdf")}>
                <Download size={18} />
                PDF
              </button>
            </div>
          </div>

          <div className="reportes-pro-table-card">
            <div className="reportes-pro-table-header">
              <div>
                <h2>Vista previa del reporte</h2>
                <p>{items.length} registros encontrados</p>
              </div>
            </div>

            <div className="reportes-pro-table-wrapper">
              <table className="reportes-pro-table">
                <thead>
                  <tr>
                    <th>Empresa</th>
                    <th>Sede</th>
                    <th>Equipo</th>
                    <th>Técnico</th>
                    <th>Tipo</th>
                    <th>Estado</th>
                    <th>Programado</th>
                    <th>Costo</th>
                  </tr>
                </thead>

                <tbody>
                  {loading ? (
                    <tr>
                      <td colSpan="8" className="empty-row">
                        Cargando reporte...
                      </td>
                    </tr>
                  ) : itemsPaginados.length === 0 ? (
                    <tr>
                      <td colSpan="8" className="empty-row empty-row-pro">
                        <Inbox size={38} />
                        <span>No hay registros con los filtros seleccionados.</span>
                      </td>
                    </tr>
                  ) : (
                    itemsPaginados.map((item) => (
                      <tr key={item.id}>
                        <td>{item.empresa}</td>
                        <td>{item.sede}</td>
                        <td>
                          <strong>{item.equipo}</strong>
                          <span>{item.codigo_inventario}</span>
                        </td>
                        <td>{item.tecnico}</td>
                        <td>{item.tipo}</td>
                        <td>
                          <span className={`estado-badge estado-${item.estado}`}>
                            {item.estado}
                          </span>
                        </td>
                        <td>{item.fecha_programada || "Sin fecha"}</td>
                        <td>${item.costo || "0"}</td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>

            <div className="reportes-pagination">
              <div className="reportes-pagination-info">
                Mostrando {inicioRegistro} a {finRegistro} de {items.length} registros
              </div>

              <div className="reportes-pagination-controls">
                <label>Filas por página:</label>

                <select
                  value={filasPorPagina}
                  onChange={(e) => setFilasPorPagina(Number(e.target.value))}
                >
                  <option value={5}>5</option>
                  <option value={10}>10</option>
                  <option value={20}>20</option>
                  <option value={50}>50</option>
                </select>

                <button onClick={irPrimeraPagina} disabled={paginaActual === 1}>
                  <ChevronsLeft size={18} />
                </button>

                <button onClick={irPaginaAnterior} disabled={paginaActual === 1}>
                  <ChevronLeft size={18} />
                </button>

                <button className="active-page">{paginaActual}</button>

                <button onClick={irPaginaSiguiente} disabled={paginaActual === totalPaginas}>
                  <ChevronRight size={18} />
                </button>

                <button onClick={irUltimaPagina} disabled={paginaActual === totalPaginas}>
                  <ChevronsRight size={18} />
                </button>
              </div>
            </div>
          </div>
        </section>
      </main>
    </div>
  );
}
