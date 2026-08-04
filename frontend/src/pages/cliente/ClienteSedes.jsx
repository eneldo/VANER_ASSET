// ============================================================
// CLIENTE SEDES PRO - FASE 24.1
// Portal Cliente Multiempresa SGAHolding
//
// Funciones:
// - Lista sedes de la empresa autenticada.
// - Búsqueda por nombre, ciudad, dirección o responsable.
// - Al hacer clic en una sede muestra:
//   * Detalle de sede
//   * Indicadores de la sede
//   * Equipos de esa sede
//   * Mantenimientos de esa sede
// - El cliente solo consume información de su empresa_id.
// ============================================================

import { useEffect, useMemo, useState } from "react";
import API from "../../api/axios";
import { getEmpresaId } from "../../utils/multiempresa";
import {
  MapPin,
  Search,
  Building2,
  MonitorCog,
  Wrench,
  ArrowLeft,
  RefreshCcw,
  Eye,
} from "lucide-react";

export default function ClienteSedes() {
  const [sedes, setSedes] = useState([]);
  const [busqueda, setBusqueda] = useState("");
  const [detalle, setDetalle] = useState(null);
  const [loading, setLoading] = useState(false);
  const [paginaActual, setPaginaActual] = useState(1);
  const registrosPorPagina = 9;

  // ============================================================
  // CARGA INICIAL
  // ============================================================

  useEffect(() => {
    cargarSedes();
  }, []);

  async function cargarSedes() {
    try {
      const empresaId = getEmpresaId();

      if (!empresaId) {
        alert("Este usuario no tiene empresa asociada.");
        return;
      }

      setLoading(true);

      const res = await API.get(`/cliente/${empresaId}/sedes`);
      setSedes(res.data || []);
    } catch (error) {
      console.error("Error cargando sedes cliente:", error);
      alert("No se pudieron cargar las sedes.");
    } finally {
      setLoading(false);
    }
  };

  // ============================================================
  // VER DETALLE DE SEDE
  // ============================================================

  const verDetalle = async (sede) => {
    try {
      const empresaId = getEmpresaId();

      if (!empresaId) {
        alert("Este usuario no tiene empresa asociada.");
        return;
      }

      setLoading(true);

      const res = await API.get(`/cliente/${empresaId}/sedes/${sede.id}`);
      setDetalle(res.data);
      window.scrollTo({ top: 0, behavior: "smooth" });
    } catch (error) {
      console.error("Error cargando detalle de sede:", error);
      alert("No se pudo cargar el detalle de la sede.");
    } finally {
      setLoading(false);
    }
  };

  // ============================================================
  // FILTRO DE SEDES
  // ============================================================

  const sedesFiltradas = useMemo(() => {
    const q = busqueda.toLowerCase();

    return sedes.filter((sede) => {
      const texto = `
        ${sede.nombre || ""}
        ${sede.ciudad || ""}
        ${sede.municipio || ""}
        ${sede.direccion || ""}
        ${sede.responsable || ""}
      `.toLowerCase();

      return texto.includes(q);
    });
  }, [sedes, busqueda]);

  // ============================================================
  // PAGINACIÓN
  // ============================================================

  const totalPaginas = Math.max(1, Math.ceil(sedesFiltradas.length / registrosPorPagina));
  const inicioPagina = (paginaActual - 1) * registrosPorPagina;
  const sedesActuales = sedesFiltradas.slice(inicioPagina, inicioPagina + registrosPorPagina);

  useEffect(() => {
    const timer = window.setTimeout(() => setPaginaActual(1), 0);
    return () => window.clearTimeout(timer);
  }, [busqueda]);

  // ============================================================
  // INDICADORES DE DETALLE
  // ============================================================

  const equiposDetalle = detalle?.equipos || [];
  const mantenimientosDetalle = detalle?.mantenimientos || [];

  const pendientes = mantenimientosDetalle.filter(
    (m) => !["FINALIZADO", "ANULADO"].includes(m.estado)
  ).length;

  const finalizados = mantenimientosDetalle.filter(
    (m) => m.estado === "FINALIZADO"
  ).length;

  return (
    <>
      {/* ======================================================
          HEADER PRINCIPAL
      ====================================================== */}
      <div className="cliente-header cliente-header-flex">
        <div>
          <h1>Sedes</h1>
          <p>
            Selecciona una sede para consultar su inventario, equipos y
            mantenimientos.
          </p>
        </div>

        <button className="cliente-btn-secondary" onClick={cargarSedes}>
          <RefreshCcw size={16} />
          Actualizar
        </button>
      </div>

      {/* ======================================================
          SI HAY DETALLE, MOSTRAMOS PANEL DE SEDE
      ====================================================== */}
      {detalle ? (
        <section className="cliente-panel cliente-sede-detail">
          <div className="cliente-detail-header">
            <button
              className="cliente-btn-secondary"
              onClick={() => setDetalle(null)}
            >
              <ArrowLeft size={16} />
              Volver a sedes
            </button>

            <span className="cliente-badge">Vista sede</span>
          </div>

          <div className="cliente-sede-hero">
            <div className="cliente-sede-hero-icon">
              <Building2 size={30} />
            </div>

            <div>
              <h2>{detalle.sede?.nombre || "Sede"}</h2>
              <p>{detalle.sede?.direccion || "Sin dirección registrada"}</p>
              <small>
                Ciudad/Municipio:{" "}
                {detalle.sede?.ciudad ||
                  detalle.sede?.municipio ||
                  "No registrado"}
              </small>
            </div>
          </div>

          <div className="cliente-cards cliente-cards-compact">
            <MiniCard
              title="Equipos sede"
              value={equiposDetalle.length}
              icon={<MonitorCog size={22} />}
            />
            <MiniCard
              title="Mantenimientos"
              value={mantenimientosDetalle.length}
              icon={<Wrench size={22} />}
            />
            <MiniCard title="Pendientes" value={pendientes} />
            <MiniCard title="Realizados" value={finalizados} />
          </div>

          <div className="cliente-two-columns">
            {/* ==================================================
                EQUIPOS DE LA SEDE
            ================================================== */}
            <div className="cliente-subpanel">
              <div className="cliente-subpanel-header">
                <h3>Equipos de esta sede</h3>
                <span>{equiposDetalle.length} registros</span>
              </div>

              <div className="cliente-table-scroll">
                <table className="cliente-table">
                  <thead>
                    <tr>
                      <th>Equipo</th>
                      <th>Marca</th>
                      <th>Modelo</th>
                      <th>Estado</th>
                      <th>Criticidad</th>
                    </tr>
                  </thead>

                  <tbody>
                    {equiposDetalle.map((equipo) => (
                      <tr key={equipo.id}>
                        <td>
                          <strong>{equipo.nombre || "Equipo"}</strong>
                          <br />
                          <small>{equipo.serie || "Sin serie"}</small>
                        </td>
                        <td>{equipo.marca || "—"}</td>
                        <td>{equipo.modelo || "—"}</td>
                        <td>
                          <span className="cliente-status">
                            {equipo.estado || "—"}
                          </span>
                        </td>
                        <td>
                          <span
                            className={
                              ["ALTA", "CRITICA"].includes(
                                String(equipo.criticidad || "").toUpperCase()
                              )
                                ? "cliente-status danger"
                                : "cliente-status ok"
                            }
                          >
                            {equipo.criticidad || "—"}
                          </span>
                        </td>
                      </tr>
                    ))}

                    {equiposDetalle.length === 0 && (
                      <tr>
                        <td colSpan="5" className="cliente-empty-row">
                          Esta sede no tiene equipos registrados.
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>

            {/* ==================================================
                MANTENIMIENTOS DE LA SEDE
            ================================================== */}
            <div className="cliente-subpanel">
              <div className="cliente-subpanel-header">
                <h3>Mantenimientos de esta sede</h3>
                <span>{mantenimientosDetalle.length} registros</span>
              </div>

              <div className="cliente-table-scroll">
                <table className="cliente-table">
                  <thead>
                    <tr>
                      <th>Tipo</th>
                      <th>Estado</th>
                      <th>Fecha programada</th>
                      <th>Resultado</th>
                    </tr>
                  </thead>

                  <tbody>
                    {mantenimientosDetalle.map((m) => (
                      <tr key={m.id}>
                        <td>{m.tipo || "—"}</td>
                        <td>
                          <span className={estadoClass(m.estado)}>
                            {m.estado || "—"}
                          </span>
                        </td>
                        <td>{formatDate(m.fecha_programada)}</td>
                        <td>{m.resultado_final || m.observaciones || "—"}</td>
                      </tr>
                    ))}

                    {mantenimientosDetalle.length === 0 && (
                      <tr>
                        <td colSpan="4" className="cliente-empty-row">
                          Esta sede no tiene mantenimientos registrados.
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </section>
      ) : (
        <>
          {/* ==================================================
              BUSCADOR
          ================================================== */}
          <div className="cliente-search-box">
            <Search size={17} />
            <input
              placeholder="Buscar sede, ciudad, dirección o responsable..."
              value={busqueda}
              onChange={(e) => setBusqueda(e.target.value)}
            />
          </div>

          {/* ==================================================
              GRID DE SEDES
          ================================================== */}
          {loading ? (
            <div className="cliente-panel cliente-empty-panel">
              Cargando sedes...
            </div>
          ) : (
            <div className="cliente-grid">
              {sedesActuales.map((sede) => (
                <button
                  key={sede.id}
                  className="cliente-sede-card cliente-sede-card-button"
                  onClick={() => verDetalle(sede)}
                >
                  <div className="cliente-card-top">
                    <div className="cliente-card-icon-small">
                      <MapPin size={18} />
                    </div>

                    <span className="cliente-badge">
                      {sede.ciudad || sede.municipio || "Sede"}
                    </span>
                  </div>

                  <h3>{sede.nombre || "Sede sin nombre"}</h3>

                  <p>{sede.direccion || "Sin dirección registrada"}</p>

                  <div className="cliente-sede-stats">
                    <div>
                      <span>Equipos</span>
                      <strong>{sede.total_equipos || 0}</strong>
                    </div>

                    <div>
                      <span>Mantenimientos</span>
                      <strong>{sede.total_mantenimientos || 0}</strong>
                    </div>
                  </div>

                  <div className="cliente-card-action">
                    <Eye size={15} />
                    Ver detalle de sede
                  </div>
                </button>
              ))}

              {sedesFiltradas.length === 0 && (
                <div className="cliente-panel cliente-empty-panel">
                  No se encontraron sedes para esta empresa.
                </div>
              )}
            </div>
          )}

          {!loading && sedesFiltradas.length > 0 && (
            <div className="cliente-pagination">
              <div className="cliente-pagination-info">
                Mostrando {sedesActuales.length} de {sedesFiltradas.length} sedes
              </div>

              <button
                disabled={paginaActual === 1}
                onClick={() => setPaginaActual((p) => Math.max(1, p - 1))}
              >
                ←
              </button>

              {Array.from({ length: totalPaginas }, (_, index) => (
                <button
                  key={index}
                  className={paginaActual === index + 1 ? "active" : ""}
                  onClick={() => setPaginaActual(index + 1)}
                >
                  {index + 1}
                </button>
              ))}

              <button
                disabled={paginaActual === totalPaginas}
                onClick={() => setPaginaActual((p) => Math.min(totalPaginas, p + 1))}
              >
                →
              </button>
            </div>
          )}
        </>
      )}
    </>
  );
}

// ============================================================
// COMPONENTE MINI CARD
// ============================================================

function MiniCard({ title, value, icon }) {
  return (
    <div className="cliente-card">
      <span>
        {icon} {title}
      </span>
      <strong>{value}</strong>
    </div>
  );
}

// ============================================================
// HELPERS
// ============================================================

function formatDate(value) {
  if (!value) return "—";

  const d = new Date(value);

  if (Number.isNaN(d.getTime())) return value;

  return d.toLocaleDateString();
}

function estadoClass(estado) {
  const value = String(estado || "").toUpperCase();

  if (value === "FINALIZADO") return "cliente-status ok";
  if (value === "ANULADO") return "cliente-status danger";
  if (value === "EN_PROCESO") return "cliente-status progress";
  if (value === "PAUSADO") return "cliente-status warning";

  return "cliente-status";
}
