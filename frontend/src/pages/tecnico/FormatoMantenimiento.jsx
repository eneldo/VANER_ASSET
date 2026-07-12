// ============================================================
// PÁGINA: FormatoMantenimiento
// Archivo: frontend/src/pages/tecnico/FormatoMantenimiento.jsx
// Función:
// - Carga la bitácora correcta según el equipo.
// - Aire acondicionado, CCTV, nevera/congelador, bombas,
//   tablero eléctrico, llamado de enfermería, ascensor,
//   e industrial general.
// ============================================================

import { useEffect, useEffectEvent, useMemo, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import "../../styles/formatoMantenimiento.css";
import SignaturePad from "../../components/SignaturePad";
import { isNetworkError, queueOfflineRequest } from "../../utils/offlineQueue";

const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

const TEMPLATES = {
  AIRE_ACONDICIONADO: {
    titulo: "DE AIRES ACONDICIONADOS",
    codigo: "SGA - MAN -019",
    tipos: [
      "Aire Ventana",
      "Aire MiniSplit",
      "Aire Piso Techo",
      "Aire Central",
      "Aire Cassette",
      "Ctral. Chiller",
    ],
    trabajos: [
      ["lavado_panel_condensador", "Lavado de Panel Condensador"],
      ["inspeccion_bomba", "Inspección de Bomba"],
      ["limpieza_control_electrico", "Limpieza de Control Eléctrico"],
      ["limpieza_rejillas", "Limpieza de Rejillas"],
      ["inspeccion_transmision", "Inspección de Transmisión"],
      ["lavado_filtros_aire", "Lavado de Filtros de Aire"],
      ["limpieza_bandeja_drenaje", "Limpieza de Bandeja Drenaje"],
      ["inspeccion_carga_refrigerante", "Inspección de Carga Refrigerante"],
      ["lubricacion_rodamientos", "Lubricación de Rodamientos"],
      ["lavado_panel_evaporacion", "Lavado de Panel de Evaporación"],
      ["revision_ventiladores", "Revisión de Ventiladores"],
      ["revision_compresor", "Revisión de Compresor"],
      ["revision_temperatura", "Revisión de Temperatura"],
      ["revision_presion", "Revisión de Presión"],
      ["revision_fugas", "Revisión de REfrigerante"],
      ["verificar_ventilador", "Verificar funcionamiento de Ventilador"],
      ["prueba_funcionamiento", "Prueba general de funcionamiento"],
    ],
    mediciones: [
      ["compresor_1", "Compresor 1"],
      ["compresor_2", "Compresor 2"],
      ["ventilador_condensadora_1", "Ventilador Condensadora 1"],
      ["ventilador_condensadora_2", "Ventilador Condensadora 2"],
      ["blower_1", "Blower 1"],
      ["blower_2", "Blower 2"],
      
    ],
  },

  CCTV: {
    titulo: "DE CÁMARAS DE SEGURIDAD / CCTV",
    codigo: "SGA - MAN -CCTV",
    tipos: [
      "Cámara IP",
      "Cámara Analógica",
      "Cámara PTZ",
      "DVR",
      "NVR",
      "XDVR",
      "Monitor",
    ],
    trabajos: [
      ["limpieza_fisica_camara", "Limpieza física de cámara"],
      ["limpieza_interna_xdvr", "Limpieza interna del XDVR"],
      ["limpieza_lente", "Limpieza de lente"],
      ["limpieza_ventiladores_xdvr", "Limpieza de ventiladores XDVR"],
      ["verificacion_enfoque", "Verificación de enfoque"],
      ["revision_temperatura_xdvr", "Revisión de temperatura XDVR"],
      ["verificacion_vision_nocturna_ir", "Verificación de visión nocturna IR"],
      ["validacion_discos_duros_xdvr", "Validación de Discos Duros XDVR"],
      ["revision_carcasa_soporte", "Revisión de carcasa y soporte"],
      ["verificacion_almacenamiento", "Verificación de Almacenamiento"],
      ["ajuste_tornilleria", "Ajuste de tornillería"],
      ["revision_grabacion_continua", "Revisión de Grabación Continua"],
      ["revision_cableado_utp_coaxial", "Revisión de cableado UTP / coaxial"],
      ["configuracion_usuarios", "Configuración de Usuarios"],
      ["verificacion_conectores", "Verificación de conectores"],
      ["validacion_red", "Validación de Red"],
      ["medicion_voltaje", "Medición de voltaje"],
      ["verificacion_puertos", "Verificación de Puertos"],
      ["verificacion_poe", "Verificación de PoE"],
      ["backup_configuracion", "Backup de Configuración"],
      ["validacion_transmision_video", "Validación de transmisión de video"],
      ["actualizacion_firmware_xdvr", "Actualización de Firmware"],
      ["verificacion_grabacion", "Verificación de grabación"],
      ["validacion_acceso_movil", "Validación de Acceso Móvil"],
      ["prueba_movimiento_ptz", "Prueba de movimiento PTZ"],
      ["funcionalidad_monitores", "Funcionalidad de los Monitores"],
      ["validacion_acceso_remoto", "Validación de acceso remoto"],
      ["actualizacion_firmware", "Actualización de firmware"],
      ["revision_fuente_alimentacion", "Revisión de fuente de alimentación"],
      ["prueba_grabacion", "Prueba de grabación"],
      ["revision_dvr_nvr", "Revisión DVR/NVR"],
    ],
    mediciones: [
      ["camara_1", "Cámara / Canal 1"],
      ["camara_2", "Cámara / Canal 2"],
      ["camara_3", "Cámara / Canal 3"],
      ["camara_4", "Cámara / Canal 4"],
      ["dvr_nvr_xdvr", "DVR / NVR / XDVR"],
      ["monitor", "Monitor"],
    ],
  },

  REFRIGERACION: {
    titulo: "DE NEVERAS Y CONGELADORES",
    codigo: "SGA - MAN -REF",
    tipos: ["Nevera", "Congelador", "Refrigerador", "Vitrina refrigerada"],
    trabajos: [
      ["limpieza_condensador", "Limpieza de condensador"],
      ["limpieza_evaporador", "Limpieza de evaporador"],
      ["revision_empaques", "Revisión de empaques"],
      ["revision_termostato", "Revisión de termostato"],
      ["revision_temperatura", "Verificación de temperatura"],
      ["revision_compresor", "Revisión de compresor"],
      ["revision_ventiladores", "Revisión de ventiladores"],
      ["revision_drenaje", "Revisión de drenaje"],
      ["revision_gas", "Revisión de carga refrigerante"],
      ["prueba_funcionamiento", "Prueba general de funcionamiento"],
    ],
    mediciones: [
      ["compresor", "Compresor"],
      ["ventilador_evaporador", "Ventilador evaporador"],
      ["ventilador_condensador", "Ventilador condensador"],
      ["temperatura", "Temperatura"],
    ],
  },

  BOMBA_AGUA: {
    titulo: "DE BOMBAS DE AGUA",
    codigo: "SGA - MAN -BOM",
    tipos: ["Bomba centrífuga", "Bomba sumergible", "Bomba presión", "Motobomba"],
    trabajos: [
      ["revision_fugas", "Revisión de fugas"],
      ["revision_sellos", "Revisión de sellos mecánicos"],
      ["revision_rodamientos", "Revisión de rodamientos"],
      ["lubricacion", "Lubricación"],
      ["revision_motor", "Revisión de motor"],
      ["revision_tablero", "Revisión de tablero"],
      ["revision_presion", "Verificación de presión"],
      ["revision_succion", "Revisión de succión"],
      ["revision_descarga", "Revisión de descarga"],
      ["prueba_operacion", "Prueba de operación"],
    ],
    mediciones: [
      ["motor", "Motor"],
      ["bomba", "Bomba"],
      ["presion", "Presión"],
      ["corriente", "Corriente"],
    ],
  },

  TABLERO_ELECTRICO: {
    titulo: "DE TABLEROS ELÉCTRICOS",
    codigo: "SGA - MAN -ELEC",
    tipos: ["Tablero eléctrico", "Breaker", "Transferencia", "Control"],
    trabajos: [
      ["limpieza_interna", "Limpieza interna"],
      ["ajuste_borneras", "Ajuste de borneras"],
      ["revision_breakers", "Revisión de breakers"],
      ["revision_contactores", "Revisión de contactores"],
      ["revision_reles", "Revisión de relés"],
      ["revision_tierra", "Revisión de puesta a tierra"],
      ["medicion_voltaje", "Medición de voltaje"],
      ["medicion_corriente", "Medición de corriente"],
      ["revision_calentamiento", "Inspección de calentamiento"],
      ["rotulado", "Verificación de rotulado"],
    ],
    mediciones: [
      ["entrada", "Entrada"],
      ["salida", "Salida"],
      ["breaker_principal", "Breaker principal"],
      ["tierra", "Tierra"],
    ],
  },

  LLAMADO_ENFERMERIA: {
    titulo: "DE LLAMADO DE ENFERMERÍA",
    codigo: "SGA - MAN -LENF",
    tipos: ["Panel central", "Pulsador", "Luz indicadora", "Módulo habitación"],
    trabajos: [
      ["revision_panel", "Revisión de panel central"],
      ["revision_pulsadores", "Revisión de pulsadores"],
      ["revision_senal_visual", "Revisión de señal visual"],
      ["revision_senal_sonora", "Revisión de señal sonora"],
      ["revision_cableado", "Revisión de cableado"],
      ["limpieza_componentes", "Limpieza de componentes"],
      ["prueba_habitacion", "Prueba por habitación"],
      ["revision_fuente", "Revisión de fuente"],
      ["revision_comunicacion", "Revisión de comunicación"],
      ["prueba_general", "Prueba general del sistema"],
    ],
    mediciones: [
      ["panel", "Panel central"],
      ["habitacion_1", "Habitación / punto 1"],
      ["habitacion_2", "Habitación / punto 2"],
      ["habitacion_3", "Habitación / punto 3"],
    ],
  },

  ASCENSOR: {
    titulo: "DE ASCENSORES",
    codigo: "SGA - MAN -ASC",
    tipos: [
      "Ascensor eléctrico",
      "Ascensor hidráulico",
      "Ascensor camillero",
      "Ascensor de carga",
      "Plataforma elevadora",
    ],
    trabajos: [
      ["lubricacion_rieles", "Lubricación de Rieles"],
      ["ajuste_zapata", "Ajuste Zapata"],
      ["ajuste_guayas", "Ajuste de Guayas"],
      ["verificacion_botonera_cabina", "Verificación Botonera Cabina"],
      ["chequeo_bloqueo_paracaidas", "Chequeo de Bloqueo de paracaídas"],
      ["apertura_cierre_puertas", "Apertura y Cierre de Puertas"],
      ["revision_frenos", "Revisión de Frenos"],
      ["inspeccion_visual_general", "Inspección visual General"],
      ["verificacion_ventilacion", "Verificación Ventilación"],
      ["nivelacion_cabina", "Nivelación Cabina"],
      ["limpieza_general", "Limpieza General"],
      ["verificacion_motor", "Verificación del Motor"],
      ["revision_electrica", "Revisión Eléctrica"],
      ["ajuste_componentes", "Ajuste de Componentes"],
      ["prueba_operacion", "Prueba de Operación"],
    ],
    mediciones: [
      ["motor", "Motor"],
      ["frenos", "Frenos"],
      ["cabina", "Cabina"],
      ["puertas", "Puertas"],
      ["botonera", "Botonera"],
    ],
  },

  INDUSTRIAL_GENERAL: {
    titulo: "DE EQUIPOS INDUSTRIALES",
    codigo: "SGA - MAN -IND",
    tipos: [
      "Planta eléctrica",
      "Red contra incendios",
      "Báscula",
      "Ventilador industrial",
      "Portón eléctrico",
      "Lavadora industrial",
      "Congelador industrial",
      "Equipo industrial",
    ],
    trabajos: [
      ["fugas", "Fugas"],
      ["vidrio_gabinete", "Vidrio Gabinete"],
      ["limpieza_general", "Limpieza General"],
      ["sirena_alarma_contraincendio", "Funcionamiento Sirena Alarma Contraincendio"],
      ["nivel_aceite", "Nivel de Aceite"],
      ["sensor_humo_funcionando", "Sensor de Humo Funcionando"],
      ["cambio_filtros_aire_combustible", "Cambio de Filtros Aire y Combustible"],
      ["sirena_estrobo_luz_sonido", "Sirena con Estrobo Luz y Sonido"],
      ["lubricacion_rodamientos", "Lubricación de Rodamientos"],
      ["estacion_manual_contraincendios", "Estación Manual Contraincendios"],
      ["presion_agua", "Presión de agua"],
      ["cambio_aceite_motor", "Cambio de Aceite Motor"],
      ["fusibles", "Fusibles"],
      ["tablero_transferencia_operando", "Tablero Transferencia Operando"],
      ["breakers", "Breakers"],
      ["ups_operando", "UPS Operando"],
      ["conexion_mangueras", "Conexión de Mangueras"],
      ["banco_baterias_parametros", "Banco de Baterías dentro de Parámetros"],
      ["prueba_caudal", "Prueba de Caudal"],
      ["funcionamiento_lavadora", "Funcionamiento Lavadora"],
      ["prueba_presion", "Prueba de Presión"],
      ["basculas_industriales", "Básculas Industriales"],
      ["porton_electrico", "Portón Eléctrico"],
      ["ventilador_industrial", "Ventilador Industrial"],
      ["rieles_porton_electrico", "Rieles de Portón Eléctrico"],
      ["congelador_industrial", "Congelador Industrial"],
      ["control_remoto_porton", "Funcionamiento Control Remoto Portón Eléctrico"],
      [
        "anclajes_tornillos_bases",
        "Anclajes, tornillos y bases de soporte firmemente ajustados",
      ],
      ["tanque_gasolina", "Tanque de Gasolina"],
      [
        "ausencia_oxido_grietas_chasis",
        "Ausencia de óxido, grietas o deformaciones en el chasis",
      ],
      [
        "niveles_aceite_lubricantes",
        "Estado de los niveles de aceite y lubricantes",
      ],
    ],
    mediciones: [
      ["motor", "Motor"],
      ["control", "Control"],
      ["seguridad", "Sistema de seguridad"],
      ["operacion", "Operación"],
      ["voltaje", "Voltaje"],
      ["presion", "Presión"],
    ],
  },
};

function extraerTextoPlano(valor) {
  if (!valor) return "";

  if (typeof valor === "string" || typeof valor === "number") {
    return String(valor);
  }

  if (Array.isArray(valor)) {
    return valor.map(extraerTextoPlano).join(" ");
  }

  if (typeof valor === "object") {
    return Object.values(valor).map(extraerTextoPlano).join(" ");
  }

  return "";
}

function detectarTemplate(mantenimiento) {
  const texto = extraerTextoPlano(mantenimiento)
    .toLowerCase()
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "");

  console.log("TEXTO DETECTADO PARA BITACORA:", texto);

  if (
    texto.includes("aire") ||
    texto.includes("acondicionado") ||
    texto.includes("minisplit") ||
    texto.includes("mini split") ||
    texto.includes("chiller") ||
    texto.includes("cassette")
  ) {
    return "AIRE_ACONDICIONADO";
  }

  if (
    texto.includes("cctv") ||
    texto.includes("camara") ||
    texto.includes("camara de seguridad") ||
    texto.includes("seguridad") ||
    texto.includes("dvr") ||
    texto.includes("nvr") ||
    texto.includes("xdvr") ||
    texto.includes("sony") ||
    texto.includes("dahua") ||
    texto.includes("hikvision")
  ) {
    return "CCTV";
  }

  if (
    texto.includes("nevera") ||
    texto.includes("congelador") ||
    texto.includes("refrigerador") ||
    texto.includes("refrigeracion") ||
    texto.includes("freezer")
  ) {
    return "REFRIGERACION";
  }

  if (
    texto.includes("bomba") ||
    texto.includes("motobomba") ||
    texto.includes("hidraulica") ||
    texto.includes("agua")
  ) {
    return "BOMBA_AGUA";
  }

  if (
    texto.includes("tablero") ||
    texto.includes("electrico") ||
    texto.includes("breaker") ||
    texto.includes("transferencia")
  ) {
    return "TABLERO_ELECTRICO";
  }

  if (
    texto.includes("llamado") ||
    texto.includes("enfermeria") ||
    texto.includes("habitacion") ||
    texto.includes("panel central")
  ) {
    return "LLAMADO_ENFERMERIA";
  }

  if (
    texto.includes("ascensor") ||
    texto.includes("elevador") ||
    texto.includes("cabina") ||
    texto.includes("paracaidas") ||
    texto.includes("paracaídas")
  ) {
    return "ASCENSOR";
  }

  if (
    texto.includes("ventilador") ||
    texto.includes("industrial") ||
    texto.includes("planta electrica") ||
    texto.includes("planta electrica") ||
    texto.includes("bascula") ||
    texto.includes("bascula") ||
    texto.includes("red contra incendios") ||
    texto.includes("porton") ||
    texto.includes("portón") ||
    texto.includes("lavadora")
  ) {
    return "INDUSTRIAL_GENERAL";
  }

  return "INDUSTRIAL_GENERAL";
}

