import http.server
import socketserver
import webbrowser
from pathlib import Path

PORT = 8000
EVAL_DIR = Path(__file__).resolve().parent

class DashboardHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(EVAL_DIR), **kwargs)

    def do_GET(self):
        if self.path in ("/", ""):
            self.path = "/dashboard.html"
        return super().do_GET()

if __name__ == "__main__":
    print(f"\n=======================================================")
    print(f" Week 6 Eval Dashboard Server")
    print(f" URL: http://localhost:{PORT}")
    print(f" Press Ctrl+C to stop the server")
    print(f"=======================================================\n")
    
    # Automatically open browser
    try:
        webbrowser.open(f"http://localhost:{PORT}")
    except Exception:
        pass

    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), DashboardHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")
