// ============================================================
// PÁGINA: Notificaciones Cliente/Empresa
// Archivo: frontend/src/pages/cliente/ClienteNotificaciones.jsx
// Fase 29 - Notificaciones y Alertas PRO
// ============================================================
// Objetivo:
//   Permitir que el cliente/empresa vea sus alertas filtradas por
//   empresa_id, sin exponer notificaciones de otras empresas.
// ============================================================

import { useEffect, useState } from "react";
import { Bell, CheckCircle2, RefreshCw, AlertTriangle } from "lucide-react";
import API from "../../api/axios";
import "./cliente.css";
import "../../styles/notificaciones.css";

function getCurrentUser() {
  try {
    return JSON.parse(localStorage.getItem("user"));
  } catch {
    return null;
  }
}

function getEmpresaId() {
  const user = getCurrentUser();
  return user?.empresa_id || localStorage.getItem("empresa_id") || null;
}

function formatearFecha(valor) {
  if (!valor) return "Sin fecha";
  try {
    return new Date(valor).toLocaleString("es-CO");
  } catch {
    return valor;
  }
}

export default function ClienteNotificaciones() {
  const [notificaciones, setNotificaciones] = useState([]);
  const [resumen, setResumen] = useState({ total: 0, no_leidas: 0, alta: 0, media: 0, baja: 0 });
  const [cargando, setCargando] = useState(false);
  const [mensaje, setMensaje] = useState("");

  const empresaId = getEmpresaId();

  const cargarDatos = async () => {
    if (!empresaId) {
      setMensaje("No se encontró empresa_id en el usuario actual.");
      return;
    }

    setCargando(true);
    setMensaje("");

    try {
      const [listadoResp, resumenResp] = await Promise.all([
        API.get(`/notificaciones/?rol_destino=EMPRESA&empresa_id=${empresaId}&limite=100`),
        API.get(`/notificaciones/resumen?rol_destino=EMPRESA&empresa_id=${empresaId}`),
      ]);

      setNotificaciones(listadoResp.data || []);
      setResumen(resumenResp.data || { total: 0, no_leidas: 0, alta: 0, media: 0, baja: 0 });
    } catch (error) {
      console.error("Error cargando notificaciones cliente", error);
      setMensaje("No fue posible cargar las notificaciones del cliente.");
    } finally {
      setCargando(false);
    }
  };

  useEffect(() => {
    cargarDatos();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const marcarLeida = async (id) => {
    try {
      await API.put(`/notificaciones/${id}/leer`);
      await cargarDatos();
    } catch (error) {
      console.error("Error marcando como leída", error);
      setMensaje("No fue posible marcar como leída.");
    }
  };

  return (
    <div className="cliente-section">
      <div className="cliente-header">
        <div>
          <span className="notificaciones-eyebrow">Centro de alertas</span>
          <h1>Notificaciones</h1>
          <p>Consulta alertas de mantenimientos, equipos y novedades de tu empresa.</p>
        </div>

        <button className="btn-secundario" onClick={cargarDatos} disabled={cargando}>
          <RefreshCw size={17} />
          Actualizar
        </button>
      </div>

      {mensaje && <div className="notificaciones-message">{mensaje}</div>}

      <section className="notificaciones-kpis compactas">
        <article className="noti-kpi">
          <Bell size={20} />
          <div><strong>{resumen.total}</strong><span>Total</span></div>
        </article>
        <article className="noti-kpi pendiente">
          <AlertTriangle size={20} />
          <div><strong>{resumen.no_leidas}</strong><span>No leídas</span></div>
        </article>
        <article className="noti-kpi alta">
          <AlertTriangle size={20} />
          <div><strong>{resumen.alta}</strong><span>Alta prioridad</span></div>
        </article>
      </section>

      <div className="notificaciones-lista cliente-lista">
        {cargando && <div className="notificaciones-empty">Cargando notificaciones...</div>}

        {!cargando && notificaciones.length === 0 && (
          <div className="notificaciones-empty">No hay notificaciones para tu empresa.</div>
        )}

        {!cargando && notificaciones.map((item) => (
          <article key={item.id} className={`notificacion-card ${item.leida ? "leida" : "no-leida"}`}>
            <div className="notificacion-icono"><Bell size={18} /></div>
            <div className="notificacion-body">
              <div className="notificacion-top">
                <div>
                  <h3>{item.titulo}</h3>
                  <p>{item.mensaje || "Sin detalle adicional."}</p>
                </div>
                <span className={`badge-prioridad ${String(item.prioridad).toLowerCase()}`}>{item.prioridad}</span>
              </div>
              <div className="notificacion-meta">
                <span>{item.tipo}</span>
                <span>{formatearFecha(item.creado_en)}</span>
              </div>
            </div>

            {!item.leida && (
              <div className="notificacion-actions">
                <button onClick={() => marcarLeida(item.id)} title="Marcar como leída">
                  <CheckCircle2 size={17} />
                </button>
              </div>
            )}
          </article>
        ))}
      </div>
    </div>
  );
}
