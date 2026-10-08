#!/usr/bin/env python3
"""Le Mur de Vice City : mini forum sans compte (stdlib + sqlite).
Écoute 127.0.0.1:8830 derrière Caddy (handle_path /mur/*).
GET  /api/messages?s=<sujet>   -> 50 derniers messages du sujet
POST /api/messages {s,p,m,l}   -> ajoute ; 1 message / 30 s / IP ; 500 car.
Modération : sqlite3 /var/lib/mur/mur.db  (UPDATE messages SET cache=1 WHERE id=…)
"""
import json, re, sqlite3, time, os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

DB = os.environ.get("MUR_DB", "/var/lib/mur/mur.db")
SUJETS = {"sortie", "pc", "collector", "leonida", "radio", "libre"}
MOTS = re.compile(r"\b(fdp|ntm|nique|pute|salope|enculé|connard|connasse|pd|nigg\w*|fag\w*|cunt|bitch|retard\w*)\b", re.I)
PUB = re.compile(r"https?://|www\.|\.(com|net|fr|io|gg)\b|telegram|whatsapp|crypto|casino|free\s*money", re.I)
DERNIER = {}

def db():
    c = sqlite3.connect(DB); c.execute("""CREATE TABLE IF NOT EXISTS messages(
        id INTEGER PRIMARY KEY, t INTEGER, s TEXT, p TEXT, m TEXT, l TEXT, ip TEXT, cache INTEGER DEFAULT 0)""")
    c.execute("CREATE INDEX IF NOT EXISTS i_s ON messages(s, t)"); return c

class H(BaseHTTPRequestHandler):
    def _j(self, code, obj):
        b = json.dumps(obj, ensure_ascii=False).encode()
        self.send_response(code); self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store"); self.send_header("Content-Length", str(len(b))); self.end_headers(); self.wfile.write(b)
    def ip(self):
        return (self.headers.get("X-Forwarded-For") or self.client_address[0]).split(",")[0].strip()
    def do_GET(self):
        u = urlparse(self.path)
        if u.path != "/api/messages": return self._j(404, {"e": "?"})
        s = parse_qs(u.query).get("s", ["sortie"])[0]
        if s not in SUJETS: return self._j(400, {"e": "sujet"})
        c = db(); rows = c.execute("SELECT t,p,m,l FROM messages WHERE s=? AND cache=0 ORDER BY t DESC LIMIT 50", (s,)).fetchall(); c.close()
        self._j(200, [{"t": r[0], "p": r[1], "m": r[2], "l": r[3]} for r in rows])
    def do_POST(self):
        if urlparse(self.path).path != "/api/messages": return self._j(404, {"e": "?"})
        try:
            d = json.loads(self.rfile.read(min(int(self.headers.get("Content-Length", 0)), 4000)))
        except Exception: return self._j(400, {"e": "json"})
        s, p, m, l = str(d.get("s", "")), str(d.get("p", "")).strip()[:24], str(d.get("m", "")).strip()[:500], str(d.get("l", "fr"))[:2]
        if s not in SUJETS or len(p) < 2 or len(m) < 2: return self._j(400, {"e": "vide"})
        if MOTS.search(p + " " + m) or PUB.search(m): return self._j(400, {"e": "refusé"})
        ip = self.ip(); now = time.time()
        if now - DERNIER.get(ip, 0) < 30: return self._j(429, {"e": "30 s"})
        DERNIER[ip] = now
        c = db(); c.execute("INSERT INTO messages(t,s,p,m,l,ip) VALUES(?,?,?,?,?,?)", (int(now), s, p, m, l, ip)); c.commit(); c.close()
        self._j(200, {"ok": 1})
    def log_message(self, *a): pass

if __name__ == "__main__":
    os.makedirs(os.path.dirname(DB), exist_ok=True); db().close()
    ThreadingHTTPServer(("127.0.0.1", 8830), H).serve_forever()
