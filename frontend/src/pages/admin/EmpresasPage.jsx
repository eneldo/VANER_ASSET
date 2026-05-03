// =========================================================
// PÁGINA ADMIN - EMPRESAS / CLIENTES
// Página base para luego conectar CRUD de empresas
// =========================================================

import AdminLayout from "./AdminLayout";
import { Building2 } from "lucide-react";

export default function EmpresasPage() {
  return (
    <AdminLayout>
      <div className="page-header">
        <div className="page-icon">
          <Building2 size={26} />
        </div>

        <div>
          <h1>Empresas / Cliente</h1>
          <p>Administra las empresas cliente del sistema.</p>
        </div>
      </div>

      <section className="page-card">
        <h2>Módulo Empresas</h2>
        <p>
          Aquí conectaremos el formulario para crear, listar, editar y eliminar empresas.
        </p>
      </section>
    </AdminLayout>
  );
}