cd drone_control
docker build -t drone_control_img:0.1 .
docker run --name=drone_control_cnt --network iot_network -v .\target_drone_control_conf.yaml:\app\drone_control_conf.yaml --restart always -d drone_control_img:0.1
docker stop drone_control_cnt
docker rm drone_control_cnt
cd ..
cd localization_service
docker build -t localization_service_img:0.1 .
docker run --name=localization_service_cnt --network iot_network -v .\target_localization_conf.yaml:\app\localization_conf.yaml --restart always -d localization_service_img:0.1
docker stop localization_service_cnt
docker rm localization_service_cnt
cd ..
cd system_monitoring_service
docker build -t system_monitoring_service_img:0.1 .
docker run --name=system_monitoring_service_cnt --network iot_network -v .\target_system_monitoring_conf.yaml:\app\system_monitoring_conf.yaml --restart always -d system_monitoring_service_img:0.1
docker stop system_monitoring_service_cnt
docker rm system_monitoring_service_cnt
cd ..
cd notification_microservice
docker build -t notification_microservice_img:0.1 .