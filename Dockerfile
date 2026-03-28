# ------------------------------
# Base image
# ------------------------------
FROM python:3.10-slim

WORKDIR /app

# ------------------------------
# System dependencies
# ------------------------------
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# ------------------------------
# Python dependencies
# ------------------------------
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# ------------------------------
# Copy environment code
# ------------------------------
COPY . /app

# ------------------------------
# Expose HF Space port
# ------------------------------
EXPOSE 7860

# ------------------------------
# Run server
# ------------------------------
CMD ["python", "app.py"]
