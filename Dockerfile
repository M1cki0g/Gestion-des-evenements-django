FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=main.settings

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy project
COPY . /app/

# Create static files directory
RUN mkdir -p /app/staticfiles

# Write a simpler startup script
RUN echo '#!/bin/sh\n\
echo "Starting application..."\n\
echo "Collecting static files..."\n\
COLLECTSTATIC_DRYRUN=1 python manage.py collectstatic --noinput || true\n\
echo "Starting server..."\n\
python server.py' > /app/entrypoint.sh \
    && chmod +x /app/entrypoint.sh

# Expose port
EXPOSE 8080

# Run the script at startup
CMD ["/app/entrypoint.sh"]
