import { describe, expect, it } from 'vitest';
import {
  construirPayloadFormato,
  construirPrefillFormato,
  extraerEquipoAsignado,
  obtenerMensajeErrorFormato,
} from './formatoMantenimientoUtils';


const detalle = {
  encabezado: {
    empresa_nombre: 'Hospital Central',
    sede_nombre: 'Sede Norte',
  },
  tecnico: {
    nombre_completo: 'Técnico Asignado',
  },
  mantenimiento: {
    id: 'mant-1',
    tipo: 'PREVENTIVO',
  },
  equipo_basico: {
    id: 'equipo-1',
    nombre: 'Bomba principal',
    categoria: 'Equipos industriales',
    inventario: 'INV-450',
    codigo_id: 'EQ-001',
    marca: 'Marca',
    modelo: 'Modelo',
    serie: 'SER-9',
    ubicacion: 'Cuarto de bombas',
    criticidad: 'ALTA',
    estado: 'OPERATIVO',
  },
};


describe('formatoMantenimientoUtils', () => {
  it('extrae todos los datos visibles del equipo asignado', () => {
    expect(extraerEquipoAsignado(detalle)).toMatchObject({
      nombre: 'Bomba principal',
      inventario: 'INV-450',
      codigo_id: 'EQ-001',
      serie: 'SER-9',
      ubicacion: 'Cuarto de bombas',
      empresa_nombre: 'Hospital Central',
      sede_nombre: 'Sede Norte',
      tecnico_nombre: 'Técnico Asignado',
    });
  });

  it('precarga inventario ubicacion tecnico y tipo desde la respuesta anidada', () => {
    expect(construirPrefillFormato(detalle, 'mant-1', {})).toMatchObject({
      mantenimiento_id: 'mant-1',
      numero_ot: 'mant-1',
      numero_inventario: 'INV-450',
      ubicacion: 'Cuarto de bombas',
      tecnico_nombre: 'Técnico Asignado',
      mantenimiento_tipo: 'PREVENTIVO',
      tipo_equipo: 'Bomba principal',
    });
  });

  it('normaliza fecha y tecnico vacios antes de guardar', () => {
    expect(construirPayloadFormato({
      fecha: '',
      tecnico_id: '',
      tipo_equipo: '',
      trabajos_realizados: { limpieza: true },
    }, 'mant-1', 'INDUSTRIAL_GENERAL', { titulo: 'Industrial' })).toMatchObject({
      mantenimiento_id: 'mant-1',
      fecha: null,
      tecnico_id: null,
      tipo_equipo: 'INDUSTRIAL_GENERAL',
      trabajos_realizados: {
        limpieza: true,
        _plantilla: 'INDUSTRIAL_GENERAL',
        _titulo_plantilla: 'Industrial',
      },
    });
  });

  it('muestra los errores 422 como texto legible', () => {
    const error = {
      response: {
        data: {
          detail: [{ loc: ['body', 'fecha'], msg: 'Input should be a valid date' }],
        },
      },
    };

    expect(obtenerMensajeErrorFormato(error, 'Error guardando')).toBe(
      'Fecha: Input should be a valid date',
    );
  });

  it('muestra mensajes estructurados del backend', () => {
    const error = {
      response: { data: { detail: { mensaje: 'Faltan evidencias obligatorias' } } },
    };

    expect(obtenerMensajeErrorFormato(error, 'Error guardando')).toBe(
      'Faltan evidencias obligatorias',
    );
  });
});
