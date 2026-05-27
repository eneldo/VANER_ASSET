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
} from "lucide-react";

import AdminLayout from "./AdminLayout";

import "../../styles/configuracion-sistema.css";

export default function ConfiguracionSistemaPage() {
  const navigate = useNavigate();

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
        "Parámetros generales, logos, SMTP y configuración global.",
      icono: <Settings size={24} />,
      ruta: "/admin/configuracion",
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
        "Correos corporativos, plantillas, pruebas y notificaciones.",
      icono: <Mail size={24} />,
      ruta: "/admin/smtp-inteligente",
      estado: "Activo",
    },

    {
      titulo: "Monitor VPS + PostgreSQL",
      descripcion:
        "Estado del servidor, Docker, CPU, RAM, disco y PostgreSQL.",
      icono: <Activity size={24} />,
      ruta: "/admin/monitor-vps",
      estado: "Activo",
    },

    {
      titulo: "Seguridad PRO",
      descripcion:
        "Auditoría, permisos, hardening y monitoreo.",
      icono: <ShieldCheck size={24} />,
      ruta: "/admin/auditoria",
      estado: "Activo",
    },
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

              <h1>Centro de Configuración SaaS PRO</h1>

              <p>
                Gestión centralizada de módulos inteligentes,
                automatización, seguridad y servicios empresariales.
              </p>
            </div>

            {/* ================================================= */}
            {/* BOTÓN HAMBURGUESA */}
            {/* ================================================= */}

            <button
              className="config-menu-btn"
              onClick={() => {
                const event = new CustomEvent("toggle-sidebar");
                window.dispatchEvent(event);
              }}
            >
              <Menu size={22} />
              <span>Menú</span>
            </button>

          </div>
        </div>

        {/* ================================================= */}
        {/* GRID */}
        {/* ================================================= */}

        <div className="config-grid">

          {cards.map((item, index) => (
            <div
              key={index}
              className="config-card"
              onClick={() => navigate(item.ruta)}
            >

              <div className="config-card-top">

                <div className="config-icon">
                  {item.icono}
                </div>

                <span className="config-status">
                  {item.estado}
                </span>

              </div>

              <h3>{item.titulo}</h3>

              <p>{item.descripcion}</p>

              <div className="config-arrow">
                →
              </div>

            </div>
          ))}

        </div>
      </div>
    </AdminLayout>
  );
}