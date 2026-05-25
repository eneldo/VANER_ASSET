/*
===========================================================
COORDINADOR — HOJA DE VIDA DE EQUIPOS PRO
Archivo: frontend/src/pages/coordinador/CoordinadorHojaVida.jsx
===========================================================
*/

import React, { useEffect, useMemo, useState } from "react";
import API from "../../api/axios";
import { FileText, RefreshCw, Search, Save, Printer } from "lucide-react";
import { useParams } from "react-router-dom";
import "../../styles/coordinador.css";

const hojaInicial = {
  adquisicion: "",
  costo: "",
  proveedor: "",
  pais_fabricacion: "",
  vida_util: "",
  requiere_calibracion: false,
  rango_voltaje: "",
  rango_presion: "",
  gas_refrigerante: "",
  capacidad: "",
  rango_corriente: "",
  rango_velocidad: "",
  rango_potencia: "",
  rango_temperatura: "",
  frecuencia: "",
  rango_humedad: "",
  otros: "",
  manual_operacion: false,
  manual_mantenimiento: false,
  manual_partes: false,
  manual_despiece: false,
  plano_electronico: false,
  plano_electrico: false,
  plano_neumatico: false,
  plano_mecanico: false,
  riesgo_bajo: false,
  riesgo_moderado: false,
  riesgo_alto: false,
  riesgo_elevado: false,
};

