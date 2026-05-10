# Create Dockerfile at project root
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies (if needed by Bandit or other tools)
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY eval/ ./eval/

# Expose port
EXPOSE 8000

# Set environment variables (will be overridden at runtime)
ENV PYTHONUNBUFFERED=1

# Run FastAPI
CMD ["uvicorn", "src.api:app", "--host", "0.0.0.0", "--port", "8000"]