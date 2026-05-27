// ============================================================
// BI EJECUTIVO PRO
// ============================================================

import { useEffect, useState } from "react";

import {
  BarChart3,
  Building2,
  Users,
  Wrench,
  MonitorCog,
  Building,
} from "lucide-react";

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from "recharts";

import axios from "../../api/axios";

import AdminLayout from "./AdminLayout";

import "../../styles/bi-executive.css";

export default function BIExecutivePage() {

  const [kpis, setKpis] = useState({});

  const [estados, setEstados] = useState([]);

  const [empresas, setEmpresas] = useState([]);

  // ============================================================
  // CARGAR BI
  // ============================================================

  const cargarBI = async () => {

    try {

      const [
        kpiRes,
        estadosRes,
        empresasRes
      ] = await Promise.all([

        axios.get("/bi-ejecutivo/kpis"),

        axios.get(
          "/bi-ejecutivo/mantenimientos-estados"
        ),

        axios.get(
          "/bi-ejecutivo/equipos-empresa"
        ),

      ]);

      setKpis(kpiRes.data);

      setEstados(estadosRes.data);

      setEmpresas(empresasRes.data);

    } catch (error) {

      console.error(
        "Error BI Ejecutivo:",
        error
      );

    }

  };

  useEffect(() => {
    cargarBI();
  }, []);

  return (

    <AdminLayout>

      <div className="bi-page">

        {/* ================================================= */}
        {/* HEADER */}
        {/* ================================================= */}

        <div className="bi-header">

          <div>

            <span className="bi-badge">
              BUSINESS INTELLIGENCE
            </span>

            <h1>
              BI Ejecutivo Enterprise
            </h1>

            <p>
              Inteligencia empresarial,
              indicadores y análisis SaaS.
            </p>

          </div>

        </div>

        {/* ================================================= */}
        {/* KPIS */}
        {/* ================================================= */}

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

        {/* ================================================= */}
        {/* CHARTS */}
        {/* ================================================= */}

        <div className="bi-chart-grid">

          {/* ============================================= */}
          {/* ESTADOS */}
          {/* ============================================= */}

          <div className="bi-chart-card">

            <div className="bi-chart-title">

              <BarChart3 size={18} />

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
                  radius={[8, 8, 0, 0]}
                />

              </BarChart>

            </ResponsiveContainer>

          </div>

          {/* ============================================= */}
          {/* EMPRESAS */}
          {/* ============================================= */}

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

                  {empresas.map((_, index) => (

                    <Cell
                      key={index}
                    />

                  ))}

                </Pie>

                <Tooltip />

              </PieChart>

            </ResponsiveContainer>

          </div>

        </div>

      </div>

    </AdminLayout>

  );

}