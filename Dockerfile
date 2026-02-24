# Build stage for frontend
FROM node:20-alpine AS frontend-builder
WORKDIR /app/splitter

# Copy package files
COPY splitter/package*.json ./
COPY splitter/.nvmrc ./

# Clean install with better error handling
RUN npm ci --prefer-offline --no-audit || npm install --legacy-peer-deps

# Copy source code
COPY splitter/src ./src
COPY splitter/index.html ./
COPY splitter/vite.config.js ./
COPY splitter/eslint.config.js ./

# Build frontend
RUN npm run build && ls -la dist/

# Python backend stage
FROM python:3.11-slim
WORKDIR /app

# Install system dependencies (for spleeter and audio processing)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libsndfile1 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY vocal-splitter-backend/requirements-deploy.txt .
RUN pip install --no-cache-dir -r requirements-deploy.txt

# Copy backend files
COPY vocal-splitter-backend/ .

# Copy built frontend from builder stage
COPY --from=frontend-builder /app/splitter/dist ./static

# Create necessary directories
RUN mkdir -p uploads output spleeter_models

# Expose port
EXPOSE 8000

# Run the Flask app with Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--timeout", "300", "--workers", "1", "app:app"]
