// =========================================================
// MODAL EJECUCIÓN TÉCNICA PRO - SGA PRO
// Archivo: frontend/src/pages/ModalEjecucionTecnica.jsx
//
// Funciones:
// - Modal grande tipo SaaS para iniciar, pausar y finalizar.
// - Guarda estado inicial, acciones, resultado y observaciones.
// - Sube evidencias.
// - Sin firma obligatoria.
// =========================================================

import { useEffect, useState } from "react";
import API from "../api/axios";

import {
  X,
  Play,
  Pause,
  CheckCircle,
  Save,
  UploadCloud,
  FileText,
  Eye,
  Trash2,
  Barcode,
  Cpu,
  MapPin,
  ShieldAlert,
  CalendarDays,
  Settings,
  Image,
  ClipboardList,
} from "lucide-react";

export default function ModalEjecucionTecnica({
  detalle,
  usuarioId,
  onClose,
  onRefreshDashboard,
  onRefreshDetalle,
  onAbrirFormato,
}) {
  const mantenimiento = detalle?.mantenimiento || {};
  const equipo = detalle?.equipo_basico || {};
  const evidenciasIniciales = detalle?.evidencias || [];

  const mantenimientoId = mantenimiento.id;

  const [estadoInicial, setEstadoInicial] = useState("");
  const [accionesRealizadas, setAccionesRealizadas] = useState("");
  const [resultadoFinal, setResultadoFinal] = useState("");
  const [observaciones, setObservaciones] = useState("");

  const [archivo, setArchivo] = useState(null);
  const [tipoEvidencia, setTipoEvidencia] = useState("DURANTE");
  const [descripcionEvidencia, setDescripcionEvidencia] = useState("");

  const [guardando, setGuardando] = useState(false);
  const [subiendo, setSubiendo] = useState(false);
  const [eliminandoId, setEliminandoId] = useState(null);
  const [previewEvidencia, setPreviewEvidencia] = useState(null);
  const [evidencias, setEvidencias] = useState(evidenciasIniciales);

  useEffect(() => {
    setEstadoInicial(mantenimiento.estado_inicial || mantenimiento.estado_inicial_equipo || "");
    setAccionesRealizadas(mantenimiento.acciones_realizadas || "");
    setResultadoFinal(mantenimiento.resultado_final || "");
    setObservaciones(mantenimiento.observaciones || "");
  }, [mantenimiento.id]);

  useEffect(() => {
    setEvidencias(Array.isArray(evidenciasIniciales) ? evidenciasIniciales : []);
  }, [detalle]);

  const cargarEvidencias = async () => {
    if (!mantenimientoId) {
      setEvidencias([]);
      return;
    }

    try {
      const res = await API.get(`/evidencias/mantenimiento/${mantenimientoId}`);
      setEvidencias(Array.isArray(res.data) ? res.data : []);
    } catch (error) {
      console.error("Error cargando evidencias:", error);
      setEvidencias([]);
    }
  };

  const guardarAvance = async (nuevoEstado = "") => {
    try {
      setGuardando(true);

      const formData = new FormData();
      formData.append("usuario_id", usuarioId);
      formData.append("estado_inicial", estadoInicial || "");
      formData.append("acciones_realizadas", accionesRealizadas || "");
      formData.append("resultado_final", resultadoFinal || "");
      formData.append("observaciones", observaciones || "");
      formData.append("nuevo_estado", nuevoEstado || "");

      await API.patch(
        `/dashboard-tecnico/mantenimiento/${mantenimientoId}/avance`,
        formData
      );

      await onRefreshDashboard();

      if (onRefreshDetalle) {
        await onRefreshDetalle(mantenimientoId);
      }

      if (nuevoEstado) {
        alert(`Mantenimiento actualizado a ${nuevoEstado}.`);
      } else {
        alert("Avance técnico guardado correctamente.");
      }
    } catch (error) {
      console.error(error);
      alert(error.response?.data?.detail || "No se pudo guardar el avance técnico.");
    } finally {
      setGuardando(false);
    }
  };

  const subirEvidencia = async () => {
    if (!archivo) {
      alert("Selecciona una imagen o PDF.");
      return;
    }

    try {
      setSubiendo(true);

      const formData = new FormData();
      formData.append("usuario_id", usuarioId);
      formData.append("tipo", tipoEvidencia);
      formData.append("descripcion", descripcionEvidencia || "");
      formData.append("archivo", archivo);

      const res = await API.post(
        `/dashboard-tecnico/mantenimiento/${mantenimientoId}/evidencia`,
        formData
      );

      setArchivo(null);
      setDescripcionEvidencia("");

      if (res.data?.evidencia) {
        setEvidencias((prev) => [res.data.evidencia, ...prev]);
      }

      await cargarEvidencias();
      await onRefreshDashboard();

      if (onRefreshDetalle) {
        await onRefreshDetalle(mantenimientoId);
      }

      alert("Evidencia cargada correctamente.");
    } catch (error) {
      console.error(error);
      alert(error.response?.data?.detail || "No se pudo subir la evidencia.");
    } finally {
      setSubiendo(false);
    }
  };


  const eliminarEvidencia = async (evidenciaId) => {
    const confirmar = window.confirm(
      "¿Deseas eliminar esta evidencia? Esta acción no se puede deshacer."
    );

    if (!confirmar) return;

    try {
      setEliminandoId(evidenciaId);

      await API.delete(`/evidencias/${evidenciaId}`);

      setEvidencias((prev) => prev.filter((ev) => String(ev.id) !== String(evidenciaId)));

      await cargarEvidencias();
      await onRefreshDashboard();

      if (onRefreshDetalle) {
        await onRefreshDetalle(mantenimientoId);
      }

      alert("Evidencia eliminada correctamente.");
    } catch (error) {
      console.error(error);
      alert(error.response?.data?.detail || "No se pudo eliminar la evidencia.");
    } finally {
      setEliminandoId(null);
    }
  };

  const abrirFormato = () => {
    onAbrirFormato({
      mantenimiento_id: mantenimientoId,
      id: mantenimientoId,
    });
  };

  return (
    <div className="tec-exec-backdrop">
      <div className="tec-exec-modal">
        <button className="tec-exec-close" onClick={onClose}>
          <X size={22} />
        </button>

        <div className="tec-exec-head">
          <span>EJECUCIÓN TÉCNICA</span>
          <h1>{equipo.nombre || "Equipo sin nombre"}</h1>
          <p>
            Estado actual: <strong>{mantenimiento.estado || "—"}</strong>
          </p>
        </div>

        <div className="tec-exec-grid">
          <aside className="tec-exec-left">
            <section className="tec-exec-card">
              <h2>Hoja de vida del equipo</h2>

              <InfoItem icon={<Barcode size={16} />} label="Código inventario" value={equipo.codigo_id || equipo.inventario} />
              <InfoItem icon={<Cpu size={16} />} label="Equipo" value={equipo.nombre} />
              <InfoItem icon={<Settings size={16} />} label="Marca" value={equipo.marca} />
              <InfoItem icon={<Settings size={16} />} label="Modelo" value={equipo.modelo} />
              <InfoItem icon={<Barcode size={16} />} label="Serie" value={equipo.serie} />
              <InfoItem icon={<MapPin size={16} />} label="Ubicación" value={equipo.ubicacion} />
              <InfoItem icon={<ShieldAlert size={16} />} label="Criticidad" value={equipo.criticidad} />
              <InfoItem icon={<CheckCircle size={16} />} label="Estado equipo" value={equipo.estado} />
            </section>

            <section className="tec-exec-card tec-exec-maint">
              <h2>Información del mantenimiento</h2>

              <InfoText label="Tipo" value={mantenimiento.tipo} />
              <InfoText label="Fecha programada" value={formatDate(mantenimiento.fecha_programada)} />
              <InfoText label="Inicio" value={formatDate(mantenimiento.fecha_inicio)} />
              <InfoText label="Fin" value={formatDate(mantenimiento.fecha_finalizacion || mantenimiento.fecha_fin)} />

              <button
                className="tec-exec-primary full"
                onClick={() => guardarAvance("EN_PROCESO")}
                disabled={guardando}
              >
                <Play size={16} />
                Iniciar mantenimiento
              </button>
            </section>
          </aside>

          <main className="tec-exec-right">
            <section className="tec-exec-form-card">
              <label>Estado inicial del equipo / cómo se encontró</label>
              <textarea
                value={estadoInicial}
                onChange={(e) => setEstadoInicial(e.target.value)}
                placeholder="Ej: Equipo enciende, presenta ruido anormal, filtros sucios..."
              />

              <label>Acciones realizadas</label>
              <textarea
                value={accionesRealizadas}
                onChange={(e) => setAccionesRealizadas(e.target.value)}
                placeholder="Ej: Limpieza general, revisión eléctrica, ajuste de conexiones..."
              />

              <label>Resultado final</label>
              <textarea
                value={resultadoFinal}
                onChange={(e) => setResultadoFinal(e.target.value)}
                placeholder="Ej: Equipo queda operativo, pendiente cambio de repuesto..."
              />

              <label>Observaciones</label>
              <textarea
                value={observaciones}
                onChange={(e) => setObservaciones(e.target.value)}
                placeholder="Observaciones adicionales del técnico..."
              />
            </section>

            <section className="tec-exec-form-card">
              <h2>
                <Image size={18} />
                Evidencias fotográficas
              </h2>

              <div className="tec-exec-upload">
                <select
                  value={tipoEvidencia}
                  onChange={(e) => setTipoEvidencia(e.target.value)}
                >
                  <option value="ANTES">Antes</option>
                  <option value="DURANTE">Durante</option>
                  <option value="DESPUES">Después</option>
                  <option value="SOPORTE">Soporte</option>
                </select>

                <input
                  type="file"
                  accept=".jpg,.jpeg,.png,.pdf"
                  onChange={(e) => setArchivo(e.target.files?.[0] || null)}
                />

                <button onClick={subirEvidencia} disabled={subiendo}>
                  <UploadCloud size={16} />
                  {subiendo ? "Subiendo..." : "Subir"}
                </button>
              </div>

              <input
                className="tec-exec-desc"
                value={descripcionEvidencia}
                onChange={(e) => setDescripcionEvidencia(e.target.value)}
                placeholder="Descripción de la evidencia..."
              />

              <div className="tec-exec-evidencias">
                {evidencias.length === 0 && (
                  <p>No hay evidencias cargadas.</p>
                )}

                {evidencias.map((ev) => {
                  const url = getFileUrl(ev.archivo_url);
                  const imagen = isImage(ev.archivo_url);

                  return (
                    <article key={ev.id} className="tec-exec-evidencia tec-evidence-card-pro">
                      <div className="tec-evidence-card-preview">
                        {imagen ? (
                          <img src={url} alt={ev.nombre_original || "Evidencia"} />
                        ) : (
                          <div className="tec-evidence-file-preview">
                            <FileText size={30} />
                            <span>{isPdf(ev.archivo_url) ? "PDF" : "Archivo"}</span>
                          </div>
                        )}
                      </div>

                      <div className="tec-evidence-card-info">
                        <strong>{ev.tipo || "SOPORTE"}</strong>
                        <span>{ev.nombre_original || ev.filename || "Archivo"}</span>
                        <small>{ev.descripcion || "Sin descripción"}</small>

                        <div className="tec-evidence-card-actions">
                          <button
                            type="button"
                            className="tec-exec-light"
                            onClick={() => setPreviewEvidencia({ ...ev, url })}
                          >
                            <Eye size={15} />
                            Ver
                          </button>

                          <button
                            type="button"
                            className="tec-exec-danger"
                            onClick={() => eliminarEvidencia(ev.id)}
                            disabled={eliminandoId === ev.id}
                          >
                            <Trash2 size={15} />
                            {eliminandoId === ev.id ? "Eliminando..." : "Eliminar"}
                          </button>
                        </div>
                      </div>
                    </article>
                  );
                })}
              </div>
            </section>

            <section className="tec-exec-form-card tec-exec-signature-optional">
              <h2>
                <ClipboardList size={18} />
                Firma digital del técnico
              </h2>

              <div className="tec-exec-signature-box">
                <span>Firma opcional no requerida en esta fase</span>
              </div>
            </section>
          </main>
        </div>

        <div className="tec-exec-footer">
          <button className="tec-exec-light" onClick={onClose}>
            Cancelar
          </button>

          <button
            className="tec-exec-light"
            onClick={() => guardarAvance("")}
            disabled={guardando}
          >
            <Save size={16} />
            {guardando ? "Guardando..." : "Guardar avance"}
          </button>

          <button
            className="tec-exec-format"
            onClick={abrirFormato}
          >
            <ClipboardList size={16} />
            Formato oficial
          </button>

          <button
            className="tec-exec-danger"
            onClick={() => guardarAvance("PAUSADO")}
            disabled={guardando}
          >
            <Pause size={16} />
            Pausar
          </button>

          <button
            className="tec-exec-primary"
            onClick={() => guardarAvance("FINALIZADO")}
            disabled={guardando}
          >
            <CheckCircle size={16} />
            Finalizar
          </button>
        </div>

        {previewEvidencia && (
          <div className="tec-modal-backdrop">
            <div className="tec-modal tec-modal-large">
              <div className="tec-modal-header">
                <div>
                  <h2>Vista de evidencia</h2>
                  <p>{previewEvidencia.nombre_original || previewEvidencia.filename || "Archivo"}</p>
                </div>

                <button onClick={() => setPreviewEvidencia(null)}>
                  <X size={18} />
                </button>
              </div>

              {isPdf(previewEvidencia.archivo_url) ? (
                <iframe
                  src={previewEvidencia.url}
                  title="Evidencia PDF"
                  className="tec-evidence-iframe"
                />
              ) : (
                <img
                  src={previewEvidencia.url}
                  alt="Vista evidencia"
                  className="tec-evidence-big-img"
                />
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

function InfoItem({ icon, label, value }) {
  return (
    <div className="tec-exec-info-item">
      <div className="tec-exec-info-icon">{icon}</div>
      <strong>{label}:</strong>
      <span>{value || "No registrado"}</span>
    </div>
  );
}

function InfoText({ label, value }) {
  return (
    <p className="tec-exec-info-text">
      <strong>{label}:</strong> {value || "Pendiente"}
    </p>
  );
}

function formatDate(value) {
  if (!value) return "Sin fecha";
  const d = new Date(value);
  return Number.isNaN(d.getTime()) ? value : d.toLocaleString();
}

function getFileUrl(url) {
  if (!url) return "#";
  if (url.startsWith("http://") || url.startsWith("https://")) return url;

  const base = String(
    import.meta.env.VITE_API_URL ||
      API?.defaults?.baseURL ||
      window.location.origin
  ).replace(/\/$/, "");

  return url.startsWith("/") ? `${base}${url}` : `${base}/${url}`;
}

function isPdf(url = "") {
  return String(url).toLowerCase().includes(".pdf");
}

function isImage(url = "") {
  const lower = String(url).toLowerCase();
  return [".jpg", ".jpeg", ".png", ".webp", ".gif"].some((ext) =>
    lower.includes(ext)
  );
}