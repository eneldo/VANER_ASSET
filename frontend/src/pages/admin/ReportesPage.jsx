// =========================================================
// PÁGINA ADMIN - REPORTES
// Página base para reportes del sistema
// =========================================================

import AdminLayout from "./AdminLayout";
import { FileText } from "lucide-react";

export default function ReportesPage() {
  return (
    <AdminLayout>
      <div className="page-header">
        <div className="page-icon">
          <FileText size={26} />
        </div>

        <div>
          <h1>Reportes</h1>
          <p>Genera reportes de inventario, mantenimiento y evidencias.</p>
        </div>
      </div>

      <section className="page-card">
        <h2>Módulo Reportes</h2>
        <p>
          Aquí construiremos reportes PDF y vistas resumidas del sistema.
        </p>
      </section>
    </AdminLayout>
  );
}