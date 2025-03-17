# Use a lightweight Python image
FROM python:3.10-slim

# Install system dependencies (Poppler, Tesseract for OCR)
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    libopenjp2-7-dev \
    libjpeg-dev \
    libpng-dev \
    zlib1g-dev \
    tesseract-ocr \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy project files
COPY . .

# Keep the prints
ENV PYTHONUNBUFFERED=1

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose FastAPI's default port
EXPOSE 8000

# Command to run FastAPI with Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]