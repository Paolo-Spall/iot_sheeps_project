# IoT Sheeps Project

This repository contains a demo version of an IoT software system designed for managing a fleet of drones used for sheep grazing monitoring. It was developed as the project for the **Distributed and Internet of Things Software Architectures** course.

## Overview

**Platform Support:**  
- Multiplatform: Linux, iOS, Windows  

**Architecture:**  
- Based on a microservice architecture  
- Containerized using Docker  
- Services are deployed on a Docker network and orchestrated with Docker Compose

## Microservices

The system is composed of the following containerized microservices, each with its own `Dockerfile`, `requirements.txt`, and configuration file:

- **data-fetcher**
- **drone_control**
- **gateway-http-mqtt**
- **http-api**
- **localization_service**
- **mqtt-broker**
- **notification_microservice**
- **system_monitoring_service**

## Non-containerized Components

In addition to the microservices, the project includes the following components which run outside of Docker:

### Drone Simulation Models

- **Location:** `mqtt-tester/`
- **Files:** `drone_device_#.py` (where `#` represents individual drone simulation scripts)  
- **Purpose:** Simulate the drones used for monitoring

### Notification Socket Client

- **Location:** `notification_client/`
- **File:** `notification_client.py`
- **Purpose:** Deployed locally on the machine, this client receives socket notifications and visualizes them on your computer

## Deployment & Execution

### Orchestrating with Docker Compose

The microservices are orchestrated via Docker Compose. The Docker Compose configuration file is located in the `docker-compose/` directory.

To start the containerized services, run:

```bash
docker-compose -f docker-compose/docker-compose.yml up --build
```

### Running the Notification Client

In a separate terminal, start the notification client by running:

```bash
python notification_client/notification_client.py
```

### Running the Drone Simulation

Depending on your operating system, run the drone simulation scripts as follows:

- **Linux/Mac:**  
  Execute the bash script:
  ```bash
  ./drones_runner_test.sh
  ```
- **Windows:**  
  Run the Python script:
  ```bash
  python drones_runner_test.py
  ```

## Repository Structure

```
iot_sheeps_project/
├── docker-compose/
│   └── docker-compose.yml
├── data-fetcher/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── config.yml
├── drone_control/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── config.yml
├── gateway-http-mqtt/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── config.yml
├── http-api/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── config.yml
├── localization_service/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── config.yml
├── mqtt-broker/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── config.yml
├── notification_microservice/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── config.yml
├── system_monitoring_service/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── config.yml
├── mqtt-tester/
│   ├── drone_device_1.py
│   ├── drone_device_2.py
│   └── ... (other drone simulation scripts)
├── notification_client/
│   └── notification_client.py
├── drones_runner_test.sh    # For Linux/Mac
└── drones_runner_test.py    # For Windows
```

## Prerequisites

- **Docker** and **Docker Compose** must be installed to run the containerized microservices.
- **Python 3.x** is required for running the notification client and the drone simulation scripts.
- **Bash shell** (for Linux/Mac users) to execute the `drones_runner_test.sh` script.

## Contributing

Contributions, bug fixes, and enhancements are welcome! Please open an issue or submit a pull request if you have suggestions.

## License

*Include license information here if applicable.*

## Contact

For questions or support, please contact [your_email@example.com](mailto:your_email@example.com).
