// =========================================================
// ADMIN LAYOUT
// Contenedor general para páginas del administrador
// Incluye sidebar + contenido dinámico
// =========================================================

import { useContext } from "react";
import { AuthContext } from "../../context/AuthContext";
import Sidebar from "../../components/Sidebar";

export default function AdminLayout({ children }) {
  const { user, logout } = useContext(AuthContext);

  return (
    <div style={{ display: "flex", minHeight: "100vh", background: "#f5f8ff" }}>
      {/* Sidebar institucional */}
      <Sidebar user={user} onLogout={logout} />

      {/* Contenido principal */}
      <main style={{ flex: 1, padding: "32px" }}>
        {children}
      </main>
    </div>
  );
}