// ============================================================
// Página: Reportes PRO
// Proyecto: SGA PRO
// Descripción:
// Dashboard de reportes administrativos con indicadores,
// gráficas y resumen ejecutivo.
// ============================================================

import React, { useEffect, useState } from "react";
import axios from "axios";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from "recharts";
import {
  Building2,
  MapPin,
  MonitorCog,
  Wrench,
  Users,
  ShieldCheck,
} from "lucide-react";

import "../../styles/reportes.css";

const API_URL = "http://127.0.0.1:8000";

export default function ReportesPage() {
  const [resumen, setResumen] = useState({});
  const [mantenimientosEstado, setMantenimientosEstado] = useState([]);
  const [equiposEstado, setEquiposEstado] = useState([]);
  const [auditoria, setAuditoria] = useState([]);

  useEffect(() => {
    cargarReportes();
  }, []);

  const cargarReportes = async () => {
    try {
      const [r1, r2, r3, r4] = await Promise.all([
        axios.get(`${API_URL}/reportes/resumen`),
        axios.get(`${API_URL}/reportes/mantenimientos-por-estado`),
        axios.get(`${API_URL}/reportes/equipos-por-estado`),
        axios.get(`${API_URL}/reportes/auditoria-reciente`),
      ]);

      setResumen(r1.data);
      setMantenimientosEstado(r2.data);
      setEquiposEstado(r3.data);
      setAuditoria(r4.data);
    } catch (error) {
      console.error("Error cargando reportes:", error);
    }
  };

  const cards = [
    {
      label: "Empresas",
      value: resumen.empresas || 0,
      icon: <Building2 />,
    },
    {
      label: "Sedes",
      value: resumen.sedes || 0,
      icon: <MapPin />,
    },
    {
      label: "Equipos",
      value: resumen.equipos || 0,
      icon: <MonitorCog />,
    },
    {
      label: "Mantenimientos",
      value: resumen.mantenimientos || 0,
      icon: <Wrench />,
    },
    {
      label: "Técnicos",
      value: resumen.tecnicos || 0,
      icon: <Users />,
    },
    {
      label: "Eventos Auditoría",
      value: resumen.auditoria || 0,
      icon: <ShieldCheck />,
    },
  ];

  return (
    <div className="reportes-page">
      <div className="reportes-header">
        <div>
          <h1>Reportes PRO</h1>
          <p>Resumen ejecutivo del sistema SGA PRO.</p>
        </div>

        <button onClick={cargarReportes}>Actualizar</button>
      </div>

      <section className="reportes-cards">
        {cards.map((card, index) => (
          <div className="reporte-card" key={index}>
            <div className="reporte-icon">{card.icon}</div>
            <div>
              <h3>{card.value}</h3>
              <p>{card.label}</p>
            </div>
          </div>
        ))}
      </section>

      <section className="reportes-grid">
        <div className="reporte-panel">
          <h2>Mantenimientos por Estado</h2>

          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={mantenimientosEstado}>
              <XAxis dataKey="estado" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="total" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="reporte-panel">
          <h2>Equipos por Estado</h2>

          <ResponsiveContainer width="100%" height={280}>
            <PieChart>
              <Pie
                data={equiposEstado}
                dataKey="total"
                nameKey="estado"
                outerRadius={95}
                label
              >
                {equiposEstado.map((_, index) => (
                  <Cell key={index} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </section>

      <section className="reporte-panel auditoria-preview">
        <h2>Auditoría Reciente</h2>

        <div className="reportes-table-wrap">
          <table>
            <thead>
              <tr>
                <th>Fecha</th>
                <th>Usuario</th>
                <th>Rol</th>
                <th>Módulo</th>
                <th>Acción</th>
                <th>Descripción</th>
              </tr>
            </thead>

            <tbody>
              {auditoria.map((item) => (
                <tr key={item.id}>
                  <td>{new Date(item.fecha).toLocaleString()}</td>
                  <td>{item.usuario || "Sistema"}</td>
                  <td>{item.rol || "-"}</td>
                  <td>{item.modulo}</td>
                  <td>
                    <span className="badge-accion">{item.accion}</span>
                  </td>
                  <td>{item.descripcion || "-"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}