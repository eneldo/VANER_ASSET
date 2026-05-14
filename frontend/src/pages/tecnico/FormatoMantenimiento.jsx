// ============================================================
// PÁGINA: FormatoMantenimiento
// Archivo: frontend/src/pages/tecnico/FormatoMantenimiento.jsx
// Descripción:
// Formulario técnico para diligenciar mantenimiento preventivo/correctivo.
// ============================================================

import React, { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import "../../styles/formatoMantenimiento.css";

const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

export default function FormatoMantenimiento() {
  const { mantenimientoId } = useParams();
  const navigate = useNavigate();

  const [formatoId, setFormatoId] = useState(null);
  const [guardando, setGuardando] = useState(false);

  const [form, setForm] = useState({
    mantenimiento_id: Number(mantenimientoId),
    tecnico_id: null,
    fecha: "",
    numero_ot: "",
    numero_inventario: "",
    ubicacion: "",
    mantenimiento_tipo: "Preventivo",
    tecnico_nombre: "",
    tecnico_auxiliar: "",
    tipo_equipo: "",
    trabajos_realizados: {
      lavado_panel_condensador: false,
      limpieza_control_electrico: false,
      inspeccion_transmision: false,
      limpieza_bandeja_drenaje: false,
      lubricacion_rodamientos: false,
      inspeccion_bomba: false,
      limpieza_rejillas: false,
      lavado_filtros_aire: false,
      inspeccion_carga_refrigerante: false,
      lavado_panel_evaporacion: false,
      otro: "",
    },
    datos_funcionamiento: {
      compresor_1_l1: "",
      compresor_1_l2: "",
      compresor_1_l3: "",
      compresor_2_l1: "",
      compresor_2_l2: "",
      compresor_2_l3: "",
      ventilador_condensadora_1_l1: "",
      ventilador_condensadora_1_l2: "",
      ventilador_condensadora_1_l3: "",
      ventilador_condensadora_2_l1: "",
      ventilador_condensadora_2_l2: "",
      ventilador_condensadora_2_l3: "",
      ventilador_condensadora_3_l1: "",
      ventilador_condensadora_3_l2: "",
      ventilador_condensadora_3_l3: "",
      ventilador_condensadora_4_l1: "",
      ventilador_condensadora_4_l2: "",
      ventilador_condensadora_4_l3: "",
      blower_1_l1: "",
      blower_1_l2: "",
      blower_1_l3: "",
      blower_2_l1: "",
      blower_2_l2: "",
      blower_2_l3: "",
      presion_alta_etapa_1: "",
      presion_alta_etapa_2: "",
      presion_baja_etapa_1: "",
      presion_baja_etapa_2: "",
    },
    repuestos_utilizados: [
      { cantidad: "", descripcion: "" },
      { cantidad: "", descripcion: "" },
      { cantidad: "", descripcion: "" },
      { cantidad: "", descripcion: "" },
    ],
    observaciones: "",
    firma_usuario: "",
    firma_operario: "",
    firma_coordinador: "",
  });

  useEffect(() => {
    cargarFormatoExistente();
  }, [mantenimientoId]);

  const cargarFormatoExistente = async () => {
    try {
      const res = await fetch(`${API_URL}/formatos-mantenimiento/mantenimiento/${mantenimientoId}`);

      if (!res.ok) return;

      const data = await res.json();
      setFormatoId(data.id);

      setForm({
        ...form,
        ...data,
        fecha: data.fecha || "",
        trabajos_realizados: data.trabajos_realizados || form.trabajos_realizados,
        datos_funcionamiento: data.datos_funcionamiento || form.datos_funcionamiento,
        repuestos_utilizados: data.repuestos_utilizados?.length
          ? data.repuestos_utilizados
          : form.repuestos_utilizados,
      });
    } catch (error) {
      console.log("No existe formato previo.");
    }
  };

  const actualizarCampo = (campo, valor) => {
    setForm((prev) => ({
      ...prev,
      [campo]: valor,
    }));
  };

  const actualizarTrabajo = (campo, valor) => {
    setForm((prev) => ({
      ...prev,
      trabajos_realizados: {
        ...prev.trabajos_realizados,
        [campo]: valor,
      },
    }));
  };

  const actualizarDato = (campo, valor) => {
    setForm((prev) => ({
      ...prev,
      datos_funcionamiento: {
        ...prev.datos_funcionamiento,
        [campo]: valor,
      },
    }));
  };

  const actualizarRepuesto = (index, campo, valor) => {
    const copia = [...form.repuestos_utilizados];
    copia[index][campo] = valor;

    setForm((prev) => ({
      ...prev,
      repuestos_utilizados: copia,
    }));
  };

  const agregarRepuesto = () => {
    setForm((prev) => ({
      ...prev,
      repuestos_utilizados: [
        ...prev.repuestos_utilizados,
        { cantidad: "", descripcion: "" },
      ],
    }));
  };

  const guardarFormato = async () => {
    setGuardando(true);

    try {
      const url = formatoId
        ? `${API_URL}/formatos-mantenimiento/${formatoId}`
        : `${API_URL}/formatos-mantenimiento/`;

      const method = formatoId ? "PUT" : "POST";

      const res = await fetch(url, {
        method,
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          ...form,
          mantenimiento_id: Number(mantenimientoId),
        }),
      });

      if (!res.ok) {
        const error = await res.json();
        alert(error.detail || "No se pudo guardar el formato.");
        return;
      }

      const data = await res.json();
      setFormatoId(data.id);
      alert("Formato guardado correctamente.");
    } catch (error) {
      console.error(error);
      alert("Error guardando el formato.");
    } finally {
      setGuardando(false);
    }
  };

  const guardarEImprimir = async () => {
    await guardarFormato();

    setTimeout(() => {
      if (formatoId) {
        navigate(`/tecnico/formato-mantenimiento/${mantenimientoId}/imprimir`);
      } else {
        navigate(`/tecnico/formato-mantenimiento/${mantenimientoId}/imprimir`);
      }
    }, 500);
  };

  return (
    <div className="formato-page">
      <div className="formato-topbar no-print">
        <div>
          <h1>Formato de Mantenimiento</h1>
          <p>Diligenciamiento técnico preventivo / correctivo</p>
        </div>

        <div className="formato-actions">
          <button onClick={() => navigate(-1)} className="btn-secundario">
            Volver
          </button>
          <button onClick={guardarFormato} className="btn-principal" disabled={guardando}>
            {guardando ? "Guardando..." : "Guardar"}
          </button>
          <button onClick={guardarEImprimir} className="btn-imprimir">
            Imprimir / PDF
          </button>
        </div>
      </div>

      <div className="formato-hoja">
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

        <div className="grid-form tres">
          <label>
            Fecha
            <input
              type="date"
              value={form.fecha}
              onChange={(e) => actualizarCampo("fecha", e.target.value)}
            />
          </label>

          <label>
            Mantenimiento
            <select
              value={form.mantenimiento_tipo}
              onChange={(e) => actualizarCampo("mantenimiento_tipo", e.target.value)}
            >
              <option value="Preventivo">Preventivo</option>
              <option value="Correctivo">Correctivo</option>
            </select>
          </label>

          <label>
            O.T. No.
            <input
              value={form.numero_ot}
              onChange={(e) => actualizarCampo("numero_ot", e.target.value)}
            />
          </label>
        </div>

        <div className="grid-form dos">
          <label>
            N° Inventario
            <input
              value={form.numero_inventario}
              onChange={(e) => actualizarCampo("numero_inventario", e.target.value)}
            />
          </label>

          <label>
            Ubicación
            <input
              value={form.ubicacion}
              onChange={(e) => actualizarCampo("ubicacion", e.target.value)}
            />
          </label>
        </div>

        <div className="grid-form dos">
          <label>
            Técnico
            <input
              value={form.tecnico_nombre}
              onChange={(e) => actualizarCampo("tecnico_nombre", e.target.value)}
            />
          </label>

          <label>
            Técnico auxiliar
            <input
              value={form.tecnico_auxiliar}
              onChange={(e) => actualizarCampo("tecnico_auxiliar", e.target.value)}
            />
          </label>
        </div>

        <h3>Tipo de equipo a revisar</h3>

        <div className="tipo-equipos">
          {["Aire Ventana", "Aire MiniSplit", "Aire Piso Techo", "Aire Central", "Aire Cassette", "Ctral. Chiller"].map(
            (tipo) => (
              <label key={tipo}>
                <input
                  type="radio"
                  name="tipo_equipo"
                  checked={form.tipo_equipo === tipo}
                  onChange={() => actualizarCampo("tipo_equipo", tipo)}
                />
                {tipo}
              </label>
            )
          )}
        </div>

        <h3>Trabajos realizados</h3>

        <div className="trabajos-grid">
          <label>
            Lavado de Panel Condensador
            <input
              type="checkbox"
              checked={form.trabajos_realizados.lavado_panel_condensador}
              onChange={(e) => actualizarTrabajo("lavado_panel_condensador", e.target.checked)}
            />
          </label>

          <label>
            Inspección de Bomba
            <input
              type="checkbox"
              checked={form.trabajos_realizados.inspeccion_bomba}
              onChange={(e) => actualizarTrabajo("inspeccion_bomba", e.target.checked)}
            />
          </label>

          <label>
            Limpieza de Control Eléctrico
            <input
              type="checkbox"
              checked={form.trabajos_realizados.limpieza_control_electrico}
              onChange={(e) => actualizarTrabajo("limpieza_control_electrico", e.target.checked)}
            />
          </label>

          <label>
            Limpieza de Rejillas
            <input
              type="checkbox"
              checked={form.trabajos_realizados.limpieza_rejillas}
              onChange={(e) => actualizarTrabajo("limpieza_rejillas", e.target.checked)}
            />
          </label>

          <label>
            Inspección de Transmisión
            <input
              type="checkbox"
              checked={form.trabajos_realizados.inspeccion_transmision}
              onChange={(e) => actualizarTrabajo("inspeccion_transmision", e.target.checked)}
            />
          </label>

          <label>
            Lavado de Filtros de Aire
            <input
              type="checkbox"
              checked={form.trabajos_realizados.lavado_filtros_aire}
              onChange={(e) => actualizarTrabajo("lavado_filtros_aire", e.target.checked)}
            />
          </label>

          <label>
            Limpieza de Bandeja Drenaje
            <input
              type="checkbox"
              checked={form.trabajos_realizados.limpieza_bandeja_drenaje}
              onChange={(e) => actualizarTrabajo("limpieza_bandeja_drenaje", e.target.checked)}
            />
          </label>

          <label>
            Inspección de Carga Refrigerante
            <input
              type="checkbox"
              checked={form.trabajos_realizados.inspeccion_carga_refrigerante}
              onChange={(e) => actualizarTrabajo("inspeccion_carga_refrigerante", e.target.checked)}
            />
          </label>

          <label>
            Lubricación de Rodamientos
            <input
              type="checkbox"
              checked={form.trabajos_realizados.lubricacion_rodamientos}
              onChange={(e) => actualizarTrabajo("lubricacion_rodamientos", e.target.checked)}
            />
          </label>

          <label>
            Lavado de Panel de Evaporación
            <input
              type="checkbox"
              checked={form.trabajos_realizados.lavado_panel_evaporacion}
              onChange={(e) => actualizarTrabajo("lavado_panel_evaporacion", e.target.checked)}
            />
          </label>
        </div>

        <label className="campo-full">
          Otro
          <textarea
            value={form.trabajos_realizados.otro}
            onChange={(e) => actualizarTrabajo("otro", e.target.value)}
          />
        </label>

        <h3>Datos de funcionamiento del equipo</h3>

        <div className="tabla-funcionamiento">
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
            <div className="func-row" key={key}>
              <span>{label}</span>
              <input placeholder="L1" value={form.datos_funcionamiento[`${key}_l1`] || ""} onChange={(e) => actualizarDato(`${key}_l1`, e.target.value)} />
              <input placeholder="L2" value={form.datos_funcionamiento[`${key}_l2`] || ""} onChange={(e) => actualizarDato(`${key}_l2`, e.target.value)} />
              <input placeholder="L3" value={form.datos_funcionamiento[`${key}_l3`] || ""} onChange={(e) => actualizarDato(`${key}_l3`, e.target.value)} />
            </div>
          ))}

          <div className="presiones">
            <input placeholder="Presión Alta Etapa 1" value={form.datos_funcionamiento.presion_alta_etapa_1} onChange={(e) => actualizarDato("presion_alta_etapa_1", e.target.value)} />
            <input placeholder="Presión Alta Etapa 2" value={form.datos_funcionamiento.presion_alta_etapa_2} onChange={(e) => actualizarDato("presion_alta_etapa_2", e.target.value)} />
            <input placeholder="Presión Baja Etapa 1" value={form.datos_funcionamiento.presion_baja_etapa_1} onChange={(e) => actualizarDato("presion_baja_etapa_1", e.target.value)} />
            <input placeholder="Presión Baja Etapa 2" value={form.datos_funcionamiento.presion_baja_etapa_2} onChange={(e) => actualizarDato("presion_baja_etapa_2", e.target.value)} />
          </div>
        </div>

        <h3>Repuestos utilizados</h3>

        <div className="repuestos">
          {form.repuestos_utilizados.map((rep, index) => (
            <div className="repuesto-row" key={index}>
              <input
                placeholder="Cant"
                value={rep.cantidad}
                onChange={(e) => actualizarRepuesto(index, "cantidad", e.target.value)}
              />
              <input
                placeholder="Descripción del repuesto"
                value={rep.descripcion}
                onChange={(e) => actualizarRepuesto(index, "descripcion", e.target.value)}
              />
            </div>
          ))}
        </div>

        <button type="button" className="btn-agregar no-print" onClick={agregarRepuesto}>
          + Agregar repuesto
        </button>

        <label className="campo-full">
          Observaciones
          <textarea
            value={form.observaciones}
            onChange={(e) => actualizarCampo("observaciones", e.target.value)}
          />
        </label>

        <div className="firmas">
          <label>
            Firma del Usuario
            <input
              value={form.firma_usuario}
              onChange={(e) => actualizarCampo("firma_usuario", e.target.value)}
            />
          </label>

          <label>
            Firma del Operario
            <input
              value={form.firma_operario}
              onChange={(e) => actualizarCampo("firma_operario", e.target.value)}
            />
          </label>

          <label>
            Firma del Coordinador
            <input
              value={form.firma_coordinador}
              onChange={(e) => actualizarCampo("firma_coordinador", e.target.value)}
            />
          </label>
        </div>
      </div>
    </div>
  );
}