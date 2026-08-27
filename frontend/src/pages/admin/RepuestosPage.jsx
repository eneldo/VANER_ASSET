// ============================================================
// REPUESTOS Y CONSUMIBLES — Página principal
// Catálogo, bodegas, existencias, movimientos, solicitudes,
// proveedores, compatibilidad.
// ============================================================

import { useCallback, useEffect, useState } from "react";
import {
  Package, Search, Plus, Edit, RefreshCw, ChevronLeft, ChevronRight,
  X, CheckCircle2, AlertTriangle, Truck, ArrowRightLeft, Warehouse,
  ShoppingCart, Tags,
} from "lucide-react";

import AdminLayout from "./AdminLayout";
import API from "../../api/axios";
import { showToast } from "../../utils/toast";
import "../../styles/maintenance-wizard.css";
import "./MantenimientosPage.css";

const TABS = [
  { key: "catalogo", label: "Catálogo", icon: Package },
  { key: "existencias", label: "Existencias", icon: Warehouse },
  { key: "movimientos", label: "Movimientos", icon: ArrowRightLeft },
  { key: "solicitudes", label: "Solicitudes", icon: ShoppingCart },
  { key: "proveedores", label: "Proveedores", icon: Truck },
];

export default function RepuestosPage() {
  const [tab, setTab] = useState("catalogo");
  const [dashboard, setDashboard] = useState(null);

  useEffect(() => {
    API.get("/repuestos/dashboard").then((r) => setDashboard(r.data)).catch(() => {});
  }, []);

  return (
    <AdminLayout>
      <div className="mant-page">
        <div className="sga-module-hero">
          <div className="sga-module-hero__icon">
            <Package size={24} />
          </div>
          <div className="sga-module-hero__text">
            <span>Inventario</span>
            <h1>Repuestos y Consumibles</h1>
            <p>Catálogo, existencias, movimientos, solicitudes, proveedores y compatibilidad con equipos.</p>
          </div>
        </div>

        {dashboard && (
          <div className="mant-stats-grid" style={{ marginBottom: 16 }}>
            <StatCard label="Repuestos activos" value={dashboard.total_repuestos_activos} icon={Package} />
            <StatCard label="Unidades disponibles" value={Number(dashboard.total_unidades_disponibles).toLocaleString()} icon={Warehouse} />
            <StatCard label="Stock bajo" value={dashboard.repuestos_stock_bajo} icon={AlertTriangle} danger />
            <StatCard label="Agotados" value={dashboard.repuestos_agotados} icon={X} danger />
            <StatCard label="Valor inventario" value={`$${Number(dashboard.valor_inventario).toLocaleString()}`} icon={Tags} />
            <StatCard label="Solicitudes pendientes" value={dashboard.solicitudes_pendientes} icon={ShoppingCart} />
          </div>
        )}

        <div className="mant-filters-row" style={{ borderBottom: "1px solid #e2e8f0", marginBottom: 0 }}>
          <div className="mant-filter-chips">
            {TABS.map((t) => (
              <button
                key={t.key}
                className={`mant-chip ${tab === t.key ? "active" : ""}`}
                onClick={() => setTab(t.key)}
              >
                <t.icon size={13} style={{ marginRight: 4 }} />
                {t.label}
              </button>
            ))}
          </div>
        </div>

        <div style={{ marginTop: 16 }}>
          {tab === "catalogo" && <CatalogoTab />}
          {tab === "existencias" && <ExistenciasTab />}
          {tab === "movimientos" && <MovimientosTab />}
          {tab === "solicitudes" && <SolicitudesTab />}
          {tab === "proveedores" && <ProveedoresTab />}
        </div>
      </div>
    </AdminLayout>
  );
}

function StatCard({ label, value, icon: Icon, danger }) {
  return (
    <div className={`mant-stat-card ${danger ? "danger" : ""}`}>
      <div className="mant-stat-icon"><Icon size={18} /></div>
      <div>
        <span className="mant-stat-value">{value}</span>
        <span className="mant-stat-label">{label}</span>
      </div>
    </div>
  );
}

