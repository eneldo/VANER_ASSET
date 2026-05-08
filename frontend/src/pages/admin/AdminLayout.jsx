// =========================================================
// ADMIN LAYOUT PRO SGA
// Layout global para TODOS los módulos administrativos.
//
// FUNCIONES:
// - Renderiza la barra lateral.
// - Mantiene scroll interno.
// - Responsive.
// - Mantiene el contenido dentro del layout.
//
// IMPORTANTE:
// NO redirecciona roles.
// SOLO pinta el layout.
// =========================================================

import Sidebar from "../../components/Sidebar";
import "../../styles/sidebar.css";

export default function AdminLayout({ children }) {
  return (
    <div className="admin-layout-pro">
      {/* =====================================================
          SIDEBAR IZQUIERDA
      ===================================================== */}
      <Sidebar />

      {/* =====================================================
          CONTENIDO PRINCIPAL
      ===================================================== */}
      <main className="admin-content-pro">
        {children}
      </main>
    </div>
  );
}