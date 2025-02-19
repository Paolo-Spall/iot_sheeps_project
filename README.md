# IoT Sheeps Project

This repository contains a demo version of an IoT software for the management of a fleet of drones used for sheep grazing monitoring. It is a project for the "Distributed and Internet of Things Software Architectures" course.

## Overview

- Multiplatform (Linux, iOS, Windows).
- Based on a microservice architecture.
- Bely on Docker for containerization.

## Microservices

The project is composed of the following microservices:

- data-fetcher
- drone_control
- gateway-http-mqtt
- http-api
- localization_service
- mqtt-broker
- notification_microservice
- system_monitoring_service

Each microservice is containerized using Docker, and each has its own `Dockerfile`, `requirements.txt` file, and configuration files. They are deployed on a Docker network.

## Directory Structure

- **microservices**: Each one of the previous mentioned microservices ha its own directory in the root repository.
- **docker-compose**: Contains the `docker-compose.yml` file used to orchestrate the running of the microservices.
- **mqtt-tester**: Contains the models which simulate the drones (`drone_device_#.py`).
- **notification_client**: Contains the notification socket client (`notification_client.py`).

## Running the System

### Step 1: Run Docker Compose

Navigate to the `docker-compose` directory and run the following command to start all the microservices:

```sh
docker-compose up --build
```

### Step 2: Run the Notification Client

Run the `notification_client.py` script locally on your machine to receive socket notifications and visualize them on the computer:

```sh
python notification_client/notification_client.py
```

### Step 3: Run the Drones Script

You can run the drones script using a single command. For Linux and macOS, use the bash script `drones_runner_test.sh`:

```sh
./drones_runner_test.sh
```

For Windows, use the Python script `drones_runner_test.py`:

```sh
python drones_runner_test.py
```

## Components Not in Containers

- **Models which simulate the drones**: Located in `mqtt-tester/drone_device_#.py`.
- **Notification socket client**: Located in `notification_client/notification_client.py`.

These components are deployed locally on the machine.

## Conclusion

This project demonstrates the use of a microservice architecture for managing a fleet of drones used for sheep grazing monitoring. By leveraging Docker for containerization and Docker Compose for orchestration, the system is easily deployable and scalable across multiple platforms.
