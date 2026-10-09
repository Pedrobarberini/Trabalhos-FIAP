import os
from http.server import ThreadingHTTPServer

from http_server import Handler


def main():
    host = os.environ.get('AI_HOST', '127.0.0.1')
    port = int(os.environ.get('AI_PORT', '8001'))
    print(f'IA disponível em http://{host}:{port}', flush=True)
    ThreadingHTTPServer((host, port), Handler).serve_forever()


if __name__ == '__main__':
    main()
