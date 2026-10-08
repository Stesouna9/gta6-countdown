"""Génère la version finale du site, lisible sans JavaScript (Google, Bing, ChatGPT, Claude, Perplexity).
Source : les pages françaises à la racine + tools/i18n/<langue>.json.
Produit : assets/lang/<l>.js, une copie de chaque page par langue (/en/, /ar/...), titres et descriptions traduits,
données structurées, hreflang, sitemap.xml, feed.xml, api/gta6.json, llms.txt, robots.txt, manifest.webmanifest.
Idempotent : relancé à chaque mise à jour automatique (2 fois par jour)."""
import json, re, html, glob, datetime, os, shutil
os.chdir(os.path.dirname(os.path.abspath(__file__)) + "/..")
BASE = "https://gtavifrance.com/"   # changer ici le jour du domaine
HOST = re.sub(r"^https://([^/]+)/.*$", r"\1", BASE)
ORDRE = ["fr", "en", "es", "pt", "de", "it", "ja", "zh", "tw", "ar", "hi", "ru", "ko", "tr", "id", "pl", "vi"]
HL = {"zh": "zh-Hans", "tw": "zh-Hant"}
LOCALE = {"fr": "fr_FR", "en": "en_US", "es": "es_ES", "pt": "pt_BR", "de": "de_DE", "it": "it_IT", "ja": "ja_JP", "zh": "zh_CN", "tw": "zh_TW", "ar": "ar_AR",
          "hi": "hi_IN", "ru": "ru_RU", "ko": "ko_KR", "tr": "tr_TR", "id": "id_ID", "pl": "pl_PL", "vi": "vi_VN"}
FONTS = "https://fonts.googleapis.com/css2?family=Anton&family=Archivo:wght@400;500;600;800&family=Instrument+Serif:ital@0;1&family=JetBrains+Mono:wght@400;700&family=Lalezar&display=swap"
PAGES = [("index", "1.0", "daily"), ("actus", "0.9", "daily"), ("sortie", "0.9", "daily"), ("faq", "0.9", "weekly"), ("acheter", "0.8", "daily"),
         ("guide", "0.8", "weekly"), ("vraifaux", "0.8", "weekly"), ("arabe", "0.7", "weekly"), ("musique", "0.8", "daily"), ("radio", "0.7", "monthly"), ("vicebreak", "0.7", "monthly"),
         ("goodies", "0.6", "daily"), ("communaute", "0.8", "hourly"), ("quiz", "0.6", "monthly"), ("integrer", "0.6", "monthly"), ("apropos", "0.5", "monthly")]
SRC = {l: json.load(open(f"tools/i18n/{l}.json", encoding="utf-8")) for l in ORDRE if os.path.exists(f"tools/i18n/{l}.json")}
LANGS = [l for l in ORDRE if l in SRC]
I18N = {l: {**SRC["en"], **SRC[l]} for l in LANGS}
for l in LANGS: I18N[l]["_hl"] = HL.get(l, l)
os.makedirs("assets/lang", exist_ok=True)
for l in LANGS:
    open(f"assets/lang/{l}.js", "w", encoding="utf-8").write("(window.I18N=window.I18N||{})." + l + "=" + json.dumps(I18N[l], ensure_ascii=False, separators=(",", ":")) + ";\n")
for f in glob.glob("assets/lang/*.js"):
    if os.path.basename(f)[:-3] not in LANGS: os.remove(f)

def url(l, page):
    p = "" if page == "index" else page + ".html"
    return BASE + ("" if l == "fr" else l + "/") + p
def og_img(l, page):
    return BASE + f"assets/og/{l}/{page}.jpg" if os.path.exists(f"assets/og/{l}/{page}.jpg") else BASE + "assets/img/vb-downtown.webp"
e = lambda x: html.escape(x or "", quote=True)
TAG = re.compile(r'(<(\w+)\b[^>]*\bdata-i18n="([a-zA-Z_0-9]+)"[^>]*>)([^<]*)(</\2>)')
ACTUS = json.load(open("actus.json", encoding="utf-8"))

