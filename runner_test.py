import subprocess
import time

def run_command(cmd, cwd):
    subprocess.Popen(
        f'start cmd /k "{cmd}"',
        cwd=cwd,
        shell=True
    )
    time.sleep(2)  # Attendi un po' prima di eseguire il prossimo comando

commands = [
    ("python drone_control.py", r"C:\Users\User\PycharmProjects\IoT_projects\iot_sheeps_project\microservices\drone_control\app"),
    ("python system_monitoring.py", r"C:\Users\User\PycharmProjects\IoT_projects\iot_sheeps_project\microservices\system_monitoring_service\app"),
    ("python localization.py", r"C:\Users\User\PycharmProjects\IoT_projects\iot_sheeps_project\microservices\localization_service\app"),
    ("python json_point_list.py", r"C:\Users\User\PycharmProjects\IoT_projects\iot_sheeps_project\mqtt-tester"),
    ("python drone_device_01.py", r"C:\Users\User\PycharmProjects\IoT_projects\iot_sheeps_project\mqtt-tester"),
    ("python drone_device_02.py", r"C:\Users\User\PycharmProjects\IoT_projects\iot_sheeps_project\mqtt-tester"),
    ("python drone_device_03.py", r"C:\Users\User\PycharmProjects\IoT_projects\iot_sheeps_project\mqtt-tester"),
    ("python json_notification_consumer.py", r"C:\Users\User\PycharmProjects\IoT_projects\iot_sheeps_project\mqtt-tester"),
]

for cmd, path in commands:
    run_command(cmd, path)
