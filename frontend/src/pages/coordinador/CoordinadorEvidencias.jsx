/*
===========================================================
COORDINADOR — EVIDENCIAS PRO
Archivo: frontend/src/pages/coordinador/CoordinadorEvidencias.jsx
===========================================================
*/

import { useEffect, useMemo, useState } from "react";
import API from "../../api/axios";
import { RefreshCw, Search, ExternalLink, FileImage } from "lucide-react";
import "../../styles/coordinador.css";

const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

export default function CoordinadorEvidencias() {
  const [evidencias, setEvidencias] = useState([]);
  const [busqueda, setBusqueda] = useState("");
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState("");
  const [pagina, setPagina] = useState(1);

  const registrosPorPagina = 12;

  useEffect(() => {
    cargarDatos();
  }, []);

  async function cargarDatos() {
    try {
      setCargando(true);
      setError("");
      const resEvidencias = await API.get("/coordinador/evidencias");
      setEvidencias(resEvidencias.data || []);
    } catch (err) {
      console.error("Error cargando evidencias:", err);
      setError("No se pudieron cargar las evidencias.");
    } finally {
      setCargando(false);
    }
  };

  const evidenciasFiltradas = useMemo(() => {
    const texto = busqueda.toLowerCase();
    return evidencias.filter((e) =>
      `${e.tipo || ""} ${e.descripcion || ""} ${e.nombre_original || ""} ${e.equipo_nombre || ""} ${e.mantenimiento_tipo || ""}`
        .toLowerCase()
        .includes(texto)
    );
  }, [evidencias, busqueda]);

  const totalPaginas = Math.max(1, Math.ceil(evidenciasFiltradas.length / registrosPorPagina));
  const visibles = evidenciasFiltradas.slice((pagina - 1) * registrosPorPagina, pagina * registrosPorPagina);

  const urlArchivo = (archivoUrl) => {
    if (!archivoUrl) return "";
    if (archivoUrl.startsWith("http")) return archivoUrl;
    return `${API_URL}${archivoUrl}`;
  };

  const esImagen = (archivo) => /\.(png|jpg|jpeg|webp|gif)$/i.test(archivo || "");

  return (
    <div className="coord-page">
      <div className="coord-hero">
        <div>
          <span className="coord-eyebrow">SOPORTES · EVIDENCIAS</span>
          <h2>Evidencias</h2>
          <p>Consulta evidencias fotográficas y documentos asociados a mantenimientos y equipos.</p>
        </div>

        <button className="coord-btn secondary" onClick={cargarDatos}>
          <RefreshCw size={17} />
          Actualizar
        </button>
      </div>

      {error && <div className="coord-alert error">{error}</div>}

      <div className="coord-filters">
        <div className="coord-search">
          <Search size={18} />
          <input
            type="text"
            placeholder="Buscar por equipo, tipo, archivo o descripción..."
            value={busqueda}
            onChange={(e) => {
              setBusqueda(e.target.value);
              setPagina(1);
            }}
          />
        </div>
      </div>

      <div className="coord-card-grid evidencias">
        {visibles.length === 0 ? (
          <div className="coord-card">
            <p className="coord-empty">{cargando ? "Cargando evidencias..." : "No hay evidencias disponibles."}</p>
          </div>
        ) : (
          visibles.map((evidencia) => {
            const url = urlArchivo(evidencia.archivo_url);

            return (
              <article className="coord-evidencia-card" key={evidencia.id}>
                <div className="coord-evidencia-preview">
                  {esImagen(url) ? (
                    <img src={url} alt={evidencia.nombre_original || "Evidencia"} />
                  ) : (
                    <FileImage size={42} />
                  )}
                </div>

                <div className="coord-evidencia-body">
                  <span className="coord-badge blue">{evidencia.tipo || "SOPORTE"}</span>
                  <h3>{evidencia.equipo_nombre || "Equipo sin identificar"}</h3>
                  <p>{evidencia.descripcion || "Sin descripción"}</p>
                  <small>{evidencia.nombre_original || "Archivo"}</small>
                </div>

                <a className="coord-evidencia-link" href={url} target="_blank" rel="noreferrer">
                  <ExternalLink size={16} />
                  Ver archivo
                </a>
              </article>
            );
          })
        )}
      </div>

      <div className="coord-pagination">
        <button disabled={pagina <= 1} onClick={() => setPagina((p) => p - 1)}>Anterior</button>
        <span>Página {pagina} de {totalPaginas}</span>
        <button disabled={pagina >= totalPaginas} onClick={() => setPagina((p) => p + 1)}>Siguiente</button>
      </div>
    </div>
  );
}
