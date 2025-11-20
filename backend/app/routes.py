from fastapi import APIRouter, Request
from app.services.central import IA
import os


router = APIRouter()



@router.post("/activar")
async def activar_orion(request: Request):
    data = await request.json()
    mensaje = data.get("mensaje", "")

    print(f"🛰️ Texto recibido: {mensaje}")

    # Añade print antes de llamar a IA
    print("Llamando a IA...")
    Respuesta_IA = await IA(texto=mensaje)
    print("Respuesta IA recibida")

    print(f"🛰️ Respuesta: {Respuesta_IA}")

    return {
        "text": Respuesta_IA["text"],
        "audio_url": "http://localhost:8000/audio/output0_0.wav"
    }

@router.post("/encriptado")
async def resolucion(request: Request):
    data = await request.json()
    mensaje = data.get("mensaje", "")
    print(f"🛰️ Texto recibido: {mensaje}")

    archivo_path = os.path.join(os.path.dirname(__file__), "memory", "Variables.txt")

    # Leer y modificar
    with open(archivo_path, "r", encoding="utf-8") as f:
        lineas = f.read().split("//")

    nuevas_lineas = []
    for linea in lineas:
        if not linea.strip():
            continue
        clave, valor = linea.strip().split(":", 1)
        if clave == "Encriptado":
            nuevas_lineas.append(f"{clave}:{mensaje}")
        else:
            nuevas_lineas.append(f"{clave}:{valor}")

    # Escribir nuevamente
    with open(archivo_path, "w", encoding="utf-8") as f:
        f.write("//" + "//".join(nuevas_lineas))

    return {"text": mensaje}

@router.post("/sensor")
async def resolucion(request: Request):
    data = await request.json()
    mensaje = data.get("mensaje", "")
    print(f"🛰️ Texto recibido: {mensaje}")

    archivo_path = os.path.join(os.path.dirname(__file__), "memory", "Variables.txt")

    # Leer y modificar
    with open(archivo_path, "r", encoding="utf-8") as f:
        lineas = f.read().split("//")

    nuevas_lineas = []
    for linea in lineas:
        if not linea.strip():
            continue
        clave, valor = linea.strip().split(":", 1)
        if clave == "Sensor":
            nuevas_lineas.append(f"{clave}:{mensaje}")
        else:
            nuevas_lineas.append(f"{clave}:{valor}")

    # Escribir nuevamente
    with open(archivo_path, "w", encoding="utf-8") as f:
        f.write("//" + "//".join(nuevas_lineas))

    return {"text": mensaje}

@router.post("/movil")
async def resolucion(request: Request):
    return {"text"}

@router.post("/Chat")
async def resolucion(request: Request):
    return {"text"}
@router.post("/ChatVoz")
async def resolucion(request: Request):
    return {"text"}
@router.post("/Asistente")
async def resolucion(request: Request):
    return {"text"}

