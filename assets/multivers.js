/* Barre commune des sites OKALAM : GTA VI France, Vice Bay Radio, Vice Break, Kotoba, VoteDay.
   Même fichier sur gtavifrance.com et vicebayradio.com (assets/multivers.js ou multivers.js). */
(function(){
  if(window.__mv) return; window.__mv=1;
  var h=location.hostname.replace(/^www\./,''), me=/gtavifrance/.test(h)?'gta':/vicebayradio/.test(h)?'vbr':'';
  var src=me==='gta'?'gtavifrance':me==='vbr'?'vicebayradio':'site';
  var q='?utm_source='+src+'&utm_medium=referral&utm_campaign=multivers';
  var S=[
    ['gta','GTA VI France','https://gtavifrance.com/'],
    ['vbr','Vice Bay Radio','https://vicebayradio.com/'],
    ['vb','Vice Break','https://okalamstudio.com/vicebreak.html'],
    ['kot','Kotoba','https://okalamstudio.com/kotoba.html'],
    ['vd','VoteDay','https://okalamstudio.com/voteday.html']
  ];
  var P=[
    ['Kotoba · le mot du jour, gratuit sur iPhone et Android','https://okalamstudio.com/kotoba.html'],
    ['VoteDay · une question A ou B chaque jour','https://okalamstudio.com/voteday.html'],
    ['Vice Break · le casse-briques néon, sortie le 19 novembre','https://okalamstudio.com/vicebreak.html'],
    ['Vice Bay Radio · six stations FM, toute la nuit','https://vicebayradio.com/'],
    ['GTA VI France · le compte à rebours, les actus, la boutique','https://gtavifrance.com/']
  ].filter(function(p){return !(me==='gta'&&/gtavifrance/.test(p[1])||me==='vbr'&&/vicebayradio/.test(p[1]));});
  var css='#mvbar{position:relative;z-index:200;display:flex;align-items:center;gap:6px;min-height:38px;padding:0 14px;background:#0d0912;border-bottom:1px solid rgba(255,255,255,.14);font:600 12px/1.2 "DM Sans",system-ui,sans-serif;color:#f2e8d5;letter-spacing:.02em}'+
  '#mvbar .mvl{flex:none;font:700 10px "Space Mono",ui-monospace,monospace;letter-spacing:.16em;color:#ffb02e;margin-right:6px;text-transform:uppercase}'+
  '#mvbar .mvs{display:flex;gap:4px;overflow-x:auto;scrollbar-width:none;flex:1 1 auto}#mvbar .mvs::-webkit-scrollbar{display:none}'+
  '#mvbar a{flex:none;color:inherit;text-decoration:none;padding:7px 11px;border-radius:999px;border:1px solid transparent;white-space:nowrap}'+
  '#mvbar a:hover{border-color:rgba(242,232,213,.5)}#mvbar a.on{background:#f2e8d5;color:#16111d;pointer-events:none}'+
  '#mvbar .mvp{flex:none;max-width:42%;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;color:#ffb02e;padding:7px 4px 7px 12px;border-left:1px solid rgba(255,255,255,.14);margin-left:6px}'+
  '#mvbar .mvp i{font:700 9px "Space Mono",ui-monospace,monospace;border:1px solid rgba(255,176,46,.6);border-radius:4px;padding:1px 4px;margin-right:7px;font-style:normal}'+
  '@media(max-width:760px){#mvbar .mvp{display:none}#mvbar .mvl{display:none}}';
  var st=document.createElement('style'); st.textContent=css; document.head.appendChild(st);
  var b=document.createElement('div'); b.id='mvbar'; b.setAttribute('role','navigation'); b.setAttribute('aria-label','Les sites OKALAM');
  var html='<span class="mvl">Le multivers</span><div class="mvs">';
  S.forEach(function(s){ html+='<a'+(s[0]===me?' class="on" aria-current="true"':'')+' href="'+s[2]+q+'">'+s[1]+'</a>'; });
  html+='</div><a class="mvp" id="mvp" href="#"></a>';
  b.innerHTML=html;
  function ins(){ document.body.insertBefore(b,document.body.firstChild); var i=Math.floor(Math.random()*P.length), el=document.getElementById('mvp');
    function show(){ el.innerHTML='<i>PUB</i>'+P[i][0]; el.href=P[i][1]+q; i=(i+1)%P.length; } show(); setInterval(show,7000); }
  if(document.body) ins(); else document.addEventListener('DOMContentLoaded',ins);
})();
