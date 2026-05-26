// =========================================================
// CONFIGURACIÓN SISTEMA - CENTRO DE CONTROL
// Archivo: frontend/src/pages/admin/ConfiguracionSistemaPage.jsx
// =========================================================

import { useNavigate } from "react-router-dom";
import {
  Settings,
  SlidersHorizontal,
  Archive,
  Mail,
  ShieldCheck,
  Activity,
  Server,
  ArrowRight,
} from "lucide-react";

import "../../styles/configuracion-sistema.css";

export default function ConfiguracionSistemaPage() {
  const navigate = useNavigate();

  const modulos = [
    {
      titulo: "Configuración General",
      descripcion: "Parámetros base del sistema, seguridad, evidencias y mantenimiento.",
      ruta: "/admin/configuracion",
      icono: Settings,
      estado: "Activo",
    },
    {
      titulo: "Configuración Inteligente",
      descripcion: "Identidad SaaS, logo, SMTP corporativo, colores, backups y notificaciones.",
      ruta: "/admin/configuracion-inteligente",
      icono: SlidersHorizontal,
      estado: "Activo",
    },
    {
      titulo: "Backups Inteligentes",
      descripcion: "Respaldos de PostgreSQL, evidencias/uploads y paquetes ZIP descargables.",
      ruta: "/admin/backups",
      icono: Archive,
      estado: "Activo",
    },
    {
      titulo: "SMTP Inteligente",
      descripcion: "Correo corporativo, pruebas SMTP, plantillas HTML y trazabilidad de envíos.",
      ruta: "/admin/smtp-inteligente",
      icono: Mail,
      estado: "Activo",
    },
    {
      titulo: "Automatización SaaS",
      descripcion: "Scheduler, tareas recurrentes, jobs automáticos y módulos ON/OFF.",
      ruta: "/admin/automatizacion",
      icono: Activity,
      estado: "Activo",
    },
    {
      titulo: "DevOps / Monitor",
      descripcion: "Espacio reservado para monitoreo VPS, Docker, PostgreSQL, logs y salud del sistema.",
      ruta: "/admin/configuracion-sistema",
      icono: Server,
      estado: "Próximo",
    },
    {
      titulo: "Seguridad Sistema",
      descripcion: "Auditoría, permisos, políticas de acceso y endurecimiento de plataforma.",
      ruta: "/admin/auditoria",
      icono: ShieldCheck,
      estado: "Activo",
    },
  ];

  return (
    <main className="cfgsys-page">
      <section className="cfgsys-hero">
        <div>
          <p className="cfgsys-kicker">SGA EMPRESARIAL · ADMIN SAAS PRO</p>
          <h1>Configuración Sistema</h1>
          <p>
            Centro unificado para configuración, automatización, backups, SMTP,
            seguridad y operación técnica del SaaS.
          </p>
        </div>
      </section>

      <section className="cfgsys-grid">
        {modulos.map((modulo) => {
          const Icon = modulo.icono;

          return (
            <button
              key={modulo.titulo}
              className="cfgsys-card"
              type="button"
              onClick={() => navigate(modulo.ruta)}
            >
              <div className="cfgsys-card-top">
                <span className="cfgsys-icon"><Icon size={22} /></span>
                <span className={`cfgsys-status ${modulo.estado === "Próximo" ? "next" : "active"}`}>
                  {modulo.estado}
                </span>
              </div>

              <h2>{modulo.titulo}</h2>
              <p>{modulo.descripcion}</p>

              <div className="cfgsys-card-action">
                <span>Abrir módulo</span>
                <ArrowRight size={17} />
              </div>
            </button>
          );
        })}
      </section>
    </main>
  );
}
