// ============================================================
// DASHBOARD CLIENTE INTELIGENTE - SGA PRO
// Cards dinámicas: sedes, equipos, pendientes y realizados.
// ============================================================

import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import API from "../../api/axios";
import { getEmpresaId } from "./ClienteLayout";
import { MapPin, MonitorCog, Clock, CheckCircle } from "lucide-react";

export default function ClienteDashboard() {
  const navigate = useNavigate();
  const [data, setData] = useState(null);

  useEffect(() => {
    cargar();
  }, []);

  const cargar = async () => {
    const empresaId = getEmpresaId();

    if (!empresaId) {
      alert("Este usuario no tiene empresa asociada.");
      return;
    }

    const res = await API.get(`/cliente/${empresaId}/dashboard`);
    setData(res.data);
  };

  return (
    <>
      <div className="cliente-header">
        <h1>Dashboard Cliente</h1>
        <p>Resumen general de tus sedes, equipos y mantenimientos.</p>
      </div>

      <section className="cliente-cards">
        <Card
          title="Sedes"
          value={data?.total_sedes || 0}
          icon={<MapPin />}
          onClick={() => navigate("/cliente/sedes")}
        />

        <Card
          title="Inventario / Equipos"
          value={data?.total_equipos || 0}
          icon={<MonitorCog />}
          onClick={() => navigate("/cliente/equipos")}
        />

        <Card
          title="Pendientes"
          value={data?.mantenimientos_pendientes || 0}
          icon={<Clock />}
          onClick={() => navigate("/cliente/mantenimientos?estado=PENDIENTES")}
        />

        <Card
          title="Realizados"
          value={data?.mantenimientos_realizados || 0}
          icon={<CheckCircle />}
          onClick={() => navigate("/cliente/mantenimientos?estado=REALIZADOS")}
        />
      </section>

      <section className="cliente-panel">
        <h2>Accesos rápidos</h2>
        <p>
          Selecciona una tarjeta superior para consultar sedes, inventario,
          mantenimientos pendientes o realizados.
        </p>
      </section>
    </>
  );
}

function Card({ title, value, icon, onClick }) {
  return (
    <button className="cliente-card cliente-card-click" onClick={onClick}>
      <span>
        {icon}
        {title}
      </span>
      <strong>{value}</strong>
    </button>
  );
}