import { useEffect, useMemo, useState } from "react";
import {
  Wrench, Calendar, FileCheck, ArrowRight, ArrowLeft,
  CheckCircle2, Clock, MapPin, User, AlertTriangle,
  Lightbulb,
} from "lucide-react";
import EquipmentSearch from "../../components/EquipmentSearch";
import { showToast } from "../../utils/toast";
import API from "../../api/axios";

const TIPOS = [
  { value: "PREVENTIVO", label: "Preventivo" },
  { value: "CORRECTIVO", label: "Correctivo" },
  { value: "CALIBRACION", label: "Calibración" },
  { value: "INSPECCION", label: "Inspección" },
];

const PRIORIDADES = [
  { value: "BAJA", label: "Baja", color: "#6b7280" },
  { value: "MEDIA", label: "Media", color: "#2563eb" },
  { value: "ALTA", label: "Alta", color: "#d97706" },
  { value: "CRITICA", label: "Crítica", color: "#dc2626" },
];

const DESCRIPCION_PLACEHOLDER = {
  PREVENTIVO: "Trabajo preventivo solicitado",
  CORRECTIVO: "Falla o incidencia reportada",
  CALIBRACION: "Calibración requerida",
  INSPECCION: "Objetivo de la inspección",
};

const DRAFT_KEY = "vaner_maintenance_draft";

function calcEnd(isoStart, minutes) {
  if (!isoStart || !minutes) return "";
  const d = new Date(isoStart);
  d.setMinutes(d.getMinutes() + Number(minutes));
  return d.toISOString().slice(0, 16);
}

function loadDraft() {
  try {
    const raw = localStorage.getItem(DRAFT_KEY);
    return raw ? JSON.parse(raw) : null;
  } catch { return null; }
}

function saveDraft(form) {
  try {
    if (form.equipo_id) {
      localStorage.setItem(DRAFT_KEY, JSON.stringify(form));
    }
  } catch { /* ignore */ }
}

function clearDraft() {
  try { localStorage.removeItem(DRAFT_KEY); } catch { /* ignore */ }
}

