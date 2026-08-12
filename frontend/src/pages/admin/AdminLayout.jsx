// =========================================================
// ADMIN LAYOUT RESPONSIVE PRO SGA
// Archivo: frontend/src/pages/admin/AdminLayout.jsx
// Fase 32.2
// =========================================================

import { useState } from "react";
import { Menu } from "lucide-react";
import Sidebar from "../../components/Sidebar";
import { useAuth } from "../../hooks/useAuth";
import "../../styles/sidebar.css";
import "../../styles/admin.css";

const SIDEBAR_COLLAPSED_KEY = "sga-admin-sidebar-collapsed";

function getInitialSidebarCollapsed() {
  if (typeof window === "undefined") return false;

  try {
    return window.localStorage.getItem(SIDEBAR_COLLAPSED_KEY) === "true";
  } catch {
    return false;
  }
}

export default function AdminLayout({
  children,
  className = "",
  contentClassName = "",
}) {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(getInitialSidebarCollapsed);
  const { user, logout } = useAuth();

  const toggleSidebarCollapsed = () => {
    setSidebarCollapsed((collapsed) => {
      const nextCollapsed = !collapsed;

      try {
        window.localStorage.setItem(SIDEBAR_COLLAPSED_KEY, String(nextCollapsed));
      } catch {
        // El menu sigue funcionando aunque el navegador bloquee localStorage.
      }

      return nextCollapsed;
    });
  };

  const layoutClassName = [
    "admin-layout-pro",
    sidebarCollapsed ? "sidebar-collapsed" : "",
    className,
  ]
    .filter(Boolean)
    .join(" ");

  return (
    <div className={layoutClassName}>
      <button className="admin-mobile-menu-btn" onClick={() => setSidebarOpen(true)} aria-label="Abrir menú">
        <Menu size={22} />
      </button>

      <Sidebar
        user={user}
        onLogout={logout}
        isOpen={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
        collapsed={sidebarCollapsed}
        onToggleCollapsed={toggleSidebarCollapsed}
      />

      {sidebarOpen && <div className="admin-sidebar-overlay" onClick={() => setSidebarOpen(false)} />}

      <main className={["admin-content-pro", contentClassName].filter(Boolean).join(" ")}>
        {children}
      </main>
    </div>
  );
}
