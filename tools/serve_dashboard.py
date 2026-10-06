#!/usr/bin/env python3
"""
Dashboard Server with CORS & Live Data Support (tools/serve_dashboard.py)
Serves the Genesis Bounty Hunter autonomous dashboard on http://localhost:8080 / http://localhost:8000
"""

import os
import sys
import http.server
import socketserver

PORT = 8080
DIRECTORY = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "dashboard")

class DashboardHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        super().end_headers()

def run_server(port=PORT):
    socketserver.TCPServer.allow_reuse_address = True
    try:
        with socketserver.TCPServer(("", port), DashboardHandler) as httpd:
            print(f"[+] Genesis Bounty Hunter Dashboard running at http://localhost:{port}/")
            print(f"[+] Serving directory: {DIRECTORY}")
            httpd.serve_forever()
    except OSError as e:
        print(f"[-] Port {port} busy ({e}), trying {port + 1}...")
        with socketserver.TCPServer(("", port + 1), DashboardHandler) as httpd:
            print(f"[+] Genesis Bounty Hunter Dashboard running at http://localhost:{port + 1}/")
            httpd.serve_forever()

if __name__ == '__main__':
    p = int(sys.argv[1]) if len(sys.argv) > 1 else PORT
    run_server(p)
