// =========================================================
// PÁGINA ADMIN - SEDES
// Página base para gestionar sedes por empresa
// =========================================================

import AdminLayout from "./AdminLayout";
import { MapPin } from "lucide-react";

export default function SedesPage() {
  return (
    <AdminLayout>
      <div className="page-header">
        <div className="page-icon">
          <MapPin size={26} />
        </div>

        <div>
          <h1>Sedes</h1>
          <p>Administra las sedes asociadas a cada empresa cliente.</p>
        </div>
      </div>

      <section className="page-card">
        <h2>Módulo Sedes</h2>
        <p>
          Aquí conectaremos el formulario para crear sedes vinculadas a una empresa.
        </p>
      </section>
    </AdminLayout>
  );
}