/*
===========================================================
FASE 32 — INFORMES COORDINADOR PRO
Archivo: frontend/src/pages/coordinador/CoordinadorInformes.jsx

Funciones:
- Informe general de todos los mantenimientos
- Informe filtrado por equipo
- Resumen por estado
- Resumen por tipo
- Exportar CSV
- Imprimir / guardar PDF sin hoja en blanco
===========================================================
*/

import React, { useEffect, useMemo, useState } from "react";
import API from "../../api/axios";
import {
  FileBarChart,
  Printer,
  RefreshCw,
  Download,
  Search,
  ClipboardList,
} from "lucide-react";
import "../../styles/coordinador.css";

export default function CoordinadorInformes() {
  const [mantenimientos, setMantenimientos] = useState([]);
  const [catalogos, setCatalogos] = useState({ equipos: [], tecnicos: [] });

  const [equipoFiltro, setEquipoFiltro] = useState("");
  const [busqueda, setBusqueda] = useState("");

  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState("");

  const mostrarNombreEquipo = (equipo) => {
    if (!equipo) return "Sin equipo";

    return (
      equipo.nombre ||
      equipo.equipo_nombre ||
      equipo.codigo_inventario ||
      equipo.codigo ||
      equipo.serie ||
      `Equipo ${String(equipo.id || "").slice(0, 8)}`
    );
  };

  const obtenerNombreEquipo = (mantenimiento) => {
    if (mantenimiento.equipo_nombre) return mantenimiento.equipo_nombre;
    if (mantenimiento.nombre_equipo) return mantenimiento.nombre_equipo;
    if (mantenimiento.equipo) return mantenimiento.equipo;

    const equipo = catalogos.equipos?.find(
      (e) => String(e.id) === String(mantenimiento.equipo_id)
    );

    return mostrarNombreEquipo(equipo);
  };

  const obtenerNombreTecnico = (mantenimiento) => {
    if (mantenimiento.tecnico_nombre) return mantenimiento.tecnico_nombre;
    if (mantenimiento.nombre_tecnico) return mantenimiento.nombre_tecnico;
    if (mantenimiento.tecnico) return mantenimiento.tecnico;

    const tecnico = catalogos.tecnicos?.find(
      (t) => String(t.id) === String(mantenimiento.tecnico_id)
    );

    return (
      tecnico?.nombre_completo ||
      tecnico?.nombre ||
      tecnico?.usuario_nombre ||
      tecnico?.email ||
      tecnico?.correo ||
      `Técnico ${String(mantenimiento.tecnico_id || "").slice(0, 8)}`
    );
  };

  const cargarInformes = async () => {
    try {
      setCargando(true);
      setError("");

      const [resMantenimientos, resCatalogos] = await Promise.all([
        API.get("/coordinador/mantenimientos"),
        API.get("/coordinador/catalogos"),
      ]);

      setMantenimientos(resMantenimientos.data || []);
      setCatalogos(resCatalogos.data || { equipos: [], tecnicos: [] });
    } catch (err) {
      console.error("Error cargando informes:", err);
      setError("No se pudo cargar el informe operativo.");
    } finally {
      setCargando(false);
    }
  };

  useEffect(() => {
    cargarInformes();
  }, []);

  const mantenimientosFiltrados = useMemo(() => {
    return mantenimientos.filter((m) => {
      const coincideEquipo = equipoFiltro
        ? String(m.equipo_id) === String(equipoFiltro)
        : true;

      const texto = `
        ${obtenerNombreEquipo(m)}
        ${obtenerNombreTecnico(m)}
        ${m.tipo || ""}
        ${m.estado || ""}
        ${m.fecha_programada || ""}
        ${m.observaciones || ""}
      `.toLowerCase();

      const coincideBusqueda = texto.includes(busqueda.toLowerCase());

      return coincideEquipo && coincideBusqueda;
    });
  }, [mantenimientos, equipoFiltro, busqueda, catalogos]);

  const porEstado = useMemo(() => {
    return mantenimientosFiltrados.reduce((acc, item) => {
      const estado = item.estado || "SIN_ESTADO";
      acc[estado] = (acc[estado] || 0) + 1;
      return acc;
    }, {});
  }, [mantenimientosFiltrados]);

  const porTipo = useMemo(() => {
    return mantenimientosFiltrados.reduce((acc, item) => {
      const tipo = item.tipo || "SIN_TIPO";
      acc[tipo] = (acc[tipo] || 0) + 1;
      return acc;
    }, {});
  }, [mantenimientosFiltrados]);

  const equipoSeleccionado = useMemo(() => {
    if (!equipoFiltro) return "Todos los equipos";

    const equipo = catalogos.equipos?.find(
      (e) => String(e.id) === String(equipoFiltro)
    );

    return mostrarNombreEquipo(equipo);
  }, [equipoFiltro, catalogos]);

  const descargarCSV = () => {
    const encabezados = [
      "Equipo",
      "Técnico",
      "Tipo",
      "Estado",
      "Fecha programada",
      "Observaciones",
    ];

    const filas = mantenimientosFiltrados.map((m) => [
      obtenerNombreEquipo(m),
      obtenerNombreTecnico(m),
      m.tipo || "",
      m.estado || "",
      m.fecha_programada || "",
      m.observaciones || "",
    ]);

    const csv = [encabezados, ...filas]
      .map((fila) =>
        fila.map((valor) => `"${String(valor).replace(/"/g, '""')}"`).join(",")
      )
      .join("\n");

    const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);

    const link = document.createElement("a");
    link.href = url;
    link.download = equipoFiltro
      ? `informe_equipo_${equipoSeleccionado}.csv`
      : "informe_general_mantenimientos.csv";

    link.click();
    URL.revokeObjectURL(url);
  };

  const imprimir = () => {
    const contenido = document.getElementById("informe-coordinador-print");

    if (!contenido) {
      alert("No se encontró el contenido del informe.");
      return;
    }

    const ventana = window.open("", "_blank", "width=1100,height=800");

    if (!ventana) {
      alert("El navegador bloqueó la ventana de impresión.");
      return;
    }

    ventana.document.write(`
      <html>
        <head>
          <title>Informe Coordinador SGA PRO</title>

          <style>
            body {
              font-family: "Times New Roman", Times, serif;
              font-style: italic;
              padding: 34px;
              color: #0f172a;
              background: white;
            }

            .print-header {
              border-bottom: 3px solid #1d4ed8;
              padding-bottom: 14px;
              margin-bottom: 24px;
            }

            .print-header h1 {
              margin: 0;
              font-size: 28px;
              color: #0f172a;
            }

            .print-header p {
              margin: 5px 0 0;
              color: #475569;
              font-size: 14px;
            }

            .print-meta {
              display: grid;
              grid-template-columns: repeat(3, 1fr);
              gap: 12px;
              margin-bottom: 22px;
            }

            .print-box {
              border: 1px solid #cbd5e1;
              border-radius: 12px;
              padding: 12px;
              background: #f8fafc;
            }

            .print-box span {
              display: block;
              color: #64748b;
              font-size: 12px;
              margin-bottom: 4px;
            }

            .print-box strong {
              font-size: 18px;
              color: #0f172a;
            }

            .print-grid {
              display: grid;
              grid-template-columns: 1fr 1fr;
              gap: 18px;
              margin-bottom: 24px;
            }

            .print-card {
              border: 1px solid #cbd5e1;
              border-radius: 12px;
              padding: 16px;
            }

            .print-card h3 {
              margin: 0 0 12px;
              font-size: 18px;
            }

            .print-row {
              display: flex;
              justify-content: space-between;
              border-bottom: 1px solid #e2e8f0;
              padding: 7px 0;
              font-size: 14px;
            }

            table {
              width: 100%;
              border-collapse: collapse;
              margin-top: 18px;
              font-size: 13px;
            }

            th {
              background: #0f172a;
              color: white;
              padding: 10px;
              text-align: left;
            }

            td {
              border: 1px solid #cbd5e1;
              padding: 8px;
              vertical-align: top;
            }

            .footer {
              margin-top: 28px;
              font-size: 12px;
              color: #64748b;
              border-top: 1px solid #cbd5e1;
              padding-top: 10px;
            }

            @page {
              size: A4 landscape;
              margin: 12mm;
            }
          </style>
        </head>

        <body>
          ${contenido.innerHTML}
        </body>
      </html>
    `);

    ventana.document.close();
    ventana.focus();

    setTimeout(() => {
      ventana.print();
    }, 500);
  };

  if (cargando) {
    return <div className="coord-loading">Cargando informes operativos...</div>;
  }

  return (
    <div className="coord-page">
      <div className="coord-page-header">
        <div>
          <span className="coord-eyebrow">SGA PRO · REPORTES</span>
          <h2>Informes Operativos</h2>
          <p>
            Genera informe general de mantenimientos o informe específico por
            equipo.
          </p>
        </div>

        <div className="coord-actions">
          <button className="coord-secondary-btn" onClick={cargarInformes}>
            <RefreshCw size={17} />
            Actualizar
          </button>

          <button className="coord-secondary-btn" onClick={descargarCSV}>
            <Download size={17} />
            CSV
          </button>

          <button className="coord-primary-btn" onClick={imprimir}>
            <Printer size={17} />
            Imprimir / PDF
          </button>
        </div>
      </div>

      {error && <div className="coord-alert error">{error}</div>}

      <div className="coord-filters">
        <div className="coord-search">
          <Search size={18} />
          <input
            type="text"
            placeholder="Buscar por equipo, técnico, estado, tipo u observación..."
            value={busqueda}
            onChange={(e) => setBusqueda(e.target.value)}
          />
        </div>

        <select
          value={equipoFiltro}
          onChange={(e) => setEquipoFiltro(e.target.value)}
        >
          <option value="">Informe general: todos los equipos</option>
          {catalogos.equipos?.map((equipo) => (
            <option key={equipo.id} value={equipo.id}>
              {mostrarNombreEquipo(equipo)}
            </option>
          ))}
        </select>
      </div>

      <div id="informe-coordinador-print">
        <div className="print-header">
          <h1>Informe Coordinador SGA PRO</h1>
          <p>
            Tipo de informe:{" "}
            <strong>
              {equipoFiltro ? "Informe por equipo" : "Informe general"}
            </strong>
          </p>
          <p>
            Equipo: <strong>{equipoSeleccionado}</strong>
          </p>
          <p>
            Fecha de generación:{" "}
            <strong>{new Date().toLocaleString("es-CO")}</strong>
          </p>
        </div>

        <div className="print-meta">
          <div className="print-box">
            <span>Total mantenimientos</span>
            <strong>{mantenimientosFiltrados.length}</strong>
          </div>

          <div className="print-box">
            <span>Equipos filtrados</span>
            <strong>{equipoFiltro ? 1 : catalogos.equipos?.length || 0}</strong>
          </div>

          <div className="print-box">
            <span>Técnicos registrados</span>
            <strong>{catalogos.tecnicos?.length || 0}</strong>
          </div>
        </div>

        <div className="coord-report-grid print-grid">
          <div className="coord-card print-card">
            <div className="coord-card-header">
              <div>
                <h3>Mantenimientos por estado</h3>
                <p>Distribución operacional actual.</p>
              </div>
              <FileBarChart size={26} />
            </div>

            <div className="coord-summary-list">
              {Object.entries(porEstado).length === 0 ? (
                <p className="coord-muted">No hay datos disponibles.</p>
              ) : (
                Object.entries(porEstado).map(([estado, total]) => (
                  <div className="coord-summary-row print-row" key={estado}>
                    <span>{estado}</span>
                    <strong>{total}</strong>
                  </div>
                ))
              )}
            </div>
          </div>

          <div className="coord-card print-card">
            <div className="coord-card-header">
              <div>
                <h3>Mantenimientos por tipo</h3>
                <p>Clasificación según actividad técnica.</p>
              </div>
              <FileBarChart size={26} />
            </div>

            <div className="coord-summary-list">
              {Object.entries(porTipo).length === 0 ? (
                <p className="coord-muted">No hay datos disponibles.</p>
              ) : (
                Object.entries(porTipo).map(([tipo, total]) => (
                  <div className="coord-summary-row print-row" key={tipo}>
                    <span>{tipo}</span>
                    <strong>{total}</strong>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>

        <div className="coord-card">
          <div className="coord-card-header">
            <div>
              <h3>Detalle de mantenimientos</h3>
              <p>Listado base para auditoría y control administrativo.</p>
            </div>
            <ClipboardList size={26} />
          </div>

          <div className="coord-table-wrap">
            <table className="coord-table">
              <thead>
                <tr>
                  <th>Equipo</th>
                  <th>Técnico</th>
                  <th>Tipo</th>
                  <th>Estado</th>
                  <th>Fecha programada</th>
                  <th>Observaciones</th>
                </tr>
              </thead>

              <tbody>
                {mantenimientosFiltrados.length === 0 ? (
                  <tr>
                    <td colSpan="6" className="coord-empty">
                      No hay registros para generar informe.
                    </td>
                  </tr>
                ) : (
                  mantenimientosFiltrados.map((m) => (
                    <tr key={m.id}>
                      <td>{obtenerNombreEquipo(m)}</td>
                      <td>{obtenerNombreTecnico(m)}</td>
                      <td>{m.tipo || "Sin tipo"}</td>
                      <td>
                        <span
                          className={`coord-status ${String(
                            m.estado || ""
                          ).toLowerCase()}`}
                        >
                          {m.estado || "SIN ESTADO"}
                        </span>
                      </td>
                      <td>{m.fecha_programada || "Sin fecha"}</td>
                      <td>{m.observaciones || "Sin observaciones"}</td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>

        <div className="footer">
          Informe generado automáticamente por SGA PRO — Módulo Coordinador.
        </div>
      </div>
    </div>
  );
}