// =========================================================
// EVIDENCIAS PAGE PRO
// Galería visual + filtros + SaaS UI
// Admin consulta evidencias por equipo o mantenimiento.
// FIX PRODUCCIÓN:
// - No usa 127.0.0.1.
// - Construye URL pública desde VITE_API_URL.
// - Renderiza imagen real.
// - Preview modal para imagen/PDF.
// =========================================================

import { useEffect, useMemo, useState } from "react";
import AdminLayout from "./AdminLayout";
import API from "../../api/axios";

import {
  Image,
  Search,
  RefreshCcw,
  Trash2,
  FileText,
  Eye,
  ExternalLink,
} from "lucide-react";

const API_BASE =
  import.meta.env.VITE_API_URL ||
  API?.defaults?.baseURL ||
  window.location.origin;

function buildFileUrl(url) {
  if (!url) return "";

  if (url.startsWith("http://") || url.startsWith("https://")) {
    return url;
  }

  const base = String(API_BASE).replace(/\/$/, "");

  if (url.startsWith("/")) {
    return `${base}${url}`;
  }

  return `${base}/${url}`;
}

function esPdf(url = "") {
  return String(url).toLowerCase().includes(".pdf");
}

function esImagen(url = "") {
  const lower = String(url).toLowerCase();
  return (
    lower.includes(".jpg") ||
    lower.includes(".jpeg") ||
    lower.includes(".png") ||
    lower.includes(".webp") ||
    lower.includes(".gif")
  );
}

function formatDate(value) {
  if (!value) return "Sin fecha";

  const d = new Date(value);

  if (Number.isNaN(d.getTime())) return value;

  return d.toLocaleString("es-CO");
}

