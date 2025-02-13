docker network create iot_network
cd mqtt-broker
docker run --name=my-mosquitto-broker --network iot_network -p 1883:1883 -v .\mosquitto.conf:\mosquitto\config\mosquitto.conf -v .\data:\mosquitto\data -v .\log:\mosquitto\log --restart always -d eclipse-mosquitto:2.0.12
docker stop my-mosquitto-broker
docker rm my-mosquitto-broker
cd ..
cd http-api
docker build -t http_iot_inventory_api:0.1 .
docker run --name=http-inventory-api --network iot_network -p 7070:7070 --restart always -d http_iot_inventory_api:0.1
docker stop http-inventory-api
docker rm http-inventory-api
cd ..
cd data-fetcher
docker build -t mqtt_data_fetcher:0.1 .
docker run --name=mqtt_data_fetcher --network iot_network -v .\target_fetcher_conf.yaml:\app\fetcher_conf.yaml --restart always -d mqtt_data_fetcher:0.1
docker stop mqtt_data_fetcher
docker rm mqtt_data_fetcher
cd ..
cd web-ui
docker build -t web-ui:0.1 .
docker run --name=web-ui -p 7071:7071 -v .\target_web_conf.yaml:\app\web_conf.yaml --restart always -d web-ui:0.1
docker stop web-ui
docker rm web-ui