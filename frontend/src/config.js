const getBaseUrl = () => {
    const host = window.location.hostname;
    // Si estamos en localhost, usa localhost. Si es una IP (ej: 192.168.x o 100.x), usa esa IP.
    // Esto asume que el backend corre en el puerto 8000 en la misma máquina/IP.
    return `http://${host}:8000`;
};

export const API_URL = getBaseUrl();
console.log("🔧 [Config] API_URL detected:", API_URL);
// Ajustar si tu endpoint WS es distinto, pero usualmente sigue el mismo host
export const WS_URL = API_URL.replace("http", "ws") + "/ws";
