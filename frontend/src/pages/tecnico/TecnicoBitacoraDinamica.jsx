// ============================================================
// PÁGINA: BITÁCORA DINÁMICA TÉCNICO PRO
// Archivo: frontend/src/pages/tecnico/TecnicoBitacoraDinamica.jsx
// ============================================================
// Carga automáticamente el formato correcto según el equipo del mantenimiento.
// ============================================================

import React, { useEffect, useMemo, useState, useContext } from "react";
import { useNavigate, useParams } from "react-router-dom";
import {
  ArrowLeft,
  Save,
  ClipboardCheck,
  Wrench,
  Building2,
  MapPin,
  Cpu,
  History,
  FileText,
} from "lucide-react";

import { AuthContext } from "../../context/AuthContext";
import formatosDinamicosApi from "../../api/formatosDinamicosApi";
import FormatoDinamicoRenderer from "../../components/FormatoDinamicoRenderer";
import "../../styles/bitacoraDinamica.css";

export default function TecnicoBitacoraDinamica() {
  const { mantenimientoId } = useParams();
  const navigate = useNavigate();
  const { user } = useContext(AuthContext);

  const [loading, setLoading] = useState(true);
  const [guardando, setGuardando] = useState(false);
  const [error, setError] = useState("");
  const [contexto, setContexto] = useState(null);
  const [respuestas, setRespuestas] = useState({});
  const [form, setForm] = useState({
    estado_inicial: "",
    estado_final: "OPERATIVO",
    observaciones: "",
    recomendaciones: "",
    repuestos_utilizados: "",
  });

  useEffect(() => {
    cargarContexto();
  }, [mantenimientoId]);

  const cargarContexto = async () => {
    setLoading(true);
    setError("");

    try {
      const res = await formatosDinamicosApi.obtenerBitacoraMantenimiento(mantenimientoId);
      const data = res.data;
      setContexto(data);

      const bitacora = data.bitacora;
      if (bitacora) {
        setForm({
          estado_inicial: bitacora.estado_inicial || data.mantenimiento?.estado_inicial || "",
          estado_final: bitacora.estado_final || "OPERATIVO",
          observaciones: bitacora.observaciones || "",
          recomendaciones: bitacora.recomendaciones || "",
          repuestos_utilizados: bitacora.repuestos_utilizados || "",
        });

        const previas = {};
        (bitacora.respuestas || []).forEach((r) => {
          if (r.campo_id) {
            previas[r.campo_id] = {
              valor: r.valor || "",
              observacion: r.observacion || "",
            };
          }
        });
        setRespuestas(previas);
      } else {
        setForm((prev) => ({
          ...prev,
          estado_inicial: data.mantenimiento?.estado_inicial || "",
        }));
      }
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.detail || "No se pudo cargar la bitácora dinámica.");
    } finally {
      setLoading(false);
    }
  };

  const progreso = useMemo(() => {
    const campos = contexto?.formato?.campos || [];
    if (!campos.length) return 0;
    const diligenciados = campos.filter((c) => {
      const r = respuestas[c.id];
      return r && String(r.valor || "").trim() !== "";
    }).length;
    return Math.round((diligenciados / campos.length) * 100);
  }, [contexto, respuestas]);

  const actualizarRespuesta = (campoId, data) => {
    setRespuestas((prev) => ({ ...prev, [campoId]: data }));
  };

  const guardar = async () => {
    if (!contexto?.formato?.id) {
      alert("No hay formato asociado.");
      return;
    }

    setGuardando(true);

    try {
      const payload = {
        mantenimiento_id: mantenimientoId,
        tecnico_id: user?.tecnico_id || contexto.mantenimiento?.tecnico_id || null,
        formato_id: contexto.formato.id,
        ...form,
        respuestas: Object.entries(respuestas).map(([campo_id, r]) => ({
          campo_id,
          valor: r.valor || "",
          observacion: r.observacion || "",
        })),
      };

      await formatosDinamicosApi.guardarBitacora(payload);
      alert("Bitácora dinámica guardada correctamente.");
      await cargarContexto();
    } catch (err) {
      console.error(err);
      alert(err.response?.data?.detail || "Error guardando la bitácora.");
    } finally {
      setGuardando(false);
    }
  };

  if (loading) {
    return <div className="bd-loading">Cargando bitácora dinámica PRO...</div>;
  }

  if (error) {
    return (
      <div className="bd-page">
        <div className="bd-error-card">
          <h2>No se pudo cargar</h2>
          <p>{error}</p>
          <button onClick={() => navigate(-1)}>Volver</button>
        </div>
      </div>
    );
  }

  const { mantenimiento, equipo, formato } = contexto;

  return (
    <div className="bd-page">
      <header className="bd-hero">
        <button className="bd-back" onClick={() => navigate(-1)}>
          <ArrowLeft size={18} /> Volver
        </button>

        <div className="bd-hero-main">
          <div className="bd-icon-wrap">
            <ClipboardCheck size={34} />
          </div>
          <div>
            <h1>Bitácora dinámica de mantenimiento</h1>
            <p>Formato cargado automáticamente según el tipo de equipo.</p>
          </div>
        </div>

        <div className="bd-actions">
          <button className="bd-btn secondary" onClick={() => window.print()}>
            <FileText size={17} /> PDF / Imprimir
          </button>
          <button className="bd-btn primary" onClick={guardar} disabled={guardando}>
            <Save size={17} /> {guardando ? "Guardando..." : "Guardar bitácora"}
          </button>
        </div>
      </header>

      <section className="bd-summary-grid">
        <article className="bd-summary-card">
          <span><Cpu size={16} /> Equipo</span>
          <strong>{equipo?.nombre || "Equipo"}</strong>
          <small>{equipo?.marca || "Sin marca"} · {equipo?.modelo || "Sin modelo"}</small>
          <small>Inventario: {equipo?.inventario || equipo?.codigo_id || "N/A"}</small>
        </article>

        <article className="bd-summary-card">
          <span><Wrench size={16} /> Formato aplicado</span>
          <strong>{formato?.nombre}</strong>
          <small>Código: {formato?.codigo}</small>
          <small>{formato?.campos?.length || 0} campos técnicos</small>
        </article>

        <article className="bd-summary-card">
          <span><Building2 size={16} /> Mantenimiento</span>
          <strong>{mantenimiento?.tipo}</strong>
          <small>Estado actual: {mantenimiento?.estado}</small>
          <small>OT: {mantenimiento?.id}</small>
        </article>

        <article className="bd-summary-card progress">
          <span><History size={16} /> Avance</span>
          <strong>{progreso}%</strong>
          <div className="bd-progress"><i style={{ width: `${progreso}%` }} /></div>
          <small>Diligenciamiento del checklist</small>
        </article>
      </section>

      <section className="bd-common-card">
        <div className="bd-section-title">
          <h3>Información técnica general</h3>
          <span>Datos comunes</span>
        </div>

        <div className="bd-common-grid">
          <label>
            Estado inicial
            <input
              value={form.estado_inicial}
              onChange={(e) => setForm({ ...form, estado_inicial: e.target.value })}
              placeholder="Ej: Operativo, fuera de servicio, intermitente"
            />
          </label>

          <label>
            Estado final
            <select
              value={form.estado_final}
              onChange={(e) => setForm({ ...form, estado_final: e.target.value })}
            >
              <option value="OPERATIVO">Operativo</option>
              <option value="OPERATIVO_CON_OBSERVACIONES">Operativo con observaciones</option>
              <option value="PENDIENTE_REPUESTO">Pendiente repuesto</option>
              <option value="FUERA_DE_SERVICIO">Fuera de servicio</option>
              <option value="REQUIERE_CAMBIO">Requiere cambio</option>
              <option value="REQUIERE_INTERVENCION_MAYOR">Requiere intervención mayor</option>
            </select>
          </label>

          <label>
            Repuestos utilizados
            <textarea
              value={form.repuestos_utilizados}
              onChange={(e) => setForm({ ...form, repuestos_utilizados: e.target.value })}
              placeholder="Código, descripción, cantidad, serial..."
            />
          </label>

          <label>
            Recomendaciones técnicas
            <textarea
              value={form.recomendaciones}
              onChange={(e) => setForm({ ...form, recomendaciones: e.target.value })}
              placeholder="Recomendaciones para el próximo mantenimiento..."
            />
          </label>
        </div>

        <label className="bd-full-label">
          Observaciones generales
          <textarea
            value={form.observaciones}
            onChange={(e) => setForm({ ...form, observaciones: e.target.value })}
            placeholder="Describe hallazgos, condiciones del equipo y resultado final..."
          />
        </label>
      </section>

      <FormatoDinamicoRenderer
        campos={formato?.campos || []}
        respuestas={respuestas}
        onChange={actualizarRespuesta}
      />

      <footer className="bd-footer-actions">
        <button className="bd-btn secondary" onClick={() => navigate(-1)}>
          Cancelar
        </button>
        <button className="bd-btn primary" onClick={guardar} disabled={guardando}>
          <Save size={17} /> {guardando ? "Guardando..." : "Guardar bitácora"}
        </button>
      </footer>
    </div>
  );
}
