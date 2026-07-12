// ============================================================
// CRONOGRAMA CLIENTE PRO FULL
// Archivo: frontend/src/pages/cliente/ClienteCronograma.jsx
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
  CalendarDays,
  RefreshCcw,
  Search,
  ChevronLeft,
  ChevronRight,
} from "lucide-react";

export default function ClienteCronograma() {
  const [mantenimientos, setMantenimientos] = useState([]);
  const [busqueda, setBusqueda] = useState("");
  const [loading, setLoading] = useState(false);

  const [paginaActual, setPaginaActual] = useState(1);
  const registrosPorPagina = 10;

  useEffect(() => {
    cargarCronograma();
  }, []);

  async function cargarCronograma() {
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
      console.error("Error cargando cronograma cliente:", error);
      alert("Error cargando cronograma.");
    } finally {
      setLoading(false);
    }
  };

  const filtrados = useMemo(() => {
    let data = [...mantenimientos];

    if (busqueda.trim()) {
      const q = busqueda.toLowerCase();
      data = data.filter((m) => {
        const texto = `
          ${m.equipo_nombre || ""}
          ${m.tipo || ""}
          ${m.estado || ""}
          ${m.fecha_programada || ""}
          ${m.fecha_inicio || ""}
          ${m.tecnico_nombre || ""}
        `.toLowerCase();

        return texto.includes(q);
      });
    }

    return data.sort((a, b) => {
      const fa = new Date(a.fecha_programada || a.fecha_inicio || 0).getTime();
      const fb = new Date(b.fecha_programada || b.fecha_inicio || 0).getTime();
      return fa - fb;
    });
  }, [mantenimientos, busqueda]);

  const totalPaginas = Math.max(1, Math.ceil(filtrados.length / registrosPorPagina));
  const inicio = (paginaActual - 1) * registrosPorPagina;
  const registrosActuales = filtrados.slice(inicio, inicio + registrosPorPagina);

  useEffect(() => {
    const timer = window.setTimeout(() => setPaginaActual(1), 0);
    return () => window.clearTimeout(timer);
  }, [busqueda]);

  return (
    <>
      <div className="cliente-header cliente-header-flex">
        <div>
          <h1>Cronograma</h1>
          <p>Consulta la programación de mantenimientos de los equipos de tu empresa.</p>
        </div>

        <button className="cliente-btn-secondary" onClick={cargarCronograma}>
          <RefreshCcw size={16} />
          Actualizar
        </button>
      </div>

      <section className="cliente-panel">
        <div className="cliente-search-box">
          <Search size={17} />
          <input
            placeholder="Buscar equipo, tipo, estado, técnico o fecha..."
            value={busqueda}
            onChange={(e) => setBusqueda(e.target.value)}
          />
        </div>

        <div className="cliente-subpanel-header">
          <h3>
            <CalendarDays size={18} /> Programación de mantenimientos
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
                <th>Observación</th>
              </tr>
            </thead>

            <tbody>
              {loading ? (
                <tr>
                  <td colSpan="7" className="cliente-empty-row">
                    Cargando cronograma...
                  </td>
                </tr>
              ) : registrosActuales.length === 0 ? (
                <tr>
                  <td colSpan="7" className="cliente-empty-row">
                    No hay mantenimientos programados.
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
                    <td>{m.observaciones || m.resultado_final || "—"}</td>
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
  return "cliente-status";
}
