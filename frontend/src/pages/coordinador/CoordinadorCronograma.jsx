/*
===========================================================
COORDINADOR — CRONOGRAMA PRO
Archivo: frontend/src/pages/coordinador/CoordinadorCronograma.jsx
===========================================================
*/

import React, { useEffect, useMemo, useState } from "react";
import API from "../../api/axios";
import { CalendarDays, RefreshCw, Search } from "lucide-react";
import "../../styles/coordinador.css";

const fmtFechaLarga = (fecha) => {
  if (!fecha) return "Sin fecha programada";
  try {
    return new Date(fecha).toLocaleDateString("es-CO", {
      weekday: "long",
      year: "numeric",
      month: "long",
      day: "2-digit",
    });
  } catch {
    return "Sin fecha programada";
  }
};

export default function CoordinadorCronograma() {
  const [mantenimientos, setMantenimientos] = useState([]);
  const [busqueda, setBusqueda] = useState("");
  const [estado, setEstado] = useState("");
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    cargarCronograma();
  }, []);

  const cargarCronograma = async () => {
    try {
      setCargando(true);
      setError("");
      const res = await API.get("/coordinador/cronograma");
      setMantenimientos(res.data || []);
    } catch (err) {
      console.error("Error cargando cronograma:", err);
      setError("No se pudo cargar el cronograma.");
    } finally {
      setCargando(false);
    }
  };

  const filtrados = useMemo(() => {
    const texto = busqueda.toLowerCase();
    return mantenimientos.filter((m) => {
      const coincideTexto = `${m.equipo_nombre || ""} ${m.tecnico_nombre || ""} ${m.tipo || ""} ${m.estado || ""}`
        .toLowerCase()
        .includes(texto);
      const coincideEstado = estado ? m.estado === estado : true;
      return coincideTexto && coincideEstado;
    });
  }, [mantenimientos, busqueda, estado]);

  const agrupados = useMemo(() => {
    return filtrados.reduce((acc, m) => {
      const key = m.fecha_programada ? String(m.fecha_programada).split("T")[0] : "Sin fecha";
      if (!acc[key]) acc[key] = [];
      acc[key].push(m);
      return acc;
    }, {});
  }, [filtrados]);

  return (
    <div className="coord-page">
      <div className="coord-hero">
        <div>
          <span className="coord-eyebrow">PLANEACIÓN · CRONOGRAMA</span>
          <h2>Cronograma de Mantenimientos</h2>
          <p>Vista operativa por fecha, equipo, técnico y estado.</p>
        </div>

        <button className="coord-btn secondary" onClick={cargarCronograma}>
          <RefreshCw size={17} />
          Actualizar
        </button>
      </div>

      {error && <div className="coord-alert error">{error}</div>}

      <div className="coord-filters">
        <div className="coord-search">
          <Search size={18} />
          <input
            placeholder="Buscar por equipo, técnico, tipo o estado..."
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
        {Object.keys(agrupados).length === 0 ? (
          <section className="coord-card">
            <p className="coord-empty">{cargando ? "Cargando cronograma..." : "No hay mantenimientos programados."}</p>
          </section>
        ) : (
          Object.entries(agrupados).map(([fecha, items]) => (
            <section className="coord-card" key={fecha}>
              <div className="coord-card-header">
                <div>
                  <h3>{fecha === "Sin fecha" ? "Sin fecha programada" : fmtFechaLarga(fecha)}</h3>
                  <p>{items.length} mantenimiento(s)</p>
                </div>
                <CalendarDays size={22} />
              </div>

              <div className="coord-timeline-list">
                {items.map((m) => (
                  <div className="coord-timeline-item" key={m.id}>
                    <div className="coord-timeline-dot" />
                    <div>
                      <strong>{m.equipo_nombre || "Sin equipo"}</strong>
                      <span>{m.tecnico_nombre || "Sin técnico"} · {m.tipo || "N/A"}</span>
                    </div>
                    <span className={`coord-badge ${String(m.estado || "").toLowerCase()}`}>{m.estado || "N/A"}</span>
                  </div>
                ))}
              </div>
            </section>
          ))
        )}
      </div>
    </div>
  );
}
