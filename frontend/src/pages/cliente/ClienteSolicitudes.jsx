import { useEffect, useMemo, useState } from "react";
import { AlertTriangle, RefreshCcw, Send } from "lucide-react";

import API from "../../api/axios";
import { isNetworkError, queueOfflineRequest } from "../../utils/offlineQueue";
import { getEmpresaId } from "../../utils/multiempresa";

const FORM_INICIAL = {
  sede_id: "",
  equipo_id: "",
  titulo: "",
  descripcion: "",
  prioridad: "EMERGENCIA",
  contacto_nombre: "",
  contacto_telefono: "",
};

export default function ClienteSolicitudes() {
  const [form, setForm] = useState(FORM_INICIAL);
  const [sedes, setSedes] = useState([]);
  const [equipos, setEquipos] = useState([]);
  const [solicitudes, setSolicitudes] = useState([]);
  const [guardando, setGuardando] = useState(false);
  const [loading, setLoading] = useState(false);

  const equiposSede = useMemo(
    () => equipos.filter((equipo) => String(equipo.sede_id) === String(form.sede_id)),
    [equipos, form.sede_id]
  );

  const cargar = async () => {
    const empresaId = getEmpresaId();
    if (!empresaId) return;
    setLoading(true);
    try {
      const [sedesRes, equiposRes, solicitudesRes] = await Promise.all([
        API.get(`/cliente/${empresaId}/sedes`),
        API.get(`/cliente/${empresaId}/equipos`),
        API.get("/solicitudes-correctivas/"),
      ]);
      setSedes(sedesRes.data || []);
      setEquipos(equiposRes.data || []);
      setSolicitudes(solicitudesRes.data || []);
    } catch (error) {
      if (!isNetworkError(error)) console.error("No fue posible cargar las solicitudes", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const timeout = window.setTimeout(cargar, 0);
    return () => window.clearTimeout(timeout);
  }, []);

  const actualizar = (campo, valor) => {
    setForm((prev) => ({ ...prev, [campo]: valor, ...(campo === "sede_id" ? { equipo_id: "" } : {}) }));
  };

  const enviar = async (event) => {
    event.preventDefault();
    if (!form.sede_id || form.titulo.trim().length < 5 || form.descripcion.trim().length < 15) {
      alert("Selecciona una sede y describe la emergencia con suficiente detalle.");
      return;
    }

    const payload = { ...form, equipo_id: form.equipo_id || null };
    const requestId = crypto.randomUUID();
    setGuardando(true);
    try {
      const res = await API.post("/solicitudes-correctivas/", payload, {
        headers: { "X-Idempotency-Key": requestId },
      });
      setSolicitudes((prev) => [res.data, ...prev]);
      setForm(FORM_INICIAL);
      alert("Solicitud de emergencia radicada correctamente.");
    } catch (error) {
      if (isNetworkError(error)) {
        await queueOfflineRequest({ method: "post", url: "/solicitudes-correctivas/", data: payload });
        setSolicitudes((prev) => [{
          ...payload,
          id: `offline-${requestId}`,
          estado: "PENDIENTE_SYNC",
          sede_nombre: sedes.find((s) => String(s.id) === String(payload.sede_id))?.nombre,
          created_at: new Date().toISOString(),
        }, ...prev]);
        setForm(FORM_INICIAL);
        alert("Sin conexión: la solicitud quedó guardada y se enviará automáticamente.");
      } else {
        alert(error.response?.data?.detail || "No fue posible radicar la solicitud.");
      }
    } finally {
      setGuardando(false);
    }
  };

  return (
    <>
      <div className="cliente-header cliente-header-flex">
        <div>
          <h1>Emergencias correctivas</h1>
          <p>Reporta una falla urgente y consulta el estado de atención.</p>
        </div>
        <button className="cliente-btn-secondary" onClick={cargar} disabled={loading}>
          <RefreshCcw size={16} /> Actualizar
        </button>
      </div>

      <div className="cliente-emergency-grid">
        <form className="cliente-panel cliente-emergency-form" onSubmit={enviar}>
          <h2><AlertTriangle size={20} /> Nueva solicitud</h2>
          <label>Sede *</label>
          <select value={form.sede_id} onChange={(e) => actualizar("sede_id", e.target.value)} required>
            <option value="">Seleccionar sede</option>
            {sedes.map((sede) => <option key={sede.id} value={sede.id}>{sede.nombre}</option>)}
          </select>

          <label>Equipo afectado</label>
          <select value={form.equipo_id} onChange={(e) => actualizar("equipo_id", e.target.value)}>
            <option value="">No identificado / área general</option>
            {equiposSede.map((equipo) => <option key={equipo.id} value={equipo.id}>{equipo.nombre}</option>)}
          </select>

          <label>Asunto *</label>
          <input value={form.titulo} maxLength={160} onChange={(e) => actualizar("titulo", e.target.value)} placeholder="Ej. Aire acondicionado detenido" required />

          <label>Descripción de la emergencia *</label>
          <textarea value={form.descripcion} maxLength={4000} onChange={(e) => actualizar("descripcion", e.target.value)} placeholder="Indica qué ocurrió, desde cuándo y el impacto operativo." required />

          <div className="cliente-emergency-row">
            <div><label>Contacto</label><input value={form.contacto_nombre} onChange={(e) => actualizar("contacto_nombre", e.target.value)} /></div>
            <div><label>Teléfono</label><input value={form.contacto_telefono} onChange={(e) => actualizar("contacto_telefono", e.target.value)} /></div>
          </div>

          <button className="cliente-btn cliente-emergency-submit" disabled={guardando}>
            <Send size={16} /> {guardando ? "Enviando…" : "Radicar emergencia"}
          </button>
        </form>

        <section className="cliente-panel">
          <h2>Solicitudes radicadas</h2>
          <div className="cliente-emergency-list">
            {solicitudes.length === 0 && <p>No hay solicitudes registradas.</p>}
            {solicitudes.map((item) => (
              <article key={item.id}>
                <div><strong>{item.titulo}</strong><span className={`cliente-status ${estadoClase(item.estado)}`}>{item.estado}</span></div>
                <p>{item.descripcion}</p>
                <small>{item.sede_nombre || "Sede"} · {formatearFecha(item.created_at)}</small>
                {item.respuesta_coordinador && <blockquote>{item.respuesta_coordinador}</blockquote>}
              </article>
            ))}
          </div>
        </section>
      </div>
    </>
  );
}

function estadoClase(estado) {
  if (["CERRADA", "CONVERTIDA_OT"].includes(estado)) return "ok";
  if (["EN_REVISION", "APROBADA"].includes(estado)) return "progress";
  return "pending";
}

function formatearFecha(fecha) {
  if (!fecha) return "Pendiente de sincronización";
  return new Date(fecha).toLocaleString();
}
