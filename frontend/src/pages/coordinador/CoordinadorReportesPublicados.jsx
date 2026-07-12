import { useEffect, useState } from "react";
import { CheckCircle, Download, FilePlus2, RefreshCw } from "lucide-react";
import API from "../../api/axios";

const hoy = new Date();
const inicioMes = `${hoy.getFullYear()}-${String(hoy.getMonth() + 1).padStart(2, "0")}-01`;
const finMes = new Date(hoy.getFullYear(), hoy.getMonth() + 1, 0).toISOString().slice(0, 10);

export default function CoordinadorReportesPublicados() {
  const [reportes, setReportes] = useState([]);
  const [ots, setOts] = useState([]);
  const [otId, setOtId] = useState("");
  const [inicio, setInicio] = useState(inicioMes);
  const [fin, setFin] = useState(finMes);
  const [ocupado, setOcupado] = useState(false);

  const cargar = async () => {
    const [reportesRes, otsRes] = await Promise.all([
      API.get("/reportes-publicados/"),
      API.get("/coordinador/informes"),
    ]);
    setReportes(reportesRes.data || []);
    setOts((otsRes.data || []).filter((ot) => String(ot.estado).toUpperCase() === "FINALIZADO"));
  };

  useEffect(() => {
    const timer = window.setTimeout(() => cargar().catch(console.error), 0);
    return () => window.clearTimeout(timer);
  }, []);

  const ejecutar = async (accion) => {
    setOcupado(true);
    try {
      await accion();
      await cargar();
    } catch (error) {
      alert(error.response?.data?.detail || "No fue posible completar la operación.");
    } finally {
      setOcupado(false);
    }
  };

  const descargar = async (reporte) => {
    const res = await API.get(reporte.descarga_url, { responseType: "blob" });
    const url = URL.createObjectURL(res.data);
    const link = document.createElement("a");
    link.href = url; link.download = `${reporte.titulo}.pdf`; link.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="coord-page">
      <div className="coord-hero">
        <div><span className="coord-eyebrow">PUBLICACIÓN CONTROLADA</span><h2>Reportes PDF</h2><p>Genera, revisa y aprueba documentos antes de entregarlos al cliente.</p></div>
        <button className="coord-btn secondary" onClick={() => cargar()}><RefreshCw size={17} /> Actualizar</button>
      </div>

      <div className="coord-report-builder">
        <section className="coord-card">
          <h3>Reporte específico por OT</h3>
          <select value={otId} onChange={(e) => setOtId(e.target.value)}>
            <option value="">Selecciona una OT finalizada</option>
            {ots.map((ot) => <option key={ot.id} value={ot.id}>{ot.equipo_nombre || "Equipo"} · {new Date(ot.fecha_programada).toLocaleDateString()}</option>)}
          </select>
          <button className="coord-btn primary" disabled={!otId || ocupado} onClick={() => ejecutar(() => API.post("/reportes-publicados/ot", { mantenimiento_id: otId }))}><FilePlus2 size={16} /> Generar borrador</button>
        </section>

        <section className="coord-card">
          <h3>Consolidado mensual</h3>
          <div className="coord-date-row"><input type="date" value={inicio} onChange={(e) => setInicio(e.target.value)} /><input type="date" value={fin} onChange={(e) => setFin(e.target.value)} /></div>
          <button className="coord-btn primary" disabled={!inicio || !fin || ocupado} onClick={() => ejecutar(() => API.post("/reportes-publicados/mensual", { periodo_inicio: inicio, periodo_fin: fin }))}><FilePlus2 size={16} /> Generar consolidado</button>
        </section>
      </div>

      <section className="coord-card">
        <div className="coord-card-header"><div><h3>Documentos generados</h3><p>{reportes.length} reportes</p></div></div>
        <div className="coord-table-wrap"><table className="coord-table"><thead><tr><th>Título</th><th>Tipo</th><th>Estado</th><th>Fecha</th><th>Acciones</th></tr></thead>
          <tbody>{reportes.map((reporte) => <tr key={reporte.id}><td>{reporte.titulo}</td><td>{reporte.tipo}</td><td><span className={`coord-badge ${reporte.estado.toLowerCase()}`}>{reporte.estado}</span></td><td>{new Date(reporte.created_at).toLocaleString()}</td><td><div className="coord-inline-actions"><button onClick={() => descargar(reporte)}><Download size={15} /> Revisar</button>{reporte.estado === "BORRADOR" && <button className="approve" disabled={ocupado} onClick={() => ejecutar(() => API.post(`/reportes-publicados/${reporte.id}/aprobar`))}><CheckCircle size={15} /> Aprobar y publicar</button>}</div></td></tr>)}</tbody>
        </table></div>
      </section>
    </div>
  );
}
