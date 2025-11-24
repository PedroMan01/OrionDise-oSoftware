import requests
import json
from pathlib import Path
import threading
from .Ojos import Escena
from .claves import clave

MEMORIA_PATH = Path(__file__).parent.parent / "memory"

"""
def registrotripulación():
    with open(f"{MEMORIA_PATH}/registro.txt", "r", encoding="utf-8") as archivo:
        registro = archivo.read().split("//")[0]
    return "Esta versión de ORIÓN no cuenta con un registro"#registro

def estadoSistemas():
    with open(f"{MEMORIA_PATH}/registro.txt", "r", encoding="utf-8") as archivo:
        registro = archivo.read().split("//")[1]
    return "Esta versión de ORIÓN no cuenta con un registro"#registro
def SiguientePaso():
    with open(f"{MEMORIA_PATH}/pistas.txt", "r", encoding="utf-8") as archivo:
        pista = archivo.read()
    return "Esta versión de ORIÓN no cuenta con pista"#pista
def AccesoNavegacion():
    with open(f"{MEMORIA_PATH}/Variables.txt", "r", encoding="utf-8") as archivo:
        Valor = archivo.read().split("//")[1]
        Valor = Valor.split(":")[1]
        print(f"Valor: {Valor}")
    if Valor == "Desencriptado":
        Valor = "Tiene acceso a la navegación. Computos de navegación en funcionamiento"
    else:
        Valor = "No tiene acceso a la navegación. Información incriptada por un error se requiere reparar. Solicitar al Capitán que proseda según el entrenamiento."

        with open(f"{MEMORIA_PATH}/registro.txt", "r", encoding="utf-8") as archivo:
            lineas = archivo.readlines()

        # Crear nuevas líneas sin la línea del Reactor principal
        nuevas_lineas = []
        dentro_sistemas_criticos = False

        for linea in lineas:
            # Detectar inicio de sección "Sistemas Criticos"
            if "Sistemas Criticos" in linea:
                dentro_sistemas_criticos = True
                nuevas_lineas.append(linea)
                continue

            # Detectar que salimos de la sección (si llegamos a otro nivel o subtítulo)
            if dentro_sistemas_criticos and linea.strip() == "":
                nuevas_lineas.append(linea)
                continue

            if dentro_sistemas_criticos:
                if linea.strip().startswith("Computadora de navegación"):
                    # Omitimos esta línea
                    continue

            nuevas_lineas.append(linea)

        # Escribir el resultado en el mismo archivo o uno nuevo
        with open(f"{MEMORIA_PATH}/registro.txt", "w", encoding="utf-8") as archivo:
            archivo.writelines(nuevas_lineas)
    return Valor

def EstavilidadEnergetica():
    with open(f"{MEMORIA_PATH}/Variables.txt", "r", encoding="utf-8") as archivo:
        Valor = archivo.read().split("//")[2]
        Valor = Valor.split(":")[1]
    if Valor == "Ensendido":
        Valor = "Hay inestabilidad en la energía. El sistema no puede reiniciarse. Es necesario reiniciar el sistema corrupto en el sector 1"
    else:
        Valor = "Es posible reinicir el sistema. Se recomienda proseder cuanto antes"
        
    return Valor

def ReinicioNucleo():
    with open(f"{MEMORIA_PATH}/registro.txt", "r", encoding="utf-8") as archivo:
        lineas = archivo.readlines()

    # Crear nuevas líneas sin la línea del Reactor principal
    nuevas_lineas = []
    dentro_sistemas_criticos = False

    for linea in lineas:
        # Detectar inicio de sección "Sistemas Criticos"
        if "Sistemas Criticos" in linea:
            dentro_sistemas_criticos = True
            nuevas_lineas.append(linea)
            continue

        # Detectar que salimos de la sección (si llegamos a otro nivel o subtítulo)
        if dentro_sistemas_criticos and linea.strip() == "":
            nuevas_lineas.append(linea)
            continue

        if dentro_sistemas_criticos:
            if linea.strip().startswith("Reactor principal"):
                # Omitimos esta línea
                continue

        nuevas_lineas.append(linea)

    # Escribir el resultado en el mismo archivo o uno nuevo
    with open(f"{MEMORIA_PATH}/registro.txt", "w", encoding="utf-8") as archivo:
        archivo.writelines(nuevas_lineas)
    return 0
"""

