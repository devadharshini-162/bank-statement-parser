FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies (needed for PyMuPDF / Tesseract fallback if required later)
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements
COPY requirements.txt .

# Install python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy all backend code
COPY . .

# Expose port (Render gives PORT dynamically, so we default to 8000)
ENV PORT=8000
EXPOSE 8000

# Start fastapi using uvicorn
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]
