#!/usr/bin/env python3
"""
Backend server for MY JANTES application
Provides API endpoints for devis, reservations, and invoices
"""
import os
import json
import http.server
import socketserver
import urllib.parse
from pathlib import Path
import sqlite3
from datetime import datetime
import uuid

class MyJantesAPI:
    def __init__(self):
        self.db_path = "myjantes.db"
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Table des devis
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS devis (
                id TEXT PRIMARY KEY,
                client_name TEXT NOT NULL,
                client_email TEXT NOT NULL,
                client_phone TEXT,
                service_type TEXT NOT NULL,
                description TEXT,
                prix REAL,
                status TEXT DEFAULT 'en_attente',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Table des réservations
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reservations (
                id TEXT PRIMARY KEY,
                client_name TEXT NOT NULL,
                client_email TEXT NOT NULL,
                client_phone TEXT,
                service_type TEXT NOT NULL,
                date_rdv TEXT NOT NULL,
                heure_rdv TEXT NOT NULL,
                description TEXT,
                status TEXT DEFAULT 'confirmee',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Table des factures
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS factures (
                id TEXT PRIMARY KEY,
                devis_id TEXT,
                client_name TEXT NOT NULL,
                client_email TEXT NOT NULL,
                service_type TEXT NOT NULL,
                montant REAL NOT NULL,
                status TEXT DEFAULT 'en_attente',
                date_facture TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (devis_id) REFERENCES devis (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def create_devis(self, data):
        """Créer un nouveau devis"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        devis_id = str(uuid.uuid4())[:8]
        prix = self.calculate_price(data.get('service_type', ''))
        
        cursor.execute('''
            INSERT INTO devis (id, client_name, client_email, client_phone, 
                             service_type, description, prix)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (devis_id, data['client_name'], data['client_email'], 
              data.get('client_phone', ''), data['service_type'], 
              data.get('description', ''), prix))
        
        conn.commit()
        conn.close()
        
        return {
            'success': True,
            'devis_id': devis_id,
            'prix_estime': prix,
            'message': f'Devis #{devis_id} créé avec succès'
        }
    
    def create_reservation(self, data):
        """Créer une nouvelle réservation"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        reservation_id = str(uuid.uuid4())[:8]
        
        cursor.execute('''
            INSERT INTO reservations (id, client_name, client_email, client_phone,
                                    service_type, date_rdv, heure_rdv, description)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (reservation_id, data['client_name'], data['client_email'],
              data.get('client_phone', ''), data['service_type'],
              data['date_rdv'], data['heure_rdv'], data.get('description', '')))
        
        conn.commit()
        conn.close()
        
        return {
            'success': True,
            'reservation_id': reservation_id,
            'message': f'Réservation #{reservation_id} confirmée pour le {data["date_rdv"]} à {data["heure_rdv"]}'
        }
    
    def create_facture(self, data):
        """Créer une nouvelle facture"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        facture_id = str(uuid.uuid4())[:8]
        date_facture = datetime.now().strftime('%Y-%m-%d')
        
        cursor.execute('''
            INSERT INTO factures (id, devis_id, client_name, client_email,
                                service_type, montant, date_facture)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (facture_id, data.get('devis_id'), data['client_name'], 
              data['client_email'], data['service_type'], 
              data['montant'], date_facture))
        
        conn.commit()
        conn.close()
        
        return {
            'success': True,
            'facture_id': facture_id,
            'date_facture': date_facture,
            'message': f'Facture #{facture_id} générée avec succès'
        }
    
    def get_all_devis(self):
        """Récupérer tous les devis"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM devis ORDER BY created_at DESC')
        devis = cursor.fetchall()
        conn.close()
        
        return [dict(zip([col[0] for col in cursor.description], row)) for row in devis]
    
    def get_all_reservations(self):
        """Récupérer toutes les réservations"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM reservations ORDER BY created_at DESC')
        reservations = cursor.fetchall()
        conn.close()
        
        return [dict(zip([col[0] for col in cursor.description], row)) for row in reservations]
    
    def get_all_factures(self):
        """Récupérer toutes les factures"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM factures ORDER BY created_at DESC')
        factures = cursor.fetchall()
        conn.close()
        
        return [dict(zip([col[0] for col in cursor.description], row)) for row in factures]
    
    def calculate_price(self, service_type):
        """Calculer le prix selon le type de service"""
        prices = {
            'renovation_complete': 150.0,
            'polissage': 80.0,
            'personnalisation': 200.0,
            'reparation': 120.0,
            'renovation': 150.0,
            'custom': 200.0
        }
        return prices.get(service_type, 100.0)

class MyJantesServer(http.server.BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.api = MyJantesAPI()
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """Handle GET requests"""
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'OK')
            return
        
        # API endpoints
        if self.path == '/api/devis':
            self.send_json_response(self.api.get_all_devis())
        elif self.path == '/api/reservations':
            self.send_json_response(self.api.get_all_reservations())
        elif self.path == '/api/factures':
            self.send_json_response(self.api.get_all_factures())
        elif self.path == '/':
            self.serve_main_page()
        else:
            self.send_404()
    
    def do_POST(self):
        """Handle POST requests"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            # Parse JSON data
            if self.headers.get('Content-Type') == 'application/json':
                data = json.loads(post_data.decode('utf-8'))
            else:
                # Parse form data
                data = urllib.parse.parse_qs(post_data.decode('utf-8'))
                data = {k: v[0] if len(v) == 1 else v for k, v in data.items()}
            
            # Route to appropriate handler
            if self.path == '/api/devis':
                result = self.api.create_devis(data)
                self.send_json_response(result)
            elif self.path == '/api/reservations':
                result = self.api.create_reservation(data)
                self.send_json_response(result)
            elif self.path == '/api/factures':
                result = self.api.create_facture(data)
                self.send_json_response(result)
            else:
                self.send_404()
                
        except Exception as e:
            self.send_error_response(str(e))
    
    def send_json_response(self, data):
        """Send JSON response"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))
    
    def send_error_response(self, error_msg):
        """Send error response"""
        self.send_response(400)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        response = {'success': False, 'error': error_msg}
        self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
    
    def send_404(self):
        """Send 404 response"""
        self.send_response(404)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'Not Found')
    
    def do_OPTIONS(self):
        """Handle OPTIONS requests for CORS"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def serve_main_page(self):
        """Serve the main application page with working forms"""
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        
        html_content = """<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MY JANTES - Les Experts de la Jante Aluminium</title>
    <meta name="description" content="MY JANTES - Spécialiste de la rénovation de jantes en aluminium à Liévin. Qualité exceptionnelle, garantie totale. Rénovation, personnalisation, dévoilage, décapage.">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
        * { 
            margin: 0; 
            padding: 0; 
            box-sizing: border-box; 
        }
        
        :root {
            --primary-color: #DC2626;
            --primary-dark: #B91C1C;
            --primary-light: #FCA5A5;
            --secondary-color: #374151;
            --accent-color: #F59E0B;
            --text-color: #111827;
            --text-light: #6B7280;
            --bg-color: #F9FAFB;
            --white: #FFFFFF;
            --shadow: 0 10px 25px rgba(0,0,0,0.1);
            --shadow-lg: 0 20px 40px rgba(0,0,0,0.15);
            --border-radius: 12px;
            --transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.7;
            color: var(--text-color);
            background: var(--bg-color);
            overflow-x: hidden;
        }
        
        /* Navigation */
        .navbar {
            background: linear-gradient(135deg, var(--primary-color) 0%, var(--primary-dark) 100%);
            color: var(--white);
            padding: 0;
            box-shadow: var(--shadow);
            position: sticky;
            top: 0;
            z-index: 1000;
        }
        
        .navbar-content {
            max-width: 1400px;
            margin: 0 auto;
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 1rem 2rem;
        }
        
        .logo {
            font-size: 2rem;
            font-weight: 900;
            letter-spacing: -1px;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        
        .logo i {
            font-size: 2.2rem;
            color: var(--accent-color);
        }
        
        .nav-links {
            display: flex;
            list-style: none;
            gap: 0;
        }
        
        .nav-links a {
            color: var(--white);
            text-decoration: none;
            padding: 1rem 1.5rem;
            border-radius: var(--border-radius);
            transition: var(--transition);
            font-weight: 500;
            position: relative;
            overflow: hidden;
        }
        
        .nav-links a::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: rgba(255,255,255,0.1);
            transition: var(--transition);
        }
        
        .nav-links a:hover::before,
        .nav-links a.active::before {
            left: 0;
        }
        
        .nav-links a:hover,
        .nav-links a.active {
            background: rgba(255,255,255,0.15);
            transform: translateY(-2px);
        }
        
        .mobile-menu-btn {
            display: none;
            background: none;
            border: none;
            color: var(--white);
            font-size: 1.5rem;
            cursor: pointer;
        }
        
        /* Hero Section */
        .hero {
            background: linear-gradient(135deg, rgba(220, 38, 38, 0.95) 0%, rgba(185, 28, 28, 0.95) 100%),
                        url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 600"><defs><pattern id="grid" width="60" height="60" patternUnits="userSpaceOnUse"><path d="M 60 0 L 0 0 0 60" fill="none" stroke="rgba(255,255,255,0.1)" stroke-width="1"/></pattern></defs><rect width="100%" height="100%" fill="url(%23grid)"/></svg>');
            color: var(--white);
            text-align: center;
            padding: 6rem 2rem;
            position: relative;
            overflow: hidden;
        }
        
        .hero::before {
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
            animation: rotate 30s linear infinite;
            pointer-events: none;
        }
        
        @keyframes rotate {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .hero-content {
            max-width: 800px;
            margin: 0 auto;
            position: relative;
            z-index: 2;
        }
        
        .hero h1 {
            font-size: clamp(2.5rem, 5vw, 4rem);
            font-weight: 900;
            margin-bottom: 1.5rem;
            line-height: 1.2;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        
        .hero .subtitle {
            font-size: clamp(1.1rem, 2vw, 1.3rem);
            margin-bottom: 2rem;
            opacity: 0.95;
            line-height: 1.6;
        }
        
        .hero-cta {
            display: flex;
            gap: 1rem;
            justify-content: center;
            flex-wrap: wrap;
            margin-top: 2rem;
        }
        
        .btn {
            background: var(--white);
            color: var(--primary-color);
            padding: 1rem 2rem;
            border: none;
            border-radius: var(--border-radius);
            cursor: pointer;
            font-size: 1.1rem;
            font-weight: 600;
            transition: var(--transition);
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            box-shadow: var(--shadow);
        }
        
        .btn:hover {
            transform: translateY(-3px);
            box-shadow: var(--shadow-lg);
        }
        
        .btn-secondary {
            background: transparent;
            color: var(--white);
            border: 2px solid var(--white);
        }
        
        .btn-secondary:hover {
            background: var(--white);
            color: var(--primary-color);
        }
        
        /* Container */
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 0 2rem;
        }
        
        .page {
            display: none;
            min-height: 70vh;
        }
        
        .page.active {
            display: block;
        }
        
        /* Services Grid */
        .services-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 2rem;
            padding: 4rem 0;
        }
        
        .service-card {
            background: var(--white);
            padding: 2.5rem;
            border-radius: var(--border-radius);
            box-shadow: var(--shadow);
            transition: var(--transition);
            text-align: center;
            position: relative;
            overflow: hidden;
        }
        
        .service-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 4px;
            background: linear-gradient(90deg, var(--primary-color), var(--accent-color));
            transition: var(--transition);
        }
        
        .service-card:hover::before {
            left: 0;
        }
        
        .service-card:hover {
            transform: translateY(-10px);
            box-shadow: var(--shadow-lg);
        }
        
        .service-card .icon {
            font-size: 3rem;
            color: var(--primary-color);
            margin-bottom: 1.5rem;
        }
        
        .service-card h3 {
            font-size: 1.5rem;
            color: var(--text-color);
            margin-bottom: 1rem;
        }
        
        .service-card p {
            color: var(--text-light);
            line-height: 1.6;
        }
        
        /* Info Section */
        .info-section {
            background: var(--white);
            padding: 4rem 0;
            margin: 4rem 0;
            border-radius: var(--border-radius);
            box-shadow: var(--shadow);
        }
        
        .info-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 3rem;
            text-align: center;
        }
        
        .info-item h4 {
            color: var(--primary-color);
            font-size: 1.3rem;
            margin-bottom: 1rem;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 0.5rem;
        }
        
        .info-item .icon {
            font-size: 1.5rem;
        }
        
        /* Contact Info */
        .contact-info {
            background: linear-gradient(135deg, var(--secondary-color) 0%, var(--text-color) 100%);
            color: var(--white);
            padding: 3rem;
            border-radius: var(--border-radius);
            margin: 3rem 0;
            text-align: center;
        }
        
        .contact-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 2rem;
            margin-top: 2rem;
        }
        
        .contact-item {
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 1rem;
        }
        
        .contact-item .icon {
            font-size: 2rem;
            color: var(--accent-color);
        }
        
        .contact-item h4 {
            font-size: 1.2rem;
            margin-bottom: 0.5rem;
        }
        
        .contact-item a {
            color: var(--white);
            text-decoration: none;
            transition: var(--transition);
        }
        
        .contact-item a:hover {
            color: var(--accent-color);
        }
        
        /* Form Styles */
        .form-container {
            background: var(--white);
            padding: 3rem;
            border-radius: var(--border-radius);
            box-shadow: var(--shadow);
            max-width: 600px;
            margin: 2rem auto;
        }
        
        .form-group {
            margin-bottom: 1.5rem;
        }
        
        .form-group label {
            display: block;
            margin-bottom: 0.5rem;
            font-weight: 600;
            color: var(--text-color);
        }
        
        .form-group input,
        .form-group select,
        .form-group textarea {
            width: 100%;
            padding: 1rem;
            border: 2px solid #E5E7EB;
            border-radius: var(--border-radius);
            font-size: 1rem;
            transition: var(--transition);
            background: var(--bg-color);
        }
        
        .form-group input:focus,
        .form-group select:focus,
        .form-group textarea:focus {
            outline: none;
            border-color: var(--primary-color);
            background: var(--white);
            box-shadow: 0 0 0 3px rgba(220, 38, 38, 0.1);
        }
        
        .form-group textarea {
            resize: vertical;
            min-height: 120px;
        }
        
        /* Messages */
        .success-message,
        .error-message {
            padding: 1rem 1.5rem;
            border-radius: var(--border-radius);
            margin-bottom: 1.5rem;
            display: none;
            font-weight: 500;
        }
        
        .success-message {
            background: #D1FAE5;
            color: #065F46;
            border-left: 4px solid #10B981;
        }
        
        .error-message {
            background: #FEE2E2;
            color: #991B1B;
            border-left: 4px solid #EF4444;
        }
        
        /* Data Display */
        .data-list {
            background: var(--white);
            border-radius: var(--border-radius);
            box-shadow: var(--shadow);
            overflow: hidden;
            margin: 2rem 0;
        }
        
        .data-item {
            padding: 2rem;
            border-bottom: 1px solid #E5E7EB;
            transition: var(--transition);
        }
        
        .data-item:last-child {
            border-bottom: none;
        }
        
        .data-item:hover {
            background: var(--bg-color);
        }
        
        .data-item h4 {
            color: var(--primary-color);
            margin-bottom: 1rem;
            font-size: 1.2rem;
        }
        
        .status {
            display: inline-block;
            padding: 0.4rem 1rem;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .status.en_attente { 
            background: #FEF3C7; 
            color: #92400E; 
        }
        .status.confirmee { 
            background: #D1FAE5; 
            color: #065F46; 
        }
        .status.payee { 
            background: #DBEAFE; 
            color: #1E40AF; 
        }
        
        /* Footer */
        .footer {
            background: var(--secondary-color);
            color: var(--white);
            padding: 3rem 0 1rem;
            margin-top: 4rem;
        }
        
        .footer-content {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 2rem;
        }
        
        .footer-section h4 {
            color: var(--accent-color);
            margin-bottom: 1rem;
            font-size: 1.2rem;
        }
        
        .footer-section a {
            color: #D1D5DB;
            text-decoration: none;
            transition: var(--transition);
            display: block;
            margin-bottom: 0.5rem;
        }
        
        .footer-section a:hover {
            color: var(--white);
        }
        
        .footer-bottom {
            text-align: center;
            padding-top: 2rem;
            margin-top: 2rem;
            border-top: 1px solid #4B5563;
            color: #9CA3AF;
        }
        
        /* Responsive */
        @media (max-width: 768px) {
            .navbar-content {
                padding: 1rem;
                flex-wrap: wrap;
            }
            
            .nav-links {
                display: none;
                width: 100%;
                flex-direction: column;
                gap: 0;
                margin-top: 1rem;
            }
            
            .nav-links.show {
                display: flex;
            }
            
            .mobile-menu-btn {
                display: block;
            }
            
            .hero {
                padding: 4rem 1rem;
            }
            
            .hero-cta {
                flex-direction: column;
                align-items: center;
            }
            
            .container {
                padding: 0 1rem;
            }
            
            .services-grid {
                grid-template-columns: 1fr;
                gap: 1.5rem;
            }
            
            .service-card {
                padding: 2rem 1.5rem;
            }
            
            .form-container {
                padding: 2rem 1.5rem;
                margin: 1rem;
            }
            
            .contact-grid {
                grid-template-columns: 1fr;
            }
            
            .info-grid {
                grid-template-columns: 1fr;
                gap: 2rem;
            }
        }
        
        @media (max-width: 480px) {
            .logo {
                font-size: 1.5rem;
            }
            
            .hero h1 {
                font-size: 2rem;
            }
            
            .hero .subtitle {
                font-size: 1rem;
            }
            
            .btn {
                padding: 0.8rem 1.5rem;
                font-size: 1rem;
            }
        }
        
        /* Loading Animation */
        .loading {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid rgba(255,255,255,.3);
            border-radius: 50%;
            border-top-color: var(--white);
            animation: spin 1s ease-in-out infinite;
        }
        
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <nav class="navbar">
        <div class="navbar-content">
            <div class="logo">
                <i class="fas fa-cog"></i>
                MY JANTES
            </div>
            <ul class="nav-links" id="nav-links">
                <li><a href="#accueil" onclick="showPage('accueil')" class="active">Accueil</a></li>
                <li><a href="#devis" onclick="showPage('devis')">Devis</a></li>
                <li><a href="#reservation" onclick="showPage('reservation')">Réservation</a></li>
                <li><a href="#facturation" onclick="showPage('facturation')">Facturation</a></li>
                <li><a href="#admin" onclick="showPage('admin')">Admin</a></li>
                <li><a href="#contact" onclick="showPage('contact')">Contact</a></li>
            </ul>
            <button class="mobile-menu-btn" onclick="toggleMobileMenu()">
                <i class="fas fa-bars"></i>
            </button>
        </div>
    </nav>

    <!-- Page Accueil -->
    <div id="accueil" class="page active">
        <!-- Hero Section -->
        <section class="hero">
            <div class="hero-content">
                <h1>LES EXPERTS DE LA JANTE ALU</h1>
                <p class="subtitle">
                    Rénovation de jantes chez MY JANTES : <strong>Qualité exceptionnelle, garantie totale</strong>. 
                    Choisissez l'excellence pour vos jantes en aluminium !
                </p>
                <div class="hero-cta">
                    <a href="#devis" onclick="showPage('devis')" class="btn">
                        <i class="fas fa-calculator"></i>
                        Demander un Devis
                    </a>
                    <a href="tel:0321408053" class="btn btn-secondary">
                        <i class="fas fa-phone"></i>
                        03.21.40.80.53
                    </a>
                </div>
            </div>
        </section>

        <div class="container">
            <!-- Services Section -->
            <section class="services-grid">
                <div class="service-card">
                    <div class="icon"><i class="fas fa-sync-alt"></i></div>
                    <h3>Rénovation</h3>
                    <p>Spécialisation exclusive dans les jantes en aluminium. Retrouvez l'aspect d'origine de vos jantes avec notre processus de rénovation complet et nos techniques professionnelles.</p>
                </div>
                <div class="service-card">
                    <div class="icon"><i class="fas fa-palette"></i></div>
                    <h3>Personnalisation</h3>
                    <p>Donnez une nouvelle identité à vos jantes avec nos services de personnalisation. Couleurs, finitions et designs uniques pour un style qui vous ressemble.</p>
                </div>
                <div class="service-card">
                    <div class="icon"><i class="fas fa-tools"></i></div>
                    <h3>Dévoilage</h3>
                    <p>Correction des déformations de vos jantes aluminium. Nos experts utilisent des techniques professionnelles pour redonner la forme parfaite à vos jantes.</p>
                </div>
                <div class="service-card">
                    <div class="icon"><i class="fas fa-spray-can"></i></div>
                    <h3>Décapage</h3>
                    <p>Préparation complète de vos jantes avant rénovation. Décapage professionnel pour éliminer tous les défauts et préparer une finition parfaite.</p>
                </div>
            </section>

            <!-- Pourquoi nous choisir -->
            <section class="info-section">
                <div class="container">
                    <h2 style="text-align: center; color: var(--primary-color); margin-bottom: 3rem; font-size: 2.5rem;">
                        Pourquoi nous choisir ?
                    </h2>
                    <div class="info-grid">
                        <div class="info-item">
                            <h4><i class="fas fa-award icon"></i> Expert dans le domaine</h4>
                            <p>Experts en rénovation de jantes en aluminium, nous garantissons des résultats exceptionnels pour sublimer votre véhicule. Faites confiance à notre savoir-faire.</p>
                        </div>
                        <div class="info-item">
                            <h4><i class="fas fa-history icon"></i> Des années d'expertise</h4>
                            <p>Tous nos employés peuvent justifier d'une expérience de plus de 5 ans dans l'entretien de jantes alliage.</p>
                        </div>
                        <div class="info-item">
                            <h4><i class="fas fa-clock icon"></i> Disponibilité</h4>
                            <p>Nous sommes disponibles du lundi au samedi pour vous apporter la solution la plus adaptée à vos besoins.</p>
                        </div>
                        <div class="info-item">
                            <h4><i class="fas fa-shield-alt icon"></i> Garanties</h4>
                            <p>Rénovation de jantes chez MY JANTES : Qualité exceptionnelle, garantie totale. Choisissez l'excellence pour vos jantes en aluminium.</p>
                        </div>
                    </div>
                </div>
            </section>

            <!-- Contact Info -->
            <section class="contact-info">
                <h3>Informations de Contact</h3>
                <div class="contact-grid">
                    <div class="contact-item">
                        <div class="icon"><i class="fas fa-map-marker-alt"></i></div>
                        <h4>Adresse</h4>
                        <p>
                            <a href="https://maps.app.goo.gl/u7ZRefbJoqxisW8G8" target="_blank">
                                46 rue de la Convention<br>
                                62800 Liévin
                            </a>
                        </p>
                    </div>
                    <div class="contact-item">
                        <div class="icon"><i class="fas fa-phone"></i></div>
                        <h4>Téléphone</h4>
                        <p><a href="tel:0321408053">03.21.40.80.53</a></p>
                        <p style="font-size: 0.9em; margin-top: 0.5rem;">Avec ou sans rendez-vous</p>
                    </div>
                    <div class="contact-item">
                        <div class="icon"><i class="fas fa-clock"></i></div>
                        <h4>Horaires d'ouverture</h4>
                        <p>
                            Lundi - Vendredi : 9h–12h / 13.30h-18h<br>
                            Samedi : 9h - 13h
                        </p>
                    </div>
                    <div class="contact-item">
                        <div class="icon"><i class="fas fa-building"></i></div>
                        <h4>SIRET</h4>
                        <p>91367819900021</p>
                    </div>
                </div>
            </section>
        </div>

        <!-- Footer -->
        <footer class="footer">
            <div class="container">
                <div class="footer-content">
                    <div class="footer-section">
                        <h4>MY JANTES</h4>
                        <p>Les experts de la rénovation de jantes en aluminium à Liévin depuis plus de 5 ans.</p>
                        <p><strong>SIRET:</strong> 91367819900021</p>
                    </div>
                    <div class="footer-section">
                        <h4>Services</h4>
                        <a href="#devis" onclick="showPage('devis')">Demander un devis</a>
                        <a href="#reservation" onclick="showPage('reservation')">Prendre rendez-vous</a>
                        <a href="#contact" onclick="showPage('contact')">Nous contacter</a>
                    </div>
                    <div class="footer-section">
                        <h4>Informations légales</h4>
                        <a href="#mentions" onclick="showPage('mentions')">Mentions légales</a>
                        <a href="#cgv" onclick="showPage('cgv')">CGV</a>
                        <a href="#confidentialite" onclick="showPage('confidentialite')">Politique de confidentialité</a>
                        <a href="#garantie" onclick="showPage('garantie')">Garantie</a>
                    </div>
                    <div class="footer-section">
                        <h4>Contact</h4>
                        <p><i class="fas fa-map-marker-alt"></i> 46 rue de la Convention, 62800 Liévin</p>
                        <p><i class="fas fa-phone"></i> <a href="tel:0321408053">03.21.40.80.53</a></p>
                        <p><i class="fas fa-clock"></i> Lun-Ven: 9h-12h / 13h30-18h<br>Sam: 9h-13h</p>
                    </div>
                </div>
                <div class="footer-bottom">
                    <p>&copy; 2025 MY JANTES. Tous droits réservés. | Rénovation de jantes aluminium à Liévin</p>
                </div>
            </div>
        </footer>
    </div>

    <!-- Pages intérieures -->
    <div class="container">
        <!-- Page Devis -->
        <div id="devis" class="page">
            <h2>Créer un Devis</h2>
            <div class="form-container">
                <div id="devis-success" class="success-message"></div>
                <div id="devis-error" class="error-message"></div>
                
                <form id="devis-form" onsubmit="createDevis(event)">
                    <div class="form-group">
                        <label for="devis-client-name">Nom du client</label>
                        <input type="text" id="devis-client-name" name="client_name" required>
                    </div>
                    <div class="form-group">
                        <label for="devis-client-email">Email</label>
                        <input type="email" id="devis-client-email" name="client_email" required>
                    </div>
                    <div class="form-group">
                        <label for="devis-client-phone">Téléphone</label>
                        <input type="tel" id="devis-client-phone" name="client_phone">
                    </div>
                    <div class="form-group">
                        <label for="devis-service">Type de service</label>
                        <select id="devis-service" name="service_type" required>
                            <option value="">Sélectionner un service</option>
                            <option value="renovation_complete">Rénovation complète - 150€</option>
                            <option value="polissage">Polissage professionnel - 80€</option>
                            <option value="personnalisation">Personnalisation - 200€</option>
                            <option value="reparation">Réparation - 120€</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="devis-description">Description</label>
                        <textarea id="devis-description" name="description" rows="4" placeholder="Détails du travail à effectuer..."></textarea>
                    </div>
                    <button type="submit" class="btn">Créer le Devis</button>
                </form>
            </div>
        </div>

        <!-- Page Réservation -->
        <div id="reservation" class="page">
            <h2>Prendre Rendez-vous</h2>
            <div class="form-container">
                <div id="reservation-success" class="success-message"></div>
                <div id="reservation-error" class="error-message"></div>
                
                <form id="reservation-form" onsubmit="createReservation(event)">
                    <div class="form-group">
                        <label for="res-client-name">Nom du client</label>
                        <input type="text" id="res-client-name" name="client_name" required>
                    </div>
                    <div class="form-group">
                        <label for="res-client-email">Email</label>
                        <input type="email" id="res-client-email" name="client_email" required>
                    </div>
                    <div class="form-group">
                        <label for="res-client-phone">Téléphone</label>
                        <input type="tel" id="res-client-phone" name="client_phone">
                    </div>
                    <div class="form-group">
                        <label for="res-service">Type de service</label>
                        <select id="res-service" name="service_type" required>
                            <option value="">Sélectionner un service</option>
                            <option value="renovation_complete">Rénovation complète</option>
                            <option value="polissage">Polissage professionnel</option>
                            <option value="personnalisation">Personnalisation</option>
                            <option value="reparation">Réparation</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="res-date">Date du rendez-vous</label>
                        <input type="date" id="res-date" name="date_rdv" required>
                    </div>
                    <div class="form-group">
                        <label for="res-heure">Heure du rendez-vous</label>
                        <select id="res-heure" name="heure_rdv" required>
                            <option value="">Sélectionner une heure</option>
                            <option value="09:00">09:00</option>
                            <option value="10:00">10:00</option>
                            <option value="11:00">11:00</option>
                            <option value="14:00">14:00</option>
                            <option value="15:00">15:00</option>
                            <option value="16:00">16:00</option>
                            <option value="17:00">17:00</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="res-description">Description</label>
                        <textarea id="res-description" name="description" rows="3" placeholder="Détails sur vos jantes..."></textarea>
                    </div>
                    <button type="submit" class="btn">Confirmer la Réservation</button>
                </form>
            </div>
        </div>

        <!-- Page Facturation -->
        <div id="facturation" class="page">
            <h2>Générer une Facture</h2>
            <div class="form-container">
                <div id="facture-success" class="success-message"></div>
                <div id="facture-error" class="error-message"></div>
                
                <form id="facture-form" onsubmit="createFacture(event)">
                    <div class="form-group">
                        <label for="fact-client-name">Nom du client</label>
                        <input type="text" id="fact-client-name" name="client_name" required>
                    </div>
                    <div class="form-group">
                        <label for="fact-client-email">Email</label>
                        <input type="email" id="fact-client-email" name="client_email" required>
                    </div>
                    <div class="form-group">
                        <label for="fact-service">Type de service</label>
                        <select id="fact-service" name="service_type" required onchange="updateMontant()">
                            <option value="">Sélectionner un service</option>
                            <option value="renovation_complete">Rénovation complète - 150€</option>
                            <option value="polissage">Polissage professionnel - 80€</option>
                            <option value="personnalisation">Personnalisation - 200€</option>
                            <option value="reparation">Réparation - 120€</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="fact-montant">Montant (€)</label>
                        <input type="number" id="fact-montant" name="montant" step="0.01" required>
                    </div>
                    <div class="form-group">
                        <label for="fact-devis-id">ID Devis (optionnel)</label>
                        <input type="text" id="fact-devis-id" name="devis_id" placeholder="ex: abc123">
                    </div>
                    <button type="submit" class="btn">Générer la Facture</button>
                </form>
            </div>
        </div>

        <!-- Page Admin -->
        <div id="admin" class="page">
            <h2>Tableau de Bord Admin</h2>
            
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 2rem; margin-bottom: 2rem;">
                <div class="form-container">
                    <h3>Derniers Devis</h3>
                    <div id="devis-list" class="data-list"></div>
                </div>
                <div class="form-container">
                    <h3>Dernières Réservations</h3>
                    <div id="reservations-list" class="data-list"></div>
                </div>
                <div class="form-container">
                    <h3>Dernières Factures</h3>
                    <div id="factures-list" class="data-list"></div>
                </div>
            </div>
            
            <button onclick="loadAdminData()" class="btn">Actualiser les Données</button>
        </div>

        <!-- Page Contact -->
        <div id="contact" class="page">
            <h2><i class="fas fa-envelope"></i> Nous Contacter</h2>
            <div class="contact-info" style="margin: 2rem 0;">
                <h3>Informations de Contact</h3>
                <div class="contact-grid">
                    <div class="contact-item">
                        <div class="icon"><i class="fas fa-map-marker-alt"></i></div>
                        <h4>Adresse</h4>
                        <p><a href="https://maps.app.goo.gl/u7ZRefbJoqxisW8G8" target="_blank">
                            46 rue de la Convention<br>62800 Liévin
                        </a></p>
                    </div>
                    <div class="contact-item">
                        <div class="icon"><i class="fas fa-phone"></i></div>
                        <h4>Téléphone</h4>
                        <p><a href="tel:0321408053">03.21.40.80.53</a></p>
                        <p style="font-size: 0.9em;">Avec ou sans rendez-vous</p>
                    </div>
                    <div class="contact-item">
                        <div class="icon"><i class="fas fa-clock"></i></div>
                        <h4>Horaires d'ouverture</h4>
                        <p>Lundi - Vendredi : 9h–12h / 13.30h-18h<br>Samedi : 9h - 13h</p>
                    </div>
                    <div class="contact-item">
                        <div class="icon"><i class="fas fa-building"></i></div>
                        <h4>SIRET</h4>
                        <p>91367819900021</p>
                    </div>
                </div>
            </div>
        </div>

        <!-- Page Mentions Légales -->
        <div id="mentions" class="page">
            <div class="form-container" style="max-width: 800px;">
                <h2><i class="fas fa-balance-scale"></i> Mentions Légales</h2>
                
                <h3>Éditeur du site</h3>
                <p><strong>MY JANTES</strong><br>
                46 rue de la Convention<br>
                62800 Liévin<br>
                SIRET : 91367819900021<br>
                Téléphone : <a href="tel:0321408053">03.21.40.80.53</a></p>

                <h3>Directeur de publication</h3>
                <p>Le directeur de la publication est le gérant de MY JANTES.</p>

                <h3>Hébergement</h3>
                <p>Ce site est hébergé par Replit, Inc.</p>

                <h3>Propriété intellectuelle</h3>
                <p>L'ensemble des contenus présents sur ce site (textes, images, logos, etc.) sont la propriété exclusive de MY JANTES, sauf mention contraire.</p>

                <h3>Données personnelles</h3>
                <p>Conformément au RGPD, vous disposez d'un droit d'accès, de rectification et de suppression de vos données personnelles. Pour exercer ces droits, contactez-nous au 03.21.40.80.53.</p>
            </div>
        </div>

        <!-- Page CGV -->
        <div id="cgv" class="page">
            <div class="form-container" style="max-width: 800px;">
                <h2><i class="fas fa-file-contract"></i> Conditions Générales de Vente</h2>
                
                <h3>Article 1 - Objet</h3>
                <p>Les présentes conditions générales de vente s'appliquent à tous les services de rénovation de jantes proposés par MY JANTES.</p>

                <h3>Article 2 - Prestations</h3>
                <p>MY JANTES propose les services suivants :</p>
                <ul>
                    <li>Rénovation complète de jantes aluminium : 150€</li>
                    <li>Polissage professionnel : 80€</li>
                    <li>Personnalisation : 200€</li>
                    <li>Réparation : 120€</li>
                    <li>Dévoilage selon devis</li>
                    <li>Décapage selon devis</li>
                </ul>

                <h3>Article 3 - Garantie</h3>
                <p>MY JANTES garantit ses prestations selon les termes définis dans nos conditions de garantie. Nous nous engageons sur la qualité exceptionnelle de nos interventions.</p>

                <h3>Article 4 - Modalités de paiement</h3>
                <p>Le paiement s'effectue à la livraison des jantes rénovées. Moyens acceptés : espèces, chèque, carte bancaire.</p>

                <h3>Article 5 - Délais</h3>
                <p>Les délais de réalisation sont communiqués lors de la prise de rendez-vous et peuvent varier selon la charge de travail.</p>

                <h3>Article 6 - Responsabilité</h3>
                <p>MY JANTES s'engage à apporter le plus grand soin dans l'exécution de ses prestations. Notre responsabilité est limitée au montant de la prestation.</p>
            </div>
        </div>

        <!-- Page Politique de Confidentialité -->
        <div id="confidentialite" class="page">
            <div class="form-container" style="max-width: 800px;">
                <h2><i class="fas fa-shield-alt"></i> Politique de Confidentialité</h2>
                
                <h3>Collecte des données</h3>
                <p>MY JANTES collecte uniquement les données nécessaires à la réalisation de ses prestations : nom, prénom, coordonnées, détails de la demande.</p>

                <h3>Utilisation des données</h3>
                <p>Vos données sont utilisées exclusivement pour :</p>
                <ul>
                    <li>La gestion de votre dossier client</li>
                    <li>L'établissement de devis et factures</li>
                    <li>La prise de rendez-vous</li>
                    <li>Le suivi de la prestation</li>
                </ul>

                <h3>Protection des données</h3>
                <p>Nous mettons en œuvre toutes les mesures techniques et organisationnelles pour protéger vos données personnelles contre tout accès non autorisé.</p>

                <h3>Vos droits</h3>
                <p>Conformément au RGPD, vous disposez des droits suivants :</p>
                <ul>
                    <li>Droit d'accès à vos données</li>
                    <li>Droit de rectification</li>
                    <li>Droit d'effacement</li>
                    <li>Droit à la portabilité</li>
                </ul>
                <p>Pour exercer ces droits : <a href="tel:0321408053">03.21.40.80.53</a></p>

                <h3>Conservation des données</h3>
                <p>Vos données sont conservées pendant la durée nécessaire à la réalisation de la prestation et conformément aux obligations légales.</p>
            </div>
        </div>

        <!-- Page Garantie -->
        <div id="garantie" class="page">
            <div class="form-container" style="max-width: 800px;">
                <h2><i class="fas fa-certificate"></i> Nos Garanties</h2>
                
                <h3>Garantie Qualité Exceptionnelle</h3>
                <p>MY JANTES s'engage sur une <strong>qualité exceptionnelle</strong> pour toutes ses prestations de rénovation de jantes aluminium.</p>

                <h3>Garantie Totale</h3>
                <p>Nous offrons une <strong>garantie totale</strong> sur nos interventions :</p>
                <ul>
                    <li>Garantie de satisfaction ou reprise des travaux</li>
                    <li>Garantie sur les matériaux utilisés</li>
                    <li>Garantie sur la tenue de la finition</li>
                </ul>

                <h3>Durée de garantie</h3>
                <p>Selon le type de prestation :</p>
                <ul>
                    <li><strong>Rénovation complète :</strong> 12 mois sur la finition</li>
                    <li><strong>Polissage :</strong> 6 mois sur l'éclat</li>
                    <li><strong>Personnalisation :</strong> 12 mois sur la couleur et finition</li>
                    <li><strong>Réparation :</strong> 12 mois sur la zone réparée</li>
                </ul>

                <h3>Conditions de garantie</h3>
                <p>La garantie s'applique sous réserve :</p>
                <ul>
                    <li>D'un usage normal des jantes</li>
                    <li>De l'absence de chocs ultérieurs</li>
                    <li>Du respect des conseils d'entretien</li>
                </ul>

                <h3>Mise en jeu de la garantie</h3>
                <p>En cas de problème couvert par la garantie, contactez-nous au <a href="tel:0321408053">03.21.40.80.53</a>. Nous interviendrons rapidement pour corriger le défaut constaté.</p>

                <h3>Expertise professionnelle</h3>
                <p>Avec plus de 5 ans d'expérience par employé, MY JANTES garantit un savoir-faire professionnel reconnu dans la rénovation de jantes aluminium.</p>
            </div>
        </div>
    </div>

    <script>
        function showPage(pageId) {
            // Hide all pages
            document.querySelectorAll('.page').forEach(page => {
                page.classList.remove('active');
            });
            
            // Show selected page
            document.getElementById(pageId).classList.add('active');
            
            // Update navigation
            document.querySelectorAll('.nav-links a').forEach(link => {
                link.classList.remove('active');
            });
            document.querySelector(`[href="#${pageId}"]`).classList.add('active');
            
            // Load admin data when accessing admin page
            if (pageId === 'admin') {
                loadAdminData();
            }
            
            // Close mobile menu after navigation
            const navLinks = document.getElementById('nav-links');
            if (navLinks.classList.contains('show')) {
                navLinks.classList.remove('show');
            }
        }

        function toggleMobileMenu() {
            const navLinks = document.getElementById('nav-links');
            navLinks.classList.toggle('show');
        }

        async function createDevis(event) {
            event.preventDefault();
            const form = event.target;
            const formData = new FormData(form);
            const data = Object.fromEntries(formData);
            
            try {
                const response = await fetch('/api/devis', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });
                
                const result = await response.json();
                
                if (result.success) {
                    document.getElementById('devis-success').textContent = result.message;
                    document.getElementById('devis-success').style.display = 'block';
                    document.getElementById('devis-error').style.display = 'none';
                    form.reset();
                } else {
                    throw new Error(result.error);
                }
            } catch (error) {
                document.getElementById('devis-error').textContent = 'Erreur: ' + error.message;
                document.getElementById('devis-error').style.display = 'block';
                document.getElementById('devis-success').style.display = 'none';
            }
        }

        async function createReservation(event) {
            event.preventDefault();
            const form = event.target;
            const formData = new FormData(form);
            const data = Object.fromEntries(formData);
            
            try {
                const response = await fetch('/api/reservations', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });
                
                const result = await response.json();
                
                if (result.success) {
                    document.getElementById('reservation-success').textContent = result.message;
                    document.getElementById('reservation-success').style.display = 'block';
                    document.getElementById('reservation-error').style.display = 'none';
                    form.reset();
                } else {
                    throw new Error(result.error);
                }
            } catch (error) {
                document.getElementById('reservation-error').textContent = 'Erreur: ' + error.message;
                document.getElementById('reservation-error').style.display = 'block';
                document.getElementById('reservation-success').style.display = 'none';
            }
        }

        async function createFacture(event) {
            event.preventDefault();
            const form = event.target;
            const formData = new FormData(form);
            const data = Object.fromEntries(formData);
            
            try {
                const response = await fetch('/api/factures', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });
                
                const result = await response.json();
                
                if (result.success) {
                    document.getElementById('facture-success').textContent = result.message;
                    document.getElementById('facture-success').style.display = 'block';
                    document.getElementById('facture-error').style.display = 'none';
                    form.reset();
                } else {
                    throw new Error(result.error);
                }
            } catch (error) {
                document.getElementById('facture-error').textContent = 'Erreur: ' + error.message;
                document.getElementById('facture-error').style.display = 'block';
                document.getElementById('facture-success').style.display = 'none';
            }
        }

        function updateMontant() {
            const service = document.getElementById('fact-service').value;
            const montantInput = document.getElementById('fact-montant');
            const prices = {
                'renovation_complete': 150,
                'polissage': 80,
                'personnalisation': 200,
                'reparation': 120
            };
            if (prices[service]) {
                montantInput.value = prices[service];
            }
        }

        async function loadAdminData() {
            try {
                // Load devis
                const devisResponse = await fetch('/api/devis');
                const devisList = await devisResponse.json();
                displayDevis(devisList);
                
                // Load reservations
                const resResponse = await fetch('/api/reservations');
                const resList = await resResponse.json();
                displayReservations(resList);
                
                // Load factures
                const factResponse = await fetch('/api/factures');
                const factList = await factResponse.json();
                displayFactures(factList);
                
            } catch (error) {
                console.error('Erreur lors du chargement des données:', error);
            }
        }

        function displayDevis(devisList) {
            const container = document.getElementById('devis-list');
            container.innerHTML = '';
            
            devisList.slice(0, 5).forEach(devis => {
                const div = document.createElement('div');
                div.className = 'data-item';
                div.innerHTML = `
                    <h4>Devis #${devis.id}</h4>
                    <p><strong>Client:</strong> ${devis.client_name}</p>
                    <p><strong>Service:</strong> ${devis.service_type}</p>
                    <p><strong>Prix:</strong> ${devis.prix}€</p>
                    <span class="status ${devis.status}">${devis.status}</span>
                `;
                container.appendChild(div);
            });
        }

        function displayReservations(resList) {
            const container = document.getElementById('reservations-list');
            container.innerHTML = '';
            
            resList.slice(0, 5).forEach(res => {
                const div = document.createElement('div');
                div.className = 'data-item';
                div.innerHTML = `
                    <h4>RDV #${res.id}</h4>
                    <p><strong>Client:</strong> ${res.client_name}</p>
                    <p><strong>Date:</strong> ${res.date_rdv} à ${res.heure_rdv}</p>
                    <p><strong>Service:</strong> ${res.service_type}</p>
                    <span class="status ${res.status}">${res.status}</span>
                `;
                container.appendChild(div);
            });
        }

        function displayFactures(factList) {
            const container = document.getElementById('factures-list');
            container.innerHTML = '';
            
            factList.slice(0, 5).forEach(fact => {
                const div = document.createElement('div');
                div.className = 'data-item';
                div.innerHTML = `
                    <h4>Facture #${fact.id}</h4>
                    <p><strong>Client:</strong> ${fact.client_name}</p>
                    <p><strong>Montant:</strong> ${fact.montant}€</p>
                    <p><strong>Date:</strong> ${fact.date_facture}</p>
                    <span class="status ${fact.status}">${fact.status}</span>
                `;
                container.appendChild(div);
            });
        }

        // Set minimum date to today for reservations
        document.addEventListener('DOMContentLoaded', function() {
            const today = new Date().toISOString().split('T')[0];
            document.getElementById('res-date').setAttribute('min', today);
        });
    </script>
</body>
</html>"""
        
        self.wfile.write(html_content.encode('utf-8'))

def main():
    """Main server function"""
    PORT = int(os.environ.get("PORT", 5000))
    
    try:
        socketserver.TCPServer.allow_reuse_address = True
        with socketserver.TCPServer(("0.0.0.0", PORT), MyJantesServer) as httpd:
            print(f"MY JANTES - Serveur démarré sur le port {PORT}")
            httpd.serve_forever()
    except Exception as e:
        print(f"Erreur serveur: {e}")

if __name__ == "__main__":
    main()