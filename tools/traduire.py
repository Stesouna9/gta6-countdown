# Traduction automatique des articles : la routine écrit fr + en, ce script complète les 15 autres langues.
# Tourne dans GitHub Actions (traduire.yml). Traduit depuis en, nœud texte par nœud texte, balises et liens intacts.
import json, re, sys, time, html
from deep_translator import GoogleTranslator
L17 = ["fr","en","es","pt","de","it","ja","zh","tw","ar","hi","ru","ko","tr","idn","pl","vi"]
G = {"zh":"zh-CN","tw":"zh-TW","idn":"id"}
MAX = int(sys.argv[1]) if len(sys.argv) > 1 else 4
def trad(txt, l):
    txt = txt.strip()
    if not txt: return txt
    err = None
    for i in range(3):
        try: return GoogleTranslator(source="en", target=G.get(l, l)).translate(txt) or txt
        except Exception as e:
            err = e; time.sleep(2 + i * 3)
    print("échec", l, err); return txt
def trad_html(h, l):
    out = []
    for part in re.split(r"(<[^>]+>)", h):
        if not part or part.startswith("<") or not re.search(r"\w", part): out.append(part); continue
        out.append(html.escape(trad(html.unescape(part), l), quote=False))
    return "".join(out)
arts = json.load(open("data/articles.json", encoding="utf-8"))
faits = []
for a in arts:
    src = a.get("en") if isinstance(a.get("en"), dict) and a["en"].get("t") else None
    if not src: continue
    manq = [l for l in L17 if l not in ("fr", "en") and (not isinstance(a.get(l), dict) or not a[l].get("t"))]
    if not manq: continue
    for l in manq:
        a[l] = {"t": trad(src["t"], l), "d": trad(src.get("d", ""), l), "h": trad_html(src.get("h", ""), l)}
        time.sleep(0.4)
    faits.append(a["id"] + " (" + ",".join(manq) + ")")
    if len(faits) >= MAX: break
if not faits: print("rien à traduire"); sys.exit(0)
json.dump(arts, open("data/articles.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("traduit :", "; ".join(faits))
