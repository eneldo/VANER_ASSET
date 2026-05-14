/*
===========================================================
FASE 32 — DASHBOARD COORDINADOR INTELIGENTE PRO
Archivo: frontend/src/pages/coordinador/CoordinadorDashboard.jsx
===========================================================
*/

import React, { useEffect, useMemo, useState } from "react";
import API from "../../api/axios";
import { useNavigate } from "react-router-dom";
import {
  ClipboardList,
  Clock,
  UserCheck,
  PlayCircle,
  CheckCircle2,
  XCircle,
  Wrench,
  Users,
  RefreshCw,
} from "lucide-react";
import "../../styles/coordinador.css";

export default function CoordinadorDashboard() {
  const navigate = useNavigate();

  const [mantenimientos, setMantenimientos] = useState([]);
  const [catalogos, setCatalogos] = useState({ equipos: [], tecnicos: [] });
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState("");

  const cargarDashboard = async () => {
    try {
      setCargando(true);
      setError("");

      const [resMantenimientos, resCatalogos] = await Promise.all([
        API.get("/coordinador/mantenimientos"),
        API.get("/coordinador/catalogos"),
      ]);

      setMantenimientos(resMantenimientos.data || []);
      setCatalogos(resCatalogos.data || { equipos: [], tecnicos: [] });
    } catch (err) {
      console.error("Error dashboard coordinador:", err);
      setError("No se pudo cargar el dashboard del coordinador.");
    } finally {
      setCargando(false);
    }
  };

  useEffect(() => {
    cargarDashboard();
  }, []);

  const metricas = useMemo(() => {
    return {
      total: mantenimientos.length,
      programados: mantenimientos.filter((m) => m.estado === "PROGRAMADO").length,
      asignados: mantenimientos.filter((m) => m.estado === "ASIGNADO").length,
      enProceso: mantenimientos.filter((m) => m.estado === "EN_PROCESO").length,
      finalizados: mantenimientos.filter((m) => m.estado === "FINALIZADO").length,
      anulados: mantenimientos.filter((m) => m.estado === "ANULADO").length,
      equipos: catalogos?.equipos?.length || 0,
      tecnicos: catalogos?.tecnicos?.length || 0,
    };
  }, [mantenimientos, catalogos]);

  const irAMantenimientos = (estado = "") => {
    if (estado) {
      navigate(`/coordinador/mantenimientos?estado=${estado}`);
    } else {
      navigate("/coordinador/mantenimientos");
    }
  };

  const kpis = [
    {
      label: "Total mantenimientos",
      value: metricas.total,
      icon: ClipboardList,
      className: "blue",
      onClick: () => irAMantenimientos(),
    },
    {
      label: "Programados",
      value: metricas.programados,
      icon: Clock,
      className: "cyan",
      onClick: () => irAMantenimientos("PROGRAMADO"),
    },
    {
      label: "Asignados",
      value: metricas.asignados,
      icon: UserCheck,
      className: "indigo",
      onClick: () => irAMantenimientos("ASIGNADO"),
    },
    {
      label: "En proceso",
      value: metricas.enProceso,
      icon: PlayCircle,
      className: "amber",
      onClick: () => irAMantenimientos("EN_PROCESO"),
    },
    {
      label: "Finalizados",
      value: metricas.finalizados,
      icon: CheckCircle2,
      className: "green",
      onClick: () => irAMantenimientos("FINALIZADO"),
    },
    {
      label: "Anulados",
      value: metricas.anulados,
      icon: XCircle,
      className: "red",
      onClick: () => irAMantenimientos("ANULADO"),
    },
    {
      label: "Equipos",
      value: metricas.equipos,
      icon: Wrench,
      className: "purple",
      onClick: () => navigate("/coordinador/mantenimientos"),
    },
    {
      label: "Técnicos",
      value: metricas.tecnicos,
      icon: Users,
      className: "slate",
      onClick: () => navigate("/coordinador/mantenimientos"),
    },
  ];

  if (cargando) {
    return <div className="coord-loading">Cargando dashboard operativo...</div>;
  }

  return (
    <div className="coord-page">
      <div className="coord-page-header">
        <div>
          <span className="coord-eyebrow">SGA PRO · PANEL OPERATIVO</span>
          <h2>Dashboard Coordinador</h2>
          <p>
            Control centralizado de mantenimientos, técnicos, estados y operación diaria.
          </p>
        </div>

        <button className="coord-primary-btn" onClick={cargarDashboard}>
          <RefreshCw size={17} />
          Actualizar
        </button>
      </div>

      {error && <div className="coord-alert error">{error}</div>}

      <div className="coord-kpi-grid">
        {kpis.map((item) => {
          const Icon = item.icon;

          return (
            <button
              type="button"
              className={`coord-kpi coord-kpi-click ${item.className}`}
              key={item.label}
              onClick={item.onClick}
            >
              <div className="coord-kpi-icon">
                <Icon size={24} />
              </div>

              <div>
                <strong>{item.value}</strong>
                <span>{item.label}</span>
              </div>
            </button>
          );
        })}
      </div>

      <div className="coord-card">
        <div className="coord-card-header">
          <div>
            <h3>Mantenimientos recientes</h3>
            <p>Últimos registros operativos del módulo coordinador.</p>
          </div>
        </div>

        <div className="coord-table-wrap">
          <table className="coord-table">
            <thead>
              <tr>
                <th>Equipo</th>
                <th>Técnico</th>
                <th>Tipo</th>
                <th>Estado</th>
                <th>Fecha programada</th>
                <th>Observaciones</th>
              </tr>
            </thead>

            <tbody>
              {mantenimientos.length === 0 ? (
                <tr>
                  <td colSpan="6" className="coord-empty">
                    No hay mantenimientos recientes.
                  </td>
                </tr>
              ) : (
                mantenimientos.slice(0, 8).map((m) => (
                  <tr key={m.id}>
                    <td>{m.equipo_nombre || m.equipo || "Sin equipo"}</td>
                    <td>{m.tecnico_nombre || m.tecnico || "Sin técnico"}</td>
                    <td>{m.tipo || "Sin tipo"}</td>
                    <td>
                      <span className={`coord-status ${String(m.estado || "").toLowerCase()}`}>
                        {m.estado || "SIN ESTADO"}
                      </span>
                    </td>
                    <td>{m.fecha_programada || "Sin fecha"}</td>
                    <td>{m.observaciones || "Sin observaciones"}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}