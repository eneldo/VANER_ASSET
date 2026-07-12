import { useEffect, useRef } from "react";

const WIDTH = 700;
const HEIGHT = 260;

export default function SignaturePad({ label, value, onChange, required = false }) {
  const canvasRef = useRef(null);
  const drawingRef = useRef(false);

  useEffect(() => {
    const canvas = canvasRef.current;
    const context = canvas.getContext("2d");
    context.fillStyle = "#ffffff";
    context.fillRect(0, 0, WIDTH, HEIGHT);
    context.strokeStyle = "#0f172a";
    context.lineWidth = 4;
    context.lineCap = "round";
    context.lineJoin = "round";
    if (value?.startsWith("data:image/")) {
      const image = new Image();
      image.onload = () => context.drawImage(image, 0, 0, WIDTH, HEIGHT);
      image.src = value;
    }
  }, [value]);

  const punto = (event) => {
    const rect = event.currentTarget.getBoundingClientRect();
    return {
      x: (event.clientX - rect.left) * (WIDTH / rect.width),
      y: (event.clientY - rect.top) * (HEIGHT / rect.height),
    };
  };

  const iniciar = (event) => {
    event.preventDefault();
    drawingRef.current = true;
    event.currentTarget.setPointerCapture(event.pointerId);
    const context = event.currentTarget.getContext("2d");
    const { x, y } = punto(event);
    context.beginPath(); context.moveTo(x, y);
  };

  const dibujar = (event) => {
    if (!drawingRef.current) return;
    event.preventDefault();
    const context = event.currentTarget.getContext("2d");
    const { x, y } = punto(event);
    context.lineTo(x, y); context.stroke();
  };

  const finalizar = (event) => {
    if (!drawingRef.current) return;
    drawingRef.current = false;
    event.currentTarget.getContext("2d").closePath();
    onChange(event.currentTarget.toDataURL("image/png"));
  };

  const limpiar = () => onChange("");

  return (
    <div className="signature-pad-field">
      <div className="signature-pad-head"><strong>{label}{required ? " *" : ""}</strong><button type="button" onClick={limpiar}>Limpiar</button></div>
      <canvas
        ref={canvasRef} width={WIDTH} height={HEIGHT} className="signature-pad-canvas"
        onPointerDown={iniciar} onPointerMove={dibujar} onPointerUp={finalizar} onPointerCancel={finalizar}
        aria-label={`${label}. Firma dentro del recuadro con el dedo, lápiz o mouse.`}
      />
      <small>{value ? "Firma capturada" : "Firma dentro del recuadro"}</small>
    </div>
  );
}
