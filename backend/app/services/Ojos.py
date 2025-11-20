import requests, json
import time
import random
from playsound import playsound
from pathlib import Path
import threading
from datetime import datetime

MEMORIA_PATH = Path(__file__).parent.parent / "memory"



BASE = "http://localhost:8123"
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiI5YmY3YmFkNjNiODI0MTQxYTZhZDUzOTczMWY0N2U0ZCIsImlhdCI6MTc1NTk2Nzk4MSwiZXhwIjoyMDcxMzI3OTgxfQ.Wwnv0rn6oI4ZPQOeVyxFuwDTHHP9d9wo1nL6TatA2S8"
ENTITY = "weather.forecast_casa"

url_on = "http://localhost:8123/api/services/light/turn_on"
url_off = "http://localhost:8123/api/services/light/turn_off"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json",
}

def corregir_color(rgb): 
    r = int(rgb[0])
    g = int(rgb[1]-rgb[0]*.2406761-rgb[2]*.2575886)
    b = int(rgb[2]*.9602401-rgb[1]*.5692199)
    print(f"🎨 Color corregido: {r}, {max(g, 0)}, {max(b, 0)}")
    return (r, max(g, 0), max(b, 0))

def Escena(nombre_escena, nombre_entidad = "light.strip_lights", brillo = 255, color = [255, 255, 255]):

    #color = corregir_color(color)
    
    if "apagar" in nombre_escena:
        data_off = {
            "entity_id": nombre_entidad
        }
        response = requests.post(url_off, headers=headers, json=data_off)
        if response.status_code != 200:
            print(f"Error al apagar: {response.status_code}, {response.text}")
            return 1
    if "cambiar brillo" in nombre_escena:
        data_brillo = {
            "entity_id": nombre_entidad,
            "brightness": brillo
        }
        response = requests.post(url_on, headers=headers, json=data_brillo)
        if response.status_code != 200:
            print(f"Error al cambiar el brillo: {response.status_code}, {response.text}")
            return 2
    if "encender_cambiar color" in nombre_escena:
        data_color = {
            "entity_id": nombre_entidad,
            "rgb_color": color,
            "brightness": brillo
        }
        response = requests.post(url_on, headers=headers, json=data_color)
        if response.status_code != 200:
            print(f"Error al cambiar el color: {response.status_code}, {response.text}")
            return 3
    if "alarma" in nombre_escena:
        alarma(nombre_entidad)
    
    if "Reinicio" in nombre_escena:
        reiniciar_nucleo(nombre_entidad)

    return 0

def alarma(Nombre_entidad, repeticiones = 10):

    contador = 0
    while contador < repeticiones:
        data_on = {
            "entity_id": Nombre_entidad,
            "rgb_color": [255, 0, 0],  # Rojo en formato RGB
            "brightness": 255          # Brillo al 50% (128 de 255)
        }
        response = requests.post(url_on, headers=headers, json=data_on)
        if response.status_code != 200:
            print(f"Error al encender la luz: {response.status_code}, {response.text}")
            break
        time.sleep(2)

        data_off = {
            "entity_id": Nombre_entidad
        }
        response = requests.post(url_off, headers=headers, json=data_off)
        if response.status_code != 200:
            print(f"Error al apagar la luz: {response.status_code}, {response.text}")
            break
        time.sleep(2)
        contador += 1
    return 0

def reproducir_chispazo(Nombre_audio):
    playsound(f'{Path(__file__).parent.parent / "audio"}/{Nombre_audio}')

def chispaso(Nombre_entidad):
    url_state = f"http://localhost:8123/api/states/{Nombre_entidad}"
    response = requests.get(url_state, headers=headers)
    if response.status_code == 200:
        estado = response.json()
        color_original = estado["attributes"].get("rgb_color", [255, 255, 255])
        brillo_original = estado["attributes"].get("brightness", 255)
        print(f"Estado original: {color_original}, {brillo_original}")

    else:
        print(f"Error al obtener estado: {response.status_code}, {response.text}")




    data_on = {
        "entity_id": Nombre_entidad,
        "rgb_color": [255, 255, 255],
        "brightness": 255
    }
    data_restore = {
        "entity_id": Nombre_entidad,
        "rgb_color": color_original,
        "brightness": brillo_original
    }
    data_off = {
        "entity_id": Nombre_entidad
    }
    Valor = True
    while Valor:
        intervalo = random.randint(1, 60)
        time.sleep(intervalo)
        with open(f"{MEMORIA_PATH}/Variables.txt", "r", encoding="utf-8") as archivo:
            Valor = archivo.read().split("//")[2]
            Valor = Valor.split(":")[1]
            print(f"Valor: {Valor}")
        if Valor == "Ensendido":
            Valor = True
        else:
            Valor = False
        if not Valor:
            break
        aleatorio = 1
        for i in range(aleatorio):
            #Reproducir sonido
            threading.Thread(
                target=reproducir_chispazo,
                args=("Chispas.mp3",),
                daemon=True
            ).start()
            time.sleep(0)
            response = requests.post(url_off, headers=headers, json=data_off)
            if response.status_code != 200:
                print(f"Error al apagar la luz: {response.status_code}, {response.text}")
                break
            time.sleep(.5)
            response = requests.post(url_on, headers=headers, json=data_on)
            if response.status_code != 200:
                print(f"Error al encender la luz: {response.status_code}, {response.text}")
                break
            time.sleep(.2)
            response = requests.post(url_off, headers=headers, json=data_off)
            if response.status_code != 200:
                print(f"Error al apagar la luz: {response.status_code}, {response.text}")
                break
            time.sleep(2)
            threading.Thread(
                target=reproducir_chispazo,
                args=("Chispas.mp3",),
                daemon=True
            ).start()
            time.sleep(.5)
            response = requests.post(url_on, headers=headers, json=data_on)
            if response.status_code != 200:
                print(f"Error al encender la luz: {response.status_code}, {response.text}")
                break
            time.sleep(.2)
            response = requests.post(url_off, headers=headers, json=data_off)
            if response.status_code != 200:
                print(f"Error al apagar la luz: {response.status_code}, {response.text}")
                break
            time.sleep(2)
            response = requests.post(url_on, headers=headers, json=data_restore)
            if response.status_code != 200:
                print(f"Error al apagar la luz: {response.status_code}, {response.text}")
                break
    time.sleep(1)
    return 0

