// =========================================================
// PÁGINA ADMIN - EVIDENCIAS
// Página base para revisar evidencias fotográficas
// =========================================================

import AdminLayout from "./AdminLayout";
import { Image } from "lucide-react";

export default function EvidenciasPage() {
  return (
    <AdminLayout>
      <div className="page-header">
        <div className="page-icon">
          <Image size={26} />
        </div>

        <div>
          <h1>Evidencias</h1>
          <p>Consulta evidencias antes, durante y después del mantenimiento.</p>
        </div>
      </div>

      <section className="page-card">
        <h2>Módulo Evidencias</h2>
        <p>
          Aquí se visualizarán las evidencias cargadas por los técnicos.
        </p>
      </section>
    </AdminLayout>
  );
}