FROM python:3.11-slim

# Install curl for the healthcheck
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install dependencies (leverages Docker cache if requirements.txt doesn't change)
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY backend/ .

# Copy lightweight DB reference for standalone execution
# The compose file will mount the real DB dynamically over this location
COPY database.sqlite /database.sqlite

# Unbuffered output for better debugging
ENV PYTHONUNBUFFERED=1
EXPOSE 5000

CMD ["python", "app.py"]
