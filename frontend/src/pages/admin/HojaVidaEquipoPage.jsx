// =========================================================
// PÁGINA ADMIN - HOJA DE VIDA TÉCNICA DEL EQUIPO
// Paso 2: Registro histórico, técnico y apoyo técnico
//
// CAMBIOS REALIZADOS:
// - Se corrige manejo de errores para no mostrar [object Object].
// - Se convierten fechas vacías "" a null antes de guardar.
// - Se convierte costo vacío a null y costo digitado a número.
// - Se mantiene carga automática de datos básicos del equipo.
// - Se deja listo para crear o actualizar la hoja de vida.
// =========================================================

import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import AdminLayout from "./AdminLayout";
import API from "../../api/axios";
import { FileText, Save, ArrowLeft, Printer } from "lucide-react";
import "../../styles/sidebar.css";

export default function HojaVidaEquipoPage() {
  const { equipoId } = useParams();
  const navigate = useNavigate();

  const [cargando, setCargando] = useState(true);
  const [existeHoja, setExisteHoja] = useState(false);
  const [encabezado, setEncabezado] = useState({});
  const [equipo, setEquipo] = useState({});

  const [form, setForm] = useState({
    equipo_id: equipoId,

    adquisicion: "",
    costo: "",
    fecha_compra: "",
    fecha_instalacion: "",
    proveedor: "",
    pais_fabricacion: "",
    fecha_fabricacion: "",
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

    clase_diagnostico: false,
    clase_prevencion: false,
    clase_rehabilitacion: false,
    clase_analisis: false,

    riesgo_bajo: false,
    riesgo_moderado: false,
    riesgo_alto: false,
    riesgo_elevado: false,
  });

  useEffect(() => {
    cargarHojaVida();
  }, [equipoId]);

  // =======================================================
  // MOSTRAR ERRORES LEGIBLES
  // Evita alertas tipo [object Object]
  // =======================================================
  const obtenerMensajeError = (error) => {
    const detail = error.response?.data?.detail;

    if (Array.isArray(detail)) {
      return detail
        .map((e) => {
          const campo = Array.isArray(e.loc) ? e.loc.join(".") : "campo";
          return `${campo}: ${e.msg}`;
        })
        .join("\n");
    }

    if (typeof detail === "string") {
      return detail;
    }

    if (detail && typeof detail === "object") {
      return JSON.stringify(detail, null, 2);
    }

    return "Error inesperado. Revisa consola y backend.";
  };

  // =======================================================
  // CARGAR HOJA DE VIDA + DATOS BÁSICOS DEL EQUIPO
  // =======================================================
  const cargarHojaVida = async () => {
    try {
      setCargando(true);

      const res = await API.get(
        `/equipo-hoja-vida/equipo/${equipoId}/completa`
      );

      setEncabezado(res.data.encabezado || {});
      setEquipo(res.data.equipo_basico || {});

      const hoja = res.data.hoja_vida_tecnica;

      if (hoja) {
        setExisteHoja(true);

        setForm({
          equipo_id: equipoId,

          adquisicion: hoja.adquisicion || "",
          costo: hoja.costo || "",
          fecha_compra: hoja.fecha_compra || "",
          fecha_instalacion: hoja.fecha_instalacion || "",
          proveedor: hoja.proveedor || "",
          pais_fabricacion: hoja.pais_fabricacion || "",
          fecha_fabricacion: hoja.fecha_fabricacion || "",
          vida_util: hoja.vida_util || "",
          requiere_calibracion: hoja.requiere_calibracion || false,

          rango_voltaje: hoja.rango_voltaje || "",
          rango_presion: hoja.rango_presion || "",
          gas_refrigerante: hoja.gas_refrigerante || "",
          capacidad: hoja.capacidad || "",
          rango_corriente: hoja.rango_corriente || "",
          rango_velocidad: hoja.rango_velocidad || "",
          rango_potencia: hoja.rango_potencia || "",
          rango_temperatura: hoja.rango_temperatura || "",
          frecuencia: hoja.frecuencia || "",
          rango_humedad: hoja.rango_humedad || "",
          otros: hoja.otros || "",

          manual_operacion: hoja.manual_operacion || false,
          manual_mantenimiento: hoja.manual_mantenimiento || false,
          manual_partes: hoja.manual_partes || false,
          manual_despiece: hoja.manual_despiece || false,

          plano_electronico: hoja.plano_electronico || false,
          plano_electrico: hoja.plano_electrico || false,
          plano_neumatico: hoja.plano_neumatico || false,
          plano_mecanico: hoja.plano_mecanico || false,

          clase_diagnostico: hoja.clase_diagnostico || false,
          clase_prevencion: hoja.clase_prevencion || false,
          clase_rehabilitacion: hoja.clase_rehabilitacion || false,
          clase_analisis: hoja.clase_analisis || false,

          riesgo_bajo: hoja.riesgo_bajo || false,
          riesgo_moderado: hoja.riesgo_moderado || false,
          riesgo_alto: hoja.riesgo_alto || false,
          riesgo_elevado: hoja.riesgo_elevado || false,
        });
      } else {
        setExisteHoja(false);
      }
    } catch (error) {
      console.error("ERROR CARGANDO HOJA DE VIDA:", error.response?.data || error);
      alert("Error cargando hoja de vida:\n" + obtenerMensajeError(error));
    } finally {
      setCargando(false);
    }
  };

  // =======================================================
  // MANEJO DEL FORMULARIO
  // =======================================================
  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;

    setForm({
      ...form,
      [name]: type === "checkbox" ? checked : value,
    });
  };

  // =======================================================
  // PREPARAR PAYLOAD PARA BACKEND
  // Convierte valores vacíos a null cuando aplica.
  // =======================================================
  const prepararPayload = () => {
    const payload = { ...form };

    const camposFecha = [
      "fecha_compra",
      "fecha_instalacion",
      "fecha_fabricacion",
    ];

    camposFecha.forEach((campo) => {
      if (payload[campo] === "") {
        payload[campo] = null;
      }
    });

    if (payload.costo === "" || payload.costo === null) {
      payload.costo = null;
    } else {
      payload.costo = Number(payload.costo);
    }

    return payload;
  };

  // =======================================================
  // GUARDAR O ACTUALIZAR HOJA DE VIDA
  // =======================================================
  const guardarHojaVida = async (e) => {
    e.preventDefault();

    try {
      const payload = prepararPayload();

      if (existeHoja) {
        await API.put(`/equipo-hoja-vida/equipo/${equipoId}`, payload);
        alert("Hoja de vida actualizada correctamente");
      } else {
        await API.post("/equipo-hoja-vida/", payload);
        alert("Hoja de vida creada correctamente");
        setExisteHoja(true);
      }

      await cargarHojaVida();
    } catch (error) {
      console.error("ERROR GUARDANDO HOJA DE VIDA:", error.response?.data || error);
      alert("Error guardando hoja de vida:\n" + obtenerMensajeError(error));
    }
  };

  if (cargando) {
    return (
      <AdminLayout>
        <p>Cargando hoja de vida...</p>
      </AdminLayout>
    );
  }

  return (
    <AdminLayout>
      <div className="page-header no-print">
        <div className="page-icon">
          <FileText size={26} />
        </div>

        <div>
          <h1>Hoja de Vida Técnica</h1>
          <p>Completa el paso 2 de la hoja de vida del equipo.</p>
        </div>
      </div>

      <div className="hoja-actions no-print">
        <button
          type="button"
          className="btn-secondary"
          onClick={() => navigate("/admin/equipos")}
        >
          <ArrowLeft size={17} />
          Volver
        </button>

        <button
          type="button"
          className="btn-secondary"
          onClick={() => window.print()}
        >
          <Printer size={17} />
          Imprimir
        </button>

        <button type="button" className="btn-primary" onClick={guardarHojaVida}>
          <Save size={17} />
          Guardar hoja de vida
        </button>
      </div>

      <form onSubmit={guardarHojaVida} className="hoja-documento">
        {/* ===================================================
            ENCABEZADO DOCUMENTAL
            =================================================== */}
        <section className="hoja-header">
          <div className="hoja-logo-box">
            {encabezado?.empresa_logo_url ? (
              <img
                src={`http://127.0.0.1:8000${encabezado.empresa_logo_url}`}
                alt="Logo empresa"
              />
            ) : (
              <div className="hoja-logo-placeholder">LOGO</div>
            )}
          </div>

          <div className="hoja-title">
            <h2>HOJA DE VIDA EQUIPO HOSPITALARIO</h2>
            <p>{encabezado?.empresa_nombre || "Empresa cliente"}</p>
            <p>{encabezado?.sede_nombre || "Sede"}</p>
          </div>

          <div className="hoja-code">
            <strong>{equipo?.inventario || equipo?.codigo_id || "N/A"}</strong>
            <span>Inventario / Código</span>
          </div>
        </section>

        {/* ===================================================
            DATOS BÁSICOS DEL EQUIPO
            =================================================== */}
        <section className="hoja-section">
          <h3>DATOS DEL EQUIPO</h3>

          <div className="hoja-grid-4">
            <Info label="Equipo" value={equipo?.nombre} />
            <Info label="Marca" value={equipo?.marca} />
            <Info label="Modelo" value={equipo?.modelo} />
            <Info label="Serie" value={equipo?.serie} />
            <Info label="Ubicación" value={equipo?.ubicacion} />
            <Info label="INVIMA" value={equipo?.invima} />
            <Info label="Código ID" value={equipo?.codigo_id} />
            <Info label="Inventario" value={equipo?.inventario} />
            <Info label="Estado" value={equipo?.estado} />
            <Info label="Criticidad" value={equipo?.criticidad} />
            <Info label="Categoría" value={equipo?.categoria} />
          </div>
        </section>

        {/* ===================================================
            REGISTRO HISTÓRICO
            =================================================== */}
        <section className="hoja-section">
          <h3>REGISTRO HISTÓRICO</h3>

          <div className="crud-form hoja-form">
            <Input label="Adquisición" name="adquisicion" value={form.adquisicion} onChange={handleChange} />
            <Input label="Costo" name="costo" type="number" value={form.costo} onChange={handleChange} />
            <Input label="Fecha compra" name="fecha_compra" type="date" value={form.fecha_compra} onChange={handleChange} />
            <Input label="Fecha instalación" name="fecha_instalacion" type="date" value={form.fecha_instalacion} onChange={handleChange} />
            <Input label="Proveedor" name="proveedor" value={form.proveedor} onChange={handleChange} />
            <Input label="País fabricación" name="pais_fabricacion" value={form.pais_fabricacion} onChange={handleChange} />
            <Input label="Fecha fabricación" name="fecha_fabricacion" type="date" value={form.fecha_fabricacion} onChange={handleChange} />
            <Input label="Vida útil" name="vida_util" value={form.vida_util} onChange={handleChange} />

            <label className="checkbox-line">
              <input
                type="checkbox"
                name="requiere_calibracion"
                checked={form.requiere_calibracion}
                onChange={handleChange}
              />
              Requiere calibración
            </label>
          </div>
        </section>

        {/* ===================================================
            REGISTRO TÉCNICO
            =================================================== */}
        <section className="hoja-section">
          <h3>REGISTRO TÉCNICO DE FUNCIONAMIENTO</h3>

          <div className="crud-form hoja-form">
            <Input label="Rango voltaje" name="rango_voltaje" value={form.rango_voltaje} onChange={handleChange} />
            <Input label="Rango presión" name="rango_presion" value={form.rango_presion} onChange={handleChange} />
            <Input label="Gas refrigerante" name="gas_refrigerante" value={form.gas_refrigerante} onChange={handleChange} />
            <Input label="Capacidad" name="capacidad" value={form.capacidad} onChange={handleChange} />
            <Input label="Rango corriente" name="rango_corriente" value={form.rango_corriente} onChange={handleChange} />
            <Input label="Rango velocidad" name="rango_velocidad" value={form.rango_velocidad} onChange={handleChange} />
            <Input label="Rango potencia" name="rango_potencia" value={form.rango_potencia} onChange={handleChange} />
            <Input label="Rango temperatura" name="rango_temperatura" value={form.rango_temperatura} onChange={handleChange} />
            <Input label="Frecuencia" name="frecuencia" value={form.frecuencia} onChange={handleChange} />
            <Input label="Rango humedad" name="rango_humedad" value={form.rango_humedad} onChange={handleChange} />

            <div className="form-group full">
              <label>Otros</label>
              <textarea
                name="otros"
                value={form.otros}
                onChange={handleChange}
                placeholder="Aquí ingresaremos otros datos que no estén en los campos anteriores"
              />
            </div>
          </div>
        </section>

        {/* ===================================================
            APOYO TÉCNICO
            =================================================== */}
        <section className="hoja-section">
          <h3>REGISTRO DE APOYO TÉCNICO</h3>

          <div className="check-grid">
            <CheckGroup title="Manuales">
              <Check label="Operación" name="manual_operacion" checked={form.manual_operacion} onChange={handleChange} />
              <Check label="Mantenimiento" name="manual_mantenimiento" checked={form.manual_mantenimiento} onChange={handleChange} />
              <Check label="Partes" name="manual_partes" checked={form.manual_partes} onChange={handleChange} />
              <Check label="Despiece" name="manual_despiece" checked={form.manual_despiece} onChange={handleChange} />
            </CheckGroup>

            <CheckGroup title="Planos">
              <Check label="Electrónico" name="plano_electronico" checked={form.plano_electronico} onChange={handleChange} />
              <Check label="Eléctrico" name="plano_electrico" checked={form.plano_electrico} onChange={handleChange} />
              <Check label="Neumático" name="plano_neumatico" checked={form.plano_neumatico} onChange={handleChange} />
              <Check label="Mecánico" name="plano_mecanico" checked={form.plano_mecanico} onChange={handleChange} />
            </CheckGroup>

            <CheckGroup title="Clasif. Biomédica">
              <Check label="Diagnóstico" name="clase_diagnostico" checked={form.clase_diagnostico} onChange={handleChange} />
              <Check label="Prevención" name="clase_prevencion" checked={form.clase_prevencion} onChange={handleChange} />
              <Check label="Rehabilitación" name="clase_rehabilitacion" checked={form.clase_rehabilitacion} onChange={handleChange} />
              <Check label="Análisis Lab." name="clase_analisis" checked={form.clase_analisis} onChange={handleChange} />
            </CheckGroup>

            <CheckGroup title="Clasif. Riesgo">
              <Check label="Bajo (I)" name="riesgo_bajo" checked={form.riesgo_bajo} onChange={handleChange} />
              <Check label="Moderado (IIA)" name="riesgo_moderado" checked={form.riesgo_moderado} onChange={handleChange} />
              <Check label="Alto (IIB)" name="riesgo_alto" checked={form.riesgo_alto} onChange={handleChange} />
              <Check label="Elevado (III)" name="riesgo_elevado" checked={form.riesgo_elevado} onChange={handleChange} />
            </CheckGroup>
          </div>
        </section>
      </form>
    </AdminLayout>
  );
}

// =========================================================
// COMPONENTES AUXILIARES
// =========================================================

function Info({ label, value }) {
  return (
    <div className="info-cell">
      <span>{label}</span>
      <strong>{value || "N/A"}</strong>
    </div>
  );
}

function Input({ label, name, value, onChange, type = "text" }) {
  return (
    <div className="form-group">
      <label>{label}</label>
      <input name={name} type={type} value={value || ""} onChange={onChange} />
    </div>
  );
}

function CheckGroup({ title, children }) {
  return (
    <div className="check-group">
      <h4>{title}</h4>
      {children}
    </div>
  );
}

function Check({ label, name, checked, onChange }) {
  return (
    <label className="check-item">
      <input type="checkbox" name={name} checked={checked} onChange={onChange} />
      {label}
    </label>
  );
}