import React, { useState, useEffect } from "react";

const palabras = [
  "CASUAL", "CARGAR", "CANTAR", "CABLES",
  "CAMINO", "CIELOS", "CEBADA", "CLAVES",
  "CIRCOS", "CINEMA", "CADENA", "CREDOS",
];

const caracteresRuido = "¡!@#$%^&*()_+=-{}[]<>¿?/|°´¨~`\\:;',.";

const compararLikeness = (palabra, clave) => {
  let match = 0;
  for (let i = 0; i < palabra.length; i++) {
    if (palabra[i] === clave[i]) match++;
  }
  return match;
};

const generarLinea = (palabrasIncluidas, setHandlers) => {
  let linea = "";
  const longitudLinea = 100;
  const palabra = palabrasIncluidas.length > 0 ? palabrasIncluidas.pop() : null;
  const posicion = palabra ? Math.floor(Math.random() * (longitudLinea - palabra.length)) : -1;

  for (let i = 0; i < longitudLinea; i++) {
    if (i === posicion && palabra) {
      setHandlers.push({ inicio: i, fin: i + palabra.length, palabra });
      linea += palabra;
      i += palabra.length - 1;
    } else {
      linea += caracteresRuido[Math.floor(Math.random() * caracteresRuido.length)];
    }
  }

  return linea;
};

const CriptMinigame = () => {
  const [clave, setClave] = useState("");
  const [intentos, setIntentos] = useState(4);
  const [mensaje, setMensaje] = useState("");
  const [bloqueado, setBloqueado] = useState(false);
  const [pantalla, setPantalla] = useState([]);

  useEffect(() => {
    const nuevaClave = palabras[Math.floor(Math.random() * palabras.length)];
    setClave(nuevaClave);

    const palabrasSeleccionadas = [...palabras].sort(() => 0.5 - Math.random()).slice(0, 10);
    const handlers = [];

    const lineas = Array.from({ length: 16 }, () =>
      generarLinea(palabrasSeleccionadas, handlers)
    );

    setPantalla(lineas.map((linea, idx) => ({ texto: linea, idx })));
    setClickables(handlers);
  }, []);

  const [clickables, setClickables] = useState([]);

  const manejarClick = (palabra) => {
    if (bloqueado) return;

    if (palabra === clave) {
      setMensaje("🔓 ¡Acceso concedido!");
      fetch("http://localhost:8000/encriptado", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ mensaje: "Desencriptado" }),
      })
      setBloqueado(true);
    } else {
      const likeness = compararLikeness(palabra, clave);
      setIntentos((prev) => prev - 1);
      setMensaje(`❌ Caracteres coincidentes = ${likeness}`);
      if (intentos - 1 === 0) {
        setMensaje(`⛔ Acceso denegado. La clave era: ${clave}`);
        setBloqueado(true);
      }
    }
  };

  return (
    <div className="p-4 bg-black text-green-600 font-mono min-h-screen whitespace-pre text-sm terminal">
      <h1 className="text-xl mb-2">== TERMINAL DE SEGURIDAD ==</h1>
      <p className="mb-3">INTENTOS RESTANTES: {intentos}</p>
      {pantalla.map(({ texto, idx }) => {
        const elementos = [];
        for (let i = 0; i < texto.length; ) {
          const clickeable = clickables.find(
            (c) => c.inicio === i && pantalla[idx].texto.includes(c.palabra)
          );
          if (clickeable) {
            elementos.push(
              <span
                key={`${idx}-${i}`}
                className="text-yellow-300 cursor-pointer hover:underline"
                onClick={() => manejarClick(clickeable.palabra)}
              >
                {clickeable.palabra}
              </span>
            );
            i += clickeable.palabra.length;
          } else {
            elementos.push(
              <span key={`${idx}-${i}`}>{texto[i]}</span>
            );
            i++;
          }
        }
        return <div key={idx}>{elementos}</div>;
      })}
      <div className="mt-4 text-lg">{mensaje}</div>
    </div>
  );
};

export default CriptMinigame;

