// =========================================================
// SIDEBAR PRO SGA
// Menú lateral institucional con navegación por rol.
//
// Mejora:
// - Si user viene vacío desde props, intenta leer localStorage.user.
// - ADMIN y COORDINADOR ven menú administrativo.
// - TECNICO conserva acceso técnico.
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
  Bell,
} from "lucide-react";

import "../styles/sidebar.css";

export default function Sidebar({ user, onLogout }) {
  const navigate = useNavigate();

  // =======================================================
  // USUARIO SEGURO
  // Si por alguna razón AuthContext no entrega user,
  // usamos localStorage para evitar que el menú desaparezca.
  // =======================================================
  let userSeguro = user;

  if (!userSeguro) {
    try {
      userSeguro = JSON.parse(localStorage.getItem("user"));
    } catch {
      userSeguro = null;
    }
  }

  const rol = userSeguro?.rol;
  const esAdmin = rol === "ADMIN" || rol === "COORDINADOR";
  const esTecnico = rol === "TECNICO";

  // =======================================================
  // CERRAR SESIÓN
  // =======================================================
  const handleLogout = () => {
    if (typeof onLogout === "function") {
      onLogout();
    } else {
      localStorage.removeItem("token");
      localStorage.removeItem("user");
    }

    navigate("/");
  };

  return (
    <aside className="sga-sidebar">
      {/* ===================================================
          MARCA
      =================================================== */}
      <div className="sga-brand">
        <div className="sga-logo">SGA</div>

        <div>
          <h2>SGA PRO</h2>
          <p>Gestión de Activos</p>
        </div>
      </div>

      <p className="sga-menu-title">MÓDULO PRINCIPAL</p>

      <nav className="sga-menu">
        {/* Dashboard según rol */}
        <NavLink
          to={esTecnico ? "/tecnico" : "/admin"}
          className={({ isActive }) =>
            isActive ? "sga-menu-item active" : "sga-menu-item"
          }
        >
          <LayoutDashboard size={18} />
          Dashboard
        </NavLink>

        {/* Menú ADMIN / COORDINADOR */}
        {esAdmin && (
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


            {/* FASE 29 - CENTRO DE NOTIFICACIONES */}
            <NavLink
              to="/admin/notificaciones"
              className={({ isActive }) =>
                isActive ? "sga-menu-item active" : "sga-menu-item"
              }
            >
              <Bell size={18} />
              Notificaciones
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

        {/* Opciones operativas */}
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

        {esAdmin && (
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

      {/* Usuario */}
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