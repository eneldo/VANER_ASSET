// =========================================================
// SIDEBAR PRO SGA
// Menú lateral institucional con navegación por rol
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
} from "lucide-react";

import "../styles/sidebar.css";

export default function Sidebar({ user, onLogout }) {
  const navigate = useNavigate();

  // =======================================================
  // CERRAR SESIÓN
  // Limpia sesión y redirige al login
  // =======================================================
  const handleLogout = () => {
    onLogout();
    navigate("/");
  };

  return (
    <aside className="sga-sidebar">
      {/* ===================================================
          LOGO / MARCA DEL SISTEMA
          =================================================== */}
      <div className="sga-brand">
        <div className="sga-logo">SGA</div>
        <div>
          <h2>SGA PRO</h2>
          <p>Gestión de Activos</p>
        </div>
      </div>

      <p className="sga-menu-title">MÓDULO PRINCIPAL</p>

      {/* ===================================================
          MENÚ PRINCIPAL
          =================================================== */}
      <nav className="sga-menu">
        <NavLink
          to={user?.rol === "ADMIN" ? "/admin" : "/tecnico"}
          className={({ isActive }) =>
            isActive ? "sga-menu-item active" : "sga-menu-item"
          }
        >
          <LayoutDashboard size={18} />
          Dashboard
        </NavLink>

        {/* Menú exclusivo para ADMIN */}
        {user?.rol === "ADMIN" && (
          <>
            <NavLink
              to="/admin/empresas"
              className={({ isActive }) =>
                isActive ? "sga-menu-item active" : "sga-menu-item"
              }
            >
              <Building2 size={18} />
              Empresas / Cliente
            </NavLink>

            <NavLink
              to="/admin/sedes"
              className={({ isActive }) =>
                isActive ? "sga-menu-item active" : "sga-menu-item"
              }
            >
              <MapPin size={18} />
              Sedes
            </NavLink>

            <NavLink
              to="/admin/categorias"
              className={({ isActive }) =>
                isActive ? "sga-menu-item active" : "sga-menu-item"
              }
            >
              <Tags size={18} />
              Categorías
            </NavLink>

            <NavLink
              to="/admin/tecnicos"
              className={({ isActive }) =>
                isActive ? "sga-menu-item active" : "sga-menu-item"
              }
            >
              <UserCog size={18} />
              Técnicos
            </NavLink>

            <NavLink
              to="/admin/usuarios"
              className={({ isActive }) =>
                isActive ? "sga-menu-item active" : "sga-menu-item"
              }
            >
              <Users size={18} />
              Usuarios y Permisos
            </NavLink>
          </>
        )}

        <NavLink
          to="/admin/equipos"
          className={({ isActive }) =>
            isActive ? "sga-menu-item active" : "sga-menu-item"
          }
        >
          <MonitorCog size={18} />
          Equipos
        </NavLink>

        <NavLink
          to="/admin/mantenimientos"
          className={({ isActive }) =>
            isActive ? "sga-menu-item active" : "sga-menu-item"
          }
        >
          <Wrench size={18} />
          Mantenimientos
        </NavLink>

        <NavLink
          to="/admin/evidencias"
          className={({ isActive }) =>
            isActive ? "sga-menu-item active" : "sga-menu-item"
          }
        >
          <Image size={18} />
          Evidencias
        </NavLink>

        <NavLink
          to="/admin/reportes"
          className={({ isActive }) =>
            isActive ? "sga-menu-item active" : "sga-menu-item"
          }
        >
          <FileText size={18} />
          Reportes
        </NavLink>

        {user?.rol === "ADMIN" && (
          <NavLink
            to="/admin/configuracion"
            className={({ isActive }) =>
              isActive ? "sga-menu-item active" : "sga-menu-item"
            }
          >
            <Settings size={18} />
            Configuración
          </NavLink>
        )}
      </nav>

      {/* ===================================================
          CARD DEL USUARIO ACTIVO
          =================================================== */}
      <div className="sga-user-card">
        <div className="sga-user-avatar">
          {user?.nombre_completo?.substring(0, 2).toUpperCase() || "US"}
        </div>

        <div>
          <strong>{user?.nombre_completo || "Usuario"}</strong>
          <span>{user?.rol}</span>
        </div>
      </div>

      {/* ===================================================
          BOTÓN CERRAR SESIÓN
          =================================================== */}
      <button className="sga-logout" onClick={handleLogout}>
        <LogOut size={18} />
        Cerrar sesión
      </button>
    </aside>
  );
}