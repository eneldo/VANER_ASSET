// ============================================================
// Página: Auditoría del Sistema
// Proyecto: SGA PRO
// Descripción:
// Consulta avanzada de eventos, acciones y trazabilidad.
// ============================================================

import React, { useEffect, useState } from "react";
import axios from "axios";
import { ShieldCheck, Search, RefreshCw } from "lucide-react";

import "../../styles/auditoria.css";

const API_URL = "http://127.0.0.1:8000";

export default function AuditoriaPage() {
  const [registros, setRegistros] = useState([]);
  const [filtros, setFiltros] = useState({
    usuario: "",
    modulo: "",
    accion: "",
    desde: "",
    hasta: "",
  });

  useEffect(() => {
    cargarAuditoria();
  }, []);

  const cargarAuditoria = async () => {
    try {
      const params = {};

      Object.keys(filtros).forEach((key) => {
        if (filtros[key]) params[key] = filtros[key];
      });

      const response = await axios.get(`${API_URL}/auditoria/`, { params });
      setRegistros(response.data);
    } catch (error) {
      console.error("Error cargando auditoría:", error);
    }
  };

  const limpiarFiltros = () => {
    setFiltros({
      usuario: "",
      modulo: "",
      accion: "",
      desde: "",
      hasta: "",
    });
  };

  return (
    <div className="auditoria-page">
      <div className="auditoria-header">
        <div className="auditoria-title">
          <ShieldCheck />
          <div>
            <h1>Auditoría del Sistema</h1>
            <p>Trazabilidad completa de acciones realizadas en SGA PRO.</p>
          </div>
        </div>

        <button onClick={cargarAuditoria}>
          <RefreshCw size={18} />
          Actualizar
        </button>
      </div>

      <section className="auditoria-filtros">
        <div>
          <label>Usuario</label>
          <input
            value={filtros.usuario}
            onChange={(e) =>
              setFiltros({ ...filtros, usuario: e.target.value })
            }
            placeholder="Buscar usuario"
          />
        </div>

        <div>
          <label>Módulo</label>
          <input
            value={filtros.modulo}
            onChange={(e) =>
              setFiltros({ ...filtros, modulo: e.target.value })
            }
            placeholder="Ej: Equipos"
          />
        </div>

        <div>
          <label>Acción</label>
          <input
            value={filtros.accion}
            onChange={(e) =>
              setFiltros({ ...filtros, accion: e.target.value })
            }
            placeholder="Ej: CREAR"
          />
        </div>

        <div>
          <label>Desde</label>
          <input
            type="date"
            value={filtros.desde}
            onChange={(e) =>
              setFiltros({ ...filtros, desde: e.target.value })
            }
          />
        </div>

        <div>
          <label>Hasta</label>
          <input
            type="date"
            value={filtros.hasta}
            onChange={(e) =>
              setFiltros({ ...filtros, hasta: e.target.value })
            }
          />
        </div>

        <div className="auditoria-actions">
          <button onClick={cargarAuditoria}>
            <Search size={17} />
            Buscar
          </button>

          <button className="secondary" onClick={limpiarFiltros}>
            Limpiar
          </button>
        </div>
      </section>

      <section className="auditoria-table-card">
        <div className="auditoria-table-header">
          <h2>Registros encontrados</h2>
          <span>{registros.length} eventos</span>
        </div>

        <div className="auditoria-table-wrap">
          <table>
            <thead>
              <tr>
                <th>Fecha</th>
                <th>Usuario</th>
                <th>Rol</th>
                <th>Módulo</th>
                <th>Acción</th>
                <th>Descripción</th>
                <th>IP</th>
              </tr>
            </thead>

            <tbody>
              {registros.length === 0 ? (
                <tr>
                  <td colSpan="7" className="empty">
                    No hay registros de auditoría.
                  </td>
                </tr>
              ) : (
                registros.map((item) => (
                  <tr key={item.id}>
                    <td>{new Date(item.fecha).toLocaleString()}</td>
                    <td>{item.usuario_nombre || "Sistema"}</td>
                    <td>{item.usuario_rol || "-"}</td>
                    <td>{item.modulo}</td>
                    <td>
                      <span className="auditoria-badge">{item.accion}</span>
                    </td>
                    <td>{item.descripcion || "-"}</td>
                    <td>{item.ip_origen || "-"}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}