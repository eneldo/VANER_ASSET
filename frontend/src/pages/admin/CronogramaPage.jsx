// ============================================================
// PÁGINA: Cronograma PRO Admin
// Archivo: frontend/src/pages/admin/CronogramaPage.jsx
// Fase 28 - SGA PRO
// ============================================================
// Objetivo:
//   Visualizar la agenda de mantenimientos programados.
//   Incluye filtros, KPIs, timeline y calendario simple.
// ============================================================

import { useEffect, useMemo, useState } from "react";
import { CalendarDays, Filter, RefreshCw, Wrench } from "lucide-react";
import API from "../../api/axios";
import "../../styles/cronograma.css";

const ESTADOS = ["", "PROGRAMADO", "ASIGNADO", "EN_PROCESO", "PAUSADO", "FINALIZADO", "ANULADO"];

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

export default function CronogramaPage() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(false);
  const [resumen, setResumen] = useState(null);

  const [filtros, setFiltros] = useState({
    fecha_inicio: fechaLocalISO(),
    fecha_fin: sumarDias(30),
    empresa_id: "",
    sede_id: "",
    tecnico_id: "",
    estado: "",
    tipo: "",
  });

  const cargarCronograma = async () => {
    setLoading(true);
    try {
      const params = Object.fromEntries(
        Object.entries(filtros).filter(([, value]) => value !== "" && value !== null)
      );

      const [cronogramaRes, resumenRes] = await Promise.all([
        API.get("/cronograma/admin", { params }),
        API.get("/cronograma/resumen"),
      ]);

      setItems(cronogramaRes.data?.items || []);
      setResumen(resumenRes.data || null);
    } catch (error) {
      console.error("Error cargando cronograma:", error);
      alert("No fue posible cargar el cronograma. Revisa backend y consola.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    cargarCronograma();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const kpis = useMemo(() => {
    const vencidos = items.filter((i) => i.vencido).length;
    const finalizados = items.filter((i) => i.estado === "FINALIZADO").length;
    const programados = items.filter((i) => i.estado === "PROGRAMADO").length;

    return {
      total: items.length,
      vencidos: resumen?.vencidos ?? vencidos,
      pendientes: resumen?.pendientes_30_dias ?? programados,
      finalizados: resumen?.finalizados_30_dias ?? finalizados,
    };
  }, [items, resumen]);

  const diasCalendario = useMemo(() => {
    const inicio = new Date(`${filtros.fecha_inicio}T00:00:00`);
    return Array.from({ length: 28 }, (_, index) => {
      const d = new Date(inicio);
      d.setDate(d.getDate() + index);
      const iso = fechaLocalISO(d);
      return {
        iso,
        label: d.toLocaleDateString("es-CO", { day: "2-digit", month: "short" }),
        eventos: items.filter((item) => item.fecha_programada === iso),
      };
    });
  }, [items, filtros.fecha_inicio]);

  const cambiarFiltro = (campo, valor) => {
    setFiltros((prev) => ({ ...prev, [campo]: valor }));
  };

  return (
    <div className="cronograma-page">
      <header className="cronograma-header">
        <div>
          <p className="cronograma-eyebrow">FASE 28 · CRONOGRAMA PRO</p>
          <h1>Cronograma inteligente de mantenimientos</h1>
          <span>Agenda operativa por fechas, estados, empresa, sede, técnico y tipo de mantenimiento.</span>
        </div>

        <div className="cronograma-actions">
          <button className="cronograma-btn secondary" onClick={cargarCronograma} disabled={loading}>
            <RefreshCw size={17} />
            {loading ? "Cargando..." : "Actualizar"}
          </button>
        </div>
      </header>

      <section className="cronograma-kpis">
        <article className="cronograma-kpi"><span>Total en rango</span><strong>{kpis.total}</strong></article>
        <article className="cronograma-kpi"><span>Pendientes 30 días</span><strong>{kpis.pendientes}</strong></article>
        <article className="cronograma-kpi"><span>Vencidos</span><strong>{kpis.vencidos}</strong></article>
        <article className="cronograma-kpi"><span>Finalizados</span><strong>{kpis.finalizados}</strong></article>
      </section>

      <section className="cronograma-panel">
        <div className="cronograma-section-title">
          <h2><Filter size={18} /> Filtros del cronograma</h2>
          <span>Para empresa/sede/técnico puedes pegar el ID cuando necesites filtrar exacto.</span>
        </div>

        <div className="cronograma-filtros">
          <div className="cronograma-field"><label>Desde</label><input type="date" value={filtros.fecha_inicio} onChange={(e) => cambiarFiltro("fecha_inicio", e.target.value)} /></div>
          <div className="cronograma-field"><label>Hasta</label><input type="date" value={filtros.fecha_fin} onChange={(e) => cambiarFiltro("fecha_fin", e.target.value)} /></div>
          <div className="cronograma-field"><label>Estado</label><select value={filtros.estado} onChange={(e) => cambiarFiltro("estado", e.target.value)}>{ESTADOS.map((e) => <option key={e} value={e}>{e || "Todos"}</option>)}</select></div>
          <div className="cronograma-field"><label>Tipo</label><input placeholder="Preventivo, correctivo..." value={filtros.tipo} onChange={(e) => cambiarFiltro("tipo", e.target.value)} /></div>
          <div className="cronograma-field"><label>Empresa ID</label><input placeholder="Opcional" value={filtros.empresa_id} onChange={(e) => cambiarFiltro("empresa_id", e.target.value)} /></div>
          <div className="cronograma-field"><label>Sede ID</label><input placeholder="Opcional" value={filtros.sede_id} onChange={(e) => cambiarFiltro("sede_id", e.target.value)} /></div>
        </div>

        <div className="cronograma-actions" style={{ marginTop: 14 }}>
          <button className="cronograma-btn" onClick={cargarCronograma}><CalendarDays size={17} /> Aplicar filtros</button>
        </div>
      </section>

      <section className="cronograma-body">
        <div className="cronograma-lista">
          <div className="cronograma-section-title"><h2><Wrench size={18} /> Línea de tiempo</h2><span>{items.length} registros</span></div>
          <div className="cronograma-scroll">
            {items.length === 0 ? <div className="cronograma-empty">No hay mantenimientos programados en el rango seleccionado.</div> : items.map((item) => (
              <article className="cronograma-item" key={item.id}>
                <div className="cronograma-item-top">
                  <div>
                    <h3>{item.title}</h3>
                    <p>{item.empresa_nombre || "Sin empresa"} · {item.sede_nombre || "Sin sede"}</p>
                  </div>
                  <span className={`estado-chip ${estadoClass(item)}`}>{item.vencido ? "VENCIDO" : item.estado}</span>
                </div>
                <div className="cronograma-meta">
                  <span className="cronograma-chip">📅 {item.fecha_programada || "Sin fecha"}</span>
                  <span className="cronograma-chip">🏷️ {item.tipo || "N/A"}</span>
                  <span className="cronograma-chip">🔧 {item.tecnico_nombre || "Sin técnico"}</span>
                  <span className="cronograma-chip">📍 {item.equipo_ubicacion || "Sin ubicación"}</span>
                </div>
                {item.descripcion && <p>{item.descripcion}</p>}
              </article>
            ))}
          </div>
        </div>

        <div className="cronograma-calendario">
          <div className="cronograma-section-title"><h2><CalendarDays size={18} /> Vista calendario</h2><span>28 días desde fecha inicial</span></div>
          <div className="cronograma-grid-dias">
            {diasCalendario.map((dia) => (
              <div className="cronograma-dia" key={dia.iso}>
                <strong>{dia.label}</strong>
                {dia.eventos.slice(0, 3).map((ev) => <span className="cronograma-dot" key={ev.id}>{ev.equipo_nombre || ev.tipo}</span>)}
                {dia.eventos.length > 3 && <span className="cronograma-chip">+{dia.eventos.length - 3}</span>}
              </div>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
}
