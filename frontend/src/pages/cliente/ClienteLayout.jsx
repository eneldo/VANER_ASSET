// ============================================================
// CLIENTE LAYOUT - SGAHolding
// Archivo: frontend/src/pages/cliente/ClienteLayout.jsx
// Portal Cliente estable y funcional
// ============================================================

import { NavLink, Outlet, useNavigate } from "react-router-dom";
import api from "../../api/axios";
import { clearSession } from "../../utils/authStorage";

import {
  LayoutDashboard,
  MapPin,
  MonitorCog,
  Wrench,
  CalendarDays,
  AlertTriangle,
  FileCheck2,
  LogOut,
} from "lucide-react";

import "./cliente.css";

export default function ClienteLayout() {
  const navigate = useNavigate();

  // ============================================================
  // LOGOUT
  // ============================================================

  const logout = async () => {
    try {
      await api.post("/auth/logout", {});
    } finally {
      clearSession();
      localStorage.removeItem("token");
      localStorage.removeItem("empresa_id");
      navigate("/");
    }
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
            <h2>SGAHolding</h2>
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

          <NavLink to="/cliente/solicitudes" className="cliente-link cliente-link-emergency">
            <AlertTriangle size={18} />
            Emergencias
          </NavLink>

          <NavLink to="/cliente/reportes" className="cliente-link">
            <FileCheck2 size={18} />
            Reportes aprobados
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
