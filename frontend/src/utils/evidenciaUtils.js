const IMAGE_EXTENSIONS = [".jpg", ".jpeg", ".png", ".webp", ".gif"];

function evidenceMetadata(evidencia = {}) {
  return [
    evidencia.nombre_original,
    evidencia.filename,
    evidencia.archivo_url,
    evidencia.descarga_url,
  ]
    .filter(Boolean)
    .join(" ")
    .toLowerCase();
}

export function isImageEvidence(evidencia = {}) {
  const contentType = String(evidencia.content_type || evidencia.mime_type || "").toLowerCase();
  if (contentType.startsWith("image/")) return true;
  const metadata = evidenceMetadata(evidencia);
  return IMAGE_EXTENSIONS.some((extension) => metadata.includes(extension));
}

export function isPdfEvidence(evidencia = {}) {
  const contentType = String(evidencia.content_type || evidencia.mime_type || "").toLowerCase();
  return contentType === "application/pdf" || evidenceMetadata(evidencia).includes(".pdf");
}
