// =========================================================
// SIDEBAR PRO SGA
// Archivo: frontend/src/components/Sidebar.jsx
// Menú lateral institucional SOLO para ADMIN / TECNICO.
// COORDINADOR NO debe heredar módulos ADMIN.
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
} from "lucide-react";

import "../styles/sidebar.css";

export default function Sidebar({ user, onLogout }) {
  const navigate = useNavigate();

  let userSeguro = user;

  if (!userSeguro) {
    try {
      userSeguro = JSON.parse(localStorage.getItem("user"));
    } catch {
      userSeguro = null;
    }
  }

  const rol = userSeguro?.rol;

  const esAdmin = rol === "ADMIN";
  const esTecnico = rol === "TECNICO";
  const esCoordinador = rol === "COORDINADOR";

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

  // Seguridad visual:
  // Si un coordinador cae aquí por error, lo enviamos a su layout real.
  if (esCoordinador) {
    navigate("/coordinador/dashboard");
    return null;
  }

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
        <NavLink
          to={esTecnico ? "/tecnico" : "/admin"}
          className={({ isActive }) =>
            isActive ? "sga-menu-item active" : "sga-menu-item"
          }
        >
          <LayoutDashboard size={18} />
          Dashboard
        </NavLink>

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

            <NavLink
              to="/admin/usuarios"
              className={({ isActive }) =>
                isActive ? "sga-menu-item active" : "sga-menu-item"
              }
            >
              <Users size={18} />
              Usuarios y Permisos
            </NavLink>

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

            {/* =====================================================
                LINK NUEVO / ACTUALIZADO: Reportes PRO
                Ruta conectada con App.jsx:
                /admin/reportes
            ===================================================== */}
            <NavLink
              to="/admin/reportes"
              className={({ isActive }) =>
                isActive ? "sga-menu-item active" : "sga-menu-item"
              }
            >
              <FileText size={18} />
              Reportes PRO
            </NavLink>

            <NavLink
              to="/admin/auditoria"
              className={({ isActive }) =>
                isActive ? "sga-menu-item active" : "sga-menu-item"
              }
            >
              <ShieldCheck size={18} />
              Auditoría PRO
            </NavLink>

            <NavLink
              to="/admin/configuracion"
              className={({ isActive }) =>
                isActive ? "sga-menu-item active" : "sga-menu-item"
              }
            >
              <Settings size={18} />
              Configuración
            </NavLink>
          </>
        )}

        {esTecnico && (
          <>
            <NavLink
              to="/tecnico/mantenimientos"
              className={({ isActive }) =>
                isActive ? "sga-menu-item active" : "sga-menu-item"
              }
            >
              <Wrench size={18} />
              Mis mantenimientos
            </NavLink>

            <NavLink
              to="/tecnico/evidencias"
              className={({ isActive }) =>
                isActive ? "sga-menu-item active" : "sga-menu-item"
              }
            >
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