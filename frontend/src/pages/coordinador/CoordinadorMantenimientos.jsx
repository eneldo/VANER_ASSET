// ============================================================
// PÁGINA: CoordinadorMantenimientos.jsx
// Módulo: Coordinador - Crear, editar, eliminar y filtrar mantenimientos
// ============================================================

import React, { useEffect, useMemo, useState } from "react";
import API from "../../api/axios";
import "../../styles/coordinador.css";
import { useSearchParams } from "react-router-dom";
import {
  Plus,
  Pencil,
  Trash2,
  Save,
  X,
  RefreshCw,
  Search,
  CalendarClock,
} from "lucide-react";

const ESTADOS = ["PROGRAMADO", "ASIGNADO", "EN_PROCESO", "PAUSADO", "FINALIZADO", "ANULADO"];
const TIPOS = ["PREVENTIVO", "CORRECTIVO", "PREDICTIVO", "INSPECCION"];

const formInicial = {
  id: null,
  equipo_id: "",
  tecnico_id: "",
  tipo: "PREVENTIVO",
  estado: "PROGRAMADO",
  fecha_programada: "",
  descripcion: "",
  observaciones: "",
  costo: "",
};

const fmtFecha = (fecha) => {
  if (!fecha) return "Sin fecha";
  try {
    return new Date(fecha).toLocaleDateString("es-CO");
  } catch {
    return "Sin fecha";
  }
};

const estadoClass = (estado) => `coord-badge ${String(estado || "sin").toLowerCase()}`;

