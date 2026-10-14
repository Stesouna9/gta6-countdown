# Textes fixes du site (menus, pages) : toute clé de tools/i18n/en.json absente d'une des 15 autres langues est traduite
# automatiquement (14/10/2026 : plus de texte anglais qui traîne dans les pages japonaises, arabes...).
import json, sys
sys.path.insert(0, "tools")
from traduire import gtx, proteger, nettoyer
import html
L = {"es":"es","pt":"pt","de":"de","it":"it","ja":"ja","zh":"zh","tw":"tw","ar":"ar","hi":"hi","ru":"ru","ko":"ko","tr":"tr","id":"idn","pl":"pl","vi":"vi"}
en = json.load(open("tools/i18n/en.json", encoding="utf-8"))
faits = []
for f, code in L.items():
    p = f"tools/i18n/{f}.json"
    d = json.load(open(p, encoding="utf-8"))
    manq = [k for k, v in en.items() if isinstance(v, str) and v.strip() and k not in d and not k.startswith("_")]
    if not manq: continue
    for i in range(0, len(manq), 60):
        ks = manq[i:i + 60]
        try: res = gtx([proteger(html.escape(en[k], quote=False)) for k in ks], code)
        except Exception as e: print("échec", f, e); break
        for k, r in zip(ks, res): d[k] = html.unescape(nettoyer(r)).strip()
    json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    faits.append(f"{f}:{len(manq)}")
print("i18n traduit :", " ".join(faits) if faits else "rien")
