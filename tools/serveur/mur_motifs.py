# Patch du Mur (Hetzner, /opt/mur/mur.py) : un message en majuscules est remis en minuscules
# au lieu d'être refusé, et chaque refus renvoie son motif en clair. Idempotent.
import shutil, subprocess, sys
p = "/opt/mur/mur.py"; s = open(p, encoding="utf-8").read()
old = '        if motif: journal(ip, motif, s, p, m); return self._j(400, {"e": "refusé"})'
new = '''        if motif == "cris": m = m[:1] + m[1:].lower(); motif = refus(p, m)  # majuscules : on baisse le ton
        MOTIFS = {"insulte": "refusé : insulte", "pub": "refusé : publicité ou lien", "bruit": "refusé : trop de symboles", "repetition": "refusé : répétition", "cris": "refusé : tout en majuscules"}
        if motif: journal(ip, motif, s, p, m); return self._j(400, {"e": MOTIFS.get(motif, "refusé : " + motif)})'''
if old not in s: print("déjà patché ou ligne introuvable"); sys.exit(0)
shutil.copy(p, p + ".avant_motifs"); open(p, "w", encoding="utf-8").write(s.replace(old, new, 1))
subprocess.run([sys.executable, "-m", "py_compile", p], check=True)
subprocess.run(["systemctl", "restart", "mur"], check=True); print("mur patché et redémarré")

# 2. Dates : en base, les messages de la rédaction datés dans le futur sont ramenés à maintenant
#    (une minute d'écart entre eux), et redaction_mur.py est patché : import jamais daté dans
#    le futur, dédoublonnage par texte (et non par date).
import sqlite3, time
db = "/var/lib/mur/mur.db"; c = sqlite3.connect(db); now = int(time.time())
ids = [r[0] for r in c.execute("SELECT id FROM messages WHERE t > ? AND ip = '127.0.0.1' ORDER BY t", (now + 300,))]
for k, i in enumerate(ids): c.execute("UPDATE messages SET t=? WHERE id=?", (now - 60 * (len(ids) - k), i))
c.commit(); c.close(); print("messages futurs redatés :", len(ids))
r = "/opt/mur/redaction_mur.py"; s = open(r, encoding="utf-8").read()
o1 = 'if c.execute("SELECT 1 FROM messages WHERE uid=? AND t=? AND m=?", (uid[p], t, m)).fetchone(): continue'
n1 = 'if c.execute("SELECT 1 FROM messages WHERE uid=? AND m=?", (uid[p], m)).fetchone(): continue\n        t = min(t, int(time.time()))  # jamais dans le futur'
if o1 in s:
    s = s.replace(o1, n1, 1)
    if "import time" not in s: s = "import time\n" + s
    shutil.copy(r, r + ".avant_dates"); open(r, "w", encoding="utf-8").write(s)
    subprocess.run([sys.executable, "-m", "py_compile", r], check=True); print("redaction_mur.py patché")
else: print("redaction_mur.py : déjà patché")
