FROM python:3.9-slim-buster

# Install system dependencies including tkinter
RUN apt-get update && apt-get install -y python3-tk && rm -rf /var/lib/apt/lists/*

# Copy Application Files & Requirements to /app
COPY ./app /app
COPY requirements.txt /app/requirements.txt

# Set the target container working directory to /app
WORKDIR /app

# Install Python Application Requirements
RUN pip3 install -r requirements.txt

# Python Container Application Configurations
ENV PYTHONPATH "/app/"
ENV PYTHONUNBUFFERED 1

# Run the target application
CMD [ "python3", "notification_client.py" ]