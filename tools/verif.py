import sys, time
from pathlib import Path
sys.argv = ["x", "--maintenant"]; sys.path.insert(0, str(Path.home() / "La Soso/depots/gta6-countdown/tools"))
import x_chrome as X
X.slot = "routine"
X.ouvre_onglet()
try:
    X.js("location.href='https://x.com/gtavifrancecom';1"); time.sleep(12)
    print(X.js("""(()=>JSON.stringify([...document.querySelectorAll('article')].slice(0,5).map(a=>[(a.querySelector('time')||{}).dateTime, a.innerText.replace(/\\n/g,' ').slice(0,110), ([...a.querySelectorAll('a[href*="/status/"]')].map(l=>l.getAttribute('href'))[0])])))()"""))
    print(X.js("(()=>document.body.innerText.match(/suspend|limit|verif|Something went wrong|locked/gi)+'')()"))
finally:
    X.ferme_onglet()
