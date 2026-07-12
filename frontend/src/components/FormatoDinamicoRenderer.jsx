// ============================================================
// COMPONENTE: FormatoDinamicoRenderer
// Archivo: frontend/src/components/FormatoDinamicoRenderer.jsx
// ============================================================
// Renderiza automáticamente campos dinámicos:
// checkbox, texto, numero, textarea, select.
// ============================================================


function agruparPorSeccion(campos = []) {
  return campos.reduce((acc, campo) => {
    const seccion = campo.seccion || "General";
    if (!acc[seccion]) acc[seccion] = [];
    acc[seccion].push(campo);
    return acc;
  }, {});
}

export default function FormatoDinamicoRenderer({ campos = [], respuestas = {}, onChange }) {
  const grupos = agruparPorSeccion(campos.filter((c) => c.activo !== false));

  const renderInput = (campo) => {
    const actual = respuestas[campo.id] || { valor: "", observacion: "" };
    const tipo = campo.tipo_campo || "checkbox";

    if (tipo === "checkbox") {
      return (
        <div className="bd-check-row">
          <label className="bd-checkbox">
            <input
              type="checkbox"
              checked={actual.valor === "SI"}
              onChange={(e) =>
                onChange(campo.id, {
                  ...actual,
                  valor: e.target.checked ? "SI" : "NO",
                })
              }
            />
            <span>{actual.valor === "SI" ? "Realizado" : "Pendiente"}</span>
          </label>
          <input
            className="bd-input"
            placeholder="Observación"
            value={actual.observacion || ""}
            onChange={(e) =>
              onChange(campo.id, {
                ...actual,
                observacion: e.target.value,
              })
            }
          />
        </div>
      );
    }

    if (tipo === "textarea") {
      return (
        <textarea
          className="bd-textarea"
          placeholder="Escribe la observación técnica..."
          value={actual.valor || ""}
          onChange={(e) => onChange(campo.id, { ...actual, valor: e.target.value })}
        />
      );
    }

    if (tipo === "select") {
      const opciones = String(campo.opciones || "").split(",").map((x) => x.trim()).filter(Boolean);
      return (
        <select
          className="bd-input"
          value={actual.valor || ""}
          onChange={(e) => onChange(campo.id, { ...actual, valor: e.target.value })}
        >
          <option value="">Seleccionar...</option>
          {opciones.map((op) => (
            <option key={op} value={op}>{op}</option>
          ))}
        </select>
      );
    }

    return (
      <input
        className="bd-input"
        type={tipo === "numero" ? "number" : "text"}
        placeholder={tipo === "numero" ? "Valor medido" : "Ingrese valor"}
        value={actual.valor || ""}
        onChange={(e) => onChange(campo.id, { ...actual, valor: e.target.value })}
      />
    );
  };

  return (
    <div className="bd-renderer">
      {Object.entries(grupos).map(([seccion, items]) => (
        <section key={seccion} className="bd-section-card">
          <div className="bd-section-title">
            <h3>{seccion}</h3>
            <span>{items.length} ítems</span>
          </div>

          <div className="bd-fields-grid">
            {items.map((campo) => (
              <div key={campo.id} className="bd-field-card">
                <div className="bd-field-label">
                  <strong>{campo.nombre_campo}</strong>
                  {campo.obligatorio && <span className="bd-required">Obligatorio</span>}
                </div>
                {renderInput(campo)}
              </div>
            ))}
          </div>
        </section>
      ))}
    </div>
  );
}
