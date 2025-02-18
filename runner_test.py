import subprocess
import time
 
def run_command(cmd):
    subprocess.Popen(
        f'{cmd}',
        #cwd=cwd,
        shell=True
    )
    time.sleep(2)  # Attendi un po' prima di eseguire il prossimo comando
 
commands = [
    ("python3 ./microservices/drone_control/app/drone_control.py"),
    ("python3 ./microservices/system_monitoring_service/app/system_monitoring.py"),
    ("python3 ./microservices/localization_service/app/localization.py"),
    ("python3 ./mqtt-tester/json_point_list.py"),
    ("python3 ./mqtt-tester/drone_device_01.py"),
    ("python3 ./mqtt-tester/drone_device_02.py"),
    ("python3 ./mqtt-tester/drone_device_03.py"),
    ("python3 ./mqtt-tester/json_notification_consumer.py")
]
 
for cmd in commands:
    run_command(cmd)