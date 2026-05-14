/*
===========================================================
LAYOUT COORDINADOR PRO — MENÚ DINÁMICO POR PERMISOS
Archivo: frontend/src/layouts/CoordinadorLayout.jsx
===========================================================
*/

import React, { useEffect, useMemo, useState } from "react";
import { NavLink, Outlet, useNavigate } from "react-router-dom";
import {
  LayoutDashboard,
  ClipboardList,
  CalendarDays,
  FileBarChart,
  LogOut,
  Menu,
  ShieldCheck,
  PackageSearch,
  Image,
  FileText,
} from "lucide-react";

import API from "../api/axios";
import "../styles/coordinador.css";

export default function CoordinadorLayout() {
  const [open, setOpen] = useState(true);
  const [permisos, setPermisos] = useState([]);
  const [cargandoPermisos, setCargandoPermisos] = useState(true);
  const navigate = useNavigate();

  const user = useMemo(() => {
    try {
      return JSON.parse(localStorage.getItem("user"));
    } catch {
      return null;
    }
  }, []);

  useEffect(() => {
    cargarPermisos();
  }, []);

  const cargarPermisos = async () => {
    try {
      setCargandoPermisos(true);
      const res = await API.get("/permisos/me");
      setPermisos(res.data?.permisos_finales || []);
    } catch (error) {
      console.error("Error cargando permisos del coordinador:", error);
      setPermisos([]);
    } finally {
      setCargandoPermisos(false);
    }
  };

  const tienePermiso = (...codigos) => {
    if (user?.rol === "ADMIN") return true;
    return codigos.some((codigo) => permisos.includes(codigo));
  };

  const menuItems = [
    {
      label: "Dashboard",
      to: "/coordinador/dashboard",
      icon: LayoutDashboard,
      permisos: ["DASHBOARD_VER", "COORDINADOR_DASHBOARD"],
    },
    {
      label: "Mantenimientos",
      to: "/coordinador/mantenimientos",
      icon: ClipboardList,
      permisos: ["MANTENIMIENTOS_VER", "COORDINADOR_MANTENIMIENTOS"],
    },
    {
      label: "Cronograma",
      to: "/coordinador/cronograma",
      icon: CalendarDays,
      permisos: ["CRONOGRAMA_VER", "COORDINADOR_CRONOGRAMA"],
    },
    {
      label: "Inventario / Equipos",
      to: "/coordinador/equipos",
      icon: PackageSearch,
      permisos: ["EQUIPOS_VER", "EQUIPOS_CREAR", "EQUIPOS_EDITAR", "INVENTARIO_VER"],
    },
    {
      label: "Evidencias",
      to: "/coordinador/evidencias",
      icon: Image,
      permisos: ["EVIDENCIAS_VER"],
    },
    {
      label: "Hoja de vida",
      to: "/coordinador/hoja-vida",
      icon: FileText,
      permisos: ["HOJA_VIDA_VER", "HOJA_VIDA_EDITAR"],
    },
    {
      label: "Informes",
      to: "/coordinador/informes",
      icon: FileBarChart,
      permisos: ["INFORMES_VER", "REPORTES_VER", "COORDINADOR_INFORMES"],
    },
  ];

  const menuVisible = menuItems.filter((item) => tienePermiso(...item.permisos));

  const logout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    localStorage.removeItem("user");
    navigate("/");
  };

  return (
    <div className="coord-shell">
      <aside className={open ? "coord-sidebar" : "coord-sidebar collapsed"}>
        <div className="coord-brand">
          <ShieldCheck size={28} />
          {open && (
            <div>
              <h2>SGA PRO</h2>
              <span>Coordinador</span>
            </div>
          )}
        </div>

        <nav className="coord-menu">
          {cargandoPermisos ? (
            <span className="coord-menu-loading">Cargando permisos...</span>
          ) : menuVisible.length === 0 ? (
            <span className="coord-menu-empty">Sin permisos asignados</span>
          ) : (
            menuVisible.map((item) => {
              const Icon = item.icon;
              return (
                <NavLink key={item.to} to={item.to}>
                  <Icon size={20} />
                  {open && <span>{item.label}</span>}
                </NavLink>
              );
            })
          )}
        </nav>

        <button className="coord-logout" onClick={logout}>
          <LogOut size={20} />
          {open && <span>Cerrar sesión</span>}
        </button>
      </aside>

      <main className="coord-main">
        <header className="coord-topbar">
          <button className="coord-menu-toggle" onClick={() => setOpen(!open)}>
            <Menu size={22} />
          </button>
          <div>
            <h1>Módulo Coordinador PRO</h1>
            <p>Permisos dinámicos, empresa asignada e inventario operativo.</p>
          </div>
        </header>

        <section className="coord-content">
          <Outlet />
        </section>
      </main>
    </div>
  );
}
