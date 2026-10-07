"""Rend le site lisible sans JavaScript (robots Google, Bing, ChatGPT, Claude, Perplexity).
- Remplit chaque [data-i18n] avec le texte français (le JS le remplace ensuite par la langue du visiteur).
- Insère hreflang (12 langues, ?lang=xx) + flux RSS dans <head>.
- Régénère sitemap.xml (lastmod) et feed.xml.
Idempotent : relancé à chaque mise à jour automatique."""
import json, re, html, glob, subprocess, datetime, os
os.chdir(os.path.dirname(os.path.abspath(__file__)) + "/..")
BASE = "https://stesouna9.github.io/gta6-countdown/"   # changer ici le jour du domaine
node = subprocess.run(["node", "-e", "global.navigator={language:'fr'};global.localStorage={getItem:()=>null};"
    "global.location={search:''};global.document={documentElement:{dataset:{}},querySelectorAll:()=>[],addEventListener:()=>{},getElementById:()=>null};"
    "global.window=global;require('./assets/i18n.js');process.stdout.write(JSON.stringify(I18N))"], capture_output=True, text=True, check=True)
I18N = json.loads(node.stdout); FR = I18N["fr"]; LANGS = list(I18N)
PAGES = {"index.html": ("", "1.0", "daily"), "actus.html": ("actus.html", "0.9", "daily"), "faq.html": ("faq.html", "0.9", "weekly"),
         "acheter.html": ("acheter.html", "0.8", "daily"), "radio.html": ("radio.html", "0.7", "monthly"),
         "vicebreak.html": ("vicebreak.html", "0.7", "monthly"), "goodies.html": ("goodies.html", "0.6", "daily")}
TAG = re.compile(r'(<(\w+)\b[^>]*\bdata-i18n="([a-z_0-9]+)"[^>]*>)([^<]*)(</\2>)')
for f, (path, *_ ) in PAGES.items():
    s = open(f, encoding="utf-8").read()
    s = TAG.sub(lambda m: m.group(1) + (html.escape(FR[m.group(3)], quote=False) if m.group(3) in FR else m.group(4)) + m.group(5), s)
    alt = "".join('\n  <link rel="alternate" hreflang="%s" href="%s%s?lang=%s">' % (l, BASE, path, l) for l in LANGS)
    alt += '\n  <link rel="alternate" hreflang="x-default" href="%s%s">' % (BASE, path)
    alt += '\n  <link rel="alternate" type="application/rss+xml" title="GTA 6 : actus" href="%sfeed.xml">' % BASE
    bloc = "<!--seo-->" + alt + "\n  <!--/seo-->"
    s = re.sub(r"<!--seo-->.*?<!--/seo-->", bloc, s, flags=re.S) if "<!--seo-->" in s else s.replace("</head>", "  " + bloc + "\n</head>", 1)
    open(f, "w", encoding="utf-8").write(s)
today = datetime.date.today().isoformat()
sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">']
for f, (path, prio, freq) in PAGES.items():
    alts = "".join('<xhtml:link rel="alternate" hreflang="%s" href="%s%s?lang=%s"/>' % (l, BASE, path, l) for l in LANGS)
    sm.append('  <url><loc>%s%s</loc><lastmod>%s</lastmod><changefreq>%s</changefreq><priority>%s</priority>%s</url>' % (BASE, path, today, freq, prio, alts))
open("sitemap.xml", "w").write("\n".join(sm + ["</urlset>", ""]))
def rfc(d):
    try: return datetime.datetime.fromisoformat(d[:10]).strftime("%a, %d %b %Y 08:00:00 +0000")
    except Exception: return datetime.datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S +0000")
items = []
for a in json.load(open("actus.json", encoding="utf-8")):
    items.append((a["date"], a["titre"], a["texte"], a.get("lien") or BASE + "actus.html"))
try:
    for a in json.load(open("data/news_fr.json", encoding="utf-8"))[:15]:
        items.append((a.get("d", ""), a["t"], a.get("s", ""), a["u"]))
except Exception: pass
e = lambda x: html.escape(x or "")
rss = ['<?xml version="1.0" encoding="UTF-8"?>', '<rss version="2.0"><channel>', "<title>GTA 6 : compte à rebours et actus</title>",
       "<link>%s</link>" % BASE, "<description>Date de sortie, prix, trailers et actus GTA VI, mises à jour deux fois par jour.</description>", "<language>fr</language>"]
for d, t, x, u in items:
    rss.append("<item><title>%s</title><link>%s</link><guid>%s</guid><pubDate>%s</pubDate><description>%s</description></item>" % (e(t), e(u), e(u), rfc(d), e(x)))
open("feed.xml", "w", encoding="utf-8").write("\n".join(rss + ["</channel></rss>", ""]))
print("prerender ok", len(LANGS), "langues", len(items), "items RSS")
