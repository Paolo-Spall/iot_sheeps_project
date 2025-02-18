import socket
import tkinter as tk
from tkinter import messagebox
import threading
import json
from service_message import ServiceMessage

HOST = '127.0.0.1'  # Server IP address (localhost)
PORT = 65432        # Port for server 


def show_popup(formatted_message):
    """Funzione che mostra il popup con il messaggio ricevuto."""
    root = tk.Tk()
    root.withdraw()  # Hide the main Tkinter window
    
    # Mostra il messaggio 
    messagebox.showinfo("New Notification", formatted_message)
    root.mainloop()

def receive_notifications():
    """Funzione che si connette al server e riceve notifiche."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))  # Connessione al server

        print("Client listening for notifications...")
        while True:
            data = s.recv(1024)  # Riceve il messaggio dal server
            
            
            if data:
                message = data.decode('utf-8')
                print(f"Message received from the server: {message}") 
                
                try:
                    # Converte direttamente il messaggio in JSON
                    json_data = json.loads(message)  # Converte il JSON in un dizionario
                    # Crea un oggetto ServiceMessage con i dati
                    service_message = ServiceMessage(**json_data)
                    # Ottieni il messaggio formattato come stringa leggibile
                    formatted_message = service_message.to_readable_string()
                    # Avvia il thread per mostrare il popup con il messaggio formattato
                    threading.Thread(target=show_popup, args=(formatted_message,), daemon=True).start()
                except json.JSONDecodeError:
                    print("Error: Received invalid JSON")


# Create and start the thread to receive notifications
notification_thread = threading.Thread(target=receive_notifications)
notification_thread.start()

# Initialize the Tkinter graphical interface
root = tk.Tk()
root.withdraw()  # Hide the main Tkinter window
root.mainloop()
