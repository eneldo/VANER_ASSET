import { useEffect, useState } from "react";
import API from "../api/axios";
import { FileText, Eye } from "lucide-react";

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

export default function GaleriaEvidencias({ equipoId, mantenimientoId }) {
  const [evidencias, setEvidencias] = useState([]);
  const [preview, setPreview] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    cargar();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [equipoId, mantenimientoId]);

  const cargar = async () => {
    try {
      setLoading(true);

      let url = "/evidencias/";

      if (equipoId) {
        url = `/evidencias/equipo/${equipoId}`;
      }

      if (mantenimientoId) {
        url = `/evidencias/mantenimiento/${mantenimientoId}`;
      }

      const res = await API.get(url);
      setEvidencias(Array.isArray(res.data) ? res.data : []);
    } catch (error) {
      console.error("Error cargando galería:", error);
      setEvidencias([]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={styles.wrapper}>
      <h3 style={styles.title}>Galería de evidencias</h3>

      {loading ? (
        <div style={styles.empty}>Cargando evidencias...</div>
      ) : evidencias.length === 0 ? (
        <div style={styles.empty}>No hay evidencias registradas.</div>
      ) : (
        <div style={styles.grid}>
          {evidencias.map((item) => {
            const url = buildFileUrl(item.archivo_url);

            return (
              <div key={item.id} style={styles.card}>
                <div style={styles.previewBox}>
                  {esPdf(item.archivo_url) ? (
                    <div style={styles.fileBox}>
                      <FileText size={34} />
                      <span>PDF</span>
                    </div>
                  ) : esImagen(item.archivo_url) ? (
                    <img
                      src={url}
                      alt={item.nombre_original || "Evidencia"}
                      style={styles.img}
                    />
                  ) : (
                    <div style={styles.fileBox}>
                      <FileText size={34} />
                      <span>Archivo</span>
                    </div>
                  )}
                </div>

                <div style={styles.info}>
                  <strong>{item.tipo || "SOPORTE"}</strong>
                  <small>{item.nombre_original || "Archivo"}</small>

                  <button
                    type="button"
                    style={styles.button}
                    onClick={() => setPreview({ ...item, url })}
                  >
                    <Eye size={15} />
                    Ver
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {preview && (
        <div style={styles.overlay}>
          <div style={styles.modal}>
            <div style={styles.modalHeader}>
              <h3>{preview.nombre_original || "Vista de evidencia"}</h3>
              <button type="button" onClick={() => setPreview(null)}>
                Cerrar
              </button>
            </div>

            {esPdf(preview.archivo_url) ? (
              <iframe src={preview.url} title="PDF" style={styles.iframe} />
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
    </div>
  );
}

const styles = {
  wrapper: {
    width: "100%",
  },

  title: {
    margin: "0 0 14px",
    color: "#0f172a",
    fontWeight: 900,
  },

  empty: {
    padding: 20,
    borderRadius: 14,
    background: "#f8fafc",
    color: "#64748b",
    textAlign: "center",
  },

  grid: {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fill, minmax(180px, 1fr))",
    gap: 14,
  },

  card: {
    border: "1px solid #e2e8f0",
    borderRadius: 16,
    overflow: "hidden",
    background: "#ffffff",
  },

  previewBox: {
    height: 130,
    background: "#f8fafc",
  },

  img: {
    width: "100%",
    height: "100%",
    objectFit: "cover",
    display: "block",
  },

  fileBox: {
    height: "100%",
    display: "flex",
    flexDirection: "column",
    gap: 6,
    alignItems: "center",
    justifyContent: "center",
    color: "#2563eb",
    fontWeight: 900,
  },

  info: {
    padding: 10,
    display: "grid",
    gap: 6,
  },

  button: {
    border: "none",
    borderRadius: 10,
    padding: "8px 10px",
    background: "#e0f2fe",
    color: "#0369a1",
    fontWeight: 900,
    cursor: "pointer",
    display: "inline-flex",
    alignItems: "center",
    justifyContent: "center",
    gap: 6,
  },

  overlay: {
    position: "fixed",
    inset: 0,
    zIndex: 1200,
    background: "rgba(15,23,42,.6)",
    padding: 20,
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
  },

  modal: {
    width: "min(950px, 96vw)",
    maxHeight: "90vh",
    overflow: "auto",
    background: "#ffffff",
    borderRadius: 22,
    padding: 18,
  },

  modalHeader: {
    display: "flex",
    justifyContent: "space-between",
    gap: 12,
    alignItems: "center",
    marginBottom: 12,
  },

  iframe: {
    width: "100%",
    height: "72vh",
    border: "none",
    borderRadius: 14,
  },

  bigImg: {
    width: "100%",
    maxHeight: "72vh",
    objectFit: "contain",
    borderRadius: 14,
    background: "#f8fafc",
  },
};