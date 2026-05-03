// =========================================================
// SIDEBAR PRO SGA
// Menú lateral según rol del usuario
// =========================================================

import {
  LayoutDashboard,
  Building2,
  MapPin,
  MonitorCog,
  Wrench,
  Image,
  Users,
  FileText,
  Settings,
  LogOut,
  Tags,
  UserCog,
} from "lucide-react";

import "../styles/sidebar.css";

export default function Sidebar({ user, onLogout }) {
  return (
    <aside className="sga-sidebar">
      <div className="sga-brand">
        <div className="sga-logo">SGA</div>
        <div>
          <h2>SGA PRO</h2>
          <p>Gestión de Activos</p>
        </div>
      </div>

      <p className="sga-menu-title">MÓDULO PRINCIPAL</p>

      <nav className="sga-menu">
        <a className="sga-menu-item active">
          <LayoutDashboard size={18} />
          Dashboard
        </a>

        {user?.rol === "ADMIN" && (
          <>
            <a className="sga-menu-item">
              <Building2 size={18} />
              Empresas / Cliente
            </a>

            <a className="sga-menu-item">
              <MapPin size={18} />
              Sedes
            </a>

            <a className="sga-menu-item">
              <Tags size={18} />
              Categorías
            </a>

            <a className="sga-menu-item">
              <UserCog size={18} />
              Técnicos
            </a>

            <a className="sga-menu-item">
              <Users size={18} />
              Usuarios y Permisos
            </a>
          </>
        )}

        <a className="sga-menu-item">
          <MonitorCog size={18} />
          Equipos
        </a>

        <a className="sga-menu-item">
          <Wrench size={18} />
          Mantenimientos
        </a>

        <a className="sga-menu-item">
          <Image size={18} />
          Evidencias
        </a>

        <a className="sga-menu-item">
          <FileText size={18} />
          Reportes
        </a>

        {user?.rol === "ADMIN" && (
          <a className="sga-menu-item">
            <Settings size={18} />
            Configuración
          </a>
        )}
      </nav>

      <div className="sga-user-card">
        <div className="sga-user-avatar">
          {user?.nombre_completo?.substring(0, 2).toUpperCase() || "US"}
        </div>

        <div>
          <strong>{user?.nombre_completo || "Usuario"}</strong>
          <span>{user?.rol}</span>
        </div>
      </div>

      <button className="sga-logout" onClick={onLogout}>
        <LogOut size={18} />
        Cerrar sesión
      </button>
    </aside>
  );
}