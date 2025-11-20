from dotenv import load_dotenv
from datetime import datetime
from pytz import timezone
import os
from pathlib import Path
from .L_frontal import LLM
from .Lengua import generar_audio
import asyncio

timezone = timezone('America/Santiago')

load_dotenv()
api_key = os.getenv("API_OPENROUTER")
llm = LLM(api_key)
MEMORIA_PATH = Path(__file__).parent.parent / "memory"

async def IA(nombre_usuario = "Tripulación", id = 0, texto = None, PAD = False, isMuted = "False", isPublic = "False"):
    fecha_hora_actual = datetime.now(timezone).strftime("%d/%m/%Y %H:%M")
    print(f"Hora actual: {fecha_hora_actual}, mensaje: {texto}")

    #------Contexto de la conversación--------------
    if not os.path.exists(f"{MEMORIA_PATH}/conversacion{id}.txt"):
        with open(f"{MEMORIA_PATH}/conversacion{id}.txt", 'w', encoding='utf-8') as archivo:
            archivo.write("/%/")

    with open(f"{MEMORIA_PATH}/conversacion{id}.txt", 'r', encoding='utf-8') as archivo:
        conversacion = archivo.read()
    #------Fin contexto de la conversación--------------

    Memoria = conversacion.split("/%/")
    texto_dialogo = f"*##{fecha_hora_actual} {nombre_usuario}: {texto}##*"
    Memoria[0]+= f"\n{texto_dialogo}"

    #------Interacciones progrmadas--------------
    if "orión identifícate" in texto.lower() or "orion identifícate" in texto.lower() or "orión, identifícate" in texto.lower() or "orion, identifícate" in texto.lower():
        print("Orion, identificate")
        respuesta_IA = llm.process_functions(
            "Orión, debes hacer una introducción de ti y la tripulación según el registro de la Tripulacion con tu personalidad habitual. "
            "Incluye tu nombre completo y propósito. Añade un comentario sarcástico sobre el estado actual de la nave, "
            "se estrelló y hay varios sistemas fallando, y haz una broma sobre el capitán Pedro Manríquez, que está de cumpleaños. "
            "Finaliza recordando a la tripulación que pueden llamarte si necesitan ayuda, con un tono dramático pero cómico.",
            Memoria[0], Memoria[1]
        )
    elif "finalizar programa" in texto.lower():
        respuesta_IA = llm.process_functions(texto, Memoria[0], Memoria[1])
    else:
        respuesta_IA = llm.process_functions(texto, Memoria[0], Memoria[1])
    #------Fin interacciones progrmadas--------------
    await generar_audio(respuesta_IA, id, 0)
    #------actualizar Memoria--------------
    Memoria[0]+= f"\n{respuesta_IA}"
    if len(Memoria[0]) >= 2_000:
        if not os.path.exists(f"{MEMORIA_PATH}/Pensar{id}.txt"):
            with open(f"{MEMORIA_PATH}/Pensar{id}.txt", 'w', encoding='utf-8') as archivo:
                archivo.write("")
        with open(f"{MEMORIA_PATH}/Pensar{id}.txt", 'r', encoding='utf-8') as archivo:
            Pensamiento = archivo.read()
        resumen = ""

        Pensamiento = ""
        with open(f"{MEMORIA_PATH}/Pensar{id}.txt", "w", encoding="utf-8") as archivo:
            archivo.write(Pensamiento)
        temp = Memoria[0][-0:]
        for a in range(2, len(temp)):
            if temp[a] == "/":
                if temp[a+3] == "/":
                    if temp[a+8] == " ":
                        if temp[a+11] == ":":
                            if temp[a+14] == " ":
                                Memoria[0] = temp[a-2:]
                                break
    conversacion = "/%/".join(Memoria)   
    with open(f"{MEMORIA_PATH}/conversacion{id}.txt", "w", encoding="utf-8") as archivo:
        archivo.write(conversacion)
    return {"result": "ok", "text": respuesta_IA}