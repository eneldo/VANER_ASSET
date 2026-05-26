// =========================================================
// SIDEBAR RESPONSIVE PRO SGA - AGRUPADO
// Archivo: frontend/src/components/Sidebar.jsx
// Fase UX - Configuración Sistema
// =========================================================

import { useState } from "react";
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
  ChevronDown,
  SlidersHorizontal,
  Archive,
  Mail,
  Cog,
} from "lucide-react";

import "../styles/sidebar.css";

export default function Sidebar({ user, onLogout, isOpen = false, onClose }) {
  const navigate = useNavigate();
  const [openConfigSistema, setOpenConfigSistema] = useState(true);

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
      navigate("/");
    }
  };

  const iniciales =
    userSeguro?.nombre_completo?.substring(0, 2).toUpperCase() ||
    userSeguro?.username?.substring(0, 2).toUpperCase() ||
    "US";

  const itemClass = ({ isActive }) =>
    isActive ? "sga-menu-item active" : "sga-menu-item";

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
          className={itemClass}
        >
          <LayoutDashboard size={17} />
          <span>Dashboard</span>
        </NavLink>

        {esAdmin && (
          <>
            <NavLink to="/admin/empresas" onClick={closeMobile} className={itemClass}>
              <Building2 size={17} />
              <span>Empresas / Cliente</span>
            </NavLink>

            <NavLink to="/admin/sedes" onClick={closeMobile} className={itemClass}>
              <MapPin size={17} />
              <span>Sedes</span>
            </NavLink>

            <NavLink to="/admin/categorias" onClick={closeMobile} className={itemClass}>
              <Tags size={17} />
              <span>Categorías</span>
            </NavLink>

            <NavLink to="/admin/tecnicos" onClick={closeMobile} className={itemClass}>
              <UserCog size={17} />
              <span>Técnicos</span>
            </NavLink>

            <NavLink to="/admin/usuarios" onClick={closeMobile} className={itemClass}>
              <Users size={17} />
              <span>Usuarios y Permisos</span>
            </NavLink>

            <NavLink to="/admin/equipos" onClick={closeMobile} className={itemClass}>
              <MonitorCog size={17} />
              <span>Equipos</span>
            </NavLink>

            <NavLink to="/admin/mantenimientos" onClick={closeMobile} className={itemClass}>
              <Wrench size={17} />
              <span>Mantenimientos</span>
            </NavLink>

            <NavLink to="/admin/evidencias" onClick={closeMobile} className={itemClass}>
              <Image size={17} />
              <span>Evidencias</span>
            </NavLink>

            <NavLink to="/admin/reportes" onClick={closeMobile} className={itemClass}>
              <FileText size={17} />
              <span>Reportes PRO</span>
            </NavLink>

            <NavLink to="/admin/auditoria" onClick={closeMobile} className={itemClass}>
              <ShieldCheck size={17} />
              <span>Auditoría PRO</span>
            </NavLink>

            <div className="sga-menu-group">
              <button
                type="button"
                className={`sga-menu-item sga-menu-group-btn ${openConfigSistema ? "open" : ""}`}
                onClick={() => setOpenConfigSistema((v) => !v)}
              >
                <Cog size={17} />
                <span>Configuración Sistema</span>
                <ChevronDown size={15} className="sga-chevron" />
              </button>

              {openConfigSistema && (
                <div className="sga-submenu">
                  <NavLink to="/admin/configuracion-sistema" onClick={closeMobile} className={itemClass}>
                    <Settings size={15} />
                    <span>Centro Sistema</span>
                  </NavLink>

                  <NavLink to="/admin/configuracion" onClick={closeMobile} className={itemClass}>
                    <Settings size={15} />
                    <span>Configuración General</span>
                  </NavLink>

                  <NavLink to="/admin/configuracion-inteligente" onClick={closeMobile} className={itemClass}>
                    <SlidersHorizontal size={15} />
                    <span>Configuración Inteligente</span>
                  </NavLink>

                  <NavLink to="/admin/backups" onClick={closeMobile} className={itemClass}>
                    <Archive size={15} />
                    <span>Backups</span>
                  </NavLink>

                  <NavLink to="/admin/smtp-inteligente" onClick={closeMobile} className={itemClass}>
                    <Mail size={15} />
                    <span>SMTP Inteligente</span>
                  </NavLink>
                </div>
              )}
            </div>
          </>
        )}

        {esTecnico && (
          <>
            <NavLink to="/tecnico/mantenimientos" onClick={closeMobile} className={itemClass}>
              <Wrench size={17} />
              <span>Mis mantenimientos</span>
            </NavLink>

            <NavLink to="/tecnico/evidencias" onClick={closeMobile} className={itemClass}>
              <Image size={17} />
              <span>Evidencias</span>
            </NavLink>
          </>
        )}
      </nav>

      <div className="sga-sidebar-footer">
        <div className="sga-user-card">
          <div className="sga-user-avatar">{iniciales}</div>
          <div className="sga-user-info">
            <strong>{userSeguro?.nombre_completo || userSeguro?.username || "Usuario"}</strong>
            <span>{rol || "SIN ROL"}</span>
          </div>
        </div>

        <button className="sga-logout" onClick={handleLogout}>
          <LogOut size={17} />
          <span>Cerrar sesión</span>
        </button>
      </div>
    </aside>
  );
}
