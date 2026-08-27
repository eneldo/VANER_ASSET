import { fireEvent, render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it, vi } from "vitest";
import { AuthContext } from "../../context/auth-context";
import AdminLayout from "./AdminLayout";

function renderLayout(path = "/admin/dashboard") {
  return render(
    <AuthContext.Provider
      value={{
        user: { rol: "ADMIN", nombre_completo: "Admin VANER" },
        logout: vi.fn(),
      }}
    >
      <MemoryRouter initialEntries={[path]}>
        <AdminLayout>
          <div>Contenido administrativo</div>
        </AdminLayout>
      </MemoryRouter>
    </AuthContext.Provider>,
  );
}

describe("AdminLayout", () => {
  it("contrae el menu lateral y conserva la preferencia", () => {
    renderLayout();

    const toggle = screen.getByRole("button", { name: "Contraer menu lateral" });
    const sidebar = document.getElementById("sga-admin-sidebar");

    expect(sidebar).not.toHaveClass("collapsed");

    fireEvent.click(toggle);

    expect(sidebar).toHaveClass("collapsed");
    expect(
      screen.getByRole("button", { name: "Expandir menu lateral" }),
    ).toHaveAttribute("aria-expanded", "false");
    expect(localStorage.getItem("sga-admin-sidebar-collapsed")).toBe("true");
  });

  it.each([
    ["/admin/empresas", "/admin/empresas"],
    ["/admin/categorias", "/admin/categorias"],
    ["/admin/tecnicos", "/admin/tecnicos"],
  ])("muestra la hamburguesa y el enlace activo en %s", (path, href) => {
    const { container } = renderLayout(path);

    expect(
      screen.getByRole("button", { name: "Contraer menu lateral" }),
    ).toBeInTheDocument();
    expect(container.querySelector(`a[href="${href}"]`)).toHaveClass("active");
  });

  it("restaura el menu contraido al cambiar de modulo", () => {
    const firstRender = renderLayout("/admin/empresas");

    fireEvent.click(
      screen.getByRole("button", { name: "Contraer menu lateral" }),
    );
    firstRender.unmount();

    renderLayout("/admin/categorias");

    expect(document.getElementById("sga-admin-sidebar")).toHaveClass("collapsed");
    expect(
      screen.getByRole("button", { name: "Expandir menu lateral" }),
    ).toBeInTheDocument();
  });
});
