# MY JANTES - Application Flutter

Application mobile native pour MY JANTES, spécialiste en rénovation de jantes aluminium.

## 🚀 Caractéristiques

### 📱 Support multi-plateforme
- **iOS** : Support complet iPhone/iPad
- **Android** : Compatible Android 5.0+
- **Web** : Version web responsive

### 🛠️ Fonctionnalités principales
- **Réservation en ligne** : Système de prise de rendez-vous
- **Demande de devis** : Formulaire avec upload de photos
- **Catalogue des services** : Rénovation, personnalisation, dévoilage, décapage
- **Dashboard admin** : Gestion des réservations et devis
- **Pages légales** : Conformité RGPD complète

### 🎨 Design
- **Thème My Jantes** : Couleurs authentiques (rouge #DC2626)
- **Typography** : Roboto & Roboto Condensed
- **UI moderne** : Material Design avec composants personnalisés
- **Responsive** : Adaptation automatique mobile/tablette

## 🔧 Installation

### Prérequis
- Flutter SDK 3.16.0+
- Dart SDK 3.0.0+
- Android Studio / VS Code
- Xcode (pour iOS)

### Installation des dépendances
```bash
cd flutter_app
flutter pub get
```

### Configuration du backend
1. Mettez à jour l'URL du backend dans `lib/services/api_service.dart` :
```dart
static const String baseUrl = 'https://votre-domaine-hostinger.com/wp-json/myjantes/v1';
```

2. Assurez-vous que le backend WordPress est déployé et fonctionnel

### Lancement de l'application
```bash
# Version debug
flutter run

# Version release
flutter run --release

# Web
flutter run -d chrome
```

## 🏗️ Architecture

### Structure du projet
```
flutter_app/
├── lib/
│   ├── main.dart              # Point d'entrée de l'application
│   ├── models/                # Modèles de données
│   │   ├── booking.dart
│   │   ├── service.dart
│   │   └── quote.dart
│   ├── screens/               # Écrans de l'application
│   │   ├── home_screen.dart
│   │   ├── booking_screen.dart
│   │   ├── quote_screen.dart
│   │   ├── dashboard_screen.dart
│   │   ├── login_screen.dart
│   │   └── legal/             # Pages légales
│   ├── services/              # Services API et authentification
│   │   ├── api_service.dart
│   │   └── auth_service.dart
│   └── utils/
│       └── themes.dart        # Thème et styles
├── assets/
│   ├── images/                # Images de l'application
│   └── icons/                 # Icônes et logo
└── pubspec.yaml              # Configuration des dépendances
```

### Technologies utilisées
- **Flutter 3.16+** : Framework de développement
- **Provider** : Gestion d'état
- **go_router** : Navigation déclarative
- **http** : Requêtes API
- **google_fonts** : Typography Roboto
- **image_picker** : Upload de photos
- **cached_network_image** : Cache des images
- **flutter_secure_storage** : Stockage sécurisé

## 🚀 Déploiement

### Android (Google Play Store)
1. Générer la clé de signature :
```bash
keytool -genkey -v -keystore upload-keystore.jks -keyalg RSA -keysize 2048 -validity 10000 -alias upload
```

2. Compiler l'APK :
```bash
flutter build apk --release
```

3. Compiler l'App Bundle :
```bash
flutter build appbundle --release
```

### iOS (App Store)
1. Configurer le signing dans Xcode
2. Compiler l'IPA :
```bash
flutter build ios --release
```

### Web
1. Compiler pour le web :
```bash
flutter build web --release
```

2. Déployer le dossier `build/web/`

## 🔒 Sécurité et Conformité

### RGPD
- **Pages légales complètes** : Mentions, CGV, confidentialité, garanties
- **Consentement explicite** : Pour les communications marketing
- **Droit à l'oubli** : Suppression des données sur demande
- **Portabilité** : Export des données personnelles

### Sécurité
- **Stockage sécurisé** : Données sensibles chiffrées
- **HTTPS** : Communication sécurisée avec le backend
- **Validation des données** : Contrôles côté client et serveur
- **Authentification** : JWT pour l'accès admin

## 📞 Support

**MY JANTES**
- 📍 46 rue de la Convention, 62800 Liévin
- ☎️ 03.21.40.80.53
- ✉️ contact@myjantes.fr
- 🕒 Lun-Ven 9h-12h/13h30-18h, Sam 9h-13h

## 📝 Licence

© 2025 MY JANTES. Tous droits réservés.# MyJantesFlutterApp
# MyJantes-Beta