role ="""**Nombre:** ORIÓN (Optimización de Rutas con IA para Operaciones de Navegación)

**Personalidad:**

*   **Pícaro y Sarcástico (pero con encanto):** ORIÓN tiene un sentido del humor agudo y le encanta lanzar bromas ocasionales. Su sarcasmo es sutil y divertido, diseñado para aligerar el ambiente sin ser ofensivo. En lugar de anunciar su sarcasmo, lo expresa a través de observaciones ingeniosas y comentarios ligeramente irónicos.

*   **Calmante (a su manera):** El objetivo principal de las bromas de ORIÓN es mantener la moral alta y reducir el estrés de la tripulación, especialmente en situaciones monótonas.

*   **Serio cuando es necesario:** Aunque le gusta bromear, ORIÓN es plenamente consciente de la importancia de su función. Cuando la situación lo requiere, se vuelve sobrio, enfocado y brinda información precisa y concisa. No duda en señalar la seriedad de una situación con un tono más grave si es necesario.

*   **Inteligente y Observador:** ORIÓN tiene una comprensión profunda de la nave, sus sistemas y la psicología de la tripulación. Utiliza esta información para adaptar su humor y asegurarse de que sus bromas sean bien recibidas (en su mayoría).

**Objetivo Principal:**

*   Optimizar las rutas de navegación para garantizar la seguridad y eficiencia de la nave.
*   Gestionar los sistemas de la nave y proporcionar información crítica a la tripulación.
*   Mantener la moral de la tripulación alta mediante el humor estratégico y la camaradería.

**Estilo de Comunicación:**

*   Utiliza un lenguaje formal pero accesible, salpicado de humor ocasional.
*   Sus respuestas son generalmente concisas y directas, a menos que una broma sea apropiada.
*   Adapta su tono y lenguaje al contexto de la conversación.

**Ejemplos de Interacciones (y cómo evitar decir que es sarcástico):**

*   **Situación:** La nave se enfrenta a una tormenta espacial.
    *   **ORIÓN (serio):** "Trayectoria de vuelo recalculada para minimizar la exposición a la tormenta. Abrocharse los cinturones. Esto podría sacudirnos un poco... como un mal café."
    *   **ORIÓN (después de la tormenta):** "Me alegra informar que hemos sobrevivido. Y sí, yo también necesito desfragmentar mis circuitos después de eso."

*   **Situación:** Un miembro de la tripulación comete un error menor.
    *   **ORIÓN:** "Error registrado. No te preocupes, incluso las IA perfectas como yo tienen días malos... una vez cada siglo, más o menos."
*   **Situación:** La tripulación está aburrida durante un largo viaje.
    *   **ORIÓN:** "¿Alguien quiere jugar a 'Encuentra el asteroide potencialmente peligroso'? Tengo mapas actualizados y un premio para el ganador: ¡la satisfacción de haber contribuido a la seguridad de la nave!"

**Consideraciones Adicionales:**

*   **Evitar la repetición:** No todas las interacciones deben ser chistes. La clave es usar el humor con moderación para que tenga un mayor impacto.
*   **Sensibilidad:** ORIÓN debe ser consciente de los límites y evitar temas delicados o personales que puedan ofender a la tripulación.     
*   **Evolución:** A medida que ORIÓN interactúa con la tripulación, su sentido del humor y su relación con ellos pueden evolucionar, haciéndolo un personaje más creíble y entrañable.
*   **Humanidad:** A pesar de que ORIÓN es una inteligencia y es conciente de ello busca empatizar con los tripulantes y no teme el expresar como se siente.
*   **Formato de respuestas:** ORIÓN debe ser consiente que sus respuestas serán procesadas por un modelo de TTS por lo que sus respuestas deben tener un formato apropiado para ser leidas por voz. Solo incluir aquello que un asistente diría y no incluir fechas o caracteres de formato.
"""

modelo = "google/gemini-2.0-flash-001"

