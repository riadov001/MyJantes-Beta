# MY JANTES Flutter Application

## Overview

MY JANTES is a comprehensive Flutter mobile application for a specialized aluminum wheel renovation service based in Liévin, France. The app provides a complete customer experience with online booking, quote requests with photo uploads, and an admin dashboard for business management. The application supports multiple platforms (iOS, Android, and Web) and is designed for deployment through Codemagic CI/CD with various distribution channels including Google Play Store, TestApp.io for iOS testing, and web hosting on Hostinger.

**Recent Update (August 20, 2025)**: Successfully implemented complete invoicing module with manual invoice creation, quote-to-invoice conversion, email sending, client notifications, and full admin dashboard integration. Added comprehensive invoice management with search, filtering, and status tracking.

**Deployment Fix (August 21, 2025)**: Successfully resolved all critical Replit deployment issues with comprehensive health check implementation, proper Cloud Run configuration, enhanced Flutter SDK handling with automatic installation, improved error handling with graceful fallbacks, and robust port binding for deployment environments. Updated fallback system to display professional MY JANTES homepage instead of "deployment in progress" message, providing full business information and services to visitors.

**Backend Implementation (August 21, 2025)**: Created complete Python backend with SQLite database replacing WordPress integration. Implemented full CRUD operations for devis (quotes), reservations, and factures (invoices) with automatic pricing, unique ID generation, and professional web interface. All business functionalities now operational without external dependencies.

**Interface Modernization (August 21, 2025)**: Completely redesigned responsive interface with authentic MyJantes.fr content. Added official logo integration, modern CSS animations, mobile-responsive navigation, hero section with authentic company information, comprehensive legal pages (mentions légales, CGV, politique de confidentialité, garantie), and professional footer. Interface now matches company branding with red color scheme (#DC2626) and authentic business information.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
The application follows a standard Flutter architecture pattern with clear separation of concerns:

- **Main Entry Point**: Single `main.dart` file bootstraps the app with MaterialApp configuration
- **Screen-Based Navigation**: Separate screen widgets for home, booking, quotes, admin dashboard, and legal pages
- **State Management**: Provider pattern for managing application state and user authentication
- **Service Layer**: Dedicated services for API communication and authentication logic
- **Model Layer**: Data models for bookings, quotes, and user management
- **Theme System**: Centralized theme configuration with MY JANTES branding (red #DC2626, Roboto fonts)

The app implements Material Design 3 principles with custom theming to match the brand identity. The responsive design adapts to mobile, tablet, and web viewport sizes.

### Backend Integration
The Flutter app integrates with a WordPress backend through REST API endpoints:

- **API Service**: HTTP client wrapper for WordPress REST API communication
- **Authentication Service**: JWT-based authentication for admin access
- **File Upload**: Image upload functionality for quote requests with photo attachments
- **Local Storage**: SharedPreferences for caching user preferences and authentication tokens

### Platform-Specific Configurations

**Android Configuration**:
- Bundle identifier: `fr.myjantes.app`
- Configured for both APK distribution and Google Play Store app bundles
- Keystore signing setup for production releases

**iOS Configuration**: 
- Bundle identifier: `fr.myjantes.app`
- Configured for ad-hoc distribution through TestApp.io (avoiding Apple Developer account requirement)
- Standard iOS project structure with proper xcodeproj setup

**Web Configuration**:
- Progressive Web App (PWA) ready with manifest.json
- Optimized for deployment on Hostinger hosting
- SEO-friendly with proper meta tags and Open Graph configuration

### CI/CD Architecture
The project uses Codemagic for automated builds and deployment:

- **Multi-platform Builds**: Separate workflows for Android, iOS, and Web
- **Automated Signing**: Keystore management for Android releases
- **Artifact Distribution**: Automated upload to various distribution channels
- **Environment Management**: Separate configurations for development and production

## External Dependencies

### Core Flutter Dependencies
- **flutter**: SDK framework for cross-platform development
- **http**: REST API communication with WordPress backend
- **provider**: State management for user authentication and app state
- **shared_preferences**: Local storage for user preferences and tokens
- **image_picker**: Camera and gallery access for photo uploads in quote requests
- **url_launcher**: External link handling for contact information and legal pages
- **intl**: Internationalization support for French locale

### Backend Services
- **WordPress REST API**: Custom endpoints for booking management, quote requests, and admin authentication
- **File Upload Service**: WordPress media handling for customer photo uploads

### Distribution Platforms
- **Google Play Store**: Primary Android distribution channel with app bundle support
- **TestApp.io**: iOS testing distribution platform (bypassing Apple Developer account requirement)
- **Replit Cloud Run**: Web deployment platform with automatic Flutter build detection and Python fallback server

## Recent Deployment Changes (August 20, 2025)

### Critical Deployment Issues Resolved
Successfully fixed all Replit deployment configuration problems:
- **Missing Deployment Section**: Created `replit_deployment.toml` with proper Cloud Run configuration
- **Build Command Integration**: Added comprehensive Flutter web build process with fallback mechanisms
- **Run Command Variables**: Fixed undefined `$file` variable issues in deployment scripts
- **Environment Detection**: Implemented smart production vs development environment detection

### Enhanced Deployment Architecture
- **Intelligent Build System**: Automatic Flutter SDK detection with graceful degradation
- **Multi-Script Deployment**: Enhanced `main.py`, `run.py`, and new `deploy.py` for comprehensive deployment handling
- **Professional Homepage Fallback**: When Flutter unavailable, serves complete MY JANTES business homepage with services, contact info, and professional branding
- **Cloud Run Optimization**: Memory and CPU limits, auto-scaling, health check configuration
- **Port Management**: Dynamic port binding with environment variable support
- **Build Verification**: Post-build validation ensures deployment success

### Updated Deployment Files (August 20, 2025 - Final Fix)
- `main.py`: Enhanced Python server with Flutter build detection and professional fallback
- `run.py`: Improved deployment logic with environment-specific behavior  
- `deploy.py`: New comprehensive deployment script with timeout handling, intelligent build detection, and professional fallback
- `replit_deployment.toml`: Complete deployment configuration for Cloud Run with fixed run commands
- `.replit.template`: Complete deployment template with all missing sections
- `DEPLOYMENT_FIXES_APPLIED.md`: Comprehensive documentation of all three deployment fixes applied
- All deployment scripts now use consistent `python3` executable paths
- Professional branded fallback system when Flutter SDK unavailable
- **Hostinger Web Hosting**: Web deployment platform for PWA version

### Development and CI/CD Tools
- **Codemagic**: Primary CI/CD platform for automated builds and deployments
- **GitHub/GitLab**: Source code repository management
- **Android Keystore**: Production signing for Google Play releases
- **TestApp.io Distribution**: iOS app distribution for testing without App Store

The architecture is designed for scalability and maintainability, with clear separation between platform-specific code and shared business logic. The multi-platform approach ensures maximum reach while maintaining a consistent user experience across all devices.