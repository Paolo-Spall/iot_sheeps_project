cd notification_microservice
sudo docker build -t notification_microservice_img:0.1 .
sudo docker run --name=notification_microservice --network iot_network -v ${PWD}/target_notification_microservice_conf.yaml:/app/notification_microservice_conf.yaml --restart always -d notification_microservice_img:0.1
sudo docker stop notification_microservice
sudo docker rm notification_microservice
cd ..
cd notification_client
sudo docker build -t notification_client_img:0.1 .
sudo docker run --name=notification_client_cnt --network iot_network -v ${PWD}/target_notification_client_conf.yaml:/app/notification_client_conf.yaml --restart always -d notification_client_img:0.1
sudo docker stop notification_client_cnt
sudo docker rm notification_client_cnt
cd ..
