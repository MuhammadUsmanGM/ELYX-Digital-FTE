# Use a Python 3.13 base image for the AI Employee system
FROM python:3.13-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    gnupg \
    libpq-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js and npm (for frontend and MCP servers)
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && npm install -g npm

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers (for LinkedIn automation)
RUN playwright install chromium

# Copy the rest of the application code
COPY . .

# Create necessary directories for the vault
RUN mkdir -p obsidian_vault/Needs_Action \
    obsidian_vault/Plans \
    obsidian_vault/Pending_Approval \
    obsidian_vault/Done \
    obsidian_vault/Logs \
    obsidian_vault/Responses

# Install frontend dependencies if they exist
WORKDIR /app/frontend
RUN npm install --legacy-peer-deps 2>/dev/null || echo "No frontend dependencies to install"

# Go back to main directory
WORKDIR /app

# Expose the port for the API
EXPOSE 8000

# Create a non-root user for security
RUN adduser --disabled-password --gecos '' appuser && \
    chown -R appuser:appuser /app
USER appuser

# Run the complete system
CMD ["python", "run_complete_system.py"]