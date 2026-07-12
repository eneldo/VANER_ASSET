// ============================================================
// BI EJECUTIVO AVANZADO PRO
// ============================================================

import { useEffect, useState } from "react";

import {
  Building2,
  Building,
  Users,
  Wrench,
  MonitorCog,
  AlertTriangle,
  DollarSign,
  Activity,
} from "lucide-react";

import {
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

import axios from "../../api/axios";

import AdminLayout from "./AdminLayout";

import "../../styles/bi-executive.css";

const COLORS = [
  "#2563eb",
  "#0ea5e9",
  "#14b8a6",
  "#22c55e",
  "#f59e0b",
  "#ef4444",
];

export default function BIExecutivePage() {

  const [kpis, setKpis] = useState({});

  const [estados, setEstados] = useState([]);

  const [empresas, setEmpresas] = useState([]);

  const [costos, setCostos] = useState([]);

  const [tecnicos, setTecnicos] = useState([]);

  const [criticos, setCriticos] = useState([]);

  // ============================================================
  // CARGAR BI
  // ============================================================

  const cargarBI = async () => {

    try {

      const [
        kpiRes,
        estadosRes,
        empresasRes,
        costosRes,
        tecnicosRes,
        criticosRes,
      ] = await Promise.all([

        axios.get("/bi-ejecutivo/kpis"),

        axios.get(
          "/bi-ejecutivo/mantenimientos-estados"
        ),

        axios.get(
          "/bi-ejecutivo/equipos-empresa"
        ),

        axios.get(
          "/bi-ejecutivo/costos-empresa"
        ),

        axios.get(
          "/bi-ejecutivo/tecnicos-productivos"
        ),

        axios.get(
          "/bi-ejecutivo/equipos-criticos"
        ),

      ]);

      setKpis(kpiRes.data);

      setEstados(estadosRes.data);

      setEmpresas(empresasRes.data);

      setCostos(costosRes.data);

      setTecnicos(tecnicosRes.data);

      setCriticos(criticosRes.data);

    } catch (error) {

      console.error(
        "Error BI Ejecutivo:",
        error
      );

    }

  };

  useEffect(() => {
    const timer = window.setTimeout(() => cargarBI(), 0);
    return () => window.clearTimeout(timer);
  }, []);

  return (

    <AdminLayout>

      <div className="bi-page">

        {/* HEADER */}

        <div className="bi-header">

          <div>

            <span className="bi-badge">
              BUSINESS INTELLIGENCE
            </span>

            <h1>
              BI Ejecutivo Avanzado PRO
            </h1>

            <p>
              Inteligencia empresarial,
              KPIs, productividad,
              costos y analítica SaaS.
            </p>

          </div>

        </div>

        {/* KPI */}

        <div className="bi-kpi-grid">

          <div className="bi-kpi-card">
            <Building2 size={22} />
            <div>
              <span>Empresas</span>
              <strong>
                {kpis.total_empresas || 0}
              </strong>
            </div>
          </div>

          <div className="bi-kpi-card">
            <Building size={22} />
            <div>
              <span>Sedes</span>
              <strong>
                {kpis.total_sedes || 0}
              </strong>
            </div>
          </div>

          <div className="bi-kpi-card">
            <MonitorCog size={22} />
            <div>
              <span>Equipos</span>
              <strong>
                {kpis.total_equipos || 0}
              </strong>
            </div>
          </div>

          <div className="bi-kpi-card">
            <Users size={22} />
            <div>
              <span>Usuarios</span>
              <strong>
                {kpis.total_usuarios || 0}
              </strong>
            </div>
          </div>

          <div className="bi-kpi-card">
            <Wrench size={22} />
            <div>
              <span>Mantenimientos</span>
              <strong>
                {kpis.total_mantenimientos || 0}
              </strong>
            </div>
          </div>

        </div>

        {/* CHARTS */}

        <div className="bi-chart-grid">

          {/* ESTADOS */}

          <div className="bi-chart-card">

            <div className="bi-chart-title">

              <Activity size={18} />

              <h3>
                Mantenimientos por Estado
              </h3>

            </div>

            <ResponsiveContainer
              width="100%"
              height={300}
            >

              <BarChart data={estados}>

                <XAxis dataKey="estado" />

                <YAxis />

                <Tooltip />

                <Bar
                  dataKey="total"
                  fill="#2563eb"
                  radius={[8, 8, 0, 0]}
                />

              </BarChart>

            </ResponsiveContainer>

          </div>

          {/* EMPRESAS */}

          <div className="bi-chart-card">

            <div className="bi-chart-title">

              <Building2 size={18} />

              <h3>
                Equipos por Empresa
              </h3>

            </div>

            <ResponsiveContainer
              width="100%"
              height={300}
            >

              <PieChart>

                <Pie
                  data={empresas}
                  dataKey="equipos"
                  nameKey="empresa"
                  outerRadius={100}
                  label
                >

                  {empresas.map(
                    (_, index) => (

                      <Cell
                        key={index}
                        fill={
                          COLORS[
                            index % COLORS.length
                          ]
                        }
                      />

                    )
                  )}

                </Pie>

                <Tooltip />

              </PieChart>

            </ResponsiveContainer>

          </div>

          {/* COSTOS */}

          <div className="bi-chart-card">

            <div className="bi-chart-title">

              <DollarSign size={18} />

              <h3>
                Costos por Empresa
              </h3>

            </div>

            <ResponsiveContainer
              width="100%"
              height={300}
            >

              <BarChart data={costos}>

                <XAxis dataKey="empresa" />

                <YAxis />

                <Tooltip />

                <Bar
                  dataKey="costo_total"
                  fill="#14b8a6"
                  radius={[8, 8, 0, 0]}
                />

              </BarChart>

            </ResponsiveContainer>

          </div>

          {/* TÉCNICOS */}

          <div className="bi-chart-card">

            <div className="bi-chart-title">

              <Users size={18} />

              <h3>
                Técnicos Productivos
              </h3>

            </div>

            <ResponsiveContainer
              width="100%"
              height={300}
            >

              <BarChart data={tecnicos}>

                <XAxis dataKey="tecnico" />

                <YAxis />

                <Tooltip />

                <Bar
                  dataKey="mantenimientos"
                  fill="#f59e0b"
                  radius={[8, 8, 0, 0]}
                />

              </BarChart>

            </ResponsiveContainer>

          </div>

        </div>

        {/* CRÍTICOS */}

        <div className="bi-table-card">

          <div className="bi-chart-title">

            <AlertTriangle size={18} />

            <h3>
              Equipos Críticos
            </h3>

          </div>

          <table className="bi-table">

            <thead>

              <tr>
                <th>Equipo</th>
                <th>Empresa</th>
                <th>Mantenimientos</th>
              </tr>

            </thead>

            <tbody>

              {criticos.map((item, index) => (

                <tr key={index}>

                  <td>{item.equipo}</td>

                  <td>{item.empresa}</td>

                  <td>
                    {item.mantenimientos}
                  </td>

                </tr>

              ))}

            </tbody>

          </table>

        </div>

      </div>

    </AdminLayout>

  );

}
