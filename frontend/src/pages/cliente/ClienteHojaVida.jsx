// ============================================================
// PÁGINA: ClienteHojaVida
// Archivo: frontend/src/pages/cliente/ClienteHojaVida.jsx
// FASE 36 — Portal Cliente FULL PRO
// Función:
// - Histórico / Hoja de vida por equipo para cliente.
// - Usa endpoint /cliente/{empresa_id}/equipos/{equipo_id}/hoja-vida.
// ============================================================

import React, { useEffect, useMemo, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import {
  ArrowLeft,
  Download,
  FileText,
  Image as ImageIcon,
  Printer,
  RefreshCcw,
  Wrench,
} from "lucide-react";

const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

export default function ClienteHojaVida() {
  const { equipoId } = useParams();
  const navigate = useNavigate();

  const [data, setData] = useState(null);
  const [tab, setTab] = useState("general");
  const [loading, setLoading] = useState(true);

  const empresaId = useMemo(() => {
    try {
      const user = JSON.parse(localStorage.getItem("user") || "{}");
      return localStorage.getItem("empresa_id") || user?.empresa_id || "";
    } catch {
      return localStorage.getItem("empresa_id") || "";
    }
  }, []);

  const getHeaders = () => {
    const token = localStorage.getItem("token") || localStorage.getItem("access_token");

    return {
      Authorization: token ? `Bearer ${token}` : "",
    };
  };

  useEffect(() => {
    cargarHojaVida();
  }, [equipoId]);

  const cargarHojaVida = async () => {
    setLoading(true);

    try {
      const res = await fetch(
        `${API_URL}/cliente/${empresaId}/equipos/${equipoId}/hoja-vida`,
        {
          headers: getHeaders(),
        }
      );

      const json = await res.json();
      setData(json);
    } catch (error) {
      console.error("Error cargando hoja de vida cliente:", error);
      setData(null);
    } finally {
      setLoading(false);
    }
  };

  const normalizarUrl = (url) => {
    if (!url) return "";

    if (url.startsWith("http://") || url.startsWith("https://")) {
      return url;
    }

    return `${API_URL}${url.startsWith("/") ? "" : "/"}${url}`;
  };

  const esImagen = (archivo) => {
    const texto = `${archivo || ""}`.toLowerCase();

    return (
      texto.includes(".jpg") ||
      texto.includes(".jpeg") ||
      texto.includes(".png") ||
      texto.includes(".webp") ||
      texto.includes(".gif")
    );
  };

  const renderInfo = (label, value) => (
    <div className="hv-info-line">
      <span>{label}</span>
      <strong>{value || "No registrado"}</strong>
    </div>
  );

  if (loading) {
    return <div className="cliente-panel">Cargando hoja de vida...</div>;
  }

  if (!data || !data.equipo) {
    return (
      <div className="cliente-panel cliente-empty-panel">
        No fue posible cargar la hoja de vida del equipo.
      </div>
    );
  }

  const { empresa, sede, equipo, hoja_vida, mantenimientos = [], evidencias = [] } = data;

  return (
    <section className="hv-pro hoja-vida-print">
      <div className="hv-actions no-print">
        <button className="cliente-btn-secondary" onClick={() => navigate(-1)}>
          <ArrowLeft size={17} />
          Volver
        </button>

        <div className="hv-actions-right">
          <button className="cliente-btn-secondary" onClick={cargarHojaVida}>
            <RefreshCcw size={17} />
            Actualizar
          </button>

          <button className="cliente-btn-secondary" onClick={() => window.print()}>
            <Printer size={17} />
            Imprimir / PDF
          </button>
        </div>
      </div>

      <div className="hv-header">
        <div className="hv-logo-box">
          {empresa?.logo_url ? (
            <img src={normalizarUrl(empresa.logo_url)} alt="Logo empresa" />
          ) : (
            <div className="hv-logo-placeholder">SGA</div>
          )}
        </div>

        <div className="hv-title">
          <h2>Hoja de Vida Técnica</h2>
          <p>{empresa?.nombre || "Empresa cliente"}</p>
          <p>{sede?.nombre || "Sede no registrada"}</p>
        </div>

        <div className="hv-code">
          <strong>{equipo?.codigo_inventario || equipo?.codigo || "HV"}</strong>
          <span>{equipo?.estado || "ACTIVO"}</span>
          <small>{equipo?.criticidad || "Criticidad no registrada"}</small>
        </div>
      </div>

      <h2 className="hv-equipo-name">
        {equipo?.nombre || equipo?.descripcion || "Equipo sin nombre"}
      </h2>

      <div className="hv-tabs no-print">
        <button
          className={tab === "general" ? "active" : ""}
          onClick={() => setTab("general")}
        >
          <FileText size={16} />
          General
        </button>

        <button
          className={tab === "historico" ? "active" : ""}
          onClick={() => setTab("historico")}
        >
          <Wrench size={16} />
          Histórico
        </button>

        <button
          className={tab === "evidencias" ? "active" : ""}
          onClick={() => setTab("evidencias")}
        >
          <ImageIcon size={16} />
          Evidencias
        </button>
      </div>

      {tab === "general" && (
        <>
          <div className="hv-section">
            <h3>Información general del equipo</h3>

            <div className="hv-section-grid">
              {renderInfo("Nombre", equipo.nombre)}
              {renderInfo("Código inventario", equipo.codigo_inventario)}
              {renderInfo("Marca", equipo.marca)}
              {renderInfo("Modelo", equipo.modelo)}
              {renderInfo("Serie", equipo.serie)}
              {renderInfo("Ubicación", equipo.ubicacion)}
              {renderInfo("Estado", equipo.estado)}
              {renderInfo("Criticidad", equipo.criticidad)}
            </div>
          </div>

          <div className="hv-section">
            <h3>Información técnica</h3>

            <div className="hv-section-grid">
              {renderInfo("Fabricante", hoja_vida?.fabricante)}
              {renderInfo("Proveedor", hoja_vida?.proveedor)}
              {renderInfo("Fecha adquisición", hoja_vida?.fecha_adquisicion)}
              {renderInfo("Fecha instalación", hoja_vida?.fecha_instalacion)}
              {renderInfo("Vida útil", hoja_vida?.vida_util)}
              {renderInfo("Capacidad", hoja_vida?.capacidad)}
              {renderInfo("Voltaje", hoja_vida?.voltaje)}
              {renderInfo("Potencia", hoja_vida?.potencia)}
              {renderInfo("Frecuencia", hoja_vida?.frecuencia)}
              {renderInfo("Garantía", hoja_vida?.garantia)}
              {renderInfo("Observaciones", hoja_vida?.observaciones)}
            </div>
          </div>
        </>
      )}

      {tab === "historico" && (
        <div className="hv-panel">
          <h2>Histórico de mantenimientos</h2>

          <div className="cliente-table-wrap">
            <table className="cliente-table">
              <thead>
                <tr>
                  <th>Fecha</th>
                  <th>Tipo</th>
                  <th>Estado</th>
                  <th>Técnico</th>
                  <th>Costo</th>
                </tr>
              </thead>

              <tbody>
                {mantenimientos.length === 0 ? (
                  <tr>
                    <td colSpan="5" className="cliente-empty-row">
                      No hay mantenimientos registrados para este equipo.
                    </td>
                  </tr>
                ) : (
                  mantenimientos.map((m) => (
                    <tr key={m.id}>
                      <td>{m.fecha_programada || m.fecha_inicio || "Sin fecha"}</td>
                      <td>{m.tipo || "No registrado"}</td>
                      <td>
                        <span className="cliente-status progress">
                          {m.estado || "Sin estado"}
                        </span>
                      </td>
                      <td>{m.tecnico_id || "No registrado"}</td>
                      <td>{m.costo || "0"}</td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {tab === "evidencias" && (
        <div className="hv-panel">
          <h2>Evidencias del equipo</h2>

          {evidencias.length === 0 ? (
            <div className="cliente-empty-panel">No hay evidencias registradas.</div>
          ) : (
            <div className="hv-doc-grid">
              {evidencias.map((ev) => {
                const archivo =
                  ev.archivo_url ||
                  ev.url ||
                  ev.ruta ||
                  ev.path ||
                  ev.archivo ||
                  ev.nombre_original ||
                  "";

                const url = normalizarUrl(archivo);

                return (
                  <a
                    href={url || "#"}
                    target="_blank"
                    rel="noreferrer"
                    className="hv-doc-card"
                    key={ev.id}
                  >
                    {esImagen(archivo) && url ? (
                      <img src={url} alt={ev.nombre_original || "Evidencia"} />
                    ) : (
                      <FileText size={42} />
                    )}

                    <strong>{ev.nombre_original || "Documento evidencia"}</strong>
                    <span>{ev.tipo || "Evidencia"}</span>

                    <div className="cliente-card-action">
                      <Download size={15} />
                      Abrir
                    </div>
                  </a>
                );
              })}
            </div>
          )}
        </div>
      )}
    </section>
  );
}