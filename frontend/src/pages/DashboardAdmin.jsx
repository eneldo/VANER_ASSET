// =========================================================
// DASHBOARD ADMIN SGA PRO
// Pantalla inicial para usuario ADMIN
// =========================================================

import { useContext } from "react";
import { AuthContext } from "../context/AuthContext";
import Sidebar from "../components/Sidebar";
import "../styles/sidebar.css";

export default function DashboardAdmin() {
  const { user, logout } = useContext(AuthContext);

  return (
    <div style={{ display: "flex", minHeight: "100vh", background: "#f5f8ff" }}>
      <Sidebar user={user} onLogout={logout} />

      <main style={{ flex: 1, padding: "32px" }}>
        <h1 style={{ color: "#172554", margin: 0 }}>
          Dashboard Administrador
        </h1>

        <p style={{ color: "#64748b", marginTop: 8 }}>
          Bienvenido, {user?.nombre_completo}
        </p>

        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(4, 1fr)",
            gap: 18,
            marginTop: 30,
          }}
        >
          <div className="metric-card">
            <span>Empresas</span>
            <strong>0</strong>
          </div>

          <div className="metric-card">
            <span>Sedes</span>
            <strong>0</strong>
          </div>

          <div className="metric-card">
            <span>Equipos</span>
            <strong>0</strong>
          </div>

          <div className="metric-card">
            <span>Mantenimientos</span>
            <strong>0</strong>
          </div>
        </div>
      </main>
    </div>
  );
}