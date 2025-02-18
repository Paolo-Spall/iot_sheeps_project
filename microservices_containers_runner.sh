sudo docker stop drone_control_cnt
sudo docker rm drone_control_cnt
sudo docker stop localization_service_cnt
sudo docker rm localization_service_cnt
sudo docker stop system_monitoring_service_cnt
sudo docker rm system_monitoring_service_cnt
cd drone_control
sudo docker run --name=drone_control_cnt --network iot_network -v ${PWD}/target_drone_control_conf.yaml:/app/drone_control_conf.yaml --restart always -d drone_control_img:0.1
cd ..
cd localization_service
sudo docker run --name=localization_service_cnt --network iot_network -v ${PWD}/target_localization_conf.yaml:/app/localization_conf.yaml --restart always -d localization_service_img:0.1
cd ..
cd system_monitoring_service
sudo docker run --name=system_monitoring_service_cnt --network iot_network -v ${PWD}/target_system_monitoring_conf.yaml:/app/system_monitoring_conf.yaml --restart always -d system_monitoring_service_img:0.1
