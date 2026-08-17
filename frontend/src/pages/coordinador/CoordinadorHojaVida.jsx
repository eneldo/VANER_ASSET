import { useEffect, useEffectEvent, useMemo, useRef, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import {
  Activity,
  CalendarDays,
  CheckCircle2,
  ClipboardList,
  FileCheck2,
  FileText,
  Gauge,
  Printer,
  RefreshCw,
  Save,
  Search,
  ShieldCheck,
  Wrench,
} from "lucide-react";

import API from "../../api/axios";
import "../../styles/coordinador.css";

const hojaInicial = {
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
};

const tabs = [
  { id: "identificacion", label: "Identificación", icon: ClipboardList },
  { id: "adquisicion", label: "Adquisición", icon: CalendarDays },
  { id: "tecnica", label: "Ficha técnica", icon: Gauge },
  { id: "documentacion", label: "Documentación", icon: FileCheck2 },
  { id: "mantenimientos", label: "Mantenimientos", icon: Wrench },
  { id: "riesgo", label: "Calibración y riesgo", icon: ShieldCheck },
];

const camposTecnicos = [
  ["rango_voltaje", "Voltaje", "Ej. 110-220 V"],
  ["rango_corriente", "Corriente", "Ej. 10 A"],
  ["rango_potencia", "Potencia", "Ej. 1.5 kW"],
  ["frecuencia", "Frecuencia", "Ej. 50/60 Hz"],
  ["capacidad", "Capacidad", "Capacidad nominal"],
  ["rango_presion", "Presión", "Rango de operación"],
  ["rango_temperatura", "Temperatura", "Rango permitido"],
  ["rango_humedad", "Humedad", "Rango permitido"],
  ["rango_velocidad", "Velocidad", "Rango de trabajo"],
  ["gas_refrigerante", "Gas refrigerante", "Tipo y carga"],
];

const gruposDocumentos = [
  {
    titulo: "Manuales disponibles",
    campos: [
      ["manual_operacion", "Operación"],
      ["manual_mantenimiento", "Mantenimiento"],
      ["manual_partes", "Partes"],
      ["manual_despiece", "Despiece"],
    ],
  },
  {
    titulo: "Planos disponibles",
    campos: [
      ["plano_electronico", "Electrónico"],
      ["plano_electrico", "Eléctrico"],
      ["plano_neumatico", "Neumático"],
      ["plano_mecanico", "Mecánico"],
    ],
  },
];

const riesgos = [
  ["riesgo_bajo", "Bajo", "Clase I"],
  ["riesgo_moderado", "Moderado", "Clase IIA"],
  ["riesgo_alto", "Alto", "Clase IIB"],
  ["riesgo_elevado", "Elevado", "Clase III"],
];

const clasificaciones = [
  ["clase_diagnostico", "Diagnóstico"],
  ["clase_prevencion", "Prevención"],
  ["clase_rehabilitacion", "Rehabilitación"],
  ["clase_analisis", "Análisis de laboratorio"],
];

function valorPresente(valor) {
  return valor !== null && valor !== undefined && String(valor).trim() !== "";
}

function formatearFecha(valor, incluirHora = false) {
  if (!valor) return "Sin fecha";
  const fecha = new Date(valor);
  if (Number.isNaN(fecha.getTime())) return valor;
  return new Intl.DateTimeFormat("es-CO", {
    dateStyle: "medium",
    ...(incluirHora ? { timeStyle: "short" } : {}),
  }).format(fecha);
}

function ordenarCamposTecnicos(categoria) {
  const texto = String(categoria || "").toLowerCase();
  let prioritarios = [];

  if (/aire|refrig|clima|nevera|congel/.test(texto)) {
    prioritarios = ["gas_refrigerante", "rango_temperatura", "capacidad", "rango_presion"];
  } else if (/biom[eé]d|laboratorio|m[eé]dic|diagn[oó]st/.test(texto)) {
    prioritarios = ["rango_voltaje", "rango_corriente", "rango_potencia", "frecuencia", "rango_humedad"];
  } else if (/motor|bomba|compresor|industrial/.test(texto)) {
    prioritarios = ["rango_potencia", "rango_corriente", "rango_velocidad", "rango_presion"];
  }

  return [...camposTecnicos].sort((campoA, campoB) => {
    const posicionA = prioritarios.indexOf(campoA[0]);
    const posicionB = prioritarios.indexOf(campoB[0]);
    if (posicionA === -1 && posicionB === -1) return 0;
    if (posicionA === -1) return 1;
    if (posicionB === -1) return -1;
    return posicionA - posicionB;
  });
}

export default function CoordinadorHojaVida() {
  const { equipoId: equipoIdUrl } = useParams();
  const navigate = useNavigate();
  const [equipos, setEquipos] = useState([]);
  const [equipoId, setEquipoId] = useState(equipoIdUrl || "");
  const [detalle, setDetalle] = useState(null);
  const [mantenimientos, setMantenimientos] = useState([]);
  const [hojaVida, setHojaVida] = useState(hojaInicial);
  const [busqueda, setBusqueda] = useState("");
  const [tabActiva, setTabActiva] = useState("identificacion");
  const [cargando, setCargando] = useState(true);
  const [guardando, setGuardando] = useState(false);
  const [cambiosPendientes, setCambiosPendientes] = useState(false);
  const [estadoGuardado, setEstadoGuardado] = useState("Sin cambios pendientes");
  const [mensaje, setMensaje] = useState(null);
  const versionCambios = useRef(0);

  const cargarEquiposAlMontar = useEffectEvent(() => cargarEquipos());
  const cargarHojaAlCambiarEquipo = useEffectEvent((id) => cargarHojaVida(id));
  const guardarAutomaticamente = useEffectEvent(() => guardar({ automatico: true }));

  useEffect(() => {
    cargarEquiposAlMontar();
  }, []);

  useEffect(() => {
    if (equipoId) cargarHojaAlCambiarEquipo(equipoId);
  }, [equipoId]);

  useEffect(() => {
    if (!cambiosPendientes || cargando || guardando || !equipoId) return undefined;
    const temporizador = window.setTimeout(() => guardarAutomaticamente(), 1400);
    return () => window.clearTimeout(temporizador);
  }, [cambiosPendientes, cargando, guardando, equipoId, hojaVida]);

  const mostrarMensaje = (tipo, texto) => {
    setMensaje({ tipo, texto });
    window.setTimeout(() => setMensaje(null), 3500);
  };

  async function cargarEquipos() {
    try {
      setCargando(true);
      const respuesta = await API.get("/coordinador/equipos");
      const lista = respuesta.data || [];
      setEquipos(lista);
      if (!equipoIdUrl && !equipoId && lista.length) setEquipoId(lista[0].id);
    } catch (error) {
      console.error("Error cargando equipos:", error);
      mostrarMensaje("error", "No se pudieron cargar los equipos.");
    } finally {
      if (!equipoId && !equipoIdUrl) setCargando(false);
    }
  }

  async function cargarHojaVida(id) {
    try {
      setCargando(true);
      const [respuestaHoja, respuestaMantenimientos] = await Promise.all([
        API.get(`/coordinador/equipos/${id}/hoja-vida`),
        API.get("/coordinador/mantenimientos", { params: { equipo_id: id } }),
      ]);
      setDetalle(respuestaHoja.data || null);
      setMantenimientos(respuestaMantenimientos.data || []);
      setHojaVida({ ...hojaInicial, ...(respuestaHoja.data?.hoja_vida_tecnica || {}) });
      versionCambios.current = 0;
      setCambiosPendientes(false);
      const actualizado = respuestaHoja.data?.hoja_vida_tecnica?.updated_at;
      setEstadoGuardado(actualizado ? `Último guardado: ${formatearFecha(actualizado, true)}` : "Hoja lista para completar");
    } catch (error) {
      console.error("Error cargando hoja vida:", error);
      setDetalle(null);
      setMantenimientos([]);
      setHojaVida(hojaInicial);
      setCambiosPendientes(false);
      mostrarMensaje("error", "No se pudo cargar la hoja de vida del equipo.");
    } finally {
      setCargando(false);
    }
  }

  async function guardar({ automatico = false } = {}) {
    if (!equipoId || guardando || (automatico && !cambiosPendientes)) return false;

    const versionGuardada = versionCambios.current;
    try {
      setGuardando(true);
      setEstadoGuardado(automatico ? "Guardando automáticamente..." : "Guardando cambios...");
      const payload = Object.fromEntries(
        Object.entries(hojaVida)
          .filter(([campo]) => !["id", "equipo_id", "created_at", "updated_at"].includes(campo))
          .map(([campo, valor]) => [campo, valor === "" ? null : valor]),
      );
      const respuesta = await API.put(`/coordinador/equipos/${equipoId}/hoja-vida`, payload);
      const sinCambiosNuevos = versionCambios.current === versionGuardada;
      setHojaVida((actual) => (
        sinCambiosNuevos
          ? { ...actual, ...(respuesta.data || {}) }
          : {
              ...actual,
              id: respuesta.data?.id ?? actual.id,
              equipo_id: respuesta.data?.equipo_id ?? actual.equipo_id,
              updated_at: respuesta.data?.updated_at ?? actual.updated_at,
            }
      ));
      setCambiosPendientes(!sinCambiosNuevos);
      setEstadoGuardado(
        sinCambiosNuevos
          ? `Guardado: ${formatearFecha(respuesta.data?.updated_at || new Date(), true)}`
          : "Hay cambios nuevos pendientes de autoguardado...",
      );
      if (!automatico) mostrarMensaje("success", "Hoja de vida guardada correctamente.");
      return true;
    } catch (error) {
      console.error("Error guardando hoja vida:", error);
      setEstadoGuardado("No fue posible guardar los cambios");
      mostrarMensaje("error", error?.response?.data?.detail || "No se pudo guardar la hoja de vida.");
      return false;
    } finally {
      setGuardando(false);
    }
  }

  const equiposFiltrados = useMemo(() => {
    const texto = busqueda.toLowerCase().trim();
    return equipos.filter((equipo) =>
      `${equipo.nombre || ""} ${equipo.marca || ""} ${equipo.modelo || ""} ${equipo.serie || ""} ${equipo.inventario || ""}`
        .toLowerCase()
        .includes(texto),
    );
  }, [equipos, busqueda]);

  const equipo = detalle?.equipo_basico;
  const camposTecnicosOrdenados = useMemo(
    () => ordenarCamposTecnicos(equipo?.categoria_nombre || equipo?.categoria),
    [equipo?.categoria_nombre, equipo?.categoria],
  );

  const completitud = useMemo(() => {
    if (!equipo) return 0;
    const verificaciones = [
      equipo.nombre,
      equipo.marca,
      equipo.modelo,
      equipo.serie,
      equipo.inventario || equipo.codigo_id,
      equipo.ubicacion,
      hojaVida.adquisicion,
      hojaVida.fecha_compra,
      hojaVida.proveedor,
      hojaVida.pais_fabricacion,
      hojaVida.vida_util,
      hojaVida.rango_voltaje,
      hojaVida.capacidad,
      hojaVida.otros,
      gruposDocumentos.some((grupo) => grupo.campos.some(([campo]) => hojaVida[campo])),
      riesgos.some(([campo]) => hojaVida[campo]),
    ];
    const completos = verificaciones.filter((valor) => valor === true || valorPresente(valor)).length;
    return Math.round((completos / verificaciones.length) * 100);
  }, [equipo, hojaVida]);

  const setCampo = (campo, valor) => {
    versionCambios.current += 1;
    setHojaVida((actual) => ({ ...actual, [campo]: valor }));
    setCambiosPendientes(true);
    setEstadoGuardado("Guardado automático pendiente...");
  };

  const seleccionarRiesgo = (campoSeleccionado) => {
    versionCambios.current += 1;
    setHojaVida((actual) => ({
      ...actual,
      ...Object.fromEntries(riesgos.map(([campo]) => [campo, campo === campoSeleccionado])),
    }));
    setCambiosPendientes(true);
    setEstadoGuardado("Guardado automático pendiente...");
  };

  const seleccionarEquipo = (id) => {
    setEquipoId(id);
    setTabActiva("identificacion");
    if (equipoIdUrl) navigate(`/coordinador/hoja-vida/${id}`, { replace: true });
  };

  return (
    <div className="coord-page coord-lifecycle-page">
      <div className="coord-hero coord-lifecycle-hero">
        <div>
          <span className="coord-eyebrow">INVENTARIO · CICLO DE VIDA</span>
          <h2>Hoja de Vida Técnica</h2>
          <p>Registro centralizado, autoguardado e historial operativo del activo.</p>
        </div>
        <div className="coord-actions">
          <button className="coord-btn secondary" onClick={() => window.print()} disabled={!equipo}>
            <Printer size={17} />Imprimir / PDF
          </button>
          <button className="coord-btn secondary" onClick={() => equipoId && cargarHojaVida(equipoId)} disabled={!equipoId || cargando}>
            <RefreshCw size={17} />Actualizar
          </button>
          <button className="coord-btn primary" onClick={() => guardar()} disabled={!equipoId || guardando || !cambiosPendientes}>
            <Save size={17} />{guardando ? "Guardando..." : "Guardar ahora"}
          </button>
        </div>
      </div>

      {mensaje && <div className={`coord-alert ${mensaje.tipo}`}>{mensaje.texto}</div>}

      <div className="coord-lifecycle-toolbar">
        <div className="coord-search">
          <Search size={18} />
          <input value={busqueda} onChange={(event) => setBusqueda(event.target.value)} placeholder="Buscar equipo, serie o inventario" />
        </div>
        <select value={equipoId} onChange={(event) => seleccionarEquipo(event.target.value)}>
          <option value="">Seleccionar equipo</option>
          {equiposFiltrados.map((item) => (
            <option key={item.id} value={item.id}>{item.nombre} · {item.inventario || item.codigo_id || "Sin inventario"}</option>
          ))}
        </select>
        <div className={`coord-save-state ${cambiosPendientes ? "pending" : "saved"}`}>
          {cambiosPendientes ? <Activity size={16} /> : <CheckCircle2 size={16} />}
          <span>{estadoGuardado}</span>
        </div>
      </div>

      {!equipo && !cargando ? (
        <section className="coord-card coord-empty-state">
          <FileText size={42} />
          <h3>Selecciona un equipo</h3>
          <p>La hoja de vida se cargará con sus datos técnicos e historial.</p>
        </section>
      ) : (
        <>
          <section className="coord-lifecycle-summary">
            <div className="coord-asset-summary">
              <div className="coord-asset-icon"><FileText size={26} /></div>
              <div>
                <span>{detalle?.encabezado?.empresa_nombre || "Empresa"} · {detalle?.encabezado?.sede_nombre || "Sede"}</span>
                <h3>{equipo?.nombre || "Cargando equipo..."}</h3>
                <p>{equipo?.marca || "Sin marca"} {equipo?.modelo || ""} · Serie {equipo?.serie || "N/A"}</p>
              </div>
              <span className={`coord-badge ${String(equipo?.estado || "").toLowerCase()}`}>{equipo?.estado || "Cargando"}</span>
            </div>
            <div className="coord-completeness-card">
              <div className="coord-progress-ring" style={{ "--progress": `${completitud * 3.6}deg` }}>
                <strong>{completitud}%</strong>
              </div>
              <div><span>Completitud documental</span><strong>{completitud >= 80 ? "Hoja robusta" : "Información por completar"}</strong></div>
            </div>
          </section>

          <nav className="coord-lifecycle-tabs" aria-label="Secciones hoja de vida">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              return (
                <button key={tab.id} className={tabActiva === tab.id ? "active" : ""} onClick={() => setTabActiva(tab.id)}>
                  <Icon size={17} />{tab.label}
                </button>
              );
            })}
          </nav>

          <section className="coord-card coord-lifecycle-content">
            {cargando ? <p className="coord-empty">Cargando hoja de vida...</p> : null}
            {!cargando && tabActiva === "identificacion" && (
              <TabSection titulo="Identificación del activo" descripcion="Información maestra heredada del inventario.">
                <div className="coord-detail-grid">
                  <Info label="Nombre" value={equipo?.nombre} />
                  <Info label="Categoría" value={equipo?.categoria_nombre || equipo?.categoria} />
                  <Info label="Inventario" value={equipo?.inventario || equipo?.codigo_id} />
                  <Info label="Marca" value={equipo?.marca} />
                  <Info label="Modelo" value={equipo?.modelo} />
                  <Info label="Serie" value={equipo?.serie} />
                  <Info label="Ubicación" value={equipo?.ubicacion} />
                  <Info label="Criticidad" value={equipo?.criticidad} />
                  <Info label="Estado" value={equipo?.estado} />
                </div>
                <button className="coord-btn secondary" onClick={() => navigate("/coordinador/equipos")}>Editar datos básicos en inventario</button>
              </TabSection>
            )}

            {!cargando && tabActiva === "adquisicion" && (
              <TabSection titulo="Adquisición e instalación" descripcion="Trazabilidad financiera, fabricante y puesta en servicio.">
                <div className="coord-form-grid">
                  <Field label="Tipo de adquisición" value={hojaVida.adquisicion} onChange={(valor) => setCampo("adquisicion", valor)} placeholder="Compra, comodato, donación..." />
                  <Field label="Costo" type="number" value={hojaVida.costo} onChange={(valor) => setCampo("costo", valor)} placeholder="Valor de adquisición" />
                  <Field label="Fecha de compra" type="date" value={hojaVida.fecha_compra} onChange={(valor) => setCampo("fecha_compra", valor)} />
                  <Field label="Fecha de instalación" type="date" value={hojaVida.fecha_instalacion} onChange={(valor) => setCampo("fecha_instalacion", valor)} />
                  <Field label="Proveedor" value={hojaVida.proveedor} onChange={(valor) => setCampo("proveedor", valor)} />
                  <Field label="País de fabricación" value={hojaVida.pais_fabricacion} onChange={(valor) => setCampo("pais_fabricacion", valor)} />
                  <Field label="Fecha de fabricación" type="date" value={hojaVida.fecha_fabricacion} onChange={(valor) => setCampo("fecha_fabricacion", valor)} />
                  <Field label="Vida útil estimada" value={hojaVida.vida_util} onChange={(valor) => setCampo("vida_util", valor)} placeholder="Ej. 10 años" />
                </div>
              </TabSection>
            )}

            {!cargando && tabActiva === "tecnica" && (
              <TabSection titulo="Ficha técnica adaptativa" descripcion={`Campos priorizados automáticamente para ${equipo?.categoria_nombre || equipo?.categoria || "la categoría seleccionada"}.`}>
                <div className="coord-smart-hint"><Gauge size={18} /><span>Los campos más relevantes para esta categoría aparecen primero; los demás continúan disponibles.</span></div>
                <div className="coord-form-grid">
                  {camposTecnicosOrdenados.map(([campo, label, placeholder]) => (
                    <Field key={campo} label={label} value={hojaVida[campo]} onChange={(valor) => setCampo(campo, valor)} placeholder={placeholder} />
                  ))}
                  <label className="span-2">Otros datos técnicos<textarea rows="5" value={hojaVida.otros || ""} onChange={(event) => setCampo("otros", event.target.value)} placeholder="Normas, accesorios, consumibles, condiciones de operación u observaciones técnicas" /></label>
                </div>
              </TabSection>
            )}

            {!cargando && tabActiva === "documentacion" && (
              <TabSection titulo="Documentación técnica" descripcion="Control de disponibilidad de manuales y planos del activo.">
                <div className="coord-document-grid">
                  {gruposDocumentos.map((grupo) => (
                    <div className="coord-document-group" key={grupo.titulo}>
                      <h4>{grupo.titulo}</h4>
                      {grupo.campos.map(([campo, label]) => <Check key={campo} label={label} checked={hojaVida[campo]} onChange={(valor) => setCampo(campo, valor)} />)}
                    </div>
                  ))}
                </div>
              </TabSection>
            )}

            {!cargando && tabActiva === "mantenimientos" && (
              <TabSection titulo="Historial de mantenimientos" descripcion="Eventos registrados para este equipo en la empresa activa.">
                <div className="coord-maintenance-kpis">
                  <Metric label="Total eventos" value={mantenimientos.length} />
                  <Metric label="Finalizados" value={mantenimientos.filter((item) => item.estado === "FINALIZADO").length} />
                  <Metric label="Pendientes" value={mantenimientos.filter((item) => !["FINALIZADO", "ANULADO"].includes(item.estado)).length} />
                </div>
                <div className="coord-lifecycle-timeline">
                  {mantenimientos.length === 0 ? <p className="coord-empty">Este equipo aún no tiene mantenimientos registrados.</p> : mantenimientos.map((item) => (
                    <article key={item.id}>
                      <div className="coord-timeline-dot" />
                      <div>
                        <strong>{item.tipo || "Mantenimiento"}</strong>
                        <span>{item.tecnico_nombre || "Sin técnico"} · {item.descripcion || item.observaciones || "Sin descripción"}</span>
                      </div>
                      <div className="coord-timeline-meta">
                        <span className={`coord-badge ${String(item.estado || "").toLowerCase()}`}>{item.estado || "N/A"}</span>
                        <small>{formatearFecha(item.fecha_inicio_programada || item.fecha_programada || item.created_at, true)}</small>
                      </div>
                    </article>
                  ))}
                </div>
                <button className="coord-btn primary" onClick={() => navigate(`/coordinador/mantenimientos?equipo_id=${equipoId}`)}><Wrench size={16} />Gestionar mantenimientos</button>
              </TabSection>
            )}

            {!cargando && tabActiva === "riesgo" && (
              <TabSection titulo="Calibración y clasificación" descripcion="Requisitos metrológicos, uso biomédico y nivel de riesgo.">
                <label className="coord-calibration-switch">
                  <input type="checkbox" checked={!!hojaVida.requiere_calibracion} onChange={(event) => setCampo("requiere_calibracion", event.target.checked)} />
                  <span><strong>Requiere calibración periódica</strong><small>Activa este control cuando el equipo necesite verificación metrológica.</small></span>
                </label>
                <div className="coord-classification-grid">
                  <div>
                    <h4>Clasificación biomédica</h4>
                    {clasificaciones.map(([campo, label]) => <Check key={campo} label={label} checked={hojaVida[campo]} onChange={(valor) => setCampo(campo, valor)} />)}
                  </div>
                  <div>
                    <h4>Clasificación de riesgo</h4>
                    <div className="coord-risk-options">
                      {riesgos.map(([campo, label, clase]) => (
                        <button key={campo} className={hojaVida[campo] ? "active" : ""} onClick={() => seleccionarRiesgo(campo)}>
                          <ShieldCheck size={18} /><span><strong>{label}</strong><small>{clase}</small></span>
                        </button>
                      ))}
                    </div>
                  </div>
                </div>
              </TabSection>
            )}
          </section>
        </>
      )}
    </div>
  );
}

function TabSection({ titulo, descripcion, children }) {
  return (
    <div className="coord-tab-section">
      <div className="coord-section-heading"><div><h3>{titulo}</h3><p>{descripcion}</p></div></div>
      {children}
    </div>
  );
}

function Info({ label, value }) {
  return <div><span>{label}</span><strong>{value || "N/A"}</strong></div>;
}

function Field({ label, value, onChange, type = "text", placeholder = "" }) {
  return <label>{label}<input type={type} value={value || ""} onChange={(event) => onChange(event.target.value)} placeholder={placeholder} /></label>;
}

function Check({ label, checked, onChange }) {
  return (
    <label className="coord-document-check">
      <input type="checkbox" checked={!!checked} onChange={(event) => onChange(event.target.checked)} />
      <span>{label}</span>
      <CheckCircle2 size={18} />
    </label>
  );
}

function Metric({ label, value }) {
  return <div><span>{label}</span><strong>{value}</strong></div>;
}
