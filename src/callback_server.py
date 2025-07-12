from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib import parse
import threading

HOST = "localhost"
PORT = 8000

class CallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = parse.urlparse(self.path)
        if parsed.path != "/callback":
            self.send_response(404)
            self.end_headers()
            return

        qs = parse.parse_qs(parsed.query)
        code = qs.get("code", [None])[0]
        state = qs.get("state", [None])[0]

        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"<html><body><h1>Autorizado!</h1>"
                         b"<p>Volte ao terminal.</p></body></html>")

        print(f"\n🔑 Código recebido: {code}\n🔒 State recebido: {state}\n")

        threading.Thread(target=self.server.shutdown).start()

def run():
    httpd = HTTPServer((HOST, PORT), CallbackHandler)
    print(f"▶️  Servidor de callback rodando em http://{HOST}:{PORT}/callback")
    httpd.serve_forever()
    print("⏹️  Servidor finalizado.")

if __name__ == "__main__":
    run()
