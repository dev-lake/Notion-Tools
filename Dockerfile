# Use Python 3.11 slim image as base
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_APP=app.py \
    FLASK_ENV=production

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app.py .
COPY converter.py .
COPY pdf_converter.py .
COPY templates/ templates/
COPY static/ static/
COPY translations/ translations/

# Create necessary directories
RUN mkdir -p uploads output && \
    chmod 755 uploads output

# Expose port (can be overridden by PORT env var)
EXPOSE 8080

# Health check (use PORT env var if set)
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import os, requests; port=os.environ.get('PORT', '8080'); requests.get(f'http://localhost:{port}/', timeout=5)" || exit 1

# Run the application with gunicorn for production
# Use PORT environment variable, default to 8080
CMD gunicorn --bind 0.0.0.0:${PORT:-8080} --workers 2 --threads 4 --timeout 120 --access-logfile - --error-logfile - --log-level info app:app
