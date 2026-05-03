// =========================================================
// DASHBOARD TÉCNICO PRO
// Pantalla principal del técnico con sidebar institucional
// =========================================================

import { useEffect, useState, useContext } from "react";
import API from "../api/axios";
import { AuthContext } from "../context/AuthContext";
import Sidebar from "../components/Sidebar";

export default function DashboardTecnico() {
  const { user, logout } = useContext(AuthContext);
  const [data, setData] = useState(null);

  useEffect(() => {
    if (user) {
      cargarDashboardTecnico();
    }
  }, [user]);

  const cargarDashboardTecnico = async () => {
    const res = await API.get(`/dashboard-tecnico/usuario/${user.usuario_id}`);
    setData(res.data);
  };

  if (!data) {
    return <p style={{ padding: 30 }}>Cargando dashboard técnico...</p>;
  }

  return (
    <div style={{ display: "flex", minHeight: "100vh", background: "#f5f8ff" }}>
      <Sidebar user={user} onLogout={logout} />

      <main style={{ flex: 1, padding: "32px" }}>
        <h1 style={{ margin: 0, color: "#172554" }}>
          Dashboard Técnico
        </h1>

        <p style={{ color: "#64748b", marginTop: 6 }}>
          Bienvenido, {data.usuario.nombre_completo}
        </p>

        <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 18, marginTop: 28 }}>
          <div className="metric-card">
            <span>Total asignados</span>
            <strong>{data.resumen.total_asignados}</strong>
          </div>

          <div className="metric-card">
            <span>Asignados</span>
            <strong>{data.resumen.asignados}</strong>
          </div>

          <div className="metric-card">
            <span>En proceso</span>
            <strong>{data.resumen.en_proceso}</strong>
          </div>
        </div>

        <section style={{ marginTop: 30 }}>
          <h2 style={{ color: "#172554" }}>Mantenimientos asignados</h2>

          {data.mantenimientos.map((m) => (
            <div key={m.mantenimiento_id} className="maintenance-card">
              <div>
                <h3>{m.equipo.nombre}</h3>
                <p>{m.empresa.nombre} - {m.sede.nombre}</p>
                <small>
                  Código: {m.equipo.codigo_id || "Sin código"} | Serie: {m.equipo.serie || "Sin serie"}
                </small>
              </div>

              <div>
                <span className="status-badge">{m.estado}</span>
                <p>{m.tipo}</p>
              </div>
            </div>
          ))}
        </section>
      </main>
    </div>
  );
}