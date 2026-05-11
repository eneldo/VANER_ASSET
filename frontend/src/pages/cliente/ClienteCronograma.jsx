// ============================================================
// PÁGINA: Cronograma Cliente / Empresa
// Archivo: frontend/src/pages/cliente/ClienteCronograma.jsx
// Fase 28 - SGA PRO
// ============================================================
// Objetivo:
//   Permitir que la empresa cliente vea únicamente el cronograma
//   de mantenimientos de sus propios equipos.
// ============================================================

import { useEffect, useMemo, useState } from "react";
import { CalendarDays, RefreshCw, Wrench } from "lucide-react";
import API from "../../api/axios";
import { getEmpresaId } from "./ClienteLayout";
import "../../styles/cronograma.css";

function fechaLocalISO(date = new Date()) {
  return date.toISOString().slice(0, 10);
}

function sumarDias(dias) {
  const d = new Date();
  d.setDate(d.getDate() + dias);
  return fechaLocalISO(d);
}

function estadoClass(item) {
  if (item.vencido) return "vencido";
  if (item.estado === "FINALIZADO") return "finalizado";
  if (item.estado === "ANULADO") return "anulado";
  if (item.estado === "EN_PROCESO") return "proceso";
  if (item.estado === "ASIGNADO") return "asignado";
  return "";
}

export default function ClienteCronograma() {
  const empresaId = getEmpresaId();
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(false);
  const [filtros, setFiltros] = useState({
    fecha_inicio: fechaLocalISO(),
    fecha_fin: sumarDias(30),
    estado: "",
    tipo: "",
  });

  const cargarCronograma = async () => {
    if (!empresaId) {
      alert("No se encontró empresa_id en el usuario cliente. Revisa el login o localStorage.user.");
      return;
    }

    setLoading(true);
    try {
      const params = Object.fromEntries(Object.entries(filtros).filter(([, v]) => v));
      const res = await API.get(`/cronograma/cliente/${empresaId}`, { params });
      setItems(res.data?.items || []);
    } catch (error) {
      console.error("Error cargando cronograma cliente:", error);
      alert("No fue posible cargar el cronograma del cliente.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    cargarCronograma();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const kpis = useMemo(() => ({
    total: items.length,
    vencidos: items.filter((i) => i.vencido).length,
    pendientes: items.filter((i) => !["FINALIZADO", "ANULADO"].includes(i.estado)).length,
    finalizados: items.filter((i) => i.estado === "FINALIZADO").length,
  }), [items]);

  const cambiarFiltro = (campo, valor) => setFiltros((prev) => ({ ...prev, [campo]: valor }));

  return (
    <div className="cronograma-page">
      <header className="cronograma-header">
        <div>
          <p className="cronograma-eyebrow">PORTAL EMPRESA · FASE 28</p>
          <h1>Cronograma de mantenimientos</h1>
          <span>Consulta los mantenimientos programados, vencidos y finalizados de tus equipos.</span>
        </div>

        <button className="cronograma-btn secondary" onClick={cargarCronograma} disabled={loading}>
          <RefreshCw size={17} /> {loading ? "Cargando..." : "Actualizar"}
        </button>
      </header>

      <section className="cronograma-kpis">
        <article className="cronograma-kpi"><span>Total</span><strong>{kpis.total}</strong></article>
        <article className="cronograma-kpi"><span>Pendientes</span><strong>{kpis.pendientes}</strong></article>
        <article className="cronograma-kpi"><span>Vencidos</span><strong>{kpis.vencidos}</strong></article>
        <article className="cronograma-kpi"><span>Finalizados</span><strong>{kpis.finalizados}</strong></article>
      </section>

      <section className="cronograma-panel">
        <div className="cronograma-filtros">
          <div className="cronograma-field"><label>Desde</label><input type="date" value={filtros.fecha_inicio} onChange={(e) => cambiarFiltro("fecha_inicio", e.target.value)} /></div>
          <div className="cronograma-field"><label>Hasta</label><input type="date" value={filtros.fecha_fin} onChange={(e) => cambiarFiltro("fecha_fin", e.target.value)} /></div>
          <div className="cronograma-field"><label>Estado</label><select value={filtros.estado} onChange={(e) => cambiarFiltro("estado", e.target.value)}><option value="">Todos</option><option>PROGRAMADO</option><option>ASIGNADO</option><option>EN_PROCESO</option><option>PAUSADO</option><option>FINALIZADO</option><option>ANULADO</option></select></div>
          <div className="cronograma-field"><label>Tipo</label><input placeholder="Preventivo, correctivo..." value={filtros.tipo} onChange={(e) => cambiarFiltro("tipo", e.target.value)} /></div>
        </div>
        <div className="cronograma-actions" style={{ marginTop: 14 }}><button className="cronograma-btn" onClick={cargarCronograma}><CalendarDays size={17} /> Aplicar filtros</button></div>
      </section>

      <section className="cronograma-lista">
        <div className="cronograma-section-title"><h2><Wrench size={18} /> Próximos mantenimientos</h2><span>{items.length} registros</span></div>
        <div className="cronograma-scroll">
          {items.length === 0 ? <div className="cronograma-empty">No hay mantenimientos programados para el rango seleccionado.</div> : items.map((item) => (
            <article className="cronograma-item" key={item.id}>
              <div className="cronograma-item-top">
                <div><h3>{item.equipo_nombre || item.title}</h3><p>{item.sede_nombre || "Sin sede"} · {item.equipo_ubicacion || "Sin ubicación"}</p></div>
                <span className={`estado-chip ${estadoClass(item)}`}>{item.vencido ? "VENCIDO" : item.estado}</span>
              </div>
              <div className="cronograma-meta">
                <span className="cronograma-chip">📅 {item.fecha_programada}</span>
                <span className="cronograma-chip">🏷️ {item.tipo}</span>
                <span className="cronograma-chip">🔧 {item.tecnico_nombre || "Por asignar"}</span>
                <span className="cronograma-chip"># {item.equipo_codigo || "Sin código"}</span>
              </div>
              {item.descripcion && <p>{item.descripcion}</p>}
            </article>
          ))}
        </div>
      </section>
    </div>
  );
}
