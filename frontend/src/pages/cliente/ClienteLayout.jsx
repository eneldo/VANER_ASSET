// ============================================================
// CLIENTE LAYOUT - SGA PRO
// Archivo: frontend/src/pages/cliente/ClienteLayout.jsx
// Portal Cliente estable y funcional
// ============================================================

import React from "react";
import { NavLink, Outlet, useNavigate } from "react-router-dom";

import {
  LayoutDashboard,
  MapPin,
  MonitorCog,
  Wrench,
  CalendarDays,
  LogOut,
} from "lucide-react";

import "./cliente.css";

// ============================================================
// OBTENER EMPRESA ID
// ============================================================

export function getEmpresaId() {
  try {
    const user = JSON.parse(localStorage.getItem("user") || "{}");

    return (
      localStorage.getItem("empresa_id") ||
      user?.empresa_id ||
      user?.empresa?.id ||
      ""
    );
  } catch {
    return localStorage.getItem("empresa_id") || "";
  }
}

export default function ClienteLayout() {
  const navigate = useNavigate();

  // ============================================================
  // LOGOUT
  // ============================================================

  const logout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    localStorage.removeItem("user");
    localStorage.removeItem("empresa_id");

    navigate("/");
  };

  // ============================================================
  // USUARIO
  // ============================================================

  const user = JSON.parse(localStorage.getItem("user") || "{}");

  const empresaNombre =
    user?.empresa_nombre ||
    user?.empresa?.nombre ||
    "Empresa Cliente";

  // ============================================================
  // RENDER
  // ============================================================

  return (
    <div className="cliente-shell">
      {/* ===================================================== */}
      {/* SIDEBAR */}
      {/* ===================================================== */}

      <aside className="cliente-sidebar">
        {/* ================================================= */}
        {/* LOGO */}
        {/* ================================================= */}

        <div className="cliente-brand">
          <div className="cliente-logo">SGA</div>

          <div>
            <h2>SGA PRO</h2>
            <p>Portal Empresa</p>
          </div>
        </div>

        {/* ================================================= */}
        {/* EMPRESA */}
        {/* ================================================= */}

        <div className="cliente-company">
          <span>Empresa activa</span>

          <strong>{empresaNombre}</strong>

          <small>EMPRESA</small>
        </div>

        {/* ================================================= */}
        {/* MENU */}
        {/* ================================================= */}

        <nav className="cliente-nav">
          <NavLink to="/cliente/dashboard" className="cliente-link">
            <LayoutDashboard size={18} />
            Dashboard
          </NavLink>

          <NavLink to="/cliente/sedes" className="cliente-link">
            <MapPin size={18} />
            Sedes
          </NavLink>

          <NavLink to="/cliente/equipos" className="cliente-link">
            <MonitorCog size={18} />
            Hoja de vida equipos
          </NavLink>

          <NavLink to="/cliente/mantenimientos" className="cliente-link">
            <Wrench size={18} />
            Mantenimientos
          </NavLink>

          <NavLink to="/cliente/cronograma" className="cliente-link">
            <CalendarDays size={18} />
            Cronograma
          </NavLink>
        </nav>

        {/* ================================================= */}
        {/* LOGOUT */}
        {/* ================================================= */}

        <button className="cliente-logout" onClick={logout}>
          <LogOut size={18} />
          Cerrar sesión
        </button>
      </aside>

      {/* ===================================================== */}
      {/* CONTENIDO */}
      {/* ===================================================== */}

      <main className="cliente-main">
        <Outlet />
      </main>
    </div>
  );
}