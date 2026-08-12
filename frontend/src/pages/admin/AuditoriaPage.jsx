// ============================================================
// AUDITORÍA Y MONITOREO PRO SAAS
// Archivo: frontend/src/pages/admin/AuditoriaPage.jsx
// ============================================================

import { useEffect, useMemo, useState } from "react";
import {
  Activity,
  AlertTriangle,
  CheckCircle2,
  Download,
  Eye,
  Filter,
  RefreshCw,
  Search,
  ShieldAlert,
  Wifi,
} from "lucide-react";

import api from "../../api/axios";
import AdminLayout from "./AdminLayout";
import "../../styles/auditoria-pro.css";

const SEVERIDADES = ["", "INFO", "MEDIA", "ALTA", "CRITICA"];

function formatDate(value) {
  if (!value) return "-";
  const fecha = new Date(value);
  if (Number.isNaN(fecha.getTime())) return value;

  return fecha.toLocaleString("es-CO", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export default function AuditoriaPage() {
  const [resumen, setResumen] = useState(null);
  const [eventos, setEventos] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const [filtros, setFiltros] = useState({
    q: "",
    modulo: "",
    accion: "",
    severidad: "",
  });

  const [page, setPage] = useState(0);
  const limit = 20;

  const totalPages = useMemo(
    () => Math.max(1, Math.ceil(total / limit)),
    [total]
  );

  const eventosFiltradosLocal = useMemo(() => {
    const q = filtros.q.trim().toLowerCase();

    if (!q) return eventos;

    return eventos.filter((e) => {
      const texto = `
        ${e.usuario_email || ""}
        ${e.usuario_nombre || ""}
        ${e.rol || ""}
        ${e.modulo || ""}
        ${e.accion || ""}
        ${e.ruta || ""}
        ${e.ip_origen || ""}
        ${e.request_id || ""}
        ${e.detalle || ""}
      `.toLowerCase();

      return texto.includes(q);
    });
  }, [eventos, filtros.q]);

  const cargarResumen = async () => {
    const { data } = await api.get("/auditoria-pro/resumen");
    setResumen(data);
  };

  const cargarEventos = async () => {
    setLoading(true);
    setError("");

    try {
      const params = {
        limit,
        offset: page * limit,
      };

      if (filtros.modulo) params.modulo = filtros.modulo;
      if (filtros.accion) params.accion = filtros.accion;
      if (filtros.severidad) params.severidad = filtros.severidad;

      const { data } = await api.get("/auditoria-pro/eventos", { params });

      setEventos(Array.isArray(data.eventos) ? data.eventos : []);
      setTotal(data.total || 0);
    } catch (err) {
      console.error("Error cargando auditoría:", err);
      setError(
        err.response?.data?.detail ||
          "No fue posible cargar la auditoría PRO."
      );
    } finally {
      setLoading(false);
    }
  };

  const cargarTodo = async () => {
    try {
      setError("");
      await Promise.all([cargarResumen(), cargarEventos()]);
    } catch (err) {
      console.error(err);
      setError("Error cargando el panel de auditoría PRO.");
    }
  };

  useEffect(() => {
    const timer = window.setTimeout(() => cargarTodo(), 0);
    return () => window.clearTimeout(timer);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [page]);

  const handleFiltro = (e) => {
    const { name, value } = e.target;
    setFiltros((prev) => ({ ...prev, [name]: value }));
  };

  const aplicarFiltros = () => {
    setPage(0);
    setTimeout(cargarEventos, 0);
  };

  const limpiarFiltros = () => {
    setFiltros({
      q: "",
      modulo: "",
      accion: "",
      severidad: "",
    });
    setPage(0);
    setTimeout(cargarEventos, 0);
  };

  const exportarCSV = () => {
    const headers = [
      "Fecha",
      "Usuario",
      "Rol",
      "Módulo",
      "Acción",
      "Severidad",
      "Permitido",
      "Método",
      "Ruta",
      "IP",
      "Detalle",
    ];

    const rows = eventosFiltradosLocal.map((e) => [
      formatDate(e.creado_en),
      e.usuario_email || "Sistema",
      e.rol || "-",
      e.modulo || "-",
      e.accion || "-",
      e.severidad || "-",
      e.permitido ? "SI" : "NO",
      e.metodo || "-",
      e.ruta || "-",
      e.ip_origen || "-",
      (e.detalle || "").replace(/\n/g, " "),
    ]);

    const csv = [headers, ...rows]
      .map((row) =>
        row.map((cell) => `"${String(cell).replace(/"/g, '""')}"`).join(",")
      )
      .join("\n");

    const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");

    a.href = url;
    a.download = `auditoria_pro_${new Date().toISOString().slice(0, 10)}.csv`;
    a.click();

    URL.revokeObjectURL(url);
  };

  return (
    <AdminLayout className="audit-shell" contentClassName="audit-main">
        <section className="audit-header">
          <div>
            <span className="audit-eyebrow">FASE 31.5 · Seguridad SaaS</span>
            <h1>Auditoría y Monitoreo PRO</h1>
            <p>
              Trazabilidad empresarial de accesos, acciones críticas, errores,
              módulos consultados y actividad registrada por backend.
            </p>
          </div>

          <div className="audit-header-actions">
            <button className="audit-btn audit-btn-secondary" onClick={cargarTodo}>
              <RefreshCw size={17} />
              Actualizar
            </button>

            <button className="audit-btn audit-btn-primary" onClick={exportarCSV}>
              <Download size={17} />
              Exportar CSV
            </button>
          </div>
        </section>

        {error && <div className="audit-alert">{error}</div>}

        <section className="audit-kpis">
          <article className="audit-kpi-card">
            <div className="audit-kpi-icon blue">
              <Activity size={22} />
            </div>
            <div>
              <span>Total eventos</span>
              <strong>{resumen?.total_eventos ?? 0}</strong>
            </div>
          </article>

          <article className="audit-kpi-card">
            <div className="audit-kpi-icon green">
              <CheckCircle2 size={22} />
            </div>
            <div>
              <span>Permitidos</span>
              <strong>{resumen?.permitidos ?? 0}</strong>
            </div>
          </article>

          <article className="audit-kpi-card">
            <div className="audit-kpi-icon red">
              <ShieldAlert size={22} />
            </div>
            <div>
              <span>Denegados</span>
              <strong>{resumen?.denegados ?? 0}</strong>
            </div>
          </article>

          <article className="audit-kpi-card">
            <div className="audit-kpi-icon amber">
              <AlertTriangle size={22} />
            </div>
            <div>
              <span>Errores HTTP</span>
              <strong>{resumen?.errores ?? 0}</strong>
            </div>
          </article>

          <article className="audit-kpi-card">
            <div className="audit-kpi-icon cyan">
              <Eye size={22} />
            </div>
            <div>
              <span>Página actual</span>
              <strong>{page + 1}</strong>
            </div>
          </article>

          <article className="audit-kpi-card">
            <div className="audit-kpi-icon purple">
              <Wifi size={22} />
            </div>
            <div>
              <span>Registros vista</span>
              <strong>{eventosFiltradosLocal.length}</strong>
            </div>
          </article>
        </section>

        <section className="audit-panel">
          <div className="audit-panel-title">
            <div>
              <h2>Eventos del sistema</h2>
              <p>Consulta filtrada de la actividad registrada por backend.</p>
            </div>
            <span>{total} registros</span>
          </div>

          <div className="audit-filters">
            <div className="audit-search">
              <Search size={17} />
              <input
                name="q"
                value={filtros.q}
                onChange={handleFiltro}
                placeholder="Buscar usuario, ruta, IP, request ID..."
              />
            </div>

            <input
              name="modulo"
              value={filtros.modulo}
              onChange={handleFiltro}
              placeholder="Módulo"
            />

            <input
              name="accion"
              value={filtros.accion}
              onChange={handleFiltro}
              placeholder="Acción"
            />

            <select
              name="severidad"
              value={filtros.severidad}
              onChange={handleFiltro}
            >
              {SEVERIDADES.map((sev) => (
                <option key={sev || "all"} value={sev}>
                  {sev || "Todas"}
                </option>
              ))}
            </select>

            <button className="audit-btn audit-btn-primary" onClick={aplicarFiltros}>
              <Filter size={16} />
              Filtrar
            </button>

            <button className="audit-btn audit-btn-light" onClick={limpiarFiltros}>
              Limpiar
            </button>
          </div>

          <div className="audit-table-wrap">
            <table className="audit-table">
              <thead>
                <tr>
                  <th>Fecha</th>
                  <th>Usuario</th>
                  <th>Módulo</th>
                  <th>Acción</th>
                  <th>Resultado</th>
                  <th>Severidad</th>
                  <th>Ruta</th>
                  <th>IP</th>
                </tr>
              </thead>

              <tbody>
                {loading ? (
                  <tr>
                    <td colSpan="8" className="audit-empty">
                      Cargando eventos...
                    </td>
                  </tr>
                ) : eventosFiltradosLocal.length === 0 ? (
                  <tr>
                    <td colSpan="8" className="audit-empty">
                      No hay eventos para los filtros seleccionados.
                    </td>
                  </tr>
                ) : (
                  eventosFiltradosLocal.map((e) => (
                    <tr key={e.id}>
                      <td>{formatDate(e.creado_en)}</td>

                      <td>
                        <strong>{e.usuario_email || "Sistema"}</strong>
                        <small>{e.rol || "-"}</small>
                      </td>

                      <td>{e.modulo || "-"}</td>
                      <td>{e.accion || "-"}</td>

                      <td>
                        <span
                          className={
                            e.permitido ? "audit-status ok" : "audit-status denied"
                          }
                        >
                          {e.permitido ? (
                            <CheckCircle2 size={14} />
                          ) : (
                            <ShieldAlert size={14} />
                          )}
                          {e.permitido ? "Permitido" : "Denegado"}
                        </span>
                      </td>

                      <td>
                        <span
                          className={`audit-severity ${String(
                            e.severidad || "info"
                          ).toLowerCase()}`}
                        >
                          {e.severidad || "INFO"}
                        </span>
                      </td>

                      <td className="audit-route">
                        {e.metodo || ""} {e.ruta || "-"}
                      </td>

                      <td>{e.ip_origen || "-"}</td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>

          <div className="audit-pagination">
            <button
              disabled={page === 0}
              onClick={() => setPage((p) => Math.max(0, p - 1))}
            >
              Anterior
            </button>

            <span>
              Página {page + 1} de {totalPages}
            </span>

            <button
              disabled={page + 1 >= totalPages}
              onClick={() => setPage((p) => p + 1)}
            >
              Siguiente
            </button>
          </div>
        </section>
    </AdminLayout>
  );
}
