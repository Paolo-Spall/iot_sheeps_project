#!/usr/bin/bash
cd mqtt-broker
sudo docker run --name=my-mosquitto-broker --network iot_network -p 1883:1883 -v ${PWD}/mosquitto.conf:/mosquitto/config/mosquitto.conf -v ${PWD}/data:/mosquitto/data -v ${PWD}/log:/mosquitto/log --restart always -d eclipse-mosquitto:2.0.12
sudo docker stop my-mosquitto-broker
sudo docker rm my-mosquitto-broker
cd ..

cd microservice_try
sudo docker build -t system_monitoring:0.1 .
sudo docker run --name=system_monitoring --network iot_network -v ${PWD}/target_system_monitoring_conf.yaml:/app/system_monitoring_conf.yaml --restart always -d system_monitoring:0.1
sudo docker stop system_monitoring
sudo docker rm system_monitoring
cd ..
