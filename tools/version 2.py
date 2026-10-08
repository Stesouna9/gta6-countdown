"""Cache-busting : ajoute ?v=<empreinte> aux assets CSS/JS des pages générées (le CSS est caché 30 min par les navigateurs)."""
import hashlib, re
from pathlib import Path
RACINE = Path(__file__).resolve().parent.parent
_F = ["assets/style.css", "assets/site.js", "assets/i18n.js", "assets/radio.js"]
V = hashlib.md5(b"".join((RACINE / f).read_bytes() for f in _F if (RACINE / f).exists())).hexdigest()[:8]
_RX = re.compile(r'((?:\.\./)*assets/(?:style\.css|site\.js|i18n\.js|radio\.js|lang/[a-z]+\.js))(?:\?v=[0-9a-f]+)?"')
def ver(html):
    return _RX.sub(lambda m: m.group(1) + "?v=" + V + '"', html)
