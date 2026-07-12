// =========================================================
// SIDEBAR RESPONSIVE ENTERPRISE PRO SGA
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
  LogOut,
  Tags,
  UserCog,
  ShieldCheck,
  X,
  Settings,
  Receipt,
  FileCog,
} from "lucide-react";

import "../styles/sidebar.css";

export default function Sidebar({
  user,
  onLogout,
  isOpen = false,
  onClose,
}) {
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
    if (typeof onClose === "function") {
      onClose();
    }
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

      {/* ================================================= */}
      {/* BOTÓN CERRAR MOBILE */}
      {/* ================================================= */}

      <button
        className="sga-sidebar-close"
        onClick={closeMobile}
        aria-label="Cerrar menú"
      >
        <X size={20} />
      </button>

      {/* ================================================= */}
      {/* LOGO */}
      {/* ================================================= */}

      <div className="sga-brand">

        <div className="sga-logo">
          SGA
        </div>

        <div>
          <h2>SGA PRO</h2>
          <p>Gestión Empresarial</p>
        </div>

      </div>

      {/* ================================================= */}
      {/* MENÚ */}
      {/* ================================================= */}

      <p className="sga-menu-title">
        MÓDULO PRINCIPAL
      </p>

      <nav className="sga-menu">

        {/* DASHBOARD */}

        <NavLink
          to={
            esTecnico
              ? "/tecnico/dashboard"
              : esCoordinador
              ? "/coordinador/dashboard"
              : "/admin/dashboard"
          }
          onClick={closeMobile}
          className={itemClass}
        >
          <LayoutDashboard size={17} />
          <span>Dashboard</span>
        </NavLink>

        {/* ================================================= */}
        {/* ADMIN */}
        {/* ================================================= */}

        {esAdmin && (
          <>

            <NavLink
              to="/admin/empresas"
              onClick={closeMobile}
              className={itemClass}
            >
              <Building2 size={17} />
              <span>Empresas</span>
            </NavLink>

            <NavLink
              to="/admin/sedes"
              onClick={closeMobile}
              className={itemClass}
            >
              <MapPin size={17} />
              <span>Sedes</span>
            </NavLink>

            <NavLink
              to="/admin/categorias"
              onClick={closeMobile}
              className={itemClass}
            >
              <Tags size={17} />
              <span>Categorías</span>
            </NavLink>

            <NavLink
              to="/admin/tecnicos"
              onClick={closeMobile}
              className={itemClass}
            >
              <UserCog size={17} />
              <span>Técnicos</span>
            </NavLink>

            <NavLink
              to="/admin/usuarios"
              onClick={closeMobile}
              className={itemClass}
            >
              <Users size={17} />
              <span>Usuarios</span>
            </NavLink>

            <NavLink
              to="/admin/equipos"
              onClick={closeMobile}
              className={itemClass}
            >
              <MonitorCog size={17} />
              <span>Equipos</span>
            </NavLink>

            <NavLink
              to="/admin/mantenimientos"
              onClick={closeMobile}
              className={itemClass}
            >
              <Wrench size={17} />
              <span>Mantenimientos</span>
            </NavLink>

            <NavLink
              to="/admin/evidencias"
              onClick={closeMobile}
              className={itemClass}
            >
              <Image size={17} />
              <span>Evidencias</span>
            </NavLink>

            <NavLink
              to="/admin/reportes"
              onClick={closeMobile}
              className={itemClass}
            >
              <FileText size={17} />
              <span>Reportes PRO</span>
            </NavLink>

            <NavLink to="/admin/facturacion" onClick={closeMobile} className={itemClass}>
              <Receipt size={17} />
              <span>Facturación</span>
            </NavLink>

            <NavLink to="/admin/plantillas-reportes" onClick={closeMobile} className={itemClass}>
              <FileCog size={17} />
              <span>Plantillas PDF</span>
            </NavLink>

            <NavLink
              to="/admin/auditoria"
              onClick={closeMobile}
              className={itemClass}
            >
              <ShieldCheck size={17} />
              <span>Auditoría PRO</span>
            </NavLink>

            {/* ============================================= */}
            {/* CONFIGURACIÓN CENTRAL */}
            {/* ============================================= */}

            <NavLink
              to="/admin/configuracion-sistema"
              onClick={closeMobile}
              className={itemClass}
            >
              <Settings size={17} />
              <span>Configuración Sistema</span>
            </NavLink>

          </>
        )}

        {/* ================================================= */}
        {/* TÉCNICO */}
        {/* ================================================= */}

        {esTecnico && (
          <>

            <NavLink
              to="/tecnico/mantenimientos"
              onClick={closeMobile}
              className={itemClass}
            >
              <Wrench size={17} />
              <span>Mis mantenimientos</span>
            </NavLink>

            <NavLink
              to="/tecnico/evidencias"
              onClick={closeMobile}
              className={itemClass}
            >
              <Image size={17} />
              <span>Evidencias</span>
            </NavLink>

          </>
        )}

      </nav>

      {/* ================================================= */}
      {/* FOOTER */}
      {/* ================================================= */}

      <div className="sga-sidebar-footer">

        <div className="sga-user-card">

          <div className="sga-user-avatar">
            {iniciales}
          </div>

          <div className="sga-user-info">

            <strong>
              {userSeguro?.nombre_completo ||
                userSeguro?.username ||
                "Usuario"}
            </strong>

            <span>{rol || "SIN ROL"}</span>

          </div>

        </div>

        <button
          className="sga-logout"
          onClick={handleLogout}
        >
          <LogOut size={17} />
          <span>Cerrar sesión</span>
        </button>

      </div>

    </aside>
  );
}
