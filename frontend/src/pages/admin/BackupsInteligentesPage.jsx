// ============================================================
// PÁGINA: Backups Inteligentes SaaS PRO
// Archivo: frontend/src/pages/admin/BackupsInteligentesPage.jsx
// Fase 34.2.2
// ============================================================

import { useEffect, useMemo, useState } from "react";
import { Archive, Database, Download, FolderArchive, RefreshCw, ShieldCheck, Trash2 } from "lucide-react";
import AdminLayout from "./AdminLayout";
import {
  ejecutarBackup,
  getBackupsStatus,
  limpiarBackups,
  listarBackups,
  urlDescargarBackup,
} from "../../api/backupsApi";
import "../../styles/backups-saas-pro.css";

const fmtBytes = (bytes = 0) => {
  if (!bytes) return "0 B";
  const units = ["B", "KB", "MB", "GB", "TB"];
  let size = bytes;
  let index = 0;
  while (size >= 1024 && index < units.length - 1) {
    size /= 1024;
    index += 1;
  }
  return `${size.toFixed(index === 0 ? 0 : 2)} ${units[index]}`;
};

const estadoClass = (estado) => `backup-status ${String(estado || "").toLowerCase()}`;

export default function BackupsInteligentesPage() {
  const [status, setStatus] = useState(null);
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(false);
  const [running, setRunning] = useState(false);
  const [mensaje, setMensaje] = useState("");
  const [opciones, setOpciones] = useState({ incluir_db: true, incluir_uploads: true, incluir_codigo: false });

  const totalExitosos = useMemo(() => items.filter((i) => i.estado === "EXITOSO").length, [items]);
  const totalErrores = useMemo(() => items.filter((i) => i.estado === "ERROR").length, [items]);

  const cargar = async () => {
    setLoading(true);
    setMensaje("");
    try {
      const [st, lista] = await Promise.all([getBackupsStatus(), listarBackups(50)]);
      setStatus(st);
      setItems(lista || []);
    } catch {
      setMensaje("No fue posible cargar backups inteligentes. Verifique backend y router.");
    } finally {
      setLoading(false);
    }
  };

  const crearBackup = async () => {
    setRunning(true);
    setMensaje("Generando backup, por favor espere...");
    try {
      await ejecutarBackup({ tipo: "MANUAL", creado_por: "admin", ...opciones });
      setMensaje("Backup generado correctamente.");
      await cargar();
    } catch (error) {
      setMensaje(error?.response?.data?.detail || "No fue posible generar el backup.");
    } finally {
      setRunning(false);
    }
  };

  const limpiar = async () => {
    if (!confirm("¿Desea limpiar backups antiguos según retención de 15 días?")) return;
    try {
      await limpiarBackups(15);
      await cargar();
      setMensaje("Limpieza ejecutada correctamente.");
    } catch {
      setMensaje("No fue posible limpiar backups.");
    }
  };

  useEffect(() => {
    const timer = window.setTimeout(() => cargar(), 0);
    return () => window.clearTimeout(timer);
  }, []);

  return (
    <AdminLayout>
      <main className="backup-page">
        <section className="backup-hero">
          <div>
            <span className="backup-eyebrow">FASE 34.2.2 · BACKUPS</span>
            <h1>Backups Inteligentes SaaS</h1>
            <p>Centro profesional para respaldar PostgreSQL, evidencias/uploads y paquetes ZIP descargables.</p>
          </div>
          <div className="backup-actions">
            <button className="backup-btn soft" onClick={cargar} disabled={loading}>
              <RefreshCw size={17} /> Actualizar
            </button>
            <button className="backup-btn primary" onClick={crearBackup} disabled={running}>
              <Archive size={17} /> {running ? "Generando..." : "Crear backup"}
            </button>
          </div>
        </section>

        {mensaje && <div className="backup-alert">{mensaje}</div>}

        <section className="backup-kpis">
          <article><Database /><small>Total backups</small><strong>{status?.total_backups ?? items.length}</strong></article>
          <article><ShieldCheck /><small>Exitosos</small><strong>{totalExitosos}</strong></article>
          <article><FolderArchive /><small>Peso total</small><strong>{fmtBytes(status?.total_bytes || 0)}</strong></article>
          <article><Trash2 /><small>Errores</small><strong>{totalErrores}</strong></article>
        </section>

        <section className="backup-panel">
          <div className="backup-panel-head">
            <div>
              <h2>Configuración manual</h2>
              <p>Seleccione qué componentes incluir en el backup.</p>
            </div>
            <button className="backup-btn danger" onClick={limpiar}><Trash2 size={16} /> Limpiar antiguos</button>
          </div>

          <div className="backup-switch-grid">
            <label><input type="checkbox" checked={opciones.incluir_db} onChange={(e)=>setOpciones({...opciones, incluir_db:e.target.checked})}/> PostgreSQL</label>
            <label><input type="checkbox" checked={opciones.incluir_uploads} onChange={(e)=>setOpciones({...opciones, incluir_uploads:e.target.checked})}/> Evidencias / uploads</label>
            <label><input type="checkbox" checked={opciones.incluir_codigo} onChange={(e)=>setOpciones({...opciones, incluir_codigo:e.target.checked})}/> Código backend</label>
          </div>
        </section>

        <section className="backup-panel table-panel">
          <div className="backup-panel-head">
            <div>
              <h2>Historial de backups</h2>
              <p>Últimos respaldos generados manual o automáticamente.</p>
            </div>
          </div>

          <div className="backup-table-wrap">
            <table className="backup-table">
              <thead>
                <tr>
                  <th>Fecha</th><th>Tipo</th><th>Estado</th><th>Archivo</th><th>Tamaño</th><th>Componentes</th><th>Acciones</th>
                </tr>
              </thead>
              <tbody>
                {items.map((b) => (
                  <tr key={b.id}>
                    <td>{b.iniciado_en ? new Date(b.iniciado_en).toLocaleString() : "-"}</td>
                    <td>{b.tipo}</td>
                    <td><span className={estadoClass(b.estado)}>{b.estado}</span></td>
                    <td>{b.nombre_archivo || "Sin archivo"}</td>
                    <td>{fmtBytes(b.tamano_bytes)}</td>
                    <td>{[b.incluye_db && "DB", b.incluye_uploads && "Uploads", b.incluye_codigo && "Código"].filter(Boolean).join(" · ")}</td>
                    <td>{b.estado === "EXITOSO" && <a className="backup-download" href={urlDescargarBackup(b.id)} target="_blank" rel="noreferrer"><Download size={15}/> Descargar</a>}</td>
                  </tr>
                ))}
                {!items.length && <tr><td colSpan="7" className="empty">No hay backups registrados.</td></tr>}
              </tbody>
            </table>
          </div>
        </section>
      </main>
    </AdminLayout>
  );
}
