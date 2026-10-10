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
