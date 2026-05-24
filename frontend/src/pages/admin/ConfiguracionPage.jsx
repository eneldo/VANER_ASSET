// ============================================================
// PÁGINA: Configuración PRO SaaS
// Archivo: frontend/src/pages/admin/ConfiguracionPage.jsx
// Descripción:
//   Panel profesional responsive para administrar configuración
//   global de plataforma, seguridad, evidencias, backups,
//   mantenimiento y notificaciones.
// ============================================================

import { useEffect, useMemo, useState } from "react";
import {
  Save,
  RotateCcw,
  Settings,
  ShieldCheck,
  ImagePlus,
  DatabaseBackup,
  Wrench,
  BellRing,
  Loader2,
} from "lucide-react";
import axios from "../../api/axios";
import "../../styles/configuracion-pro.css";

const DEFAULT_FORM = {
  nombre_plataforma: "SGA PRO SaaS",
  empresa_propietaria: "",
  nit: "",
  correo_soporte: "",
  telefono_soporte: "",
  url_plataforma: "",
  logo_url: "",
  color_primario: "#2563eb",
  color_secundario: "#0f172a",

  intentos_login: 5,
  minutos_bloqueo: 15,
  expiracion_token_min: 60,
  exigir_password_seguro: true,
  doble_factor_activo: false,
  auditoria_activa: true,

  max_tamano_evidencia_mb: 10,
  permitir_pdf: true,
  permitir_imagenes: true,
  ruta_evidencias: "app/uploads/evidencias",
  retencion_evidencias_dias: 365,

  backups_activos: true,
  frecuencia_backup: "DIARIO",
  hora_backup: "02:00",
  ruta_backup: "app/backups",
  retencion_backups_dias: 30,

  dias_alerta_mantenimiento: 7,
  permitir_mantenimiento_vencido: true,
  requiere_evidencia_cierre: true,
  requiere_observacion_cierre: true,
  estados_mantenimiento: "PROGRAMADO,ASIGNADO,EN_PROCESO,PAUSADO,FINALIZADO,ANULADO",

  notificaciones_activas: true,
  notificar_email: true,
  notificar_whatsapp: false,
  dias_antes_notificar: 3,
  email_remitente: "",
  smtp_host: "",
  smtp_puerto: "",
  smtp_usuario: "",
  smtp_password: "",
};

const TABS = [
  { id: "plataforma", label: "Datos plataforma", icon: Settings },
  { id: "seguridad", label: "Seguridad", icon: ShieldCheck },
  { id: "evidencias", label: "Evidencias", icon: ImagePlus },
  { id: "backups", label: "Backups", icon: DatabaseBackup },
  { id: "mantenimiento", label: "Mantenimiento", icon: Wrench },
  { id: "notificaciones", label: "Notificaciones", icon: BellRing },
];

function Field({ label, name, value, onChange, type = "text", placeholder = "", min }) {
  return (
    <label className="cfg-field">
      <span>{label}</span>
      <input
        type={type}
        name={name}
        value={value ?? ""}
        placeholder={placeholder}
        min={min}
        onChange={onChange}
      />
    </label>
  );
}

function Toggle({ label, name, checked, onChange, help }) {
  return (
    <label className="cfg-toggle">
      <input type="checkbox" name={name} checked={!!checked} onChange={onChange} />
      <div>
        <strong>{label}</strong>
        {help && <small>{help}</small>}
      </div>
    </label>
  );
}

