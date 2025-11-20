import React, { useRef, useEffect, useState } from "react";

const CameraLightDetector = () => {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const [estadoLuz, setEstadoLuz] = useState("⏳ Detectando...");
  const [estadoAnterior, setEstadoAnterior] = useState(null);
  const UMBRAL = 40;


  useEffect(() => {
    const iniciarCamara = async () => {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: true });
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
        }
      } catch (err) {
        console.error("Error al acceder a la cámara:", err);
        setEstadoLuz("❌ No se pudo acceder a la cámara");
      }
    };

    iniciarCamara();

    const intervalo = setInterval(() => {
      analizarBrillo();
    }, 1000); // cada segundo

    return () => clearInterval(intervalo);
  }, []);

  const analizarBrillo = () => {
    const video = videoRef.current;
    const canvas = canvasRef.current;
    if (!video || !canvas) return;

    const ctx = canvas.getContext("2d");
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    const frame = ctx.getImageData(0, 0, canvas.width, canvas.height);
    let totalLuminancia = 0;

    for (let i = 0; i < frame.data.length; i += 4) {
        const r = frame.data[i];
        const g = frame.data[i + 1];
        const b = frame.data[i + 2];
        const luminancia = 0.4 * r + 0.4 * g + 0.4 * b;
        totalLuminancia += luminancia;
    }

    const promedio = totalLuminancia / (frame.data.length / 4);
    const nuevoEstado = promedio > UMBRAL ? "encendida" : "apagada";

    // Solo si el estado cambió
    if (nuevoEstado !== estadoAnterior) {
        setEstadoAnterior(nuevoEstado);
        setEstadoLuz(nuevoEstado === "encendida" ? "💡 Luz encendida" : "🌑 Luz apagada");

        // Enviar POST solo si la luz se APAGA (según lo que dijiste)
        if (nuevoEstado === "apagada") {
            fetch("http://localhost:8000/sensor", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ mensaje: "Apagado" }),
            })
            .then((res) => res.json())
            .then((data) => console.log("🔁 Backend respondió:", data))
            .catch((err) => console.error("❌ Error al notificar backend:", err));
        }
    }
    };


  return (
    <div className="flex flex-col items-center justify-center p-4 text-white bg-black min-h-screen">
      <h1 className="text-2xl mb-4">Detector de luz con cámara</h1>
      <video ref={videoRef} autoPlay playsInline width="300" className="mb-4 rounded" />
      <canvas ref={canvasRef} width={100} height={100} style={{ display: "none" }} />
      <div className="text-xl mt-2">{estadoLuz}</div>
    </div>
  );
};

export default CameraLightDetector;
