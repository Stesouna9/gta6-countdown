"""Images de partage 1200x630 par page et par langue (assets/og/<l>/<page>.jpg), rendues par Chrome
pour que l'arabe, le hindi, le chinois, le japonais et le coréen s'affichent correctement. À relancer si les titres changent."""
import json, os, subprocess, tempfile, concurrent.futures as cf
from PIL import Image
os.chdir(os.path.dirname(os.path.abspath(__file__)) + "/..")
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
LANGS = ["fr", "en", "es", "pt", "de", "it", "ja", "zh", "tw", "ar", "hi", "ru", "ko", "tr", "id", "pl", "vi"]
PAGES = ["index", "actus", "sortie", "faq", "acheter", "guide", "vraifaux", "arabe", "radio", "vicebreak", "goodies", "quiz", "integrer", "apropos"]
NAV = {"index": "nav_home", "actus": "nav_news", "sortie": "nav_sortie", "faq": "nav_faq", "acheter": "nav_buy", "guide": "nav_guide", "vraifaux": "nav_vf",
       "arabe": "nav_arabe", "radio": "nav_radio", "vicebreak": "nav_vb", "goodies": "nav_goodies", "quiz": "nav_quiz", "integrer": "nav_int", "apropos": "nav_about"}
EN = json.load(open("tools/i18n/en.json"))
TPL = """<!doctype html><html lang="{hl}" dir="{dir}"><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Anton&family=JetBrains+Mono:wght@700&family=Lalezar&family=Noto+Sans+Devanagari:wght@800&display=block" rel="stylesheet">
<style>html,body{{margin:0;width:1200px;height:630px;overflow:hidden;background:#f2e8d5;color:#16111d}}
.top{{height:76px;background:#16111d;color:#f2e8d5;display:flex;justify-content:space-between;align-items:center;padding:0 48px;font:700 24px "JetBrains Mono",monospace;letter-spacing:.12em;text-transform:uppercase}}
.top b{{color:#ffc93c}} .r{{height:10px;background:#ff3b7a}} .r2{{height:10px;background:#ff8a2a}} .r3{{height:10px;background:#ffc93c}}
h1{{margin:0;position:absolute;top:106px;bottom:80px;left:0;right:0;display:flex;align-items:center;padding:0 48px;box-sizing:border-box;font:400 {fs}px/1.02 Anton,"Lalezar","Noto Sans Devanagari","Hiragino Sans","PingFang SC","PingFang TC","Apple SD Gothic Neo",sans-serif;text-transform:uppercase;text-shadow:7px 7px 0 #ff3b7a;overflow:hidden}}
.bas{{position:absolute;left:0;right:0;bottom:0;height:80px;background:#16111d;color:#f2e8d5;display:flex;justify-content:space-between;align-items:center;padding:0 48px;font:700 22px "JetBrains Mono",monospace;letter-spacing:.1em}}
.vi{{font:400 64px Anton;color:#ff3b7a;letter-spacing:0}}</style></head><body>
<div class="top"><span>VI Countdown · {kick}</span><b>19.11.2026</b></div><div class="r"></div><div class="r2"></div><div class="r3"></div>
<h1>{titre}</h1><div class="bas"><span>PS5 · XBOX SERIES X|S · LEONIDA</span><span class="vi">VI</span></div></body></html>"""
def un(l, p):
    D = {**EN, **json.load(open(f"tools/i18n/{l}.json"))}
    t = D.get("mt_" + p, "GTA VI"); n = len(t)
    fs = 138 if n < 30 else 118 if n < 45 else 100 if n < 62 else 86 if n < 80 else 74
    if l in ("ja", "zh", "tw", "ko"): fs = int(fs * .9)
    h = TPL.format(hl={"zh": "zh-Hans", "tw": "zh-Hant"}.get(l, l), dir="rtl" if l == "ar" else "ltr", kick=D.get(NAV[p], ""), titre=t, fs=fs)
    d = tempfile.mkdtemp(); f = os.path.join(d, "og.html"); open(f, "w", encoding="utf-8").write(h)
    png = os.path.join(d, "og.png")
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=1", "--window-size=1200,630",
                    "--virtual-time-budget=6000", f"--screenshot={png}", "file://" + f], capture_output=True, timeout=60)
    os.makedirs(f"assets/og/{l}", exist_ok=True)
    Image.open(png).convert("RGB").crop((0, 0, 1200, 630)).save(f"assets/og/{l}/{p}.jpg", quality=84, optimize=True)
    return l, p
with cf.ThreadPoolExecutor(6) as ex:
    r = list(ex.map(lambda a: un(*a), [(l, p) for l in LANGS for p in PAGES]))
print("og ok:", len(r))
