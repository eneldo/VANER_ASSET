// ============================================================
// PÁGINA: CoordinadorMantenimientos.jsx
// Ruta: frontend/src/pages/coordinador/CoordinadorMantenimientos.jsx
// Módulo: Coordinador - Gestión de Mantenimientos PRO
// ============================================================

import React, { useEffect, useMemo, useState } from "react";
import API from "../../api/axios";
import "../../styles/coordinador.css";
import { useSearchParams } from "react-router-dom";

const ESTADOS = [
  "PROGRAMADO",
  "ASIGNADO",
  "EN_PROCESO",
  "PAUSADO",
  "FINALIZADO",
  "ANULADO",
];

const TIPOS = ["PREVENTIVO", "CORRECTIVO", "PREDICTIVO", "INSPECCION"];

const formInicial = {
  id: null,
  equipo_id: "",
  tecnico_id: "",
  tipo: "PREVENTIVO",
  estado: "PROGRAMADO",
  fecha_programada: "",
  observaciones: "",
};

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
  useEffect(() => {
  setFiltroEstado(estadoURL);
  setPagina(1);
}, [estadoURL]);

  const [filtroTecnico, setFiltroTecnico] = useState("");
  const [pagina, setPagina] = useState(1);
  const [cargando, setCargando] = useState(false);
  const [mensaje, setMensaje] = useState(null);

  const registrosPorPagina = 8;
  // Convierte fecha ISO a formato válido para input type="date"
  const fechaParaInputDate = (fecha) => {
    if (!fecha) return "";
    return String(fecha).split("T")[0];
  };

  // Nombre definitivo del técnico para selects, filtros y tabla
  const mostrarNombreTecnico = (tecnico) => {
    if (!tecnico) return "Sin técnico";

    return (
      tecnico.nombre_completo ||
      tecnico.nombre ||
      tecnico.usuario_nombre ||
      tecnico.email ||
      tecnico.correo ||
      tecnico.username ||
      `Técnico ${String(tecnico.id || "").slice(0, 8)}`
    );
  };

  const mostrarNombreEquipo = (equipo) => {
    if (!equipo) return "Sin equipo";

    return (
      equipo.nombre ||
      equipo.equipo_nombre ||
      equipo.codigo_inventario ||
      equipo.codigo ||
      equipo.serie ||
      `Equipo ${String(equipo.id || "").slice(0, 8)}`
    );
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

  useEffect(() => {
    cargarDatos();
  }, []);

  const mostrarMensaje = (tipo, texto) => {
    setMensaje({ tipo, texto });

    setTimeout(() => {
      setMensaje(null);
    }, 3500);
  };

  const obtenerNombreTecnico = (mantenimiento) => {
    if (mantenimiento.tecnico_nombre) return mantenimiento.tecnico_nombre;
    if (mantenimiento.nombre_tecnico) return mantenimiento.nombre_tecnico;

    const tecnico = tecnicos.find(
      (t) => String(t.id) === String(mantenimiento.tecnico_id)
    );

    return mostrarNombreTecnico(tecnico);
  };

  const obtenerNombreEquipo = (mantenimiento) => {
    if (mantenimiento.equipo_nombre) return mantenimiento.equipo_nombre;
    if (mantenimiento.nombre_equipo) return mantenimiento.nombre_equipo;

    const equipo = equipos.find(
      (e) => String(e.id) === String(mantenimiento.equipo_id)
    );

    return mostrarNombreEquipo(equipo);
  };

  const mantenimientosFiltrados = useMemo(() => {
    return mantenimientos.filter((m) => {
      const texto = `
        ${obtenerNombreEquipo(m)}
        ${obtenerNombreTecnico(m)}
        ${m.tipo || ""}
        ${m.estado || ""}
        ${m.observaciones || ""}
      `.toLowerCase();

      const coincideBusqueda = texto.includes(busqueda.toLowerCase());

      const coincideEstado = filtroEstado
        ? String(m.estado) === String(filtroEstado)
        : true;

      const coincideTecnico = filtroTecnico
        ? String(m.tecnico_id) === String(filtroTecnico)
        : true;

      return coincideBusqueda && coincideEstado && coincideTecnico;
    });
  }, [mantenimientos, busqueda, filtroEstado, filtroTecnico, tecnicos, equipos]);

  const totalPaginas = Math.ceil(
    mantenimientosFiltrados.length / registrosPorPagina
  );

  const mantenimientosPaginados = mantenimientosFiltrados.slice(
    (pagina - 1) * registrosPorPagina,
    pagina * registrosPorPagina
  );

  const abrirCrear = () => {
    setModoEdicion(false);
    setForm(formInicial);
    setModalAbierto(true);
  };

  const abrirEditar = (mantenimiento) => {
    setModoEdicion(true);

    setForm({
      id: mantenimiento.id,
      equipo_id: mantenimiento.equipo_id || "",
      tecnico_id: mantenimiento.tecnico_id || "",
      tipo: mantenimiento.tipo || "PREVENTIVO",
      estado: mantenimiento.estado || "PROGRAMADO",
      fecha_programada: fechaParaInputDate(mantenimiento.fecha_programada),
      observaciones: mantenimiento.observaciones || "",
    });

    setModalAbierto(true);
  };

  const cerrarModal = () => {
    setModalAbierto(false);
    setModoEdicion(false);
    setForm(formInicial);
  };

  const handleChange = (e) => {
    const { name, value } = e.target;

    setForm((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const guardarMantenimiento = async (e) => {
    e.preventDefault();

    if (!form.equipo_id) {
      mostrarMensaje("error", "Debes seleccionar un equipo.");
      return;
    }

    if (!form.tecnico_id) {
      mostrarMensaje("error", "Debes seleccionar un técnico.");
      return;
    }

    try {
      const payload = {
        equipo_id: form.equipo_id,
        tecnico_id: form.tecnico_id,
        tipo: form.tipo,
        estado: form.estado,
        fecha_programada: form.fecha_programada || null,
        observaciones: form.observaciones,
      };

      if (modoEdicion) {
        await API.put(`/coordinador/mantenimientos/${form.id}`, payload);

        mostrarMensaje("success", "Mantenimiento actualizado correctamente.");
      } else {
        await API.post("/coordinador/mantenimientos", payload);

        mostrarMensaje("success", "Mantenimiento asignado correctamente.");
      }

      cerrarModal();
      cargarDatos();
    } catch (error) {
      console.error("Error guardando mantenimiento:", error);
      mostrarMensaje("error", "No se pudo guardar el mantenimiento.");
    }
  };

  const eliminarMantenimiento = async (id) => {
    const confirmar = window.confirm(
      "¿Seguro que deseas eliminar o anular este mantenimiento?"
    );

    if (!confirmar) return;

    try {
      await API.delete(`/coordinador/mantenimientos/${id}`);

      mostrarMensaje("success", "Mantenimiento eliminado correctamente.");
      cargarDatos();
    } catch (error) {
      console.error("Error eliminando mantenimiento:", error);
      mostrarMensaje("error", "No se pudo eliminar el mantenimiento.");
    }
  };

  const cambiarEstadoRapido = async (mantenimiento, nuevoEstado) => {
    try {
      await API.put(`/coordinador/mantenimientos/${mantenimiento.id}`, {
        equipo_id: mantenimiento.equipo_id,
        tecnico_id: mantenimiento.tecnico_id,
        tipo: mantenimiento.tipo,
        estado: nuevoEstado,
        fecha_programada: mantenimiento.fecha_programada,
        observaciones: mantenimiento.observaciones,
      });

      mostrarMensaje("success", `Estado cambiado a ${nuevoEstado}.`);
      cargarDatos();
    } catch (error) {
      console.error("Error cambiando estado:", error);
      mostrarMensaje("error", "No se pudo cambiar el estado.");
    }
  };

  const claseEstado = (estado) => {
    const normalizado = String(estado || "").toLowerCase();
    return `estado-badge estado-${normalizado}`;
  };

  return (
    <div className="coordinador-page">
      <div className="coordinador-header">
        <div>
          <p className="coordinador-subtitle">Panel Coordinador</p>
          <h1>Gestión de Mantenimientos</h1>
          <p className="coordinador-description">
            Asigna técnicos, edita mantenimientos y controla el estado operativo.
          </p>
        </div>

        <button className="btn-primary-pro" onClick={abrirCrear}>
          + Asignar nuevo
        </button>
      </div>

      {mensaje && (
        <div className={`alert-pro alert-${mensaje.tipo}`}>
          {mensaje.texto}
        </div>
      )}

      <div className="coordinador-kpis">
        <div className="kpi-card">
          <span>Total</span>
          <strong>{mantenimientos.length}</strong>
        </div>

        <div className="kpi-card">
          <span>Asignados</span>
          <strong>
            {mantenimientos.filter((m) => m.estado === "ASIGNADO").length}
          </strong>
        </div>

        <div className="kpi-card">
          <span>En proceso</span>
          <strong>
            {mantenimientos.filter((m) => m.estado === "EN_PROCESO").length}
          </strong>
        </div>

        <div className="kpi-card">
          <span>Finalizados</span>
          <strong>
            {mantenimientos.filter((m) => m.estado === "FINALIZADO").length}
          </strong>
        </div>
      </div>

      <div className="coordinador-panel">
        <div className="coordinador-filtros">
          <input
            type="text"
            placeholder="Buscar por equipo, técnico, tipo o estado..."
            value={busqueda}
            onChange={(e) => {
              setBusqueda(e.target.value);
              setPagina(1);
            }}
          />

          <select
            value={filtroEstado}
            onChange={(e) => {
              setFiltroEstado(e.target.value);
              setPagina(1);
            }}
          >
            <option value="">Todos los estados</option>
            {ESTADOS.map((estado) => (
              <option key={estado} value={estado}>
                {estado}
              </option>
            ))}
          </select>

          <select
            value={filtroTecnico}
            onChange={(e) => {
              setFiltroTecnico(e.target.value);
              setPagina(1);
            }}
          >
            <option value="">Todos los técnicos</option>
            {tecnicos.map((tecnico) => (
              <option key={tecnico.id} value={tecnico.id}>
                {mostrarNombreTecnico(tecnico)}
              </option>
            ))}
          </select>
        </div>

        <div className="tabla-wrapper-pro">
          {cargando ? (
            <div className="loading-pro">Cargando mantenimientos...</div>
          ) : (
            <table className="tabla-coordinador">
              <thead>
                <tr>
                  <th>Equipo</th>
                  <th>Técnico</th>
                  <th>Tipo</th>
                  <th>Estado</th>
                  <th>Fecha programada</th>
                  <th>Observaciones</th>
                  <th>Acciones</th>
                </tr>
              </thead>

              <tbody>
                {mantenimientosPaginados.length === 0 ? (
                  <tr>
                    <td colSpan="7" className="empty-table">
                      No hay mantenimientos para mostrar.
                    </td>
                  </tr>
                ) : (
                  mantenimientosPaginados.map((m) => (
                    <tr key={m.id}>
                      <td>
                        <strong>{obtenerNombreEquipo(m)}</strong>
                      </td>

                      <td>
                        <span className="tecnico-pill">
                          {obtenerNombreTecnico(m)}
                        </span>
                      </td>

                      <td>{m.tipo || "Sin tipo"}</td>

                      <td>
                        <select
                          className={claseEstado(m.estado)}
                          value={m.estado || "PROGRAMADO"}
                          onChange={(e) =>
                            cambiarEstadoRapido(m, e.target.value)
                          }
                        >
                          {ESTADOS.map((estado) => (
                            <option key={estado} value={estado}>
                              {estado}
                            </option>
                          ))}
                        </select>
                      </td>

                      <td>{m.fecha_programada || "Sin fecha"}</td>

                      <td className="observacion-cell">
                        {m.observaciones || "Sin observaciones"}
                      </td>

                      <td>
                        <div className="acciones-tabla">
                          <button
                            className="btn-table btn-edit"
                            onClick={() => abrirEditar(m)}
                          >
                            Editar
                          </button>

                          <button
                            className="btn-table btn-delete"
                            onClick={() => eliminarMantenimiento(m.id)}
                          >
                            Eliminar
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          )}
        </div>

        <div className="paginacion-pro">
          <button
            disabled={pagina === 1}
            onClick={() => setPagina((prev) => prev - 1)}
          >
            Anterior
          </button>

          <span>
            Página {pagina} de {totalPaginas || 1}
          </span>

          <button
            disabled={pagina === totalPaginas || totalPaginas === 0}
            onClick={() => setPagina((prev) => prev + 1)}
          >
            Siguiente
          </button>
        </div>
      </div>

      {modalAbierto && (
        <div className="modal-overlay-pro">
          <div className="modal-pro">
            <div className="modal-header-pro">
              <div>
                <h2>
                  {modoEdicion
                    ? "Editar mantenimiento"
                    : "Asignar nuevo mantenimiento"}
                </h2>
                <p>
                  Selecciona equipo, técnico responsable, tipo y estado del
                  mantenimiento.
                </p>
              </div>

              <button className="modal-close" onClick={cerrarModal}>
                ×
              </button>
            </div>

            <form className="form-pro" onSubmit={guardarMantenimiento}>
              <div className="form-grid">
                <div className="form-group">
                  <label>Equipo</label>
                  <select
                    name="equipo_id"
                    value={form.equipo_id}
                    onChange={handleChange}
                    required
                  >
                    <option value="">Seleccionar equipo</option>
                    {equipos.map((equipo) => (
                      <option key={equipo.id} value={equipo.id}>
                        {mostrarNombreEquipo(equipo)}
                      </option>
                    ))}
                  </select>
                </div>

                <div className="form-group">
                  <label>Técnico</label>
                  <select
                    name="tecnico_id"
                    value={form.tecnico_id}
                    onChange={handleChange}
                    required
                  >
                    <option value="">Seleccionar técnico</option>
                    {tecnicos.map((tecnico) => (
                      <option key={tecnico.id} value={tecnico.id}>
                        {mostrarNombreTecnico(tecnico)}
                      </option>
                    ))}
                  </select>
                </div>

                <div className="form-group">
                  <label>Tipo de mantenimiento</label>
                  <select
                    name="tipo"
                    value={form.tipo}
                    onChange={handleChange}
                  >
                    {TIPOS.map((tipo) => (
                      <option key={tipo} value={tipo}>
                        {tipo}
                      </option>
                    ))}
                  </select>
                </div>

                <div className="form-group">
                  <label>Estado</label>
                  <select
                    name="estado"
                    value={form.estado}
                    onChange={handleChange}
                  >
                    {ESTADOS.map((estado) => (
                      <option key={estado} value={estado}>
                        {estado}
                      </option>
                    ))}
                  </select>
                </div>

                <div className="form-group">
                  <label>Fecha programada</label>
                  <input
                    type="date"
                    name="fecha_programada"
                    value={form.fecha_programada || ""}
                    onChange={handleChange}
                  />
                </div>
              </div>

              <div className="form-group">
                <label>Observaciones</label>
                <textarea
                  name="observaciones"
                  value={form.observaciones}
                  onChange={handleChange}
                  placeholder="Describe las actividades, prioridad o indicaciones para el técnico..."
                  rows="4"
                />
              </div>

              <div className="modal-actions-pro">
                <button
                  type="button"
                  className="btn-secondary-pro"
                  onClick={cerrarModal}
                >
                  Cancelar
                </button>

                <button type="submit" className="btn-primary-pro">
                  {modoEdicion ? "Guardar cambios" : "Asignar mantenimiento"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}