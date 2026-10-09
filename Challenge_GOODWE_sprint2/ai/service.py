import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from models import analyze, forecast, MODEL_VERSION


class Handler(BaseHTTPRequestHandler):
    def send_json(self, status, value):
        payload = json.dumps(value, ensure_ascii=False, allow_nan=False).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def do_GET(self):
        if self.path == '/health':
            self.send_json(200, {'status': 'ok', 'version': MODEL_VERSION})
        else:
            self.send_json(404, {'error': 'Endpoint não encontrado.'})

    def do_POST(self):
        try:
            length = int(self.headers.get('Content-Length', 0))
            if length <= 0 or length > 10_000_000:
                self.send_json(413, {'error': 'Payload vazio ou muito grande.'})
                return
            data = json.loads(self.rfile.read(length))
            if self.path == '/analyze':
                result = analyze(data['history'], data['candidates'])
            elif self.path == '/forecast':
                result = forecast(data['history'], data['date'], data.get('capacity_kw', 14.4))
            else:
                self.send_json(404, {'error': 'Endpoint não encontrado.'})
                return
            self.send_json(200, result)
        except (ValueError, KeyError, TypeError, ZeroDivisionError) as error:
            self.send_json(422, {'error': str(error)})

    def log_message(self, *_):
        pass


if __name__ == '__main__':
    host, port = os.environ.get('AI_HOST', '127.0.0.1'), int(os.environ.get('AI_PORT', '8001'))
    print(f'IA disponível em http://{host}:{port}', flush=True)
    ThreadingHTTPServer((host, port), Handler).serve_forever()
