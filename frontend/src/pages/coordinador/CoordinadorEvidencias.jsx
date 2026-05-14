/*
===========================================================
COORDINADOR — EVIDENCIAS PRO
Archivo: frontend/src/pages/coordinador/CoordinadorEvidencias.jsx
Permiso usado: EVIDENCIAS_VER
===========================================================
*/

import React, { useEffect, useMemo, useState } from "react";
import API from "../../api/axios";
import { Image, RefreshCw, Search, ExternalLink } from "lucide-react";
import "../../styles/coordinador.css";

const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

export default function CoordinadorEvidencias() {
  const [evidencias, setEvidencias] = useState([]);
  const [permisos, setPermisos] = useState([]);
  const [busqueda, setBusqueda] = useState("");
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    cargarDatos();
  }, []);

  const cargarDatos = async () => {
    try {
      setCargando(true);
      setError("");
      const [resEvidencias, resPermisos] = await Promise.all([
        API.get("/evidencias/"),
        API.get("/permisos/me"),
      ]);
      setEvidencias(resEvidencias.data || []);
      setPermisos(resPermisos.data?.permisos_finales || []);
    } catch (err) {
      console.error("Error cargando evidencias:", err);
      setError("No se pudieron cargar las evidencias.");
    } finally {
      setCargando(false);
    }
  };

  const tienePermiso = (...codigos) => codigos.some((c) => permisos.includes(c));

  const evidenciasFiltradas = useMemo(() => {
    const texto = busqueda.toLowerCase();
    return evidencias.filter((e) =>
      `${e.tipo || ""} ${e.descripcion || ""} ${e.nombre_original || ""} ${e.equipo_id || ""} ${e.mantenimiento_id || ""}`
        .toLowerCase()
        .includes(texto)
    );
  }, [evidencias, busqueda]);

  const urlArchivo = (archivoUrl) => {
    if (!archivoUrl) return "";
    if (archivoUrl.startsWith("http")) return archivoUrl;
    return `${API_URL}${archivoUrl}`;
  };

  if (!tienePermiso("EVIDENCIAS_VER")) {
    return <div className="coord-alert error">No tienes permiso para ver evidencias.</div>;
  }

  return (
    <div className="coord-page">
      <div className="coord-page-header">
        <div>
          <span className="coord-eyebrow">Evidencias</span>
          <h2>Evidencias de mantenimientos</h2>
          <p>Consulta imágenes, PDFs y soportes cargados por técnicos.</p>
        </div>
        <button className="coord-secondary-btn" onClick={cargarDatos}>
          <RefreshCw size={17} /> Actualizar
        </button>
      </div>

      {error && <div className="coord-alert error">{error}</div>}

      <div className="coord-filters">
        <div className="coord-search">
          <Search size={18} />
          <input value={busqueda} onChange={(e) => setBusqueda(e.target.value)} placeholder="Buscar por tipo, descripción o archivo..." />
        </div>
      </div>

      <div className="coord-card">
        <div className="coord-card-header">
          <div>
            <h3>Galería de evidencias</h3>
            <p>{evidenciasFiltradas.length} evidencias encontradas.</p>
          </div>
          <Image size={26} />
        </div>

        {cargando ? (
          <div className="coord-loading">Cargando evidencias...</div>
        ) : evidenciasFiltradas.length === 0 ? (
          <div className="coord-empty-card">
            <Image size={34} />
            <h3>No hay evidencias</h3>
            <p>Cuando los técnicos carguen soportes aparecerán aquí.</p>
          </div>
        ) : (
          <div className="coord-gallery-grid">
            {evidenciasFiltradas.map((ev) => {
              const url = urlArchivo(ev.archivo_url);
              const esImagen = /\.(png|jpg|jpeg|webp|gif)$/i.test(url);
              return (
                <article className="coord-evidence-card" key={ev.id}>
                  <div className="coord-evidence-preview">
                    {esImagen ? (
                      <img src={url} alt={ev.nombre_original || "Evidencia"} />
                    ) : (
                      <div className="coord-file-preview"><Image size={36} /><span>Archivo</span></div>
                    )}
                  </div>
                  <div className="coord-evidence-body">
                    <strong>{ev.tipo || "EVIDENCIA"}</strong>
                    <p>{ev.descripcion || "Sin descripción"}</p>
                    <small>{ev.nombre_original || ev.filename || "Archivo"}</small>
                    {url && (
                      <a href={url} target="_blank" rel="noreferrer" className="coord-secondary-btn">
                        <ExternalLink size={15} /> Ver archivo
                      </a>
                    )}
                  </div>
                </article>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
