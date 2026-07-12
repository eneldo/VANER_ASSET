// ============================================================
// PÁGINA: ClienteIndicadores
// Archivo: frontend/src/pages/cliente/ClienteIndicadores.jsx
// FASE 36 — Portal Cliente FULL PRO
// Función:
// - Indicadores ejecutivos del cliente.
// - Usa endpoint /cliente/{empresa_id}/dashboard.
// ============================================================

import { useEffect, useEffectEvent, useMemo, useState } from "react";
import {
  Activity,
  AlertTriangle,
  BarChart3,
  CheckCircle2,
  ClipboardList,
  ShieldAlert,
  Wrench,
} from "lucide-react";

import {
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Tooltip,
  BarChart,
  Bar,
  CartesianGrid,
  XAxis,
  YAxis,
  Legend,
} from "recharts";

const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

export default function ClienteIndicadores() {
  const [data, setData] = useState(null);
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

  const cargarIndicadoresAlMontar = useEffectEvent(() => cargarIndicadores());

  useEffect(() => {
    cargarIndicadoresAlMontar();
  }, []);

  async function cargarIndicadores() {
    setLoading(true);

    try {
      const res = await fetch(`${API_URL}/cliente/${empresaId}/dashboard`, {
        headers: getHeaders(),
      });

      const json = await res.json();
      setData(json);
    } catch (error) {
      console.error("Error cargando indicadores cliente:", error);
      setData(null);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="cliente-panel">Cargando indicadores ejecutivos...</div>;
  }

  if (!data || !data.kpis) {
    return (
      <div className="cliente-panel cliente-empty-panel">
        No fue posible cargar los indicadores del cliente.
      </div>
    );
  }

  const k = data.kpis;

  const indicadoresCumplimiento = [
    {
      name: "Cumplimiento",
      total: Number(k.cumplimiento || 0),
    },
    {
      name: "Pendiente",
      total: Math.max(0, 100 - Number(k.cumplimiento || 0)),
    },
  ];

  const indicadoresMantenimiento = data?.graficas?.mantenimientos || [];
  const indicadoresEquipos = data?.graficas?.equipos || [];

  return (
    <section>
      <div className="cliente-header">
        <div className="cliente-header-flex">
          <div>
            <h1>Indicadores Cliente</h1>
            <p>KPIs ejecutivos de disponibilidad, mantenimiento y cumplimiento.</p>
          </div>

          <button className="cliente-btn-secondary" onClick={cargarIndicadores}>
            <Activity size={17} />
            Actualizar
          </button>
        </div>
      </div>

      <div className="cliente-cards">
        <div className="cliente-card">
          <span>
            <Wrench size={18} />
            Total equipos
          </span>
          <strong>{k.total_equipos || 0}</strong>
        </div>

        <div className="cliente-card">
          <span>
            <CheckCircle2 size={18} />
            Equipos operativos
          </span>
          <strong>{k.equipos_operativos || 0}</strong>
        </div>

        <div className="cliente-card">
          <span>
            <ShieldAlert size={18} />
            Equipos críticos
          </span>
          <strong>{k.equipos_criticos || 0}</strong>
        </div>

        <div className="cliente-card">
          <span>
            <AlertTriangle size={18} />
            Fuera de servicio
          </span>
          <strong>{k.equipos_fuera_servicio || 0}</strong>
        </div>

        <div className="cliente-card">
          <span>
            <ClipboardList size={18} />
            Pendientes
          </span>
          <strong>{k.mantenimientos_pendientes || 0}</strong>
        </div>

        <div className="cliente-card">
          <span>
            <CheckCircle2 size={18} />
            Finalizados
          </span>
          <strong>{k.mantenimientos_finalizados || 0}</strong>
        </div>

        <div className="cliente-card">
          <span>
            <BarChart3 size={18} />
            Cumplimiento
          </span>
          <strong>{k.cumplimiento || 0}%</strong>
        </div>

        <div className="cliente-card">
          <span>
            <Activity size={18} />
            Sedes
          </span>
          <strong>{k.total_sedes || 0}</strong>
        </div>
      </div>

      <div className="cliente-two-columns">
        <div className="cliente-panel">
          <h3>Cumplimiento global</h3>

          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={indicadoresCumplimiento}
                dataKey="total"
                nameKey="name"
                outerRadius={105}
                label
              >
                <Cell fill="#2563eb" />
                <Cell fill="#e2e8f0" />
              </Pie>
              <Tooltip />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </div>

        <div className="cliente-panel">
          <h3>Mantenimientos</h3>

          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={indicadoresMantenimiento}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis allowDecimals={false} />
              <Tooltip />
              <Legend />
              <Bar dataKey="total" name="Total" fill="#06b6d4" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="cliente-panel">
        <h3>Estado de equipos</h3>

        <ResponsiveContainer width="100%" height={320}>
          <BarChart data={indicadoresEquipos}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" />
            <YAxis allowDecimals={false} />
            <Tooltip />
            <Legend />
            <Bar dataKey="total" name="Equipos" fill="#2563eb" />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </section>
  );
}
