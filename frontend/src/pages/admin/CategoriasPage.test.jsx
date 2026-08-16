import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { afterEach, describe, expect, it, vi } from 'vitest';
import CategoriasPage from './CategoriasPage';


vi.mock('./AdminLayout', () => ({
  default: ({ children }) => <div>{children}</div>,
}));


function jsonResponse(data, ok = true) {
  return {
    ok,
    json: async () => data,
  };
}


afterEach(() => {
  vi.restoreAllMocks();
  vi.unstubAllGlobals();
});


describe('CategoriasPage', () => {
  it('crea una categoria desde el formulario', async () => {
    const solicitudes = [];
    vi.stubGlobal('fetch', vi.fn(async (input, options = {}) => {
      solicitudes.push({ url: String(input), options });
      if (options.method === 'POST') {
        return jsonResponse({ id: 'categoria-2', ...JSON.parse(options.body) });
      }
      return jsonResponse([]);
    }));

    render(<CategoriasPage />);

    fireEvent.change(screen.getByLabelText('Nombre de categoría'), {
      target: { name: 'nombre', value: 'Equipos biomédicos' },
    });
    fireEvent.change(screen.getByLabelText('Descripción'), {
      target: { name: 'descripcion', value: 'Tecnología clínica' },
    });
    fireEvent.click(screen.getByRole('button', { name: 'Crear categoría' }));

    await screen.findByText('Categoría creada correctamente.');
    const solicitud = solicitudes.find(({ options }) => options.method === 'POST');
    expect(solicitud.url).toBe('/api/categorias/');
    expect(JSON.parse(solicitud.options.body)).toEqual({
      code: null,
      nombre: 'Equipos biomédicos',
      descripcion: 'Tecnología clínica',
      activo: true,
    });
  });

  it('edita y elimina una categoria existente', async () => {
    let categorias = [{
      id: 'categoria-1',
      code: 'BOMBAS',
      nombre: 'Bombas',
      descripcion: 'Bombas iniciales',
      activo: true,
    }];

    vi.spyOn(window, 'scrollTo').mockImplementation(() => {});
    vi.spyOn(window, 'confirm').mockReturnValue(true);
    vi.stubGlobal('fetch', vi.fn(async (input, options = {}) => {
      const url = String(input);
      if (options.method === 'PUT') {
        categorias = [{ id: 'categoria-1', ...JSON.parse(options.body) }];
        return jsonResponse(categorias[0]);
      }
      if (options.method === 'DELETE') {
        categorias = [];
        return jsonResponse({ message: 'Categoria eliminada correctamente' });
      }
      if (url.endsWith('/categorias/')) return jsonResponse(categorias);
      throw new Error(`Solicitud inesperada: ${url}`);
    }));

    render(<CategoriasPage />);

    fireEvent.click(await screen.findByTitle('Editar'));
    fireEvent.change(screen.getByLabelText('Nombre de categoría'), {
      target: { name: 'nombre', value: 'Bombas hidráulicas' },
    });
    fireEvent.change(screen.getByLabelText('Estado'), {
      target: { name: 'activo', value: 'false' },
    });
    fireEvent.click(screen.getByRole('button', { name: 'Actualizar categoría' }));

    await screen.findByText('Categoría actualizada correctamente.');
    await waitFor(() => {
      expect(fetch).toHaveBeenCalledWith(
        '/api/categorias/categoria-1',
        expect.objectContaining({ method: 'PUT' }),
      );
    });

    fireEvent.click(await screen.findByTitle('Eliminar'));
    await screen.findByText('Categoría eliminada correctamente.');
    expect(fetch).toHaveBeenCalledWith(
      '/api/categorias/categoria-1',
      expect.objectContaining({ method: 'DELETE' }),
    );
  });
});