export default function MaintenanceWizard({ equipos, sedes, tecnicos, onSuccess, onCancel }) {
  const initialDraft = useMemo(() => loadDraft(), []);
  const [step, setStep] = useState(initialDraft?.equipo_id ? 2 : 1);
  const [saving, setSaving] = useState(false);
  const [errors, setErrors] = useState({});
  const [conflictos, setConflictos] = useState(null);
  const [sugerenciaTecnico, setSugerenciaTecnico] = useState(null);
  const [sugerenciaPrioridad, setSugerenciaPrioridad] = useState(null);

  const [form, setForm] = useState(() => ({
    equipo_id: initialDraft?.equipo_id || "",
    tipo: initialDraft?.tipo || "PREVENTIVO",
    prioridad: initialDraft?.prioridad || "MEDIA",
    descripcion: initialDraft?.descripcion || "",
    fecha_inicio_programada: initialDraft?.fecha_inicio_programada || "",
    duracion_minutos: initialDraft?.duracion_minutos || "",
    tecnico_id: initialDraft?.tecnico_id || "",
    observaciones: initialDraft?.observaciones || "",
    recurrencia: initialDraft?.recurrencia || "",
    recurrencia_cantidad: initialDraft?.recurrencia_cantidad || "",
  }));

  const equipo = useMemo(
    () => equipos.find((e) => String(e.id) === String(form.equipo_id)) || null,
    [equipos, form.equipo_id],
  );

  const duracionCalculada = useMemo(() => {
    if (!form.fecha_inicio_programada || !form.duracion_minutos) return "";
    return calcEnd(form.fecha_inicio_programada, form.duracion_minutos);
  }, [form.fecha_inicio_programada, form.duracion_minutos]);

  useEffect(() => { saveDraft(form); }, [form]);

  useEffect(() => {
    let cancelled = false;
    if (form.equipo_id) {
      API.get(`/mantenimientos/conflictos/${form.equipo_id}`, {
        params: {
          tecnico_id: form.tecnico_id || undefined,
          fecha_inicio: form.fecha_inicio_programada || undefined,
          fecha_fin: duracionCalculada || undefined,
        },
      }).then((res) => { if (!cancelled) setConflictos(res.data); }).catch(() => {});
    }
    return () => { cancelled = true; };
  }, [form.equipo_id, form.tecnico_id, form.fecha_inicio_programada, duracionCalculada]);

  useEffect(() => {
    let cancelled = false;
    if (form.equipo_id) {
      API.get(`/mantenimientos/sugerir-tecnico/${form.equipo_id}`).then((res) => {
        if (!cancelled) setSugerenciaTecnico(res.data);
      }).catch(() => {});
    }
    return () => { cancelled = true; };
  }, [form.equipo_id]);

  useEffect(() => {
    let cancelled = false;
    if (form.equipo_id) {
      API.get("/mantenimientos/sugerir-prioridad", {
        params: { equipo_id: form.equipo_id, tipo: form.tipo },
      }).then((res) => { if (!cancelled) setSugerenciaPrioridad(res.data); }).catch(() => {});
    }
    return () => { cancelled = true; };
  }, [form.equipo_id, form.tipo]);

  const set = (field, value) => setForm((f) => ({ ...f, [field]: value }));

  const applySuggestedTech = (tecnicoId) => {
    set("tecnico_id", tecnicoId);
    showToast("Técnico sugerido aplicado", "info");
  };

  const applySuggestedPriority = (prioridad) => {
    set("prioridad", prioridad);
    showToast(`Prioridad ${prioridad} aplicada`, "info");
  };

  const validateStep1 = () => {
    if (!form.equipo_id) {
      setErrors({ equipo_id: "Seleccione un equipo" });
      return false;
    }
    if (conflictos && !conflictos.puede_crear) {
      setErrors({ equipo_id: conflictos.bloqueantes?.[0]?.mensaje || "Hay conflictos que impiden crear la orden" });
      return false;
    }
    setErrors({});
    return true;
  };

  const validateStep2 = () => {
    const e = {};
    if (!form.descripcion.trim()) e.descripcion = "Describa el trabajo a realizar";
    if (!form.fecha_inicio_programada) e.fecha_inicio_programada = "Seleccione fecha y hora de inicio";
    if (form.duracion_minutos && Number(form.duracion_minutos) <= 0)
      e.duracion_minutos = "La duración debe ser mayor a 0";
    setErrors(e);
    return Object.keys(e).length === 0;
  };

  const next = () => {
    if (step === 1 && validateStep1()) setStep(2);
    else if (step === 2 && validateStep2()) setStep(3);
  };

  const back = () => setStep((s) => Math.max(1, s - 1));

  const submit = async () => {
    setSaving(true);
    try {
      const payload = {
        equipo_id: form.equipo_id,
        tipo: form.tipo,
        descripcion: form.descripcion,
        prioridad: form.prioridad,
        fecha_inicio_programada: form.fecha_inicio_programada || null,
        fecha_fin_programada: duracionCalculada || null,
        duracion_estimada_minutos: form.duracion_minutos ? Number(form.duracion_minutos) : null,
        tecnico_id: form.tecnico_id || null,
        observaciones: form.observaciones || null,
      };
      const res = await API.post("/mantenimientos/", payload);

      if (form.recurrencia && res?.data?.id) {
        try {
          const recRes = await API.post(
            `/mantenimientos/${res.data.id}/recurrencia`,
            null,
            { params: { frecuencia: form.recurrencia, cantidad: form.recurrencia_cantidad || 5 } },
          );
          showToast(
            `Orden creada + ${recRes.data?.cantidad || 0} órdenes recurrentes`,
            "success",
          );
        } catch {
          showToast("Orden creada pero la recurrencia falló", "warning");
        }
      } else {
        showToast("Orden de mantenimiento creada correctamente", "success");
      }

      clearDraft();
      onSuccess?.();
    } catch (err) {
      showToast(err?.response?.data?.detail || "No se pudo crear la orden", "error");
    } finally {
      setSaving(false);
    }
  };

  const tipoInfo = TIPOS.find((t) => t.value === form.tipo);
  const topSugerido = sugerenciaTecnico?.sugerencias?.[0];

  return (
    <div className="wz-root">
      <div className="wz-header">
        <div className="wz-header-icon"><Wrench size={22} /></div>
        <div>
          <h2>Nueva orden de mantenimiento</h2>
          <p>Crea una orden en 3 pasos simples</p>
        </div>
        {conflictos?.advertencias?.length > 0 && (
          <span className="wz-conflict-badge">
            <AlertTriangle size={14} /> {conflictos.advertencias.length}
          </span>
        )}
      </div>

      <div className="wz-steps">
        {[
          { n: 1, icon: Wrench, label: "Activo" },
          { n: 2, icon: Calendar, label: "Trabajo" },
          { n: 3, icon: FileCheck, label: "Confirmar" },
        ].map(({ n, icon: Icon, label }) => (
          <div key={n} className={`wz-step ${step === n ? "active" : step > n ? "done" : ""}`}>
            <div className="wz-step-circle">
              {step > n ? <CheckCircle2 size={18} /> : <Icon size={18} />}
            </div>
            <span>{label}</span>
          </div>
        ))}
      </div>

      <div className="wz-body">
        {/* ─── PASO 1: ACTIVO ─── */}
        {step === 1 && (
          <div className="wz-panel">
            <h3>Seleccionar activo</h3>
            <p className="wz-hint">Busca por nombre, código, ubicación, sede o marca</p>

            <EquipmentSearch
              equipos={equipos}
              sedes={sedes}
              selectedId={form.equipo_id}
              onSelect={(eq) => set("equipo_id", eq ? eq.id : "")}
            />
            {errors.equipo_id && <span className="wz-error">{errors.equipo_id}</span>}

            {conflictos && conflictos.bloqueantes?.length > 0 && (
              <div className="wz-alert wz-alert-error">
                <AlertTriangle size={16} />
                <div>
                  <strong>Conflictos detectados</strong>
                  {conflictos.bloqueantes.map((c, i) => <p key={i}>{c.mensaje}</p>)}
                </div>
              </div>
            )}

            {conflictos && conflictos.advertencias?.length > 0 && (
              <div className="wz-alert wz-alert-warn">
                <AlertTriangle size={16} />
                <div>
                  <strong>Advertencias</strong>
                  {conflictos.advertencias.map((c, i) => <p key={i}>{c.mensaje}</p>)}
                </div>
              </div>
            )}

            {equipo && (
              <div className="wz-equipment-card">
                <div className="wz-eq-card-header">
                  <strong>{equipo.nombre}</strong>
                  {equipo.estado && <span className={`wz-eq-status ${equipo.estado === "OPERATIVO" ? "ok" : "warn"}`}>{equipo.estado}</span>}
                </div>
                <div className="wz-eq-card-grid">
                  {equipo.codigo_id && <div><span>Código</span><strong>{equipo.codigo_id}</strong></div>}
                  {equipo.inventario && <div><span>Inventario</span><strong>{equipo.inventario}</strong></div>}
                  {equipo.serie && <div><span>Serie</span><strong>{equipo.serie}</strong></div>}
                  {equipo.marca && <div><span>Marca</span><strong>{equipo.marca}</strong></div>}
                  {equipo.modelo && <div><span>Modelo</span><strong>{equipo.modelo}</strong></div>}
                  {equipo.ubicacion && (
                    <div className="wz-eq-location"><MapPin size={13} /><span>Ubicación</span><strong>{equipo.ubicacion}</strong></div>
                  )}
                  {equipo.criticidad && <div><span>Criticidad</span><strong>{equipo.criticidad}</strong></div>}
                </div>
              </div>
            )}
          </div>
        )}

        {/* ─── PASO 2: TRABAJO ─── */}
        {step === 2 && (
          <div className="wz-panel">
            <h3>Programar trabajo</h3>

            <div className="wz-form-grid">
              <label className="wz-field">
                <span>Tipo de mantenimiento *</span>
                <select value={form.tipo} onChange={(e) => set("tipo", e.target.value)}>
                  {TIPOS.map((t) => <option key={t.value} value={t.value}>{t.label}</option>)}
                </select>
              </label>

              <label className="wz-field">
                <span>
                  Prioridad
                  {sugerenciaPrioridad && (
                    <button
                      type="button"
                      className="wz-suggest-btn"
                      onClick={() => applySuggestedPriority(sugerenciaPrioridad.prioridad_sugerida)}
                      title={`Sugerida: ${sugerenciaPrioridad.prioridad_sugerida}`}
                    >
                      <Lightbulb size={12} /> Sugerir
                    </button>
                  )}
                </span>
                <select value={form.prioridad} onChange={(e) => set("prioridad", e.target.value)}>
                  {PRIORIDADES.map((p) => <option key={p.value} value={p.value}>{p.label}</option>)}
                </select>
                {sugerenciaPrioridad && (
                  <small className="wz-suggest-hint">
                    <Lightbulb size={11} /> {sugerenciaPrioridad.prioridad_sugerida}
                    {sugerenciaPrioridad.motivos?.length > 0 && ` — ${sugerenciaPrioridad.motivos[0]}`}
                  </small>
                )}
              </label>

              <label className="wz-field wz-field-full">
                <span>Descripción / Trabajo solicitado *</span>
                <textarea
                  rows={3}
                  placeholder={DESCRIPCION_PLACEHOLDER[form.tipo] || "Describa el trabajo"}
                  value={form.descripcion}
                  onChange={(e) => set("descripcion", e.target.value)}
                />
                {errors.descripcion && <span className="wz-error">{errors.descripcion}</span>}
              </label>

              <label className="wz-field">
                <span>Fecha y hora de inicio *</span>
                <input
                  type="datetime-local"
                  value={form.fecha_inicio_programada}
                  onChange={(e) => set("fecha_inicio_programada", e.target.value)}
                />
                {errors.fecha_inicio_programada && <span className="wz-error">{errors.fecha_inicio_programada}</span>}
              </label>

              <label className="wz-field">
                <span>Duración estimada (minutos)</span>
                <input
                  type="number"
                  min="1"
                  placeholder="Ej: 120"
                  value={form.duracion_minutos}
                  onChange={(e) => set("duracion_minutos", e.target.value)}
                />
                {errors.duracion_minutos && <span className="wz-error">{errors.duracion_minutos}</span>}
              </label>

              {duracionCalculada && (
                <div className="wz-calculated">
                  <Clock size={14} />
                  <span>Fecha fin calculada: <strong>{new Date(duracionCalculada).toLocaleString()}</strong></span>
                </div>
              )}

              <label className="wz-field">
                <span>
                  Técnico responsable (opcional)
                  {topSugerido && (
                    <button
                      type="button"
                      className="wz-suggest-btn"
                      onClick={() => applySuggestedTech(topSugerido.tecnico_id)}
                      title={`Sugerir ${topSugerido.nombre}`}
                    >
                      <Lightbulb size={12} /> Sugerir
                    </button>
                  )}
                </span>
                <select value={form.tecnico_id} onChange={(e) => set("tecnico_id", e.target.value)}>
                  <option value="">Pendiente por asignar</option>
                  {tecnicos.map((t) => (
                    <option key={t.id} value={t.id}>
                      {t.usuario?.nombre_completo || t.nombre || t.especialidad || `Técnico ${t.id}`}
                    </option>
                  ))}
                </select>
                {topSugerido && !form.tecnico_id && (
                  <small className="wz-suggest-hint">
                    <Lightbulb size={11} /> {topSugerido.nombre}
                    {topSugerido.ordenes_activas > 0 && ` (${topSugerido.ordenes_activas} órdenes activas)`}
                  </small>
                )}
              </label>

              <label className="wz-field wz-field-full">
                <span>Observaciones (opcional)</span>
                <textarea
                  rows={2}
                  placeholder="Notas adicionales"
                  value={form.observaciones}
                  onChange={(e) => set("observaciones", e.target.value)}
                />
              </label>

              <label className="wz-field">
                <span>Recurrencia (opcional)</span>
                <select value={form.recurrencia} onChange={(e) => set("recurrencia", e.target.value)}>
                  <option value="">Sin recurrencia</option>
                  <option value="SEMANAL">Semanal</option>
                  <option value="MENSUAL">Mensual</option>
                  <option value="BIMESTRAL">Bimestral</option>
                  <option value="TRIMESTRAL">Trimestral</option>
                  <option value="SEMESTRAL">Semestral</option>
                  <option value="ANUAL">Anual</option>
                </select>
              </label>

              {form.recurrencia && (
                <label className="wz-field">
                  <span>Cantidad de repeticiones</span>
                  <input
                    type="number"
                    min="1"
                    max="24"
                    placeholder="Ej: 5"
                    value={form.recurrencia_cantidad}
                    onChange={(e) => set("recurrencia_cantidad", e.target.value)}
                  />
                  <small className="wz-suggest-hint">
                    Se crearán {form.recurrencia_cantidad || "?"} órdenes adicionales
                  </small>
                </label>
              )}
            </div>

            {conflictos && conflictos.advertencias?.length > 0 && (
              <div className="wz-alert wz-alert-warn" style={{ marginTop: 16 }}>
                <AlertTriangle size={16} />
                <div>
                  <strong>Advertencias</strong>
                  {conflictos.advertencias.map((c, i) => <p key={i}>{c.mensaje}</p>)}
                </div>
              </div>
            )}
          </div>
        )}

        {/* ─── PASO 3: CONFIRMAR ─── */}
        {step === 3 && (
          <div className="wz-panel">
            <h3>Confirmar orden</h3>

            <div className="wz-summary">
              {equipo && (
                <div className="wz-summary-section">
                  <h4><MapPin size={14} /> Activo</h4>
                  <div className="wz-summary-grid">
                    <div><span>Equipo</span><strong>{equipo.nombre}</strong></div>
                    {equipo.codigo_id && <div><span>Código</span><strong>{equipo.codigo_id}</strong></div>}
                    {equipo.inventario && <div><span>Inventario</span><strong>{equipo.inventario}</strong></div>}
                    {equipo.ubicacion && <div><span>Ubicación</span><strong>{equipo.ubicacion}</strong></div>}
                  </div>
                </div>
              )}

              <div className="wz-summary-section">
                <h4><Wrench size={14} /> Trabajo</h4>
                <div className="wz-summary-grid">
                  <div><span>Tipo</span><strong>{tipoInfo?.label || form.tipo}</strong></div>
                  <div><span>Prioridad</span>
                    <strong style={{ color: PRIORIDADES.find((p) => p.value === form.prioridad)?.color }}>
                      {form.prioridad}
                    </strong>
                  </div>
                  <div className="wz-summary-full"><span>Descripción</span><strong>{form.descripcion}</strong></div>
                </div>
              </div>

              <div className="wz-summary-section">
                <h4><Calendar size={14} /> Programación</h4>
                <div className="wz-summary-grid">
                  <div><span>Inicio</span><strong>{form.fecha_inicio_programada ? new Date(form.fecha_inicio_programada).toLocaleString() : "Sin definir"}</strong></div>
                  {duracionCalculada && <div><span>Fin calculado</span><strong>{new Date(duracionCalculada).toLocaleString()}</strong></div>}
                  {form.duracion_minutos && <div><span>Duración</span><strong>{form.duracion_minutos} min</strong></div>}
                  <div><span>Técnico</span>
                    <strong>
                      <User size={13} style={{ marginRight: 4 }} />
                      {form.tecnico_id
                        ? tecnicos.find((t) => String(t.id) === form.tecnico_id)?.usuario?.nombre_completo
                          || tecnicos.find((t) => String(t.id) === form.tecnico_id)?.nombre || "Asignado"
                        : "Pendiente por asignar"}
                    </strong>
                  </div>
                </div>
              </div>

              {form.observaciones && (
                <div className="wz-summary-section">
                  <h4>Observaciones</h4>
                  <p className="wz-summary-notes">{form.observaciones}</p>
                </div>
              )}

              {form.recurrencia && (
                <div className="wz-summary-section">
                  <h4><Calendar size={14} /> Recurrencia</h4>
                  <div className="wz-summary-grid">
                    <div><span>Frecuencia</span><strong>{form.recurrencia}</strong></div>
                    <div><span>Repeticiones</span><strong>{form.recurrencia_cantidad || 5} órdenes adicionales</strong></div>
                  </div>
                </div>
              )}

              {conflictos && conflictos.advertencias?.length > 0 && (
                <div className="wz-alert wz-alert-warn">
                  <AlertTriangle size={16} />
                  <div>
                    <strong>Advertencias</strong>
                    {conflictos.advertencias.map((c, i) => <p key={i}>{c.mensaje}</p>)}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      <div className="wz-footer">
        <button className="wz-btn-secondary" onClick={() => { clearDraft(); onCancel?.(); }} disabled={saving}>
          Cancelar
        </button>

        {step > 1 && (
          <button className="wz-btn-outline" onClick={back} disabled={saving}>
            <ArrowLeft size={15} /> Anterior
          </button>
        )}

        {step < 3 ? (
          <button className="wz-btn-primary" onClick={next}>
            Siguiente <ArrowRight size={15} />
          </button>
        ) : (
          <button className="wz-btn-primary" onClick={submit} disabled={saving || (conflictos && !conflictos.puede_crear)}>
            {saving ? "Creando..." : "Crear orden de mantenimiento"}
          </button>
        )}
      </div>
    </div>
  );
}
