/*
===========================================================
LAYOUT COORDINADOR PRO
Archivo: frontend/src/layouts/CoordinadorLayout.jsx

Mejoras:
- Menú siempre visible para rol COORDINADOR.
- Permisos dinámicos se respetan si existen, pero no dejan el portal vacío.
- Diseño responsive con sidebar colapsable.
===========================================================
*/

import { useEffect, useMemo, useState } from "react";
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
  FileCheck2,
  X,
} from "lucide-react";

import API from "../api/axios";
import { CoordinatorCompanyContext } from "../context/CoordinatorCompanyContext";
import { clearSession } from "../utils/authStorage";
import "../styles/coordinador.css";

export default function CoordinadorLayout() {
  const user = useMemo(() => {
    try {
      return JSON.parse(localStorage.getItem("user"));
    } catch {
      return null;
    }
  }, []);
  const esAdmin = String(user?.rol || "").toUpperCase() === "ADMIN";
  const esCoordinador = String(user?.rol || "").toUpperCase() === "COORDINADOR";

  const [open, setOpen] = useState(true);
  const [mobileOpen, setMobileOpen] = useState(false);
  const [permisos, setPermisos] = useState([]);
  const [cargandoPermisos, setCargandoPermisos] = useState(!esCoordinador);
  const [empresasAutorizadas, setEmpresasAutorizadas] = useState([]);
  const [empresaActivaId, setEmpresaActivaId] = useState(
    localStorage.getItem("coordinator_active_company_id") || user?.empresa_id || "",
  );
  const [cargandoEmpresas, setCargandoEmpresas] = useState(esCoordinador);
  const navigate = useNavigate();

  const cargarPermisos = async () => {
    try {
      setCargandoPermisos(true);
      const res = await API.get("/permisos/me");
      setPermisos(res.data?.permisos_finales || []);
    } catch (error) {
      console.warn("No se pudieron cargar permisos. Se usa menú base del coordinador.", error);
      setPermisos([]);
    } finally {
      setCargandoPermisos(false);
    }
  };

  useEffect(() => {
    if (esCoordinador) return undefined;

    const timer = window.setTimeout(() => cargarPermisos(), 0);
    return () => window.clearTimeout(timer);
  }, [esCoordinador]);

  useEffect(() => {
    if (!esCoordinador) return undefined;

    let activo = true;
    API.get("/coordinador/empresas-autorizadas")
      .then((response) => {
        if (!activo) return;
        const empresas = response.data || [];
        const almacenada = localStorage.getItem("coordinator_active_company_id");
        const seleccion = empresas.some((empresa) => String(empresa.id) === String(almacenada))
          ? almacenada
          : empresas.find((empresa) => empresa.es_principal)?.id || empresas[0]?.id || "";

        setEmpresasAutorizadas(empresas);
        setEmpresaActivaId(seleccion);
        if (seleccion) localStorage.setItem("coordinator_active_company_id", seleccion);
      })
      .catch((error) => {
        console.error("No se pudieron cargar las empresas autorizadas:", error);
        setEmpresasAutorizadas([]);
      })
      .finally(() => {
        if (activo) setCargandoEmpresas(false);
      });

    return () => {
      activo = false;
    };
  }, [esCoordinador]);

  const cambiarEmpresaActiva = (empresaId) => {
    setEmpresaActivaId(empresaId);
    localStorage.setItem("coordinator_active_company_id", empresaId);
  };

  const tienePermiso = (...codigos) => {
    // Regla PRO: ADMIN todo. COORDINADOR tiene menú operativo base aunque aún no se hayan sembrado permisos.
    if (esAdmin || esCoordinador) return true;
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
      permisos: ["EQUIPOS_VER", "INVENTARIO_VER"],
    },
    {
      label: "Hojas de vida",
      to: "/coordinador/hoja-vida",
      icon: FileText,
      permisos: ["HOJA_VIDA_VER", "HOJA_VIDA_EDITAR"],
    },
    {
      label: "Evidencias",
      to: "/coordinador/evidencias",
      icon: Image,
      permisos: ["EVIDENCIAS_VER"],
    },
    {
      label: "Reportes",
      to: "/coordinador/informes",
      icon: FileBarChart,
      permisos: ["INFORMES_VER", "REPORTES_VER", "COORDINADOR_INFORMES"],
    },
    {
      label: "Aprobar y publicar",
      to: "/coordinador/reportes-publicados",
      icon: FileCheck2,
      permisos: ["INFORMES_VER", "REPORTES_VER", "COORDINADOR_INFORMES"],
    },
  ];

  const menuVisible = menuItems.filter((item) => tienePermiso(...item.permisos));

  const logout = async () => {
    try {
      await API.post("/auth/logout", {});
    } finally {
      clearSession();
      localStorage.removeItem("token");
      navigate("/");
    }
  };

  const cerrarMobile = () => setMobileOpen(false);

  return (
    <div className="coord-shell">
      {mobileOpen && <div className="coord-backdrop" onClick={cerrarMobile} />}

      <aside
        className={[
          "coord-sidebar",
          open ? "" : "collapsed",
          mobileOpen ? "mobile-open" : "",
        ].join(" ")}
      >
        <button className="coord-close-mobile" onClick={cerrarMobile} aria-label="Cerrar menú">
          <X size={18} />
        </button>

        <div className="coord-brand">
          <div className="coord-brand-icon">
            <ShieldCheck size={26} />
          </div>
          {open && (
            <div>
              <h2>SGAHolding</h2>
              <span>Portal Coordinador</span>
            </div>
          )}
        </div>

        <div className="coord-user-mini">
          {open && (
            <>
              <strong>{user?.nombre_completo || user?.username || "Coordinador"}</strong>
              <span>{user?.empresa_nombre || "Empresa asignada"}</span>
            </>
          )}
        </div>

        <nav className="coord-menu">
          {cargandoPermisos && !esCoordinador && !esAdmin ? (
            <span className="coord-menu-loading">Cargando permisos...</span>
          ) : (
            menuVisible.map((item) => {
              const Icon = item.icon;
              return (
                <NavLink key={item.to} to={item.to} onClick={cerrarMobile}>
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
          <button className="coord-menu-toggle desktop" onClick={() => setOpen(!open)}>
            <Menu size={22} />
          </button>

          <button className="coord-menu-toggle mobile" onClick={() => setMobileOpen(true)}>
            <Menu size={22} />
          </button>

          <div>
            <h1>Módulo Coordinador PRO</h1>
            <p>Inventario, hojas de vida, mantenimientos, evidencias y reportes operativos.</p>
          </div>
          {esCoordinador && (
            <label className="coord-company-switcher">
              <span>Empresa activa</span>
              <select
                value={empresaActivaId}
                onChange={(event) => cambiarEmpresaActiva(event.target.value)}
                disabled={cargandoEmpresas || empresasAutorizadas.length <= 1}
              >
                {empresasAutorizadas.map((empresa) => (
                  <option key={empresa.id} value={empresa.id}>{empresa.nombre}</option>
                ))}
              </select>
            </label>
          )}
        </header>

        <section className="coord-content">
          <CoordinatorCompanyContext.Provider
            value={{ empresaActivaId, empresasAutorizadas, cambiarEmpresaActiva }}
          >
            <Outlet key={empresaActivaId || "sin-empresa"} />
          </CoordinatorCompanyContext.Provider>
        </section>
      </main>
    </div>
  );
}