const formInicial = (mantenimientoId) => ({
  mantenimiento_id: String(mantenimientoId),
  tecnico_id: null,
  fecha: "",
  numero_ot: "",
  numero_inventario: "",
  ubicacion: "",
  mantenimiento_tipo: "Preventivo",
  tecnico_nombre: "",
  tecnico_auxiliar: "",
  tipo_equipo: "",
  trabajos_realizados: {},
  datos_funcionamiento: {},
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

export default function FormatoMantenimiento() {
  const { mantenimientoId } = useParams();
  const navigate = useNavigate();

  const [formatoId, setFormatoId] = useState(null);
  const [guardando, setGuardando] = useState(false);
  const [, setMantenimiento] = useState(null);
  const [templateKey, setTemplateKey] = useState("INDUSTRIAL_GENERAL");
  const [form, setForm] = useState(formInicial(mantenimientoId));

  const template = useMemo(() => TEMPLATES[templateKey], [templateKey]);

  const getHeaders = () => {
    const token = localStorage.getItem("token") || localStorage.getItem("access_token");

    return {
      "Content-Type": "application/json",
      Authorization: token ? `Bearer ${token}` : "",
    };
  };

  async function cargarDetalleMantenimiento() {
    try {
      const res = await fetch(
        `${API_URL}/dashboard-tecnico/mantenimiento/${mantenimientoId}/detalle`,
        { headers: getHeaders() }
      );

      if (!res.ok) return;

      const data = await res.json();
      setMantenimiento(data);

      const detectado = detectarTemplate(data);
      console.log("PLANTILLA SELECCIONADA:", detectado);

      setTemplateKey(detectado);

      setForm((prev) => ({
        ...prev,
        mantenimiento_id: String(mantenimientoId),
        numero_ot: data.numero_ot || data.ot || prev.numero_ot || "",
        numero_inventario:
          data.codigo_inventario ||
          data.codigo ||
          data.serie ||
          data.equipo_codigo ||
          data.codigo_serie ||
          prev.numero_inventario ||
          "",
        ubicacion:
          data.ubicacion ||
          data.area ||
          data.zona ||
          data.sede_nombre ||
          prev.ubicacion ||
          "",
        tecnico_nombre:
          data.tecnico ||
          data.tecnico_nombre ||
          data.nombre_tecnico ||
          prev.tecnico_nombre ||
          "",
        mantenimiento_tipo:
          data.tipo ||
          data.tipo_mantenimiento ||
          prev.mantenimiento_tipo ||
          "Preventivo",
        tipo_equipo:
          data.equipo ||
          data.equipo_nombre ||
          data.nombre_equipo ||
          data.categoria ||
          data.categoria_nombre ||
          prev.tipo_equipo ||
          "",
      }));
    } catch (error) {
      console.error("No se pudo cargar el detalle del mantenimiento:", error);
    }
  };

  async function cargarFormatoExistente() {
    try {
      const res = await fetch(
        `${API_URL}/formatos-mantenimiento/mantenimiento/${mantenimientoId}`,
        { headers: getHeaders() }
      );

      if (!res.ok) return;

      const data = await res.json();
      setFormatoId(data.id);

      const plantillaGuardada = data?.trabajos_realizados?._plantilla;

      if (plantillaGuardada && TEMPLATES[plantillaGuardada]) {
        setTemplateKey(plantillaGuardada);
      }

      setForm((prev) => ({
        ...prev,
        ...data,
        mantenimiento_id: String(mantenimientoId),
        fecha: data.fecha || "",
        trabajos_realizados: data.trabajos_realizados || {},
        datos_funcionamiento: data.datos_funcionamiento || {},
        repuestos_utilizados:
          data.repuestos_utilizados?.length
            ? data.repuestos_utilizados
            : prev.repuestos_utilizados,
      }));
    } catch {
      console.log("No existe formato previo.");
    }
  };

  const cargarFormatoAlCambiarOt = useEffectEvent(() => {
    cargarDetalleMantenimiento();
    cargarFormatoExistente();
  });

  useEffect(() => {
    const timer = window.setTimeout(() => {
      cargarFormatoAlCambiarOt();
    }, 0);
    return () => window.clearTimeout(timer);
  }, [mantenimientoId]);

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
    const endpoint = formatoId
      ? `/formatos-mantenimiento/${formatoId}`
      : "/formatos-mantenimiento/";
    const url = `${API_URL}${endpoint}`;
    const method = formatoId ? "PUT" : "POST";
    const payload = {
      ...form,
      mantenimiento_id: String(mantenimientoId),
      tipo_equipo: form.tipo_equipo || templateKey,
      trabajos_realizados: {
        ...form.trabajos_realizados,
        _plantilla: templateKey,
        _titulo_plantilla: template.titulo,
      },
    };

    try {
      const res = await fetch(url, {
        method,
        headers: getHeaders(),
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        const error = await res.json();
        alert(error.detail || "No se pudo guardar el formato.");
        return;
      }

      const data = await res.json();
      setFormatoId(data.id);
      alert("Bitácora guardada correctamente.");
    } catch (error) {
      console.error(error);
      if (isNetworkError(error)) {
        await queueOfflineRequest({ method: formatoId ? "put" : "post", url: endpoint, data: payload });
        alert("Sin conexión: el formato y la firma quedaron guardados para sincronización automática.");
        return;
      }
      alert("Error guardando la bitácora.");
    } finally {
      setGuardando(false);
    }
  };

  const guardarEImprimir = async () => {
    await guardarFormato();

    setTimeout(() => {
      navigate(`/tecnico/formato-mantenimiento/${mantenimientoId}/imprimir`);
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
            {template.titulo}
          </div>

          <div className="formato-code">
            <p>Código: {template.codigo}</p>
            <p>Versión: 00</p>
            <p>Emisión: 23/01/24</p>
          </div>
        </div>

        <div className="grid-form tres">
          <label>
            Fecha
            <input
              type="date"
              value={form.fecha || ""}
              onChange={(e) => actualizarCampo("fecha", e.target.value)}
            />
          </label>

          <label>
            Mantenimiento
            <select
              value={form.mantenimiento_tipo || "Preventivo"}
              onChange={(e) => actualizarCampo("mantenimiento_tipo", e.target.value)}
            >
              <option value="Preventivo">Preventivo</option>
              <option value="Correctivo">Correctivo</option>
            </select>
          </label>

          <label>
            O.T. No.
            <input
              value={form.numero_ot || ""}
              onChange={(e) => actualizarCampo("numero_ot", e.target.value)}
            />
          </label>
        </div>

        <div className="grid-form dos">
          <label>
            N° Inventario / Serie
            <input
              value={form.numero_inventario || ""}
              onChange={(e) => actualizarCampo("numero_inventario", e.target.value)}
            />
          </label>

          <label>
            Ubicación
            <input
              value={form.ubicacion || ""}
              onChange={(e) => actualizarCampo("ubicacion", e.target.value)}
            />
          </label>
        </div>

        <div className="grid-form dos">
          <label>
            Técnico
            <input
              value={form.tecnico_nombre || ""}
              onChange={(e) => actualizarCampo("tecnico_nombre", e.target.value)}
            />
          </label>

          <label>
            Técnico auxiliar
            <input
              value={form.tecnico_auxiliar || ""}
              onChange={(e) => actualizarCampo("tecnico_auxiliar", e.target.value)}
            />
          </label>
        </div>

        <h3>Tipo de equipo a revisar</h3>

        <div className="tipo-equipos">
          {template.tipos.map((tipo) => (
            <label key={tipo}>
              <input
                type="radio"
                name="tipo_equipo"
                checked={form.tipo_equipo === tipo}
                onChange={() => actualizarCampo("tipo_equipo", tipo)}
              />
              {tipo}
            </label>
          ))}
        </div>

        <h3>Trabajos realizados</h3>

        <div className="trabajos-grid">
          {template.trabajos.map(([key, label]) => (
            <label key={key}>
              {label}
              <input
                type="checkbox"
                checked={Boolean(form.trabajos_realizados?.[key])}
                onChange={(e) => actualizarTrabajo(key, e.target.checked)}
              />
            </label>
          ))}
        </div>

        <label className="campo-full">
          Otro
          <textarea
            value={form.trabajos_realizados?.otro || ""}
            onChange={(e) => actualizarTrabajo("otro", e.target.value)}
          />
        </label>

        <h3>Datos de funcionamiento del equipo</h3>

        <div className="tabla-funcionamiento">
          {template.mediciones.map(([key, label]) => (
            <div className="func-row" key={key}>
              <span>{label}</span>

              <input
                placeholder="L1 / Valor 1"
                value={form.datos_funcionamiento?.[`${key}_l1`] || ""}
                onChange={(e) => actualizarDato(`${key}_l1`, e.target.value)}
              />

              <input
                placeholder="L2 / Valor 2"
                value={form.datos_funcionamiento?.[`${key}_l2`] || ""}
                onChange={(e) => actualizarDato(`${key}_l2`, e.target.value)}
              />

              <input
                placeholder="L3 / Valor 3"
                value={form.datos_funcionamiento?.[`${key}_l3`] || ""}
                onChange={(e) => actualizarDato(`${key}_l3`, e.target.value)}
              />
            </div>
          ))}

          <div className="presiones">
            <input
              placeholder="Voltaje / Presión / Temperatura"
              value={form.datos_funcionamiento?.valor_1 || ""}
              onChange={(e) => actualizarDato("valor_1", e.target.value)}
            />

            <input
              placeholder="Corriente / Estado"
              value={form.datos_funcionamiento?.valor_2 || ""}
              onChange={(e) => actualizarDato("valor_2", e.target.value)}
            />

            <input
              placeholder="Resultado prueba"
              value={form.datos_funcionamiento?.valor_3 || ""}
              onChange={(e) => actualizarDato("valor_3", e.target.value)}
            />

            <input
              placeholder="Observación técnica"
              value={form.datos_funcionamiento?.valor_4 || ""}
              onChange={(e) => actualizarDato("valor_4", e.target.value)}
            />
          </div>
        </div>

        <h3>Repuestos utilizados</h3>

        <div className="repuestos">
          {form.repuestos_utilizados.map((rep, index) => (
            <div className="repuesto-row" key={index}>
              <input
                placeholder="Cant"
                value={rep.cantidad || ""}
                onChange={(e) => actualizarRepuesto(index, "cantidad", e.target.value)}
              />

              <input
                placeholder="Descripción del repuesto"
                value={rep.descripcion || ""}
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
            value={form.observaciones || ""}
            onChange={(e) => actualizarCampo("observaciones", e.target.value)}
          />
        </label>

        <div className="firmas">
          <SignaturePad label="Firma del cliente / usuario" value={form.firma_usuario || ""} onChange={(value) => actualizarCampo("firma_usuario", value)} />
          <SignaturePad label="Firma del técnico / operario" value={form.firma_operario || ""} onChange={(value) => actualizarCampo("firma_operario", value)} />

          <label>
            Firma del Coordinador
            <input
              value={form.firma_coordinador || ""}
              onChange={(e) => actualizarCampo("firma_coordinador", e.target.value)}
            />
          </label>
        </div>
      </div>
    </div>
  );
}