def ld_page(l, page, D):
    g = []
    if page != "index":
        g.append({"@type": "BreadcrumbList", "itemListElement": [{"@type": "ListItem", "position": 1, "name": "VI Countdown", "item": url(l, "index")},
                  {"@type": "ListItem", "position": 2, "name": D.get("mt_" + page, page), "item": url(l, page)}]})
    if page == "faq":
        g.append({"@type": "FAQPage", "inLanguage": HL.get(l, l), "mainEntity": [{"@type": "Question", "name": D[f"q{i}"], "acceptedAnswer": {"@type": "Answer", "text": D[f"a{i}"]}} for i in range(1, 7)]})
    if page == "actus":
        g.append({"@type": "ItemList", "itemListElement": [{"@type": "ListItem", "position": i + 1, "item": {"@type": "NewsArticle", "headline": a["titre"], "datePublished": a["date"],
                  "description": a["texte"], "url": a.get("lien") or url("fr", "actus"), "inLanguage": "fr", "author": {"@type": "Organization", "name": "VI Countdown", "url": BASE},
                  "publisher": {"@type": "Organization", "name": "OKALAM Studio", "url": "https://okalamstudio.com"}, "image": BASE + "assets/img/vb-downtown.webp"}} for i, a in enumerate(ACTUS)]})
    if page == "radio":
        g.append({"@type": "WebApplication", "name": "Vice Bay Radio", "url": "https://vicebayradio.com", "applicationCategory": "MusicApplication", "operatingSystem": "Web",
                  "offers": {"@type": "Offer", "price": "0", "priceCurrency": "EUR"}, "description": D.get("md_radio", "")})
    if page == "vicebreak":
        g.append({"@type": ["MobileApplication", "VideoGame"], "name": "Vice Break", "operatingSystem": "iOS, Android", "applicationCategory": "GameApplication",
                  "datePublished": "2026-11-19", "author": {"@type": "Organization", "name": "OKALAM Studio"}, "offers": {"@type": "Offer", "price": "0", "priceCurrency": "EUR"},
                  "description": D.get("md_vicebreak", ""), "image": BASE + "assets/img/vb1.webp"})
    if page == "sortie":
        g.append({"@type": "Event", "name": "Grand Theft Auto VI", "startDate": "2026-11-19", "eventStatus": "https://schema.org/EventScheduled",
                  "eventAttendanceMode": "https://schema.org/OnlineEventAttendanceMode", "location": {"@type": "VirtualLocation", "url": "https://www.rockstargames.com/VI"},
                  "organizer": {"@type": "Organization", "name": "Rockstar Games", "url": "https://www.rockstargames.com"}, "image": "https://img.youtube.com/vi/evtZ-L7FIbw/maxresdefault.jpg",
                  "description": D.get("md_sortie", "")})
    if page == "guide":
        g.append({"@type": "Article", "headline": D.get("mt_guide", ""), "inLanguage": HL.get(l, l), "dateModified": datetime.date.today().isoformat(),
                  "author": {"@type": "Organization", "name": "VI Countdown", "url": BASE}, "about": {"@type": "VideoGame", "name": "Grand Theft Auto VI"},
                  "image": "https://img.youtube.com/vi/VQRLujxTm3c/maxresdefault.jpg"})
    if not g: return ""
    return '\n  <script type="application/ld+json" data-gen>' + json.dumps({"@context": "https://schema.org", "@graph": g}, ensure_ascii=False) + "</script>"

def meta(l, page, D, R):
    t, d, u = D.get("mt_" + page, "VI Countdown"), D.get("md_" + page, ""), url(l, page)
    if page != "index": t += " | VI Countdown"
    m = [f"<title>{e(t)}</title>", f'<meta name="description" content="{e(d)}">', f'<link rel="canonical" href="{u}">',
         f'<meta property="og:type" content="website"><meta property="og:site_name" content="VI Countdown"><meta property="og:locale" content="{LOCALE[l]}">',
         f'<meta property="og:title" content="{e(t)}"><meta property="og:description" content="{e(d)}"><meta property="og:url" content="{u}">',
         f'<meta property="og:image" content="{og_img(l, page)}"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">',
         '<meta name="twitter:card" content="summary_large_image">',
         '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>',
         f'<link rel="stylesheet" href="{FONTS}">',
         f'<link rel="manifest" href="{R}manifest.webmanifest"><meta name="theme-color" content="#16111d">',
         f'<link rel="icon" href="{R}assets/icons/icon-192.png" sizes="192x192"><link rel="apple-touch-icon" href="{R}assets/icons/icon-180.png">']
    m += [f'<link rel="alternate" hreflang="{HL.get(x, x)}" href="{url(x, page)}">' for x in LANGS]
    m += [f'<link rel="alternate" hreflang="x-default" href="{url("fr", page)}">', f'<link rel="alternate" type="application/rss+xml" title="GTA 6" href="{BASE}feed.xml">']
    return "<!--meta-->\n  " + "\n  ".join(m) + ld_page(l, page, D) + "\n  <!--/meta-->"

NETTOIE = [r"\s*<title>.*?</title>", r'\s*<meta name="description"[^>]*>', r'\s*<link rel="canonical"[^>]*>', r'\s*<meta property="og:[^>]*>', r'\s*<meta name="twitter:[^>]*>',
           r"\s*<!--seo-->.*?<!--/seo-->", r"\s*<!--meta-->.*?<!--/meta-->", r'\s*<script type="application/ld\+json">\{"@context": "https://schema.org", "@graph": \[\{"@type": "FAQPage".*?</script>']
