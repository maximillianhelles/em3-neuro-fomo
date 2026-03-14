from http.server import HTTPServer, SimpleHTTPRequestHandler
import json
import os
 
PORT = 8000
DATA_FILE = os.path.join(os.path.dirname(__file__), "values.json")
 
 
class CORSHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        super().end_headers()
 
    def do_GET(self):
        if self.path == "/values":
            with open(DATA_FILE, "r") as f:
                data = json.load(f)
            body = json.dumps(data).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", len(body))
            self.end_headers()
            self.wfile.write(body)
        else:
            self.send_response(404)
            self.end_headers()
 
    def log_message(self, format, *args):
        print(f"[server] {self.address_string()} - {format % args}")
 
 
if __name__ == "__main__":
    print(f"[server] Serving on http://localhost:{PORT}")
    print(f"[server] Data endpoint: http://localhost:{PORT}/values")
    HTTPServer(("", PORT), CORSHandler).serve_forever()