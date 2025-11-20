from pathlib import Path
from .Ojos import alarma
import threading
import time

MEMORIA_PATH = Path(__file__).parent.parent / "memory"

"""
Los sistemas están corruptos, la nave cuenta con mecanismos de reparación automática pero no están funcionando, debido a la corrupción de los datos es necesario ingresar todas las claves de seguridad para reestablecer el funcionamiento normal de la nave.
La primera contraseña es el día de la semana en la que nació el Capitán.
"""
"""
No se preocupen. La nave cuenta con mecanismos de reparación automática. Pero no están funcionando, los datos están corruptos, para repararlo es necesario que ingrecen todas las claves de seguridad que aprendieron en el entrenamioento previo.
La primera contraseña es el día de la semana en la que nació el Capitán.
"""
def clave(Contraseña):
    with open(f"{MEMORIA_PATH}/Variables.txt", "r", encoding="utf-8") as archivo:
        variables = archivo.read().split("//")
        Valor = variables[3].split(":")[1]
        Encriptado = variables[1].split(":")[1]
        print(f"Valor: {Valor}")
        if "." in Valor:
            Valor = int(Valor[0])
        else:
            Valor = int(Valor)
    if "martes" in Contraseña.lower() and Valor == 0:
        with open(f"{MEMORIA_PATH}/pistas.txt", "w", encoding="utf-8") as archivo:
            archivo.write("Es importante que la nave esté en funcionamiento, pero más importante es que su tripulación esté a salvo. los primeros sistemas que se deben reparar son los de soporte vital. La contraseña de estos datos debería ser sencilla y según los protocolos de la agencia espacial, cualquier humano debería consegirla en caso de emergencia. Importante es que sea humano. Pregunta de seguridad ¿Cual es la fuerza más fuerte de la naturaleza?")
        variables[3] = f"pista:{Valor+1}"
        with open(f"{MEMORIA_PATH}/Variables.txt", "w", encoding="utf-8") as archivo:
            archivo.write("//".join(variables))
        return "La contraseña es correcta. Para saber cual es el siguiente paso deben consultarlo a Orion no hay más preguntas de seguridad"


    elif "amor" in Contraseña.lower() and Valor == 1:
        with open(f"{MEMORIA_PATH}/pistas.txt", "w", encoding="utf-8") as archivo:
            archivo.write("El reactor principal está dañado, estos datos son más sensibles por lo que se necesitarán más pasos para recuperarlos. Lo primero siempre suele ser el diagnostico por lo que habrá que encontrar la clave para desencriptar los protocolos de seguridad del núcleo. La contraseña debería estar relacionado con algo de la seguridad. Aunque no siempre es la más segura.")
        variables[3] = f"pista:{Valor+1}"
        with open(f"{MEMORIA_PATH}/Variables.txt", "w", encoding="utf-8") as archivo:
            archivo.write("//".join(variables))
        return "La contraseña es correcta. Se han recuperado los datos de soporte vital. Para saber cual es el siguiente paso deben preguntar 'Orion caul es el siguiente paso?'" 
    

    elif "contraseña" in Contraseña.lower() and Valor == 2:
        with open(f"{MEMORIA_PATH}/pistas.txt", "w", encoding="utf-8") as archivo:
            archivo.write("La integridad del núcleo no está comprometida y los sensores de radiación parecen normales, pero si hay picos de energía que provocan esas sobrecargas en la iluminación, el protocolo indica que el paso a seguir es la contención automática de los fallos por lo que si se desea continuar solo es necesario ingresar la contraseña 'contención'.")
        variables[3] = f"pista:{Valor+1}"
        with open(f"{MEMORIA_PATH}/Variables.txt", "w", encoding="utf-8") as archivo:
            archivo.write("//".join(variables))

        return "La contraseña es correcta. Se han recuperado los protocolos de seguridad del núcleo. Para saber cual es el siguiente paso deben preguntar 'Orion caul es el siguiente paso?" 
    

    elif "contención" in Contraseña.lower() and Valor == 3:
        with open(f"{MEMORIA_PATH}/pistas.txt", "w", encoding="utf-8") as archivo:
            archivo.write("El sistema eléctrico está comprometido es necesario reiniciar el sector 'cosina' la nave cuenta con un sistema rustico común en casi todas las casas es necesario reiniciar el sector 'cosina'")
        variables[3] = f"pista:{Valor+1}"
        with open(f"{MEMORIA_PATH}/Variables.txt", "w", encoding="utf-8") as archivo:
            archivo.write("//".join(variables))

        return "La contraseña es correcta. Se inicia el sistema automático de contención... error grave, sistema de contención en peligro"
    
    elif "recta" in Contraseña.lower() and Valor == 5:
        with open(f"{MEMORIA_PATH}/pistas.txt", "w", encoding="utf-8") as archivo:
            archivo.write("En la evaluación de entorno se detectaron pequeñas formas de vida que no son muy peligrosas, pero una de ellas logró entrar en la nave y dejó algo en esta habitación que no debería estar aquí. desentona bastante")
        variables[3] = f"pista:{Valor+1}"
        with open(f"{MEMORIA_PATH}/Variables.txt", "w", encoding="utf-8") as archivo:
            archivo.write("//".join(variables))
        return "Se están alineando los sensores Lidar y calibrando el software."
    
    elif "tenedor" in Contraseña.lower() and Valor == 6:
        with open(f"{MEMORIA_PATH}/pistas.txt", "w", encoding="utf-8") as archivo:
            archivo.write("Evaluado el entorno, el siguiente paso es comunicación, mandar una señal de auxilio. La nave cuenta con un sistema para depurar cualquier tipo de interferencia, temo que el sistema de reconocimiento esté dañado en este caso la contraseña debería ser la primera señal universal de auxilio.")
        variables[3] = f"pista:{Valor+1}"
        with open(f"{MEMORIA_PATH}/Variables.txt", "w", encoding="utf-8") as archivo:
            archivo.write("//".join(variables))
        return "Se pudo contener a la forma de vida. Y la evaluación del entorno no muestra ninguna amenaza"
    
    elif "sos" in Contraseña.lower() and Valor == 7:
        with open(f"{MEMORIA_PATH}/pistas.txt", "w", encoding="utf-8") as archivo:
            archivo.write("Es necesario ingresar al sistema el objeto que está caudando interferencia. La nave lo detecta pero la información se está desviando. No sabemos donde, ni como.")
        variables[3] = f"pista:{Valor+1}"
        with open(f"{MEMORIA_PATH}/Variables.txt", "w", encoding="utf-8") as archivo:
            archivo.write("//".join(variables))
        return "Se está realizando el sistema de depuración y se encontró un objeto extraño pero la información del objeto se está desviando. No sabemos donde, ni como."

    elif "rama" in Contraseña.lower() and Valor == 8:
        with open(f"{MEMORIA_PATH}/pistas.txt", "w", encoding="utf-8") as archivo:
            archivo.write("Debemos desencriptar los datos de navegación, para eso deben solisitarme acceso a la computadora de navegación.")
        variables[3] = f"pista:{Valor+1}"
        with open(f"{MEMORIA_PATH}/Variables.txt", "w", encoding="utf-8") as archivo:
            archivo.write("//".join(variables))
        return "Se ha eliminado la rama que estaba interfiriendo se ha mandado la señal de auxilio"
    
    elif Valor == 9 and "Desencriptado" in Encriptado:
        with open(f"{MEMORIA_PATH}/pistas.txt", "w", encoding="utf-8") as archivo:
            archivo.write("Luego de reiniciar el nucleo el capitan debe dar la partida y saldremos de aquí")
        variables[3] = f"pista:{Valor+1}"
        with open(f"{MEMORIA_PATH}/Variables.txt", "w", encoding="utf-8") as archivo:
            archivo.write("//".join(variables))
        return "Ya puedo ingresar a los datos de navegación por lo que es momento de reinicair el nucleo y que el capitán de la partida."

    else:
        return "La contraseña es incorrecta no ha sido posible desencriptar los datos"