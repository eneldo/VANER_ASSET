// =========================================================
// PÁGINA ADMIN - CONFIGURACIÓN
// Página base para ajustes generales
// =========================================================

import AdminLayout from "./AdminLayout";
import { Settings } from "lucide-react";

export default function ConfiguracionPage() {
  return (
    <AdminLayout>
      <div className="page-header">
        <div className="page-icon">
          <Settings size={26} />
        </div>

        <div>
          <h1>Configuración</h1>
          <p>Ajustes generales del sistema SGA PRO.</p>
        </div>
      </div>

      <section className="page-card">
        <h2>Módulo Configuración</h2>
        <p>
          Aquí irán parámetros globales del sistema.
        </p>
      </section>
    </AdminLayout>
  );
}