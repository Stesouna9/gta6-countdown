(function(){
 var grid=document.getElementById('buzz-grid');if(!grid)return;
 var filter='Tous', search=document.getElementById('buzz-search'),count=document.getElementById('buzz-count'),empty=document.getElementById('buzz-no-results');
 function update(){var q=search.value.trim().toLocaleLowerCase('fr'),n=0;grid.querySelectorAll('.buzz-card').forEach(function(c){var show=(filter==='Tous'||c.dataset.platform===filter)&&c.textContent.toLocaleLowerCase('fr').includes(q);c.hidden=!show;if(show)n++;});count.textContent=n+' sujet'+(n>1?'s':'')+' dans la sélection';empty.hidden=n!==0;}
 document.querySelectorAll('[data-buzz-filter]').forEach(function(b){b.addEventListener('click',function(){filter=b.dataset.buzzFilter;document.querySelectorAll('[data-buzz-filter]').forEach(function(x){x.setAttribute('aria-pressed',String(x===b));});update();});});search.addEventListener('input',update);update();
})();
