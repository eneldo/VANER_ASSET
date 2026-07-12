// ============================================================
// Página: Exportaciones PRO
// Proyecto: SGA PRO - Fase 27
// Archivo: frontend/src/pages/admin/ExportacionesPage.jsx
//
// Función:
// - Permite descargar reportes en Excel y PDF.
// - Incluye filtros por empresa, sede, estado y fechas.
// - Usa Axios centralizado para respetar token si existe.
// ============================================================

import { useEffect, useMemo, useState } from "react";
import {
  Download,
  FileSpreadsheet,
  FileText,
  RefreshCcw,
  Filter,
  Building2,
  MapPin,
  Wrench,
  MonitorCog,
  ShieldCheck,
  BarChart3,
} from "lucide-react";

import API from "../../api/axios";
import "../../styles/exportaciones.css";

const REPORTES = [
  {
    key: "reporte-general",
    titulo: "Reporte general del sistema",
    descripcion: "Indicadores globales de empresas, sedes, equipos, mantenimientos, técnicos y auditoría.",
    icono: BarChart3,
    usaFiltros: false,
  },
  {
    key: "equipos",
    titulo: "Reporte de equipos",
    descripcion: "Inventario técnico filtrado por empresa, sede y estado del equipo.",
    icono: MonitorCog,
    usaFiltros: true,
    tipoEstado: "equipo",
  },
  {
    key: "mantenimientos",
    titulo: "Reporte de mantenimientos",
    descripcion: "Listado de mantenimientos con técnico, estado, fechas, costo y observaciones.",
    icono: Wrench,
    usaFiltros: true,
    tipoEstado: "mantenimiento",
    usaFechas: true,
  },
  {
    key: "auditoria",
    titulo: "Reporte de auditoría",
    descripcion: "Eventos del sistema, cambios relevantes, usuario, módulo, acción e IP de origen.",
    icono: ShieldCheck,
    usaFiltros: false,
    usaFechas: true,
  },
];