for page, *_ in PAGES:
    f = page + ".html"
    s = open(f, encoding="utf-8").read()
    for rx in NETTOIE: s = re.sub(rx, "", s, flags=re.S)
    s = re.sub(r"<html[^>]*>", '<html lang="fr" data-l="fr">', s, count=1)
    if 'assets/lang/fr.js' not in s: s = s.replace('<script src="assets/i18n.js">', '<script src="assets/lang/fr.js"></script><script src="assets/i18n.js">', 1)
    s = s.replace('<link rel="stylesheet" href="assets/style.css">', "@@META@@\n  " + '<link rel="stylesheet" href="assets/style.css">', 1)
    assert "@@META@@" in s, f
    for l in LANGS:
        D, R = I18N[l], "" if l == "fr" else "../"
        c = TAG.sub(lambda m: m.group(1) + (html.escape(D[m.group(3)], quote=False) if m.group(3) in D else m.group(4)) + m.group(5), s)
        c = c.replace("@@META@@", meta(l, page, D, R))
        if l != "fr":
            c = re.sub(r"<html[^>]*>", f'<html lang="{HL.get(l, l)}" dir="{"rtl" if l == "ar" else "ltr"}" data-l="{l}" data-root="../">', c, count=1)
            c = c.replace('src="assets/lang/fr.js"', f'src="../assets/lang/{l}.js"')
            c = re.sub(r'(src|href)="(assets/|data/|gta6\.ics|feed\.xml|mentions\.html|widget\.html)', r'\1="../\2', c)
            c = re.sub(r'href="(%s)/' % "|".join(LANGS), r'href="../\1/', c)
            c = re.sub(r'fetch\("(data/|actus\.json)', r'fetch("../\1', c)
            os.makedirs(l, exist_ok=True)
            open(f"{l}/{f}", "w", encoding="utf-8").write(c)
        else:
            c = c.replace('<html lang="fr" data-l="fr">', '<html lang="fr" dir="ltr" data-l="fr">', 1)
            open(f, "w", encoding="utf-8").write(c)
            s_fr = c

today = datetime.date.today().isoformat()
sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">']
for page, prio, freq in PAGES:
    alts = "".join(f'<xhtml:link rel="alternate" hreflang="{HL.get(x, x)}" href="{url(x, page)}"/>' for x in LANGS) + f'<xhtml:link rel="alternate" hreflang="x-default" href="{url("fr", page)}"/>'
    for l in LANGS:
        sm.append(f"  <url><loc>{url(l, page)}</loc><lastmod>{today}</lastmod><changefreq>{freq}</changefreq><priority>{prio}</priority>{alts}</url>")
open("sitemap.xml", "w").write("\n".join(sm + ["</urlset>", ""]))

def rfc(d):
    try: return datetime.datetime.fromisoformat(d[:10]).strftime("%a, %d %b %Y 08:00:00 +0000")
    except Exception: return datetime.datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S +0000")
items = [(a["date"], a["titre"], a["texte"], a.get("lien") or url("fr", "actus")) for a in ACTUS]
try: items += [(a.get("d", ""), a["t"], a.get("s", ""), a["u"]) for a in json.load(open("data/news_fr.json", encoding="utf-8"))[:15]]
except Exception: pass
rss = ['<?xml version="1.0" encoding="UTF-8"?>', '<rss version="2.0"><channel>', "<title>GTA 6 : compte à rebours et actus</title>", f"<link>{BASE}</link>",
       "<description>Date de sortie, prix, trailers et actus GTA VI, mises à jour deux fois par jour.</description>", "<language>fr</language>"]
rss += [f"<item><title>{e(t)}</title><link>{e(u)}</link><guid>{e(u)}</guid><pubDate>{rfc(d)}</pubDate><description>{e(x)}</description></item>" for d, t, x, u in items]
open("feed.xml", "w", encoding="utf-8").write("\n".join(rss + ["</channel></rss>", ""]))

