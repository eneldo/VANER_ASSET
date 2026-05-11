// ============================================================
// FASE 30 - PÁGINA ADMIN: AUDITORÍA PRO AVANZADA
// Archivo: frontend/src/pages/admin/AuditoriaPage.jsx
// Objetivo:
//   Mostrar trazabilidad del sistema con filtros, métricas,
//   tabla profesional y exportación CSV.
// ============================================================

import React, { useEffect, useMemo, useState } from "react";
import axios from "axios";
import {
  Activity,
  AlertTriangle,
  Download,
  Filter,
  ShieldCheck,
  Search,
  RefreshCw,
  Lock,
} from "lucide-react";
// este fue el que modifique import AdminLayout from "../../components/AdminLayout";

import "../../styles/auditoria.css";
import AdminLayout from "./AdminLayout";

const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

export default function AuditoriaPage() {
  const [eventos, setEventos] = useState([]);
  const [resumen, setResumen] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const [filtros, setFiltros] = useState({
    modulo: "",
    accion: "",
    nivel: "",
    usuario: "",
    fecha_inicio: "",
    fecha_fin: "",
  });

  const token = localStorage.getItem("token");

  const authHeaders = useMemo(() => ({
    headers: token ? { Authorization: `Bearer ${token}` } : {},
  }), [token]);

  // ============================================================
  // Cargar resumen de auditoría
  // ============================================================
  const cargarResumen = async () => {
    try {
      const res = await axios.get(`${API_URL}/auditoria/resumen`, authHeaders);
      setResumen(res.data);
    } catch (err) {
      console.error("Error cargando resumen de auditoría", err);
    }
  };

  // ============================================================
  // Cargar eventos con filtros
  // ============================================================
  const cargarEventos = async () => {
    setLoading(true);
    setError("");

    try {
      const params = {};
      Object.entries(filtros).forEach(([key, value]) => {
        if (value) params[key] = value;
      });

      const res = await axios.get(`${API_URL}/auditoria/`, {
        ...authHeaders,
        params: { ...params, limit: 200 },
      });

      setEventos(Array.isArray(res.data) ? res.data : []);
    } catch (err) {
      console.error("Error cargando auditoría", err);
      setError("No fue posible cargar la auditoría. Verifica backend, token y router /auditoria.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    cargarResumen();
    cargarEventos();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const cambiarFiltro = (e) => {
    const { name, value } = e.target;
    setFiltros((prev) => ({ ...prev, [name]: value }));
  };

  const limpiarFiltros = () => {
    setFiltros({
      modulo: "",
      accion: "",
      nivel: "",
      usuario: "",
      fecha_inicio: "",
      fecha_fin: "",
    });
  };

  const exportarCSV = () => {
    const params = new URLSearchParams();
    if (filtros.modulo) params.append("modulo", filtros.modulo);
    if (filtros.nivel) params.append("nivel", filtros.nivel);

    window.open(`${API_URL}/auditoria/exportar/csv?${params.toString()}`, "_blank");
  };

  const badgeNivel = (nivel) => {
    const clase = `audit-badge ${String(nivel || "INFO").toLowerCase()}`;
    return <span className={clase}>{nivel || "INFO"}</span>;
  };

  return (
    <AdminLayout>
      <section className="audit-page">
        {/* ===================================================== */}
        {/* Encabezado PRO */}
        {/* ===================================================== */}
        <div className="audit-header">
          <div>
            <span className="audit-kicker">FASE 30 · Seguridad y trazabilidad</span>
            <h1>Auditoría PRO del Sistema</h1>
            <p>
              Consulta eventos críticos, cambios de estado, acciones de usuarios,
              accesos, alertas y trazabilidad multiempresa.
            </p>
          </div>

          <div className="audit-actions">
            <button className="audit-btn secondary" onClick={() => { cargarResumen(); cargarEventos(); }}>
              <RefreshCw size={17} /> Actualizar
            </button>
            <button className="audit-btn primary" onClick={exportarCSV}>
              <Download size={17} /> Exportar CSV
            </button>
          </div>
        </div>

        {/* ===================================================== */}
        {/* Métricas */}
        {/* ===================================================== */}
        <div className="audit-metrics-grid">
          <div className="audit-card metric">
            <Activity className="audit-icon" />
            <span>Total eventos</span>
            <strong>{resumen?.total_eventos ?? 0}</strong>
          </div>

          <div className="audit-card metric">
            <ShieldCheck className="audit-icon" />
            <span>Eventos hoy</span>
            <strong>{resumen?.eventos_hoy ?? 0}</strong>
          </div>

          <div className="audit-card metric warning">
            <AlertTriangle className="audit-icon" />
            <span>Advertencias</span>
            <strong>{resumen?.eventos_warning ?? 0}</strong>
          </div>

          <div className="audit-card metric danger">
            <Lock className="audit-icon" />
            <span>Seguridad / Error</span>
            <strong>{(resumen?.eventos_security ?? 0) + (resumen?.eventos_error ?? 0)}</strong>
          </div>
        </div>

        {/* ===================================================== */}
        {/* Filtros */}
        {/* ===================================================== */}
        <div className="audit-card filters">
          <div className="audit-section-title">
            <Filter size={18} />
            <h2>Filtros de búsqueda</h2>
          </div>

          <div className="audit-filters-grid">
            <label>
              Módulo
              <input name="modulo" value={filtros.modulo} onChange={cambiarFiltro} placeholder="Ej: Equipos" />
            </label>

            <label>
              Acción
              <input name="accion" value={filtros.accion} onChange={cambiarFiltro} placeholder="Ej: CREAR" />
            </label>

            <label>
              Nivel
              <select name="nivel" value={filtros.nivel} onChange={cambiarFiltro}>
                <option value="">Todos</option>
                <option value="INFO">INFO</option>
                <option value="WARNING">WARNING</option>
                <option value="ERROR">ERROR</option>
                <option value="SECURITY">SECURITY</option>
              </select>
            </label>

            <label>
              Usuario
              <input name="usuario" value={filtros.usuario} onChange={cambiarFiltro} placeholder="Nombre usuario" />
            </label>

            <label>
              Desde
              <input type="date" name="fecha_inicio" value={filtros.fecha_inicio} onChange={cambiarFiltro} />
            </label>

            <label>
              Hasta
              <input type="date" name="fecha_fin" value={filtros.fecha_fin} onChange={cambiarFiltro} />
            </label>
          </div>

          <div className="audit-filter-actions">
            <button className="audit-btn primary" onClick={cargarEventos}>
              <Search size={17} /> Buscar
            </button>
            <button className="audit-btn secondary" onClick={limpiarFiltros}>Limpiar</button>
          </div>
        </div>

        {error && <div className="audit-error">{error}</div>}

        {/* ===================================================== */}
        {/* Tabla */}
        {/* ===================================================== */}
        <div className="audit-card table-card">
          <div className="audit-section-title">
            <Activity size={18} />
            <h2>Eventos recientes</h2>
          </div>

          <div className="audit-table-wrap">
            <table className="audit-table">
              <thead>
                <tr>
                  <th>Fecha</th>
                  <th>Nivel</th>
                  <th>Módulo</th>
                  <th>Acción</th>
                  <th>Usuario</th>
                  <th>Entidad</th>
                  <th>Descripción</th>
                  <th>IP</th>
                </tr>
              </thead>
              <tbody>
                {loading ? (
                  <tr><td colSpan="8" className="audit-empty">Cargando auditoría...</td></tr>
                ) : eventos.length === 0 ? (
                  <tr><td colSpan="8" className="audit-empty">No hay eventos para los filtros seleccionados.</td></tr>
                ) : (
                  eventos.map((e) => (
                    <tr key={e.id}>
                      <td>{new Date(e.created_at).toLocaleString()}</td>
                      <td>{badgeNivel(e.nivel)}</td>
                      <td>{e.modulo}</td>
                      <td>{e.accion}</td>
                      <td>{e.usuario_nombre || "Sistema"}</td>
                      <td>{e.entidad || "—"}</td>
                      <td className="audit-description">{e.descripcion || "—"}</td>
                      <td>{e.ip_origen || "—"}</td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      </section>
    </AdminLayout>
  );
}
