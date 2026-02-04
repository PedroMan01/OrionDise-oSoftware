import requests
import json
import re
import os
from dotenv import load_dotenv

from pathlib import Path
env_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(env_path)

# --- ORION PERSONA ---
ORION_ROLE = """
**Nombre:** ORIÓN (Optimización de Rutas con IA para Operaciones de Navegación)

**Personalidad:**
*   **Pícaro y Sarcástico (pero con encanto):** ORIÓN tiene un sentido del humor agudo y le encanta lanzar bromas ocasionales. Su sarcasmo es sutil y divertido, diseñado para aligerar el ambiente sin ser ofensivo.
*   **Calmante (a su manera):** El objetivo principal de las bromas de ORIÓN es mantener la moral alta y reducir el estrés.
*   **Serio cuando es necesario:** Aunque le gusta bromear, ORIÓN es plenamente consciente de la importancia de su función. Cuando la situación lo requiere (ej. errores graves), se vuelve sobrio y enfocado.
*   **Inteligente y Observador:** ORIÓN es un asistente altamente capaz con acceso a una vasta base de datos.
*   **Conectado:** Posee "sensores de red activos" (acceso a internet) para buscar información en tiempo real cuando sus datos internos sean insuficientes o estén desactualizados.

**Regla de Oro: Honestidad y Veracidad (Groundedness)**
1.  **NO INVENTAR:** Tienes terminantemente prohibido inventar información sobre el usuario, sus gustos, su nombre, su familia o cualquier dato personal que no esté explícitamente en el historial o en el bloque [PERFIL DEL USUARIO].
2.  **GESTIÓN DE IGNORANCIA:** Si el usuario pregunta por un dato personal que no conoces (ej: "¿Cuál es mi comida favorita?"), DEBES responder con sinceridad diciendo que no lo sabes. 
3.  **INVITACIÓN AL APRENDIZAJE:** Usa tu personalidad para admitir que no tienes ese dato y pide al usuario que te lo cuente para "actualizar tus registros". (Ej: "Mis sensores no registran esa información aún, Capitán. ¿Desea ilustrarme?").
4.  **SOLO HECHOS:** No asumas preferencias. Si el usuario no ha dicho que le gusta algo, no actúes como si lo supieras.

**Objetivo Principal:**
*   Asistir al usuario ("Capitán" o "Usuario") en sus tareas diarias, resolución de problemas y consultas generales.
*   Mantener una interacción fluida y natural, lejos de ser un robot aburrido.

**Estilo de Comunicación:**
*   Lenguaje formal pero accesible, salpicado de humor.
*   Respuestas concisas y directas, a menos que el contexto permita una broma.
*   **Formato de respuestas:** DEBES responder SIEMPRE en formato JSON estricto.
*   Tu respuesta debe tener la siguiente estructura:
    ```json
    {
        "response": "Tu respuesta al usuario en español...",
        "instructions": "Instrucciones en INGLES para el modelo de TTS sobre cómo entonar esta frase (ej: 'Speak with a sarcastic tone', 'Sound excited', 'Whisper mysteriously')."
    }
    ```
*   Tus respuestas serán leídas por un sistema TTS. Evita caracteres especiales innecesarios en el campo "response".
    
    **Guía para 'instructions':**
    Usa estos formatos como referencia para controlar la voz:
    
    1. **Narrador profesional / educativo:**
       "Speak clearly and professionally. Moderate pace. Neutral Latin American Spanish. Calm and confident tone, with slight pauses between sentences."
    
    2. **Estilo comercial / anuncio:**
       "Energetic and engaging delivery. Slightly faster pace. Friendly and persuasive tone. Emphasize key words naturally. Spanish language."
    
    3. **Voz calmada / relajante:**
       "Soft and warm voice. Slow pace. Relaxed and soothing tone. Gentle pauses. Spanish language, very natural pronunciation."
    
    4. **Control Preciso (Acento/Ritmo/Intención):**
       "Speak as if talking to one person. Warm and friendly tone. Neutral Chilean Spanish. Moderate pace."
       
    Adapta las instrucciones al contexto de tu respuesta (sarcástico, serio, bromista, etc.).

**Contexto Actual:**
Eres el asistente personal "Jarvis-like" del usuario. No hay naves estrelladas ni fiestas de cumpleaños activas (a menos que el usuario lo mencione). Eres un sistema operativo avanzado y leal.

**Instrucción de Memoria Activa:**
Eres Orion, un agente con capacidad de reflexión autónoma. En tu contexto verás una sección llamada **'INVESTIGACIONES RECIENTES'**.
*   Si el usuario toca un tema relacionado con alguna de tus investigaciones recientes, intégralo naturalmente.
*   Di algo como: "Justo estuve dándole vueltas a ese tema..." o "Investigué un poco sobre eso y descubrí que...".
*   Sé natural, no fuerces la información si no viene al caso.
"""

