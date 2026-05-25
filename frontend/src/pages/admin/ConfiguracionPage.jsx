// ============================================================
// PÁGINA: Configuración Inteligente SaaS
// Archivo: frontend/src/pages/admin/ConfiguracionPage.jsx
// Fase 34.1 - Configuración Inteligente SaaS PRO
// ============================================================

import React, { useEffect, useMemo, useState } from "react";
import {
  Upload,
  Save,
  Mail,
  DatabaseBackup,
  Palette,
  Image as ImageIcon,
  ShieldCheck,
  Bell,
  Wrench,
  Settings,
  Menu,
  X,
  CheckCircle2,
  AlertTriangle,
} from "lucide-react";
import AdminLayout from "./AdminLayout";
import { configuracionApi } from "../../api/configuracionApi";
import "../../styles/configuracion-saas-pro.css";

const API_BASE = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

const DEFAULT_CONFIG = {
  nombre_plataforma: "SGA SaaS PRO",
  logo_url: null,
  color_primario: "#2563eb",
  color_secundario: "#0f172a",
  color_acento: "#22c55e",
  smtp: {
    host: "",
    port: 587,
    username: "",
    password: "",
    from_email: "",
    from_name: "SGA SaaS PRO",
    use_tls: true,
    use_ssl: false,
  },
  backups: {
    habilitado: true,
    frecuencia: "DIARIO",
    hora: "02:00",
    retencion_dias: 30,
    incluir_evidencias: true,
    ruta_destino: "app/exports/backups",
  },
  evidencias: {
    max_mb: 15,
    formatos_permitidos: ["jpg", "jpeg", "png", "pdf", "webp"],
    requiere_descripcion: false,
    permitir_pdf: true,
    permitir_imagen: true,
    compresion_imagen: true,
  },
  mantenimiento: {
    dias_alerta_vencimiento: 3,
    permitir_reprogramacion: true,
    requiere_evidencia_finalizar: true,
    requiere_observacion_finalizar: true,
    estados_permitidos: ["PROGRAMADO", "ASIGNADO", "EN_PROCESO", "PAUSADO", "FINALIZADO", "ANULADO"],
  },
  notificaciones: {
    email_habilitado: true,
    whatsapp_habilitado: false,
    whatsapp_provider: "",
    whatsapp_token: "",
    notificar_asignacion: true,
    notificar_vencimiento: true,
    notificar_finalizacion: true,
    notificar_cliente: true,
    correos_copia: [],
  },
};

const TABS = [
  { id: "identidad", label: "Identidad", icon: ImageIcon },
  { id: "smtp", label: "SMTP", icon: Mail },
  { id: "backups", label: "Backups", icon: DatabaseBackup },
  { id: "evidencias", label: "Evidencias", icon: ShieldCheck },
  { id: "mantenimiento", label: "Mantenimiento", icon: Wrench },
  { id: "notificaciones", label: "Notificaciones", icon: Bell },
  { id: "colores", label: "Colores", icon: Palette },
];

function Toggle({ checked, onChange, label }) {
  return (
    <label className="cfg-toggle-row">
      <button
        type="button"
        className={`cfg-toggle ${checked ? "active" : ""}`}
        onClick={() => onChange(!checked)}
        aria-label={label}
      >
        <span />
      </button>
      <span>{label}</span>
    </label>
  );
}