// ============================================================
// CATÁLOGO
// ============================================================

function CatalogoTab() {
  const [items, setItems] = useState([]);
  const [busqueda, setBusqueda] = useState("");
  const [pagina, setPagina] = useState(1);
  const [total, setTotal] = useState(0);
  const [form, setForm] = useState(null);
  const porPagina = 20;

  const cargar = useCallback(async () => {
    try {
      const params = { page: pagina, per_page: porPagina };
      if (busqueda.trim()) params.buscar = busqueda.trim();
      const res = await API.get("/repuestos/", { params });
      const data = res.data;
      setItems(Array.isArray(data) ? data : []);
      setTotal(Array.isArray(data) ? data.length : 0);
    } catch {
      showToast("Error cargando catálogo", "error");
    }
  }, [pagina, busqueda]);

  useEffect(() => { cargar(); }, [pagina, busqueda]); // eslint-disable-line react-hooks/set-state-in-effect

  const guardar = async () => {
    if (!form.codigo || !form.nombre) {
      showToast("Código y nombre son obligatorios", "warning");
      return;
    }
    try {
      if (form.id) {
        await API.put(`/repuestos/${form.id}`, form);
        showToast("Repuesto actualizado", "success");
      } else {
        await API.post("/repuestos/", form);
        showToast("Repuesto creado", "success");
      }
      setForm(null);
      await cargar();
    } catch (errSave) {
      showToast(errSave?.response?.data?.detail || "Error al guardar", "error");
    }
  };

  const toggleEstado = async (id) => {
    try {
      await API.patch(`/repuestos/${id}/estado`);
      showToast("Estado actualizado", "success");
      await cargar();
    } catch {
      showToast("Error al cambiar estado", "error");
    }
  };

  const totalPaginas = Math.max(1, Math.ceil(total / porPagina));

  return (
    <section className="mant-card mant-list-card">
      <div className="mant-section-header">
        <div><h2>Catálogo de Repuestos</h2><p>{total} referencias registradas</p></div>
        <button className="mant-save-btn" onClick={() => setForm({ codigo: "", nombre: "", tipo: "REPUESTO", maneja_lote: false, maneja_serial: false, control_vencimiento: false })}>
          <Plus size={14} /> Nuevo repuesto
        </button>
      </div>

      <div className="mant-filters-row">
        <div className="mant-search-box">
          <Search size={16} />
          <input placeholder="Buscar por código, nombre, referencia..." value={busqueda} onChange={(e) => { setBusqueda(e.target.value); setPagina(1); }} />
        </div>
        <button className="mant-reload-btn" onClick={cargar}><RefreshCw size={14} /></button>
      </div>

      <div className="mant-table-wrap">
        <table className="mant-table">
          <thead>
            <tr>
              <th>Código</th>
              <th>Nombre</th>
              <th>Tipo</th>
              <th>Referencia</th>
              <th>Marca</th>
              <th>Unidad</th>
              <th>Stock Mín.</th>
              <th>Estado</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            {items.map((r) => (
              <tr key={r.id}>
                <td><strong>{r.codigo}</strong></td>
                <td>{r.nombre}</td>
                <td><span className="mant-type-badge">{r.tipo}</span></td>
                <td>{r.referencia || "—"}</td>
                <td>{r.marca || "—"}</td>
                <td>{r.unidad_medida_id || "UN"}</td>
                <td>{r.stock_minimo || "0"}</td>
                <td><span className={`mant-badge ${r.activo ? "badge-green" : "badge-red"}`}>{r.activo ? "Activo" : "Inactivo"}</span></td>
                <td>
                  <div className="mant-actions">
                    <button className="mant-view-btn" onClick={() => setForm(r)} title="Editar"><Edit size={14} /></button>
                    <button className="mant-edit-btn" onClick={() => toggleEstado(r.id)} title="Toggle estado">
                      {r.activo ? <X size={14} /> : <CheckCircle2 size={14} />}
                    </button>
                  </div>
                </td>
              </tr>
            ))}
            {items.length === 0 && <tr><td colSpan="9" className="mant-empty">No hay repuestos registrados.</td></tr>}
          </tbody>
        </table>
      </div>

      <div className="mant-pagination">
        <button disabled={pagina === 1} onClick={() => setPagina(pagina - 1)}><ChevronLeft size={16} /> Anterior</button>
        <span>Página {pagina} de {totalPaginas}</span>
        <button disabled={pagina === totalPaginas} onClick={() => setPagina(pagina + 1)}>Siguiente <ChevronRight size={16} /></button>
      </div>

      {form && (
        <div className="mant-overlay" onClick={() => setForm(null)}>
          <div className="mant-modal" onClick={(e) => e.stopPropagation()} style={{ maxWidth: 600 }}>
            <div className="mant-modal-header">
              <h2>{form.id ? "Editar repuesto" : "Nuevo repuesto"}</h2>
              <button onClick={() => setForm(null)}><X size={18} /></button>
            </div>
            <div className="mant-detail-grid" style={{ gridTemplateColumns: "1fr 1fr" }}>
              <FormField label="Código *" value={form.codigo} onChange={(v) => setForm({ ...form, codigo: v })} />
              <FormField label="Nombre *" value={form.nombre} onChange={(v) => setForm({ ...form, nombre: v })} />
              <FormField label="Descripción" value={form.descripcion || ""} onChange={(v) => setForm({ ...form, descripcion: v })} multiline />
              <div className="mant-detail">
                <span>Tipo</span>
                <select value={form.tipo} onChange={(e) => setForm({ ...form, tipo: e.target.value })} className="mant-input">
                  <option value="REPUESTO">Repuesto</option>
                  <option value="CONSUMIBLE">Consumible</option>
                </select>
              </div>
              <FormField label="Referencia" value={form.referencia || ""} onChange={(v) => setForm({ ...form, referencia: v })} />
              <FormField label="Marca" value={form.marca || ""} onChange={(v) => setForm({ ...form, marca: v })} />
              <FormField label="Fabricante" value={form.fabricante || ""} onChange={(v) => setForm({ ...form, fabricante: v })} />
              <FormField label="Código barras" value={form.codigo_barras || ""} onChange={(v) => setForm({ ...form, codigo_barras: v })} />
              <FormField label="Stock mínimo" value={form.stock_minimo || ""} onChange={(v) => setForm({ ...form, stock_minimo: v })} type="number" />
              <FormField label="Stock máximo" value={form.stock_maximo || ""} onChange={(v) => setForm({ ...form, stock_maximo: v })} type="number" />
              <FormField label="Punto reposición" value={form.punto_reposicion || ""} onChange={(v) => setForm({ ...form, punto_reposicion: v })} type="number" />
              <FormField label="Último costo" value={form.ultimo_costo || ""} onChange={(v) => setForm({ ...form, ultimo_costo: v })} type="number" />
            </div>
            <div className="mant-form-actions">
              <button className="mant-save-btn" onClick={guardar}>
                <CheckCircle2 size={14} /> {form.id ? "Actualizar" : "Crear"}
              </button>
            </div>
          </div>
        </div>
      )}
    </section>
  );
}

