# validador.py
import json
import pika

# Configuración de RabbitMQ
connection_params = pika.ConnectionParameters('localhost')
connection = pika.BlockingConnection(connection_params)
channel = connection.channel()
channel.queue_declare(queue='cola_de_formularios')

def validar_formulario(formulario):
    # Aquí iría la lógica para validar el formulario
    # Por ejemplo, verificar que la edad es un número
    if not isinstance(formulario.get("edad"), int):
        return False
    return True

def callback(ch, method, properties, body):
    formulario = json.loads(body)
    print(f" [x] Recibido {formulario}")
    if validar_formulario(formulario):
        print(f" [x] Formulario válido: {formulario}")
        # Aquí podrías enviar el formulario válido a otra cola o a un módulo de almacenamiento
    else:
        print(f" [x] Formulario inválido: {formulario}")
        # Aquí podrías almacenar el formulario inválido

channel.basic_consume(queue='cola_de_formularios', on_message_callback=callback, auto_ack=True)

print(' [*] Esperando mensajes. Para salir presione CTRL+C')
channel.start_consuming()