export default function EvidenciasPage() {
  const [evidencias, setEvidencias] = useState([]);
  const [mantenimientos, setMantenimientos] = useState([]);
  const [equipos, setEquipos] = useState([]);

  const [filtroTipo, setFiltroTipo] = useState("");
  const [filtroEquipo, setFiltroEquipo] = useState("");
  const [filtroMantenimiento, setFiltroMantenimiento] = useState("");
  const [busqueda, setBusqueda] = useState("");

  const [loading, setLoading] = useState(false);
  const [preview, setPreview] = useState(null);
  const [mensaje, setMensaje] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    cargarTodo();
  }, []);

  const cargarTodo = async () => {
    try {
      setLoading(true);
      setError("");
      setMensaje("");

      const [resEvidencias, resMantenimientos, resEquipos] =
        await Promise.all([
          API.get("/evidencias/"),
          API.get("/mantenimientos/"),
          API.get("/equipos/"),
        ]);

      setEvidencias(Array.isArray(resEvidencias.data) ? resEvidencias.data : []);
      setMantenimientos(
        Array.isArray(resMantenimientos.data) ? resMantenimientos.data : []
      );
      setEquipos(Array.isArray(resEquipos.data) ? resEquipos.data : []);
    } catch (err) {
      console.error("Error cargando evidencias:", err);
      setError("Error cargando evidencias.");
    } finally {
      setLoading(false);
    }
  };

  const eliminar = async (id) => {
    const ok = window.confirm("¿Eliminar evidencia?");
    if (!ok) return;

    try {
      setError("");
      await API.delete(`/evidencias/${id}`);
      setMensaje("Evidencia eliminada correctamente.");
      await cargarTodo();
    } catch (err) {
      console.error(err);
      setError("No se pudo eliminar la evidencia.");
    }
  };

  const getEquipoNombre = (equipoId) => {
    const equipo = equipos.find((e) => String(e.id) === String(equipoId));

    return (
      equipo?.nombre ||
      equipo?.codigo_id ||
      equipo?.codigo ||
      `Equipo ${equipoId || ""}`
    );
  };

  const getMantenimientoTexto = (mantenimientoId) => {
    const m = mantenimientos.find(
      (item) => String(item.id) === String(mantenimientoId)
    );

    if (!m) return mantenimientoId ? `Mantenimiento ${mantenimientoId}` : "—";

    return `#${m.id} · ${m.tipo || "Mantenimiento"} · ${
      m.estado || "Sin estado"
    }`;
  };

  const filtradas = useMemo(() => {
    return evidencias.filter((e) => {
      const texto = `
        ${e.tipo || ""}
        ${e.descripcion || ""}
        ${e.nombre_original || ""}
        ${getEquipoNombre(e.equipo_id)}
        ${getMantenimientoTexto(e.mantenimiento_id)}
      `.toLowerCase();

      const coincideTexto = texto.includes(busqueda.toLowerCase());

      const coincideTipo = filtroTipo ? e.tipo === filtroTipo : true;

      const coincideEquipo = filtroEquipo
        ? String(e.equipo_id) === String(filtroEquipo)
        : true;

      const coincideMantenimiento = filtroMantenimiento
        ? String(e.mantenimiento_id) === String(filtroMantenimiento)
        : true;

      return (
        coincideTexto &&
        coincideTipo &&
        coincideEquipo &&
        coincideMantenimiento
      );
    });
  }, [
    evidencias,
    busqueda,
    filtroTipo,
    filtroEquipo,
    filtroMantenimiento,
    equipos,
    mantenimientos,
  ]);

  return (
    <AdminLayout>
      <div className="page-header">
        <div className="page-icon">
          <Image size={26} />
        </div>

        <div>
          <h1>Evidencias</h1>
          <p>Consulta fotos, PDF y soportes asociados a equipos y mantenimientos.</p>
        </div>
      </div>

      {mensaje && <div style={styles.successAlert}>{mensaje}</div>}
      {error && <div style={styles.errorAlert}>{error}</div>}

      <section style={styles.card}>
        <div style={styles.cardHeader}>
          <div>
            <h2 style={styles.title}>Galería de evidencias</h2>
            <p style={styles.subtitle}>{filtradas.length} evidencias encontradas</p>
          </div>

          <button className="btn-secondary" onClick={cargarTodo}>
            <RefreshCcw size={16} />
            Actualizar
          </button>
        </div>

        <div style={styles.filters}>
          <div style={styles.searchBox}>
            <Search size={17} />
            <input
              placeholder="Buscar por tipo, descripción, equipo o mantenimiento..."
              value={busqueda}
              onChange={(e) => setBusqueda(e.target.value)}
              style={styles.searchInput}
            />
          </div>

          <select
            style={styles.select}
            value={filtroTipo}
            onChange={(e) => setFiltroTipo(e.target.value)}
          >
            <option value="">Todos los tipos</option>
            <option value="ANTES">Antes</option>
            <option value="DURANTE">Durante</option>
            <option value="DESPUES">Después</option>
            <option value="SOPORTE">Soporte</option>
          </select>

          <select
            style={styles.select}
            value={filtroEquipo}
            onChange={(e) => setFiltroEquipo(e.target.value)}
          >
            <option value="">Todos los equipos</option>
            {equipos.map((equipo) => (
              <option key={equipo.id} value={equipo.id}>
                {equipo.nombre || equipo.codigo_id || equipo.codigo}
              </option>
            ))}
          </select>

          <select
            style={styles.select}
            value={filtroMantenimiento}
            onChange={(e) => setFiltroMantenimiento(e.target.value)}
          >
            <option value="">Todos los mantenimientos</option>
            {mantenimientos.map((m) => (
              <option key={m.id} value={m.id}>
                #{m.id} · {m.tipo} · {m.estado}
              </option>
            ))}
          </select>
        </div>

        {loading ? (
          <div style={styles.empty}>Cargando evidencias...</div>
        ) : filtradas.length === 0 ? (
          <div style={styles.empty}>
            No hay evidencias registradas con los filtros actuales.
          </div>
        ) : (
          <div style={styles.grid}>
            {filtradas.map((e) => {
              const url = buildFileUrl(e.archivo_url);

              return (
                <div key={e.id} style={styles.evidenceCard}>
                  <div style={styles.previewBox}>
                    {esPdf(e.archivo_url) ? (
                      <div style={styles.pdfBox}>
                        <FileText size={44} />
                        <span>Documento PDF</span>
                      </div>
                    ) : esImagen(e.archivo_url) ? (
                      <img
                        src={url}
                        alt={e.nombre_original || "Evidencia"}
                        style={styles.img}
                        loading="lazy"
                        onError={(event) => {
                          event.currentTarget.style.display = "none";
                        }}
                      />
                    ) : (
                      <div style={styles.pdfBox}>
                        <FileText size={44} />
                        <span>Archivo</span>
                      </div>
                    )}
                  </div>

                  <div style={styles.info}>
                    <div style={styles.infoTop}>
                      <span style={styles.badge(e.tipo)}>{e.tipo || "SOPORTE"}</span>
                      <small>{formatDate(e.created_at)}</small>
                    </div>

                    <strong style={styles.equipo}>
                      {getEquipoNombre(e.equipo_id)}
                    </strong>

                    <small style={styles.mantenimiento}>
                      {getMantenimientoTexto(e.mantenimiento_id)}
                    </small>

                    <p style={styles.descripcion}>
                      {e.descripcion || "Sin descripción"}
                    </p>

                    <div style={styles.actions}>
                      <button
                        style={styles.viewBtn}
                        onClick={() => setPreview({ ...e, url })}
                      >
                        <Eye size={15} />
                        Ver
                      </button>

                      <a
                        href={url}
                        target="_blank"
                        rel="noreferrer"
                        style={styles.openBtn}
                      >
                        <ExternalLink size={15} />
                        Abrir
                      </a>

                      <button
                        style={styles.deleteBtn}
                        onClick={() => eliminar(e.id)}
                      >
                        <Trash2 size={15} />
                        Eliminar
                      </button>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </section>

      {preview && (
        <div style={styles.overlay}>
          <div style={styles.modal}>
            <div style={styles.modalHeader}>
              <div>
                <h2 style={styles.modalTitle}>Vista de evidencia</h2>
                <p style={styles.modalSubtitle}>
                  {preview.nombre_original || "Archivo de evidencia"}
                </p>
              </div>

              <button style={styles.closeBtn} onClick={() => setPreview(null)}>
                Cerrar
              </button>
            </div>

            {esPdf(preview.archivo_url) ? (
              <iframe
                src={preview.url}
                title="PDF Evidencia"
                style={styles.iframe}
              />
            ) : (
              <img
                src={preview.url}
                alt={preview.nombre_original || "Evidencia"}
                style={styles.bigImg}
              />
            )}
          </div>
        </div>
      )}
    </AdminLayout>
  );
}

const styles = {
  successAlert: {
    marginBottom: 16,
    padding: "12px 16px",
    borderRadius: 14,
    background: "#dcfce7",
    border: "1px solid #bbf7d0",
    color: "#166534",
    fontWeight: 800,
  },

  errorAlert: {
    marginBottom: 16,
    padding: "12px 16px",
    borderRadius: 14,
    background: "#fee2e2",
    border: "1px solid #fecaca",
    color: "#991b1b",
    fontWeight: 800,
  },

  card: {
    background: "white",
    borderRadius: 24,
    padding: 24,
    border: "1px solid #e5eef8",
    boxShadow: "0 18px 45px rgba(15, 23, 42, 0.07)",
  },

  cardHeader: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    gap: 16,
    marginBottom: 18,
    flexWrap: "wrap",
  },

  title: {
    margin: 0,
    fontSize: 22,
    fontWeight: 900,
    color: "#0f172a",
  },

  subtitle: {
    margin: "5px 0 0",
    color: "#64748b",
  },

  filters: {
    display: "grid",
    gridTemplateColumns: "1.5fr repeat(3, 1fr)",
    gap: 12,
    marginBottom: 22,
  },

  searchBox: {
    border: "1px solid #dbe5ef",
    borderRadius: 16,
    padding: "0 14px",
    display: "flex",
    alignItems: "center",
    gap: 9,
    background: "#f8fafc",
  },

  searchInput: {
    width: "100%",
    border: "none",
    outline: "none",
    background: "transparent",
    padding: "12px 0",
  },

  select: {
    border: "1px solid #dbe5ef",
    borderRadius: 16,
    padding: "12px 13px",
    background: "white",
    color: "#0f172a",
    fontWeight: 700,
  },

  empty: {
    padding: 36,
    textAlign: "center",
    background: "#f8fafc",
    borderRadius: 18,
    color: "#64748b",
  },

  grid: {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fill, minmax(260px, 1fr))",
    gap: 18,
  },

  evidenceCard: {
    background: "#f8fafc",
    border: "1px solid #e2e8f0",
    borderRadius: 20,
    overflow: "hidden",
  },

  previewBox: {
    height: 190,
    background: "white",
    borderBottom: "1px solid #e2e8f0",
  },

  img: {
    width: "100%",
    height: "100%",
    objectFit: "cover",
    display: "block",
  },

  pdfBox: {
    height: "100%",
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    justifyContent: "center",
    gap: 8,
    color: "#2563eb",
    fontWeight: 900,
  },

  info: {
    padding: 14,
    display: "flex",
    flexDirection: "column",
    gap: 7,
  },

  infoTop: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
  },

  badge: (tipo) => ({
    padding: "5px 10px",
    borderRadius: 999,
    fontSize: 11,
    fontWeight: 900,
    background:
      tipo === "ANTES"
        ? "#fef3c7"
        : tipo === "DURANTE"
        ? "#dbeafe"
        : tipo === "DESPUES"
        ? "#dcfce7"
        : "#e0e7ff",
    color:
      tipo === "ANTES"
        ? "#92400e"
        : tipo === "DURANTE"
        ? "#1d4ed8"
        : tipo === "DESPUES"
        ? "#166534"
        : "#3730a3",
  }),

  equipo: {
    color: "#0f172a",
    fontSize: 14,
  },

  mantenimiento: {
    color: "#475569",
  },

  descripcion: {
    margin: 0,
    color: "#64748b",
    fontSize: 13,
    minHeight: 34,
  },

  actions: {
    display: "grid",
    gridTemplateColumns: "1fr 1fr 1fr",
    gap: 8,
    marginTop: 6,
  },

  viewBtn: {
    border: "none",
    borderRadius: 12,
    padding: "9px 10px",
    background: "#e0f2fe",
    color: "#0369a1",
    fontWeight: 900,
    cursor: "pointer",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    gap: 6,
  },

  openBtn: {
    border: "none",
    borderRadius: 12,
    padding: "9px 10px",
    background: "#eef2ff",
    color: "#3730a3",
    fontWeight: 900,
    textDecoration: "none",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    gap: 6,
  },

  deleteBtn: {
    border: "none",
    borderRadius: 12,
    padding: "9px 10px",
    background: "#fee2e2",
    color: "#b91c1c",
    fontWeight: 900,
    cursor: "pointer",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    gap: 6,
  },

  overlay: {
    position: "fixed",
    inset: 0,
    background: "rgba(15,23,42,.55)",
    backdropFilter: "blur(5px)",
    zIndex: 999,
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    padding: 20,
  },

  modal: {
    width: "min(1000px, 96vw)",
    maxHeight: "92vh",
    background: "white",
    borderRadius: 24,
    padding: 20,
    overflow: "auto",
    boxShadow: "0 30px 80px rgba(15,23,42,.3)",
  },

  modalHeader: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    gap: 14,
    marginBottom: 14,
    flexWrap: "wrap",
  },

  modalTitle: {
    margin: 0,
    fontSize: 22,
    fontWeight: 900,
  },

  modalSubtitle: {
    margin: "5px 0 0",
    color: "#64748b",
  },

  closeBtn: {
    border: "1px solid #dbeafe",
    borderRadius: 14,
    background: "white",
    color: "#1e40af",
    padding: "10px 15px",
    fontWeight: 900,
    cursor: "pointer",
  },

  bigImg: {
    width: "100%",
    maxHeight: "75vh",
    objectFit: "contain",
    borderRadius: 18,
    background: "#f8fafc",
  },

  iframe: {
    width: "100%",
    height: "75vh",
    border: "none",
    borderRadius: 18,
    background: "#f8fafc",
  },
};