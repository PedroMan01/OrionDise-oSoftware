import { useEffect, useRef, useState } from "react";

const OrionListener = () => {
  const [escuchando, setEscuchando] = useState(false);
  const [botonVisible, setBotonVisible] = useState(true);
  const [ultimoTexto, setUltimoTexto] = useState("");

  // refs compartidos
  const audioContextRef = useRef(null); // micrófono
  const playbackContextRef = useRef(null); // reproducción
  const analyserRef = useRef(null);
  const dataArrayRef = useRef(null);
  const canvasRef = useRef(null);
  const recognitionRef = useRef(null);
  const animationFrameRef = useRef(null);

  // estado operativo
  const isRecognizingRef = useRef(false);
  const escucha = useRef(true);

  // control timeouts / intervals
  const startRetryRef = useRef(null);
  const keepAliveRef = useRef(null);

  /* ------------------ utilidades de dibujo ------------------ */
  const iniciarOlaCargando = () => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    const numPuntos = 7;
    const espacio = canvas.width / (numPuntos + 1);
    const centroY = canvas.height / 2;
    let frame = 0;

    const drawOla = () => {
      animationFrameRef.current = requestAnimationFrame(drawOla);
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      for (let i = 0; i < numPuntos; i++) {
        const x = espacio * (i + 1);
        const offset = (i * Math.PI) / 7;
        const radio = 10 + Math.abs(Math.cos(frame / 15 + offset)) * 5;
        ctx.beginPath();
        ctx.arc(x, centroY, radio, 0, Math.PI * 2);
        ctx.fillStyle = `rgb(50, 200, 150)`;
        ctx.fill();
      }
      frame++;
    };

    drawOla();
  };

  const detenerOlaCargando = () => {
    if (animationFrameRef.current) {
      cancelAnimationFrame(animationFrameRef.current);
      animationFrameRef.current = null;
    }
  };

  const stopVisualizer = () => {
    if (animationFrameRef.current) {
      cancelAnimationFrame(animationFrameRef.current);
      animationFrameRef.current = null;
    }
    if (audioContextRef.current) {
      try {
        audioContextRef.current.close();
      } catch {}
      audioContextRef.current = null;
    }
  };

  /* ------------------ SpeechRecognition robusto ------------------ */
  const createRecognition = () => {
    const SpeechRecognition =
      window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      alert("Tu navegador no soporta reconocimiento de voz");
      return;
    }

    if (recognitionRef.current) {
      try {
        recognitionRef.current.onresult = null;
        recognitionRef.current.onend = null;
        recognitionRef.current.onerror = null;
        recognitionRef.current.abort();
      } catch {}
    }

    const recognition = new SpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = "es-ES";

    recognition.onstart = () => {
      isRecognizingRef.current = true;
    };

    recognition.onresult = (event) => {
      for (let i = event.resultIndex; i < event.results.length; ++i) {
        const result = event.results[i];
        if (result.isFinal) {
          const fraseFinal = result[0].transcript.trim().toLowerCase();
          if (
            (fraseFinal.includes("orion") || fraseFinal.includes("orión")) &&
            escucha.current
          ) {
            escucha.current = false;
            setUltimoTexto(fraseFinal);
            detenerEscucha();
            iniciarOlaCargando();

            fetch("http://localhost:8000/activar", {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({ mensaje: fraseFinal }),
            })
              .then((res) => res.json())
              .then((data) => {
                if (data.audio_url) {
                  reproducirRespuesta(`${data.audio_url}?t=${Date.now()}`);
                } else {
                  setTimeout(() => {
                    escucha.current = true;
                    iniciarEscucha();
                  }, 350);
                }
              })
              .catch((err) => {
                console.error("Error fetch activar:", err);
                escucha.current = true;
                setTimeout(() => iniciarEscucha(), 350);
              });
          }
        }
      }
    };

    recognition.onend = () => {
      isRecognizingRef.current = false;
      if (escucha.current) safeStartWithRetries(recognition, 5, 250);
    };

    recognition.onerror = () => {
      isRecognizingRef.current = false;
      if (escucha.current) safeStartWithRetries(recognition, 5, 300);
    };

    recognitionRef.current = recognition;
  };

  const safeStartWithRetries = (recog, retries = 5, delay = 300) => {
    if (!recog || isRecognizingRef.current) return;
    if (startRetryRef.current) {
      clearTimeout(startRetryRef.current);
      startRetryRef.current = null;
    }
    try {
      recog.start();
    } catch {
      if (retries > 0) {
        const nextDelay = Math.min(delay * 2, 2000);
        startRetryRef.current = setTimeout(
          () => safeStartWithRetries(recog, retries - 1, nextDelay),
          delay
        );
      } else {
        try {
          recog.abort();
        } catch {}
        startRetryRef.current = setTimeout(() => {
          createRecognition();
          setTimeout(
            () => safeStartWithRetries(recognitionRef.current, 5, 300),
            300
          );
        }, 400);
      }
    }
  };

  /* ------------------ control escucha ------------------ */
  const detenerEscucha = () => {
    if (startRetryRef.current) clearTimeout(startRetryRef.current);
    escucha.current = false;
    setEscuchando(false);
    const recog = recognitionRef.current;
    if (recog) {
      try {
        recog.abort();
      } catch {
        try {
          recog.stop();
        } catch {}
      }
    }
    stopVisualizer();
    detenerOlaCargando();
  };

  const iniciarEscucha = async () => {
    if (!recognitionRef.current) createRecognition();
    escucha.current = true;
    setEscuchando(true);
    safeStartWithRetries(recognitionRef.current, 6, 250);
    try {
      await startVisualizer();
    } catch (e) {
      console.warn("startVisualizer fallo:", e);
    }
  };

  /* ------------------ reproducir respuesta ------------------ */
  const reproducirRespuesta = async (audioUrl) => {
    detenerOlaCargando();
    stopVisualizer();

    const audio = new Audio(audioUrl);
    audio.crossOrigin = "anonymous";

    if (playbackContextRef.current) {
      try {
        playbackContextRef.current.close();
      } catch {}
    }
    playbackContextRef.current = new (window.AudioContext ||
      window.webkitAudioContext)();

    const source = playbackContextRef.current.createMediaElementSource(audio);
    const analyser = playbackContextRef.current.createAnalyser();
    analyser.fftSize = 64;
    const dataArray = new Uint8Array(analyser.frequencyBinCount);

    source.connect(analyser);
    analyser.connect(playbackContextRef.current.destination);

    const canvas = canvasRef.current;
    const ctx = canvas?.getContext("2d");
    const numPuntos = 7;
    const espacio = canvas ? canvas.width / (numPuntos + 1) : 0;
    const centroY = canvas ? canvas.height / 2 : 0;

    const draw = () => {
      animationFrameRef.current = requestAnimationFrame(draw);
      analyser.getByteFrequencyData(dataArray);
      if (!ctx) return;
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      for (let i = 0; i < numPuntos; i++) {
        const x = espacio * (i + 1);
        const volumen = dataArray[i] || 0;
        const radio = Math.max(8, Math.pow(volumen, 1.3) / 24);
        ctx.beginPath();
        ctx.arc(x, centroY, radio + 3, 0, Math.PI * 2);
        ctx.fillStyle = `rgb(${150 + volumen / 2}, ${50 - volumen}, ${
          200 - volumen / 2
        })`;
        ctx.fill();
      }
    };
    draw();

    await new Promise((resolve) => {
      let safetyTimeout;
      const cleanup = () => {
        if (animationFrameRef.current) {
          cancelAnimationFrame(animationFrameRef.current);
          animationFrameRef.current = null;
        }
        try {
          playbackContextRef.current?.close();
        } catch {}
        playbackContextRef.current = null;
        clearTimeout(safetyTimeout);
        resolve();
      };

      audio.play().catch((err) => {
        console.warn("audio.play fallo:", err);
        cleanup();
      });

      audio.onended = cleanup;
      audio.onpause = cleanup;

      // timeout basado en duración
      safetyTimeout = setTimeout(
        cleanup,
        (isNaN(audio.duration) ? 60 : audio.duration + 5) * 1000
      );
    });

    setTimeout(() => {
      escucha.current = true;
      iniciarEscucha();
    }, 400);
  };

  /* ------------------ visualizador micrófono ------------------ */
  const startVisualizer = async () => {
    if (audioContextRef.current) {
      try {
        audioContextRef.current.close();
      } catch {}
    }
    audioContextRef.current = new (window.AudioContext ||
      window.webkitAudioContext)();

    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    const source = audioContextRef.current.createMediaStreamSource(stream);

    analyserRef.current = audioContextRef.current.createAnalyser();
    analyserRef.current.fftSize = 64;
    dataArrayRef.current = new Uint8Array(analyserRef.current.frequencyBinCount);
    source.connect(analyserRef.current);

    const canvas = canvasRef.current;
    const ctx = canvas?.getContext("2d");
    const numPuntos = 7;
    const espacio = canvas ? canvas.width / (numPuntos + 1) : 0;
    const centroY = canvas ? canvas.height / 2 : 0;

    const draw = () => {
      animationFrameRef.current = requestAnimationFrame(draw);
      analyserRef.current.getByteFrequencyData(dataArrayRef.current);
      if (!ctx) return;
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      for (let i = 0; i < numPuntos; i++) {
        const x = espacio * (i + 1);
        const volumen = dataArrayRef.current[i] || 0;
        const radio = Math.max(8, Math.pow(volumen, 1.3) / 24);
        ctx.beginPath();
        ctx.arc(x, centroY, radio, 0, Math.PI * 2);
        ctx.fillStyle = `rgb(${100 + volumen}, ${150 + volumen / 2}, ${
          200 - volumen / 2
        })`;
        ctx.fill();
      }
    };
    draw();
  };

  /* ------------------ botón ------------------ */
  const toggleEscucha = async () => {
    setBotonVisible(false);
    if (!escuchando) {
      escucha.current = true;
      setEscuchando(true);
      safeStartWithRetries(recognitionRef.current, 6, 250);
      try {
        await startVisualizer();
      } catch (e) {
        console.warn("startVisualizer toggle fallo:", e);
      }
    } else {
      escucha.current = false;
      detenerEscucha();
    }
  };

  /* ------------------ useEffect ------------------ */
  useEffect(() => {
    createRecognition();
    keepAliveRef.current = setInterval(() => {
      if (escucha.current && !isRecognizingRef.current) {
        if (recognitionRef.current) {
          safeStartWithRetries(recognitionRef.current, 5, 300);
        } else {
          createRecognition();
          setTimeout(
            () => safeStartWithRetries(recognitionRef.current, 5, 300),
            300
          );
        }
      }
    }, 15000);

    return () => {
      clearInterval(keepAliveRef.current);
      clearTimeout(startRetryRef.current);
      try {
        recognitionRef.current?.abort();
      } catch {}
      stopVisualizer();
      detenerOlaCargando();
      try {
        playbackContextRef.current?.close();
      } catch {}
    };
  }, []);

  /* ------------------ render ------------------ */
  return (
    <div className="flex flex-col items-center">
      {botonVisible && (
        <button
          onClick={toggleEscucha}
          className="mb-6 px-6 py-3 rounded-full text-xl font-bold shadow-xl bg-green-500 hover:bg-green-600 transition"
        >
          Escuchar
        </button>
      )}
      <canvas
        ref={canvasRef}
        width={500}
        height={300}
        className="bg-black rounded-lg"
      ></canvas>
      {ultimoTexto && (
        <p className="mt-6 text-lg text-green-400">
          Último texto capturado: <br />
          <span className="italic">"{ultimoTexto}"</span>
        </p>
      )}
    </div>
  );
};

export default OrionListener;
