/*
FASE 31.6 - MULTIEMPRESA SEGURA PRO
Archivo: frontend/src/pages/admin/MultiempresaAuditoriaPage.jsx

Panel visual preparado para consultar auditoría multiempresa.
Puedes conectarlo luego al endpoint /auditoria/multiempresa si ya lo tienes.
*/

import React from "react";
import AdminLayout from "../../components/AdminLayout";

export default function MultiempresaAuditoriaPage() {
  return (
    <AdminLayout>
      <section className="admin-page">
        <div className="page-header">
          <h1>Auditoría Multiempresa</h1>
          <p>
            Control de accesos por empresa, trazabilidad de consultas y seguridad SaaS.
          </p>
        </div>

        <div className="card pro-card">
          <h3>Fase 31.6 activa</h3>
          <p>
            El backend ahora debe filtrar los datos usando el <strong>empresa_id</strong>
            del token del usuario autenticado, no el valor enviado desde el frontend.
          </p>
        </div>

        <div className="card pro-card">
          <h3>Reglas SaaS recomendadas</h3>
          <ul>
            <li>ADMIN y COORDINADOR: acceso global según permisos.</li>
            <li>CLIENTE/EMPRESA: solo datos de su empresa.</li>
            <li>TÉCNICO: solo mantenimientos asignados o alcance permitido.</li>
            <li>Todo acceso sensible debe quedar auditado.</li>
          </ul>
        </div>
      </section>
    </AdminLayout>
  );
}
