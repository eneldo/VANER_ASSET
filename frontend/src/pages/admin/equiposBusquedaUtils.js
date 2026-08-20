const PALABRAS_IGNORADAS = new Set([
  "de",
  "del",
  "el",
  "la",
  "los",
  "las",
  "y",
  "para",
  "por",
]);

export function normalizarTextoBusqueda(valor) {
  return String(valor || "")
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLocaleLowerCase("es")
    .replace(/[^a-z0-9]+/g, " ")
    .trim();
}

function tokenizar(valor) {
  const texto = normalizarTextoBusqueda(valor);
  return texto ? texto.split(/\s+/).filter(Boolean) : [];
}

function variantesToken(token) {
  const variantes = new Set([token]);

  if (token.length > 4 && token.endsWith("ces")) {
    variantes.add(token.slice(0, -3) + "z");
  }
  if (token.length > 4 && token.endsWith("es")) {
    variantes.add(token.slice(0, -2));
  }
  if (token.length > 3 && token.endsWith("s")) {
    variantes.add(token.slice(0, -1));
  }

  return variantes;
}

export function coincideBusquedaEquipo(valores, busqueda) {
  const tokensConsulta = tokenizar(busqueda).filter(
    (token) => !PALABRAS_IGNORADAS.has(token)
  );
  if (!tokensConsulta.length) return true;

  const tokensEquipo = tokenizar((Array.isArray(valores) ? valores : [valores]).join(" "));
  const variantesEquipo = new Set(
    tokensEquipo.flatMap((token) => Array.from(variantesToken(token)))
  );

  return tokensConsulta.every((tokenConsulta) => {
    const variantesConsulta = variantesToken(tokenConsulta);
    return Array.from(variantesConsulta).some((consulta) =>
      Array.from(variantesEquipo).some(
        (candidato) => candidato === consulta || (consulta.length >= 3 && candidato.startsWith(consulta))
      )
    );
  });
}

export function coincideBusquedaEquipoConContexto(
  valoresEquipo,
  valoresContexto,
  busqueda
) {
  const tokensConsulta = tokenizar(busqueda).filter(
    (token) => !PALABRAS_IGNORADAS.has(token)
  );
  if (!tokensConsulta.length) return true;

  if (coincideBusquedaEquipo(valoresEquipo, busqueda)) return true;

  const identificaElEquipo = tokensConsulta.some((token) =>
    coincideBusquedaEquipo(valoresEquipo, token)
  );
  if (!identificaElEquipo) return false;

  return coincideBusquedaEquipo(
    [...valoresEquipo, ...(Array.isArray(valoresContexto) ? valoresContexto : [valoresContexto])],
    busqueda
  );
}
