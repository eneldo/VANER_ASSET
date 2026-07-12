import { describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { AuthContext } from "../context/auth-context";
import ProtectedRoute from "./ProtectedRoute";
import RoleRoute from "./RoleRoute";

function renderRoutes(context, guard) {
  return render(
    <AuthContext.Provider value={context}>
      <MemoryRouter initialEntries={["/privado"]}>
        <Routes>
          <Route path="/login" element={<div>LOGIN</div>} />
          <Route path="/no-autorizado" element={<div>DENEGADO</div>} />
          <Route path="/privado" element={guard} />
        </Routes>
      </MemoryRouter>
    </AuthContext.Provider>,
  );
}

const base = { loading: false, isAuthenticated: true, user: { rol: "EMPRESA", empresa_id: "tenant-a" }, hasPermission: vi.fn(() => true) };

describe("guardas de rutas", () => {
  it("envía usuarios anónimos al login", () => {
    renderRoutes({ ...base, isAuthenticated: false }, <ProtectedRoute><div>PRIVADO</div></ProtectedRoute>);
    expect(screen.getByText("LOGIN")).toBeInTheDocument();
    expect(screen.queryByText("PRIVADO")).not.toBeInTheDocument();
  });

  it("deniega un permiso ausente", () => {
    renderRoutes({ ...base, hasPermission: vi.fn(() => false) }, <ProtectedRoute permission="facturacion"><div>PRIVADO</div></ProtectedRoute>);
    expect(screen.getByText("DENEGADO")).toBeInTheDocument();
  });

  it("deniega a un director en rutas administrativas", () => {
    renderRoutes(base, <RoleRoute roles={["ADMIN"]}><div>ADMIN</div></RoleRoute>);
    expect(screen.getByText("DENEGADO")).toBeInTheDocument();
    expect(screen.queryByText("ADMIN")).not.toBeInTheDocument();
  });

  it("permite únicamente el rol autorizado", () => {
    renderRoutes(base, <RoleRoute roles={["EMPRESA"]}><div>PORTAL CLIENTE</div></RoleRoute>);
    expect(screen.getByText("PORTAL CLIENTE")).toBeInTheDocument();
  });
});
