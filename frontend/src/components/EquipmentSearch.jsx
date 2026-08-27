import { useCallback, useRef, useState } from "react";
import { Search, X, MapPin } from "lucide-react";

export default function EquipmentSearch({ equipos, onSelect, selectedId }) {
  const [query, setQuery] = useState("");
  const [open, setOpen] = useState(false);
  const [highlight, setHighlight] = useState(0);
  const inputRef = useRef(null);
  const listRef = useRef(null);

  const selected = equipos.find((e) => String(e.id) === String(selectedId));

  const normalize = (v) => (v || "").toString().toLowerCase();

  const results = query.trim().length < 2
    ? []
    : equipos.filter((eq) => {
        const q = normalize(query);
        const fields = [
          eq.nombre, eq.codigo_id, eq.codigo, eq.inventario,
          eq.serie, eq.marca, eq.modelo, eq.ubicacion,
        ];
        return fields.some((f) => normalize(f).includes(q));
      }).slice(0, 12);

  const handleQueryChange = (value) => {
    setQuery(value);
    setHighlight(0);
    setOpen(true);
  };

  const pick = useCallback((eq) => {
    onSelect(eq);
    setQuery("");
    setOpen(false);
    inputRef.current?.blur();
  }, [onSelect]);

  const onKey = (e) => {
    if (e.key === "ArrowDown") {
      e.preventDefault();
      setHighlight((h) => Math.min(h + 1, results.length - 1));
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      setHighlight((h) => Math.max(h - 1, 0));
    } else if (e.key === "Enter" && results[highlight]) {
      e.preventDefault();
      pick(results[highlight]);
    } else if (e.key === "Escape") {
      setOpen(false);
    }
  };

  return (
    <div className="eq-search-root">
      {selected && !open ? (
        <div className="eq-search-selected">
          <div className="eq-search-selected-info">
            <span className="eq-search-selected-name">{selected.nombre}</span>
            <span className="eq-search-selected-meta">
              {selected.codigo_id && <span>Cód: {selected.codigo_id}</span>}
              {selected.inventario && <span>Inv: {selected.inventario}</span>}
              {selected.serie && <span>Ser: {selected.serie}</span>}
            </span>
            <span className="eq-search-selected-location">
              {selected.ubicacion || "Sin ubicación"}
            </span>
          </div>
          <button
            type="button"
            className="eq-search-clear"
            onClick={() => { onSelect(null); setQuery(""); }}
            aria-label="Deseleccionar equipo"
          >
            <X size={16} />
          </button>
        </div>
      ) : (
        <div className="eq-search-input-wrap">
          <Search size={16} className="eq-search-icon" />
          <input
            ref={inputRef}
            type="text"
            className="eq-search-input"
            placeholder="Buscar por nombre, código, inventario, serie, marca..."
            value={query}
            onChange={(e) => handleQueryChange(e.target.value)}
            onFocus={() => setOpen(true)}
            onBlur={() => setTimeout(() => setOpen(false), 150)}
            onKeyDown={onKey}
            autoComplete="off"
          />
          {query && (
            <button
              type="button"
              className="eq-search-clear-input"
              onClick={() => { setQuery(""); inputRef.current?.focus(); }}
            >
              <X size={14} />
            </button>
          )}
        </div>
      )}

      {open && results.length > 0 && (
        <ul className="eq-search-dropdown" ref={listRef}>
          {results.map((eq, i) => (
            <li
              key={eq.id}
              className={`eq-search-item ${i === highlight ? "highlighted" : ""}`}
              onMouseDown={() => pick(eq)}
              onMouseEnter={() => setHighlight(i)}
            >
              <div className="eq-search-item-main">
                <span className="eq-search-item-name">{eq.nombre}</span>
                <span className="eq-search-item-codigo">{eq.codigo_id || eq.codigo || ""}</span>
              </div>
              <div className="eq-search-item-meta">
                {eq.inventario && <span>{eq.inventario}</span>}
                {eq.serie && <span>{eq.serie}</span>}
                {eq.marca && <span>{eq.marca} {eq.modelo || ""}</span>}
              </div>
              <div className="eq-search-item-location">
                <MapPin size={12} /> {eq.ubicacion || "Sin ubicación"}
              </div>
            </li>
          ))}
        </ul>
      )}

      {open && query.trim().length >= 2 && results.length === 0 && (
        <div className="eq-search-empty">No se encontraron equipos con "{query}"</div>
      )}
    </div>
  );
}
