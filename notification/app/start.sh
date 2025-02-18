#!/bin/bash
# Avvia entrambi gli script Python
python3 notification_microservice.py &  # Avvia in background
python3 notification_client.py          # Avvia in foreground

