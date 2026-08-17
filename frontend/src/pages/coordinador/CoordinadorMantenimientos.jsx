import MantenimientosPage from "../admin/MantenimientosPage";
import { useCoordinatorCompany } from "../../context/CoordinatorCompanyContext";

export default function CoordinadorMantenimientos() {
  const { empresaActivaId, empresasAutorizadas, cambiarEmpresaActiva } = useCoordinatorCompany();

  return (
    <MantenimientosPage
      mode="coordinador"
      embedded
      coordinatorCompanies={empresasAutorizadas}
      activeCompanyId={empresaActivaId}
      onCompanyChange={cambiarEmpresaActiva}
    />
  );
}
