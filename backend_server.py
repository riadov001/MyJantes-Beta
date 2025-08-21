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
    <title>MY JANTES - Application de Gestion</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f8f9fa;
        }
        .navbar {
            background: #DC2626;
            color: white;
            padding: 1rem 0;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            position: sticky;
            top: 0;
            z-index: 100;
        }
        .navbar-content {
            max-width: 1200px;
            margin: 0 auto;
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0 20px;
        }
        .logo { font-size: 1.8em; font-weight: bold; }
        .nav-links {
            display: flex;
            list-style: none;
            gap: 2rem;
        }
        .nav-links a {
            color: white;
            text-decoration: none;
            padding: 0.5rem 1rem;
            border-radius: 5px;
            transition: background 0.3s;
        }
        .nav-links a:hover, .nav-links a.active {
            background: rgba(255,255,255,0.2);
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem 20px;
        }
        .page {
            display: none;
        }
        .page.active {
            display: block;
        }
        .form-group {
            margin-bottom: 1rem;
        }
        .form-group label {
            display: block;
            margin-bottom: 0.5rem;
            font-weight: 500;
            color: #DC2626;
        }
        .form-group input, .form-group select, .form-group textarea {
            width: 100%;
            padding: 0.8rem;
            border: 2px solid #ddd;
            border-radius: 8px;
            font-size: 1rem;
        }
        .form-group input:focus, .form-group select:focus, .form-group textarea:focus {
            outline: none;
            border-color: #DC2626;
        }
        .btn {
            background: #DC2626;
            color: white;
            padding: 0.8rem 1.5rem;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 1rem;
            font-weight: 500;
            transition: background 0.3s;
        }
        .btn:hover {
            background: #B91C1C;
        }
        .form-container {
            background: white;
            padding: 2rem;
            border-radius: 15px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            max-width: 600px;
            margin: 0 auto;
        }
        .success-message {
            background: #10B981;
            color: white;
            padding: 1rem;
            border-radius: 8px;
            margin-bottom: 1rem;
            display: none;
        }
        .error-message {
            background: #EF4444;
            color: white;
            padding: 1rem;
            border-radius: 8px;
            margin-bottom: 1rem;
            display: none;
        }
        .data-list {
            background: white;
            border-radius: 15px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        .data-item {
            padding: 1rem;
            border-bottom: 1px solid #eee;
        }
        .data-item:last-child {
            border-bottom: none;
        }
        .data-item h4 {
            color: #DC2626;
            margin-bottom: 0.5rem;
        }
        .status {
            display: inline-block;
            padding: 0.25rem 0.75rem;
            border-radius: 12px;
            font-size: 0.85rem;
            font-weight: 500;
        }
        .status.en_attente { background: #FEF3C7; color: #92400E; }
        .status.confirmee { background: #D1FAE5; color: #065F46; }
        .status.payee { background: #DBEAFE; color: #1E40AF; }
    </style>
</head>
<body>
    <nav class="navbar">
        <div class="navbar-content">
            <div class="logo">MY JANTES</div>
            <ul class="nav-links">
                <li><a href="#accueil" onclick="showPage('accueil')" class="active">Accueil</a></li>
                <li><a href="#devis" onclick="showPage('devis')">Devis</a></li>
                <li><a href="#reservation" onclick="showPage('reservation')">Réservation</a></li>
                <li><a href="#facturation" onclick="showPage('facturation')">Facturation</a></li>
                <li><a href="#admin" onclick="showPage('admin')">Admin</a></li>
            </ul>
        </div>
    </nav>

    <div class="container">
        <!-- Page Accueil -->
        <div id="accueil" class="page active">
            <h1>Bienvenue sur MY JANTES</h1>
            <p>Application de gestion complète pour votre entreprise de rénovation de jantes.</p>
            <div style="margin-top: 2rem;">
                <h3>Services disponibles :</h3>
                <ul style="margin: 1rem 0; padding-left: 2rem;">
                    <li>Rénovation complète de jantes aluminium</li>
                    <li>Polissage professionnel</li>
                    <li>Personnalisation et customisation</li>
                    <li>Réparation de rayures et impacts</li>
                </ul>
            </div>
        </div>

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