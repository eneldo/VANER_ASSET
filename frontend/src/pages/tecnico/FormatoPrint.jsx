// ============================================================
// PÁGINA: FormatoPrint
// Archivo: frontend/src/pages/tecnico/FormatoPrint.jsx
// Descripción:
// Vista imprimible del formato técnico.
// ============================================================

import { useEffect, useEffectEvent, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import "../../styles/formatoMantenimiento.css";

const API_URL = import.meta.env.VITE_API_URL || "/api";

export default function FormatoPrint() {
  const { mantenimientoId } = useParams();
  const navigate = useNavigate();

  const [form, setForm] = useState(null);

  async function cargarFormato() {
    try {
      const token = localStorage.getItem("access_token") || localStorage.getItem("token");
      const res = await fetch(`${API_URL}/formatos-mantenimiento/mantenimiento/${mantenimientoId}`, {
        headers: { Authorization: token ? `Bearer ${token}` : "" },
      });

      if (!res.ok) {
        alert("No se encontró formato para imprimir.");
        navigate(-1);
        return;
      }

      const data = await res.json();
      setForm(data);

      setTimeout(() => {
        window.print();
      }, 600);
    } catch (error) {
      console.error(error);
      alert("Error cargando formato.");
    }
  };

  const cargarFormatoAlCambiarOt = useEffectEvent(() => cargarFormato());

  useEffect(() => {
    const timer = window.setTimeout(() => cargarFormatoAlCambiarOt(), 0);
    return () => window.clearTimeout(timer);
  }, [mantenimientoId]);

  const check = (valor) => (valor ? "☑" : "☐");

  if (!form) {
    return <div className="formato-page">Cargando formato...</div>;
  }

  const t = form.trabajos_realizados || {};
  const d = form.datos_funcionamiento || {};
  const repuestos = form.repuestos_utilizados || [];

  return (
    <div className="formato-page print-mode">
      <div className="formato-topbar no-print">
        <button onClick={() => navigate(-1)} className="btn-secundario">
          Volver
        </button>
        <button onClick={() => window.print()} className="btn-imprimir">
          Imprimir nuevamente
        </button>
      </div>

      <div className="formato-hoja print-hoja">
        <div className="formato-header">
          <div className="formato-logo">
            <strong>SGA</strong>
            <span>CONSTRUCTION</span>
            <small>Maintenance & Services</small>
          </div>

          <div className="formato-title">
            FORMATO DE MANTENIMIENTO PREVENTIVO / CORRECTIVO
            <br />
            DE AIRES ACONDICIONADOS
          </div>

          <div className="formato-code">
            <p>Código: SGA - MAN -019</p>
            <p>Versión: 00</p>
            <p>Emisión: 23/01/24</p>
          </div>
        </div>

        <table className="print-table">
          <tbody>
            <tr>
              <td>Fecha: {form.fecha || ""}</td>
              <td>Mantenimiento: {form.mantenimiento_tipo || ""}</td>
              <td>O.T. No: {form.numero_ot || ""}</td>
            </tr>
            <tr>
              <td>N° Inventario: {form.numero_inventario || ""}</td>
              <td colSpan="2">Ubicación: {form.ubicacion || ""}</td>
            </tr>
            <tr>
              <td>Técnico: {form.tecnico_nombre || ""}</td>
              <td colSpan="2">Técnico Auxiliar: {form.tecnico_auxiliar || ""}</td>
            </tr>
          </tbody>
        </table>

        <h3>TIPO DE EQUIPO A REVISAR</h3>

        <div className="print-options">
          {["Aire Ventana", "Aire MiniSplit", "Aire Piso Techo", "Aire Central", "Aire Cassette", "Ctral. Chiller"].map(
            (tipo) => (
              <span key={tipo}>
                {tipo} {form.tipo_equipo === tipo ? "☑" : "☐"}
              </span>
            )
          )}
        </div>

        <h3>TRABAJOS REALIZADOS</h3>

        <table className="print-table">
          <tbody>
            <tr>
              <td>Lavado de Panel Condensador</td>
              <td>{check(t.lavado_panel_condensador)}</td>
              <td>Inspección de Bomba</td>
              <td>{check(t.inspeccion_bomba)}</td>
            </tr>
            <tr>
              <td>Limpieza de Control Eléctrico</td>
              <td>{check(t.limpieza_control_electrico)}</td>
              <td>Limpieza de Rejillas</td>
              <td>{check(t.limpieza_rejillas)}</td>
            </tr>
            <tr>
              <td>Inspección de Transmisión</td>
              <td>{check(t.inspeccion_transmision)}</td>
              <td>Lavado de Filtros de Aire</td>
              <td>{check(t.lavado_filtros_aire)}</td>
            </tr>
            <tr>
              <td>Limpieza de Bandeja Drenaje</td>
              <td>{check(t.limpieza_bandeja_drenaje)}</td>
              <td>Inspección de Carga Refrigerante</td>
              <td>{check(t.inspeccion_carga_refrigerante)}</td>
            </tr>
            <tr>
              <td>Lubricación de Rodamientos</td>
              <td>{check(t.lubricacion_rodamientos)}</td>
              <td>Lavado de Panel de Evaporación</td>
              <td>{check(t.lavado_panel_evaporacion)}</td>
            </tr>
            <tr>
              <td colSpan="4">OTRO: {t.otro || ""}</td>
            </tr>
          </tbody>
        </table>

        <h3>DATOS DE FUNCIONAMIENTO DEL EQUIPO</h3>

        <table className="print-table">
          <thead>
            <tr>
              <th>Equipo</th>
              <th>L1</th>
              <th>L2</th>
              <th>L3</th>
            </tr>
          </thead>
          <tbody>
            {[
              ["Compresor 1", "compresor_1"],
              ["Compresor 2", "compresor_2"],
              ["Ventilador Condensadora 1", "ventilador_condensadora_1"],
              ["Ventilador Condensadora 2", "ventilador_condensadora_2"],
              ["Ventilador Condensadora 3", "ventilador_condensadora_3"],
              ["Ventilador Condensadora 4", "ventilador_condensadora_4"],
              ["Blower 1", "blower_1"],
              ["Blower 2", "blower_2"],
            ].map(([label, key]) => (
              <tr key={key}>
                <td>{label}</td>
                <td>{d[`${key}_l1`] || ""}</td>
                <td>{d[`${key}_l2`] || ""}</td>
                <td>{d[`${key}_l3`] || ""}</td>
              </tr>
            ))}
            <tr>
              <td>Presión Alta Etapa 1</td>
              <td colSpan="3">{d.presion_alta_etapa_1 || ""}</td>
            </tr>
            <tr>
              <td>Presión Alta Etapa 2</td>
              <td colSpan="3">{d.presion_alta_etapa_2 || ""}</td>
            </tr>
            <tr>
              <td>Presión Baja Etapa 1</td>
              <td colSpan="3">{d.presion_baja_etapa_1 || ""}</td>
            </tr>
            <tr>
              <td>Presión Baja Etapa 2</td>
              <td colSpan="3">{d.presion_baja_etapa_2 || ""}</td>
            </tr>
          </tbody>
        </table>

        <h3>REPUESTOS UTILIZADOS</h3>

        <table className="print-table">
          <thead>
            <tr>
              <th>Cant</th>
              <th>Descripción</th>
            </tr>
          </thead>
          <tbody>
            {repuestos.map((rep, index) => (
              <tr key={index}>
                <td>{rep.cantidad}</td>
                <td>{rep.descripcion}</td>
              </tr>
            ))}
          </tbody>
        </table>

        <div className="print-observaciones">
          <strong>Observaciones:</strong>
          <p>{form.observaciones || ""}</p>
        </div>

        <div className="print-firmas">
          <div>
            {esFirmaImagen(form.firma_usuario) ? <img src={form.firma_usuario} alt="Firma del usuario" /> : <span>Sin firma</span>}
            <strong>Firma del Usuario</strong>
          </div>
          <div>
            {esFirmaImagen(form.firma_operario) ? <img src={form.firma_operario} alt="Firma del operario" /> : <span>Sin firma</span>}
            <strong>Firma del Operario</strong>
          </div>
          <div>
            <span>{form.firma_coordinador || ""}</span>
            <strong>Firma del Coordinador</strong>
          </div>
        </div>
      </div>
    </div>
  );
}

function esFirmaImagen(value) {
  return String(value || "").startsWith("data:image/png;base64,");
}
