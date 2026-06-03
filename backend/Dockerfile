FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    gcc libpq-dev \
    poppler-utils \
    tesseract-ocr tesseract-ocr-por tesseract-ocr-eng \
    libnss3 libnspr4 libatk1.0-0 libatk-bridge2.0-0 \
    libcups2 libdrm2 libxkbcommon0 libxcomposite1 \
    libxdamage1 libxfixes3 libxrandr2 libgbm1 libasound2 \
    libpango-1.0-0 libcairo2 libgdk-pixbuf-2.0-0 \
    fonts-liberation fonts-noto-color-emoji \
    wget curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN playwright install chromium
COPY . .