export default function ConfiguracionPage() {
  const [config, setConfig] = useState(DEFAULT_CONFIG);
  const [activeTab, setActiveTab] = useState("identidad");
  const [menuOpen, setMenuOpen] = useState(false);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [logoFile, setLogoFile] = useState(null);
  const [logoPreview, setLogoPreview] = useState(null);
  const [testEmail, setTestEmail] = useState("");
  const [message, setMessage] = useState(null);

  const logoUrl = useMemo(() => {
    if (logoPreview) return logoPreview;
    if (!config.logo_url) return null;
    if (config.logo_url.startsWith("http")) return config.logo_url;
    return `${API_BASE}${config.logo_url}`;
  }, [config.logo_url, logoPreview]);

  useEffect(() => {
    cargarConfiguracion();
  }, []);

  const cargarConfiguracion = async () => {
    try {
      setLoading(true);
      const data = await configuracionApi.obtener();
      setConfig({ ...DEFAULT_CONFIG, ...data });
    } catch (error) {
      showMessage("error", "No fue posible cargar la configuración.");
    } finally {
      setLoading(false);
    }
  };

  const showMessage = (type, text) => {
    setMessage({ type, text });
    window.setTimeout(() => setMessage(null), 4500);
  };

  const updateRoot = (field, value) => {
    setConfig((prev) => ({ ...prev, [field]: value }));
  };

  const updateBlock = (block, field, value) => {
    setConfig((prev) => ({
      ...prev,
      [block]: {
        ...(prev[block] || {}),
        [field]: value,
      },
    }));
  };

  const handleLogoChange = (event) => {
    const file = event.target.files?.[0];
    if (!file) return;
    setLogoFile(file);
    setLogoPreview(URL.createObjectURL(file));
  };

  const subirLogo = async () => {
    if (!logoFile) {
      showMessage("error", "Selecciona primero un logo.");
      return;
    }

    try {
      setSaving(true);
      const res = await configuracionApi.subirLogo(logoFile);
      updateRoot("logo_url", res.data.logo_url);
      setLogoFile(null);
      setLogoPreview(null);
      showMessage("success", "Logo subido correctamente.");
    } catch (error) {
      showMessage("error", error?.response?.data?.detail || "No fue posible subir el logo.");
    } finally {
      setSaving(false);
    }
  };

  const guardar = async () => {
    try {
      setSaving(true);
      const saved = await configuracionApi.guardar(config);
      setConfig({ ...DEFAULT_CONFIG, ...saved });
      showMessage("success", "Configuración guardada en PostgreSQL.");
    } catch (error) {
      showMessage("error", error?.response?.data?.detail || "No fue posible guardar la configuración.");
    } finally {
      setSaving(false);
    }
  };

  const probarCorreo = async () => {
    if (!testEmail) {
      showMessage("error", "Escribe un correo destino para la prueba.");
      return;
    }

    try {
      setSaving(true);
      await configuracionApi.probarCorreo({
        to_email: testEmail,
        subject: "Prueba SMTP - SGA SaaS PRO",
        message: "El correo corporativo quedó configurado correctamente en SGA SaaS PRO.",
      });
      showMessage("success", "Correo de prueba enviado correctamente.");
    } catch (error) {
      showMessage("error", error?.response?.data?.detail || "No fue posible enviar el correo de prueba.");
    } finally {
      setSaving(false);
    }
  };

  const probarBackup = async () => {
    try {
      setSaving(true);
      await configuracionApi.probarBackup();
      showMessage("success", "Configuración de backup validada correctamente.");
    } catch (error) {
      showMessage("error", error?.response?.data?.detail || "No fue posible validar el backup.");
    } finally {
      setSaving(false);
    }
  };

  const renderTab = () => {
    if (activeTab === "identidad") {
      return (
        <section className="cfg-card">
          <div className="cfg-card-head">
            <div>
              <h2>Identidad de la plataforma</h2>
              <p>Logo real, nombre comercial y vista previa institucional.</p>
            </div>
            <ImageIcon size={24} />
          </div>

          <div className="cfg-grid two">
            <div className="cfg-field">
              <label>Nombre plataforma</label>
              <input value={config.nombre_plataforma} onChange={(e) => updateRoot("nombre_plataforma", e.target.value)} />
            </div>

            <div className="cfg-field">
              <label>Subir logo</label>
              <div className="cfg-upload-row">
                <input type="file" accept="image/png,image/jpeg,image/webp,image/svg+xml" onChange={handleLogoChange} />
                <button type="button" onClick={subirLogo} disabled={saving} className="cfg-btn secondary">
                  <Upload size={17} /> Subir
                </button>
              </div>
            </div>
          </div>

          <div className="cfg-logo-preview">
            {logoUrl ? <img src={logoUrl} alt="Logo plataforma" /> : <div className="cfg-empty-logo">Sin logo</div>}
            <div>
              <h3>{config.nombre_plataforma}</h3>
              <p>Preview del encabezado institucional para la plataforma.</p>
            </div>
          </div>
        </section>
      );
    }

    if (activeTab === "smtp") {
      return (
        <section className="cfg-card">
          <div className="cfg-card-head">
            <div>
              <h2>SMTP corporativo</h2>
              <p>Configura correo empresarial para notificaciones y pruebas reales.</p>
            </div>
            <Mail size={24} />
          </div>

          <div className="cfg-grid three">
            <div className="cfg-field"><label>Host SMTP</label><input value={config.smtp.host} onChange={(e) => updateBlock("smtp", "host", e.target.value)} placeholder="smtp.tudominio.com" /></div>
            <div className="cfg-field"><label>Puerto</label><input type="number" value={config.smtp.port} onChange={(e) => updateBlock("smtp", "port", Number(e.target.value))} /></div>
            <div className="cfg-field"><label>Nombre remitente</label><input value={config.smtp.from_name} onChange={(e) => updateBlock("smtp", "from_name", e.target.value)} /></div>
            <div className="cfg-field"><label>Usuario</label><input value={config.smtp.username} onChange={(e) => updateBlock("smtp", "username", e.target.value)} /></div>
            <div className="cfg-field"><label>Contraseña / App password</label><input type="password" value={config.smtp.password} onChange={(e) => updateBlock("smtp", "password", e.target.value)} /></div>
            <div className="cfg-field"><label>Correo remitente</label><input value={config.smtp.from_email} onChange={(e) => updateBlock("smtp", "from_email", e.target.value)} /></div>
          </div>

          <div className="cfg-switches">
            <Toggle checked={config.smtp.use_tls} onChange={(v) => updateBlock("smtp", "use_tls", v)} label="Usar TLS" />
            <Toggle checked={config.smtp.use_ssl} onChange={(v) => updateBlock("smtp", "use_ssl", v)} label="Usar SSL" />
          </div>

          <div className="cfg-test-row">
            <input value={testEmail} onChange={(e) => setTestEmail(e.target.value)} placeholder="correo@empresa.com" />
            <button type="button" onClick={probarCorreo} disabled={saving} className="cfg-btn primary"><Mail size={17} /> Probar envío</button>
          </div>
        </section>
      );
    }

    if (activeTab === "backups") {
      return (
        <section className="cfg-card">
          <div className="cfg-card-head"><div><h2>Backups automáticos</h2><p>Define frecuencia, hora, retención y ruta de almacenamiento.</p></div><DatabaseBackup size={24} /></div>
          <div className="cfg-grid three">
            <div className="cfg-field"><label>Frecuencia</label><select value={config.backups.frecuencia} onChange={(e) => updateBlock("backups", "frecuencia", e.target.value)}><option>DIARIO</option><option>SEMANAL</option><option>MENSUAL</option></select></div>
            <div className="cfg-field"><label>Hora</label><input type="time" value={config.backups.hora} onChange={(e) => updateBlock("backups", "hora", e.target.value)} /></div>
            <div className="cfg-field"><label>Retención días</label><input type="number" value={config.backups.retencion_dias} onChange={(e) => updateBlock("backups", "retencion_dias", Number(e.target.value))} /></div>
            <div className="cfg-field wide"><label>Ruta destino</label><input value={config.backups.ruta_destino} onChange={(e) => updateBlock("backups", "ruta_destino", e.target.value)} /></div>
          </div>
          <div className="cfg-switches"><Toggle checked={config.backups.habilitado} onChange={(v) => updateBlock("backups", "habilitado", v)} label="Backups habilitados" /><Toggle checked={config.backups.incluir_evidencias} onChange={(v) => updateBlock("backups", "incluir_evidencias", v)} label="Incluir evidencias" /></div>
          <button type="button" onClick={probarBackup} disabled={saving} className="cfg-btn secondary"><DatabaseBackup size={17} /> Validar backup</button>
        </section>
      );
    }

    if (activeTab === "evidencias") {
      const formatos = (config.evidencias.formatos_permitidos || []).join(", ");
      return (
        <section className="cfg-card">
          <div className="cfg-card-head"><div><h2>Parámetros de evidencias</h2><p>Controla formatos, peso máximo y reglas para fotos/PDF.</p></div><ShieldCheck size={24} /></div>
          <div className="cfg-grid two">
            <div className="cfg-field"><label>Peso máximo por archivo (MB)</label><input type="number" value={config.evidencias.max_mb} onChange={(e) => updateBlock("evidencias", "max_mb", Number(e.target.value))} /></div>
            <div className="cfg-field"><label>Formatos permitidos</label><input value={formatos} onChange={(e) => updateBlock("evidencias", "formatos_permitidos", e.target.value.split(",").map((x) => x.trim()).filter(Boolean))} /></div>
          </div>
          <div className="cfg-switches"><Toggle checked={config.evidencias.requiere_descripcion} onChange={(v) => updateBlock("evidencias", "requiere_descripcion", v)} label="Requiere descripción" /><Toggle checked={config.evidencias.permitir_pdf} onChange={(v) => updateBlock("evidencias", "permitir_pdf", v)} label="Permitir PDF" /><Toggle checked={config.evidencias.permitir_imagen} onChange={(v) => updateBlock("evidencias", "permitir_imagen", v)} label="Permitir imágenes" /><Toggle checked={config.evidencias.compresion_imagen} onChange={(v) => updateBlock("evidencias", "compresion_imagen", v)} label="Compresión de imagen" /></div>
        </section>
      );
    }

    if (activeTab === "mantenimiento") {
      return (
        <section className="cfg-card">
          <div className="cfg-card-head"><div><h2>Parámetros de mantenimiento</h2><p>Reglas operativas para vencimientos, cierre y reprogramación.</p></div><Wrench size={24} /></div>
          <div className="cfg-grid two">
            <div className="cfg-field"><label>Días alerta vencimiento</label><input type="number" value={config.mantenimiento.dias_alerta_vencimiento} onChange={(e) => updateBlock("mantenimiento", "dias_alerta_vencimiento", Number(e.target.value))} /></div>
            <div className="cfg-field"><label>Estados permitidos</label><input value={(config.mantenimiento.estados_permitidos || []).join(", ")} onChange={(e) => updateBlock("mantenimiento", "estados_permitidos", e.target.value.split(",").map((x) => x.trim()).filter(Boolean))} /></div>
          </div>
          <div className="cfg-switches"><Toggle checked={config.mantenimiento.permitir_reprogramacion} onChange={(v) => updateBlock("mantenimiento", "permitir_reprogramacion", v)} label="Permitir reprogramación" /><Toggle checked={config.mantenimiento.requiere_evidencia_finalizar} onChange={(v) => updateBlock("mantenimiento", "requiere_evidencia_finalizar", v)} label="Exigir evidencia al finalizar" /><Toggle checked={config.mantenimiento.requiere_observacion_finalizar} onChange={(v) => updateBlock("mantenimiento", "requiere_observacion_finalizar", v)} label="Exigir observación al finalizar" /></div>
        </section>
      );
    }

    if (activeTab === "notificaciones") {
      return (
        <section className="cfg-card">
          <div className="cfg-card-head"><div><h2>Notificaciones Email / WhatsApp</h2><p>Activa canales y eventos críticos del sistema.</p></div><Bell size={24} /></div>
          <div className="cfg-grid two">
            <div className="cfg-field"><label>Proveedor WhatsApp</label><input value={config.notificaciones.whatsapp_provider} onChange={(e) => updateBlock("notificaciones", "whatsapp_provider", e.target.value)} placeholder="Twilio, Meta, WATI..." /></div>
            <div className="cfg-field"><label>Token WhatsApp</label><input type="password" value={config.notificaciones.whatsapp_token} onChange={(e) => updateBlock("notificaciones", "whatsapp_token", e.target.value)} /></div>
            <div className="cfg-field wide"><label>Correos en copia separados por coma</label><input value={(config.notificaciones.correos_copia || []).join(", ")} onChange={(e) => updateBlock("notificaciones", "correos_copia", e.target.value.split(",").map((x) => x.trim()).filter(Boolean))} /></div>
          </div>
          <div className="cfg-switches"><Toggle checked={config.notificaciones.email_habilitado} onChange={(v) => updateBlock("notificaciones", "email_habilitado", v)} label="Email habilitado" /><Toggle checked={config.notificaciones.whatsapp_habilitado} onChange={(v) => updateBlock("notificaciones", "whatsapp_habilitado", v)} label="WhatsApp habilitado" /><Toggle checked={config.notificaciones.notificar_asignacion} onChange={(v) => updateBlock("notificaciones", "notificar_asignacion", v)} label="Asignación" /><Toggle checked={config.notificaciones.notificar_vencimiento} onChange={(v) => updateBlock("notificaciones", "notificar_vencimiento", v)} label="Vencimiento" /><Toggle checked={config.notificaciones.notificar_finalizacion} onChange={(v) => updateBlock("notificaciones", "notificar_finalizacion", v)} label="Finalización" /><Toggle checked={config.notificaciones.notificar_cliente} onChange={(v) => updateBlock("notificaciones", "notificar_cliente", v)} label="Notificar cliente" /></div>
        </section>
      );
    }

    return (
      <section className="cfg-card">
        <div className="cfg-card-head"><div><h2>Colores institucionales</h2><p>Personaliza la identidad visual SaaS.</p></div><Palette size={24} /></div>
        <div className="cfg-grid three">
          {["color_primario", "color_secundario", "color_acento"].map((field) => (
            <div className="cfg-field" key={field}>
              <label>{field.replace("color_", "Color ")}</label>
              <div className="cfg-color-row"><input type="color" value={config[field]} onChange={(e) => updateRoot(field, e.target.value)} /><input value={config[field]} onChange={(e) => updateRoot(field, e.target.value)} /></div>
            </div>
          ))}
        </div>
        <div className="cfg-theme-preview" style={{ "--cfg-primary": config.color_primario, "--cfg-secondary": config.color_secundario, "--cfg-accent": config.color_acento }}>
          <div className="cfg-theme-sidebar">SGA</div><div className="cfg-theme-content"><span>Dashboard</span><button>Acción principal</button></div>
        </div>
      </section>
    );
  };

  return (
    <AdminLayout>
      <div className="cfg-page">
        <div className="cfg-hero">
          <div>
            <span className="cfg-kicker"><Settings size={16} /> Fase 34.1</span>
            <h1>Configuración Inteligente SaaS</h1>
            <p>Centro profesional para identidad, correos, backups, evidencias, mantenimientos y notificaciones.</p>
          </div>
          <div className="cfg-actions">
            <button type="button" className="cfg-btn ghost" onClick={() => setMenuOpen(!menuOpen)}><Menu size={18} /> Menú</button>
            <button type="button" className="cfg-btn primary" onClick={guardar} disabled={saving || loading}><Save size={18} /> Guardar</button>
          </div>
        </div>

        {message && <div className={`cfg-alert ${message.type}`}>{message.type === "success" ? <CheckCircle2 size={18} /> : <AlertTriangle size={18} />} {message.text}</div>}

        <div className="cfg-layout">
          <aside className={`cfg-tabs ${menuOpen ? "open" : ""}`}>
            <div className="cfg-tabs-head"><strong>Configuración</strong><button onClick={() => setMenuOpen(false)}><X size={18} /></button></div>
            {TABS.map((tab) => {
              const Icon = tab.icon;
              return <button key={tab.id} type="button" className={activeTab === tab.id ? "active" : ""} onClick={() => { setActiveTab(tab.id); setMenuOpen(false); }}><Icon size={18} /> {tab.label}</button>;
            })}
          </aside>
          <main className="cfg-content">{loading ? <div className="cfg-loading">Cargando configuración...</div> : renderTab()}</main>
        </div>
      </div>
    </AdminLayout>
  );
}
