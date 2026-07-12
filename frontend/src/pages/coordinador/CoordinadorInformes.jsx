/*
===========================================================
FASE COORDINADOR PRO — INFORMES
Archivo: frontend/src/pages/coordinador/CoordinadorInformes.jsx
===========================================================
*/

import { useEffect, useMemo, useState } from "react";
import API from "../../api/axios";
import { FileBarChart, Printer, RefreshCw, Download, Search } from "lucide-react";
import "../../styles/coordinador.css";

const fmtFecha = (fecha) => {
  if (!fecha) return "Sin fecha";
  try {
    return new Date(fecha).toLocaleDateString("es-CO");
  } catch {
    return "Sin fecha";
  }
};

export default function CoordinadorInformes() {
  const [mantenimientos, setMantenimientos] = useState([]);
  const [catalogos, setCatalogos] = useState({ equipos: [], tecnicos: [] });
  const [equipoFiltro, setEquipoFiltro] = useState("");
  const [estadoFiltro, setEstadoFiltro] = useState("");
  const [busqueda, setBusqueda] = useState("");
  const [, setCargando] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    cargarInformes();
  }, []);

  async function cargarInformes() {
    try {
      setCargando(true);
      setError("");

      const [resMantenimientos, resCatalogos] = await Promise.all([
        API.get("/coordinador/informes"),
        API.get("/coordinador/catalogos"),
      ]);

      setMantenimientos(resMantenimientos.data || []);
      setCatalogos(resCatalogos.data || { equipos: [], tecnicos: [] });
    } catch (err) {
      console.error("Error informes coordinador:", err);
      setError("No se pudieron cargar los informes.");
    } finally {
      setCargando(false);
    }
  };

  const mantenimientosFiltrados = useMemo(() => {
    const texto = busqueda.toLowerCase();

    return mantenimientos.filter((m) => {
      const coincideTexto = `${m.equipo_nombre || ""} ${m.tecnico_nombre || ""} ${m.estado || ""} ${m.tipo || ""} ${m.observaciones || ""}`
        .toLowerCase()
        .includes(texto);

      const coincideEquipo = equipoFiltro ? String(m.equipo_id) === String(equipoFiltro) : true;
      const coincideEstado = estadoFiltro ? String(m.estado) === String(estadoFiltro) : true;

      return coincideTexto && coincideEquipo && coincideEstado;
    });
  }, [mantenimientos, busqueda, equipoFiltro, estadoFiltro]);

  const resumen = useMemo(() => {
    const porEstado = {};
    const porTipo = {};
    mantenimientosFiltrados.forEach((m) => {
      porEstado[m.estado || "SIN_ESTADO"] = (porEstado[m.estado || "SIN_ESTADO"] || 0) + 1;
      porTipo[m.tipo || "SIN_TIPO"] = (porTipo[m.tipo || "SIN_TIPO"] || 0) + 1;
    });

    return { porEstado, porTipo };
  }, [mantenimientosFiltrados]);

  const descargarCSV = () => {
    const encabezados = ["Equipo", "Técnico", "Tipo", "Estado", "Fecha programada", "Observaciones"];
    const filas = mantenimientosFiltrados.map((m) => [
      m.equipo_nombre || "",
      m.tecnico_nombre || "",
      m.tipo || "",
      m.estado || "",
      fmtFecha(m.fecha_programada),
      (m.observaciones || m.descripcion || "").replaceAll("\n", " "),
    ]);

    const csv = [encabezados, ...filas]
      .map((fila) => fila.map((valor) => `"${String(valor).replaceAll('"', '""')}"`).join(","))
      .join("\n");

    const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const enlace = document.createElement("a");
    enlace.href = url;
    enlace.download = "informe_coordinador_sga.csv";
    enlace.click();
    URL.revokeObjectURL(url);
  };

  const imprimir = () => window.print();

  return (
    <div className="coord-page">
      <div className="coord-hero">
        <div>
          <span className="coord-eyebrow">REPORTES · COORDINADOR</span>
          <h2>Reportes Operativos</h2>
          <p>Informe general o por equipo con exportación CSV e impresión PDF.</p>
        </div>

        <div className="coord-actions">
          <button className="coord-btn secondary" onClick={cargarInformes}>
            <RefreshCw size={17} />
            Actualizar
          </button>
          <button className="coord-btn secondary" onClick={descargarCSV}>
            <Download size={17} />
            CSV
          </button>
          <button className="coord-btn primary" onClick={imprimir}>
            <Printer size={17} />
            Imprimir / PDF
          </button>
        </div>
      </div>

      {error && <div className="coord-alert error">{error}</div>}

      <div className="coord-filters">
        <div className="coord-search">
          <Search size={18} />
          <input
            type="text"
            placeholder="Buscar por equipo, técnico, estado, tipo u observación..."
            value={busqueda}
            onChange={(e) => setBusqueda(e.target.value)}
          />
        </div>

        <select value={equipoFiltro} onChange={(e) => setEquipoFiltro(e.target.value)}>
          <option value="">Todos los equipos</option>
          {catalogos.equipos?.map((equipo) => (
            <option key={equipo.id} value={equipo.id}>{equipo.nombre || equipo.codigo_inventario}</option>
          ))}
        </select>

        <select value={estadoFiltro} onChange={(e) => setEstadoFiltro(e.target.value)}>
          <option value="">Todos los estados</option>
          <option value="PROGRAMADO">PROGRAMADO</option>
          <option value="ASIGNADO">ASIGNADO</option>
          <option value="EN_PROCESO">EN_PROCESO</option>
          <option value="PAUSADO">PAUSADO</option>
          <option value="FINALIZADO">FINALIZADO</option>
          <option value="ANULADO">ANULADO</option>
        </select>
      </div>

      <div id="informe-coordinador-print">
        <div className="coord-report-header">
          <div>
            <h1>Informe Coordinador SGA PRO</h1>
            <p>Fecha de generación: {new Date().toLocaleString("es-CO")}</p>
          </div>
          <FileBarChart size={34} />
        </div>

        <div className="coord-kpi-grid mini">
          <div className="coord-kpi blue"><strong>{mantenimientosFiltrados.length}</strong><span>Total mantenimientos</span></div>
          <div className="coord-kpi green"><strong>{resumen.porEstado.FINALIZADO || 0}</strong><span>Finalizados</span></div>
          <div className="coord-kpi amber"><strong>{resumen.porEstado.PROGRAMADO || 0}</strong><span>Programados</span></div>
          <div className="coord-kpi indigo"><strong>{resumen.porEstado.EN_PROCESO || 0}</strong><span>En proceso</span></div>
        </div>

        <section className="coord-card">
          <div className="coord-card-header">
            <div>
              <h3>Detalle del informe</h3>
              <p>{mantenimientosFiltrados.length} registros encontrados.</p>
            </div>
          </div>

          <div className="coord-table-wrap">
            <table className="coord-table">
              <thead>
                <tr>
                  <th>Equipo</th>
                  <th>Técnico</th>
                  <th>Tipo</th>
                  <th>Estado</th>
                  <th>Fecha</th>
                  <th>Observaciones</th>
                </tr>
              </thead>
              <tbody>
                {mantenimientosFiltrados.length === 0 ? (
                  <tr>
                    <td colSpan="6" className="coord-empty">No hay datos para generar informe.</td>
                  </tr>
                ) : (
                  mantenimientosFiltrados.map((m) => (
                    <tr key={m.id}>
                      <td>{m.equipo_nombre || "Sin equipo"}</td>
                      <td>{m.tecnico_nombre || "Sin técnico"}</td>
                      <td>{m.tipo || "N/A"}</td>
                      <td><span className={`coord-badge ${String(m.estado || "").toLowerCase()}`}>{m.estado || "N/A"}</span></td>
                      <td>{fmtFecha(m.fecha_programada)}</td>
                      <td>{m.observaciones || m.descripcion || "Sin observaciones"}</td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </section>
      </div>
    </div>
  );
}
