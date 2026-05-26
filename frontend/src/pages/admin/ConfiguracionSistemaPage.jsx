// =========================================================
// CONFIGURACIÓN SISTEMA - SGA SaaS PRO
// Archivo: frontend/src/pages/admin/ConfiguracionSistemaPage.jsx
// Agrupa configuración, automatización, backups, SMTP y futuros módulos.
// =========================================================

import { useNavigate } from "react-router-dom";
import {
  Settings,
  SlidersHorizontal,
  Archive,
  Mail,
  Activity,
  Server,
  ShieldCheck,
  MessageCircle,
  FileText,
  ChevronRight,
} from "lucide-react";

import "../../styles/configuracion-sistema.css";

export default function ConfiguracionSistemaPage() {
  const navigate = useNavigate();

  const modulos = [
    {
      titulo: "Configuración General",
      descripcion: "Parámetros principales del sistema y opciones base.",
      icono: Settings,
      ruta: "/admin/configuracion",
      estado: "Activo",
    },
    {
      titulo: "Configuración Inteligente",
      descripcion: "Logo, SMTP base, colores, evidencias, backups y notificaciones.",
      icono: SlidersHorizontal,
      ruta: "/admin/configuracion-inteligente",
      estado: "Activo",
    },
    {
      titulo: "Automatización SaaS",
      descripcion: "Scheduler, tareas automáticas, estados y módulos ON/OFF.",
      icono: Activity,
      ruta: "/admin/automatizacion",
      estado: "Activo",
    },
    {
      titulo: "Backups Inteligentes",
      descripcion: "Respaldo de PostgreSQL, evidencias y paquetes descargables.",
      icono: Archive,
      ruta: "/admin/backups",
      estado: "Activo",
    },
    {
      titulo: "SMTP Inteligente",
      descripcion: "Correos corporativos, plantillas, pruebas y notificaciones.",
      icono: Mail,
      ruta: "/admin/smtp-inteligente",
      estado: "Activo",
    },
    {
      titulo: "WhatsApp",
      descripcion: "Preparado para integración con proveedor WhatsApp empresarial.",
      icono: MessageCircle,
      ruta: "#",
      estado: "Próximamente",
      disabled: true,
    },
    {
      titulo: "Monitor / DevOps",
      descripcion: "Estado de VPS, servicios, PostgreSQL, API y frontend.",
      icono: Server,
      ruta: "#",
      estado: "Próximamente",
      disabled: true,
    },
    {
      titulo: "Logs Inteligentes",
      descripcion: "Auditoría técnica, errores, eventos y trazabilidad operativa.",
      icono: FileText,
      ruta: "#",
      estado: "Próximamente",
      disabled: true,
    },
    {
      titulo: "Seguridad Sistema",
      descripcion: "Hardening, políticas, sesiones, recuperación y control avanzado.",
      icono: ShieldCheck,
      ruta: "#",
      estado: "Próximamente",
      disabled: true,
    },
  ];

  const abrirModulo = (modulo) => {
    if (modulo.disabled || modulo.ruta === "#") return;
    navigate(modulo.ruta);
  };

  return (
    <main className="config-sistema-page">
      <section className="config-sistema-hero">
        <div>
          <p className="config-sistema-kicker">SGA EMPRESARIAL · SISTEMA</p>
          <h1>Configuración Sistema</h1>
          <p>
            Centro unificado para módulos técnicos, automatización, backups,
            SMTP, monitoreo y futuras integraciones SaaS PRO.
          </p>
        </div>
      </section>

      <section className="config-sistema-grid">
        {modulos.map((modulo) => {
          const Icon = modulo.icono;
          return (
            <button
              key={modulo.titulo}
              type="button"
              className={`config-sistema-card ${modulo.disabled ? "disabled" : ""}`}
              onClick={() => abrirModulo(modulo)}
              disabled={modulo.disabled}
            >
              <div className="config-sistema-icon">
                <Icon size={22} />
              </div>

              <div className="config-sistema-content">
                <div className="config-sistema-title-row">
                  <h3>{modulo.titulo}</h3>
                  <span className={modulo.disabled ? "badge-pending" : "badge-active"}>
                    {modulo.estado}
                  </span>
                </div>
                <p>{modulo.descripcion}</p>
              </div>

              {!modulo.disabled && <ChevronRight size={20} className="config-sistema-arrow" />}
            </button>
          );
        })}
      </section>
    </main>
  );
}
