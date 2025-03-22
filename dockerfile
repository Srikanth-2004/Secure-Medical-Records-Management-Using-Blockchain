# Dockerfile
FROM python:3.9-slim

WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the init.sql file into the container
COPY docker-entrypoint-initdb.d/init.sql /app/init.sql

# Copy the rest of the application code
COPY . .

# Ensure Flask logs are printed to the terminal
ENV PYTHONUNBUFFERED=1

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]