import socket
import json
import paho.mqtt.client as mqtt
from notification.app.service_message import ServiceMessage
from json import JSONDecodeError
import threading

# MQTT
broker_ip = "127.0.0.1"
broker_port = 1883
subscribe_topic = "notification"

# Socket
HOST = '127.0.0.1'
PORT = 65432

# Variabile globale per il client connesso
client_conn = None

def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe(subscribe_topic)

def on_message(client, userdata, msg):
    """ Callback per ricevere i messaggi MQTT """
    global client_conn
    message_text = msg.payload.decode()  # Decodifica il payload in una stringa
    
    print(f"Message received on {msg.topic}: {msg.payload.decode()}")

    try:
        # Leggiamo direttamente il JSON
        json_data = json.loads(message_text)
        formatted_message = json.dumps(json_data)  # Opzionale: lo riconvertiamo in stringa per l'invio

        # Invia JSON al client TCP
        if client_conn:
            client_conn.sendall(formatted_message.encode('utf-8'))
            print(f"Sent JSON to TCP client: {formatted_message}")
        else:
            print("No TCP client connected!")

    except JSONDecodeError:
        print("Error parsing the message received from the broker.")

# Funzione per avviare il client MQTT
def start_mqtt_client():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(broker_ip, broker_port, 60)
    client.loop_forever()

# Funzione per avviare il server TCP
def start_tcp_server():
    global client_conn

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((HOST, PORT))
        server_socket.listen()
        print("Waiting for incoming TCP client connections...")

        while True:
            conn, addr = server_socket.accept()
            print(f"TCP Client Connected: {addr}")
            client_conn = conn

            try:
                while True:
                    data = conn.recv(1024)
                    if not data:
                        print("Client disconnected.")
                        client_conn = None
                        break

                    try:
                        # Decodifica JSON
                        received_json = json.loads(data.decode('utf-8'))
                        print(f"Received JSON from TCP Client: {received_json}")
                        conn.sendall(str.encode("OK"))

                    except JSONDecodeError:
                        print("Invalid JSON received from TCP Client")
                        conn.sendall(str.encode("KO"))

            except:
                client_conn = None
                break

# Funzione principale
def main():
    tcp_thread = threading.Thread(target=start_tcp_server, daemon=True)
    tcp_thread.start()

    mqtt_thread = threading.Thread(target=start_mqtt_client, daemon=True)
    mqtt_thread.start()

    print("Notification microservice is running...")
    while True:
        pass  # Mantiene il programma attivo

if __name__ == "__main__":
    main()


