import subprocess
import time

# Lista per tenere traccia dei processi avviati
processes = []

def run_command(cmd, cwd):
    proc = subprocess.Popen(
        ["cmd", "/k", cmd],
        cwd=cwd,
        creationflags=subprocess.CREATE_NEW_CONSOLE
    )
    processes.append(proc)
    time.sleep(2)  # Attendi un po' prima di eseguire il prossimo comando

commands = [
    ("python drone_device_01.py", r"C:\Users\User\PycharmProjects\IoT_projects\iot_sheeps_project\mqtt-tester"),
    ("python drone_device_02.py", r"C:\Users\User\PycharmProjects\IoT_projects\iot_sheeps_project\mqtt-tester"),
    ("python drone_device_03.py", r"C:\Users\User\PycharmProjects\IoT_projects\iot_sheeps_project\mqtt-tester"),
    ("python notification_client.py", r"C:\Users\User\PycharmProjects\IoT_projects\iot_sheeps_project\notification_client")
]

# Avvia tutti i comandi
for cmd, path in commands:
    run_command(cmd, path)

input("Premi Invio per chiudere tutte le finestre aperte...\n")

# Termina tutti i processi avviati
for proc in processes:
    proc.terminate()  # prova a terminare in maniera ordinata