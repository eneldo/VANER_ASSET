// =========================================================
// PÁGINA ADMIN - EQUIPOS
// Página base para inventario de equipos
// =========================================================

import AdminLayout from "./AdminLayout";
import { MonitorCog } from "lucide-react";

export default function EquiposPage() {
  return (
    <AdminLayout>
      <div className="page-header">
        <div className="page-icon">
          <MonitorCog size={26} />
        </div>

        <div>
          <h1>Equipos</h1>
          <p>Inventario básico de equipos del sistema.</p>
        </div>
      </div>

      <section className="page-card">
        <h2>Módulo Equipos</h2>
        <p>
          Aquí irá el paso 1: creación de equipo con datos básicos.
        </p>
      </section>
    </AdminLayout>
  );
}