import socket
import tkinter as tk
from tkinter import messagebox
import threading
import json
import signal
from service_message import ServiceMessage
 
HOST = '127.0.0.1'  # Server address (localhost)
PORT = 65432        # Server port
 
# Event flag to signal shutdown
stop_event = threading.Event()
 
def show_popup(formatted_message):
    """Displays a popup with the received message."""
    tmp_root = tk.Tk()
    tmp_root.withdraw()  # Hide the main window
    messagebox.showinfo("New Notification", formatted_message)
    tmp_root.destroy()   # Destroy the temporary window after closing the popup
 
def receive_notifications():
    """Connects to the server and listens for notifications until shutdown is requested."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(1.0)  # Set timeout to avoid infinite blocking in recv()
        try:
            s.connect((HOST, PORT))
        except Exception as e:
            print(f"Error connecting to server: {e}")
            return
 
        print("Client listening for notifications...")
        while not stop_event.is_set():
            try:
                data = s.recv(1024)
                if not data:
                    # If no data is received, exit the loop
                    break
                message = data.decode('utf-8')
                print(f"Message received: {message}")
 
                try:
                    json_data = json.loads(message)
                    service_message = ServiceMessage(**json_data)
                    formatted_message = service_message.to_readable_string()
                    # Start a separate thread to display the popup
                    threading.Thread(target=show_popup, args=(formatted_message,), daemon=True).start()
                except json.JSONDecodeError:
                    print("Error: Invalid JSON format")
            except socket.timeout:
                # If socket times out, check again if stop_event is set
                continue
            except Exception as e:
                print(f"Receiving error: {e}")
                break
    print("Notification thread terminated.")
 
# Start the notification thread as a daemon (will exit with the main thread)
notification_thread = threading.Thread(target=receive_notifications, daemon=True)
notification_thread.start()
 
# Create the main graphical window with an exit button
root = tk.Tk()
root.title("Notification Client")
label = tk.Label(root, text="The client is running.\nPress 'Exit' to close the application.")
label.pack(padx=20, pady=10)
exit_button = tk.Button(root, text="Exit", command=lambda: on_close())
exit_button.pack(pady=10)
 
def on_close():
    """Handles client shutdown."""
    print("Shutting down client...")
    stop_event.set()  # Signal the notification thread to stop
    root.destroy()    # Close the main Tkinter window
 
# Set up window close event handling
root.protocol("WM_DELETE_WINDOW", on_close)
 
# Handle Ctrl+C (SIGINT) to ensure proper shutdown
signal.signal(signal.SIGINT, lambda sig, frame: on_close())
 
root.mainloop()
print("Program terminated.")