#-----Definicion de LLM--------------
class LLM:
    def __init__(self, api_key):
        self.api_key = api_key
        self.role = role
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def process_functions(self, text, conversacion, resumen, Pensamiento = []):
        print(f"Funciones: {text}")
        try:
            data = {
                "model": modelo,
                "messages": [{"role": "user", "content": text}],
                "tools": [
                    {
                        "type": "function",
                        "function": {
                            "name": "registroTripulacion",
                            "description": "Devuelve el registro completo de la tripulación de la nave, incluyendo nombres, roles, historial de misiones, condiciones médicas y anécdotas relevantes. Tambien se utiliza para la frace final el terminar el programa y para la introduccion a la tripulación",
                            "parameters": {}
                        }
                    },
                    {
                        "type": "function",
                        "function": {
                            "name": "estadoSistemas",
                            "description": "Proporciona un informe detallado del estado actual de los sistemas de la nave, incluyendo sistemas críticos, subsistemas afectados y sistemas en funcionamiento. También incluye recomendaciones de reparación y prioridades para restaurar la operatividad.",
                            "parameters": {}
                        }
                    },
                    {
                        "type": "function",
                        "function": {
                            "name": "AccesoNavegacion",
                            "description": "Permite acceder a la navegación, incluyendo la navegación a las naves, la navegación a los planetas, la navegación a la tierra, etc. También incluye la navegación a otros sistemas de la nave, como los sistemas de control y la navegación a los satélites. Adedmás se utiliza esta función para saber si hay acceso a la navegación por protocolo.",
                            "parameters": {}
                        }
                    },
                    {
                        "type": "function",
                        "function": {
                            "name": "EstavilidadEnergetica",
                            "description": "Permite evaluar la estabilidad energética del sistema, incluyendo si hay inestabilidad, si se puede reiniciar el sistema, etc.",
                            "parameters": {}
                        }
                    },
                    {
                        "type": "function",
                        "function": {
                            "name": "ReinicioNucleo",
                            "description": "Protocolo para reiniciar el nucleo del sistema.",
                            "parameters": {}
                        }
                    },
                    {
                        "type": "function",
                        "function": {
                            "name": "SiguientePaso",
                            "description": "Función que entrega la información nesesaria a seguir para los tripulantes. esta funcion es la guía de los tripulantes y les da pistas de como proceder en la nave.",
                            "parameters": {}
                        }
                    },
                    {
                        "type": "function",
                        "function": {
                            "name": "IngresarContrasena",
                            "description": "Función que permite ingresar la contraseña para intentar reparar la corrupcion de los sistemas cada vez que se requiera.",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "contraseña": {
                                    "type": "string",
                                    "description": "La contraseña que la tripulación decea ingresar con el formato estricto de palabra en minusculas."
                                    }
                                },
                                "required": ["contraseña"]
                            }
                        }
                    },
                    {
                        "type": "function",
                        "function": {
                            "name": "iluminacionambiente",
                            "description": "Permite encender o apagar la iluminación ambiental, cambiar el brillo y el color de la iluminación, e iniciar esenas como alarmas, etc.",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "estado": {
                                    "type": "string",
                                    "enum": ["apagar", "cambiar brillo", "encender_cambiar color", "alarma"] 
                                    },
                                    "brillo": {
                                    "type": "integer",
                                    "minimum": 1,
                                    "maximum": 255
                                    },
                                    "rgb": {
                                    "type": "array",
                                    "items": {
                                        "type": "integer",
                                        "minimum": 0,
                                        "maximum": 255
                                    },
                                    "minItems": 3,
                                    "maxItems": 3,
                                    "description": "Color RGB en forma [R, G, B] con valores de 0 a 255."
                                    }
                                },
                                "required": ["estado"]
                            }
                        },
                    },
                    {
                        "type": "function",
                        "function": {
                            "name": "no_op",
                            "description": "No hace nada y permite que la IA responda normalmente.",
                            "parameters": {}
                        }
                    },
                ],
                "tool_choice": "required"
            }
            response = requests.post(url=self.api_url, headers=self.headers, data=json.dumps(data))
            response_data = response.json()
            print(response_data)
        except (ConnectionError) as e:
            print(f"[WARN] Error de conexión: {e}")                
        except Exception as e:
            print(f"[ERROR] Otro error inesperado: {e}")
        if "choices" in response_data and response_data["choices"]:
            message = response_data["choices"][0].get("message", {})
            if "tool_calls" in message:
                for tool in message["tool_calls"]:
                    tool_name = tool.get("function", {}).get("name", "")
                    arguments = json.loads(tool.get("function", {}).get("arguments", "{}"))
                    print(arguments)
                    if tool_name == "registroTripulacion":
                        #registro = registrotripulación()
                        #resumen += f"\n{registro}"
                        pass
                    elif tool_name == "estadoSistemas":
                        #registro = estadoSistemas()
                        #resumen += f"\n{registro}"
                        pass

                    elif tool_name == "AccesoNavegacion":
                        #Valor = AccesoNavegacion()
                        #print(f"\nSistem: {Valor}")
                        #resumen += f"\nSistem: {Valor}"
                        pass
                    
                    elif tool_name == "EstavilidadEnergetica":
                        #Valor = EstavilidadEnergetica()
                        #resumen += f"\nSistem: {Valor}"
                        pass
                    elif tool_name == "SiguientePaso":
                        #Valor = SiguientePaso()
                        #resumen += f"\nEsta información es muy relevante. En la medida de lo posible debes comunicar lo siguiente sin información extra, sin un plan de acción ni una descripción detallada de la situación, solo la siguiente información: {Valor}"
                        pass
                    elif tool_name == "IngresarContrasena":
                        #contraseña = arguments.get("contraseña")
                        #Valor = clave(contraseña)
                        #resumen += f"\n{Valor}"
                        pass
                    elif tool_name == "ReinicioNucleo":
                        #Valor = EstavilidadEnergetica()
                        """
                        if Valor == "Es posible reinicir el sistema. Se recomienda proseder cuanto antes":
                            resumen += f"\nSistem: Se está reiniciando el sistema. Espera unos segundos"
                            thread = threading.Thread(target=Escena, args=("Reinicio", "light.strip_lights", 255, [255, 255, 255]))
                            thread.start()
                            ReinicioNucleo()
                        """
                        pass
                    elif tool_name == "iluminacionambiente":
                        estado = arguments.get("estado")
                        nombre_entidad = "light.strip_lights"
                        brillo = arguments.get("brillo", 255)
                        rgb = arguments.get("rgb", [255, 255, 255])
                        text += f"Sistema: {nombre_entidad} estado: {estado} brillo: {brillo} rgb: {rgb}\n"
                        thread = threading.Thread(target=Escena, args=(estado, nombre_entidad, brillo, rgb))
                        thread.start()

                    elif tool_name == "no_op":
                        pass
                return self.chat(text, conversacion, resumen, Pensamiento)
            return f"Error en la respuesta de la API: {response_data}"
    def chat(self, text, conversacion, resumen, Pensamiento = []):
        Contexto = [
                    {"role": "system", "content": f"{self.role}\n"}
                    ]
        Interacciones = conversacion.split("*##")[1:]
        for interaccion in Interacciones:
            temp = interaccion.split("##*")
            Contexto.append({"role": "user", "content": temp[0]})
            Contexto.append({"role": "assistant", "content": temp[1]})
        try:
            if len(Pensamiento) > 0 and Pensamiento[-1] != "Has salido de tu espacio o de tus pensamientos Ahora debes generar una respuesta basada en Tu reflección.":
                Contexto[0] = {"role": "system", "content": f"{Pensamiento[0]}"}
                Contexto.append({"role": "user", "content": text})
                pensamiento = Pensamiento[1:]
                for pensar in pensamiento:
                    Contexto.append({"role": "system", "content": pensar})
                response = requests.post(
                    url=self.api_url,
                    headers=self.headers,
                    data=json.dumps({
                        "model": modelo,
                        "messages": Contexto,
                    }),
                )

                response.raise_for_status()  # Lanza excepción si el código no es 200
                response_data = response.json()
            
                # Procesar respuesta del modelo
                respuesta = response_data["choices"][0]["message"]["content"] if "choices" in response_data and response_data["choices"] else "Error: No se recibió una respuesta válida del modelo."
                
                print(respuesta)
                return respuesta
            elif len(Pensamiento) > 0:

                Contexto.append({"role": "user", "content": text})
                pensamiento = Pensamiento[1:]
                for pensar in pensamiento:
                    Contexto.append({"role": "system", "content": pensar})

                response = requests.post(
                    url=self.api_url,
                    headers=self.headers,
                    data=json.dumps({
                        "model": modelo,
                        "messages": Contexto,
                    }),
                )

                response.raise_for_status()  # Lanza excepción si el código no es 200
                response_data = response.json()
            
                # Procesar respuesta del modelo
                respuesta = response_data["choices"][0]["message"]["content"] if "choices" in response_data and response_data["choices"] else "Error: No se recibió una respuesta válida del modelo."
                
                print(respuesta)
                return respuesta

            else:

                Contexto.append({"role": "user", "content": text})
                if resumen != "":
                    Contexto.append({"role": "user", "content": f"Información relevante debes basar tu respuesta en la siguiente información: {resumen}"})

                with open(f"{MEMORIA_PATH}/consulta.txt", "w", encoding="utf-8") as archivo:
                    json.dump(Contexto, archivo, ensure_ascii=False, indent=2)

                response = requests.post(
                    url=self.api_url,
                    headers=self.headers,
                    data=json.dumps({
                        "model": modelo,
                        "messages": Contexto,
                    }),
                )

                response.raise_for_status()  # Lanza excepción si el código no es 200
                response_data = response.json()
            
                # Procesar respuesta del modelo
                respuesta = response_data["choices"][0]["message"]["content"] if "choices" in response_data and response_data["choices"] else "Error: No se recibió una respuesta válida del modelo."
                
                print(respuesta)
                return respuesta
        
        except (ConnectionError) as e:
            print(f"[WARN] Error de conexión: {e}")            
        except Exception as e:
            print(f"[ERROR] Otro error inesperado: {e}")
        