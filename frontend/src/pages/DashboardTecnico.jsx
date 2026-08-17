// =========================================================
// DASHBOARD TÉCNICO PRO - SGAHolding
// Archivo: frontend/src/pages/DashboardTecnico.jsx
//
// Fase A + B:
// - Bandeja compacta inteligente.
// - Tabs por estado.
// - Modal de ejecución técnica.
// - Histórico de mantenimientos finalizados.
// =========================================================

import { useCallback, useEffect, useMemo, useState, useContext } from "react";
import { useNavigate } from "react-router-dom";
import API from "../api/axios";
import { AuthContext } from "../context/auth-context";
import { isImageEvidence, isPdfEvidence } from "../utils/evidenciaUtils";
import ModalEjecucionTecnica from "./ModalEjecucionTecnica";

import {
  Wrench,
  Play,
  CheckCircle,
  UploadCloud,
  Eye,
  RefreshCcw,
  X,
  FileText,
  Clock,
  LogOut,
  ClipboardList,
  Activity,
  History,
  Search,
  CalendarDays,
  Building2,
  MapPin,
} from "lucide-react";

import "./DashboardTecnico.css";

const API_BASE =
  import.meta.env.VITE_API_URL ||
  API?.defaults?.baseURL ||
  window.location.origin;

function buildFileUrl(url) {
  if (!url) return "#";
  if (url.startsWith("http://") || url.startsWith("https://")) return url;
  const base = String(API_BASE).replace(/\/$/, "");
  return url.startsWith("/") ? `${base}${url}` : `${base}/${url}`;
}

function buildDownloadUrl(evidencia) {
  if (!evidencia) return "#";

  if (evidencia.descarga_url) {
    return buildFileUrl(evidencia.descarga_url);
  }

  const filename =
    evidencia.filename ||
    String(evidencia.archivo_url || "").split("/").filter(Boolean).pop();

  return filename ? buildFileUrl(`/evidencias/descargar/${filename}`) : "#";
}

function handleImageFallback(event, fallbackUrl) {
  const img = event.currentTarget;

  if (fallbackUrl && fallbackUrl !== "#" && img.src !== fallbackUrl) {
    img.src = fallbackUrl;
    return;
  }

  img.style.display = "none";
}

