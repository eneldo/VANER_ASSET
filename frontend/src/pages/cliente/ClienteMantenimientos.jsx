// ============================================================
// MANTENIMIENTOS CLIENTE PRO - FASE 24.2
// Consulta mantenimientos de la empresa cliente.
//
// Funciones:
// - Lee filtro desde URL:
//   /cliente/mantenimientos?estado=PENDIENTES
//   /cliente/mantenimientos?estado=REALIZADOS
// - Permite alternar Todos / Pendientes / Realizados.
// - Muestra badges profesionales por estado.
// ============================================================

import { useEffect, useMemo, useState } from "react";
import API from "../../api/axios";
import { getEmpresaId } from "./ClienteLayout";
import { RefreshCcw, Wrench } from "lucide-react";

export default function ClienteMantenimientos() {
  const params = new URLSearchParams(window.location.search);
  const filtroInicial = params.get("estado") || "TODOS";

  const [mantenimientos, setMantenimientos] = useState([]);
  const [filtro, setFiltro] = useState(filtroInicial);

  useEffect(() => {
    cargar();
  }, []);

  const cargar = async () => {
    const empresaId = getEmpresaId();

    if (!empresaId) {
      alert("Este usuario no tiene empresa asociada.");
      return;
    }

    const res = await API.get(`/cliente/${empresaId}/mantenimientos`);
    setMantenimientos(res.data || []);
  };

  const filtrados = useMemo(() => {
    if (filtro === "PENDIENTES") {
      return mantenimientos.filter(
        (m) => !["FINALIZADO", "ANULADO"].includes(String(m.estado).toUpperCase())
      );
    }

    if (filtro === "REALIZADOS") {
      return mantenimientos.filter(
        (m) => String(m.estado).toUpperCase() === "FINALIZADO"
      );
    }

    return mantenimientos;
  }, [mantenimientos, filtro]);

  return (
    <>
      <div className="cliente-header cliente-header-flex">
        <div>
          <h1>Mantenimientos</h1>
          <p>Consulta mantenimientos pendientes y realizados de tus equipos.</p>
        </div>

        <button className="cliente-btn-secondary" onClick={cargar}>
          <RefreshCcw size={16} />
          Actualizar
        </button>
      </div>

      <div style={{ display: "flex", gap: 10, marginBottom: 18, flexWrap: "wrap" }}>
        <button
          className={filtro === "TODOS" ? "cliente-btn" : "cliente-btn-secondary"}
          onClick={() => setFiltro("TODOS")}
        >
          Todos
        </button>

        <button
          className={
            filtro === "PENDIENTES" ? "cliente-btn" : "cliente-btn-secondary"
          }
          onClick={() => setFiltro("PENDIENTES")}
        >
          Pendientes
        </button>

        <button
          className={
            filtro === "REALIZADOS" ? "cliente-btn" : "cliente-btn-secondary"
          }
          onClick={() => setFiltro("REALIZADOS")}
        >
          Realizados
        </button>
      </div>

      <section className="cliente-panel">
        <div className="cliente-subpanel-header">
          <h3>
            <Wrench size={18} /> Historial de mantenimientos
          </h3>
          <span>{filtrados.length} registros</span>
        </div>

        <div className="cliente-table-wrap">
          <table className="cliente-table">
            <thead>
              <tr>
                <th>Tipo</th>
                <th>Estado</th>
                <th>Fecha programada</th>
                <th>Inicio</th>
                <th>Fin</th>
                <th>Resultado / Observación</th>
              </tr>
            </thead>

            <tbody>
              {filtrados.map((m) => (
                <tr key={m.id}>
                  <td>{m.tipo || "—"}</td>

                  <td>
                    <span className={estadoClass(m.estado)}>
                      {m.estado || "—"}
                    </span>
                  </td>

                  <td>{formatDate(m.fecha_programada)}</td>
                  <td>{formatDate(m.fecha_inicio)}</td>
                  <td>{formatDate(m.fecha_fin)}</td>
                  <td>
                    {m.resultado_final ||
                      m.observacion_estado ||
                      m.observaciones ||
                      "—"}
                  </td>
                </tr>
              ))}

              {filtrados.length === 0 && (
                <tr>
                  <td colSpan="6" className="cliente-empty-row">
                    No hay mantenimientos para mostrar.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </section>
    </>
  );
}

function formatDate(value) {
  if (!value) return "—";

  const d = new Date(value);

  if (Number.isNaN(d.getTime())) return value;

  return d.toLocaleString();
}

function estadoClass(estado) {
  const value = String(estado || "").toUpperCase();

  if (value === "FINALIZADO") return "cliente-status ok";
  if (value === "ANULADO") return "cliente-status danger";
  if (value === "EN_PROCESO") return "cliente-status progress";
  if (value === "PAUSADO") return "cliente-status warning";
  if (value === "ASIGNADO") return "cliente-status";
  if (value === "PROGRAMADO") return "cliente-status";

  return "cliente-status";
}