// ============================================================
// EXISTENCIAS
// ============================================================

function ExistenciasTab() {
  const [items, setItems] = useState([]);
  const [repuestos, setRepuestos] = useState([]);
  const [bodegas, setBodegas] = useState([]);
  const [filtroRepuesto, setFiltroRepuesto] = useState("");
  const [filtroBodega, setFiltroBodega] = useState("");

  useEffect(() => {
    Promise.all([
      API.get("/repuestos/existencias", { params: { repuesto_id: filtroRepuesto || undefined, bodega_id: filtroBodega || undefined } }),
      API.get("/repuestos/", { params: { per_page: 200 } }),
      API.get("/repuestos/bodegas"),
    ]).then(([resE, resR, resB]) => {
      setItems(resE.data || []);
      setRepuestos(resR.data || []);
      setBodegas(resB.data || []);
    }).catch(() => {});
  }, [filtroRepuesto, filtroBodega]);

  const getRepNombre = (id) => repuestos.find((r) => r.id === id)?.nombre || "—";
  const getBodegaNombre = (id) => bodegas.find((b) => b.id === id)?.nombre || "—";

  return (
    <section className="mant-card mant-list-card">
      <div className="mant-section-header">
        <div><h2>Existencias por Bodega</h2><p>{items.length} registros de stock</p></div>
      </div>

      <div className="mant-filters-row">
        <select value={filtroRepuesto} onChange={(e) => setFiltroRepuesto(e.target.value)} className="mant-input" style={{ maxWidth: 250 }}>
          <option value="">Todos los repuestos</option>
          {repuestos.map((r) => <option key={r.id} value={r.id}>{r.codigo} - {r.nombre}</option>)}
        </select>
        <select value={filtroBodega} onChange={(e) => setFiltroBodega(e.target.value)} className="mant-input" style={{ maxWidth: 200 }}>
          <option value="">Todas las bodegas</option>
          {bodegas.map((b) => <option key={b.id} value={b.id}>{b.nombre}</option>)}
        </select>
      </div>

      <div className="mant-table-wrap">
        <table className="mant-table">
          <thead>
            <tr>
              <th>Repuesto</th>
              <th>Bodega</th>
              <th>Física</th>
              <th>Reservada</th>
              <th>Disponible</th>
              <th>Lote</th>
              <th>Serial</th>
              <th>Vencimiento</th>
            </tr>
          </thead>
          <tbody>
            {items.map((e) => {
              const disponible = Number(e.existencia_fisica) - Number(e.cantidad_reservada);
              return (
                <tr key={e.id}>
                  <td>{getRepNombre(e.repuesto_id)}</td>
                  <td>{getBodegaNombre(e.bodega_id)}</td>
                  <td>{Number(e.existencia_fisica).toLocaleString()}</td>
                  <td>{Number(e.cantidad_reservada).toLocaleString()}</td>
                  <td className={disponible <= 0 ? "text-danger" : ""}>{disponible.toLocaleString()}</td>
                  <td>{e.lote || "—"}</td>
                  <td>{e.serial || "—"}</td>
                  <td>{e.fecha_vencimiento || "—"}</td>
                </tr>
              );
            })}
            {items.length === 0 && <tr><td colSpan="8" className="mant-empty">No hay existencias registradas.</td></tr>}
          </tbody>
        </table>
      </div>
    </section>
  );
}

