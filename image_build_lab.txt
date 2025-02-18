docker network create iot_network
cd mqtt-broker
docker stop my-mosquitto-broker
docker rm my-mosquitto-broker
cd ..
cd http-api
docker build -t http_iot_inventory_api_lab:0.1 .
docker run --name=http-inventory-api-lab --network iot_network -p 7070:7070 --restart always -d http_iot_inventory_api_lab:0.1
docker stop http-inventory-api-lab
docker rm http-inventory-api-lab
cd ..
cd data-fetcher
docker build -t mqtt_data_fetcher_lab:0.1 .
docker run --name=mqtt_data_fetcher_lab --network iot_network -v .\target_fetcher_conf.yaml:\app\fetcher_conf.yaml --restart always -d mqtt_data_fetcher_lab:0.1
docker stop mqtt_data_fetcher_lab
docker rm mqtt_data_fetcher_lab
cd ..
cd web-ui
docker build -t web-ui-lab:0.1 .
docker run --name=web-ui-lab -p 7071:7071 --network iot_network -v .\target_web_conf.yaml:\app\web_conf.yaml --restart always -d web-ui-lab:0.1
docker stop web-ui-lab
docker rm web-ui-lab
cd ..