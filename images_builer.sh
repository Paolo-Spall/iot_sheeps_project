#!/usr/bin/bash
cd mqtt-broker
sudo docker run --name=my-mosquitto-broker --network iot_network -p 1883:1883 -v ${PWD}/mosquitto.conf:/mosquitto/config/mosquitto.conf -v ${PWD}/data:/mosquitto/data -v ${PWD}/log:/mosquitto/log --restart always -d eclipse-mosquitto:2.0.12
sudo docker stop my-mosquitto-broker
sudo docker rm my-mosquitto-broker
cd ..
cd http-api
sudo docker build -t http_iot_inventory_api:0.1 .
sudo docker run --name=http-inventory-api --network iot_network -p 7070:7070 -v ${PWD}/target_web_conf.yaml:/app/conf.yaml --restart always -d http_iot_inventory_api:0.1
sudo docker stop http-inventory-api
sudo docker rm http-inventory-api
cd ..
cd data-fetcher
sudo docker build -t mqtt_data_fetcher:0.1 .
sudo docker run --name=mqtt_data_fetcher --network iot_network -v ${PWD}/target_fetcher_conf.yaml:/app/fetcher_conf.yaml --restart always -d mqtt_data_fetcher:0.1
sudo docker stop mqtt_data_fetcher
sudo docker rm mqtt_data_fetcher
cd ..
cd web-ui
sudo docker build -t web-ui:0.1 .
sudo docker run --name=web-ui -p 7071:7071 -v ${PWD}/target_web_conf.yaml:/app/web_conf.yaml --restart always -d web-ui:0.1
sudo docker stop web-ui
sudo docker rm web-ui
cd ..