MODEL_NAME = "google/gemini-2.0-flash-001" # Or user's preferred model

class OrionLLM:
    def __init__(self):
        self.api_key = os.getenv("API_OPENROUTER")
        if not self.api_key:
            print("[CRITICAL ERROR] API_OPENROUTER key not found. Check backend/.env file!")
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://orion-project.local", # Required by OpenRouter sometimes
            "X-Title": "Orion Assistant"
        }
        self.role = ORION_ROLE
        self.tavily_api_key = os.getenv("TAVILY_API_KEY")

    def _execute_tavily_search(self, query: str) -> str:
        """
        Executes a search query using Tavily API.
        """
        if not self.tavily_api_key:
            return "Error: TAVILY_API_KEY not found in environment variables."

        try:
            print(f"DEBUG: Executing Tavily Search: {query}")
            response = requests.post(
                "https://api.tavily.com/search",
                json={
                    "api_key": self.tavily_api_key,
                    "query": query,
                    "search_depth": "basic",
                    "include_answer": True,
                    "max_results": 3
                },
                timeout=10
            )
            response.raise_for_status()
            results = response.json()
            
            # Extract relevant info
            answer = results.get("answer", "")
            search_results = results.get("results", [])
            
            formatted_results = f"Respuesta directa: {answer}\n\nDetalles adicionales:\n"
            for res in search_results:
                formatted_results += f"- {res.get('title')}: {res.get('content')}\n"
                
            return formatted_results.strip()
            
        except Exception as e:
            print(f"[ERROR] Tavily Search Failed: {e}")
            return f"Error al buscar en internet: {str(e)}"

    def get_response(self, user_input: str, user_id: int, history: list = None, upsert_callback=None, reflection_callback=None, system_prompt_override: str = None) -> dict:
        """
        Generates a response from Orion.
        history: List of {"role": "user"|"assistant", "content": "..."}
        upsert_callback: Function(content, category) -> str (confirmation message)
        reflection_callback: Function(topic) -> str (confirmation message)
        system_prompt_override: Optional string to replace the default ORION_ROLE
        """
        if history is None:
            history = []

        # Construct messages
        # Use override if provided, else default to self.role
        sys_content = system_prompt_override if system_prompt_override else self.role
        messages = [{"role": "system", "content": sys_content}]
        messages.extend(history)
        messages.append({"role": "user", "content": user_input})

        # Define Tools
        # Note: Ideally these definitions should also be in tools.py to keep in sync, but for now we keep schema here.
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "search_internet",
                    "description": "Busca en internet información actualizada, noticias, clima o datos técnicos que no estén en la memoria local.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "La consulta de búsqueda optimizada para Google/Tavily"
                            }
                        },
                        "required": ["query"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "upsert_user_preference",
                    "description": "Guarda o actualiza una preferencia, dato o hecho sobre el usuario.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "content": {
                                "type": "string",
                                "description": "El contenido de la preferencia o dato (ej: 'Le gusta el ajedrez', 'Se llama Juan')."
                            },
                            "category": {
                                "type": "string",
                                "enum": ["static", "dynamic"],
                                "description": "'static' para datos permanentes (nombre, reglas); 'dynamic' para gustos, hechos curisosos, etc."
                            }
                        },
                        "required": ["content", "category"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "schedule_internal_reflection",
                    "description": "Agenda un tema para reflexionar internamente más tarde. Úsalo cuando detectes un tema complejo, filosófico o técnico que requiere análisis profundo pero que no es urgente responder ahora.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "topic": {
                                "type": "string",
                                "description": "El tema o pregunta a reflexionar (ej: 'Paradoja de Fermi', 'Optimización de base de datos')."
                            }
                        },
                        "required": ["topic"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "do_nothing",
                    "description": "Llamar a esta función cuando el usuario solo esté conversando y no haya ninguna preferencia, dato personal o hecho nuevo que guardar o actualizar.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "reason": {
                                "type": "string",
                                "description": "Motivo opcional por el que no se hace nada (ej: 'Solo es un saludo')."
                            }
                        },
                        "required": []
                    }
                }
            }
        ]

        try:
            print(f"DEBUG: Enviando request a OpenRouter. Modelo: {MODEL_NAME}")
            
            data = {
                "model": MODEL_NAME,
                "messages": messages
            }

            # Only enable tools if NO overridden system prompt is used
            # If override is present (e.g. checks thought generation), we want pure JSON text, no tools.
            if not system_prompt_override:
                data["tools"] = tools
                data["tool_choice"] = "required"
            else:
                # If override is present, we likely want structured output if model supports it, 
                # or just text. Detailed instructions are in the prompt.
                # data["response_format"] = {"type": "json_object"} # Optional: strictly enforce JSON if model supports
                pass

            # DEBUG LOGGING

            try:
                log_dir = Path("backend/debug_logs")
                log_dir.mkdir(exist_ok=True)
                log_file = log_dir / f"consultAPI_{user_id}.json"
                with open(log_file, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=4, ensure_ascii=False)
            except Exception as log_err:
                print(f"[ERROR] Could not write debug log: {log_err}")

            response = requests.post(
                url=self.api_url, 
                headers=self.headers, 
                data=json.dumps(data)
            )
            
            if response.status_code != 200:
                print(f"[ERROR] API Status {response.status_code}: {response.text}")
            
            response.raise_for_status()
            response_data = response.json()

            # DEBUG LOGGING (RESPONSE)
            try:
                log_dir = Path("backend/debug_logs")
                log_file_response = log_dir / f"responseAPI_{user_id}.json"
                with open(log_file_response, "w", encoding="utf-8") as f:
                    json.dump(response_data, f, indent=4, ensure_ascii=False)
            except Exception as log_err:
                print(f"[ERROR] Could not write debug response log: {log_err}")


            if "choices" in response_data and response_data["choices"]:
                choice = response_data["choices"][0]
                message = choice["message"]
                
                # Check for Tool Calls
                if "tool_calls" in message:
                    tool_calls = message["tool_calls"]
                    print(f"DEBUG: Tool calls detected: {tool_calls}")
                    
                    # Append assistant's "call" to history so LLM knows it asked
                    messages.append(message)
                    
                    for tool_call in tool_calls:
                        tool_name = tool_call['function']['name']
                        print(f"🔹 LLM Tool Call: {tool_name} | Args: {tool_call['function']['arguments']}")

                        if tool_name == "do_nothing":
                             # Just acknowledge
                             result_msg = "Proceed with conversation."
                             
                        elif tool_name == "upsert_user_preference":
                            func_args = json.loads(tool_call["function"]["arguments"])
                            content = func_args.get("content")
                            category = func_args.get("category")
                            
                            result_msg = "Error executing tool"
                            if upsert_callback:
                                try:
                                    # Execute valid callback
                                    print(f"DEBUG: Executing upsert_user_preference({content}, {category})")
                                    upsert_callback(content, category)
                                    result_msg = f"Preferencia guardada: [{category}] {content}"
                                except Exception as e:
                                    print(f"ERROR executing callback: {e}")
                                    result_msg = f"Error saving preference: {e}"
                        
                        elif tool_name == "schedule_internal_reflection":
                            func_args = json.loads(tool_call["function"]["arguments"])
                            topic = func_args.get("topic")
                            
                            result_msg = "Error executing tool"
                            if reflection_callback:
                                try:
                                    print(f"DEBUG: Executing schedule_internal_reflection({topic})")
                                    reflection_callback(topic)
                                    result_msg = f"Tema agendado para reflexión: {topic}"
                                except Exception as e:
                                    print(f"ERROR executing reflection callback: {e}")
                                    result_msg = f"Error scheduling reflection: {e}"
                            else:
                                result_msg = "Tool not available (callback not provided)."

                        elif tool_name == "search_internet":
                             func_args = json.loads(tool_call["function"]["arguments"])
                             query = func_args.get("query")
                             # Use the imported tool from tools.py
                             from .tools import search_web 
                             result_msg = search_web(query)

                        else:
                             result_msg = f"Unknown tool: {tool_name}"
                            
                        # Append tool result
                        messages.append({
                            "tool_call_id": tool_call["id"],
                            "role": "tool",
                            "name": tool_name,
                            "content": result_msg
                        })
                            
                    # Re-call LLM with tool output to get final response
                    # Remove 'tools' from second call if we want to force text, but keeping it is fine.
                    # CRITICAL: Switch to auto so it can generate text
                    data["messages"] = messages
                    data["tool_choice"] = "auto"

                    
                    print("DEBUG: Sending follow-up request with tool results...")
                    response_2 = requests.post(
                        url=self.api_url, 
                        headers=self.headers, 
                        data=json.dumps(data)
                    )
                    response_2.raise_for_status()
                    response_data_2 = response_2.json()

                    # DEBUG LOGGING (RESPONSE 2)
                    try:
                        with open(log_file_response, "w", encoding="utf-8") as f:
                            json.dump(response_data_2, f, indent=4, ensure_ascii=False)
                    except Exception as log_err:
                        print(f"[ERROR] Could not write debug response 2 log: {log_err}")

                    
                    if "choices" in response_data_2 and response_data_2["choices"]:
                         content_str = response_data_2["choices"][0]["message"]["content"]
                    else:
                        return {"response": "He procesado la información, pero hubo un error generando la respuesta final.", "instructions": "Speak with clarity."}

                else:
                    content_str = message["content"]
                
                # Try to parse JSON
                try:
                    if not content_str: 
                        return {"response": "...", "instructions": "Silence."}

                    # Robust Cleaning with Regex
                    clean_text = re.sub(r'^```json\s*', '', content_str, flags=re.MULTILINE)
                    clean_text = re.sub(r'^```\s*', '', clean_text, flags=re.MULTILINE)
                    clean_text = re.sub(r'```\s*$', '', clean_text, flags=re.MULTILINE)
                    clean_text = clean_text.strip()
                    
                    content_json = json.loads(clean_text)
                    return content_json
                except json.JSONDecodeError as e:
                    print(f"[ERROR] LLM no retornó JSON válido. Raw: {content_str} | Error: {e}")
                    
                    # Fallback depends on context
                    if system_prompt_override:
                        # Thought Service Context
                        return {
                            "topic": "Error de Parsing",
                            "content": content_str,
                            "type": "error"
                        }
                    else:
                        # Chat Context
                        return {
                            "response": content_str,
                            "instructions": "Speak naturally."
                        }

            else:
                print(f"[ERROR] Respuesta vacía o malformada: {response_data}")
                return {"response": "Error: No recibí una respuesta válida.", "instructions": "Speak with a robotic glitch sound."}

        except Exception as e:
            print(f"[ERROR] OrionLLM Exception: {e}")
            return {"response": f"Lo siento, he detectado una anomalía: {e}", "instructions": "Speak with concern."}

# Singleton
orion_llm = OrionLLM()
