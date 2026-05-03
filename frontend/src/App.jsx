// =========================================================
// APP PRINCIPAL SGA PRO
// Define rutas principales por rol
// =========================================================

import { BrowserRouter, Routes, Route } from "react-router-dom";
import Login from "./pages/Login";
import DashboardTecnico from "./pages/DashboardTecnico";
import DashboardAdmin from "./pages/DashboardAdmin";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Login */}
        <Route path="/" element={<Login />} />

        {/* Dashboard según rol */}
        <Route path="/admin" element={<DashboardAdmin />} />
        <Route path="/tecnico" element={<DashboardTecnico />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;