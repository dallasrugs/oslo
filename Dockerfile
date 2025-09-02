# Use a lightweight Python image
FROM python:3.12-slim

# Set working directory inside the container
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies for building Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        gcc \
        libffi-dev \
        libssl-dev \
        && rm -rf /var/lib/apt/lists/*

# Create a virtual environment
RUN python -m venv /opt/venv

# Make sure the virtualenv's bin directory is in PATH
ENV PATH="/opt/venv/bin:$PATH"

# Install Python dependencies inside virtualenv
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy app code
COPY app/ .

# Expose the port FastAPI will run on
EXPOSE 8000

# Command to run FastAPI using dev
WORKDIR /app
CMD ["fastapi", "dev", "main.py", "--host", "0.0.0.0", "--port", "8000"]

