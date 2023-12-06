import threading
import json
import os
from flask import Flask, request, jsonify
import requests
import time
from time import sleep

app = Flask(__name__)
HEARTBEAT_TIMEOUT = 10
HEARTBEAT_INTERVAL = 5

# Configuración inicial del nodo
NODE_ID = os.getenv('NODE_ID', 'node_1')
ES_LIDER = bool(int(os.getenv('ES_LIDER', '0')))
ARCHIVO_LOG = f"log_{NODE_ID}.txt"
SEGUIDORES = json.loads(os.getenv('SEGUIDORES', '[]'))
URL_LIDER = os.getenv('URL_LIDER', "http://localhost:5000")
PUERTO = int(os.getenv('PUERTO', '5000'))

# Número mínimo de confirmaciones necesarias para considerar una escritura exitosa
MIN_CONFIRMACIONES_REQUERIDAS = len(SEGUIDORES) // 2 + 1

# Utilidad para agregar al registro
def agregar_al_registro(entrada):
    with open(ARCHIVO_LOG, "a") as archivo_log:
        archivo_log.write(json.dumps(entrada) + "\n")

# Utilidad para replicar a los seguidores con manejo de errores
def replicar_a_seguidores(entrada):
    confirmaciones = 0
    for url_seguidor in SEGUIDORES:
        try:
            response = requests.post(f"{url_seguidor}/replicar", json=entrada, timeout=10)
            print(f"Respuesta de {url_seguidor}: {response.status_code}")  # Añadir registro de respuesta
            if response.status_code == 200:
                confirmaciones += 1
                # Si se alcanza el número mínimo de confirmaciones, considerar la escritura como exitosa
                if confirmaciones >= MIN_CONFIRMACIONES_REQUERIDAS:
                    return True
        except requests.exceptions.RequestException as e:
            print(f"Error al replicar a {url_seguidor}: {e}")
    return False

# Ruta de Flask para escribir datos
@app.route('/escribir', methods=['POST'])
def escribir_datos():
    if not ES_LIDER:
        return jsonify({"error": "Este nodo no es un líder."}), 403

    datos = request.json
    agregar_al_registro(datos)

    # Intenta replicar a los seguidores
    if replicar_a_seguidores(datos):
        return jsonify({"success": "Datos escritos y replicados exitosamente."}), 200
    else:
        return jsonify({"error": "No hay suficientes confirmaciones de seguidores."}), 500

# Función de heartbeat para detectar la disponibilidad de nodos
def heartbeat():
    while True:
        if ES_LIDER:
            # El líder envía un heartbeat a los seguidores
            for seguidor in SEGUIDORES:
                try:
                    requests.get(f"{seguidor}/heartbeat")
                except requests.RequestException:
                    print(f"El seguidor {seguidor} no está respondiendo.")
        else:
            # El seguidor espera el heartbeat del líder
            try:
                requests.get(f"{URL_LIDER}/heartbeat")
            except requests.RequestException:
                print("El líder no responde, iniciando la elección de líder.")
                # Aquí se iniciaría la lógica para una elección de líder
        sleep(HEARTBEAT_INTERVAL)

# Ruta de heartbeat para el líder y los seguidores
@app.route('/heartbeat', methods=['GET'])
def manejar_heartbeat():
    return jsonify({"estado": "activo", "id_nodo": NODE_ID}), 200

# Ruta de Flask para replicar datos (solo seguidores)
@app.route('/replicar', methods=['POST'])
def replicar_datos():
    datos = request.json
    agregar_al_registro(datos)
    return jsonify({"success": "Datos replicados exitosamente."}), 200
@app.route('/leer', methods=['GET'])
def leer_datos():
    # Aquí puedes añadir la lógica para leer datos, por ejemplo:
    # 1. Leer el archivo de registro y devolver su contenido
    # 2. Buscar en una base de datos si estás utilizando una
    # 3. Etc.
    return jsonify({"mensaje": "Aquí van los datos leídos"}), 200


# Función para simular la desconexión y reconexión de nodos
def simular_falla_nodo():
    global ES_LIDER
    # Simula una desconexión temporal
    time.sleep(10)
    ES_LIDER = False
    print(f"El Nodo {NODE_ID} se ha desconectado temporalmente.")
    # Simula una reconexión y elección del líder
    time.sleep(10)
    ES_LIDER = True
    print(f"El Nodo {NODE_ID} se ha vuelto a conectar y ahora es el líder.")

# Iniciar el thread de heartbeat
thread_heartbeat = threading.Thread(target=heartbeat)
thread_heartbeat.daemon = True  # Esto asegura que el thread se cierre con el programa
thread_heartbeat.start()

if __name__ == '__main__':
    # Configurar el nodo según las variables de entorno
    NODE_ID = os.getenv('NODE_ID', 'node_1')
    ES_LIDER = bool(int(os.getenv('ES_LIDER', '0')))
    ARCHIVO_LOG = f"log_{NODE_ID}.txt"
    SEGUIDORES = json.loads(os.getenv('SEGUIDORES', '[]'))
    URL_LIDER = os.getenv('URL_LIDER', URL_LIDER)
    PUERTO = int(os.getenv('PUERTO', '5000'))
    
    # Iniciar el servidor Flask
    app.run(port=PUERTO)