export default function DashboardTecnico() {
  const { user, logout } = useContext(AuthContext);
  const navigate = useNavigate();

  const [data, setData] = useState(null);
  const [busqueda, setBusqueda] = useState("");
  const [filtroEstado, setFiltroEstado] = useState("");
  const [tabActivo, setTabActivo] = useState("ACTIVOS");

  const [detalle, setDetalle] = useState(null);
  const [modalEvidencia, setModalEvidencia] = useState(null);
  const [modalEjecucion, setModalEjecucion] = useState(null);
  const [modalHistorico, setModalHistorico] = useState(false);

  const [archivo, setArchivo] = useState(null);
  const [tipoEvidencia, setTipoEvidencia] = useState("ANTES");
  const [descripcionEvidencia, setDescripcionEvidencia] = useState("");
  const [evidenciasTecnico, setEvidenciasTecnico] = useState([]);
  const [cargandoEvidencias, setCargandoEvidencias] = useState(false);
  const [previewEvidencia, setPreviewEvidencia] = useState(null);

  const [pagina, setPagina] = useState(1);
  const porPagina = 8;

  const usuarioId = user?.usuario_id || user?.id;

  const cargarDashboardTecnico = useCallback(async () => {
    try {
      const res = await API.get(`/dashboard-tecnico/usuario/${usuarioId}`);
      setData(res.data);
    } catch (error) {
      console.error(error);
      alert("Error cargando portal técnico.");
    }
  }, [usuarioId]);

  useEffect(() => {
    if (!usuarioId) return undefined;
    const timer = window.setTimeout(() => cargarDashboardTecnico(), 0);
    return () => window.clearTimeout(timer);
  }, [usuarioId, cargarDashboardTecnico]);

  const mantenimientos = useMemo(() => data?.mantenimientos || [], [data?.mantenimientos]);
  const resumen = data?.resumen || {};

  const filtrados = useMemo(() => {
    const q = busqueda.toLowerCase();

    return mantenimientos.filter((m) => {
      const estado = String(m.estado || "").toUpperCase();

      const texto = `
        ${m.equipo?.nombre || ""}
        ${m.empresa?.nombre || ""}
        ${m.sede?.nombre || ""}
        ${m.tipo || ""}
        ${m.estado || ""}
        ${m.equipo?.codigo_id || ""}
        ${m.equipo?.inventario || ""}
        ${m.equipo?.serie || ""}
        ${m.equipo?.ubicacion || ""}
        ${m.equipo?.marca || ""}
        ${m.equipo?.modelo || ""}
      `.toLowerCase();

      const textoOk = texto.includes(q);
      const estadoOk = filtroEstado ? estado === filtroEstado : true;

      let tabOk = true;

      if (tabActivo === "ACTIVOS") {
        tabOk = ["PROGRAMADO", "ASIGNADO", "EN_PROCESO", "PAUSADO"].includes(estado);
      }

      if (tabActivo === "PROGRAMADOS") {
        tabOk = ["PROGRAMADO", "ASIGNADO"].includes(estado);
      }

      if (tabActivo === "EN_PROCESO") {
        tabOk = estado === "EN_PROCESO";
      }

      if (tabActivo === "PAUSADOS") {
        tabOk = estado === "PAUSADO";
      }

      if (tabActivo === "FINALIZADOS") {
        tabOk = estado === "FINALIZADO";
      }

      if (tabActivo === "TODOS") {
        tabOk = true;
      }

      return textoOk && estadoOk && tabOk;
    });
  }, [mantenimientos, busqueda, filtroEstado, tabActivo]);

  const totalPaginas = Math.max(1, Math.ceil(filtrados.length / porPagina));

  const visibles = filtrados.slice(
    (pagina - 1) * porPagina,
    pagina * porPagina
  );

  const cambiarTab = (tab) => {
    setTabActivo(tab);
    setFiltroEstado("");
    setPagina(1);
  };

  const filtrarPorCard = (estado) => {
    setFiltroEstado(estado);
    setTabActivo("TODOS");
    setPagina(1);
  };

  const abrirFormato = (mantenimiento) => {
    const id = mantenimiento.mantenimiento_id || mantenimiento.id;

    if (!id) {
      alert("No se encontró el ID del mantenimiento.");
      return;
    }

    navigate(`/tecnico/formato-mantenimiento/${id}`);
  };

  const abrirBitacora = (mantenimiento) => {
    const id = mantenimiento.mantenimiento_id || mantenimiento.id;

    if (!id) {
      alert("No se encontró el ID del mantenimiento.");
      return;
    }

    navigate(`/tecnico/formato-mantenimiento/${id}`);
  };

  const verDetalle = async (mantenimiento) => {
    try {
      const res = await API.get(
        `/dashboard-tecnico/mantenimiento/${mantenimiento.mantenimiento_id}/detalle`
      );
      setDetalle(res.data);
    } catch (error) {
      console.error(error);
      alert("No se pudo cargar el detalle.");
    }
  };

  const abrirEjecucionTecnica = async (mantenimiento) => {
    try {
      const res = await API.get(
        `/dashboard-tecnico/mantenimiento/${mantenimiento.mantenimiento_id}/detalle`
      );

      setModalEjecucion(res.data);
    } catch (error) {
      console.error(error);
      alert("No se pudo abrir la ejecución técnica.");
    }
  };

  const refrescarDetalleEjecucion = async (mantenimientoId) => {
    try {
      const res = await API.get(
        `/dashboard-tecnico/mantenimiento/${mantenimientoId}/detalle`
      );

      setModalEjecucion(res.data);
    } catch (error) {
      console.error(error);
    }
  };

  const cargarEvidenciasMantenimiento = async (mantenimientoId) => {
    if (!mantenimientoId) {
      setEvidenciasTecnico([]);
      return;
    }

    try {
      setCargandoEvidencias(true);
      const res = await API.get(`/evidencias/mantenimiento/${mantenimientoId}`);
      setEvidenciasTecnico(Array.isArray(res.data) ? res.data : []);
    } catch (error) {
      console.error("Error cargando evidencias del técnico:", error);
      setEvidenciasTecnico([]);
    } finally {
      setCargandoEvidencias(false);
    }
  };

  const abrirModalEvidencia = async (mantenimiento) => {
    setModalEvidencia(mantenimiento);
    setArchivo(null);
    setTipoEvidencia("ANTES");
    setDescripcionEvidencia("");
    await cargarEvidenciasMantenimiento(mantenimiento.mantenimiento_id);
  };

  const eliminarEvidenciaTecnico = async (evidenciaId) => {
    if (String(modalEvidencia?.estado || "").toUpperCase() === "FINALIZADO") {
      alert("Solicita al coordinador o administrador que reabra el mantenimiento antes de eliminar evidencias.");
      return;
    }

    const confirmar = window.confirm(
      "¿Deseas eliminar esta evidencia? Esta acción no se puede deshacer."
    );

    if (!confirmar) return;

    try {
      await API.delete(`/evidencias/${evidenciaId}`);

      if (modalEvidencia?.mantenimiento_id) {
        await cargarEvidenciasMantenimiento(modalEvidencia.mantenimiento_id);
      }

      await cargarDashboardTecnico();
      alert("Evidencia eliminada correctamente.");
    } catch (error) {
      console.error(error);
      alert(error.response?.data?.detail || "Error eliminando evidencia.");
    }
  };

  const subirEvidenciaRapida = async () => {
    if (String(modalEvidencia?.estado || "").toUpperCase() === "FINALIZADO") {
      alert("Solicita al coordinador o administrador que reabra el mantenimiento antes de cargar evidencias.");
      return;
    }

    if (!archivo || !modalEvidencia) {
      alert("Selecciona un archivo.");
      return;
    }

    try {
      const formData = new FormData();
      formData.append("usuario_id", usuarioId);
      formData.append("tipo", tipoEvidencia);
      formData.append("descripcion", descripcionEvidencia);
      formData.append("archivo", archivo);

      await API.post(
        `/dashboard-tecnico/mantenimiento/${modalEvidencia.mantenimiento_id}/evidencia`,
        formData
      );

      setArchivo(null);
      setDescripcionEvidencia("");

      await cargarEvidenciasMantenimiento(modalEvidencia.mantenimiento_id);
      await cargarDashboardTecnico();
      alert("Evidencia subida correctamente.");
    } catch (error) {
      console.error(error);
      alert(error.response?.data?.detail || "Error subiendo evidencia.");
    }
  };

  if (!data) {
    return <div className="tec-loading">Cargando dashboard técnico...</div>;
  }

  const evidenciaSoloLectura = String(modalEvidencia?.estado || "").toUpperCase() === "FINALIZADO";

  return (
    <div className="tec-shell">
      <aside className="tec-sidebar">
        <div className="tec-brand">
          <div className="tec-logo">SGA</div>
          <div>
            <h2>SGAHolding</h2>
            <p>Portal Técnico</p>
          </div>
        </div>

        <div className="tec-user-card">
          <strong>{user?.nombre_completo || "Técnico"}</strong>
          <span>TECNICO</span>
        </div>

        <nav className="tec-nav">
          <button className="active">
            <Wrench size={17} />
            Mis mantenimientos
          </button>

          <button onClick={() => setModalHistorico(true)}>
            <History size={17} />
            Histórico
          </button>
        </nav>

        <button className="tec-logout" onClick={logout}>
          <LogOut size={16} />
          Salir
        </button>
      </aside>

      <main className="tec-main">
        <div className="tec-header">
          <div>
            <p className="tec-kicker">SGAHolding · PORTAL TÉCNICO</p>
            <h1>Dashboard Técnico</h1>
            <p>Gestiona únicamente tus mantenimientos asignados.</p>
          </div>

          <button className="tec-btn-secondary" onClick={cargarDashboardTecnico}>
            <RefreshCcw size={17} />
            Actualizar
          </button>
        </div>

        <section className="tec-hero">
          <div>
            <span>MÓDULO OPERATIVO</span>
            <h2>Bitácora técnica en tiempo real</h2>
            <p>Inicia, documenta, pausa y finaliza mantenimientos asignados con trazabilidad automática.</p>
          </div>

          <div className="tec-hero-badge">
            <Activity size={18} />
            <div>
              <strong>Sesión técnica activa</strong>
              <small>{user?.nombre_completo || "Técnico"}</small>
            </div>
          </div>
        </section>

        <section className="tec-cards">
          <MetricCard title="Total" value={resumen.total_asignados || 0} icon={<Wrench />} onClick={() => cambiarTab("TODOS")} />
          <MetricCard title="Asignados" value={resumen.asignados || 0} icon={<Clock />} onClick={() => filtrarPorCard("ASIGNADO")} />
          <MetricCard title="Programados" value={resumen.programados || 0} icon={<Clock />} onClick={() => filtrarPorCard("PROGRAMADO")} />
          <MetricCard title="En proceso" value={resumen.en_proceso || 0} icon={<Play />} onClick={() => filtrarPorCard("EN_PROCESO")} />
          <MetricCard title="Finalizados" value={resumen.finalizados || 0} icon={<CheckCircle />} onClick={() => filtrarPorCard("FINALIZADO")} />
        </section>

        <section className="tec-panel">
          <div className="tec-panel-header pro">
            <div>
              <h2>Mis mantenimientos asignados</h2>
              <p>{filtrados.length} registros encontrados</p>
            </div>

            <button className="tec-history-btn" onClick={() => setModalHistorico(true)}>
              <History size={17} />
              Ver histórico
            </button>
          </div>

          <div className="tec-smart-tabs">
            <button className={tabActivo === "ACTIVOS" ? "active" : ""} onClick={() => cambiarTab("ACTIVOS")}>
              Activos
            </button>
            <button className={tabActivo === "PROGRAMADOS" ? "active" : ""} onClick={() => cambiarTab("PROGRAMADOS")}>
              Programados
            </button>
            <button className={tabActivo === "EN_PROCESO" ? "active" : ""} onClick={() => cambiarTab("EN_PROCESO")}>
              En proceso
            </button>
            <button className={tabActivo === "PAUSADOS" ? "active" : ""} onClick={() => cambiarTab("PAUSADOS")}>
              Pausados
            </button>
            <button className={tabActivo === "FINALIZADOS" ? "active" : ""} onClick={() => cambiarTab("FINALIZADOS")}>
              Finalizados
            </button>
            <button className={tabActivo === "TODOS" ? "active" : ""} onClick={() => cambiarTab("TODOS")}>
              Todos
            </button>
          </div>

          <section className="tec-toolbar compact">
            <div className="tec-searchbox">
              <Search size={16} />
              <input
                placeholder="Buscar por equipo, empresa, sede, código, serie, tipo o estado..."
                value={busqueda}
                onChange={(e) => {
                  setBusqueda(e.target.value);
                  setPagina(1);
                }}
              />
            </div>

            <select
              value={filtroEstado}
              onChange={(e) => {
                setFiltroEstado(e.target.value);
                setPagina(1);
              }}
            >
              <option value="">Todos los estados</option>
              <option value="PROGRAMADO">Programado</option>
              <option value="ASIGNADO">Asignado</option>
              <option value="EN_PROCESO">En proceso</option>
              <option value="PAUSADO">Pausado</option>
              <option value="FINALIZADO">Finalizado</option>
            </select>
          </section>

          <div className="tec-worklist">
            {visibles.map((m) => (
              <MantenimientoRow
                key={m.mantenimiento_id}
                mantenimiento={m}
                onDetalle={() => verDetalle(m)}
                onEvidencia={() => abrirModalEvidencia(m)}
                onBitacora={() => abrirBitacora(m)}
                onIniciar={() => abrirEjecucionTecnica(m)}
              />
            ))}
          </div>

          {filtrados.length === 0 && (
            <div className="tec-empty">No hay mantenimientos en esta vista.</div>
          )}

          <div className="tec-pagination">
            <button disabled={pagina === 1} onClick={() => setPagina(pagina - 1)}>
              Anterior
            </button>

            <span>Página {pagina} de {totalPaginas}</span>

            <button disabled={pagina === totalPaginas} onClick={() => setPagina(pagina + 1)}>
              Siguiente
            </button>
          </div>
        </section>
      </main>

      {detalle && <DetalleModal detalle={detalle} onClose={() => setDetalle(null)} />}

      {modalEjecucion && (
        <ModalEjecucionTecnica
          detalle={modalEjecucion}
          usuarioId={usuarioId}
          onClose={() => setModalEjecucion(null)}
          onRefreshDashboard={cargarDashboardTecnico}
          onRefreshDetalle={refrescarDetalleEjecucion}
          onAbrirFormato={abrirFormato}
        />
      )}

      {modalHistorico && (
        <HistoricoTecnicoModal
          usuarioId={usuarioId}
          onClose={() => setModalHistorico(false)}
          onDetalle={verDetalle}
          onBitacora={abrirBitacora}
        />
      )}

      {modalEvidencia && (
        <div className="tec-modal-backdrop">
          <div className="tec-modal">
            <div className="tec-modal-header">
              <h2>{evidenciaSoloLectura ? "Evidencias del mantenimiento" : "Subir evidencia"}</h2>
              <button onClick={() => setModalEvidencia(null)}>
                <X size={18} />
              </button>
            </div>

            <div className="tec-form">
              {evidenciaSoloLectura && (
                <div className="tec-readonly-notice">
                  Este mantenimiento está finalizado. Puedes consultar las evidencias, pero un coordinador o administrador debe reabrirlo para reemplazarlas.
                </div>
              )}
              <label>Tipo</label>
              <select disabled={evidenciaSoloLectura} value={tipoEvidencia} onChange={(e) => setTipoEvidencia(e.target.value)}>
                <option value="ANTES">Antes</option>
                <option value="DURANTE">Durante</option>
                <option value="DESPUES">Después</option>
                <option value="SOPORTE">Soporte</option>
              </select>

              <label>Archivo</label>
              <input
                type="file"
                accept=".jpg,.jpeg,.png,.pdf"
                onChange={(e) => setArchivo(e.target.files?.[0] || null)}
                disabled={evidenciaSoloLectura}
              />

              <label>Descripción</label>
              <textarea
                value={descripcionEvidencia}
                onChange={(e) => setDescripcionEvidencia(e.target.value)}
                disabled={evidenciaSoloLectura}
              />

              <button className="tec-btn-primary" onClick={subirEvidenciaRapida} disabled={evidenciaSoloLectura}>
                <UploadCloud size={17} />
                Subir evidencia
              </button>

              <div className="tec-evidence-manager">
                <div className="tec-evidence-manager-head">
                  <h3>Evidencias cargadas</h3>
                  <span>{evidenciasTecnico.length} archivo(s)</span>
                </div>

                {cargandoEvidencias ? (
                  <div className="tec-empty">Cargando evidencias...</div>
                ) : evidenciasTecnico.length === 0 ? (
                  <div className="tec-empty">Aún no hay evidencias para este mantenimiento.</div>
                ) : (
                  <div className="tec-evidence-manager-grid">
                    {evidenciasTecnico.map((ev) => {
                      const url = buildFileUrl(ev.archivo_url);
                      const fallbackUrl = buildDownloadUrl(ev);

                      return (
                        <article key={ev.id} className="tec-evidence-item">
                          <div className="tec-evidence-preview">
                            {isImageEvidence(ev) ? (
                              <img
                                src={url}
                                alt={ev.nombre_original || "Evidencia"}
                                onError={(event) => handleImageFallback(event, fallbackUrl)}
                              />
                            ) : (
                              <div className="tec-evidence-file">
                                <FileText size={32} />
                                <span>{isPdfEvidence(ev) ? "PDF" : "Archivo"}</span>
                              </div>
                            )}
                          </div>

                          <div className="tec-evidence-body">
                            <strong>{ev.tipo || "SOPORTE"}</strong>
                            <small>{ev.nombre_original || ev.filename || "Archivo"}</small>
                            <p>{ev.descripcion || "Sin descripción"}</p>

                            <div className="tec-evidence-actions">
                              <button
                                type="button"
                                className="tec-exec-light"
                                onClick={() => setPreviewEvidencia({ ...ev, url, fallbackUrl })}
                              >
                                <Eye size={15} />
                                Ver
                              </button>

                              <button
                                type="button"
                                className="tec-exec-danger"
                                onClick={() => eliminarEvidenciaTecnico(ev.id)}
                                disabled={evidenciaSoloLectura}
                              >
                                Eliminar
                              </button>
                            </div>
                          </div>
                        </article>
                      );
                    })}
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      {previewEvidencia && (
        <div className="tec-modal-backdrop">
          <div className="tec-modal tec-modal-large">
            <div className="tec-modal-header">
              <div>
                <h2>Vista de evidencia</h2>
                <p>{previewEvidencia.nombre_original || previewEvidencia.filename || "Archivo"}</p>
              </div>

              <button onClick={() => setPreviewEvidencia(null)}>
                <X size={18} />
              </button>
            </div>

            {isPdfEvidence(previewEvidencia) ? (
              <iframe
                src={previewEvidencia.url}
                title="Evidencia PDF"
                className="tec-evidence-iframe"
              />
            ) : (
              <img
                src={previewEvidencia.url}
                alt="Vista evidencia"
                className="tec-evidence-big-img"
                onError={(event) => handleImageFallback(event, previewEvidencia.fallbackUrl)}
              />
            )}
          </div>
        </div>
      )}
    </div>
  );
}

function MetricCard({ title, value, icon, onClick }) {
  return (
    <button className="tec-card" onClick={onClick}>
      <div className="tec-card-icon">{icon}</div>
      <div>
        <span>{title}</span>
        <strong>{value}</strong>
      </div>
    </button>
  );
}

function MantenimientoRow({ mantenimiento, onDetalle, onEvidencia, onBitacora, onIniciar }) {
  const e = mantenimiento.equipo || {};
  const empresa = mantenimiento.empresa || {};
  const sede = mantenimiento.sede || {};
  const estado = String(mantenimiento.estado || "").toUpperCase();

  return (
    <article className="tec-work-row">
      <div className={`tec-work-priority ${statusLineClass(estado)}`} />

      <div className="tec-work-content">
        <div className="tec-work-main">
          <div>
            <div className="tec-work-badges">
              <span className="tec-type-badge">{mantenimiento.tipo || "MANTENIMIENTO"}</span>
              <span className={statusClass(estado)}>{estado || "SIN ESTADO"}</span>
            </div>

            <h3>{e.nombre || "Equipo sin nombre"}</h3>

            <p>
              <Building2 size={14} />
              {empresa.nombre || "Empresa no registrada"} · {sede.nombre || "Sede no registrada"}
            </p>
          </div>

          <button className="tec-work-primary" onClick={onIniciar}>
            <Play size={16} />
            {estado === "FINALIZADO"
              ? "Ver finalizado"
              : estado === "EN_PROCESO"
                ? "Continuar ejecución"
                : "Iniciar"}
          </button>
        </div>

        <div className="tec-work-meta">
          <InfoMini icon={<CalendarDays size={14} />} label="Programado" value={formatDate(mantenimiento.fecha_programada)} />
          <InfoMini icon={<MapPin size={14} />} label="Ubicación" value={e.ubicacion || "—"} />
          <InfoMini
            icon={<ClipboardList size={14} />}
            label="Inventario / Código / Serie"
            value={`${e.inventario || "—"} / ${e.codigo_id || "—"} / ${e.serie || "—"}`}
          />
          <InfoMini icon={<Activity size={14} />} label="Estado equipo" value={e.estado || "—"} />
        </div>

        <div className="tec-work-actions">
          <button onClick={onDetalle}>
            <Eye size={15} />
            Detalle
          </button>

          <button onClick={onEvidencia}>
            <UploadCloud size={15} />
            Evidencia
          </button>

          <button className="dark" onClick={onBitacora}>
            <ClipboardList size={15} />
            Bitácora
          </button>
        </div>
      </div>
    </article>
  );
}

function HistoricoTecnicoModal({ usuarioId, onClose, onDetalle, onBitacora }) {
  const [historico, setHistorico] = useState([]);
  const [cargando, setCargando] = useState(true);

  const [desde, setDesde] = useState("");
  const [hasta, setHasta] = useState("");
  const [empresa, setEmpresa] = useState("");
  const [sede, setSede] = useState("");
  const [equipo, setEquipo] = useState("");

  const cargarHistorico = useCallback(async () => {
    try {
      setCargando(true);

      const params = new URLSearchParams();

      if (desde) params.append("desde", desde);
      if (hasta) params.append("hasta", hasta);
      if (empresa) params.append("empresa", empresa);
      if (sede) params.append("sede", sede);
      if (equipo) params.append("equipo", equipo);

      const res = await API.get(
        `/dashboard-tecnico/usuario/${usuarioId}/historico?${params.toString()}`
      );

      setHistorico(res.data.historico || []);
    } catch (error) {
      console.error(error);
      alert("No se pudo cargar el histórico.");
    } finally {
      setCargando(false);
    }
  }, [desde, empresa, equipo, hasta, sede, usuarioId]);

  useEffect(() => {
    const timer = window.setTimeout(() => cargarHistorico(), 0);
    return () => window.clearTimeout(timer);
  }, [cargarHistorico]);

  return (
    <div className="tec-modal-backdrop">
      <div className="tec-modal tec-history-modal">
        <div className="tec-modal-header">
          <div>
            <h2>Histórico de mantenimientos realizados</h2>
            <p>{historico.length} mantenimientos finalizados</p>
          </div>

          <button onClick={onClose}>
            <X size={18} />
          </button>
        </div>

        <div className="tec-history-filters">
          <input type="date" value={desde} onChange={(e) => setDesde(e.target.value)} />
          <input type="date" value={hasta} onChange={(e) => setHasta(e.target.value)} />
          <input placeholder="Empresa" value={empresa} onChange={(e) => setEmpresa(e.target.value)} />
          <input placeholder="Sede" value={sede} onChange={(e) => setSede(e.target.value)} />
          <input placeholder="Equipo" value={equipo} onChange={(e) => setEquipo(e.target.value)} />

          <button onClick={cargarHistorico}>
            <Search size={15} />
            Filtrar
          </button>
        </div>

        {cargando ? (
          <div className="tec-empty">Cargando histórico...</div>
        ) : (
          <div className="tec-history-table-wrap">
            <table className="tec-history-table">
              <thead>
                <tr>
                  <th>Fecha finalización</th>
                  <th>Equipo</th>
                  <th>Empresa / Sede</th>
                  <th>Tipo</th>
                  <th>Resultado</th>
                  <th>Acciones</th>
                </tr>
              </thead>

              <tbody>
                {historico.map((m) => (
                  <tr key={m.mantenimiento_id}>
                    <td>{formatDate(m.fecha_finalizacion || m.fecha_fin)}</td>
                    <td>
                      <strong>{m.equipo?.nombre || "Equipo"}</strong>
                      <span>{m.equipo?.codigo_id || m.equipo?.inventario || "Sin código"}</span>
                    </td>
                    <td>
                      <strong>{m.empresa?.nombre || "Empresa"}</strong>
                      <span>{m.sede?.nombre || "Sede"}</span>
                    </td>
                    <td>{m.tipo || "—"}</td>
                    <td>{m.resultado_final || m.observaciones || "Sin resultado registrado"}</td>
                    <td>
                      <div className="tec-history-actions">
                        <button onClick={() => onDetalle(m)}>Detalle</button>
                        <button onClick={() => onBitacora(m)}>Bitácora</button>
                      </div>
                    </td>
                  </tr>
                ))}

                {historico.length === 0 && (
                  <tr>
                    <td colSpan="6">
                      <div className="tec-empty">No hay mantenimientos finalizados con estos filtros.</div>
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

function DetalleModal({ detalle, onClose }) {
  const mantenimiento = detalle.mantenimiento || {};
  const equipo = detalle.equipo_basico || {};
  const encabezado = detalle.encabezado || {};
  const evidencias = detalle.evidencias || [];

  return (
    <div className="tec-modal-backdrop">
      <div className="tec-modal tec-modal-large">
        <div className="tec-modal-header">
          <h2>Detalle del mantenimiento</h2>
          <button onClick={onClose}><X size={18} /></button>
        </div>

        <div className="tec-detail-grid">
          <Info title="Equipo" value={equipo.nombre} />
          <Info title="Inventario" value={equipo.inventario} />
          <Info title="Código interno" value={equipo.codigo_id} />
          <Info title="Categoría" value={equipo.categoria} />
          <Info title="Marca" value={equipo.marca} />
          <Info title="Modelo" value={equipo.modelo} />
          <Info title="Serie" value={equipo.serie} />
          <Info title="Ubicación" value={equipo.ubicacion} />
          <Info title="Empresa" value={encabezado.empresa_nombre} />
          <Info title="Sede" value={encabezado.sede_nombre} />
          <Info title="Criticidad" value={equipo.criticidad} />
          <Info title="Estado del equipo" value={equipo.estado} />
          <Info title="Registro INVIMA" value={equipo.invima} />
          <Info title="Tipo" value={mantenimiento.tipo} />
          <Info title="Estado" value={mantenimiento.estado} />
          <Info title="Resultado final" value={mantenimiento.resultado_final} />
          <Info title="Observaciones" value={mantenimiento.observaciones} />
        </div>

        <h3>Evidencias</h3>

        <div className="tec-evidence-grid">
          {evidencias.map((ev) => (
            <a
              key={ev.id}
              className="tec-evidence-card"
              href={getFileUrl(ev.archivo_url)}
              target="_blank"
              rel="noreferrer"
            >
              <FileText size={24} />
              <strong>{ev.tipo}</strong>
              <span>{ev.nombre_original || "Archivo"}</span>
            </a>
          ))}

          {evidencias.length === 0 && <div className="tec-empty">Sin evidencias.</div>}
        </div>
      </div>
    </div>
  );
}

function Info({ title, value }) {
  return (
    <div className="tec-info">
      <span>{title}</span>
      <strong>{value || "—"}</strong>
    </div>
  );
}

function InfoMini({ icon, label, value }) {
  return (
    <div className="tec-info-mini">
      <div>{icon}</div>
      <span>{label}</span>
      <strong>{value || "—"}</strong>
    </div>
  );
}

function statusClass(estado) {
  const value = String(estado || "").toUpperCase();
  if (value === "FINALIZADO") return "tec-status ok";
  if (value === "PAUSADO") return "tec-status warning";
  if (value === "EN_PROCESO") return "tec-status progress";
  if (value === "PROGRAMADO") return "tec-status programado";
  return "tec-status";
}

function statusLineClass(estado) {
  const value = String(estado || "").toUpperCase();
  if (value === "FINALIZADO") return "line-ok";
  if (value === "PAUSADO") return "line-warning";
  if (value === "EN_PROCESO") return "line-progress";
  if (value === "PROGRAMADO") return "line-programado";
  return "line-default";
}

function formatDate(value) {
  if (!value) return "Sin fecha";
  const d = new Date(value);
  return Number.isNaN(d.getTime()) ? value : d.toLocaleString();
}

function getFileUrl(url) {
  return buildFileUrl(url);
}
