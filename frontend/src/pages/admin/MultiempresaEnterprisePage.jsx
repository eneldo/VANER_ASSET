// ============================================================
// MULTIEMPRESA ENTERPRISE PRO
// Archivo: frontend/src/pages/admin/MultiempresaEnterprisePage.jsx
// FASE 34.3 — Panel Multiempresa Enterprise PRO
// ============================================================

import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import {
  Building2,
  Users,
  MonitorCog,
  MapPin,
  Wrench,
  RefreshCw,
} from "lucide-react";

import AdminLayout from "./AdminLayout";
import axios from "../../api/axios";

import "../../styles/multiempresa-enterprise.css";

export default function MultiempresaEnterprisePage() {
  const navigate = useNavigate();

  const [empresas, setEmpresas] = useState([]);
  const [dashboard, setDashboard] = useState({
    empresas: 0,
    usuarios: 0,
    equipos: 0,
    mantenimientos: 0,
  });

  const [loading, setLoading] = useState(true);

  // ============================================================
  // CARGAR DATOS REALES DESDE POSTGRESQL
  // ============================================================

  const cargarDatos = async () => {
    try {
      setLoading(true);

      const [dashboardRes, empresasRes] = await Promise.all([
        axios.get("/multiempresa-enterprise/dashboard"),
        axios.get("/multiempresa-enterprise/empresas"),
      ]);

      setDashboard(dashboardRes.data);

      setEmpresas(empresasRes.data?.empresas || []);
    } catch (error) {
      console.error("Error cargando Multiempresa Enterprise:", error);
      setEmpresas([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    cargarDatos();
  }, []);

  // ============================================================
  // IR A EMPRESA REAL
  // ============================================================

  const abrirEmpresa = (empresaId) => {
    /*
      Si tu EmpresasPage tiene edición por query string,
      aquí se envía el ID real de la empresa.
    */
    navigate(`/admin/empresas?empresa_id=${empresaId}`);
  };

  return (
    <AdminLayout>
      <div className="multiempresa-page">

        {/* ================================================= */}
        {/* HEADER */}
        {/* ================================================= */}

        <div className="multiempresa-header">
          <div>
            <span className="multiempresa-badge">
              MULTIEMPRESA ENTERPRISE
            </span>

            <h1>Panel Multiempresa Enterprise PRO</h1>

            <p>
              Gestión SaaS real de empresas, sedes, usuarios,
              equipos y mantenimientos con aislamiento por empresa.
            </p>
          </div>

          <button
            className="multiempresa-refresh"
            onClick={cargarDatos}
            disabled={loading}
          >
            <RefreshCw size={18} />
            {loading ? "Actualizando..." : "Actualizar"}
          </button>
        </div>

        {/* ================================================= */}
        {/* KPIS GLOBALES */}
        {/* ================================================= */}

        <div className="multiempresa-kpi-grid">

          <div className="multiempresa-kpi-card">
            <Building2 size={22} />
            <div>
              <span>Empresas</span>
              <strong>{dashboard.empresas || 0}</strong>
            </div>
          </div>

          <div className="multiempresa-kpi-card">
            <Users size={22} />
            <div>
              <span>Usuarios</span>
              <strong>{dashboard.usuarios || 0}</strong>
            </div>
          </div>

          <div className="multiempresa-kpi-card">
            <MonitorCog size={22} />
            <div>
              <span>Equipos</span>
              <strong>{dashboard.equipos || 0}</strong>
            </div>
          </div>

          <div className="multiempresa-kpi-card">
            <Wrench size={22} />
            <div>
              <span>Mantenimientos</span>
              <strong>{dashboard.mantenimientos || 0}</strong>
            </div>
          </div>

        </div>

        {/* ================================================= */}
        {/* EMPRESAS REALES */}
        {/* ================================================= */}

        {loading ? (
          <div className="multiempresa-empty">
            Cargando empresas reales desde PostgreSQL...
          </div>
        ) : empresas.length === 0 ? (
          <div className="multiempresa-empty">
            No hay empresas creadas en el sistema.
          </div>
        ) : (
          <div className="multiempresa-grid">
            {empresas.map((empresa) => (
              <button
                type="button"
                className="empresa-card"
                key={empresa.id}
                onClick={() => abrirEmpresa(empresa.id)}
              >
                <div className="empresa-top">
                  <div className="empresa-icon">
                    <Building2 size={22} />
                  </div>

                  <span
                    className={
                      empresa.activo
                        ? "empresa-status activa"
                        : "empresa-status inactiva"
                    }
                  >
                    {empresa.estado}
                  </span>
                </div>

                <div className="empresa-info">
                  <h3>{empresa.nombre}</h3>

                  <p>
                    {empresa.nit
                      ? `NIT: ${empresa.nit}`
                      : "Sin NIT registrado"}
                  </p>

                  <small>
                    {empresa.correo || "Sin correo registrado"}
                  </small>
                </div>

                <div className="empresa-body">
                  <div>
                    <MapPin size={16} />
                    <strong>{empresa.sedes}</strong>
                    <p>Sedes</p>
                  </div>

                  <div>
                    <MonitorCog size={16} />
                    <strong>{empresa.equipos}</strong>
                    <p>Equipos</p>
                  </div>

                  <div>
                    <Users size={16} />
                    <strong>{empresa.usuarios}</strong>
                    <p>Usuarios</p>
                  </div>

                  <div>
                    <Wrench size={16} />
                    <strong>{empresa.mantenimientos}</strong>
                    <p>Manten.</p>
                  </div>
                </div>

                <div className="empresa-action">
                  Ver empresa
                </div>
              </button>
            ))}
          </div>
        )}

      </div>
    </AdminLayout>
  );
}