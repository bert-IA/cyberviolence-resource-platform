#!/usr/bin/env python3
"""
Serveur HTTP local pour les docs.
Force charset=utf-8 sur tous les fichiers texte pour que Firefox affiche
correctement les caractères accentués.
"""
import http.server
import os

PORT = 5500
DIRECTORY = os.path.dirname(os.path.abspath(__file__))


class UTF8Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def guess_type(self, path):
        result = super().guess_type(path)
        # Python 3.12+ retourne une string, versions antérieures un tuple
        mime = result if isinstance(result, str) else (result[0] if result else None)
        if not mime:
            mime = "text/plain"
        # Force charset=utf-8 sur tous les types texte
        if mime.startswith("text/") and "charset" not in mime:
            mime = f"{mime}; charset=utf-8"
        return mime

    def log_message(self, format, *args):
        print(f"[docs] {self.address_string()} - {format % args}")


if __name__ == "__main__":
    with http.server.HTTPServer(("", PORT), UTF8Handler) as httpd:
        print(f"Docs disponibles sur http://localhost:{PORT}/")
        print(f"  children-flow.html : http://localhost:{PORT}/children-flow.html")
        print(f"  Formation JS/React : http://localhost:{PORT}/FORMATION_ARRAY_METHODS.md")
        print("Ctrl+C pour arrêter.")
        httpd.serve_forever()
