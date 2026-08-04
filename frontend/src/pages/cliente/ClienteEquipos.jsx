// ============================================================
// CLIENTE EQUIPOS + HOJA DE VIDA NIVEL DIOS
// Portal Cliente SGA PRO
//
// Funciones:
// - Inventario completo de empresa.
// - Sede de cada equipo.
// - Hoja de vida estilo formato profesional.
// - Logo de empresa.
// - Encabezado empresa/sede/equipo.
// - Historial de mantenimientos del equipo.
// - Evidencias/documentos.
// - Imprimir / guardar como PDF.
// - Exportar CSV compatible con Excel.
// ============================================================

import { useCallback, useEffect, useMemo, useState } from "react";
import API from "../../api/axios";
import { getEmpresaId } from "../../utils/multiempresa";
import {
  FileText,
  Printer,
  Download,
  Search,
  ArrowLeft,
  ClipboardList,
  Image,
  Wrench,
} from "lucide-react";

const API_URL = import.meta.env.VITE_API_URL || "/api";

export default function ClienteEquipos() {
  const [equipos, setEquipos] = useState([]);
  const [sedes, setSedes] = useState([]);
  const [busqueda, setBusqueda] = useState("");
  const [detalle, setDetalle] = useState(null);
  const [tab, setTab] = useState("HOJA");
  const [paginaActual, setPaginaActual] = useState(1);
  const registrosPorPagina = 10;

  async function cargar() {
    const empresaId = getEmpresaId();

    if (!empresaId) {
      alert("Este usuario no tiene empresa asociada.");
      return;
    }

    const [resEquipos, resSedes] = await Promise.all([
      API.get(`/cliente/${empresaId}/equipos`),
      API.get(`/cliente/${empresaId}/sedes`),
    ]);

    setEquipos(resEquipos.data || []);
    setSedes(resSedes.data || []);
  };

  useEffect(() => {
    const timer = window.setTimeout(() => cargar(), 0);
    return () => window.clearTimeout(timer);
  }, []);

  const verHojaVida = async (equipo) => {
    const empresaId = getEmpresaId();

    const res = await API.get(
      `/cliente/${empresaId}/equipos/${equipo.id}/hoja-vida`
    );

    setDetalle(res.data);
    setTab("HOJA");
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  const nombreSede = useCallback((sedeId) => {
    return sedes.find((s) => String(s.id) === String(sedeId))?.nombre || "—";
  }, [sedes]);

  const filtrados = useMemo(() => {
    const q = busqueda.toLowerCase();

    return equipos.filter((e) => {
      const texto = `
        ${e.nombre || ""}
        ${e.marca || ""}
        ${e.modelo || ""}
        ${e.serie || ""}
        ${e.estado || ""}
        ${e.criticidad || ""}
        ${nombreSede(e.sede_id)}
      `.toLowerCase();

      return texto.includes(q);
    });
  }, [equipos, busqueda, nombreSede]);

  const totalPaginas = Math.max(1, Math.ceil(filtrados.length / registrosPorPagina));
  const inicioPagina = (paginaActual - 1) * registrosPorPagina;
  const equiposActuales = filtrados.slice(inicioPagina, inicioPagina + registrosPorPagina);

  useEffect(() => {
    const timer = window.setTimeout(() => setPaginaActual(1), 0);
    return () => window.clearTimeout(timer);
  }, [busqueda]);

  const imprimirHojaVida = () => {
    window.print();
  };

  const exportarCSV = () => {
    if (!detalle) return;

    const equipo = detalle.equipo || {};
    const hoja = detalle.hoja_vida || {};
    const empresa = detalle.empresa || {};
    const sede = detalle.sede || {};

    const filas = [
      ["SECCION", "CAMPO", "VALOR"],
      ["Empresa", "Nombre", empresa.nombre || ""],
      ["Empresa", "NIT", empresa.nit || ""],
      ["Sede", "Nombre", sede.nombre || ""],
      ["Sede", "Dirección", sede.direccion || ""],
      ["Equipo", "Nombre", equipo.nombre || ""],
      ["Equipo", "Marca", equipo.marca || ""],
      ["Equipo", "Modelo", equipo.modelo || ""],
      ["Equipo", "Serie", equipo.serie || ""],
      ["Equipo", "Estado", equipo.estado || ""],
      ["Equipo", "Criticidad", equipo.criticidad || ""],
      ...Object.entries(hoja || {}).map(([campo, valor]) => [
        "Hoja de vida",
        campo,
        valor ?? "",
      ]),
    ];

    const csv = filas
      .map((fila) =>
        fila.map((v) => `"${String(v).replaceAll('"', '""')}"`).join(";")
      )
      .join("\n");

    const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);

    const a = document.createElement("a");
    a.href = url;
    a.download = `hoja_vida_${equipo.nombre || "equipo"}.csv`;
    a.click();

    URL.revokeObjectURL(url);
  };

  return (
    <>
      <div className="cliente-header cliente-header-flex no-print">
        <div>
          <h1>Inventario y hoja de vida</h1>
          <p>
            Consulta todos los equipos de tu empresa, por sede, y revisa su hoja
            de vida técnica.
          </p>
        </div>
      </div>

      {!detalle ? (
        <>
          <div className="cliente-search-box">
            <Search size={17} />
            <input
              placeholder="Buscar equipo, sede, marca, modelo, serie, estado..."
              value={busqueda}
              onChange={(e) => setBusqueda(e.target.value)}
            />
          </div>

          <section className="cliente-panel">
            <div className="cliente-subpanel-header">
              <h3>Inventario general de la empresa</h3>
              <span>{filtrados.length} equipos</span>
            </div>

            <div className="cliente-table-scroll">
              <table className="cliente-table">
                <thead>
                  <tr>
                    <th>Equipo</th>
                    <th>Sede</th>
                    <th>Marca</th>
                    <th>Modelo</th>
                    <th>Serie</th>
                    <th>Estado</th>
                    <th>Criticidad</th>
                    <th>Acción</th>
                  </tr>
                </thead>

                <tbody>
                  {equiposActuales.map((e) => (
                    <tr key={e.id}>
                      <td>
                        <strong>{e.nombre || "Equipo"}</strong>
                        <br />
                        <small>{e.codigo_id || e.inventario || "Sin código"}</small>
                      </td>
                      <td>{nombreSede(e.sede_id)}</td>
                      <td>{e.marca || "—"}</td>
                      <td>{e.modelo || "—"}</td>
                      <td>{e.serie || "—"}</td>
                      <td>
                        <span className="cliente-status">{e.estado || "—"}</span>
                      </td>
                      <td>
                        <span
                          className={
                            ["ALTA", "CRITICA"].includes(
                              String(e.criticidad || "").toUpperCase()
                            )
                              ? "cliente-status danger"
                              : "cliente-status ok"
                          }
                        >
                          {e.criticidad || "—"}
                        </span>
                      </td>
                      <td>
                        <button
                          className="cliente-btn"
                          onClick={() => verHojaVida(e)}
                        >
                          <FileText size={15} />
                          Ver hoja de vida
                        </button>
                      </td>
                    </tr>
                  ))}

                  {filtrados.length === 0 && (
                    <tr>
                      <td colSpan="8" className="cliente-empty-row">
                        No hay equipos registrados para esta empresa.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>

            <div className="cliente-pagination no-print">
              <div className="cliente-pagination-info">
                Mostrando {equiposActuales.length} de {filtrados.length} equipos
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
          </section>
        </>
      ) : (
        <HojaVidaFullPro
          detalle={detalle}
          tab={tab}
          setTab={setTab}
          onVolver={() => setDetalle(null)}
          onPrint={imprimirHojaVida}
          onExport={exportarCSV}
        />
      )}
    </>
  );
}

function HojaVidaFullPro({ detalle, tab, setTab, onVolver, onPrint, onExport }) {
  const empresa = detalle.empresa || {};
  const sede = detalle.sede || {};
  const equipo = detalle.equipo || {};
  const hoja = detalle.hoja_vida || {};
  const mantenimientos = detalle.mantenimientos || [];
  const evidencias = detalle.evidencias || [];

  const logoUrl = getLogoUrl(empresa.logo_url);

  return (
    <section className="hv-pro hoja-vida-print">
      {/* BOTONES */}
      <div className="hv-actions no-print">
        <button className="cliente-btn-secondary" onClick={onVolver}>
          <ArrowLeft size={16} />
          Volver al inventario
        </button>

        <div className="hv-actions-right">
          <button className="cliente-btn-secondary" onClick={onPrint}>
            <Printer size={16} />
            Imprimir / PDF
          </button>

          <button className="cliente-btn" onClick={onExport}>
            <Download size={16} />
            Exportar Excel
          </button>
        </div>
      </div>

      {/* TABS */}
      <div className="hv-tabs no-print">
        <button className={tab === "HOJA" ? "active" : ""} onClick={() => setTab("HOJA")}>
          <ClipboardList size={15} />
          Hoja de vida
        </button>
        <button className={tab === "MANTENIMIENTOS" ? "active" : ""} onClick={() => setTab("MANTENIMIENTOS")}>
          <Wrench size={15} />
          Historial mantenimientos
        </button>
        <button className={tab === "DOCUMENTOS" ? "active" : ""} onClick={() => setTab("DOCUMENTOS")}>
          <Image size={15} />
          Documentos / evidencias
        </button>
      </div>

      {tab === "HOJA" && (
        <>
          {/* ENCABEZADO FORMATO */}
          <div className="hv-header">
            <div className="hv-logo-box">
              {logoUrl ? (
                <img src={logoUrl} alt="Logo empresa" />
              ) : (
                <div className="hv-logo-placeholder">SGA</div>
              )}
            </div>

            <div className="hv-title">
              <h2>HOJA DE VIDA</h2>
              <p>EMPRESA SOCIAL DEL ESTADO {empresa.nombre || ""}</p>
              <p>SEDE: {sede.nombre || "—"}</p>
            </div>

            <div className="hv-code">
              <strong>{equipo.codigo_id || equipo.inventario || "SIN CÓDIGO"}</strong>
              <span>{equipo.estado || "—"}</span>
              <small>{equipo.tipo || "Equipo"}</small>
            </div>
          </div>

          <Section title="Identificación del prestador">
            <Info label="Empresa" value={empresa.nombre} />
            <Info label="NIT" value={empresa.nit} />
            <Info label="Teléfono" value={empresa.telefono} />
            <Info label="Correo" value={empresa.email || empresa.correo} />
            <Info label="Dirección" value={empresa.direccion} />
            <Info label="Sede" value={sede.nombre} />
            <Info label="Dirección sede" value={sede.direccion} />
            <Info label="Ciudad/Municipio" value={sede.ciudad || sede.municipio} />
          </Section>

          <h1 className="hv-equipo-name">{equipo.nombre || "Equipo"}</h1>

          <Section title="Datos del equipo">
            <Info label="Marca" value={equipo.marca} />
            <Info label="Modelo" value={equipo.modelo} />
            <Info label="Serie" value={equipo.serie} />
            <Info label="Ubicación" value={equipo.ubicacion} />
            <Info label="INVIMA" value={equipo.invima} />
            <Info label="Código ID" value={equipo.codigo_id} />
            <Info label="Inventario" value={equipo.inventario} />
            <Info label="Estado" value={equipo.estado} />
            <Info label="Criticidad" value={equipo.criticidad} />
          </Section>

          <Section title="Registro histórico">
            <Info label="Adquisición" value={hoja.adquisicion} />
            <Info label="Fecha compra" value={hoja.fecha_compra} />
            <Info label="Instalación" value={hoja.fecha_instalacion} />
            <Info label="Proveedor" value={hoja.proveedor} />
            <Info label="Costo" value={hoja.costo} />
            <Info label="Vida útil" value={hoja.vida_util} />
            <Info label="País fabricación" value={hoja.pais_fabricacion} />
            <Info label="Fecha fabricación" value={hoja.fecha_fabricacion} />
          </Section>

          <Section title="Registro técnico de funcionamiento">
            <Info label="Rango voltaje" value={hoja.rango_voltaje} />
            <Info label="Rango corriente" value={hoja.rango_corriente} />
            <Info label="Rango potencia" value={hoja.rango_potencia} />
            <Info label="Frecuencia" value={hoja.frecuencia} />
            <Info label="Rango presión" value={hoja.rango_presion} />
            <Info label="Rango velocidad" value={hoja.rango_velocidad} />
            <Info label="Rango temperatura" value={hoja.rango_temperatura} />
            <Info label="Rango humedad" value={hoja.rango_humedad} />
          </Section>

          <Section title="Registro de apoyo técnico">
            <Check label="Manual operación" value={hoja.manual_operacion} />
            <Check label="Manual mantenimiento" value={hoja.manual_mantenimiento} />
            <Check label="Manual partes" value={hoja.manual_partes} />
            <Check label="Manual despiece" value={hoja.manual_despiece} />
            <Check label="Plano electrónico" value={hoja.plano_electronico} />
            <Check label="Plano eléctrico" value={hoja.plano_electrico} />
            <Check label="Plano neumático" value={hoja.plano_neumatico} />
            <Check label="Plano mecánico" value={hoja.plano_mecanico} />
            <Check label="Clasif. diagnóstico" value={hoja.clase_diagnostico} />
            <Check label="Clasif. prevención" value={hoja.clase_prevencion} />
            <Check label="Riesgo bajo" value={hoja.riesgo_bajo} />
            <Check label="Riesgo moderado" value={hoja.riesgo_moderado} />
            <Check label="Riesgo alto" value={hoja.riesgo_alto} />
            <Check label="Riesgo elevado" value={hoja.riesgo_elevado} />
          </Section>

          <Section title="Mantenimiento">
            <Info label="Periodicidad" value={hoja.periodicidad} />
            <Info label="Calibración" value={hoja.calibracion} />
            <Info label="Periodo calibración" value={hoja.periodo_calibracion} />
          </Section>
        </>
      )}

      {tab === "MANTENIMIENTOS" && (
        <div className="hv-panel">
          <h2>Historial de mantenimientos del equipo</h2>
          <table className="cliente-table">
            <thead>
              <tr>
                <th>Tipo</th>
                <th>Estado</th>
                <th>Programado</th>
                <th>Inicio</th>
                <th>Fin</th>
                <th>Resultado</th>
              </tr>
            </thead>
            <tbody>
              {mantenimientos.map((m) => (
                <tr key={m.id}>
                  <td>{m.tipo || "—"}</td>
                  <td><span className="cliente-status">{m.estado || "—"}</span></td>
                  <td>{formatDate(m.fecha_programada)}</td>
                  <td>{formatDate(m.fecha_inicio)}</td>
                  <td>{formatDate(m.fecha_fin)}</td>
                  <td>{m.resultado_final || m.observaciones || "—"}</td>
                </tr>
              ))}
              {mantenimientos.length === 0 && (
                <tr>
                  <td colSpan="6" className="cliente-empty-row">
                    Este equipo no tiene mantenimientos registrados.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      )}

      {tab === "DOCUMENTOS" && (
        <div className="hv-panel">
          <h2>Documentos y evidencias</h2>
          <div className="hv-doc-grid">
            {evidencias.map((ev) => {
              const url = getFileUrl(ev.archivo_url);
              const isPdf = String(ev.archivo_url || "").toLowerCase().includes(".pdf");

              return (
                <a key={ev.id} href={url} target="_blank" rel="noreferrer" className="hv-doc-card">
                  {isPdf ? <FileText size={34} /> : <img src={url} alt={ev.nombre_original || "Evidencia"} />}
                  <strong>{ev.tipo || "Documento"}</strong>
                  <span>{ev.nombre_original || "Archivo"}</span>
                </a>
              );
            })}

            {evidencias.length === 0 && (
              <div className="cliente-empty-row">
                Este equipo no tiene documentos o evidencias registradas.
              </div>
            )}
          </div>
        </div>
      )}
    </section>
  );
}

function Section({ title, children }) {
  return (
    <div className="hv-section">
      <h3>{title}</h3>
      <div className="hv-section-grid">{children}</div>
    </div>
  );
}

function Info({ label, value }) {
  return (
    <div className="hv-info-line">
      <span>{label}</span>
      <strong>{formatValue(value)}</strong>
    </div>
  );
}

function Check({ label, value }) {
  const checked =
    value === true ||
    value === "True" ||
    value === "true" ||
    value === "SI" ||
    value === "Sí";

  return (
    <div className="hv-check">
      <span>{checked ? "☑" : "☐"}</span>
      <strong>{label}</strong>
    </div>
  );
}

function getLogoUrl(url) {
  if (!url) return null;
  if (url.startsWith("http")) return url;
  return `${API_URL}${url}`;
}

function getFileUrl(url) {
  if (!url) return "#";
  if (url.startsWith("http")) return url;
  return `${API_URL}${url}`;
}

function formatValue(value) {
  if (value === true || value === "True" || value === "true") return "Sí";
  if (value === false || value === "False" || value === "false") return "No";
  if (value === null || value === undefined || value === "") return "—";
  return String(value);
}

function formatDate(value) {
  if (!value) return "—";
  const d = new Date(value);
  return Number.isNaN(d.getTime()) ? value : d.toLocaleString();
}
