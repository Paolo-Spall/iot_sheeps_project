import socket
import json
import paho.mqtt.client as mqtt
from service_message import ServiceMessage
from json import JSONDecodeError
import threading
import yaml

CONF_FILE_PATH = "notification_microservice_conf.yaml"

# MQTT
broker_ip = "127.0.0.1"
broker_port = 1883
subscribe_topic = "notification"

# Socket
HOST = '0.0.0.0'
PORT = 65432

# Read Configuration from target Configuration File Path
def read_configuration_file():
    global configuration_dict

    with open(CONF_FILE_PATH, 'r') as file:
        configuration_dict = yaml.safe_load(file)

    return configuration_dict

configuration_dict = read_configuration_file()

# MQTT
broker_ip = configuration_dict["mqtt"]["broker_ip"]
broker_port = configuration_dict["mqtt"]["broker_port"]
subscribe_topic = configuration_dict["mqtt"]["subscribe_topic"]

# Socket
HOST = configuration_dict["socket"]["server"]["host"]
PORT = configuration_dict["socket"]["server"]["port"]

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


