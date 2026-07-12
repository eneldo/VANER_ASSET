// ============================================================
// CLIENTE MANTENIMIENTOS PRO FULL
// Archivo: frontend/src/pages/cliente/ClienteMantenimientos.jsx
// Mejoras:
// - Búsqueda
// - Paginación
// - Scroll interno elegante
// - Tabla con altura controlada
// - Responsive PRO
// ============================================================

import { useEffect, useMemo, useState } from "react";
import API from "../../api/axios";
import { getEmpresaId } from "../../utils/multiempresa";
import {
  RefreshCcw,
  Wrench,
  Search,
  ChevronLeft,
  ChevronRight,
} from "lucide-react";

export default function ClienteMantenimientos() {
  const params = new URLSearchParams(window.location.search);
  const filtroInicial = params.get("estado") || "TODOS";

  const [mantenimientos, setMantenimientos] = useState([]);
  const [filtro, setFiltro] = useState(filtroInicial);
  const [busqueda, setBusqueda] = useState("");
  const [loading, setLoading] = useState(false);

  const [paginaActual, setPaginaActual] = useState(1);
  const registrosPorPagina = 10;

  useEffect(() => {
    cargar();
  }, []);

  async function cargar() {
    try {
      const empresaId = getEmpresaId();

      if (!empresaId) {
        alert("Este usuario no tiene empresa asociada.");
        return;
      }

      setLoading(true);
      const res = await API.get(`/cliente/${empresaId}/mantenimientos`);
      setMantenimientos(res.data || []);
    } catch (error) {
      console.error("Error cargando mantenimientos cliente:", error);
      alert("Error cargando mantenimientos.");
    } finally {
      setLoading(false);
    }
  };

  const filtrados = useMemo(() => {
    let data = [...mantenimientos];

    if (filtro === "PENDIENTES") {
      data = data.filter(
        (m) => !["FINALIZADO", "ANULADO"].includes(String(m.estado || "").toUpperCase())
      );
    }

    if (filtro === "REALIZADOS") {
      data = data.filter(
        (m) => String(m.estado || "").toUpperCase() === "FINALIZADO"
      );
    }

    if (busqueda.trim()) {
      const q = busqueda.toLowerCase();
      data = data.filter((m) => {
        const texto = `
          ${m.equipo_nombre || ""}
          ${m.tipo || ""}
          ${m.estado || ""}
          ${m.fecha_programada || ""}
          ${m.resultado_final || ""}
          ${m.observaciones || ""}
          ${m.tecnico_nombre || ""}
        `.toLowerCase();

        return texto.includes(q);
      });
    }

    return data;
  }, [mantenimientos, filtro, busqueda]);

  const totalPaginas = Math.max(1, Math.ceil(filtrados.length / registrosPorPagina));
  const inicio = (paginaActual - 1) * registrosPorPagina;
  const registrosActuales = filtrados.slice(inicio, inicio + registrosPorPagina);

  useEffect(() => {
    const timer = window.setTimeout(() => setPaginaActual(1), 0);
    return () => window.clearTimeout(timer);
  }, [filtro, busqueda]);

  return (
    <>
      <div className="cliente-header cliente-header-flex">
        <div>
          <h1>Mantenimientos</h1>
          <p>Consulta mantenimientos pendientes y realizados de tus equipos.</p>
        </div>

        <button className="cliente-btn-secondary" onClick={cargar}>
          <RefreshCcw size={16} />
          Actualizar
        </button>
      </div>

      <section className="cliente-panel">
        <div style={{ display: "flex", gap: 10, marginBottom: 18, flexWrap: "wrap" }}>
          <button
            className={filtro === "TODOS" ? "cliente-btn" : "cliente-btn-secondary"}
            onClick={() => setFiltro("TODOS")}
          >
            Todos
          </button>

          <button
            className={filtro === "PENDIENTES" ? "cliente-btn" : "cliente-btn-secondary"}
            onClick={() => setFiltro("PENDIENTES")}
          >
            Pendientes
          </button>

          <button
            className={filtro === "REALIZADOS" ? "cliente-btn" : "cliente-btn-secondary"}
            onClick={() => setFiltro("REALIZADOS")}
          >
            Realizados
          </button>
        </div>

        <div className="cliente-search-box">
          <Search size={17} />
          <input
            placeholder="Buscar equipo, técnico, tipo, estado o fecha..."
            value={busqueda}
            onChange={(e) => setBusqueda(e.target.value)}
          />
        </div>

        <div className="cliente-subpanel-header">
          <h3>
            <Wrench size={18} /> Historial de mantenimientos
          </h3>
          <span>{filtrados.length} registros</span>
        </div>

        <div className="cliente-table-scroll">
          <table className="cliente-table">
            <thead>
              <tr>
                <th>Equipo</th>
                <th>Tipo</th>
                <th>Estado</th>
                <th>Fecha programada</th>
                <th>Inicio</th>
                <th>Fin</th>
                <th>Resultado / Observación</th>
              </tr>
            </thead>

            <tbody>
              {loading ? (
                <tr>
                  <td colSpan="7" className="cliente-empty-row">
                    Cargando mantenimientos...
                  </td>
                </tr>
              ) : registrosActuales.length === 0 ? (
                <tr>
                  <td colSpan="7" className="cliente-empty-row">
                    No hay mantenimientos para mostrar.
                  </td>
                </tr>
              ) : (
                registrosActuales.map((m) => (
                  <tr key={m.id}>
                    <td>{m.equipo_nombre || m.equipo_id || "Equipo"}</td>
                    <td>{m.tipo || "—"}</td>
                    <td>
                      <span className={estadoClass(m.estado)}>{m.estado || "—"}</span>
                    </td>
                    <td>{formatDate(m.fecha_programada)}</td>
                    <td>{formatDate(m.fecha_inicio)}</td>
                    <td>{formatDate(m.fecha_fin)}</td>
                    <td>{m.resultado_final || m.observacion_estado || m.observaciones || "—"}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        <div className="cliente-pagination">
          <div className="cliente-pagination-info">
            Mostrando {registrosActuales.length} de {filtrados.length} registros
          </div>

          <button
            disabled={paginaActual === 1}
            onClick={() => setPaginaActual((p) => Math.max(1, p - 1))}
          >
            <ChevronLeft size={16} />
          </button>

          {Array.from({ length: totalPaginas }, (_, index) => (
            <button
              key={index}
              className={paginaActual === index + 1 ? "active" : ""}
              onClick={() => setPaginaActual(index + 1)}
            >
              {index + 1}
            </button>
          ))}

          <button
            disabled={paginaActual === totalPaginas}
            onClick={() => setPaginaActual((p) => Math.min(totalPaginas, p + 1))}
          >
            <ChevronRight size={16} />
          </button>
        </div>
      </section>
    </>
  );
}

function formatDate(value) {
  if (!value) return "—";
  const d = new Date(value);
  if (Number.isNaN(d.getTime())) return value;
  return d.toLocaleString();
}

function estadoClass(estado) {
  const value = String(estado || "").toUpperCase();

  if (value === "FINALIZADO") return "cliente-status ok";
  if (value === "ANULADO") return "cliente-status danger";
  if (value === "EN_PROCESO") return "cliente-status progress";
  if (value === "PAUSADO") return "cliente-status warning";
  if (value === "ASIGNADO") return "cliente-status";
  if (value === "PROGRAMADO") return "cliente-status";

  return "cliente-status";
}
