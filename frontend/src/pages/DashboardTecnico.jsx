// =========================================================
// DASHBOARD TÉCNICO PRO - SGA PRO
// Técnico solo ve mantenimientos asignados
// Cards clicables + acciones + paginación
// =========================================================

import { useEffect, useMemo, useState, useContext } from "react";
import API from "../api/axios";
import { AuthContext } from "../context/AuthContext";
import {
  Wrench,
  Play,
  Pause,
  CheckCircle,
  UploadCloud,
  Eye,
  RefreshCcw,
  X,
  FileText,
  Clock,
  LogOut,
} from "lucide-react";

import "./DashboardTecnico.css";

export default function DashboardTecnico() {
  const { user, logout } = useContext(AuthContext);

  const [data, setData] = useState(null);
  const [busqueda, setBusqueda] = useState("");
  const [filtroEstado, setFiltroEstado] = useState("");
  const [observacion, setObservacion] = useState("");
  const [detalle, setDetalle] = useState(null);
  const [modalEvidencia, setModalEvidencia] = useState(null);

  const [archivo, setArchivo] = useState(null);
  const [tipoEvidencia, setTipoEvidencia] = useState("ANTES");
  const [descripcionEvidencia, setDescripcionEvidencia] = useState("");

  const [pagina, setPagina] = useState(1);
  const porPagina = 6;

  const usuarioId = user?.usuario_id || user?.id;

  useEffect(() => {
    if (usuarioId) cargarDashboardTecnico();
  }, [usuarioId]);

  const cargarDashboardTecnico = async () => {
    try {
      const res = await API.get(`/dashboard-tecnico/usuario/${usuarioId}`);
      setData(res.data);
    } catch (error) {
      console.error(error);
      alert("Error cargando portal técnico.");
    }
  };

  const mantenimientos = data?.mantenimientos || [];
  const resumen = data?.resumen || {};

  const filtrados = useMemo(() => {
    const q = busqueda.toLowerCase();

    return mantenimientos.filter((m) => {
      const texto = `
        ${m.equipo?.nombre || ""}
        ${m.empresa?.nombre || ""}
        ${m.sede?.nombre || ""}
        ${m.tipo || ""}
        ${m.estado || ""}
      `.toLowerCase();

      const estadoOk = filtroEstado ? m.estado === filtroEstado : true;

      return texto.includes(q) && estadoOk;
    });
  }, [mantenimientos, busqueda, filtroEstado]);

  const totalPaginas = Math.max(1, Math.ceil(filtrados.length / porPagina));

  const visibles = filtrados.slice(
    (pagina - 1) * porPagina,
    pagina * porPagina
  );

  const filtrarPorCard = (estado) => {
    setFiltroEstado(estado);
    setPagina(1);
  };

  const cambiarEstado = async (mantenimiento, nuevoEstado) => {
    try {
      const formData = new FormData();
      formData.append("usuario_id", usuarioId);
      formData.append("nuevo_estado", nuevoEstado);
      formData.append("observacion", observacion || "");

      await API.patch(
        `/dashboard-tecnico/mantenimiento/${mantenimiento.mantenimiento_id}/estado`,
        formData
      );

      setObservacion("");
      await cargarDashboardTecnico();
      alert("Estado actualizado correctamente.");
    } catch (error) {
      console.error(error);
      alert(error.response?.data?.detail || "No se pudo cambiar el estado.");
    }
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

  const subirEvidencia = async () => {
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

      setModalEvidencia(null);
      setArchivo(null);
      setDescripcionEvidencia("");

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

  return (
    <div className="tec-shell">
      <aside className="tec-sidebar">
        <div className="tec-brand">
          <div className="tec-logo">SGA</div>
          <div>
            <h2>SGA PRO</h2>
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
        </nav>

        <button className="tec-logout" onClick={logout}>
          <LogOut size={16} />
          Salir
        </button>
      </aside>

      <main className="tec-main">
        <div className="tec-header">
          <div>
            <p className="tec-kicker">SGA PRO · PORTAL TÉCNICO</p>
            <h1>Dashboard Técnico</h1>
            <p>Gestiona únicamente tus mantenimientos asignados.</p>
          </div>

          <button className="tec-btn-secondary" onClick={cargarDashboardTecnico}>
            <RefreshCcw size={17} />
            Actualizar
          </button>
        </div>

        <section className="tec-cards">
          <MetricCard title="Total" value={resumen.total_asignados || 0} icon={<Wrench />} onClick={() => filtrarPorCard("")} />
          <MetricCard title="Asignados" value={resumen.asignados || 0} icon={<Clock />} onClick={() => filtrarPorCard("ASIGNADO")} />
          <MetricCard title="En proceso" value={resumen.en_proceso || 0} icon={<Play />} onClick={() => filtrarPorCard("EN_PROCESO")} />
          <MetricCard title="Pausados" value={resumen.pausados || 0} icon={<Pause />} onClick={() => filtrarPorCard("PAUSADO")} />
          <MetricCard title="Finalizados" value={resumen.finalizados || 0} icon={<CheckCircle />} onClick={() => filtrarPorCard("FINALIZADO")} />
        </section>

        <section className="tec-toolbar">
          <input
            placeholder="Buscar por equipo, empresa, sede, tipo o estado..."
            value={busqueda}
            onChange={(e) => {
              setBusqueda(e.target.value);
              setPagina(1);
            }}
          />

          <select
            value={filtroEstado}
            onChange={(e) => {
              setFiltroEstado(e.target.value);
              setPagina(1);
            }}
          >
            <option value="">Todos los estados</option>
            <option value="ASIGNADO">Asignado</option>
            <option value="EN_PROCESO">En proceso</option>
            <option value="PAUSADO">Pausado</option>
            <option value="FINALIZADO">Finalizado</option>
          </select>
        </section>

        <section className="tec-observation">
          <label>Observación técnica rápida</label>
          <textarea
            value={observacion}
            onChange={(e) => setObservacion(e.target.value)}
            placeholder="Observación para acompañar el cambio de estado..."
          />
        </section>

        <section className="tec-panel">
          <div className="tec-panel-header">
            <div>
              <h2>Mantenimientos asignados</h2>
              <p>{filtrados.length} registros encontrados</p>
            </div>
          </div>

          <div className="tec-grid">
            {visibles.map((m) => (
              <MantenimientoCard
                key={m.mantenimiento_id}
                mantenimiento={m}
                onDetalle={() => verDetalle(m)}
                onEvidencia={() => setModalEvidencia(m)}
                onEstado={(estado) => cambiarEstado(m, estado)}
              />
            ))}
          </div>

          {filtrados.length === 0 && (
            <div className="tec-empty">No tienes mantenimientos asignados.</div>
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

      {modalEvidencia && (
        <div className="tec-modal-backdrop">
          <div className="tec-modal">
            <div className="tec-modal-header">
              <h2>Subir evidencia</h2>
              <button onClick={() => setModalEvidencia(null)}>
                <X size={18} />
              </button>
            </div>

            <div className="tec-form">
              <label>Tipo</label>
              <select value={tipoEvidencia} onChange={(e) => setTipoEvidencia(e.target.value)}>
                <option value="ANTES">Antes</option>
                <option value="DURANTE">Durante</option>
                <option value="DESPUES">Después</option>
                <option value="SOPORTE">Soporte</option>
              </select>

              <label>Archivo</label>
              <input type="file" accept=".jpg,.jpeg,.png,.pdf" onChange={(e) => setArchivo(e.target.files?.[0] || null)} />

              <label>Descripción</label>
              <textarea value={descripcionEvidencia} onChange={(e) => setDescripcionEvidencia(e.target.value)} />

              <button className="tec-btn-primary" onClick={subirEvidencia}>
                <UploadCloud size={17} />
                Subir evidencia
              </button>
            </div>
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

function MantenimientoCard({ mantenimiento, onDetalle, onEvidencia, onEstado }) {
  const e = mantenimiento.equipo || {};
  const empresa = mantenimiento.empresa || {};
  const sede = mantenimiento.sede || {};

  return (
    <article className="tec-maint-card">
      <div className="tec-maint-top">
        <div>
          <h3>{e.nombre || "Equipo"}</h3>
          <p>{empresa.nombre || "Empresa"} · {sede.nombre || "Sede"}</p>
        </div>

        <span className={statusClass(mantenimiento.estado)}>
          {mantenimiento.estado}
        </span>
      </div>

      <div className="tec-maint-info">
        <div><span>Tipo</span><strong>{mantenimiento.tipo || "—"}</strong></div>
        <div><span>Programado</span><strong>{formatDate(mantenimiento.fecha_programada)}</strong></div>
        <div><span>Código / Serie</span><strong>{e.codigo_id || e.inventario || "—"} / {e.serie || "—"}</strong></div>
        <div><span>Ubicación</span><strong>{e.ubicacion || "—"}</strong></div>
      </div>

      <div className="tec-actions">
        <button className="tec-btn-secondary" onClick={onDetalle}><Eye size={15} />Detalle</button>
        <button className="tec-btn-secondary" onClick={onEvidencia}><UploadCloud size={15} />Evidencia</button>
      </div>

      <div className="tec-state-actions">
        <button onClick={() => onEstado("EN_PROCESO")}><Play size={14} />Iniciar</button>
        <button onClick={() => onEstado("PAUSADO")}><Pause size={14} />Pausar</button>
        <button onClick={() => onEstado("FINALIZADO")}><CheckCircle size={14} />Finalizar</button>
      </div>
    </article>
  );
}

function DetalleModal({ detalle, onClose }) {
  const mantenimiento = detalle.mantenimiento || {};
  const equipo = detalle.equipo_basico || {};
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
          <Info title="Marca" value={equipo.marca} />
          <Info title="Modelo" value={equipo.modelo} />
          <Info title="Serie" value={equipo.serie} />
          <Info title="Ubicación" value={equipo.ubicacion} />
          <Info title="Tipo" value={mantenimiento.tipo} />
          <Info title="Estado" value={mantenimiento.estado} />
          <Info title="Observaciones" value={mantenimiento.observaciones} />
        </div>

        <h3>Evidencias</h3>

        <div className="tec-evidence-grid">
          {evidencias.map((ev) => (
            <a key={ev.id} className="tec-evidence-card" href={getFileUrl(ev.archivo_url)} target="_blank" rel="noreferrer">
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

function statusClass(estado) {
  const value = String(estado || "").toUpperCase();
  if (value === "FINALIZADO") return "tec-status ok";
  if (value === "PAUSADO") return "tec-status warning";
  if (value === "EN_PROCESO") return "tec-status progress";
  return "tec-status";
}

function formatDate(value) {
  if (!value) return "—";
  const d = new Date(value);
  return Number.isNaN(d.getTime()) ? value : d.toLocaleString();
}

function getFileUrl(url) {
  if (!url) return "#";
  if (url.startsWith("http")) return url;
  return `http://127.0.0.1:8000${url}`;
}