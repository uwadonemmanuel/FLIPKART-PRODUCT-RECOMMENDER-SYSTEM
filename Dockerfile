## Parent image
FROM python:3.10-slim

## Essential environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

## Work directory inside the docker container
WORKDIR /app

## Installing system dependancies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

## Copy requirements first for better caching
COPY requirements.txt .

## Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

## Copying all contents from local to app
COPY . .

## Install the package in editable mode
RUN pip install --no-cache-dir -e .

# Used PORTS
EXPOSE 5000

# Run the app 
CMD ["python", "app.py"]