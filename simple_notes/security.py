import mimetypes
import secrets
from flask import request, g

mimetypes.add_type('application/javascript', '.js')
mimetypes.add_type('text/css', '.css')

# CSP nonce setter

def set_csp_nonce():
    g.csp_nonce = secrets.token_urlsafe(16)

# Security headers

def set_security_headers(response):
    nonce = getattr(g, 'csp_nonce', None)
    csp = [
        "default-src 'self'",
        f"script-src 'self' https://cdn.jsdelivr.net" + (f" 'nonce-{nonce}'" if nonce else ""),
        "style-src 'self' https://cdn.jsdelivr.net",
        "font-src 'self' https://cdn.jsdelivr.net",
        "img-src 'self' data:"
    ]
    response.headers['Content-Security-Policy'] = '; '.join(csp)
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['Referrer-Policy'] = 'no-referrer-when-downgrade'

    try:
        p = request.path
        if p.startswith('/static/'):
            if p.endswith('.js'):
                response.headers['Content-Type'] = 'application/javascript; charset=utf-8'
            elif p.endswith('.css'):
                response.headers['Content-Type'] = 'text/css; charset=utf-8'
    except Exception:
        pass
    return response