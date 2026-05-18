// =========================================================
// SIDEBAR RESPONSIVE PRO SGA
// Archivo: frontend/src/components/Sidebar.jsx
// =========================================================

import { NavLink, useNavigate } from "react-router-dom";
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
  ShieldCheck,
  X,
} from "lucide-react";

import "../styles/sidebar.css";

export default function Sidebar({ user, onLogout, isOpen = false, onClose }) {
  const navigate = useNavigate();

  let userSeguro = user;

  if (!userSeguro) {
    try {
      userSeguro = JSON.parse(localStorage.getItem("user"));
    } catch {
      userSeguro = null;
    }
  }

  const rol = String(userSeguro?.rol || "").toUpperCase();

  const esAdmin = rol === "ADMIN";
  const esTecnico = rol === "TECNICO";
  const esCoordinador = rol === "COORDINADOR";

  const closeMobile = () => {
    if (typeof onClose === "function") onClose();
  };

  const handleLogout = () => {
    if (typeof onLogout === "function") {
      onLogout();
    } else {
      localStorage.removeItem("token");
      localStorage.removeItem("access_token");
      localStorage.removeItem("refresh_token");
      localStorage.removeItem("user");
    }

    navigate("/");
  };

  if (esCoordinador) {
    navigate("/coordinador/dashboard");
    return null;
  }

  return (
    <aside className={`sga-sidebar ${isOpen ? "open" : ""}`}>
      <button
        className="sga-sidebar-close"
        onClick={closeMobile}
        aria-label="Cerrar menú"
      >
        <X size={20} />
      </button>

      <div className="sga-brand">
        <div className="sga-logo">SGA</div>

        <div>
          <h2>SGA PRO</h2>
          <p>Gestión de Activos</p>
        </div>
      </div>

      <p className="sga-menu-title">MÓDULO PRINCIPAL</p>

      <nav className="sga-menu">
        <NavLink
          to={esTecnico ? "/tecnico/dashboard" : "/admin/dashboard"}
          onClick={closeMobile}
          className={({ isActive }) =>
            isActive ? "sga-menu-item active" : "sga-menu-item"
          }
        >
          <LayoutDashboard size={18} />
          Dashboard
        </NavLink>

        {esAdmin && (
          <>
            <NavLink to="/admin/empresas" onClick={closeMobile} className={({ isActive }) => isActive ? "sga-menu-item active" : "sga-menu-item"}>
              <Building2 size={18} />
              Empresas / Cliente
            </NavLink>

            <NavLink to="/admin/sedes" onClick={closeMobile} className={({ isActive }) => isActive ? "sga-menu-item active" : "sga-menu-item"}>
              <MapPin size={18} />
              Sedes
            </NavLink>

            <NavLink to="/admin/categorias" onClick={closeMobile} className={({ isActive }) => isActive ? "sga-menu-item active" : "sga-menu-item"}>
              <Tags size={18} />
              Categorías
            </NavLink>

            <NavLink to="/admin/tecnicos" onClick={closeMobile} className={({ isActive }) => isActive ? "sga-menu-item active" : "sga-menu-item"}>
              <UserCog size={18} />
              Técnicos
            </NavLink>

            <NavLink to="/admin/usuarios" onClick={closeMobile} className={({ isActive }) => isActive ? "sga-menu-item active" : "sga-menu-item"}>
              <Users size={18} />
              Usuarios y Permisos
            </NavLink>

            <NavLink to="/admin/equipos" onClick={closeMobile} className={({ isActive }) => isActive ? "sga-menu-item active" : "sga-menu-item"}>
              <MonitorCog size={18} />
              Equipos
            </NavLink>

            <NavLink to="/admin/mantenimientos" onClick={closeMobile} className={({ isActive }) => isActive ? "sga-menu-item active" : "sga-menu-item"}>
              <Wrench size={18} />
              Mantenimientos
            </NavLink>

            <NavLink to="/admin/evidencias" onClick={closeMobile} className={({ isActive }) => isActive ? "sga-menu-item active" : "sga-menu-item"}>
              <Image size={18} />
              Evidencias
            </NavLink>

            <NavLink to="/admin/reportes" onClick={closeMobile} className={({ isActive }) => isActive ? "sga-menu-item active" : "sga-menu-item"}>
              <FileText size={18} />
              Reportes PRO
            </NavLink>

            <NavLink to="/admin/auditoria" onClick={closeMobile} className={({ isActive }) => isActive ? "sga-menu-item active" : "sga-menu-item"}>
              <ShieldCheck size={18} />
              Auditoría PRO
            </NavLink>

            <NavLink to="/admin/configuracion" onClick={closeMobile} className={({ isActive }) => isActive ? "sga-menu-item active" : "sga-menu-item"}>
              <Settings size={18} />
              Configuración
            </NavLink>
          </>
        )}

        {esTecnico && (
          <>
            <NavLink to="/tecnico/mantenimientos" onClick={closeMobile} className={({ isActive }) => isActive ? "sga-menu-item active" : "sga-menu-item"}>
              <Wrench size={18} />
              Mis mantenimientos
            </NavLink>

            <NavLink to="/tecnico/evidencias" onClick={closeMobile} className={({ isActive }) => isActive ? "sga-menu-item active" : "sga-menu-item"}>
              <Image size={18} />
              Evidencias
            </NavLink>
          </>
        )}
      </nav>

      <div className="sga-user-card">
        <div className="sga-user-avatar">
          {userSeguro?.nombre_completo?.substring(0, 2).toUpperCase() || "US"}
        </div>

        <div>
          <strong>{userSeguro?.nombre_completo || "Usuario"}</strong>
          <span>{rol || "SIN ROL"}</span>
        </div>
      </div>

      <button className="sga-logout" onClick={handleLogout}>
        <LogOut size={18} />
        Cerrar sesión
      </button>
    </aside>
  );
}