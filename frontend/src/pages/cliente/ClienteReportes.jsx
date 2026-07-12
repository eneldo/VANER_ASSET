import { useEffect, useState } from "react";
import { Download, FileCheck2, RefreshCcw } from "lucide-react";
import API from "../../api/axios";

export default function ClienteReportes() {
  const [reportes, setReportes] = useState([]);
  const [loading, setLoading] = useState(true);

  const cargar = async () => {
    setLoading(true);
    try {
      const res = await API.get("/reportes-publicados/");
      setReportes(res.data || []);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const timer = window.setTimeout(() => cargar().catch(console.error), 0);
    return () => window.clearTimeout(timer);
  }, []);

  const descargar = async (reporte) => {
    const res = await API.get(reporte.descarga_url, { responseType: "blob" });
    const url = URL.createObjectURL(res.data);
    const link = document.createElement("a");
    link.href = url; link.download = `${reporte.titulo}.pdf`; link.click();
    URL.revokeObjectURL(url);
  };

  return (
    <>
      <div className="cliente-header cliente-header-flex"><div><h1>Reportes aprobados</h1><p>Documentos oficiales publicados por coordinación.</p></div><button className="cliente-btn-secondary" onClick={cargar} disabled={loading}><RefreshCcw size={16} /> Actualizar</button></div>
      <section className="cliente-panel cliente-reports-grid">
        {reportes.length === 0 && <div className="cliente-empty-live">No hay reportes aprobados disponibles.</div>}
        {reportes.map((reporte) => (
          <article key={reporte.id} className="cliente-report-card">
            <FileCheck2 size={28} /><div><strong>{reporte.titulo}</strong><p>{reporte.tipo === "MENSUAL" ? `${reporte.periodo_inicio} a ${reporte.periodo_fin}` : "Reporte por equipo / OT"}</p><small>Aprobado {reporte.aprobado_at ? new Date(reporte.aprobado_at).toLocaleString() : "por coordinación"}</small></div>
            <button className="cliente-btn" onClick={() => descargar(reporte)}><Download size={16} /> Descargar PDF</button>
          </article>
        ))}
      </section>
    </>
  );
}
