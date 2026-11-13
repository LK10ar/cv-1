#!/usr/bin/env python3
"""Petit serveur local pour le site UI PACT (Next.js exporte).
Lance :  python serveur.py   puis ouvre http://localhost:8000
Il sert les fichiers, remplace /_next/image par les images du dossier public/,
et repond aux appels /api/... du site."""
import http.server, socketserver, os, sys, urllib.parse, mimetypes, webbrowser, threading

ROOT = os.path.dirname(os.path.abspath(__file__))
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
mimetypes.add_type('image/svg+xml', '.svg')
mimetypes.add_type('text/javascript', '.js')

class H(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=ROOT, **k)

    def log_message(self, *a):
        pass

    def _send_file(self, path):
        with open(path, 'rb') as f:
            data = f.read()
        ctype = mimetypes.guess_type(path)[0] or 'application/octet-stream'
        self.send_response(200)
        self.send_header('Content-Type', ctype)
        self.send_header('Content-Length', str(len(data)))
        self.end_headers()
        self.wfile.write(data)


    def _resized(self, path, w):
        """Reduit les grosses photos (si Pillow est installe : pip install pillow) et garde un cache."""
        try:
            from PIL import Image
        except ImportError:
            return path
        if not w or not path.lower().endswith(('.jpg', '.jpeg', '.png')):
            return path
        w = min(max(w, 64), 1600)
        cache = os.path.join(ROOT, '_cache')
        os.makedirs(cache, exist_ok=True)
        key = '%s_%d_%d%s' % (os.path.basename(path), os.path.getsize(path), w, os.path.splitext(path)[1].lower())
        out = os.path.join(cache, key)
        if not os.path.isfile(out):
            try:
                im = Image.open(path)
                try:
                    from PIL import ImageOps
                    im = ImageOps.exif_transpose(im)
                except Exception:
                    pass
                if im.width > w:
                    im = im.resize((w, int(im.height * w / im.width)), Image.LANCZOS)
                if out.endswith(('.jpg', '.jpeg')):
                    im.convert('RGB').save(out, quality=82, optimize=True)
                else:
                    im.save(out, optimize=True)
            except Exception:
                return path
        return out

    def do_GET(self):
        u = urllib.parse.urlparse(self.path)
        if u.path == '/_next/image':
            rel = urllib.parse.unquote(urllib.parse.parse_qs(u.query).get('url', [''])[0]).lstrip('/')
            try:
                w = int(urllib.parse.parse_qs(u.query).get('w', ['0'])[0])
            except ValueError:
                w = 0
            for base in ('public', 'images', ''):
                p = os.path.join(ROOT, base, rel)
                if rel and os.path.isfile(p):
                    return self._send_file(self._resized(p, w))
            self.send_response(404); self.end_headers(); return
        if u.path.startswith('/api/'):
            body = b'{}'
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers(); self.wfile.write(body); return
        rel = urllib.parse.unquote(u.path).lstrip('/')
        if rel == '':
            rel = 'index.html'
        # fichiers du dossier public/ servis a la racine (ex. /me-photo.svg)
        for base in ('', 'public', 'images'):
            p = os.path.join(ROOT, base, rel)
            if os.path.isfile(p):
                return self._send_file(p)
        self.send_response(404); self.end_headers()

socketserver.TCPServer.allow_reuse_address = True
with socketserver.ThreadingTCPServer(('', PORT), H) as httpd:
    url = 'http://localhost:%d' % PORT
    print('Site UI PACT sur', url, '(Ctrl+C pour arreter)')
    threading.Timer(0.8, lambda: webbrowser.open(url)).start()
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
