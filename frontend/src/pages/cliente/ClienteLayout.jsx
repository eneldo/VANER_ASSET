// ============================================================
// LAYOUT PORTAL CLIENTE - SGA PRO
// Sidebar propio para usuarios cliente.
// ============================================================

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

export default function ClienteLayout() {
  const navigate = useNavigate();
  const user = getUser();

  const salir = () => {
    localStorage.clear();
    navigate("/");
  };

  return (
    <div className="cliente-shell">
      <aside className="cliente-sidebar">
        <div className="cliente-brand">
          <div className="cliente-logo">SGA</div>
          <div>
            <h2>SGA PRO</h2>
            <p>Portal Empresa</p>
          </div>
        </div>

        <div className="cliente-company">
          <span>Empresa activa</span>
          <strong>{user?.empresa_nombre || user?.nombre_completo || "Cliente"}</strong>
          <small>{user?.rol || "CLIENTE"}</small>
        </div>

        <nav className="cliente-nav">
          <NavLink className="cliente-link" to="/cliente/dashboard">
            <LayoutDashboard size={18} />
            Dashboard
          </NavLink>

          <NavLink className="cliente-link" to="/cliente/sedes">
            <MapPin size={18} />
            Sedes
          </NavLink>

          <NavLink className="cliente-link" to="/cliente/equipos">
            <MonitorCog size={18} />
            Hoja de vida de equipos
          </NavLink>

          <NavLink className="cliente-link" to="/cliente/mantenimientos">
            <Wrench size={18} />
            Mantenimientos
          </NavLink>

          <NavLink className="cliente-link" to="/cliente/cronograma">
            <CalendarDays size={18} />
            Cronograma
          </NavLink>
        </nav>

        <button className="cliente-logout" onClick={salir}>
          <LogOut size={16} />
          Salir
        </button>
      </aside>

      <main className="cliente-main">
        <Outlet />
      </main>
    </div>
  );
}

export function getUser() {
  try {
    return JSON.parse(localStorage.getItem("user") || "{}");
  } catch {
    return {};
  }
}

export function getEmpresaId() {
  const user = getUser();
  return user?.empresa_id || localStorage.getItem("empresa_id");
}