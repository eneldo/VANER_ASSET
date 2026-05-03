// =========================================================
// PÁGINA ADMIN - MANTENIMIENTOS
// Página base para gestión de mantenimientos
// =========================================================

import AdminLayout from "./AdminLayout";
import { Wrench } from "lucide-react";

export default function MantenimientosPage() {
  return (
    <AdminLayout>
      <div className="page-header">
        <div className="page-icon">
          <Wrench size={26} />
        </div>

        <div>
          <h1>Mantenimientos</h1>
          <p>Programa, asigna y consulta mantenimientos.</p>
        </div>
      </div>

      <section className="page-card">
        <h2>Módulo Mantenimientos</h2>
        <p>
          Aquí conectaremos programación de mantenimiento y asignación de técnicos.
        </p>
      </section>
    </AdminLayout>
  );
}