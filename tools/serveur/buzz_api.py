from pathlib import Path
import ast,datetime
p=Path('/opt/mur/mur.py');s=p.read_text()
if '# BUZZ_API_V1' in s:print('Déjà installé');raise SystemExit(0)
old='''        try: _ARTS["ids"] = {x["id"] for x in json.load(open("/var/www/gtavifrance/data/articles.json", encoding="utf-8"))}; _ARTS["t"] = time.time()
        except Exception: pass'''
new='''        # BUZZ_API_V1 : conserver la liste des articles et autoriser uniquement les sujets Buzz publiés.
        try:
            ids = {x["id"] for x in json.load(open("/var/www/gtavifrance/data/articles.json", encoding="utf-8"))}
            try: ids.update("buzz-" + x["id"] for x in json.load(open("/var/www/gtavifrance/data/buzz.json", encoding="utf-8")).get("items", []))
            except (OSError, ValueError, KeyError): pass
            _ARTS["ids"] = ids; _ARTS["t"] = time.time()
        except Exception: pass'''
assert old in s;s=s.replace(old,new,1)
needle='    return {"lk": lk, "nb": nb,'
assert needle in s;s=s.replace(needle,'    clics = c.execute("SELECT COUNT(*) FROM buzz_clicks WHERE a=?", (a,)).fetchone()[0] if a.startswith("buzz-") else 0\n    return {"clics": clics, "lk": lk, "nb": nb,',1)
needle='    try: c.execute("ALTER TABLE messages ADD COLUMN uid INTEGER")'
assert needle in s;s=s.replace(needle,'    c.execute("CREATE TABLE IF NOT EXISTS buzz_clicks(a TEXT NOT NULL, v TEXT NOT NULL, t INTEGER NOT NULL, PRIMARY KEY(a,v))")\n'+needle,1)
needle='        if chemin in ("/api/art/vote", "/api/art/com", "/api/art/signaler"):'
assert needle in s
s=s.replace(needle,'''        if chemin == "/api/buzz/clic":
            a, v = str(d.get("a", "")), str(d.get("v", ""))
            if not a.startswith("buzz-") or not RX_ART.match(a) or not article_existe(a): return self._j(404, {"e": "sujet"})
            if not RX_V.match(v): return self._j(400, {"e": "v"})
            c = db(); c.execute("INSERT OR IGNORE INTO buzz_clicks(a,v,t) VALUES(?,?,?)", (a,v,int(time.time()))); c.commit()
            n = c.execute("SELECT COUNT(*) FROM buzz_clicks WHERE a=?", (a,)).fetchone()[0]; c.close()
            return self._j(200, {"clics": n})
'''+needle,1)
ast.parse(s)
bak=p.with_name('mur.py.before-buzz-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));bak.write_text(p.read_text());p.write_text(s);print('API ajoutée ; sauvegarde :',bak)
# Tests HTTP isolés : aucune fausse note ni faux clic dans la base du site.
import runpy,tempfile,threading,urllib.request,urllib.error,json
m=runpy.run_path(str(p),run_name='buzz_api_check')
with tempfile.TemporaryDirectory(prefix='gtavi-buzz-test-') as tmp:
 g=m['db'].__globals__;g['DB']=str(Path(tmp)/'test.sqlite');g['article_existe']=lambda a:a in ['buzz-test-only','article-test-only'];g['db']().close()
 server=m['ThreadingHTTPServer'](('127.0.0.1',0),m['H']);thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start();base='http://127.0.0.1:'+str(server.server_address[1])
 def call(path,body=None):
  req=urllib.request.Request(base+path,data=None if body is None else json.dumps(body).encode(),headers={'Content-Type':'application/json'})
  try:
   with urllib.request.urlopen(req,timeout=10) as r:return r.status,json.load(r)
  except urllib.error.HTTPError as e:return e.code,json.load(e)
 try:
  assert call('/api/art?a=buzz-test-only')[0]==200
  assert call('/api/art?a=buzz-inconnu')[0]==404
  status,v=call('/api/art/vote',{'a':'buzz-test-only','v':'test-visitor-123','note':5});assert status==200 and v['nb']==1 and v['moy']==5
  for _ in range(2):assert call('/api/buzz/clic',{'a':'buzz-test-only','v':'test-visitor-123'})[1]['clics']==1
  assert call('/api/art?a=buzz-test-only')[1]['clics']==1
  assert call('/api/art?a=article-test-only')[0]==200
  assert call('/api/buzz/clic',{'a':'article-test-only','v':'test-visitor-123'})[0]==404
  print('Tests API isolés : notes, moyenne, clic unique, rejet identifiant inconnu et articles existants OK')
 except Exception:
  p.write_text(bak.read_text());raise
 finally:server.shutdown();server.server_close()
