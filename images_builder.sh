#!/usr/bin/bash
cd mqtt-broker
sudo docker run --name=my-mosquitto-broker --network iot_network -p 1883:1883 -v ${PWD}/mosquitto.conf:/mosquitto/config/mosquitto.conf -v ${PWD}/data:/mosquitto/data -v ${PWD}/log:/mosquitto/log --restart always -d eclipse-mosquitto:2.0.12
sudo docker stop my-mosquitto-broker
sudo docker rm my-mosquitto-broker
cd ..
cd http-api
sudo docker build -t http_iot_inventory_api_lab:0.1 .
sudo docker run --name=http-inventory-api-lab --network iot_network -p 7070:7070 -v ${PWD}/target_api_conf.yaml:/app/conf.yaml --restart always -d http_iot_inventory_api-lab:0.1
sudo docker stop http-inventory-api-lab
sudo docker rm http-inventory-api-lab
cd ..
cd data-fetcher
sudo docker build -t mqtt_data_fetcher_lab:0.1 .
sudo docker run --name=mqtt_data_fetcher_lab --network iot_network -v ${PWD}/target_fetcher_conf.yaml:/app/fetcher_conf.yaml --restart always -d mqtt_data_fetcher_lab:0.1
sudo docker stop mqtt_data_fetcher_lab
sudo docker rm mqtt_data_fetcher_lab
cd ..
cd web-ui
sudo docker build -t web-ui-lab:0.1 .
sudo docker run --name=web-ui-lab -p 7071:7071 -v ${PWD}/target_web_conf.yaml:/app/web_conf.yaml --restart always -d web-ui-lab:0.1
sudo docker stop web-ui-lab
sudo docker rm web-ui-lab
cd ..
cd gateway-http-mqtt
sudo docker build -t gateway_http_mqtt_lab:0.1 .
sudo docker run --name=gateway-http-mqtt --network iot_network -p 7072:7072 -v ${PWD}/target_gateway_conf.yaml:/app/gateway_conf.yaml --restart always -d gateway_http_mqtt_lab:0.1
sudo docker stop gateway-http-mqtt
sudo docker rm gateway-http-mqtt
cd ..