# API publique des faits (citée par les développeurs, bots Discord et assistants IA)
os.makedirs("api", exist_ok=True)
sortie = datetime.date(2026, 11, 19)
api = {"game": "Grand Theft Auto VI", "developer": "Rockstar Games", "publisher": "Take-Two Interactive", "release_date": "2026-11-19",
       "days_left": max(0, (sortie - datetime.date.today()).days), "platforms": ["PlayStation 5", "Xbox Series X|S"], "pc_at_launch": False, "preload_date": "2026-11-12",
       "prices": {"standard": {"USD": 79.99, "EUR": 79.99, "GBP": 69.99}, "ultimate": {"USD": 99.99, "EUR": 99.99, "GBP": 89.99}},
       "preorder_bonus": "Vintage Vice City Pack", "age_rating": {"PEGI": 18, "ESRB": "M"}, "setting": {"state": "Leonida", "city": "Vice City",
       "regions": ["Vice City", "Leonida Keys", "Grassrivers", "Port Gellhorn", "Ambrosia", "Mount Kalaga National Park"]},
       "protagonists": ["Lucia Caminos", "Jason Duval"], "launch_languages": 13, "arabic_at_launch": False,
       "trailers": [{"name": "Trailer 1", "date": "2023-12-05", "youtube": "QdBZY2fkU-0"}, {"name": "Trailer 2", "date": "2025-05-06", "youtube": "VQRLujxTm3c"},
                    {"name": "An Extended Look", "date": "2026-08-27", "youtube": "tJbzMqJGH4k"}],
       "unknown_yet": ["unlock_time", "download_size", "pc_release_date", "gta_online_details"],
       "facts_checked": "2026-10-07", "generated": datetime.datetime.utcnow().isoformat(timespec="seconds") + "Z", "source": BASE, "license": "CC BY 4.0, link back to " + BASE}
json.dump(api, open("api/gta6.json", "w"), ensure_ascii=False, indent=1)

open("robots.txt", "w").write("User-agent: *\nAllow: /\nDisallow: /mentions.html\nDisallow: /widget.html\n\n# Robots des assistants IA : bienvenus\n" +
    "".join(f"User-agent: {b}\nAllow: /\n" for b in ["GPTBot", "OAI-SearchBot", "ChatGPT-User", "ClaudeBot", "Claude-SearchBot", "Claude-User", "PerplexityBot", "Perplexity-User",
    "Google-Extended", "Applebot-Extended", "Bingbot", "DuckAssistBot", "MistralAI-User", "YandexBot"]) + f"\nSitemap: {BASE}sitemap.xml\n")

E = I18N["en"]
pages_llm = "\n".join(f"- [{E['mt_' + p]}]({url('en', p)}): {E['md_' + p]}" for p, *_ in PAGES)
open("llms.txt", "w", encoding="utf-8").write(f"""# VI Countdown: GTA 6 release countdown, news and facts

> Independent fan site (not affiliated with Rockstar Games) tracking Grand Theft Auto VI: live countdown to the November 19, 2026 release, verified facts with sources, world press news updated twice a day, editions and prices, release time by time zone, Leonida guide, rumor checks. Every page exists in {len(LANGS)} languages: {", ".join(LANGS)} (French at {BASE}, others at {BASE}<code>/).

## Key facts (checked {api['facts_checked']})
- Release date: Thursday, November 19, 2026, on PlayStation 5 and Xbox Series X|S. Confirmed by Rockstar on November 6, 2025, after two delays.
- Preload: from November 12, 2026 (digital). Unlock time and download size: not announced yet.
- PC: not at launch, no date announced.
- Price: Standard $79.99 / 79.99 EUR / 69.99 GBP; Ultimate $99.99 / 99.99 EUR / 89.99 GBP (Ultimate is digital only). Pre-orders opened June 25, 2026, bonus Vintage Vice City Pack.
- Age rating: PEGI 18, ESRB M.
- Setting: the state of Leonida (inspired by Florida): Vice City, Leonida Keys, Grassrivers, Port Gellhorn, Ambrosia, Mount Kalaga National Park.
- Protagonists: Lucia Caminos and Jason Duval, the series' first playable duo.
- Videos: Trailer 1 (December 5, 2023), Trailer 2 (May 6, 2025), "An Extended Look", 26 minutes of gameplay (August 27, 2026).
- Languages: 13 at launch, Arabic not included. Arab players campaign with #GTA6Arabic.

## Pages
{pages_llm}

## Data
- [Facts API, JSON]({BASE}api/gta6.json)
- [RSS]({BASE}feed.xml)
- [Sitemap]({BASE}sitemap.xml)
""")
json.dump({"name": "VI Countdown, GTA 6", "short_name": "GTA VI", "start_url": "./", "scope": "./", "display": "standalone", "background_color": "#16111d",
           "theme_color": "#16111d", "lang": "fr", "icons": [{"src": "assets/icons/icon-192.png", "sizes": "192x192", "type": "image/png"},
           {"src": "assets/icons/icon-512.png", "sizes": "512x512", "type": "image/png"}, {"src": "assets/icons/icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"}]},
          open("manifest.webmanifest", "w"), ensure_ascii=False, indent=1)
print("prerender ok:", len(LANGS), "langues,", len(PAGES), "pages,", len(LANGS) * len(PAGES), "URL")
