// =========================================================
// CONFIGURACIÓN SISTEMA SaaS PRO
// Archivo:
// frontend/src/pages/admin/ConfiguracionSistemaPage.jsx
// =========================================================

import { useNavigate } from "react-router-dom";

import {
  Settings,
  SlidersHorizontal,
  Archive,
  Mail,
  ShieldCheck,
  Cpu,
  Menu,
  Activity,
  FileSearch,
  ServerCog,
  CalendarClock,
  DatabaseBackup,
  Building2,
} from "lucide-react";

import AdminLayout from "./AdminLayout";

import "../../styles/configuracion-sistema.css";

export default function ConfiguracionSistemaPage() {

  const navigate = useNavigate();

  // =======================================================
  // CARDS
  // =======================================================

  const cards = [

    {
      titulo: "Centro Sistema",
      descripcion:
        "Panel central de administración del sistema SaaS.",
      icono: <Cpu size={24} />,
      ruta: "/admin/configuracion",
      estado: "Activo",
    },

    {
      titulo: "Configuración General",
      descripcion:
        "Parámetros globales, branding, logos y configuración.",
      icono: <Settings size={24} />,
      ruta: "/admin/configuracion",
      estado: "Activo",
    },

    {
      titulo: "Recovery & Restore PRO",
      descripcion:
        "Backups PostgreSQL, restauración inteligente y recuperación del sistema.",
      icono: <DatabaseBackup size={24} />,
      ruta: "/admin/recovery",
      estado: "Activo",
    },

    {
      titulo: "Configuración Inteligente",
      descripcion:
        "Automatización SaaS, scheduler y comportamiento inteligente.",
      icono: <SlidersHorizontal size={24} />,
      ruta: "/admin/configuracion-inteligente",
      estado: "Activo",
    },

    {
      titulo: "Backups Inteligentes",
      descripcion:
        "Respaldos PostgreSQL, uploads y restauración segura.",
      icono: <Archive size={24} />,
      ruta: "/admin/backups",
      estado: "Activo",
    },

    {
      titulo: "SMTP Inteligente",
      descripcion:
        "Correos corporativos, plantillas y notificaciones.",
      icono: <Mail size={24} />,
      ruta: "/admin/smtp-inteligente",
      estado: "Activo",
    },

    {
      titulo: "Monitor VPS + PostgreSQL",
      descripcion:
        "Estado del servidor, Docker, CPU, RAM y PostgreSQL.",
      icono: <Activity size={24} />,
      ruta: "/admin/monitor-vps",
      estado: "Activo",
    },

    {
      titulo: "Logs Inteligentes",
      descripcion:
        "Eventos, errores, trazabilidad y monitoreo.",
      icono: <FileSearch size={24} />,
      ruta: "/admin/logs-inteligentes",
      estado: "Activo",
    },

    {
      titulo: "DevOps SaaS PRO",
      descripcion:
        "Contenedores, infraestructura y salud del sistema.",
      icono: <ServerCog size={24} />,
      ruta: "/admin/devops",
      estado: "Activo",
    },

    {
      titulo: "Seguridad PRO",
      descripcion:
        "Auditoría, permisos y hardening.",
      icono: <ShieldCheck size={24} />,
      ruta: "/admin/auditoria",
      estado: "Activo",
    },

    {
      titulo: "Scheduler Inteligente",
      descripcion:
        "Automatización avanzada de mantenimientos.",
      icono: <CalendarClock size={24} />,
      ruta: "/admin/scheduler-inteligente",
      estado: "Activo",
    },

    {
      titulo: "Multiempresa Enterprise",
      descripcion:
        "Gestión de múltiples empresas y funcionalidades empresariales.",
      icono: <Building2 size={24} />,
      ruta: "/admin/multiempresa-enterprise",
      estado: "Activo",
    }

  ];

  return (
    <AdminLayout>

      <div className="config-sistema-page">

        {/* ================================================= */}
        {/* HEADER */}
        {/* ================================================= */}

        <div className="config-sistema-header">

          <div className="config-header-top">

            <div>

              <span className="config-badge">
                CONFIGURACIÓN SISTEMA
              </span>

              <h1>
                Centro de Configuración SaaS PRO
              </h1>

              <p>
                Gestión centralizada de módulos
                inteligentes, automatización,
                seguridad y servicios empresariales.
              </p>

            </div>

            {/* BOTÓN RESPONSIVE */}

            <button
              className="config-menu-btn"
            >
              <Menu size={20} />
            </button>

          </div>

        </div>

        {/* ================================================= */}
        {/* GRID */}
        {/* ================================================= */}

        <div className="config-grid">

          {cards.map((card, index) => (

            <div
              key={index}
              className="config-card"
              onClick={() => navigate(card.ruta)}
            >

              <div className="config-card-top">

                <div className="config-icon">
                  {card.icono}
                </div>

                <span className="config-status">
                  {card.estado}
                </span>

              </div>

              <h3>
                {card.titulo}
              </h3>

              <p>
                {card.descripcion}
              </p>

            </div>

          ))}

        </div>

      </div>

    </AdminLayout>
  );
}