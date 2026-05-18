// =========================================================
// ADMIN LAYOUT RESPONSIVE PRO SGA
// Archivo: frontend/src/pages/admin/AdminLayout.jsx
// =========================================================

import { useState } from "react";
import { Menu } from "lucide-react";
import Sidebar from "../../components/Sidebar";
import "../../styles/sidebar.css";
import "../../styles/admin.css";

export default function AdminLayout({ children }) {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <div className="admin-layout-pro">
      <button
        className="admin-mobile-menu-btn"
        onClick={() => setSidebarOpen(true)}
        aria-label="Abrir menú"
      >
        <Menu size={22} />
      </button>

      <Sidebar
        isOpen={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
      />

      {sidebarOpen && (
        <div
          className="admin-sidebar-overlay"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      <main className="admin-content-pro">
        {children}
      </main>
    </div>
  );
}