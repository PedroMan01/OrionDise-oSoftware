
import { useEffect, useRef, useState } from "react";

const MobileListener = () => {
    const [isListening, setIsListening] = useState(false);
    const [hasPermission, setHasPermission] = useState(null);
    const [transcript, setTranscript] = useState("");
    const [lastFinalText, setLastFinalText] = useState("");
    const [status, setStatus] = useState("Listo");
    const [errorMsg, setErrorMsg] = useState("");
    const [isProcessing, setIsProcessing] = useState(false);


    // Config: "Wake Word" vs "Push to Talk"
    const [mode, setMode] = useState("wakeword"); // 'wakeword' | 'push'

    const recognitionRef = useRef(null);
    const audioRef = useRef(null);
    const shouldListenRef = useRef(false);

    // Checks
    const isSecure = window.isSecureContext;
    const browserSupport = !!(window.SpeechRecognition || window.webkitSpeechRecognition);

    useEffect(() => {
        if (!isSecure) {
            setErrorMsg("⚠️ Inseguro (HTTP). Usa HTTPS o configura chrome://flags.");
            setStatus("Error Seguridad");
        }

        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!SpeechRecognition) return;

        const recognition = new SpeechRecognition();
        // NOTE: On Mobile, 'continuous = true' can be buggy.
        // We will use 'continuous = false' and rely on our manual restart loop.
        recognition.continuous = false;
        recognition.interimResults = true;
        recognition.lang = "es-ES";

        recognition.onstart = () => {
            console.log("🎤 Recognition STARTED");
            setStatus(mode === 'wakeword' ? "Esperando 'Orion'..." : "Escuchando...");
            setErrorMsg("");
            setIsListening(true);
        };

        recognition.onend = () => {
            console.log("🛑 Recognition ENDED. Should listen:", shouldListenRef.current);
            setIsListening(false);

            if (shouldListenRef.current && !isProcessing) {
                setStatus("Reiniciando...");
                setTimeout(() => {
                    if (shouldListenRef.current) safeStart();
                }, 300);
            } else if (!isProcessing) {
                setStatus("Pausado");
            }
        };

        recognition.onerror = (event) => {
            if (event.error === 'not-allowed') {
                setErrorMsg("Permiso Micro Denegado");
                setHasPermission(false);
                shouldListenRef.current = false;
            } else if (event.error === 'no-speech') {
                // Ignore
            } else {
                setErrorMsg("Error Reconocimiento: " + event.error);
            }
        };

        recognition.onresult = (event) => {
            let interimTranscript = '';

            for (let i = event.resultIndex; i < event.results.length; ++i) {
                const result = event.results[i];
                const text = result[0].transcript;

                if (result.isFinal) {
                    const finalPhrase = text.trim();
                    console.log("📝 Final:", finalPhrase);
                    setLastFinalText(finalPhrase);
                    setTranscript("");

                    if (mode === 'wakeword') {
                        checkWakeWord(finalPhrase);
                    } else {
                        // Push to talk: send everything that is final
                        handleCommand(finalPhrase);
                    }
                } else {
                    interimTranscript += text;
                }
            }

            if (interimTranscript) {
                setTranscript(interimTranscript);
            }
        };

        recognitionRef.current = recognition;

        // Auto-restart if we should be listening (and aren't processing)
        if (shouldListenRef.current && !isProcessing) {
            safeStart();
        }

        return () => {
            // Do NOT reset shouldListenRef.current = false here, 
            // because we want to resume if this effect re-runs (e.g. mode change or processing finish).
            recognition.abort();
        };
    }, [isProcessing, mode]);

    const containsWakeWord = (text) => {
        const lower = text.toLowerCase();
        return [
            "orion", "orión", "marión", "arion", "avión", "camión",
            "horion", "bryan", "brian", "oreon", "oriol", "gorrion"
        ].some(w => lower.includes(w));
    };

    const checkWakeWord = (text) => {
        if (containsWakeWord(text)) {
            if (window.navigator.vibrate) window.navigator.vibrate(100);
            setStatus("¡Orion Detectado!");
            handleCommand(text);
        }
    };

    const safeStart = () => {
        try {
            recognitionRef.current.start();
        } catch (e) { /* ignore */ }
    };

    const handleCommand = (text) => {
        if (!text) return;
        console.log("🚀 Enviando:", text);
        setErrorMsg(""); // Clear previous errors

        // Pause listening logic
        shouldListenRef.current = false;
        if (recognitionRef.current) recognitionRef.current.stop();

        // Simulate "Processing" in UI immediately
        setStatus("Procesando...");
        setIsProcessing(true);

        sendToBackend(text);
    };

    const sendToBackend = (text) => {
        setStatus("Procesando...");
        const userId = localStorage.getItem("user_id") || 1;
        const protocol = window.location.protocol;
        const host = window.location.hostname;
        const port = window.location.port || "8000";

        fetch(`${protocol}//${host}:8000/activar`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                mensaje: text,
                user_id: parseInt(userId)
            }),
        })
            .then((res) => res.json())
            .then((data) => {
                console.log("📥 Recibido:", data);
                if (data.audio_url) {

                    let finalUrl = data.audio_url;
                    if (!finalUrl.startsWith("http")) {
                        finalUrl = `${protocol}//${host}:8000${data.audio_url}`;
                    }

                    playAudio(`${finalUrl}?t=${Date.now()}`);
                } else {
                    setStatus("Listo (Sin Audio)");
                    setIsProcessing(false);
                    shouldListenRef.current = true;
                    safeStart();
                }
            })
            .catch((err) => {
                console.error("Fetch Error:", err);
                setErrorMsg("Error Red: " + err.message);
                setStatus("Error");
                setIsProcessing(false);
                setTimeout(() => {
                    shouldListenRef.current = true;
                    safeStart();
                }, 2000);
            });
    };

    const playAudio = (url) => {
        setStatus("Hablando...");
        console.log("🔊 Intentando reproducir:", url);

        if (audioRef.current) {
            audioRef.current.pause();
            audioRef.current = null;
        }
        const audio = new Audio(url);
        audioRef.current = audio;

        // This promise handles the "Autoplay" error
        const playPromise = audio.play();

        if (playPromise !== undefined) {
            playPromise.catch(e => {
                console.error("Autoplay prevent:", e);
                setErrorMsg(`⚠️ Bloqueado por navegador. Toca el círculo para reintentar.`);
                setIsProcessing(false);
                setStatus("Error Audio");
            });
        }

        audio.onended = () => {
            setStatus(mode === 'wakeword' ? "Esperando 'Orion'..." : "Listo");
            setIsProcessing(false);
            shouldListenRef.current = true;
            safeStart();
            setErrorMsg(""); // Clear debug msg
        };
    };

    const toggleListening = () => {
        if (!isSecure || !browserSupport) return;

        if (shouldListenRef.current) {
            // Manual Stop
            shouldListenRef.current = false;
            recognitionRef.current?.stop();
            setStatus("Inactivo");
        } else {
            // Manual Start
            shouldListenRef.current = true;
            setHasPermission(true);
            safeStart();
            if ('wakeLock' in navigator) {
                navigator.wakeLock.request('screen').catch(console.error);
            }
        }
    };

    // --- RENDER ---
    return (
        <div className="flex flex-col h-[100dvh] w-full bg-black text-white overflow-hidden font-sans">

            {/* Header */}
            <div className="flex-none p-4 bg-gray-900 border-b border-gray-800 flex justify-between items-center z-10">
                <div className="flex items-center space-x-2">
                    <div className={`w-3 h-3 rounded-full ${shouldListenRef.current ? 'bg-green-500 animate-pulse' : 'bg-red-500'}`}></div>
                    <span className="font-bold tracking-widest text-xs">ORION MOBILE</span>
                </div>
                {/* Mode Toggle */}
                <button
                    onClick={() => setMode(mode === 'wakeword' ? 'push' : 'wakeword')}
                    className="text-xs px-2 py-1 bg-gray-800 rounded border border-gray-700 uppercase"
                >
                    {mode === 'wakeword' ? "Modo: Keyword" : "Modo: Directo"}
                </button>
            </div>

            {/* Content */}
            <div className="flex-1 flex flex-col justify-center items-center relative p-6 space-y-6">

                {/* Visualizer / Button */}
                <div
                    onClick={toggleListening}
                    className={`relative w-64 h-64 rounded-full flex items-center justify-center transition-all duration-300 border-4 cursor-pointer
                        ${shouldListenRef.current ? "border-green-500/50 bg-green-900/20" : "border-gray-700 bg-gray-900"}
                        ${isProcessing ? "animate-pulse border-blue-500" : ""}
                    `}
                >
                    {/* Ring Animations */}
                    {shouldListenRef.current && !isProcessing && (
                        <div className="absolute inset-0 rounded-full border-4 border-green-500 opacity-20 animate-ping"></div>
                    )}

                    <span className="text-5xl z-10 transition-transform active:scale-95 text-white/90">
                        {isProcessing ? "⏳" : shouldListenRef.current ? "🎙️" : "🛑"}
                    </span>
                </div>

                {/* Status & Error */}
                <div className="text-center min-h-[40px]">
                    <p className={`text-xl font-medium ${status.includes("Error") ? "text-red-400" : "text-blue-400"}`}>
                        {status}
                    </p>
                    {errorMsg && <p className="text-xs text-red-500 mt-1 bg-red-900/40 p-1 rounded max-w-xs mx-auto text-left whitespace-pre-wrap break-all">{errorMsg}</p>}
                </div>

                {/* Live Transcript */}
                <div className="w-full max-w-xs bg-gray-800/50 p-2 rounded text-center min-h-[3rem] flex items-center justify-center border border-gray-700">
                    <p className="text-lg italic text-gray-300">
                        "{transcript || lastFinalText || "..."}"
                    </p>
                </div>



            </div>

            <div className="p-4 text-center text-gray-600 text-xs pb-4">
                {mode === 'wakeword'
                    ? `Di "Orion", "Avión" o "Camión" para activar.`
                    : "Habla y la frase se enviará al pausar."}
            </div>
        </div>
    );
};

export default MobileListener;