def reiniciar_nucleo(Nombre_entidad):
    url_state = f"http://localhost:8123/api/states/{Nombre_entidad}"
    response = requests.get(url_state, headers=headers)
    if response.status_code == 200:
        estado = response.json()
        color_original = estado["attributes"].get("rgb_color", [255, 255, 255])
        brillo_original = estado["attributes"].get("brightness", 255)
        print(f"Estado original: {color_original}, {brillo_original}")

    else:
        print(f"Error al obtener estado: {response.status_code}, {response.text}")
    data_on = {
        "entity_id": Nombre_entidad,
        "rgb_color": color_original,
        "brightness": brillo_original
    }
    response = requests.post(url_on, headers=headers, json=data_on)
    if response.status_code != 200:
        print(f"Error al encender la luz: {response.status_code}, {response.text}")
    time.sleep(2)
    
    data_off = {
        "entity_id": Nombre_entidad
    }
    threading.Thread(
        target=reproducir_chispazo,
        args=("Reactivamotor1.mp3",),
        daemon=True
    ).start()
    time.sleep(2)
    response = requests.post(url_off, headers=headers, json=data_off)
    if response.status_code != 200:
        print(f"Error al apagar la luz: {response.status_code}, {response.text}")
    time.sleep(4)
    response = requests.post(url_on, headers=headers, json=data_on)
    if response.status_code != 200:
        print(f"Error al encender la luz: {response.status_code}, {response.text}")
    response = requests.post(url_off, headers=headers, json=data_off)
    time.sleep(.05)
    if response.status_code != 200:
        print(f"Error al apagar la luz: {response.status_code}, {response.text}")
    response = requests.post(url_on, headers=headers, json=data_on)
    if response.status_code != 200:
        print(f"Error al encender la luz: {response.status_code}, {response.text}")
    time.sleep(3)
    return 0

BASE = "http://localhost:8123"  # Asegúrate de que esta URL sea correcta

def get_clima(ubicacion="forecast_casa", token=TOKEN):
    entity_id = f"weather.{ubicacion}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    # 1) Estado actual
    try:
        r_state = requests.get(f"{BASE}/api/states/{entity_id}", headers=headers)
        r_state.raise_for_status()
        state = r_state.json()
        attrs = state.get("attributes", {})
        temp_unit = attrs.get("temperature_unit", "°C")
        wind_unit = attrs.get("wind_speed_unit", "km/h")

        print("Estado de ubicación:", state.get("state"))
        print("Temperatura actual:", attrs.get("temperature"), temp_unit)
        print("Humedad:", attrs.get("humidity"), "%")
        print("Velocidad del viento:", attrs.get("wind_speed"), wind_unit)

    except requests.exceptions.RequestException as e:
        print("Error al obtener estado actual:", e)
        return

    # 2) Pronóstico diario
    try:
        url = f"{BASE}/api/services/weather/get_forecasts?return_response"
        payload = {"entity_id": entity_id, "type": "daily"}

        r_fc = requests.post(url, headers=headers, json=payload)
        r_fc.raise_for_status()
        data = r_fc.json()

        # 👇 Aquí el forecast correcto
        forecast = (
            data.get("service_response", {})
            .get(entity_id, {})
            .get("forecast", [])
        )

        if not forecast:
            print("⚠️ Sin datos de pronóstico diario:", data)
            return

        # Buscar HOY por fecha
        def _to_local_date(s):
            return datetime.fromisoformat(s.replace("Z", "+00:00")).astimezone().date()

        hoy = datetime.now().astimezone().date()
        dia_hoy = next(
            (f for f in forecast if "datetime" in f and _to_local_date(f["datetime"]) == hoy),
            forecast[0]
        )

        tmax = dia_hoy.get("temperature")
        tmin = dia_hoy.get("templow") or dia_hoy.get("temperature_low")

        print("🌡️ Máxima de hoy:", tmax, temp_unit)
        print("🌡️ Mínima de hoy:", tmin, temp_unit)

        return tmax, tmin

    except requests.exceptions.RequestException as e:
        print("Error al obtener pronóstico:", e)
    except Exception as e:
        print("Error al procesar pronóstico:", e)

