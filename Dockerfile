FROM python:3.9

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN /usr/local/bin/python -m pip install --upgrade pip setuptools wheel

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install -r requirements.txt

# Copy project
COPY . /app/

# Collect static files
RUN python manage.py collectstatic --noinput

# Expose port
EXPOSE 8000

# Run server
CMD ["gunicorn", "main.wsgi:application", "--bind", "0.0.0.0:8000"]
