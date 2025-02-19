cd http-api
docker build -t http_iot_inventory_api_lab:0.1 .
cd ..
cd data-fetcher
docker build -t mqtt_data_fetcher_lab:0.1 .
cd ..
cd web-ui
docker build -t web-ui-lab:0.1 .
cd ..
::gateway-http-mqtt
::sudo docker build -t gateway_http_mqtt_lab:0.1 .
::cd ..
::drone_control
::sudo docker build -t drone_control_img:0.1 .
::cd ..
::localization_service
::sudo docker build -t localization_service_img:0.1 .
::cd ..
::cd system_monitoring_service
::docker build -t system_monitoring_service_img:0.1 .
::cd ..

