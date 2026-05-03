// =========================================================
// PÁGINA ADMIN - CATEGORÍAS
// Página base para categorías de equipos
// =========================================================

import AdminLayout from "./AdminLayout";
import { Tags } from "lucide-react";

export default function CategoriasPage() {
  return (
    <AdminLayout>
      <div className="page-header">
        <div className="page-icon">
          <Tags size={26} />
        </div>

        <div>
          <h1>Categorías</h1>
          <p>Clasifica los equipos por tipo o familia técnica.</p>
        </div>
      </div>

      <section className="page-card">
        <h2>Módulo Categorías</h2>
        <p>
          Aquí conectaremos el CRUD para crear categorías como Biomédico,
          Refrigeración, CCTV, Cómputo, Redes, entre otras.
        </p>
      </section>
    </AdminLayout>
  );
}