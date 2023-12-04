# simulador.py
import json
import random
import pika

# Configuración de RabbitMQ (ajusta los parámetros según tu configuración)
connection_params = pika.ConnectionParameters('localhost')
connection = pika.BlockingConnection(connection_params)
channel = connection.channel()
channel.queue_declare(queue='cola_de_formularios')

def generar_formulario_aleatorio():
    # Genera datos aleatorios para el formulario
    formulario = {
        "id": random.randint(1000, 9999),
        "nombre": "Nombre" + str(random.randint(1, 100)),
        "edad": random.randint(18, 99),
        # Agrega más campos según sea necesario
    }
    return formulario

def enviar_a_cola(formulario):
    channel.basic_publish(exchange='',
                          routing_key='cola_de_formularios',
                          body=json.dumps(formulario))
    print(" [x] Enviado " + str(formulario))

# Simula la generación y envío de formularios
for _ in range(10):  # Genera 10 formularios para este ejemplo
    formulario = generar_formulario_aleatorio()
    enviar_a_cola(formulario)

connection.close()
