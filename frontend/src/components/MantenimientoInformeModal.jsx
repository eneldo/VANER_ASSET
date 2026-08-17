import { Download, FileSpreadsheet, Printer, X } from "lucide-react";
import API from "../api/axios";
import { isImageEvidence, isPdfEvidence } from "../utils/evidenciaUtils";
import "../styles/mantenimientoInforme.css";

const API_BASE = import.meta.env.VITE_API_URL || API?.defaults?.baseURL || window.location.origin;

function fileUrl(url) {
  if (!url) return "#";
  if (/^(https?:|blob:)/i.test(url)) return url;
  const base = String(API_BASE).replace(/\/$/, "");
  return url.startsWith("/") ? `${base}${url}` : `${base}/${url}`;
}

function formatDate(value) {
  if (!value) return "No registrada";
  const parsed = new Date(value);
  return Number.isNaN(parsed.getTime()) ? value : parsed.toLocaleString("es-CO");
}

export default function MantenimientoInformeModal({ detalle, onClose, onDownloadExcel, onDownloadPdf }) {
  if (!detalle) return null;

  const evidencias = detalle.evidencias || [];

  return (
    <div className="maintenance-report-overlay">
      <article className="maintenance-report-document">
        <header className="maintenance-report-toolbar no-print">
          <div>
            <strong>Informe del mantenimiento</strong>
            <span>OT {detalle.id}</span>
          </div>
          <div className="maintenance-report-actions">
            <button type="button" onClick={onDownloadExcel}><FileSpreadsheet size={16} /> Excel</button>
            <button type="button" onClick={onDownloadPdf}><Download size={16} /> PDF</button>
            <button type="button" onClick={() => window.print()}><Printer size={16} /> Imprimir</button>
            <button type="button" className="close" onClick={onClose}><X size={18} /> Cerrar</button>
          </div>
        </header>

        <div className="maintenance-report-sheet">
          <header className="maintenance-report-heading">
            <div className="maintenance-report-brand">SGA</div>
            <div>
              <p>SGAHolding · Gestión de activos</p>
              <h1>Informe completo de mantenimiento</h1>
              <span>Orden de trabajo {detalle.id}</span>
            </div>
            <span className={`maintenance-report-status status-${String(detalle.estado || "").toLowerCase()}`}>
              {detalle.estado || "SIN ESTADO"}
            </span>
          </header>

          <section className="maintenance-report-grid">
            <Info label="Empresa" value={detalle.empresa} />
            <Info label="Sede" value={detalle.sede} />
            <Info label="Equipo" value={detalle.equipo} />
            <Info label="Ubicación" value={detalle.ubicacion} />
            <Info label="Inventario / código" value={detalle.codigo_inventario} />
            <Info label="Serie" value={detalle.serie} />
            <Info label="Marca / modelo" value={`${detalle.marca || "—"} / ${detalle.modelo || "—"}`} />
            <Info label="Técnico" value={detalle.tecnico} />
            <Info label="Tipo de mantenimiento" value={detalle.tipo} />
            <Info label="Fecha programada" value={formatDate(detalle.fecha_programada)} />
            <Info label="Fecha de inicio" value={formatDate(detalle.fecha_inicio)} />
            <Info label="Fecha de finalización" value={formatDate(detalle.fecha_fin)} />
          </section>

          <section className="maintenance-report-section">
            <h2>Trabajo realizado al equipo</h2>
            <div className="maintenance-report-execution">
              <TextBlock label="Estado inicial" value={detalle.estado_inicial} />
              <TextBlock label="Acciones realizadas" value={detalle.acciones_realizadas} />
              <TextBlock label="Resultado final" value={detalle.resultado_final} />
              <TextBlock label="Observaciones" value={detalle.observaciones} />
            </div>
          </section>

          <section className="maintenance-report-section">
            <h2>Repuestos utilizados</h2>
            {detalle.repuestos?.length ? (
              <table className="maintenance-report-table">
                <thead><tr><th>Descripción</th><th>Referencia</th><th>Cantidad</th><th>Unidad</th></tr></thead>
                <tbody>{detalle.repuestos.map((item, index) => (
                  <tr key={`${item.descripcion}-${index}`}><td>{item.descripcion}</td><td>{item.referencia || "—"}</td><td>{item.cantidad}</td><td>{item.unidad}</td></tr>
                ))}</tbody>
              </table>
            ) : <p className="maintenance-report-empty">No se registraron repuestos.</p>}
          </section>

          <section className="maintenance-report-section">
            <h2>Incidencias encontradas</h2>
            {detalle.incidencias?.length ? (
              <table className="maintenance-report-table">
                <thead><tr><th>Tipo</th><th>Severidad</th><th>Descripción</th><th>Estado</th></tr></thead>
                <tbody>{detalle.incidencias.map((item, index) => (
                  <tr key={`${item.descripcion}-${index}`}><td>{item.tipo}</td><td>{item.severidad}</td><td>{item.descripcion}</td><td>{item.resuelta ? "Resuelta" : "Pendiente"}</td></tr>
                ))}</tbody>
              </table>
            ) : <p className="maintenance-report-empty">No se registraron incidencias.</p>}
          </section>

          <section className="maintenance-report-section evidence-section">
            <h2>Evidencias fotográficas</h2>
            <p className="maintenance-report-evidence-summary">Antes, proceso y resultado final del mantenimiento.</p>
            <div className="maintenance-report-evidence-grid">
              {evidencias.map((evidencia) => {
                const url = fileUrl(evidencia.archivo_url);
                return (
                  <figure key={evidencia.id} className="maintenance-report-evidence">
                    {isImageEvidence(evidencia) ? (
                      <img src={url} alt={`${evidencia.tipo}: ${evidencia.descripcion || "Evidencia"}`} />
                    ) : isPdfEvidence(evidencia) ? (
                      <a href={url} target="_blank" rel="noreferrer">Abrir evidencia PDF</a>
                    ) : (
                      <span>Archivo adjunto</span>
                    )}
                    <figcaption>
                      <strong>{evidencia.tipo || "SOPORTE"}</strong>
                      <span>{evidencia.descripcion || "Sin descripción"}</span>
                      <small>{evidencia.nombre_original || "Archivo"}</small>
                    </figcaption>
                  </figure>
                );
              })}
              {!evidencias.length && <p className="maintenance-report-empty">No existen evidencias asociadas.</p>}
            </div>
          </section>

          <footer className="maintenance-report-footer">
            Documento generado desde SGAHolding · {new Date().toLocaleString("es-CO")}
          </footer>
        </div>
      </article>
    </div>
  );
}

function Info({ label, value }) {
  return <div className="maintenance-report-info"><span>{label}</span><strong>{value || "No registrado"}</strong></div>;
}

function TextBlock({ label, value }) {
  return <div className="maintenance-report-text"><strong>{label}</strong><p>{value || "No registrado"}</p></div>;
}