def despertador(Hora = None, espera = 5):
    Escena("encender_cambiar color", nombre_entidad = "light.strip_lights", brillo = 40, color = [255, 80, 20])
    time.sleep(espera)
    Escena("encender_cambiar color", nombre_entidad = "light.strip_lights", brillo = 90, color = [255, 120, 40])
    time.sleep(espera)
    Escena("encender_cambiar color", nombre_entidad = "light.strip_lights", brillo = 140, color = [255, 160, 60])
    time.sleep(espera)
    Escena("encender_cambiar color", nombre_entidad = "light.strip_lights", brillo = 190, color = [255, 200, 100])
    time.sleep(espera)
    Escena("encender_cambiar color", nombre_entidad = "light.strip_lights", brillo = 230, color = [255, 230, 150])
    time.sleep(espera)
    Escena("encender_cambiar color", nombre_entidad = "light.strip_lights", brillo = 255, color = [141, 178, 185])
    time.sleep(espera)
    Escena("encender_cambiar color", nombre_entidad = "light.strip_lights", brillo = 255, color = [27, 127, 220])
    time.sleep(espera)

    return 0

if __name__ == "__main__":
    Escena("encender_cambiar color", nombre_entidad = "light.strip_lights", brillo = 255, color = [54, 64, 212])
    """
    Escena("encender_cambiar color", nombre_entidad = "light.strip_lights", brillo = 255, color = [200, 100, 0])
    time.sleep(2)
    threading.Thread(
        target=chispaso,
        args=("light.strip_lights",),
        daemon=True
    ).start()
    #reiniciar_nucleo("light.strip_lights")
    #time.sleep(2)
    #Escena("encender_cambiar color", nombre_entidad = "light.strip_lights", brillo = 255, color = [200, 0, 0])
    #time.sleep(2)
    #alarma("light.strip_lights")
    while True:
        with open(f"{MEMORIA_PATH}/Variables.txt", "r", encoding="utf-8") as archivo:
            time.sleep(1)
            Variables = archivo.read().split("//")
            Valor = Variables[3].split(":")[1]
            print(f"Valor: {Valor}")
            Sensor = Variables[2].split(":")[1]
            print(f"Sensor: {Sensor}")
            if "4" in Valor  and "Ensendido" in Sensor:
                alarma("light.strip_lights", 1)
            elif "4" in Valor  and "Ensendido" not in Sensor:
                Escena("encender_cambiar color", nombre_entidad = "light.strip_lights", brillo = 255, color = [255, 255, 255])
                with open(f"{MEMORIA_PATH}/Variables.txt", "r", encoding="utf-8") as archivo:
                    variables = archivo.read().split("//")
                    Valor = variables[3].split(":")[1]
                    print(f"Valor: {Valor}")
                    Valor = int(Valor)
                with open(f"{MEMORIA_PATH}/pistas.txt", "w", encoding="utf-8") as archivo:
                    archivo.write("Es necesario revisar el entorno para detectar posibles amenasas. En primer lugar alinear los censores. Además hay que mantener las tenciones al mínimo después de aquella última experiencia por lo que al primero que responda la siguiente pregunta, el capitán en persona le dará el fabuloso premio de un viaje por los anillos de saturno. ¿Cual es la distancia más corta entre dos puntos?")
                variables[3] = f"pista:{Valor+1}"
                with open(f"{MEMORIA_PATH}/Variables.txt", "w", encoding="utf-8") as archivo:
                    archivo.write("//".join(variables))
            elif "6" == Valor:
                reproducir_chispazo("ductos1.mp3")
                with open(f"{MEMORIA_PATH}/Variables.txt", "r", encoding="utf-8") as archivo:
                    variables = archivo.read().split("//")
                    Valor = variables[3].split(":")[1]
                    print(f"Valor: {Valor}")
                    Valor = int(Valor)
                variables[3] = f"pista:{Valor}.0"
                with open(f"{MEMORIA_PATH}/Variables.txt", "w", encoding="utf-8") as archivo:
                    archivo.write("//".join(variables))
            elif "8" == Valor:
                while True:
                    with open(f"{MEMORIA_PATH}/Variables.txt", "r", encoding="utf-8") as archivo:
                        variables = archivo.read().split("//")
                        Valor = variables[3].split(":")[1]
                        print(f"Valor: {Valor}")
                        Valor = int(Valor)
                    if Valor == 9:
                        break
                    Escena("encender_cambiar color", color = [255, 0, 0])
                    time.sleep(2)
                    Escena("encender_cambiar color", color = [200, 90, 0])
                    time.sleep(2)
                    Escena("encender_cambiar color", color = [255, 0, 200])
                    time.sleep(2)
                    Escena("encender_cambiar color", color = [0, 0, 255])
                    time.sleep(2)
                    Escena("apagar")
                    time.sleep(3)
    """
    #despertador()
    #print(get_clima()) 