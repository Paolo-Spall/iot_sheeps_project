FROM python:3.9-slim-buster

# Copy Application Files & Requirements to /app
COPY app /app
COPY requirements.txt /app/requirements.txt

# Set the target container working directory to /app
WORKDIR /app

# Install Python Application Requirements
RUN pip3 install -r requirements.txt

# Python Container Application Configurations
ENV PYTHONPATH "/app/"
ENV PYTHONUNBUFFERED 1

# Copia ed esegui uno script per avviare entrambi i file Python
COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh

# Avvia lo script di startup
CMD ["./start.sh"]