// ============================================================
// MOVIMIENTOS
// ============================================================

function MovimientosTab() {
  const [items, setItems] = useState([]);
  const [repuestos, setRepuestos] = useState([]);
  const [filtroTipo, setFiltroTipo] = useState("");
  const [pagina, setPagina] = useState(1);
  const [total, setTotal] = useState(0);
  const porPagina = 20;

  useEffect(() => {
    Promise.all([
      API.get("/repuestos/movimientos", { params: { tipo_movimiento: filtroTipo || undefined, page: pagina, per_page: porPagina } }),
      API.get("/repuestos/", { params: { per_page: 200 } }),
    ]).then(([resM, resR]) => {
      const data = resM.data;
      setItems(Array.isArray(data) ? data : []);
      setTotal(Array.isArray(data) ? data.length : 0);
      setRepuestos(resR.data || []);
    }).catch(() => {});
  }, [filtroTipo, pagina]);

  const getRepNombre = (id) => repuestos.find((r) => r.id === id)?.nombre || "—";

  const tipos = [
    "", "ENTRADA_COMPRA", "ENTRADA_INICIAL", "SALIDA_OT", "RESERVA",
    "LIBERACION_RESERVA", "ENTREGA_TECNICO", "CONSUMO", "DEVOLUCION",
    "TRANSFERENCIA", "AJUSTE_POSITIVO", "AJUSTE_NEGATIVO",
  ];

  const totalPaginas = Math.max(1, Math.ceil(total / porPagina));

  return (
    <section className="mant-card mant-list-card">
      <div className="mant-section-header">
        <div><h2>Movimientos de Inventario</h2><p>{total} movimientos registrados</p></div>
      </div>

      <div className="mant-filters-row">
        <select value={filtroTipo} onChange={(e) => { setFiltroTipo(e.target.value); setPagina(1); }} className="mant-input" style={{ maxWidth: 220 }}>
          <option value="">Todos los tipos</option>
          {tipos.filter(Boolean).map((t) => <option key={t} value={t}>{t.replace(/_/g, " ")}</option>)}
        </select>
      </div>

      <div className="mant-table-wrap">
        <table className="mant-table">
          <thead>
            <tr>
              <th>Fecha</th>
              <th>Tipo</th>
              <th>Repuesto</th>
              <th>Cantidad</th>
              <th>Costo U.</th>
              <th>Costo T.</th>
              <th>Exist. Ant.</th>
              <th>Exist. Post.</th>
              <th>Usuario</th>
            </tr>
          </thead>
          <tbody>
            {items.map((m) => (
              <tr key={m.id}>
                <td>{m.created_at ? new Date(m.created_at).toLocaleDateString("es-CO") : "—"}</td>
                <td><span className="mant-type-badge">{m.tipo_movimiento?.replace(/_/g, " ")}</span></td>
                <td>{getRepNombre(m.repuesto_id)}</td>
                <td>{Number(m.cantidad).toLocaleString()}</td>
                <td>{m.costo_unitario ? `$${Number(m.costo_unitario).toLocaleString()}` : "—"}</td>
                <td>{m.costo_total ? `$${Number(m.costo_total).toLocaleString()}` : "—"}</td>
                <td>{m.existencia_anterior != null ? Number(m.existencia_anterior).toLocaleString() : "—"}</td>
                <td>{m.existencia_posterior != null ? Number(m.existencia_posterior).toLocaleString() : "—"}</td>
                <td>{m.usuario_id ? "—" : "—"}</td>
              </tr>
            ))}
            {items.length === 0 && <tr><td colSpan="9" className="mant-empty">No hay movimientos registrados.</td></tr>}
          </tbody>
        </table>
      </div>

      <div className="mant-pagination">
        <button disabled={pagina === 1} onClick={() => setPagina(pagina - 1)}><ChevronLeft size={16} /> Anterior</button>
        <span>Página {pagina} de {totalPaginas}</span>
        <button disabled={pagina === totalPaginas} onClick={() => setPagina(pagina + 1)}>Siguiente <ChevronRight size={16} /></button>
      </div>
    </section>
  );
}

