#!/bin/bash

# MY JANTES Flutter Web Startup Script
echo "🚀 Starting MY JANTES Flutter Application..."

# Set environment variables
export PORT=${PORT:-5000}
export FLUTTER_WEB_BUILD_PATH="flutter_app/build/web"

# Check if Flutter is installed
if command -v flutter &> /dev/null; then
    echo "✅ Flutter detected"
    
    # Navigate to Flutter app directory
    cd flutter_app
    
    # Get dependencies
    echo "📦 Installing dependencies..."
    flutter pub get
    
    # Build web version if not exists
    if [ ! -d "build/web" ]; then
        echo "🔨 Building Flutter web application..."
        flutter build web --release
    else
        echo "✅ Flutter web build exists"
    fi
    
    # Start Flutter web server
    echo "🌐 Starting Flutter web server on port $PORT..."
    flutter run -d web-server --web-hostname=0.0.0.0 --web-port=$PORT
    
else
    echo "⚠️  Flutter not found, using Python fallback server..."
    cd ..
    python3 main.py
fi