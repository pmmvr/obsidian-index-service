FROM python:3.13-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV OBSIDIAN_VAULT_PATH=/vault
ENV DB_PATH=/data/notes.sqlite

WORKDIR /app

RUN apt-get update && apt-get install -y \
  sqlite3 \
  && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY . /app/

# Create directories for volumes
RUN mkdir -p /vault /data

# Install dependencies
RUN pip install --no-cache-dir -e .

# Run the application
CMD ["python", "main.py"] 