// ============================================================
// SOLICITUDES
// ============================================================

function SolicitudesTab() {
  const [items, setItems] = useState([]);
  const [repuestos, setRepuestos] = useState([]);
  const [filtroEstado, setFiltroEstado] = useState("");
  const [pagina, setPagina] = useState(1);
  const [total, setTotal] = useState(0);
  const porPagina = 20;

  const cargar = useCallback(async () => {
    try {
      const [resS, resR] = await Promise.all([
        API.get("/repuestos/solicitudes", { params: { estado: filtroEstado || undefined, page: pagina, per_page: porPagina } }),
        API.get("/repuestos/", { params: { per_page: 200 } }),
      ]);
      const data = resS.data;
      setItems(Array.isArray(data) ? data : []);
      setTotal(Array.isArray(data) ? data.length : 0);
      setRepuestos(resR.data || []);
    } catch {
      console.error("Error");
    }
  }, [filtroEstado, pagina]);

  useEffect(() => { cargar(); }, [filtroEstado, pagina]); // eslint-disable-line react-hooks/set-state-in-effect

  const getRepNombre = (id) => repuestos.find((r) => r.id === id)?.nombre || "—";

  const aprobar = async (id) => {
    try {
      await API.post(`/repuestos/solicitudes/${id}/aprobar`);
      showToast("Solicitud aprobada", "success");
      await cargar();
    } catch (err) {
      showToast(err?.response?.data?.detail || "Error", "error");
    }
  };

  const reservar = async (id) => {
    try {
      await API.post(`/repuestos/solicitudes/${id}/reservar`);
      showToast("Reserva realizada", "success");
      await cargar();
    } catch (err) {
      showToast(err?.response?.data?.detail || "Error", "error");
    }
  };

  const entregar = async (id) => {
    try {
      await API.post(`/repuestos/solicitudes/${id}/entregar`);
      showToast("Entrega registrada", "success");
      await cargar();
    } catch (err) {
      showToast(err?.response?.data?.detail || "Error", "error");
    }
  };

  const estados = ["", "SOLICITADO", "APROBADO", "RESERVADO", "ENTREGADO", "CONSUMIDO", "DEVUELTO", "RECHAZADO", "CANCELADO"];
  const totalPaginas = Math.max(1, Math.ceil(total / porPagina));

  return (
    <section className="mant-card mant-list-card">
      <div className="mant-section-header">
        <div><h2>Solicitudes de Repuestos</h2><p>{total} solicitudes</p></div>
      </div>

      <div className="mant-filters-row">
        <div className="mant-filter-chips">
          {estados.map((e) => (
            <button key={e} className={`mant-chip ${filtroEstado === e ? "active" : ""}`} onClick={() => { setFiltroEstado(e); setPagina(1); }}>
              {e || "Todas"}
            </button>
          ))}
        </div>
      </div>

      <div className="mant-table-wrap">
        <table className="mant-table">
          <thead>
            <tr>
              <th>Repuesto</th>
              <th>Cantidad</th>
              <th>Aprobada</th>
              <th>Entregada</th>
              <th>Estado</th>
              <th>Fecha</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            {items.map((s) => (
              <tr key={s.id}>
                <td>{getRepNombre(s.repuesto_id)}</td>
                <td>{Number(s.cantidad_solicitada).toLocaleString()}</td>
                <td>{s.cantidad_aprobada ? Number(s.cantidad_aprobada).toLocaleString() : "—"}</td>
                <td>{s.cantidad_entregada ? Number(s.cantidad_entregada).toLocaleString() : "—"}</td>
                <td><span className={`mant-badge ${s.estado === "SOLICITADO" ? "badge-blue" : s.estado === "APROBADO" ? "badge-green" : s.estado === "RECHAZADO" ? "badge-red" : "badge-orange"}`}>{s.estado}</span></td>
                <td>{s.created_at ? new Date(s.created_at).toLocaleDateString("es-CO") : "—"}</td>
                <td>
                  <div className="mant-actions">
                    {s.estado === "SOLICITADO" && <button className="mant-save-btn" onClick={() => aprobar(s.id)} style={{ padding: "3px 8px", fontSize: 11 }}>Aprobar</button>}
                    {s.estado === "APROBADO" && <button className="mant-save-btn" onClick={() => reservar(s.id)} style={{ padding: "3px 8px", fontSize: 11 }}>Reservar</button>}
                    {s.estado === "RESERVADO" && <button className="mant-save-btn" onClick={() => entregar(s.id)} style={{ padding: "3px 8px", fontSize: 11 }}>Entregar</button>}
                  </div>
                </td>
              </tr>
            ))}
            {items.length === 0 && <tr><td colSpan="7" className="mant-empty">No hay solicitudes con este filtro.</td></tr>}
          </tbody>
        </table>
      </div>

      <div className="mant-pagination">
        <button disabled={pagina === 1} onClick={() => setPagina(pagina - 1)}><ChevronLeft size={16} /> Anterior</button>
        <span>Página {pagina} de {totalPaginas}</span>
        <button disabled={pagina === totalPaginas} onClick={() => setPagina(pagina + 1)}>Siguiente <ChevronRight size={16} /></button>
      </div>
    </section>
  );
}

