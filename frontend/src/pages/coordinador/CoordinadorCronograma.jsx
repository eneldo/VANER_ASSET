/*
===========================================================
FASE 32 — CRONOGRAMA COORDINADOR PRO
Archivo: frontend/src/pages/coordinador/CoordinadorCronograma.jsx
===========================================================
*/

import React, { useEffect, useMemo, useState } from "react";
import API from "../../api/axios";
import { CalendarDays, Clock, ClipboardList, Search } from "lucide-react";
import "../../styles/coordinador.css";

export default function CoordinadorCronograma() {
  const [mantenimientos, setMantenimientos] = useState([]);
  const [busqueda, setBusqueda] = useState("");
  const [estado, setEstado] = useState("");
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState("");

  const cargarCronograma = async () => {
    try {
      setCargando(true);
      setError("");

      try {
        const res = await API.get("/coordinador/cronograma");
        setMantenimientos(res.data || []);
      } catch {
        const res = await API.get("/coordinador/mantenimientos");
        setMantenimientos(res.data || []);
      }
    } catch (err) {
      console.error("Error cargando cronograma:", err);
      setError("No se pudo cargar el cronograma.");
    } finally {
      setCargando(false);
    }
  };

  useEffect(() => {
    cargarCronograma();
  }, []);

  const listaFiltrada = useMemo(() => {
    return mantenimientos
      .filter((m) => {
        const texto = `
          ${m.equipo_nombre || ""}
          ${m.tecnico_nombre || ""}
          ${m.tipo || ""}
          ${m.estado || ""}
          ${m.observaciones || ""}
        `.toLowerCase();

        const coincideBusqueda = texto.includes(busqueda.toLowerCase());
        const coincideEstado = estado ? m.estado === estado : true;

        return coincideBusqueda && coincideEstado;
      })
      .sort((a, b) => {
        const fa = a.fecha_programada ? new Date(a.fecha_programada) : new Date("2999-01-01");
        const fb = b.fecha_programada ? new Date(b.fecha_programada) : new Date("2999-01-01");
        return fa - fb;
      });
  }, [mantenimientos, busqueda, estado]);

  if (cargando) {
    return <div className="coord-loading">Cargando cronograma...</div>;
  }

  return (
    <div className="coord-page">
      <div className="coord-page-header">
        <div>
          <span className="coord-eyebrow">Agenda operativa</span>
          <h2>Cronograma de Mantenimientos</h2>
          <p>Vista organizada por fecha programada, técnico, equipo y estado.</p>
        </div>

        <button className="coord-primary-btn" onClick={cargarCronograma}>
          Actualizar
        </button>
      </div>

      {error && <div className="coord-alert error">{error}</div>}

      <div className="coord-filters">
        <div className="coord-search">
          <Search size={18} />
          <input
            type="text"
            placeholder="Buscar por equipo, técnico, tipo u observación..."
            value={busqueda}
            onChange={(e) => setBusqueda(e.target.value)}
          />
        </div>

        <select value={estado} onChange={(e) => setEstado(e.target.value)}>
          <option value="">Todos los estados</option>
          <option value="PROGRAMADO">PROGRAMADO</option>
          <option value="ASIGNADO">ASIGNADO</option>
          <option value="EN_PROCESO">EN_PROCESO</option>
          <option value="PAUSADO">PAUSADO</option>
          <option value="FINALIZADO">FINALIZADO</option>
          <option value="ANULADO">ANULADO</option>
        </select>
      </div>

      <div className="coord-timeline">
        {listaFiltrada.length === 0 ? (
          <div className="coord-empty-card">
            <CalendarDays size={36} />
            <h3>No hay mantenimientos en el cronograma</h3>
            <p>Cuando existan mantenimientos programados aparecerán en esta vista.</p>
          </div>
        ) : (
          listaFiltrada.map((m) => (
            <article className="coord-timeline-item" key={m.id}>
              <div className="coord-timeline-date">
                <CalendarDays size={22} />
                <strong>{m.fecha_programada || "Sin fecha"}</strong>
                <span>{m.estado || "SIN ESTADO"}</span>
              </div>

              <div className="coord-timeline-body">
                <div className="coord-timeline-title">
                  <ClipboardList size={20} />
                  <h3>{m.equipo_nombre || m.equipo || "Mantenimiento"}</h3>
                </div>

                <div className="coord-timeline-grid">
                  <p>
                    <strong>Tipo:</strong> {m.tipo || "Sin tipo"}
                  </p>

                  <p>
                    <strong>Técnico:</strong>{" "}
                    {m.tecnico_nombre || m.tecnico || m.tecnico_id || "Sin técnico"}
                  </p>

                  <p>
                    <strong>Estado:</strong>{" "}
                    <span className={`coord-status ${String(m.estado || "").toLowerCase()}`}>
                      {m.estado || "SIN ESTADO"}
                    </span>
                  </p>

                  <p>
                    <Clock size={16} />
                    <strong> Observaciones:</strong>{" "}
                    {m.observaciones || "Sin observaciones"}
                  </p>
                </div>
              </div>
            </article>
          ))
        )}
      </div>
    </div>
  );
}