// =========================================================
// MODAL EJECUCIÓN TÉCNICA PRO - SGAHolding
// Archivo: frontend/src/pages/ModalEjecucionTecnica.jsx
//
// Funciones:
// - Modal grande tipo SaaS para iniciar, pausar y finalizar.
// - Guarda estado inicial, acciones, resultado y observaciones.
// - Sube evidencias.
// - Sin firma obligatoria.
// =========================================================

import { useEffect, useMemo, useState } from "react";
import API from "../api/axios";
import { isNetworkError, queueOfflineRequest } from "../utils/offlineQueue";

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
  const evidenciasIniciales = useMemo(() => detalle?.evidencias || [], [detalle?.evidencias]);

  const mantenimientoId = mantenimiento.id;

  const [estadoInicial, setEstadoInicial] = useState("");
  const [accionesRealizadas, setAccionesRealizadas] = useState("");
  const [resultadoFinal, setResultadoFinal] = useState("");
  const [observaciones, setObservaciones] = useState("");
  const [repuestos, setRepuestos] = useState([]);
  const [incidencias, setIncidencias] = useState([]);

  const [archivo, setArchivo] = useState(null);
  const [tipoEvidencia, setTipoEvidencia] = useState("DURANTE");
  const [descripcionEvidencia, setDescripcionEvidencia] = useState("");

  const [guardando, setGuardando] = useState(false);
  const [subiendo, setSubiendo] = useState(false);
  const [eliminandoId, setEliminandoId] = useState(null);
  const [previewEvidencia, setPreviewEvidencia] = useState(null);
  const [evidencias, setEvidencias] = useState(evidenciasIniciales);
  const [tieneFirma, setTieneFirma] = useState(false);

  useEffect(() => {
    const timer = window.setTimeout(() => {
      setEstadoInicial(mantenimiento.estado_inicial || mantenimiento.estado_inicial_equipo || "");
      setAccionesRealizadas(mantenimiento.acciones_realizadas || "");
      setResultadoFinal(mantenimiento.resultado_final || "");
      setObservaciones(mantenimiento.observaciones || "");
      setRepuestos(Array.isArray(detalle?.repuestos) ? detalle.repuestos : []);
      setIncidencias(Array.isArray(detalle?.incidencias) ? detalle.incidencias : []);
    }, 0);
    return () => window.clearTimeout(timer);
  }, [
    mantenimiento.id,
    mantenimiento.acciones_realizadas,
    mantenimiento.estado_inicial,
    mantenimiento.estado_inicial_equipo,
    mantenimiento.observaciones,
    mantenimiento.resultado_final,
    detalle?.incidencias,
    detalle?.repuestos,
  ]);

  useEffect(() => {
    const timer = window.setTimeout(
      () => setEvidencias(Array.isArray(evidenciasIniciales) ? evidenciasIniciales : []),
      0
    );
    return () => window.clearTimeout(timer);
  }, [evidenciasIniciales]);

  useEffect(() => {
    let activo = true;
    API.get(`/formatos-mantenimiento/mantenimiento/${mantenimientoId}`)
      .then((res) => {
        if (activo) setTieneFirma([res.data?.firma_usuario, res.data?.firma_operario].some((firma) => String(firma || "").startsWith("data:image/png;base64,")));
      })
      .catch(() => {
        if (activo) setTieneFirma(false);
      });
    return () => { activo = false; };
  }, [mantenimientoId]);

  const tiposCargados = new Set(evidencias.map((item) => String(item.tipo || "").toUpperCase()));
  const pasosCompletos = ["ANTES", "DURANTE", "DESPUES"].every((tipo) => tiposCargados.has(tipo));
  const formularioCompleto = Boolean(estadoInicial.trim() && accionesRealizadas.trim() && resultadoFinal.trim());
  const puedeFinalizar = pasosCompletos && formularioCompleto && tieneFirma;

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
    if (repuestos.some((item) => !String(item.descripcion || "").trim() || Number(item.cantidad) <= 0)) {
      alert("Completa la descripción y una cantidad positiva en cada repuesto.");
      return;
    }
    if (incidencias.some((item) => !String(item.descripcion || "").trim())) {
      alert("Completa la descripción de cada incidencia.");
      return;
    }
    const formData = new FormData();
    formData.append("usuario_id", usuarioId);
    formData.append("estado_inicial", estadoInicial || "");
    formData.append("acciones_realizadas", accionesRealizadas || "");
    formData.append("resultado_final", resultadoFinal || "");
    formData.append("observaciones", observaciones || "");
    formData.append("repuestos_json", JSON.stringify(repuestos));
    formData.append("incidencias_json", JSON.stringify(incidencias));
    formData.append("nuevo_estado", nuevoEstado || "");

    try {
      setGuardando(true);

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
      if (isNetworkError(error)) {
        await queueOfflineRequest({
          method: "patch",
          url: `/dashboard-tecnico/mantenimiento/${mantenimientoId}/avance`,
          data: formData,
        });
        alert("Sin conexión: el avance quedó guardado en este dispositivo y se sincronizará automáticamente.");
        return;
      }
      alert(formatApiError(error, "No se pudo guardar el avance técnico."));
    } finally {
      setGuardando(false);
    }
  };

  const subirEvidencia = async () => {
    if (!archivo) {
      alert("Selecciona una imagen o PDF.");
      return;
    }
    if (["ANTES", "DURANTE", "DESPUES"].includes(tipoEvidencia) && !descripcionEvidencia.trim()) {
      alert("Escribe el comentario obligatorio de esta etapa.");
      return;
    }

    const formData = new FormData();
    formData.append("usuario_id", usuarioId);
    formData.append("tipo", tipoEvidencia);
    formData.append("descripcion", descripcionEvidencia || "");
    formData.append("archivo", archivo);

    try {
      setSubiendo(true);

      const res = await API.post(
        `/dashboard-tecnico/mantenimiento/${mantenimientoId}/evidencia`,
        formData
      );

      setArchivo(null);
      setDescripcionEvidencia("");
      setTipoEvidencia(nextEvidenceType(tipoEvidencia));

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
      if (isNetworkError(error)) {
        const pendiente = await queueOfflineRequest({
          method: "post",
          url: `/dashboard-tecnico/mantenimiento/${mantenimientoId}/evidencia`,
          data: formData,
        });
        setEvidencias((prev) => [{
          id: `offline-${pendiente.id}`,
          tipo: tipoEvidencia,
          descripcion: descripcionEvidencia,
          nombre_original: archivo.name,
          archivo_url: URL.createObjectURL(archivo),
          pendiente_sincronizacion: true,
        }, ...prev]);
        setArchivo(null);
        setDescripcionEvidencia("");
        setTipoEvidencia(nextEvidenceType(tipoEvidencia));
        alert("Sin conexión: la evidencia quedó protegida en este dispositivo y se sincronizará automáticamente.");
        return;
      }
      alert(formatApiError(error, "No se pudo subir la evidencia."));
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
              <div className="tec-operational-head"><h2>Repuestos utilizados</h2><button type="button" onClick={() => setRepuestos((prev) => [...prev, { descripcion: "", referencia: "", cantidad: 1, unidad: "UNIDAD", costo_unitario: "" }])}>+ Agregar</button></div>
              {repuestos.length === 0 && <p>No se utilizaron repuestos.</p>}
              {repuestos.map((item, index) => (
                <div className="tec-operational-row repuesto" key={item.id || index}>
                  <input aria-label="Descripción del repuesto" placeholder="Descripción *" value={item.descripcion || ""} onChange={(e) => setRepuestos((prev) => actualizarLista(prev, index, "descripcion", e.target.value))} />
                  <input aria-label="Referencia" placeholder="Referencia" value={item.referencia || ""} onChange={(e) => setRepuestos((prev) => actualizarLista(prev, index, "referencia", e.target.value))} />
                  <input aria-label="Cantidad" type="number" min="0.001" step="0.001" value={item.cantidad ?? 1} onChange={(e) => setRepuestos((prev) => actualizarLista(prev, index, "cantidad", e.target.value))} />
                  <select aria-label="Unidad" value={item.unidad || "UNIDAD"} onChange={(e) => setRepuestos((prev) => actualizarLista(prev, index, "unidad", e.target.value))}><option>UNIDAD</option><option>METRO</option><option>LITRO</option><option>KILOGRAMO</option><option>JUEGO</option></select>
                  <button type="button" className="tec-row-remove" onClick={() => setRepuestos((prev) => prev.filter((_, i) => i !== index))}>×</button>
                </div>
              ))}
            </section>

            <section className="tec-exec-form-card">
              <div className="tec-operational-head"><h2>Incidencias encontradas</h2><button type="button" onClick={() => setIncidencias((prev) => [...prev, { tipo: "TECNICA", severidad: "MEDIA", descripcion: "", resuelta: false }])}>+ Agregar</button></div>
              {incidencias.length === 0 && <p>No se registraron incidencias.</p>}
              {incidencias.map((item, index) => (
                <div className="tec-operational-row incidencia" key={item.id || index}>
                  <select aria-label="Tipo de incidencia" value={item.tipo || "TECNICA"} onChange={(e) => setIncidencias((prev) => actualizarLista(prev, index, "tipo", e.target.value))}><option>TECNICA</option><option>SEGURIDAD</option><option>REPUESTO</option><option>OPERATIVA</option></select>
                  <select aria-label="Severidad" value={item.severidad || "MEDIA"} onChange={(e) => setIncidencias((prev) => actualizarLista(prev, index, "severidad", e.target.value))}><option>BAJA</option><option>MEDIA</option><option>ALTA</option><option>CRITICA</option></select>
                  <input aria-label="Descripción de incidencia" placeholder="Descripción *" value={item.descripcion || ""} onChange={(e) => setIncidencias((prev) => actualizarLista(prev, index, "descripcion", e.target.value))} />
                  <label className="tec-resolved-check"><input type="checkbox" checked={Boolean(item.resuelta)} onChange={(e) => setIncidencias((prev) => actualizarLista(prev, index, "resuelta", e.target.checked))} /> Resuelta</label>
                  <button type="button" className="tec-row-remove" onClick={() => setIncidencias((prev) => prev.filter((_, i) => i !== index))}>×</button>
                </div>
              ))}
            </section>

            <section className="tec-exec-form-card">
              <h2>
                <Image size={18} />
                Evidencias fotográficas
              </h2>

              <div className="tec-step-progress" role="list" aria-label="Progreso de evidencias">
                {[["ANTES", "1. Estado inicial"], ["DURANTE", "2. Proceso"], ["DESPUES", "3. Estado final"]].map(([tipo, label]) => (
                  <span key={tipo} role="listitem" className={tiposCargados.has(tipo) ? "complete" : "pending"}>
                    {tiposCargados.has(tipo) ? "✓" : "○"} {label}
                  </span>
                ))}
                <span role="listitem" className={tieneFirma ? "complete" : "pending"}>
                  {tieneFirma ? "✓" : "○"} 4. Firma
                </span>
              </div>

              <div className="tec-exec-upload">
                <select
                  value={tipoEvidencia}
                  onChange={(e) => setTipoEvidencia(e.target.value)}
                >
                  <option value="ANTES">Antes</option>
                  <option value="DURANTE" disabled={!tiposCargados.has("ANTES")}>Durante</option>
                  <option value="DESPUES" disabled={!tiposCargados.has("ANTES") || !tiposCargados.has("DURANTE")}>Después</option>
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
                        {ev.pendiente_sincronizacion && <small>⏳ Pendiente de sincronización</small>}

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
                            disabled={eliminandoId === ev.id || ev.pendiente_sincronizacion}
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
                Firma digital del cliente o técnico
              </h2>

              <div className="tec-exec-signature-box">
                <span>{tieneFirma ? "Firma registrada en el formato oficial" : "Firma obligatoria pendiente: complétala en Formato oficial"}</span>
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
            disabled={guardando || !puedeFinalizar}
            title={puedeFinalizar ? "Finalizar orden" : "Completa las tres fotos, los campos obligatorios y la firma"}
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
  if (url.startsWith("http://") || url.startsWith("https://") || url.startsWith("blob:")) return url;

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

function formatApiError(error, fallback) {
  const detail = error?.response?.data?.detail;
  if (!detail) return fallback;
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail?.faltantes)) {
    return `${detail.mensaje || fallback}\n\nFalta:\n- ${detail.faltantes.join("\n- ")}`;
  }
  return detail.mensaje || fallback;
}

function nextEvidenceType(tipo) {
  if (tipo === "ANTES") return "DURANTE";
  if (tipo === "DURANTE") return "DESPUES";
  return "SOPORTE";
}

function actualizarLista(lista, index, campo, valor) {
  return lista.map((item, i) => i === index ? { ...item, [campo]: valor } : item);
}
