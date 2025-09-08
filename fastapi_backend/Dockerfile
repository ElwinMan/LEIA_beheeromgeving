# Use official Python image
FROM python:3.13-slim

# Set work directory for the entire container
WORKDIR /

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Copy alembic configuration
COPY alembic.ini .
COPY alembic/ ./alembic/

# Copy app files to /app
COPY ./src /app

# Copy migration script
COPY migrate.sh /migrate.sh
RUN chmod +x /migrate.sh

# Set Python path
ENV PYTHONPATH=/app

# Default command (will be overridden by docker-compose)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
