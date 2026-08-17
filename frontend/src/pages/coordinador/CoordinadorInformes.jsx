import { useEffect, useMemo, useState } from "react";
import { Download, Eye, FileSpreadsheet, RefreshCw, Search } from "lucide-react";
import API from "../../api/axios";
import MantenimientoInformeModal from "../../components/MantenimientoInformeModal";
import "../../styles/coordinador.css";

function formatDate(value) {
  if (!value) return "Sin fecha";
  const parsed = new Date(value);
  return Number.isNaN(parsed.getTime()) ? value : parsed.toLocaleDateString("es-CO");
}

export default function CoordinadorInformes() {
  const [mantenimientos, setMantenimientos] = useState([]);
  const [sedes, setSedes] = useState([]);
  const [busqueda, setBusqueda] = useState("");
  const [sedeId, setSedeId] = useState("");
  const [estado, setEstado] = useState("");
  const [fechaInicio, setFechaInicio] = useState("");
  const [fechaFin, setFechaFin] = useState("");
  const [seleccionadoId, setSeleccionadoId] = useState("");
  const [detalle, setDetalle] = useState(null);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState("");

  const queryParams = useMemo(() => {
    const params = new URLSearchParams();
    if (sedeId) params.set("sede_id", sedeId);
    if (estado) params.set("estado", estado);
    if (fechaInicio) params.set("fecha_inicio", fechaInicio);
    if (fechaFin) params.set("fecha_fin", fechaFin);
    return params.toString();
  }, [estado, fechaFin, fechaInicio, sedeId]);

  useEffect(() => {
    const timer = window.setTimeout(async () => {
      try {
        const [sedesRes, mantenimientosRes] = await Promise.all([
          API.get("/reportes/filtros/sedes"),
          API.get("/reportes/mantenimientos"),
        ]);
        setSedes(sedesRes.data || []);
        setMantenimientos(mantenimientosRes.data?.items || []);
      } catch (requestError) {
        console.error("Error cargando informes del coordinador:", requestError);
        setError("No se pudieron cargar los reportes de mantenimiento.");
      } finally {
        setCargando(false);
      }
    }, 0);
    return () => window.clearTimeout(timer);
  }, []);

  const consultar = async () => {
    try {
      setCargando(true);
      setError("");
      const res = await API.get(`/reportes/mantenimientos${queryParams ? `?${queryParams}` : ""}`);
      setMantenimientos(res.data?.items || []);
    } catch (requestError) {
      console.error("Error consultando informes:", requestError);
      setError(requestError.response?.data?.detail || "No se pudieron consultar los reportes.");
    } finally {
      setCargando(false);
    }
  };

  const filtrados = useMemo(() => {
    const texto = busqueda.trim().toLowerCase();
    if (!texto) return mantenimientos;
    return mantenimientos.filter((item) => `${item.equipo} ${item.codigo_inventario} ${item.ubicacion} ${item.tecnico} ${item.tipo} ${item.estado} ${item.acciones_realizadas} ${item.resultado_final}`.toLowerCase().includes(texto));
  }, [busqueda, mantenimientos]);

  const descargar = async (tipo, mantenimientoId = null) => {
    try {
      const endpoint = mantenimientoId
        ? `/reportes/mantenimientos/${mantenimientoId}/${tipo}`
        : `/reportes/mantenimientos/${tipo}${queryParams ? `?${queryParams}` : ""}`;
      const res = await API.get(endpoint, { responseType: "blob" });
      const url = URL.createObjectURL(res.data);
      const link = document.createElement("a");
      link.href = url;
      link.download = mantenimientoId
        ? `informe_mantenimiento_${mantenimientoId}.${tipo === "excel" ? "xlsx" : "pdf"}`
        : `reporte_mantenimientos_coordinador.${tipo === "excel" ? "xlsx" : "pdf"}`;
      document.body.appendChild(link);
      link.click();
      link.remove();
      URL.revokeObjectURL(url);
    } catch (requestError) {
      console.error("Error exportando reporte:", requestError);
      alert(requestError.response?.data?.detail || "No se pudo exportar el reporte.");
    }
  };

  const abrirInforme = async (mantenimientoId) => {
    try {
      setSeleccionadoId(String(mantenimientoId));
      const res = await API.get(`/reportes/mantenimientos/${mantenimientoId}`);
      setDetalle(res.data);
    } catch (requestError) {
      console.error("Error cargando informe:", requestError);
      alert(requestError.response?.data?.detail || "No se pudo cargar el informe completo.");
    }
  };

  return (
    <div className="coord-page">
      <div className="coord-hero">
        <div>
          <span className="coord-eyebrow">REPORTES · COORDINADOR</span>
          <h2>Informes completos de mantenimiento</h2>
          <p>Consulta, imprime y exporta las intervenciones y sus evidencias fotográficas.</p>
        </div>
        <div className="coord-actions">
          <button className="coord-btn secondary" onClick={consultar}><RefreshCw size={17} /> Actualizar</button>
          <button className="coord-btn secondary" onClick={() => descargar("excel")}><FileSpreadsheet size={17} /> Excel</button>
          <button className="coord-btn primary" onClick={() => descargar("pdf")}><Download size={17} /> PDF</button>
        </div>
      </div>

      {error && <div className="coord-alert error">{error}</div>}

      <section className="coord-card">
        <div className="coord-filters">
          <div className="coord-search">
            <Search size={18} />
            <input value={busqueda} onChange={(event) => setBusqueda(event.target.value)} placeholder="Buscar equipo, inventario, ubicación, técnico o resultado..." />
          </div>
          <select value={sedeId} onChange={(event) => setSedeId(event.target.value)}>
            <option value="">Todas las sedes</option>
            {sedes.map((sede) => <option key={sede.id} value={sede.id}>{sede.nombre}</option>)}
          </select>
          <select value={estado} onChange={(event) => setEstado(event.target.value)}>
            <option value="">Todos los estados</option>
            {["PROGRAMADO", "ASIGNADO", "EN_PROCESO", "PAUSADO", "FINALIZADO", "ANULADO"].map((item) => <option key={item}>{item}</option>)}
          </select>
          <input type="date" value={fechaInicio} onChange={(event) => setFechaInicio(event.target.value)} />
          <input type="date" value={fechaFin} onChange={(event) => setFechaFin(event.target.value)} />
          <button className="coord-btn primary" onClick={consultar}><Search size={16} /> Consultar</button>
        </div>
      </section>

      <section className="coord-card">
        <div className="coord-card-header"><div><h3>Mantenimientos</h3><p>{filtrados.length} registros disponibles</p></div></div>
        <div className="coord-table-wrap">
          <table className="coord-table">
            <thead><tr><th>Equipo</th><th>Sede / ubicación</th><th>Técnico</th><th>Tipo</th><th>Estado</th><th>Fecha</th><th>Evidencias</th><th>Acciones</th></tr></thead>
            <tbody>
              {cargando ? (
                <tr><td colSpan="8">Cargando reportes...</td></tr>
              ) : filtrados.length ? filtrados.map((item) => (
                <tr key={item.id} className={String(seleccionadoId) === String(item.id) ? "selected-report-row" : ""}>
                  <td><strong>{item.equipo}</strong><span>{item.codigo_inventario || "Sin inventario"}</span></td>
                  <td><strong>{item.sede}</strong><span>{item.ubicacion || "Sin ubicación"}</span></td>
                  <td>{item.tecnico}</td>
                  <td>{item.tipo}</td>
                  <td><span className={`coord-badge ${String(item.estado || "").toLowerCase()}`}>{item.estado}</span></td>
                  <td>{formatDate(item.fecha_programada)}</td>
                  <td>{item.evidencias_total}</td>
                  <td><button className="coord-btn secondary" onClick={() => abrirInforme(item.id)}><Eye size={15} /> Ver informe</button></td>
                </tr>
              )) : (
                <tr><td colSpan="8">No hay mantenimientos con los filtros seleccionados.</td></tr>
              )}
            </tbody>
          </table>
        </div>
      </section>

      {detalle && (
        <MantenimientoInformeModal
          detalle={detalle}
          onClose={() => setDetalle(null)}
          onDownloadExcel={() => descargar("excel", detalle.id)}
          onDownloadPdf={() => descargar("pdf", detalle.id)}
        />
      )}
    </div>
  );
}
