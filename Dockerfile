FROM python:3.9

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies including PostgreSQL development headers
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    libpq-dev \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN /usr/local/bin/python -m pip install --upgrade pip setuptools wheel

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install -r requirements.txt

# Copy project files
COPY . /app/

# Make the startup script executable
RUN chmod +x /app/start.sh

# Create static files directory
RUN mkdir -p /app/staticfiles

# Expose port
EXPOSE 8000

# Run the startup script
CMD ["/app/start.sh"]
