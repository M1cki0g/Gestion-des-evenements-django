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

# Create startup script
RUN echo '#!/bin/bash\npython manage.py collectstatic --noinput\npython manage.py migrate --noinput\ngunicorn main.wsgi:application --bind 0.0.0.0:8080' > /app/start.sh \
    && chmod +x /app/start.sh

# Copy project (after creating startup script)
COPY . /app/

# Create static files directory
RUN mkdir -p /app/staticfiles

# Expose port
EXPOSE 8000

# Run the startup script
CMD ["/app/start.sh"]
