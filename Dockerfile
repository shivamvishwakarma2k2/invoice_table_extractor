# filename: Dockerfile

FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    tesseract-ocr \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose required port
EXPOSE 7860

# Run Streamlit app with ALL required configs
CMD ["streamlit", "run", "app.py",
     "--server.port=7860",
     "--server.address=0.0.0.0",
     "--server.enableCORS=false",
     "--server.enableXsrfProtection=false",
     "--server.maxUploadSize=200"]
     