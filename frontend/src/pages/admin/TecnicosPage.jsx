// =========================================================
// PÁGINA ADMIN - TÉCNICOS
// Página base para técnicos del sistema
// =========================================================

import AdminLayout from "./AdminLayout";
import { UserCog } from "lucide-react";

export default function TecnicosPage() {
  return (
    <AdminLayout>
      <div className="page-header">
        <div className="page-icon">
          <UserCog size={26} />
        </div>

        <div>
          <h1>Técnicos</h1>
          <p>Administra perfiles técnicos y sus datos profesionales.</p>
        </div>
      </div>

      <section className="page-card">
        <h2>Módulo Técnicos</h2>
        <p>
          Aquí conectaremos la creación de perfil técnico vinculado a usuarios con rol TÉCNICO.
        </p>
      </section>
    </AdminLayout>
  );
}