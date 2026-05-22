import React, { useEffect, useMemo, useState } from "react";
import {
  Search,
  Plus,
  Pencil,
  Trash2,
  MonitorCog,
  ShieldAlert,
  CircleCheckBig,
  CircleX,
  RefreshCw,
  Eye,
} from "lucide-react";

import AdminLayout from "./AdminLayout";

import "../../styles/equipos-saas-pro-enterprise.css";

const API_URL = import.meta.env.VITE_API_URL;

export default function EquiposPage() {
  const [equipos, setEquipos] = useState([]);
  const [loading, setLoading] = useState(true);

  const [busqueda, setBusqueda] = useState("");

  const [paginaActual, setPaginaActual] = useState(1);

  const equiposPorPagina = 10;

  // ============================================================
  // CARGAR EQUIPOS
  // ============================================================

  const cargarEquipos = async () => {
    try {
      setLoading(true);

      const response = await fetch(`${API_URL}/equipos/`);

      if (!response.ok) {
        throw new Error("Error cargando equipos");
      }

      const data = await response.json();

      setEquipos(data);
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    cargarEquipos();
  }, []);

  // ============================================================
  // FILTRO
  // ============================================================

  const equiposFiltrados = useMemo(() => {
    return equipos.filter((equipo) => {
      const texto = `
        ${equipo.nombre || ""}
        ${equipo.marca || ""}
        ${equipo.modelo || ""}
        ${equipo.serie || ""}
        ${equipo.codigo_inventario || ""}
      `.toLowerCase();

      return texto.includes(busqueda.toLowerCase());
    });
  }, [equipos, busqueda]);

  // ============================================================
  // PAGINACIÓN
  // ============================================================

  const totalPaginas = Math.ceil(
    equiposFiltrados.length / equiposPorPagina
  );

  const indiceInicial =
    (paginaActual - 1) * equiposPorPagina;

  const equiposPaginados =
    equiposFiltrados.slice(
      indiceInicial,
      indiceInicial + equiposPorPagina
    );

  // ============================================================
  // KPIs
  // ============================================================

  const totalEquipos = equipos.length;

  const operativos = equipos.filter(
    (e) => e.estado === "OPERATIVO"
  ).length;

  const mantenimiento = equipos.filter(
    (e) => e.estado === "MANTENIMIENTO"
  ).length;

  const fueraServicio = equipos.filter(
    (e) => e.estado === "FUERA_SERVICIO"
  ).length;

  // ============================================================
  // RENDER
  // ============================================================

  return (
    <AdminLayout>
      <div className="equipos-enterprise-page">

        {/* ================================================= */}
        {/* HEADER */}
        {/* ================================================= */}

        <div className="enterprise-header">
          <div>
            <h1>Inventario de Equipos</h1>
            <p>
              Gestión empresarial de activos,
              mantenimiento y criticidad.
            </p>
          </div>

          <button className="btn-primary-enterprise">
            <Plus size={18} />
            Nuevo Equipo
          </button>
        </div>

        {/* ================================================= */}
        {/* KPIs */}
        {/* ================================================= */}

        <div className="enterprise-kpis">

          <div className="enterprise-kpi-card">
            <div className="kpi-icon blue">
              <MonitorCog size={28} />
            </div>

            <div>
              <h3>Total Equipos</h3>
              <h2>{totalEquipos}</h2>
            </div>
          </div>

          <div className="enterprise-kpi-card">
            <div className="kpi-icon green">
              <CircleCheckBig size={28} />
            </div>

            <div>
              <h3>Operativos</h3>
              <h2>{operativos}</h2>
            </div>
          </div>

          <div className="enterprise-kpi-card">
            <div className="kpi-icon orange">
              <RefreshCw size={28} />
            </div>

            <div>
              <h3>Mantenimiento</h3>
              <h2>{mantenimiento}</h2>
            </div>
          </div>

          <div className="enterprise-kpi-card">
            <div className="kpi-icon red">
              <ShieldAlert size={28} />
            </div>

            <div>
              <h3>Fuera Servicio</h3>
              <h2>{fueraServicio}</h2>
            </div>
          </div>

        </div>

        {/* ================================================= */}
        {/* FILTROS */}
        {/* ================================================= */}

        <div className="enterprise-toolbar">

          <div className="search-enterprise">
            <Search size={18} />

            <input
              type="text"
              placeholder="Buscar equipo..."
              value={busqueda}
              onChange={(e) =>
                setBusqueda(e.target.value)
              }
            />
          </div>

        </div>

        {/* ================================================= */}
        {/* TABLA */}
        {/* ================================================= */}

        <div className="enterprise-table-wrapper">

          <table className="enterprise-table">

            <thead>
              <tr>
                <th>Código</th>
                <th>Equipo</th>
                <th>Marca</th>
                <th>Modelo</th>
                <th>Serie</th>
                <th>Estado</th>
                <th>Criticidad</th>
                <th>Acciones</th>
              </tr>
            </thead>

            <tbody>

              {loading ? (
                <tr>
                  <td colSpan="8">
                    <div className="loading-enterprise">
                      Cargando equipos...
                    </div>
                  </td>
                </tr>
              ) : equiposPaginados.length === 0 ? (
                <tr>
                  <td colSpan="8">
                    <div className="empty-enterprise">
                      No existen equipos registrados.
                    </div>
                  </td>
                </tr>
              ) : (
                equiposPaginados.map((equipo) => (
                  <tr key={equipo.id}>

                    <td>
                      {equipo.codigo_inventario}
                    </td>

                    <td className="equipo-cell">
                      <div className="equipo-avatar">
                        <MonitorCog size={18} />
                      </div>

                      <div>
                        <strong>{equipo.nombre}</strong>

                        <span>
                          {equipo.ubicacion || "Sin ubicación"}
                        </span>
                      </div>
                    </td>

                    <td>{equipo.marca}</td>

                    <td>{equipo.modelo}</td>

                    <td>{equipo.serie}</td>

                    <td>
                      <span
                        className={`estado-badge ${(
                          equipo.estado || ""
                        ).toLowerCase()}`}
                      >
                        {equipo.estado}
                      </span>
                    </td>

                    <td>
                      <span
                        className={`criticidad-badge ${(
                          equipo.criticidad || ""
                        ).toLowerCase()}`}
                      >
                        {equipo.criticidad}
                      </span>
                    </td>

                    <td>
                      <div className="acciones-enterprise">

                        <button className="btn-action blue">
                          <Eye size={16} />
                        </button>

                        <button className="btn-action orange">
                          <Pencil size={16} />
                        </button>

                        <button className="btn-action red">
                          <Trash2 size={16} />
                        </button>

                      </div>
                    </td>

                  </tr>
                ))
              )}

            </tbody>

          </table>

        </div>

        {/* ================================================= */}
        {/* PAGINACIÓN */}
        {/* ================================================= */}

        <div className="enterprise-pagination">

          <button
            disabled={paginaActual === 1}
            onClick={() =>
              setPaginaActual((prev) => prev - 1)
            }
          >
            Anterior
          </button>

          <span>
            Página {paginaActual} de {totalPaginas || 1}
          </span>

          <button
            disabled={paginaActual === totalPaginas}
            onClick={() =>
              setPaginaActual((prev) => prev + 1)
            }
          >
            Siguiente
          </button>

        </div>

      </div>
    </AdminLayout>
  );
}