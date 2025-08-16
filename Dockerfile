# Multi-stage build for Flutter web deployment
FROM ubuntu:22.04 as flutter-builder

# Install dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    wget \
    unzip \
    libgconf-2-4 \
    gdb \
    libstdc++6 \
    libglu1-mesa \
    fonts-droid-fallback \
    lib32stdc++6 \
    python3 \
    && rm -rf /var/lib/apt/lists/*

# Install Flutter
ENV FLUTTER_VERSION=3.16.0
RUN wget -O flutter.tar.xz https://storage.googleapis.com/flutter_infra_release/releases/stable/linux/flutter_linux_${FLUTTER_VERSION}-stable.tar.xz \
    && tar xf flutter.tar.xz \
    && mv flutter /opt/ \
    && rm flutter.tar.xz

# Add Flutter to PATH
ENV PATH="/opt/flutter/bin:${PATH}"

# Pre-download Flutter dependencies
RUN flutter doctor
RUN flutter config --enable-web

# Set working directory
WORKDIR /app

# Copy Flutter project
COPY flutter_app/ ./

# Get dependencies and build
RUN flutter pub get
RUN flutter build web --release

# Production stage - lightweight Python server
FROM python:3.11-slim

WORKDIR /app

# Copy built Flutter web app
COPY --from=flutter-builder /app/build/web/ ./web/

# Copy Python server script
COPY main.py ./

# Create startup script
RUN echo '#!/bin/bash\ncd /app\npython3 main.py' > start.sh && chmod +x start.sh

# Expose port
EXPOSE 5000

# Set environment variable for production
ENV PORT=5000
ENV FLUTTER_WEB_BUILD_PATH=/app/web

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/ || exit 1

# Start the server
CMD ["python3", "main.py"]