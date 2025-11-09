# Dockerfile for AI Triage Agent
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Create directories for data and logs
RUN mkdir -p data logs

# Expose Streamlit port
EXPOSE 5000

# Run the application
CMD ["streamlit", "run", "triage_ai.py", "--server.port", "5000", "--server.address", "0.0.0.0"]