// ============================================================
// PROVEEDORES
// ============================================================

function ProveedoresTab() {
  const [items, setItems] = useState([]);
  const [form, setForm] = useState(null);

  const cargar = async () => {
    try {
      const res = await API.get("/repuestos/proveedores");
      setItems(res.data || []);
    } catch {
      console.error("Error");
    }
  };

  useEffect(() => { cargar(); }, []); // eslint-disable-line react-hooks/set-state-in-effect

  const guardar = async () => {
    if (!form.nombre) {
      showToast("Nombre es obligatorio", "warning");
      return;
    }
    try {
      if (form.id) {
        await API.put(`/repuestos/proveedores/${form.id}`, form);
        showToast("Proveedor actualizado", "success");
      } else {
        await API.post("/repuestos/proveedores", form);
        showToast("Proveedor creado", "success");
      }
      setForm(null);
      await cargar();
    } catch (err) {
      showToast(err?.response?.data?.detail || "Error", "error");
    }
  };

  return (
    <section className="mant-card mant-list-card">
      <div className="mant-section-header">
        <div><h2>Proveedores</h2><p>{items.length} proveedores registrados</p></div>
        <button className="mant-save-btn" onClick={() => setForm({ nombre: "" })}>
          <Plus size={14} /> Nuevo proveedor
        </button>
      </div>

      <div className="mant-table-wrap">
        <table className="mant-table">
          <thead>
            <tr>
              <th>Nombre</th>
              <th>NIT</th>
              <th>Contacto</th>
              <th>Teléfono</th>
              <th>Email</th>
              <th>Entrega (días)</th>
              <th>Estado</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            {items.map((p) => (
              <tr key={p.id}>
                <td><strong>{p.nombre}</strong></td>
                <td>{p.nit || "—"}</td>
                <td>{p.contacto || "—"}</td>
                <td>{p.telefono || "—"}</td>
                <td>{p.email || "—"}</td>
                <td>{p.tiempo_entrega_dias || "—"}</td>
                <td><span className={`mant-badge ${p.activo ? "badge-green" : "badge-red"}`}>{p.activo ? "Activo" : "Inactivo"}</span></td>
                <td>
                  <button className="mant-view-btn" onClick={() => setForm(p)} title="Editar"><Edit size={14} /></button>
                </td>
              </tr>
            ))}
            {items.length === 0 && <tr><td colSpan="8" className="mant-empty">No hay proveedores registrados.</td></tr>}
          </tbody>
        </table>
      </div>

      {form && (
        <div className="mant-overlay" onClick={() => setForm(null)}>
          <div className="mant-modal" onClick={(e) => e.stopPropagation()} style={{ maxWidth: 500 }}>
            <div className="mant-modal-header">
              <h2>{form.id ? "Editar proveedor" : "Nuevo proveedor"}</h2>
              <button onClick={() => setForm(null)}><X size={18} /></button>
            </div>
            <div className="mant-detail-grid" style={{ gridTemplateColumns: "1fr 1fr" }}>
              <FormField label="Nombre *" value={form.nombre} onChange={(v) => setForm({ ...form, nombre: v })} />
              <FormField label="NIT" value={form.nit || ""} onChange={(v) => setForm({ ...form, nit: v })} />
              <FormField label="Contacto" value={form.contacto || ""} onChange={(v) => setForm({ ...form, contacto: v })} />
              <FormField label="Teléfono" value={form.telefono || ""} onChange={(v) => setForm({ ...form, telefono: v })} />
              <FormField label="Email" value={form.email || ""} onChange={(v) => setForm({ ...form, email: v })} />
              <FormField label="Dirección" value={form.direccion || ""} onChange={(v) => setForm({ ...form, direccion: v })} />
              <FormField label="Días entrega" value={form.tiempo_entrega_dias || ""} onChange={(v) => setForm({ ...form, tiempo_entrega_dias: v })} type="number" />
            </div>
            <div className="mant-form-actions">
              <button className="mant-save-btn" onClick={guardar}><CheckCircle2 size={14} /> Guardar</button>
            </div>
          </div>
        </div>
      )}
    </section>
  );
}

// ============================================================
// FORM FIELD HELPER
// ============================================================

function FormField({ label, value, onChange, type = "text", multiline }) {
  return (
    <div className="mant-detail">
      <span>{label}</span>
      {multiline ? (
        <textarea className="mant-input" value={value} onChange={(e) => onChange(e.target.value)} rows={3} />
      ) : (
        <input className="mant-input" type={type} value={value} onChange={(e) => onChange(e.target.value)} />
      )}
    </div>
  );
}