export default function ConfiguracionPage() {
  const [activeTab, setActiveTab] = useState("plataforma");
  const [form, setForm] = useState(DEFAULT_FORM);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState(null);

  const activeMeta = useMemo(() => TABS.find((tab) => tab.id === activeTab), [activeTab]);

  const loadConfig = async () => {
    try {
      setLoading(true);
      const { data } = await axios.get("/configuracion/");
      setForm({ ...DEFAULT_FORM, ...data, smtp_password: data.smtp_password || "" });
    } catch (error) {
      setMessage({ type: "error", text: "No fue posible cargar la configuración." });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadConfig();
  }, []);

  const handleChange = (event) => {
    const { name, value, type, checked } = event.target;
    setForm((prev) => ({
      ...prev,
      [name]: type === "checkbox" ? checked : type === "number" ? Number(value) : value,
    }));
  };

  const handleSave = async () => {
    try {
      setSaving(true);
      setMessage(null);
      const payload = { ...form, smtp_puerto: form.smtp_puerto ? Number(form.smtp_puerto) : null };
      const { data } = await axios.put("/configuracion/", payload);
      setForm({ ...DEFAULT_FORM, ...data });
      setMessage({ type: "success", text: "Configuración guardada correctamente en PostgreSQL." });
    } catch (error) {
      setMessage({ type: "error", text: error?.response?.data?.detail || "Error al guardar la configuración." });
    } finally {
      setSaving(false);
    }
  };

  const handleRestore = async () => {
    const ok = window.confirm("¿Restaurar la configuración PRO por defecto? No se eliminarán datos operativos.");
    if (!ok) return;

    try {
      setSaving(true);
      const { data } = await axios.post("/configuracion/restaurar");
      setForm({ ...DEFAULT_FORM, ...data });
      setMessage({ type: "success", text: "Configuración restaurada correctamente." });
    } catch (error) {
      setMessage({ type: "error", text: "No fue posible restaurar la configuración." });
    } finally {
      setSaving(false);
    }
  };

  return (
    <section className="cfg-page">
      <header className="cfg-hero">
        <div>
          <p className="cfg-eyebrow">SGA SaaS Enterprise</p>
          <h1>Configuración PRO</h1>
          <span>Administra parámetros globales de plataforma, seguridad, evidencias, backups, mantenimiento y notificaciones.</span>
        </div>
        <div className="cfg-actions">
          <button className="cfg-btn ghost" onClick={handleRestore} disabled={saving}>
            <RotateCcw size={18} /> Restaurar
          </button>
          <button className="cfg-btn primary" onClick={handleSave} disabled={saving}>
            {saving ? <Loader2 className="spin" size={18} /> : <Save size={18} />} Guardar
          </button>
        </div>
      </header>

      {message && <div className={`cfg-alert ${message.type}`}>{message.text}</div>}

      <div className="cfg-layout">
        <aside className="cfg-tabs">
          {TABS.map((tab) => {
            const Icon = tab.icon;
            return (
              <button key={tab.id} className={activeTab === tab.id ? "active" : ""} onClick={() => setActiveTab(tab.id)}>
                <Icon size={18} /> {tab.label}
              </button>
            );
          })}
        </aside>

        <main className="cfg-card">
          <div className="cfg-card-title">
            {activeMeta && <activeMeta.icon size={22} />}
            <h2>{activeMeta?.label}</h2>
          </div>

          {loading ? (
            <div className="cfg-loading"><Loader2 className="spin" /> Cargando configuración...</div>
          ) : (
            <>
              {activeTab === "plataforma" && (
                <div className="cfg-grid">
                  <Field label="Nombre plataforma" name="nombre_plataforma" value={form.nombre_plataforma} onChange={handleChange} />
                  <Field label="Empresa propietaria" name="empresa_propietaria" value={form.empresa_propietaria} onChange={handleChange} />
                  <Field label="NIT" name="nit" value={form.nit} onChange={handleChange} />
                  <Field label="Correo soporte" name="correo_soporte" value={form.correo_soporte} onChange={handleChange} />
                  <Field label="Teléfono soporte" name="telefono_soporte" value={form.telefono_soporte} onChange={handleChange} />
                  <Field label="URL plataforma" name="url_plataforma" value={form.url_plataforma} onChange={handleChange} />
                  <Field label="Logo URL" name="logo_url" value={form.logo_url} onChange={handleChange} />
                  <Field label="Color primario" name="color_primario" type="color" value={form.color_primario} onChange={handleChange} />
                  <Field label="Color secundario" name="color_secundario" type="color" value={form.color_secundario} onChange={handleChange} />
                </div>
              )}

              {activeTab === "seguridad" && (
                <div className="cfg-grid">
                  <Field label="Intentos login" name="intentos_login" type="number" min="1" value={form.intentos_login} onChange={handleChange} />
                  <Field label="Minutos bloqueo" name="minutos_bloqueo" type="number" min="1" value={form.minutos_bloqueo} onChange={handleChange} />
                  <Field label="Expiración token min" name="expiracion_token_min" type="number" min="5" value={form.expiracion_token_min} onChange={handleChange} />
                  <Toggle label="Exigir contraseña segura" name="exigir_password_seguro" checked={form.exigir_password_seguro} onChange={handleChange} />
                  <Toggle label="Doble factor activo" name="doble_factor_activo" checked={form.doble_factor_activo} onChange={handleChange} />
                  <Toggle label="Auditoría activa" name="auditoria_activa" checked={form.auditoria_activa} onChange={handleChange} />
                </div>
              )}

              {activeTab === "evidencias" && (
                <div className="cfg-grid">
                  <Field label="Tamaño máximo MB" name="max_tamano_evidencia_mb" type="number" min="1" value={form.max_tamano_evidencia_mb} onChange={handleChange} />
                  <Field label="Ruta evidencias" name="ruta_evidencias" value={form.ruta_evidencias} onChange={handleChange} />
                  <Field label="Retención días" name="retencion_evidencias_dias" type="number" min="1" value={form.retencion_evidencias_dias} onChange={handleChange} />
                  <Toggle label="Permitir PDF" name="permitir_pdf" checked={form.permitir_pdf} onChange={handleChange} />
                  <Toggle label="Permitir imágenes" name="permitir_imagenes" checked={form.permitir_imagenes} onChange={handleChange} />
                </div>
              )}

              {activeTab === "backups" && (
                <div className="cfg-grid">
                  <Toggle label="Backups activos" name="backups_activos" checked={form.backups_activos} onChange={handleChange} />
                  <label className="cfg-field">
                    <span>Frecuencia backup</span>
                    <select name="frecuencia_backup" value={form.frecuencia_backup} onChange={handleChange}>
                      <option value="DIARIO">Diario</option>
                      <option value="SEMANAL">Semanal</option>
                      <option value="MENSUAL">Mensual</option>
                    </select>
                  </label>
                  <Field label="Hora backup" name="hora_backup" type="time" value={form.hora_backup} onChange={handleChange} />
                  <Field label="Ruta backup" name="ruta_backup" value={form.ruta_backup} onChange={handleChange} />
                  <Field label="Retención días" name="retencion_backups_dias" type="number" min="1" value={form.retencion_backups_dias} onChange={handleChange} />
                </div>
              )}

              {activeTab === "mantenimiento" && (
                <div className="cfg-grid">
                  <Field label="Días alerta mantenimiento" name="dias_alerta_mantenimiento" type="number" min="1" value={form.dias_alerta_mantenimiento} onChange={handleChange} />
                  <Field label="Estados mantenimiento" name="estados_mantenimiento" value={form.estados_mantenimiento} onChange={handleChange} />
                  <Toggle label="Permitir mantenimiento vencido" name="permitir_mantenimiento_vencido" checked={form.permitir_mantenimiento_vencido} onChange={handleChange} />
                  <Toggle label="Requiere evidencia al cierre" name="requiere_evidencia_cierre" checked={form.requiere_evidencia_cierre} onChange={handleChange} />
                  <Toggle label="Requiere observación al cierre" name="requiere_observacion_cierre" checked={form.requiere_observacion_cierre} onChange={handleChange} />
                </div>
              )}

              {activeTab === "notificaciones" && (
                <div className="cfg-grid">
                  <Toggle label="Notificaciones activas" name="notificaciones_activas" checked={form.notificaciones_activas} onChange={handleChange} />
                  <Toggle label="Notificar por email" name="notificar_email" checked={form.notificar_email} onChange={handleChange} />
                  <Toggle label="Notificar por WhatsApp" name="notificar_whatsapp" checked={form.notificar_whatsapp} onChange={handleChange} />
                  <Field label="Días antes de notificar" name="dias_antes_notificar" type="number" min="1" value={form.dias_antes_notificar} onChange={handleChange} />
                  <Field label="Email remitente" name="email_remitente" value={form.email_remitente} onChange={handleChange} />
                  <Field label="SMTP host" name="smtp_host" value={form.smtp_host} onChange={handleChange} />
                  <Field label="SMTP puerto" name="smtp_puerto" type="number" value={form.smtp_puerto} onChange={handleChange} />
                  <Field label="SMTP usuario" name="smtp_usuario" value={form.smtp_usuario} onChange={handleChange} />
                  <Field label="SMTP password" name="smtp_password" type="password" value={form.smtp_password} onChange={handleChange} />
                </div>
              )}
            </>
          )}
        </main>
      </div>
    </section>
  );
}