export default function CoordinadorHojaVida() {
  const { equipoId: equipoIdUrl } = useParams();

  const [equipos, setEquipos] = useState([]);
  const [equipoId, setEquipoId] = useState(equipoIdUrl || "");
  const [detalle, setDetalle] = useState(null);
  const [hojaVida, setHojaVida] = useState(hojaInicial);
  const [busqueda, setBusqueda] = useState("");
  const [cargando, setCargando] = useState(true);
  const [guardando, setGuardando] = useState(false);
  const [mensaje, setMensaje] = useState(null);

  useEffect(() => {
    cargarEquipos();
  }, []);

  useEffect(() => {
    if (equipoId) cargarHojaVida(equipoId);
  }, [equipoId]);

  const mostrarMensaje = (tipo, texto) => {
    setMensaje({ tipo, texto });
    setTimeout(() => setMensaje(null), 3500);
  };

  const cargarEquipos = async () => {
    try {
      setCargando(true);
      const res = await API.get("/coordinador/equipos");
      setEquipos(res.data || []);
      if (!equipoIdUrl && !equipoId && res.data?.length) {
        setEquipoId(res.data[0].id);
      }
    } catch (error) {
      console.error("Error cargando equipos:", error);
      mostrarMensaje("error", "No se pudieron cargar los equipos.");
    } finally {
      setCargando(false);
    }
  };

  const cargarHojaVida = async (id) => {
    try {
      setCargando(true);
      const res = await API.get(`/coordinador/equipos/${id}/hoja-vida`);
      setDetalle(res.data || null);
      setHojaVida({ ...hojaInicial, ...(res.data?.hoja_vida_tecnica || {}) });
    } catch (error) {
      console.error("Error cargando hoja vida:", error);
      setDetalle(null);
      setHojaVida(hojaInicial);
      mostrarMensaje("error", "No se pudo cargar la hoja de vida del equipo.");
    } finally {
      setCargando(false);
    }
  };

  const guardar = async () => {
    if (!equipoId) {
      mostrarMensaje("error", "Selecciona un equipo.");
      return;
    }

    try {
      setGuardando(true);
      const payload = { ...hojaVida };

      Object.keys(payload).forEach((k) => {
        if (payload[k] === "") payload[k] = null;
      });

      await API.put(`/coordinador/equipos/${equipoId}/hoja-vida`, payload);
      mostrarMensaje("success", "Hoja de vida guardada correctamente.");
      await cargarHojaVida(equipoId);
    } catch (error) {
      console.error("Error guardando hoja vida:", error);
      mostrarMensaje("error", error?.response?.data?.detail || "No se pudo guardar la hoja de vida.");
    } finally {
      setGuardando(false);
    }
  };

  const equiposFiltrados = useMemo(() => {
    const texto = busqueda.toLowerCase();
    return equipos.filter((e) =>
      `${e.nombre || ""} ${e.marca || ""} ${e.modelo || ""} ${e.serie || ""} ${e.inventario || ""}`
        .toLowerCase()
        .includes(texto)
    );
  }, [equipos, busqueda]);

  const setCampo = (campo, valor) => setHojaVida((prev) => ({ ...prev, [campo]: valor }));

  const imprimir = () => window.print();

  const equipo = detalle?.equipo_basico;

  return (
    <div className="coord-page">
      <div className="coord-hero">
        <div>
          <span className="coord-eyebrow">INVENTARIO · HOJA DE VIDA</span>
          <h2>Hoja de Vida Técnica</h2>
          <p>Consulta y actualización de datos técnicos por equipo.</p>
        </div>

        <div className="coord-actions">
          <button className="coord-btn secondary" onClick={imprimir}>
            <Printer size={17} />
            Imprimir
          </button>
          <button className="coord-btn secondary" onClick={() => equipoId && cargarHojaVida(equipoId)}>
            <RefreshCw size={17} />
            Actualizar
          </button>
          <button className="coord-btn primary" onClick={guardar} disabled={guardando || !equipoId}>
            <Save size={17} />
            Guardar
          </button>
        </div>
      </div>

      {mensaje && <div className={`coord-alert ${mensaje.tipo}`}>{mensaje.texto}</div>}

      <div className="coord-grid sidebar-content">
        <section className="coord-card">
          <div className="coord-card-header">
            <div>
              <h3>Equipos</h3>
              <p>Selecciona un equipo para consultar su hoja de vida.</p>
            </div>
            <Search size={21} />
          </div>

          <div className="coord-search">
            <Search size={18} />
            <input placeholder="Buscar equipo..." value={busqueda} onChange={(e) => setBusqueda(e.target.value)} />
          </div>

          <div className="coord-list">
            {equiposFiltrados.map((e) => (
              <button
                key={e.id}
                className={String(e.id) === String(equipoId) ? "active" : ""}
                onClick={() => setEquipoId(e.id)}
              >
                <strong>{e.nombre}</strong>
                <span>{e.marca || "Sin marca"} · {e.serie || "Sin serie"}</span>
              </button>
            ))}
          </div>
        </section>

        <section className="coord-card">
          <div id="hoja-vida-print">
            <div className="coord-card-header">
              <div>
                <h3>{equipo?.nombre || "Seleccione un equipo"}</h3>
                <p>
                  {detalle?.encabezado?.empresa_nombre || "Empresa"} · {detalle?.encabezado?.sede_nombre || "Sede"}
                </p>
              </div>
              <FileText size={24} />
            </div>

            {equipo ? (
              <>
                <div className="coord-detail-grid">
                  <div><span>Marca</span><strong>{equipo.marca || "N/A"}</strong></div>
                  <div><span>Modelo</span><strong>{equipo.modelo || "N/A"}</strong></div>
                  <div><span>Serie</span><strong>{equipo.serie || "N/A"}</strong></div>
                  <div><span>Inventario</span><strong>{equipo.inventario || equipo.codigo_inventario || "N/A"}</strong></div>
                  <div><span>Ubicación</span><strong>{equipo.ubicacion || "N/A"}</strong></div>
                  <div><span>Estado</span><strong>{equipo.estado || "N/A"}</strong></div>
                </div>

                <div className="coord-form-grid">
                  <label>
                    Adquisición
                    <input value={hojaVida.adquisicion || ""} onChange={(e) => setCampo("adquisicion", e.target.value)} />
                  </label>
                  <label>
                    Costo
                    <input type="number" value={hojaVida.costo || ""} onChange={(e) => setCampo("costo", e.target.value)} />
                  </label>
                  <label>
                    Proveedor
                    <input value={hojaVida.proveedor || ""} onChange={(e) => setCampo("proveedor", e.target.value)} />
                  </label>
                  <label>
                    País fabricación
                    <input value={hojaVida.pais_fabricacion || ""} onChange={(e) => setCampo("pais_fabricacion", e.target.value)} />
                  </label>
                  <label>
                    Vida útil
                    <input value={hojaVida.vida_util || ""} onChange={(e) => setCampo("vida_util", e.target.value)} />
                  </label>
                  <label>
                    Capacidad
                    <input value={hojaVida.capacidad || ""} onChange={(e) => setCampo("capacidad", e.target.value)} />
                  </label>
                  <label>
                    Voltaje
                    <input value={hojaVida.rango_voltaje || ""} onChange={(e) => setCampo("rango_voltaje", e.target.value)} />
                  </label>
                  <label>
                    Corriente
                    <input value={hojaVida.rango_corriente || ""} onChange={(e) => setCampo("rango_corriente", e.target.value)} />
                  </label>
                  <label>
                    Potencia
                    <input value={hojaVida.rango_potencia || ""} onChange={(e) => setCampo("rango_potencia", e.target.value)} />
                  </label>
                  <label>
                    Temperatura
                    <input value={hojaVida.rango_temperatura || ""} onChange={(e) => setCampo("rango_temperatura", e.target.value)} />
                  </label>
                  <label>
                    Frecuencia
                    <input value={hojaVida.frecuencia || ""} onChange={(e) => setCampo("frecuencia", e.target.value)} />
                  </label>
                  <label>
                    Humedad
                    <input value={hojaVida.rango_humedad || ""} onChange={(e) => setCampo("rango_humedad", e.target.value)} />
                  </label>

                  <label className="coord-check">
                    <input type="checkbox" checked={!!hojaVida.requiere_calibracion} onChange={(e) => setCampo("requiere_calibracion", e.target.checked)} />
                    Requiere calibración
                  </label>
                  <label className="coord-check">
                    <input type="checkbox" checked={!!hojaVida.manual_operacion} onChange={(e) => setCampo("manual_operacion", e.target.checked)} />
                    Manual operación
                  </label>
                  <label className="coord-check">
                    <input type="checkbox" checked={!!hojaVida.manual_mantenimiento} onChange={(e) => setCampo("manual_mantenimiento", e.target.checked)} />
                    Manual mantenimiento
                  </label>
                  <label className="coord-check">
                    <input type="checkbox" checked={!!hojaVida.riesgo_alto} onChange={(e) => setCampo("riesgo_alto", e.target.checked)} />
                    Riesgo alto
                  </label>

                  <label className="span-2">
                    Otros datos técnicos
                    <textarea rows="4" value={hojaVida.otros || ""} onChange={(e) => setCampo("otros", e.target.value)} />
                  </label>
                </div>
              </>
            ) : (
              <p className="coord-empty">Seleccione un equipo para visualizar la hoja de vida.</p>
            )}
          </div>
        </section>
      </div>
    </div>
  );
}