export default function ExportacionesPage() {
  const [catalogos, setCatalogos] = useState({
    empresas: [],
    sedes: [],
    estados_mantenimiento: [],
    estados_equipo: [],
  });

  const [filtros, setFiltros] = useState({
    empresa_id: "",
    sede_id: "",
    estado: "",
    fecha_inicio: "",
    fecha_fin: "",
  });

  const [descargando, setDescargando] = useState("");
  const [mensaje, setMensaje] = useState("");

  // ========================================================
  // CARGA DE CATÁLOGOS
  // ========================================================
  useEffect(() => {
    cargarCatalogos();
  }, []);

  async function cargarCatalogos() {
    try {
      const { data } = await API.get("/exportaciones/catalogos");
      setCatalogos(data);
    } catch (error) {
      console.error("Error cargando catálogos de exportación:", error);
      setMensaje("No fue posible cargar los catálogos. Verifica que el backend esté activo.");
    }
  };

  // ========================================================
  // SEDES FILTRADAS POR EMPRESA
  // ========================================================
  const sedesFiltradas = useMemo(() => {
    if (!filtros.empresa_id) return catalogos.sedes;
    return catalogos.sedes.filter((sede) => sede.empresa_id === filtros.empresa_id);
  }, [catalogos.sedes, filtros.empresa_id]);

  const actualizarFiltro = (campo, valor) => {
    setFiltros((prev) => ({
      ...prev,
      [campo]: valor,
      ...(campo === "empresa_id" ? { sede_id: "" } : {}),
    }));
  };

  const limpiarFiltros = () => {
    setFiltros({
      empresa_id: "",
      sede_id: "",
      estado: "",
      fecha_inicio: "",
      fecha_fin: "",
    });
  };

  // ========================================================
  // DESCARGA DE ARCHIVOS
  // ========================================================
  const descargarReporte = async (reporte, formato) => {
    const claveDescarga = `${reporte.key}-${formato}`;
    setDescargando(claveDescarga);
    setMensaje("");

    try {
      const params = {};

      // Reportes de equipos/mantenimientos usan empresa/sede/estado.
      if (reporte.usaFiltros) {
        if (filtros.empresa_id) params.empresa_id = filtros.empresa_id;
        if (filtros.sede_id) params.sede_id = filtros.sede_id;
        if (filtros.estado) params.estado = filtros.estado;
      }

      // Mantenimientos y auditoría usan rango de fechas.
      if (reporte.usaFechas) {
        if (filtros.fecha_inicio) params.fecha_inicio = filtros.fecha_inicio;
        if (filtros.fecha_fin) params.fecha_fin = filtros.fecha_fin;
      }

      const { data, headers } = await API.get(`/exportaciones/${reporte.key}/${formato}`, {
        params,
        responseType: "blob",
      });

      const extension = formato === "excel" ? "xlsx" : "pdf";
      const contentDisposition = headers["content-disposition"] || "";
      const match = contentDisposition.match(/filename="?([^";]+)"?/i);
      const nombreArchivo = match?.[1] || `${reporte.key}.${extension}`;

      const url = window.URL.createObjectURL(new Blob([data]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", nombreArchivo);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);

      setMensaje(`Archivo generado correctamente: ${nombreArchivo}`);
    } catch (error) {
      console.error("Error descargando reporte:", error);
      setMensaje("No fue posible generar el archivo. Revisa consola/backend para más detalles.");
    } finally {
      setDescargando("");
    }
  };

  const estadosDisponibles = (reporte) => {
    if (reporte.tipoEstado === "equipo") return catalogos.estados_equipo || [];
    if (reporte.tipoEstado === "mantenimiento") return catalogos.estados_mantenimiento || [];
    return [];
  };

  return (
    <div className="exportaciones-page">
      {/* =====================================================
          ENCABEZADO
      ===================================================== */}
      <header className="exportaciones-header">
        <div>
          <span className="exportaciones-kicker">FASE 27 · EXPORTACIÓN PRO</span>
          <h1>Exportaciones Excel / PDF</h1>
          <p>
            Descarga reportes del sistema SGA PRO con filtros por empresa, sede,
            estado y fechas según el tipo de reporte.
          </p>
        </div>

        <button className="btn-outline" onClick={cargarCatalogos} type="button">
          <RefreshCcw size={18} />
          Actualizar catálogos
        </button>
      </header>

      {/* =====================================================
          FILTROS GLOBALES
      ===================================================== */}
      <section className="exportaciones-filtros">
        <div className="filtros-title">
          <Filter size={19} />
          <div>
            <h2>Filtros de exportación</h2>
            <p>Se aplican automáticamente a los reportes compatibles.</p>
          </div>
        </div>

        <div className="filtros-grid">
          <label>
            <span><Building2 size={15} /> Empresa</span>
            <select value={filtros.empresa_id} onChange={(e) => actualizarFiltro("empresa_id", e.target.value)}>
              <option value="">Todas las empresas</option>
              {catalogos.empresas.map((empresa) => (
                <option key={empresa.id} value={empresa.id}>{empresa.nombre}</option>
              ))}
            </select>
          </label>

          <label>
            <span><MapPin size={15} /> Sede</span>
            <select value={filtros.sede_id} onChange={(e) => actualizarFiltro("sede_id", e.target.value)}>
              <option value="">Todas las sedes</option>
              {sedesFiltradas.map((sede) => (
                <option key={sede.id} value={sede.id}>{sede.nombre}</option>
              ))}
            </select>
          </label>

          <label>
            <span>Estado</span>
            <input
              value={filtros.estado}
              onChange={(e) => actualizarFiltro("estado", e.target.value)}
              placeholder="Ej: PROGRAMADO / OPERATIVO"
            />
          </label>

          <label>
            <span>Fecha inicio</span>
            <input type="date" value={filtros.fecha_inicio} onChange={(e) => actualizarFiltro("fecha_inicio", e.target.value)} />
          </label>

          <label>
            <span>Fecha fin</span>
            <input type="date" value={filtros.fecha_fin} onChange={(e) => actualizarFiltro("fecha_fin", e.target.value)} />
          </label>

          <button className="btn-clean" type="button" onClick={limpiarFiltros}>
            Limpiar filtros
          </button>
        </div>
      </section>

      {mensaje && <div className="exportaciones-message">{mensaje}</div>}

      {/* =====================================================
          TARJETAS DE REPORTES
      ===================================================== */}
      <section className="exportaciones-grid">
        {REPORTES.map((reporte) => {
          const Icono = reporte.icono;
          const estados = estadosDisponibles(reporte);

          return (
            <article className="exportacion-card" key={reporte.key}>
              <div className="exportacion-card-head">
                <div className="exportacion-icon"><Icono size={24} /></div>
                <div>
                  <h2>{reporte.titulo}</h2>
                  <p>{reporte.descripcion}</p>
                </div>
              </div>

              {estados.length > 0 && (
                <div className="estado-sugerencias">
                  <strong>Estados detectados:</strong>
                  <div>
                    {estados.slice(0, 6).map((estado) => (
                      <button key={estado} type="button" onClick={() => actualizarFiltro("estado", estado)}>
                        {estado}
                      </button>
                    ))}
                  </div>
                </div>
              )}

              <div className="exportacion-actions">
                <button
                  className="btn-excel"
                  onClick={() => descargarReporte(reporte, "excel")}
                  disabled={descargando === `${reporte.key}-excel`}
                  type="button"
                >
                  <FileSpreadsheet size={18} />
                  {descargando === `${reporte.key}-excel` ? "Generando..." : "Excel"}
                </button>

                <button
                  className="btn-pdf"
                  onClick={() => descargarReporte(reporte, "pdf")}
                  disabled={descargando === `${reporte.key}-pdf`}
                  type="button"
                >
                  <FileText size={18} />
                  {descargando === `${reporte.key}-pdf` ? "Generando..." : "PDF"}
                </button>
              </div>

              <div className="exportacion-footer">
                <Download size={15} />
                Archivo generado desde backend FastAPI.
              </div>
            </article>
          );
        })}
      </section>
    </div>
  );
}
