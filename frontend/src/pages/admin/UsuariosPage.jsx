// =========================================================
// PÁGINA ADMIN - USUARIOS Y PERMISOS
// Página base para usuarios, roles y accesos
// =========================================================

import AdminLayout from "./AdminLayout";
import { Users } from "lucide-react";

export default function UsuariosPage() {
  return (
    <AdminLayout>
      <div className="page-header">
        <div className="page-icon">
          <Users size={26} />
        </div>

        <div>
          <h1>Usuarios y Permisos</h1>
          <p>Crea, administra y controla los accesos del sistema.</p>
        </div>
      </div>

      <section className="page-card">
        <h2>Módulo Usuarios</h2>
        <p>
          Aquí construiremos el formulario para crear usuarios ADMIN, TÉCNICO,
          EMPRESA y COORDINADOR.
        </p>
      </section>
    </AdminLayout>
  );
}