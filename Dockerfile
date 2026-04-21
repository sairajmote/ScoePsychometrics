# Use the official Python slim image for a smaller footprint
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
# libpq-dev is useful for PostgreSQL connections if you ever switch from psycopg2-binary
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose the port the app runs on
EXPOSE 8000

# Create startup script to run migrations then start app
RUN echo '#!/bin/bash\n\
echo "Running Alembic migrations..."\n\
alembic upgrade head\n\
echo "Starting FastAPI app..."\n\
uvicorn backend.main:app --host 0.0.0.0 --port 8000' > /start.sh && chmod +x /start.sh

# Start the application with migrations
CMD ["/start.sh"]