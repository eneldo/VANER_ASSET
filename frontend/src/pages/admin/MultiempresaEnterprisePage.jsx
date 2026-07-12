// ============================================================
// MULTIEMPRESA ENTERPRISE PRO
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
  // CARGAR DATOS
  // ============================================================

  const cargarDatos = async () => {

    try {

      setLoading(true);

      const [dashboardRes, empresasRes] = await Promise.all([
        axios.get("/multiempresa-enterprise/dashboard"),
        axios.get("/multiempresa-enterprise/empresas"),
      ]);

      setDashboard(dashboardRes.data);

      setEmpresas(
        empresasRes.data?.empresas || []
      );

    } catch (error) {

      console.error(
        "Error cargando multiempresa:",
        error
      );

      setEmpresas([]);

    } finally {

      setLoading(false);

    }

  };

  useEffect(() => {
    const timer = window.setTimeout(() => cargarDatos(), 0);
    return () => window.clearTimeout(timer);
  }, []);

  // ============================================================
  // NAVEGACIÓN INTELIGENTE
  // ============================================================

  const abrirEmpresa = (empresaId) => {

    navigate(
      `/admin/empresas?empresa_id=${empresaId}`
    );

  };

  const abrirSedes = (empresaId, e) => {

    e.stopPropagation();

    navigate(
      `/admin/sedes?empresa_id=${empresaId}`
    );

  };

  const abrirEquipos = (empresaId, e) => {

    e.stopPropagation();

    navigate(
      `/admin/equipos?empresa_id=${empresaId}`
    );

  };

  const abrirUsuarios = (empresaId, e) => {

    e.stopPropagation();

    navigate(
      `/admin/usuarios?empresa_id=${empresaId}`
    );

  };

  const abrirMantenimientos = (empresaId, e) => {

    e.stopPropagation();

    navigate(
      `/admin/mantenimientos?empresa_id=${empresaId}`
    );

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

            <h1>
              Panel Multiempresa Enterprise PRO
            </h1>

            <p>
              Gestión SaaS real de empresas,
              sedes, usuarios, equipos y
              mantenimientos con aislamiento
              por empresa.
            </p>

          </div>

          <button
            className="multiempresa-refresh"
            onClick={cargarDatos}
            disabled={loading}
          >

            <RefreshCw size={18} />

            {loading
              ? "Actualizando..."
              : "Actualizar"}

          </button>

        </div>

        {/* ================================================= */}
        {/* KPI GLOBALES */}
        {/* ================================================= */}

        <div className="multiempresa-kpi-grid">

          <div className="multiempresa-kpi-card">

            <Building2 size={22} />

            <div>
              <span>Empresas</span>
              <strong>
                {dashboard.empresas || 0}
              </strong>
            </div>

          </div>

          <div className="multiempresa-kpi-card">

            <Users size={22} />

            <div>
              <span>Usuarios</span>
              <strong>
                {dashboard.usuarios || 0}
              </strong>
            </div>

          </div>

          <div className="multiempresa-kpi-card">

            <MonitorCog size={22} />

            <div>
              <span>Equipos</span>
              <strong>
                {dashboard.equipos || 0}
              </strong>
            </div>

          </div>

          <div className="multiempresa-kpi-card">

            <Wrench size={22} />

            <div>
              <span>Mantenimientos</span>
              <strong>
                {dashboard.mantenimientos || 0}
              </strong>
            </div>

          </div>

        </div>

        {/* ================================================= */}
        {/* EMPRESAS */}
        {/* ================================================= */}

        {loading ? (

          <div className="multiempresa-empty">
            Cargando empresas...
          </div>

        ) : empresas.length === 0 ? (

          <div className="multiempresa-empty">
            No existen empresas registradas.
          </div>

        ) : (

          <div className="multiempresa-grid">

            {empresas.map((empresa) => (

              <button
                key={empresa.id}
                type="button"
                className="empresa-card"
                onClick={() =>
                  abrirEmpresa(empresa.id)
                }
              >

                {/* ===================================== */}
                {/* TOP */}
                {/* ===================================== */}

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

                {/* ===================================== */}
                {/* INFO */}
                {/* ===================================== */}

                <div className="empresa-info">

                  <h3>
                    {empresa.nombre}
                  </h3>

                  <p>
                    {empresa.nit
                      ? `NIT: ${empresa.nit}`
                      : "Sin NIT"}
                  </p>

                  <small>
                    {empresa.correo ||
                      "Sin correo"}
                  </small>

                </div>

                {/* ===================================== */}
                {/* KPIS CLICKABLES */}
                {/* ===================================== */}

                <div className="empresa-body">

                  {/* SEDES */}

                  <button
                    type="button"
                    className="empresa-kpi-btn"
                    onClick={(e) =>
                      abrirSedes(
                        empresa.id,
                        e
                      )
                    }
                  >

                    <MapPin size={16} />

                    <strong>
                      {empresa.sedes}
                    </strong>

                    <p>Sedes</p>

                  </button>

                  {/* EQUIPOS */}

                  <button
                    type="button"
                    className="empresa-kpi-btn"
                    onClick={(e) =>
                      abrirEquipos(
                        empresa.id,
                        e
                      )
                    }
                  >

                    <MonitorCog size={16} />

                    <strong>
                      {empresa.equipos}
                    </strong>

                    <p>Equipos</p>

                  </button>

                  {/* USUARIOS */}

                  <button
                    type="button"
                    className="empresa-kpi-btn"
                    onClick={(e) =>
                      abrirUsuarios(
                        empresa.id,
                        e
                      )
                    }
                  >

                    <Users size={16} />

                    <strong>
                      {empresa.usuarios}
                    </strong>

                    <p>Usuarios</p>

                  </button>

                  {/* MANTENIMIENTOS */}

                  <button
                    type="button"
                    className="empresa-kpi-btn"
                    onClick={(e) =>
                      abrirMantenimientos(
                        empresa.id,
                        e
                      )
                    }
                  >

                    <Wrench size={16} />

                    <strong>
                      {empresa.mantenimientos}
                    </strong>

                    <p>Manten.</p>

                  </button>

                </div>

                <div className="empresa-action">
                  Ver empresa completa
                </div>

              </button>

            ))}

          </div>

        )}

      </div>

    </AdminLayout>

  );

}
