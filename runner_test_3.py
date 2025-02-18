import subprocess
import time

def run_command(cmd, cwd):
    subprocess.Popen(
        ['gnome-terminal', '--', '-c', f'"{cmd}"; exec bash'], 
        cwd=cwd
    )
    time.sleep(2)  # Attendi un po' prima di eseguire il prossimo comando

commands = [
    ("python3 drone_control.py", "./microservices/drone_control/app"),
    ("python3 system_monitoring.py" ,"./microservices/system_monitoring_service/app"),
    ("python3 localization.py", "./microservices/localization_service/app"),
    ("python3 json_point_list.py", "./mqtt-tester"),
    ("python3 drone_device_01.py", "./mqtt-tester"),
    ("python3 drone_device_02.py", "./mqtt-tester"),
    ("python3 drone_device_03.py", "./mqtt-tester"),
    ("python3 json_notification_consumer.py", "./mqtt-tester")
]

for cmd, path in commands:
    run_command(cmd, path)