export default function CoordinadorMantenimientos() {
  const [searchParams] = useSearchParams();
  const estadoURL = searchParams.get("estado") || "";

  const [mantenimientos, setMantenimientos] = useState([]);
  const [equipos, setEquipos] = useState([]);
  const [tecnicos, setTecnicos] = useState([]);
  const [form, setForm] = useState(formInicial);
  const [modalAbierto, setModalAbierto] = useState(false);
  const [modoEdicion, setModoEdicion] = useState(false);

  const [busqueda, setBusqueda] = useState("");
  const [filtroEstado, setFiltroEstado] = useState(estadoURL);
  const [filtroTecnico, setFiltroTecnico] = useState("");
  const [pagina, setPagina] = useState(1);
  const [cargando, setCargando] = useState(false);
  const [mensaje, setMensaje] = useState(null);

  const registrosPorPagina = 8;

  useEffect(() => {
    cargarDatos();
  }, []);

  useEffect(() => {
    setFiltroEstado(estadoURL);
    setPagina(1);
  }, [estadoURL]);

  const mostrarMensaje = (tipo, texto) => {
    setMensaje({ tipo, texto });
    setTimeout(() => setMensaje(null), 3500);
  };

  const cargarDatos = async () => {
    try {
      setCargando(true);
      const [resMantenimientos, resCatalogos] = await Promise.all([
        API.get("/coordinador/mantenimientos"),
        API.get("/coordinador/catalogos"),
      ]);

      setMantenimientos(resMantenimientos.data || []);
      setEquipos(resCatalogos.data?.equipos || []);
      setTecnicos(resCatalogos.data?.tecnicos || []);
    } catch (error) {
      console.error("Error cargando mantenimientos:", error);
      mostrarMensaje("error", "No se pudieron cargar los mantenimientos.");
    } finally {
      setCargando(false);
    }
  };

  const fechaParaInputDate = (fecha) => {
    if (!fecha) return "";
    return String(fecha).split("T")[0];
  };

  const abrirCrear = () => {
    setForm(formInicial);
    setModoEdicion(false);
    setModalAbierto(true);
  };

  const abrirEditar = (m) => {
    setForm({
      id: m.id,
      equipo_id: m.equipo_id || "",
      tecnico_id: m.tecnico_id || "",
      tipo: m.tipo || "PREVENTIVO",
      estado: m.estado || "PROGRAMADO",
      fecha_programada: fechaParaInputDate(m.fecha_programada),
      descripcion: m.descripcion || "",
      observaciones: m.observaciones || "",
      costo: m.costo || "",
    });
    setModoEdicion(true);
    setModalAbierto(true);
  };

  const cerrarModal = () => {
    setModalAbierto(false);
    setForm(formInicial);
    setModoEdicion(false);
  };

  const guardar = async (e) => {
    e.preventDefault();

    if (!form.equipo_id) {
      mostrarMensaje("error", "Selecciona un equipo.");
      return;
    }

    try {
      setCargando(true);

      const payload = {
        equipo_id: form.equipo_id,
        tecnico_id: form.tecnico_id || null,
        tipo: form.tipo,
        estado: form.estado,
        fecha_programada: form.fecha_programada ? `${form.fecha_programada}T08:00:00` : null,
        descripcion: form.descripcion || null,
        observaciones: form.observaciones || null,
        costo: form.costo ? Number(form.costo) : null,
      };

      if (modoEdicion && form.id) {
        await API.put(`/coordinador/mantenimientos/${form.id}`, payload);
        mostrarMensaje("success", "Mantenimiento actualizado correctamente.");
      } else {
        await API.post("/coordinador/mantenimientos", payload);
        mostrarMensaje("success", "Mantenimiento creado correctamente.");
      }

      cerrarModal();
      await cargarDatos();
    } catch (error) {
      console.error("Error guardando mantenimiento:", error);
      mostrarMensaje("error", error?.response?.data?.detail || "No se pudo guardar el mantenimiento.");
    } finally {
      setCargando(false);
    }
  };

  const eliminar = async (id) => {
    const confirmar = window.confirm("¿Seguro que deseas eliminar este mantenimiento?");
    if (!confirmar) return;

    try {
      setCargando(true);
      await API.delete(`/coordinador/mantenimientos/${id}`);
      mostrarMensaje("success", "Mantenimiento eliminado correctamente.");
      await cargarDatos();
    } catch (error) {
      console.error("Error eliminando mantenimiento:", error);
      mostrarMensaje("error", error?.response?.data?.detail || "No se pudo eliminar el mantenimiento.");
    } finally {
      setCargando(false);
    }
  };

  const cambiarEstadoRapido = async (m, estado) => {
    try {
      await API.put(`/coordinador/mantenimientos/${m.id}`, {
        equipo_id: m.equipo_id,
        tecnico_id: m.tecnico_id || null,
        tipo: m.tipo,
        estado,
        fecha_programada: m.fecha_programada || null,
        descripcion: m.descripcion || null,
        observaciones: m.observaciones || null,
      });
      mostrarMensaje("success", `Estado actualizado a ${estado}.`);
      await cargarDatos();
    } catch (error) {
      console.error("Error cambiando estado:", error);
      mostrarMensaje("error", "No se pudo cambiar el estado.");
    }
  };

  const mantenimientosFiltrados = useMemo(() => {
    const texto = busqueda.toLowerCase();

    return mantenimientos.filter((m) => {
      const coincideTexto = `${m.equipo_nombre || ""} ${m.tecnico_nombre || ""} ${m.tipo || ""} ${m.estado || ""} ${m.observaciones || ""}`
        .toLowerCase()
        .includes(texto);

      const coincideEstado = filtroEstado ? m.estado === filtroEstado : true;
      const coincideTecnico = filtroTecnico ? String(m.tecnico_id) === String(filtroTecnico) : true;

      return coincideTexto && coincideEstado && coincideTecnico;
    });
  }, [mantenimientos, busqueda, filtroEstado, filtroTecnico]);

  const totalPaginas = Math.max(1, Math.ceil(mantenimientosFiltrados.length / registrosPorPagina));
  const inicio = (pagina - 1) * registrosPorPagina;
  const visibles = mantenimientosFiltrados.slice(inicio, inicio + registrosPorPagina);

  return (
    <div className="coord-page">
      <div className="coord-hero">
        <div>
          <span className="coord-eyebrow">OPERACIÓN · MANTENIMIENTOS</span>
          <h2>Mantenimientos Coordinador</h2>
          <p>Crear, editar, eliminar, asignar técnico y controlar estados de mantenimientos.</p>
        </div>

        <div className="coord-actions">
          <button className="coord-btn secondary" onClick={cargarDatos}>
            <RefreshCw size={17} />
            Actualizar
          </button>
          <button className="coord-btn primary" onClick={abrirCrear}>
            <Plus size={17} />
            Nuevo mantenimiento
          </button>
        </div>
      </div>

      {mensaje && <div className={`coord-alert ${mensaje.tipo}`}>{mensaje.texto}</div>}

      <div className="coord-filters">
        <div className="coord-search">
          <Search size={18} />
          <input
            placeholder="Buscar por equipo, técnico, tipo, estado u observación..."
            value={busqueda}
            onChange={(e) => {
              setBusqueda(e.target.value);
              setPagina(1);
            }}
          />
        </div>

        <select value={filtroEstado} onChange={(e) => { setFiltroEstado(e.target.value); setPagina(1); }}>
          <option value="">Todos los estados</option>
          {ESTADOS.map((estado) => <option key={estado} value={estado}>{estado}</option>)}
        </select>

        <select value={filtroTecnico} onChange={(e) => { setFiltroTecnico(e.target.value); setPagina(1); }}>
          <option value="">Todos los técnicos</option>
          {tecnicos.map((t) => <option key={t.id} value={t.id}>{t.nombre || t.nombre_completo}</option>)}
        </select>
      </div>

      <section className="coord-card">
        <div className="coord-card-header">
          <div>
            <h3>Listado profesional de mantenimientos</h3>
            <p>{mantenimientosFiltrados.length} registros encontrados.</p>
          </div>
          <CalendarClock size={22} />
        </div>

        <div className="coord-table-wrap">
          <table className="coord-table">
            <thead>
              <tr>
                <th>Equipo</th>
                <th>Técnico</th>
                <th>Tipo</th>
                <th>Estado</th>
                <th>Fecha</th>
                <th>Observaciones</th>
                <th className="right">Acciones</th>
              </tr>
            </thead>
            <tbody>
              {visibles.length === 0 ? (
                <tr>
                  <td colSpan="7" className="coord-empty">No hay mantenimientos con los filtros seleccionados.</td>
                </tr>
              ) : (
                visibles.map((m) => (
                  <tr key={m.id}>
                    <td>
                      <strong>{m.equipo_nombre || "Sin equipo"}</strong>
                      <small>{m.sede_nombre || ""}</small>
                    </td>
                    <td>{m.tecnico_nombre || "Sin técnico"}</td>
                    <td>{m.tipo || "N/A"}</td>
                    <td>
                      <select
                        className="coord-status-select"
                        value={m.estado || "PROGRAMADO"}
                        onChange={(e) => cambiarEstadoRapido(m, e.target.value)}
                      >
                        {ESTADOS.map((estado) => <option key={estado} value={estado}>{estado}</option>)}
                      </select>
                    </td>
                    <td>{fmtFecha(m.fecha_programada)}</td>
                    <td>{m.observaciones || m.descripcion || "Sin observaciones"}</td>
                    <td className="coord-row-actions">
                      <button title="Editar" onClick={() => abrirEditar(m)}><Pencil size={16} /></button>
                      <button title="Eliminar" className="danger" onClick={() => eliminar(m.id)}><Trash2 size={16} /></button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        <div className="coord-pagination">
          <button disabled={pagina <= 1} onClick={() => setPagina((p) => p - 1)}>Anterior</button>
          <span>Página {pagina} de {totalPaginas}</span>
          <button disabled={pagina >= totalPaginas} onClick={() => setPagina((p) => p + 1)}>Siguiente</button>
        </div>
      </section>

      {modalAbierto && (
        <div className="coord-modal-backdrop">
          <div className="coord-modal large">
            <div className="coord-modal-header">
              <div>
                <h3>{modoEdicion ? "Editar mantenimiento" : "Nuevo mantenimiento"}</h3>
                <p>Formulario operativo del coordinador.</p>
              </div>
              <button onClick={cerrarModal}><X size={18} /></button>
            </div>

            <form onSubmit={guardar} className="coord-form-grid">
              <label>
                Equipo
                <select value={form.equipo_id} onChange={(e) => setForm({ ...form, equipo_id: e.target.value })} required>
                  <option value="">Seleccionar equipo</option>
                  {equipos.map((eq) => (
                    <option key={eq.id} value={eq.id}>
                      {eq.nombre || eq.codigo_inventario || eq.serie}
                    </option>
                  ))}
                </select>
              </label>

              <label>
                Técnico
                <select value={form.tecnico_id} onChange={(e) => setForm({ ...form, tecnico_id: e.target.value })}>
                  <option value="">Sin técnico</option>
                  {tecnicos.map((t) => (
                    <option key={t.id} value={t.id}>{t.nombre || t.nombre_completo}</option>
                  ))}
                </select>
              </label>

              <label>
                Tipo
                <select value={form.tipo} onChange={(e) => setForm({ ...form, tipo: e.target.value })}>
                  {TIPOS.map((tipo) => <option key={tipo} value={tipo}>{tipo}</option>)}
                </select>
              </label>

              <label>
                Estado
                <select value={form.estado} onChange={(e) => setForm({ ...form, estado: e.target.value })}>
                  {ESTADOS.map((estado) => <option key={estado} value={estado}>{estado}</option>)}
                </select>
              </label>

              <label>
                Fecha programada
                <input type="date" value={form.fecha_programada} onChange={(e) => setForm({ ...form, fecha_programada: e.target.value })} />
              </label>

              <label>
                Costo
                <input type="number" min="0" step="0.01" value={form.costo} onChange={(e) => setForm({ ...form, costo: e.target.value })} />
              </label>

              <label className="span-2">
                Descripción
                <textarea rows="3" value={form.descripcion} onChange={(e) => setForm({ ...form, descripcion: e.target.value })} />
              </label>

              <label className="span-2">
                Observaciones
                <textarea rows="3" value={form.observaciones} onChange={(e) => setForm({ ...form, observaciones: e.target.value })} />
              </label>

              <div className="coord-modal-actions span-2">
                <button type="button" className="coord-btn secondary" onClick={cerrarModal}>
                  <X size={17} />
                  Cancelar
                </button>
                <button type="submit" className="coord-btn primary" disabled={cargando}>
                  <Save size={17} />
                  Guardar
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
