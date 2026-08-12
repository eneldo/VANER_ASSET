// =========================================================
// SIDEBAR RESPONSIVE ENTERPRISE PRO SGA
// Archivo: frontend/src/components/Sidebar.jsx
// =========================================================

import { NavLink, useNavigate } from "react-router-dom";
import api from "../api/axios";
import { clearSession } from "../utils/authStorage";

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
  Menu,
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
  collapsed = false,
  onToggleCollapsed,
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

  const handleLogout = async () => {
    if (typeof onLogout === "function") {
      await onLogout();
    } else {
      try {
        await api.post("/auth/logout", {});
      } catch {
        // La sesión local siempre se elimina aunque el backend no responda.
      }
      clearSession();
      localStorage.removeItem("token");

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
    <aside
      id="sga-admin-sidebar"
      className={`sga-sidebar ${isOpen ? "open" : ""} ${collapsed ? "collapsed" : ""}`}
    >

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
          <h2>SGAHolding</h2>
          <p>Gestión Empresarial</p>
        </div>

      </div>

      {/* ================================================= */}
      {/* MENÚ */}
      {/* ================================================= */}

      {typeof onToggleCollapsed === "function" && (
        <button
          type="button"
          className="sga-sidebar-toggle"
          onClick={onToggleCollapsed}
          aria-label={collapsed ? "Expandir menu lateral" : "Contraer menu lateral"}
          aria-expanded={!collapsed}
          aria-controls="sga-admin-sidebar"
          title={collapsed ? "Expandir menu" : "Contraer menu"}
        >
          <Menu size={20} />
        </button>
      )}

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
          aria-label="Dashboard"
          title={collapsed ? "Dashboard" : undefined}
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
              aria-label="Empresas"
              title={collapsed ? "Empresas" : undefined}
            >
              <Building2 size={17} />
              <span>Empresas</span>
            </NavLink>

            <NavLink
              to="/admin/sedes"
              onClick={closeMobile}
              className={itemClass}
              aria-label="Sedes"
              title={collapsed ? "Sedes" : undefined}
            >
              <MapPin size={17} />
              <span>Sedes</span>
            </NavLink>

            <NavLink
              to="/admin/categorias"
              onClick={closeMobile}
              className={itemClass}
              aria-label="Categorías"
              title={collapsed ? "Categorías" : undefined}
            >
              <Tags size={17} />
              <span>Categorías</span>
            </NavLink>

            <NavLink
              to="/admin/tecnicos"
              onClick={closeMobile}
              className={itemClass}
              aria-label="Técnicos"
              title={collapsed ? "Técnicos" : undefined}
            >
              <UserCog size={17} />
              <span>Técnicos</span>
            </NavLink>

            <NavLink
              to="/admin/usuarios"
              onClick={closeMobile}
              className={itemClass}
              aria-label="Usuarios"
              title={collapsed ? "Usuarios" : undefined}
            >
              <Users size={17} />
              <span>Usuarios</span>
            </NavLink>

            <NavLink
              to="/admin/equipos"
              onClick={closeMobile}
              className={itemClass}
              aria-label="Equipos"
              title={collapsed ? "Equipos" : undefined}
            >
              <MonitorCog size={17} />
              <span>Equipos</span>
            </NavLink>

            <NavLink
              to="/admin/mantenimientos"
              onClick={closeMobile}
              className={itemClass}
              aria-label="Mantenimientos"
              title={collapsed ? "Mantenimientos" : undefined}
            >
              <Wrench size={17} />
              <span>Mantenimientos</span>
            </NavLink>

            <NavLink
              to="/admin/evidencias"
              onClick={closeMobile}
              className={itemClass}
              aria-label="Evidencias"
              title={collapsed ? "Evidencias" : undefined}
            >
              <Image size={17} />
              <span>Evidencias</span>
            </NavLink>

            <NavLink
              to="/admin/reportes"
              onClick={closeMobile}
              className={itemClass}
              aria-label="Reportes PRO"
              title={collapsed ? "Reportes PRO" : undefined}
            >
              <FileText size={17} />
              <span>Reportes PRO</span>
            </NavLink>

            <NavLink
              to="/admin/facturacion"
              onClick={closeMobile}
              className={itemClass}
              aria-label="Facturación"
              title={collapsed ? "Facturación" : undefined}
            >
              <Receipt size={17} />
              <span>Facturación</span>
            </NavLink>

            <NavLink
              to="/admin/plantillas-reportes"
              onClick={closeMobile}
              className={itemClass}
              aria-label="Plantillas PDF"
              title={collapsed ? "Plantillas PDF" : undefined}
            >
              <FileCog size={17} />
              <span>Plantillas PDF</span>
            </NavLink>

            <NavLink
              to="/admin/auditoria"
              onClick={closeMobile}
              className={itemClass}
              aria-label="Auditoría PRO"
              title={collapsed ? "Auditoría PRO" : undefined}
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
              aria-label="Configuración Sistema"
              title={collapsed ? "Configuración Sistema" : undefined}
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
              aria-label="Mis mantenimientos"
              title={collapsed ? "Mis mantenimientos" : undefined}
            >
              <Wrench size={17} />
              <span>Mis mantenimientos</span>
            </NavLink>

            <NavLink
              to="/tecnico/evidencias"
              onClick={closeMobile}
              className={itemClass}
              aria-label="Evidencias"
              title={collapsed ? "Evidencias" : undefined}
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
          aria-label="Cerrar sesión"
          title={collapsed ? "Cerrar sesión" : undefined}
        >
          <LogOut size={17} />
          <span>Cerrar sesión</span>
        </button>

      </div>

    </aside>
  );
}
