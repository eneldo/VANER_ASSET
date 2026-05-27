import AdminLayout from "./AdminLayout";
import "../../styles/multiempresa-enterprise.css";

export default function MultiempresaEnterprisePage() {

  const empresas = [
    {
      nombre: "Clínica Central",
      sedes: 3,
      equipos: 42,
      usuarios: 15,
      estado: "ACTIVA"
    },
    {
      nombre: "Hospital Norte",
      sedes: 2,
      equipos: 25,
      usuarios: 9,
      estado: "ACTIVA"
    }
  ];

  return (
    <AdminLayout>

      <div className="multiempresa-page">

        <div className="multiempresa-header">
          <h1>Multiempresa Enterprise PRO</h1>
          <p>
            Gestión SaaS empresarial, tenants y aislamiento enterprise.
          </p>
        </div>

        <div className="multiempresa-grid">

          {empresas.map((empresa, index) => (

            <div className="empresa-card" key={index}>

              <div className="empresa-top">

                <div>
                  <h3>{empresa.nombre}</h3>
                  <span>{empresa.estado}</span>
                </div>

              </div>

              <div className="empresa-body">

                <div>
                  <strong>{empresa.sedes}</strong>
                  <p>Sedes</p>
                </div>

                <div>
                  <strong>{empresa.equipos}</strong>
                  <p>Equipos</p>
                </div>

                <div>
                  <strong>{empresa.usuarios}</strong>
                  <p>Usuarios</p>
                </div>

              </div>

            </div>

          ))}

        </div>

      </div>

    </AdminLayout>
  );
}