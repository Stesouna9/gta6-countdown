# Traduction automatique des articles : la rédaction écrit fr + en, ce script complète les 15 autres langues.
# Lancé par Solange AVANT chaque commit (un article ne part jamais incomplet) et par GitHub Actions (traduire.yml) en filet.
# 14/10/2026 : une seule requête par article et par langue (t, d, h envoyés ensemble, format html : balises et liens
# intacts), 15 langues en parallèle → quelques secondes par article au lieu de 40 min (ancienne version nœud par nœud).
import json, re, sys, time, html
from concurrent.futures import ThreadPoolExecutor
import requests
L17 = ["fr","en","es","pt","de","it","ja","zh","tw","ar","hi","ru","ko","tr","idn","pl","vi"]
G = {"zh":"zh-CN","tw":"zh-TW","idn":"id"}
MAX = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else 20
UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15"}
NOMS = ["Leonida Keys", "Grassrivers", "Port Gellhorn", "Ambrosia", "Mount Kalaga", "Cal Hampton", "Boobie Ike", "Boobie", "Dre'Quan Priest", "Dre'Quan", "Real Dimez", "Bae-Luxe", "Roxy", "DWNPLY", "Raul Bautista", "Raul", "Brian Heder", "Brian", "Lori", "Only Raw Records", "Jack of Hearts", "Liberty City", "Leonida Penitentiary", "Flash FM", "Cocoteo", "Back Country", "Afro Bank FM", "The Chamber", "Dirty South Classics", "Vice City FM", "V-Rock FM", "Grotti Cheetah", "Shitzu Squalo", "Vapid Dominator", "Vapid Stanier", "Dinka Enduro", "Crest Kayak", "Hawk & Little Morgan", "Stock 305", "Electric Fang", "One-Eyed Willie's", "Goodtime Gear", "Sara's Unisex Salon", "Vintage Vice City Pack", "Tommy Vercetti", "Ocean Beach", "Wyman", "Rob Nelson", "Jason Schreier", "Bloomberg", "Extended Look", "GTA+", "Rockstar Games", "Rockstar North", "Rockstar", "Take-Two", "Grand Theft Auto", "GTA VI", "GTA 6", "GTA V", "GTA", "Vice City", "Vice Bay Radio", "Leonida", "Lucia Caminos", "Jason Duval", "Lucia", "Jason", "Newswire", "The Goodtime State", "PS5", "Xbox Series X|S", "Xbox", "Solange Rocheval", "Gabriel Janvier", "Daniel Jasner", "Lara Rivolet", "OKALAM Studio", "Virus Bus", "Zelnick", "Cyberleek", "GTAVIFRANCE"]
RX_NOMS = re.compile("|".join(re.escape(n) for n in NOMS))
NT = '<span class="notranslate">%s</span>'

def proteger(h):
    """Noms propres figés (hors balises) : Google ne traduit pas le contenu de class="notranslate"."""
    return "".join(p if p.startswith("<") else RX_NOMS.sub(lambda m: NT % m.group(0), p) for p in re.split(r"(<[^>]+>)", h))

def nettoyer(h):
    h = re.sub(r'<span class="notranslate">(.*?)</span>', r"\1", h, flags=re.S)
    h = re.sub(r' style=";?text-align:right;direction:rtl"', "", h)
    return re.sub(r"</a> ([.,;:)])", r"</a>\1", h)

def gtx(qs, l):
    """Traduit une liste de fragments HTML en une requête (POST, plusieurs q)."""
    for i in range(4):
        try:
            r = requests.post("https://translate.googleapis.com/translate_a/t", params={"client": "gtx", "sl": "en", "tl": G.get(l, l), "format": "html"},
                              data=[("q", q) for q in qs], headers=UA, timeout=60)
            r.raise_for_status(); j = r.json()
            j = [j] if isinstance(j, str) else [x if isinstance(x, str) else x[0] for x in j]
            if len(j) == len(qs): return j
        except Exception as e:
            err = e
        time.sleep(4 + i * 6)
    raise RuntimeError(f"échec {l}")

def article(src, l):
    t, d, h = (proteger(html.escape(src["t"], quote=False)), proteger(html.escape(src.get("d", ""), quote=False)), proteger(src.get("h", "")))
    rt, rd, rh = gtx([t, d or ".", h or "."], l)
    return {"t": html.unescape(nettoyer(rt)).strip(), "d": html.unescape(nettoyer(rd)).strip() if d else "", "h": nettoyer(rh) if h else ""}

if __name__ == "__main__":
    if "--test" in sys.argv:
        src = {"t": "Rockstar confirms GTA 6 price", "d": "Take-Two speaks.", "h": '<p>Rockstar confirmed it, <a href="https://x.y">according to IGN</a>. Price: 79.99 euros.</p><h2>Why it matters</h2>'}
        for l in ("ja", "zh", "tw", "idn", "ar"): print(l, article(src, l))
        sys.exit(0)

    arts = json.load(open("data/articles.json", encoding="utf-8"))
    faits = []
    for a in arts:
        src = a.get("en") if isinstance(a.get("en"), dict) and a["en"].get("t") else None
        if not src: continue
        manq = [l for l in L17 if l not in ("fr", "en") and (not isinstance(a.get(l), dict) or not a[l].get("t"))]
        if not manq: continue
        ok = []
        with ThreadPoolExecutor(5) as ex:
            futs = {l: ex.submit(article, src, l) for l in manq}
            for l, f in futs.items():
                try: a[l] = f.result(); ok.append(l)
                except Exception as e: print("échec", a["id"], l, str(e)[:100])
        if ok: faits.append(a["id"] + " (" + ",".join(ok) + ")")
        if len(faits) >= MAX: break
    if not faits: print("rien à traduire"); sys.exit(0)
    json.dump(arts, open("data/articles.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("traduit :", "; ".join(faits))
