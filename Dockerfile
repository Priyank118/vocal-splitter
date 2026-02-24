# Build stage for frontend
FROM node:20-alpine AS frontend-builder
WORKDIR /app/splitter
COPY splitter/package*.json ./
RUN npm cache clean --force && npm install --legacy-peer-deps
COPY splitter/ .
RUN npm run build

# Python backend stage
FROM python:3.11-slim
WORKDIR /app

# Install system dependencies (for spleeter and audio processing)
RUN apt-get update && apt-get install -y \
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
