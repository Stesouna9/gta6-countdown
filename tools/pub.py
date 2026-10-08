#!/usr/bin/env python3
"""Pages d'acquisition automatiques (à lancer APRÈS prerender.py) :
   sortie/<pays>.html   heure de sortie par pays, dans la langue du pays
   q/<slug>.html        questions longue traîne (fr, en)
   prix.html, en/prix.html   comparateur de prix
   aujourdhui.html, en/today.html   article quotidien J-n (NewsArticle)
   sitemap.xml (ajout), sitemap-images.xml, robots.txt (ajout), feed.xml (hub WebSub + article du jour)
Les pages réutilisent l'habillage rendu (nav, pied) via <base href>."""
import datetime, html, json, os, re, zoneinfo
import sys; sys.path.insert(0, __import__('os').path.dirname(__file__)); from version import ver

BASE = "https://gtavifrance.com/"
SORTIE = datetime.datetime(2026, 11, 19, 0, 0, tzinfo=zoneinfo.ZoneInfo("Europe/Paris"))
TODAY = datetime.date.today()
J = (SORTIE.date() - TODAY).days
e = lambda x: html.escape(x or "", quote=True)

# ------------------------------------------------------------------ textes
T = {
 "fr": dict(h1="GTA 6 : heure de sortie en {p}", kick="{p} · 19 novembre 2026",
   intro="À quelle heure GTA 6 sera jouable en {p}, selon les deux scénarios possibles, et ce qui est confirmé.",
   a="Scénario 1 : déblocage à minuit, heure locale", a_i="C'est ce que Rockstar a fait pour GTA V et Red Dead Redemption 2 sur console. Le plus probable.",
   b="Scénario 2 : déblocage mondial simultané", b_i="Si Rockstar choisit une heure unique pour tous (ce site compte jusqu'à minuit, heure de Paris), ça donne chez toi :",
   pre="Préchargement", pre_v="Dès le 12 novembre 2026 en numérique, pour télécharger avant le jour J.",
   plat="Plateformes", plat_v="PlayStation 5, PS5 Pro, Xbox Series X et S. Pas de version PC au lancement.",
   prix="Prix", nc="Rockstar n'a pas encore annoncé l'heure exacte. Cette page se met à jour dès que c'est officiel.",
   q1="À quelle heure sort GTA 6 en {p} ?", r1="Le 19 novembre 2026. Si Rockstar débloque à minuit locale comme pour RDR2, c'est à 00:00 le 19 novembre en {p}. En cas de déblocage mondial simultané calé sur minuit à Paris, ce serait le {b}.",
   q2="Peut-on précharger GTA 6 en {p} ?", r2="Oui, le préchargement numérique ouvre le 12 novembre 2026 sur PS5 et Xbox Series.",
   q3="GTA 6 sort-il sur PC en {p} ?", r3="Non, pas au lancement. Rockstar n'a donné aucune date pour la version PC.",
   tz="Voir les 21 fuseaux", cal="Ajouter au calendrier", buy="Acheter le jeu", verif="Faits vérifiés le", src="Source : Rockstar Games"),
 "en": dict(h1="GTA 6 release time in {p}", kick="{p} · November 19, 2026",
   intro="What time GTA 6 unlocks in {p} under the two possible scenarios, plus everything confirmed so far.",
   a="Scenario 1: midnight local time unlock", a_i="This is what Rockstar did for GTA V and Red Dead Redemption 2 on consoles. The most likely option.",
   b="Scenario 2: simultaneous worldwide unlock", b_i="If Rockstar picks one global moment (this site counts down to midnight Paris time), that means for you:",
   pre="Preload", pre_v="From November 12, 2026 for digital editions, so you can download before launch day.",
   plat="Platforms", plat_v="PlayStation 5, PS5 Pro, Xbox Series X and S. No PC version at launch.",
   prix="Price", nc="Rockstar has not announced the exact unlock time yet. This page updates as soon as it is official.",
   q1="What time does GTA 6 come out in {p}?", r1="November 19, 2026. If Rockstar unlocks at midnight local time like RDR2, that is 00:00 on November 19 in {p}. With a simultaneous worldwide unlock set to midnight in Paris, it would be {b}.",
   q2="Can I preload GTA 6 in {p}?", r2="Yes, digital preload opens on November 12, 2026 on PS5 and Xbox Series.",
   q3="Is GTA 6 coming to PC in {p}?", r3="Not at launch. Rockstar has given no date for the PC version.",
   tz="See all 21 time zones", cal="Add to calendar", buy="Buy the game", verif="Facts checked on", src="Source: Rockstar Games"),
 "es": dict(h1="GTA 6: hora de lanzamiento en {p}", kick="{p} · 19 de noviembre de 2026",
   intro="A qué hora se desbloquea GTA 6 en {p} según los dos escenarios posibles, y todo lo confirmado.",
   a="Escenario 1: desbloqueo a medianoche, hora local", a_i="Así lo hizo Rockstar con GTA V y Red Dead Redemption 2 en consolas. Lo más probable.",
   b="Escenario 2: desbloqueo mundial simultáneo", b_i="Si Rockstar elige un único momento global (esta web cuenta hasta la medianoche de París), para ti sería:",
   pre="Precarga", pre_v="Desde el 12 de noviembre de 2026 en digital, para descargar antes del lanzamiento.",
   plat="Plataformas", plat_v="PlayStation 5, PS5 Pro, Xbox Series X y S. Sin versión para PC en el lanzamiento.",
   prix="Precio", nc="Rockstar aún no ha anunciado la hora exacta. Esta página se actualiza en cuanto sea oficial.",
   q1="¿A qué hora sale GTA 6 en {p}?", r1="El 19 de noviembre de 2026. Si Rockstar desbloquea a medianoche local como con RDR2, será a las 00:00 del 19 de noviembre en {p}. Con un desbloqueo mundial simultáneo fijado a la medianoche de París, sería el {b}.",
   q2="¿Se puede precargar GTA 6 en {p}?", r2="Sí, la precarga digital abre el 12 de noviembre de 2026 en PS5 y Xbox Series.",
   q3="¿GTA 6 sale en PC en {p}?", r3="No en el lanzamiento. Rockstar no ha dado fecha para la versión de PC.",
   tz="Ver las 21 zonas horarias", cal="Añadir al calendario", buy="Comprar el juego", verif="Datos verificados el", src="Fuente: Rockstar Games"),
 "pt": dict(h1="GTA 6: horário de lançamento no {p}", kick="{p} · 19 de novembro de 2026",
   intro="A que horas GTA 6 desbloqueia no {p} nos dois cenários possíveis, e tudo o que já está confirmado.",
   a="Cenário 1: desbloqueio à meia-noite, horário local", a_i="Foi assim com GTA V e Red Dead Redemption 2 nos consoles. O mais provável.",
   b="Cenário 2: desbloqueio mundial simultâneo", b_i="Se a Rockstar escolher um único momento global (este site conta até a meia-noite de Paris), para você seria:",
   pre="Pré-carregamento", pre_v="A partir de 12 de novembro de 2026 no digital, para baixar antes do lançamento.",
   plat="Plataformas", plat_v="PlayStation 5, PS5 Pro, Xbox Series X e S. Sem versão para PC no lançamento.",
   prix="Preço", nc="A Rockstar ainda não anunciou o horário exato. Esta página é atualizada assim que for oficial.",
   q1="Que horas GTA 6 sai no {p}?", r1="Em 19 de novembro de 2026. Se a Rockstar desbloquear à meia-noite local como no RDR2, será às 00:00 de 19 de novembro no {p}. Com desbloqueio mundial simultâneo na meia-noite de Paris, seria {b}.",
   q2="Dá para pré-carregar GTA 6 no {p}?", r2="Sim, o pré-carregamento digital abre em 12 de novembro de 2026 no PS5 e Xbox Series.",
   q3="GTA 6 sai no PC no {p}?", r3="Não no lançamento. A Rockstar não deu data para a versão de PC.",
   tz="Ver os 21 fusos horários", cal="Adicionar ao calendário", buy="Comprar o jogo", verif="Fatos verificados em", src="Fonte: Rockstar Games"),
 "de": dict(h1="GTA 6: Release-Uhrzeit in {p}", kick="{p} · 19. November 2026",
   intro="Um wie viel Uhr GTA 6 in {p} freigeschaltet wird, in beiden möglichen Szenarien, plus alles Bestätigte.",
   a="Szenario 1: Freischaltung um Mitternacht Ortszeit", a_i="So hat es Rockstar bei GTA V und Red Dead Redemption 2 auf Konsolen gemacht. Am wahrscheinlichsten.",
   b="Szenario 2: weltweit gleichzeitige Freischaltung", b_i="Wählt Rockstar einen globalen Zeitpunkt (diese Seite zählt bis Mitternacht Pariser Zeit), heißt das für dich:",
   pre="Preload", pre_v="Ab dem 12. November 2026 für digitale Versionen, damit du vor dem Release laden kannst.",
   plat="Plattformen", plat_v="PlayStation 5, PS5 Pro, Xbox Series X und S. Keine PC-Version zum Start.",
   prix="Preis", nc="Rockstar hat die genaue Uhrzeit noch nicht bekannt gegeben. Diese Seite wird aktualisiert, sobald es offiziell ist.",
   q1="Um wie viel Uhr erscheint GTA 6 in {p}?", r1="Am 19. November 2026. Schaltet Rockstar wie bei RDR2 um Mitternacht Ortszeit frei, ist es um 00:00 am 19. November in {p}. Bei weltweit gleichzeitiger Freischaltung um Mitternacht in Paris wäre es {b}.",
   q2="Kann man GTA 6 in {p} vorladen?", r2="Ja, der digitale Preload startet am 12. November 2026 auf PS5 und Xbox Series.",
   q3="Kommt GTA 6 in {p} für PC?", r3="Nicht zum Start. Rockstar hat keinen Termin für die PC-Version genannt.",
   tz="Alle 21 Zeitzonen", cal="Zum Kalender hinzufügen", buy="Spiel kaufen", verif="Fakten geprüft am", src="Quelle: Rockstar Games"),
 "it": dict(h1="GTA 6: orario di uscita in {p}", kick="{p} · 19 novembre 2026",
   intro="A che ora si sblocca GTA 6 in {p} nei due scenari possibili, e tutto ciò che è confermato.",
   a="Scenario 1: sblocco a mezzanotte, ora locale", a_i="Così ha fatto Rockstar con GTA V e Red Dead Redemption 2 su console. Il più probabile.",
   b="Scenario 2: sblocco mondiale simultaneo", b_i="Se Rockstar sceglie un unico momento globale (questo sito conta fino a mezzanotte, ora di Parigi), per te sarebbe:",
   pre="Precaricamento", pre_v="Dal 12 novembre 2026 in digitale, per scaricare prima del lancio.",
   plat="Piattaforme", plat_v="PlayStation 5, PS5 Pro, Xbox Series X e S. Nessuna versione PC al lancio.",
   prix="Prezzo", nc="Rockstar non ha ancora annunciato l'orario esatto. Questa pagina si aggiorna appena è ufficiale.",
   q1="A che ora esce GTA 6 in {p}?", r1="Il 19 novembre 2026. Se Rockstar sblocca a mezzanotte locale come per RDR2, sarà alle 00:00 del 19 novembre in {p}. Con uno sblocco mondiale simultaneo fissato a mezzanotte di Parigi, sarebbe {b}.",
   q2="Si può precaricare GTA 6 in {p}?", r2="Sì, il precaricamento digitale apre il 12 novembre 2026 su PS5 e Xbox Series.",
   q3="GTA 6 esce su PC in {p}?", r3="Non al lancio. Rockstar non ha dato date per la versione PC.",
   tz="Vedi i 21 fusi orari", cal="Aggiungi al calendario", buy="Compra il gioco", verif="Fatti verificati il", src="Fonte: Rockstar Games"),
 "ja": dict(h1="GTA6 {p}での発売時刻", kick="{p} · 2026年11月19日",
   intro="{p}でGTA6が遊べるようになる時刻を、考えられる2つのシナリオで整理。確定情報もまとめました。",
   a="シナリオ1：現地時間の午前0時に解禁", a_i="GTA VとRDR2のコンソール版でRockstarが採用した方式。最も有力です。",
   b="シナリオ2：全世界同時解禁", b_i="Rockstarが世界共通の時刻を選んだ場合（当サイトはパリ時間の午前0時までカウント）、あなたの地域では：",
   pre="事前ダウンロード", pre_v="デジタル版は2026年11月12日から。発売日前にダウンロードできます。",
   plat="対応機種", plat_v="PlayStation 5、PS5 Pro、Xbox Series X|S。発売時にPC版はありません。",
   prix="価格", nc="正確な解禁時刻はRockstarから未発表です。公式発表があり次第、このページを更新します。",
   q1="GTA6は{p}では何時に発売されますか？", r1="2026年11月19日です。RDR2と同じく現地時間の午前0時解禁なら、{p}では11月19日0:00。パリ時間の午前0時に全世界同時解禁なら{b}になります。",
   q2="{p}でGTA6の事前ダウンロードはできますか？", r2="はい。デジタル版の事前ダウンロードは2026年11月12日にPS5とXbox Seriesで開始します。",
   q3="GTA6は{p}でPC版が出ますか？", r3="発売時にはありません。PC版の日程はRockstarから発表されていません。",
   tz="21都市の時刻を見る", cal="カレンダーに追加", buy="ゲームを買う", verif="事実確認日", src="出典：Rockstar Games"),
 "zh": dict(h1="GTA6 {p}发售时间", kick="{p} · 2026年11月19日",
   intro="按两种可能的方案，看看GTA6在{p}几点解锁，以及目前已确认的全部信息。",
   a="方案一：当地时间零点解锁", a_i="GTA V和《荒野大镖客2》主机版都是这样做的。可能性最大。",
   b="方案二：全球同步解锁", b_i="如果Rockstar选择全球统一时刻（本站倒计时以巴黎时间零点为准），你所在地区的时间是：",
   pre="预载", pre_v="数字版自2026年11月12日起可预载，发售前即可下载完成。",
   plat="平台", plat_v="PlayStation 5、PS5 Pro、Xbox Series X|S。首发没有PC版。",
   prix="价格", nc="Rockstar尚未公布准确解锁时间。官方公布后本页会立即更新。",
   q1="GTA6在{p}几点发售？", r1="2026年11月19日。如果像《荒野大镖客2》那样当地零点解锁，{p}就是11月19日0:00。如果以巴黎零点全球同步解锁，则是{b}。",
   q2="在{p}可以预载GTA6吗？", r2="可以，数字版预载于2026年11月12日在PS5和Xbox Series开放。",
   q3="GTA6在{p}有PC版吗？", r3="首发没有。Rockstar尚未公布PC版日期。",
   tz="查看21个时区", cal="添加到日历", buy="购买游戏", verif="事实核查日期", src="来源：Rockstar Games"),
 "tw": dict(h1="GTA6 {p}發售時間", kick="{p} · 2026年11月19日",
   intro="依兩種可能方案，看看GTA6在{p}幾點解鎖，以及目前已確認的全部資訊。",
   a="方案一：當地時間零點解鎖", a_i="GTA V與《碧血狂殺2》主機版都是如此。可能性最高。",
   b="方案二：全球同步解鎖", b_i="若Rockstar選擇全球統一時刻（本站倒數以巴黎時間零點為準），你所在地區的時間是：",
   pre="預載", pre_v="數位版自2026年11月12日起可預載，發售前即可下載完成。",
   plat="平台", plat_v="PlayStation 5、PS5 Pro、Xbox Series X|S。首發沒有PC版。",
   prix="價格", nc="Rockstar尚未公布確切解鎖時間。官方公布後本頁會立即更新。",
   q1="GTA6在{p}幾點發售？", r1="2026年11月19日。若像《碧血狂殺2》一樣當地零點解鎖，{p}就是11月19日0:00。若以巴黎零點全球同步解鎖，則是{b}。",
   q2="在{p}可以預載GTA6嗎？", r2="可以，數位版預載於2026年11月12日在PS5與Xbox Series開放。",
   q3="GTA6在{p}有PC版嗎？", r3="首發沒有。Rockstar尚未公布PC版日期。",
   tz="查看21個時區", cal="加入行事曆", buy="購買遊戲", verif="事實查核日期", src="來源：Rockstar Games"),
 "ar": dict(h1="GTA 6: موعد الإصدار في {p}", kick="{p} · 19 نوفمبر 2026",
   intro="في أي ساعة تُفتح GTA 6 في {p} وفق السيناريوهين المحتملين، مع كل ما تم تأكيده.",
   a="السيناريو 1: الفتح عند منتصف الليل بالتوقيت المحلي", a_i="هكذا فعلت Rockstar مع GTA V وRed Dead Redemption 2 على المنصات. الأرجح.",
   b="السيناريو 2: فتح عالمي متزامن", b_i="إذا اختارت Rockstar لحظة واحدة للعالم كله (هذا الموقع يعد حتى منتصف الليل بتوقيت باريس)، فسيكون عندك:",
   pre="التحميل المسبق", pre_v="من 12 نوفمبر 2026 للنسخ الرقمية، لتحمّل اللعبة قبل يوم الإصدار.",
   plat="المنصات", plat_v="PlayStation 5 وPS5 Pro وXbox Series X|S. لا نسخة PC عند الإطلاق.",
   prix="السعر", nc="لم تعلن Rockstar بعد عن الساعة الدقيقة. تُحدَّث هذه الصفحة فور الإعلان الرسمي.",
   q1="في أي ساعة تصدر GTA 6 في {p}؟", r1="في 19 نوفمبر 2026. إذا فتحت Rockstar اللعبة عند منتصف الليل المحلي كما في RDR2، فذلك عند 00:00 يوم 19 نوفمبر في {p}. أما مع فتح عالمي متزامن عند منتصف الليل في باريس فسيكون {b}.",
   q2="هل يمكن التحميل المسبق لـ GTA 6 في {p}؟", r2="نعم، يبدأ التحميل المسبق الرقمي في 12 نوفمبر 2026 على PS5 وXbox Series.",
   q3="هل تصدر GTA 6 على PC في {p}؟", r3="ليس عند الإطلاق. لم تحدد Rockstar أي موعد لنسخة PC.",
   tz="عرض 21 منطقة زمنية", cal="إضافة إلى التقويم", buy="شراء اللعبة", verif="تم التحقق من المعلومات في", src="المصدر: Rockstar Games"),
 "hi": dict(h1="GTA 6: {p} में रिलीज़ का समय", kick="{p} · 19 नवंबर 2026",
   intro="दो संभावित परिदृश्यों के अनुसार {p} में GTA 6 किस समय अनलॉक होगा, और अब तक की सभी पुष्ट जानकारी।",
   a="परिदृश्य 1: स्थानीय समय आधी रात को अनलॉक", a_i="कंसोल पर GTA V और Red Dead Redemption 2 के लिए Rockstar ने यही किया था। सबसे संभावित।",
   b="परिदृश्य 2: दुनिया भर में एक साथ अनलॉक", b_i="अगर Rockstar एक वैश्विक समय चुनता है (यह साइट पेरिस समय आधी रात तक गिनती करती है), तो आपके लिए:",
   pre="प्रीलोड", pre_v="डिजिटल संस्करणों के लिए 12 नवंबर 2026 से, ताकि लॉन्च से पहले डाउनलोड हो सके।",
   plat="प्लेटफ़ॉर्म", plat_v="PlayStation 5, PS5 Pro, Xbox Series X और S। लॉन्च पर PC संस्करण नहीं।",
   prix="कीमत", nc="Rockstar ने अभी सटीक समय घोषित नहीं किया है। आधिकारिक होते ही यह पेज अपडेट होगा।",
   q1="{p} में GTA 6 किस समय रिलीज़ होगा?", r1="19 नवंबर 2026। अगर Rockstar RDR2 की तरह स्थानीय आधी रात को अनलॉक करता है, तो {p} में 19 नवंबर को 00:00 बजे। पेरिस की आधी रात पर वैश्विक अनलॉक होने पर यह {b} होगा।",
   q2="क्या {p} में GTA 6 प्रीलोड कर सकते हैं?", r2="हाँ, डिजिटल प्रीलोड 12 नवंबर 2026 को PS5 और Xbox Series पर खुलेगा।",
   q3="क्या {p} में GTA 6 PC पर आएगा?", r3="लॉन्च पर नहीं। Rockstar ने PC संस्करण की कोई तारीख नहीं दी है।",
   tz="सभी 21 टाइम ज़ोन देखें", cal="कैलेंडर में जोड़ें", buy="गेम खरीदें", verif="तथ्य जांचे गए", src="स्रोत: Rockstar Games"),
 "ru": dict(h1="GTA 6: время выхода в {p}", kick="{p} · 19 ноября 2026",
   intro="Во сколько GTA 6 откроется в {p} по двум возможным сценариям, и всё, что уже подтверждено.",
   a="Сценарий 1: разблокировка в полночь по местному времени", a_i="Так Rockstar поступила с GTA V и Red Dead Redemption 2 на консолях. Самый вероятный вариант.",
   b="Сценарий 2: одновременная разблокировка по всему миру", b_i="Если Rockstar выберет единый момент (этот сайт считает до полуночи по Парижу), для вас это:",
   pre="Предзагрузка", pre_v="С 12 ноября 2026 для цифровых изданий, чтобы скачать до релиза.",
   plat="Платформы", plat_v="PlayStation 5, PS5 Pro, Xbox Series X и S. Версии для ПК на старте нет.",
   prix="Цена", nc="Rockstar ещё не объявила точное время. Страница обновится сразу после официального анонса.",
   q1="Во сколько выходит GTA 6 в {p}?", r1="19 ноября 2026. Если Rockstar откроет игру в полночь по местному времени, как RDR2, то в {p} это 00:00 19 ноября. При одновременной мировой разблокировке в полночь по Парижу это будет {b}.",
   q2="Можно ли предзагрузить GTA 6 в {p}?", r2="Да, цифровая предзагрузка откроется 12 ноября 2026 на PS5 и Xbox Series.",
   q3="Выйдет ли GTA 6 на ПК в {p}?", r3="Не на старте. Rockstar не назвала дату версии для ПК.",
   tz="Все 21 часовой пояс", cal="Добавить в календарь", buy="Купить игру", verif="Факты проверены", src="Источник: Rockstar Games"),
 "ko": dict(h1="GTA 6 {p} 출시 시간", kick="{p} · 2026년 11월 19일",
   intro="두 가지 가능한 시나리오에 따라 {p}에서 GTA 6가 몇 시에 해금되는지, 그리고 확정된 정보를 정리했습니다.",
   a="시나리오 1: 현지 시간 자정 해금", a_i="콘솔판 GTA V와 레드 데드 리뎀션 2에서 Rockstar가 택한 방식입니다. 가장 유력합니다.",
   b="시나리오 2: 전 세계 동시 해금", b_i="Rockstar가 전 세계 공통 시각을 택한다면(이 사이트는 파리 시간 자정까지 카운트), 당신의 지역에서는:",
   pre="사전 다운로드", pre_v="디지털판은 2026년 11월 12일부터. 출시 전에 미리 받을 수 있습니다.",
   plat="플랫폼", plat_v="PlayStation 5, PS5 Pro, Xbox Series X|S. 출시 시 PC판은 없습니다.",
   prix="가격", nc="Rockstar는 정확한 해금 시각을 아직 발표하지 않았습니다. 공식 발표 즉시 이 페이지를 갱신합니다.",
   q1="GTA 6는 {p}에서 몇 시에 출시되나요?", r1="2026년 11월 19일입니다. RDR2처럼 현지 자정에 해금되면 {p}에서는 11월 19일 0:00입니다. 파리 자정 기준 전 세계 동시 해금이면 {b}입니다.",
   q2="{p}에서 GTA 6 사전 다운로드가 가능한가요?", r2="네, 디지털판 사전 다운로드는 2026년 11월 12일 PS5와 Xbox Series에서 시작됩니다.",
   q3="GTA 6는 {p}에서 PC로 나오나요?", r3="출시 시에는 아닙니다. Rockstar는 PC판 일정을 밝히지 않았습니다.",
   tz="21개 시간대 보기", cal="캘린더에 추가", buy="게임 구매", verif="사실 확인일", src="출처: Rockstar Games"),
 "tr": dict(h1="GTA 6: {p} çıkış saati", kick="{p} · 19 Kasım 2026",
   intro="GTA 6'nın {p} için iki olası senaryoda saat kaçta açılacağı ve şu ana kadar doğrulanan her şey.",
   a="Senaryo 1: yerel saatle gece yarısı açılış", a_i="Rockstar konsolda GTA V ve Red Dead Redemption 2 için böyle yaptı. En olası seçenek.",
   b="Senaryo 2: dünya çapında eş zamanlı açılış", b_i="Rockstar tek bir küresel an seçerse (bu site Paris saatiyle gece yarısına kadar sayıyor), sizin için:",
   pre="Ön yükleme", pre_v="Dijital sürümler için 12 Kasım 2026'dan itibaren, çıkış gününden önce indirebilmeniz için.",
   plat="Platformlar", plat_v="PlayStation 5, PS5 Pro, Xbox Series X ve S. Çıkışta PC sürümü yok.",
   prix="Fiyat", nc="Rockstar kesin saati henüz açıklamadı. Resmî olur olmaz bu sayfa güncellenir.",
   q1="GTA 6 {p} için saat kaçta çıkıyor?", r1="19 Kasım 2026. Rockstar RDR2'deki gibi yerel gece yarısında açarsa, {p} için 19 Kasım 00:00. Paris gece yarısına ayarlı eş zamanlı küresel açılışta ise {b} olur.",
   q2="{p} için GTA 6 ön yüklenebilir mi?", r2="Evet, dijital ön yükleme 12 Kasım 2026'da PS5 ve Xbox Series'te açılıyor.",
   q3="GTA 6 {p} için PC'ye geliyor mu?", r3="Çıkışta değil. Rockstar PC sürümü için tarih vermedi.",
   tz="21 saat dilimini gör", cal="Takvime ekle", buy="Oyunu satın al", verif="Bilgiler şu tarihte doğrulandı:", src="Kaynak: Rockstar Games"),
 "id": dict(h1="GTA 6: jam rilis di {p}", kick="{p} · 19 November 2026",
   intro="Jam berapa GTA 6 terbuka di {p} menurut dua skenario yang mungkin, plus semua yang sudah dikonfirmasi.",
   a="Skenario 1: terbuka tengah malam waktu setempat", a_i="Begitulah Rockstar melakukannya untuk GTA V dan Red Dead Redemption 2 di konsol. Paling mungkin.",
   b="Skenario 2: terbuka serentak di seluruh dunia", b_i="Jika Rockstar memilih satu waktu global (situs ini menghitung sampai tengah malam waktu Paris), bagi Anda berarti:",
   pre="Pramuat", pre_v="Mulai 12 November 2026 untuk edisi digital, agar bisa diunduh sebelum hari rilis.",
   plat="Platform", plat_v="PlayStation 5, PS5 Pro, Xbox Series X dan S. Tidak ada versi PC saat rilis.",
   prix="Harga", nc="Rockstar belum mengumumkan jam pastinya. Halaman ini diperbarui begitu resmi.",
   q1="Jam berapa GTA 6 rilis di {p}?", r1="19 November 2026. Jika Rockstar membuka pada tengah malam setempat seperti RDR2, berarti pukul 00:00 tanggal 19 November di {p}. Dengan pembukaan serentak global pada tengah malam Paris, jadinya {b}.",
   q2="Bisakah pramuat GTA 6 di {p}?", r2="Ya, pramuat digital dibuka 12 November 2026 di PS5 dan Xbox Series.",
   q3="Apakah GTA 6 rilis di PC di {p}?", r3="Tidak saat rilis. Rockstar belum memberi tanggal untuk versi PC.",
   tz="Lihat 21 zona waktu", cal="Tambahkan ke kalender", buy="Beli gim", verif="Fakta diverifikasi pada", src="Sumber: Rockstar Games"),
 "pl": dict(h1="GTA 6: godzina premiery w {p}", kick="{p} · 19 listopada 2026",
   intro="O której GTA 6 odblokuje się w {p} według dwóch możliwych scenariuszy, plus wszystko, co potwierdzone.",
   a="Scenariusz 1: odblokowanie o północy czasu lokalnego", a_i="Tak Rockstar zrobił z GTA V i Red Dead Redemption 2 na konsolach. Najbardziej prawdopodobne.",
   b="Scenariusz 2: jednoczesne odblokowanie na całym świecie", b_i="Jeśli Rockstar wybierze jeden globalny moment (ta strona odlicza do północy czasu paryskiego), u ciebie będzie to:",
   pre="Preload", pre_v="Od 12 listopada 2026 dla wersji cyfrowych, by pobrać grę przed premierą.",
   plat="Platformy", plat_v="PlayStation 5, PS5 Pro, Xbox Series X i S. Brak wersji PC na premierę.",
   prix="Cena", nc="Rockstar nie podał jeszcze dokładnej godziny. Strona zaktualizuje się, gdy będzie oficjalnie.",
   q1="O której wychodzi GTA 6 w {p}?", r1="19 listopada 2026. Jeśli Rockstar odblokuje grę o północy czasu lokalnego jak RDR2, to o 00:00 19 listopada w {p}. Przy jednoczesnym globalnym odblokowaniu o północy w Paryżu byłoby to {b}.",
   q2="Czy można pobrać GTA 6 wcześniej w {p}?", r2="Tak, cyfrowy preload rusza 12 listopada 2026 na PS5 i Xbox Series.",
   q3="Czy GTA 6 wyjdzie na PC w {p}?", r3="Nie na premierę. Rockstar nie podał daty wersji PC.",
   tz="Zobacz 21 stref czasowych", cal="Dodaj do kalendarza", buy="Kup grę", verif="Fakty sprawdzone", src="Źródło: Rockstar Games"),
 "vi": dict(h1="GTA 6: giờ phát hành tại {p}", kick="{p} · 19 tháng 11, 2026",
   intro="GTA 6 mở khóa lúc mấy giờ tại {p} theo hai kịch bản có thể, cùng mọi thông tin đã được xác nhận.",
   a="Kịch bản 1: mở khóa lúc 0 giờ theo giờ địa phương", a_i="Rockstar đã làm vậy với GTA V và Red Dead Redemption 2 trên console. Khả năng cao nhất.",
   b="Kịch bản 2: mở khóa đồng thời toàn cầu", b_i="Nếu Rockstar chọn một thời điểm chung toàn cầu (trang này đếm ngược tới 0 giờ Paris), với bạn sẽ là:",
   pre="Tải trước", pre_v="Từ 12 tháng 11, 2026 cho bản kỹ thuật số, để tải xong trước ngày ra mắt.",
   plat="Nền tảng", plat_v="PlayStation 5, PS5 Pro, Xbox Series X và S. Không có bản PC khi ra mắt.",
   prix="Giá", nc="Rockstar chưa công bố giờ chính xác. Trang này sẽ cập nhật ngay khi có thông tin chính thức.",
   q1="GTA 6 ra mắt lúc mấy giờ tại {p}?", r1="Ngày 19 tháng 11, 2026. Nếu Rockstar mở khóa lúc 0 giờ địa phương như RDR2, tại {p} là 00:00 ngày 19/11. Nếu mở khóa đồng thời toàn cầu theo 0 giờ Paris, sẽ là {b}.",
   q2="Có thể tải trước GTA 6 tại {p} không?", r2="Có, tải trước bản kỹ thuật số mở từ 12 tháng 11, 2026 trên PS5 và Xbox Series.",
   q3="GTA 6 có ra trên PC tại {p} không?", r3="Không khi ra mắt. Rockstar chưa đưa ra ngày cho bản PC.",
   tz="Xem 21 múi giờ", cal="Thêm vào lịch", buy="Mua game", verif="Thông tin được kiểm chứng ngày", src="Nguồn: Rockstar Games"),
}

# slug, langue, nom du pays dans sa langue, fuseau, prix local confirmé ou None
PAYS = [
 ("france","fr","France","Europe/Paris","79,99 € (standard), 99,99 € (Ultimate numérique)"),
 ("belgique","fr","Belgique","Europe/Brussels","79,99 € (standard), 99,99 € (Ultimate numérique)"),
 ("suisse","fr","Suisse","Europe/Zurich",None),
 ("quebec","fr","Québec","America/Toronto",None),
 ("maroc","fr","Maroc","Africa/Casablanca",None),
 ("algerie","fr","Algérie","Africa/Algiers",None),
 ("tunisie","fr","Tunisie","Africa/Tunis",None),
 ("senegal","fr","Sénégal","Africa/Dakar",None),
 ("cote-d-ivoire","fr","Côte d'Ivoire","Africa/Abidjan",None),
 ("usa","en","the United States","America/New_York",None),
 ("usa-west-coast","en","the US West Coast","America/Los_Angeles",None),
 ("uk","en","the UK","Europe/London","£69.99 (standard), £89.99 (digital Ultimate)"),
 ("ireland","en","Ireland","Europe/Dublin","€79.99 (standard), €99.99 (digital Ultimate)"),
 ("canada","en","Canada","America/Toronto",None),
 ("australia","en","Australia","Australia/Sydney",None),
 ("new-zealand","en","New Zealand","Pacific/Auckland",None),
 ("india","en","India","Asia/Kolkata",None),
 ("south-africa","en","South Africa","Africa/Johannesburg",None),
 ("nigeria","en","Nigeria","Africa/Lagos",None),
 ("philippines","en","the Philippines","Asia/Manila",None),
 ("espana","es","España","Europe/Madrid","79,99 € (estándar), 99,99 € (Ultimate digital)"),
 ("mexico","es","México","America/Mexico_City",None),
 ("argentina","es","Argentina","America/Argentina/Buenos_Aires",None),
 ("colombia","es","Colombia","America/Bogota",None),
 ("chile","es","Chile","America/Santiago",None),
 ("brasil","pt","Brasil","America/Sao_Paulo",None),
 ("portugal","pt","Portugal","Europe/Lisbon","79,99 € (padrão), 99,99 € (Ultimate digital)"),
 ("deutschland","de","Deutschland","Europe/Berlin","79,99 € (Standard), 99,99 € (digitale Ultimate)"),
 ("osterreich","de","Österreich","Europe/Vienna","79,99 € (Standard), 99,99 € (digitale Ultimate)"),
 ("schweiz","de","der Schweiz","Europe/Zurich",None),
 ("italia","it","Italia","Europe/Rome","79,99 € (standard), 99,99 € (Ultimate digitale)"),
 ("japan","ja","日本","Asia/Tokyo",None),
 ("china","zh","中国","Asia/Shanghai",None),
 ("taiwan","tw","台灣","Asia/Taipei",None),
 ("saudi","ar","السعودية","Asia/Riyadh",None),
 ("egypt","ar","مصر","Africa/Cairo",None),
 ("uae","ar","الإمارات","Asia/Dubai",None),
 ("morocco","ar","المغرب","Africa/Casablanca",None),
 ("bharat","hi","भारत","Asia/Kolkata",None),
 ("russia","ru","России","Europe/Moscow",None),
 ("korea","ko","한국","Asia/Seoul",None),
 ("turkiye","tr","Türkiye","Europe/Istanbul",None),
 ("indonesia","id","Indonesia","Asia/Jakarta",None),
 ("polska","pl","Polsce","Europe/Warsaw",None),
 ("vietnam","vi","Việt Nam","Asia/Ho_Chi_Minh",None),
]
LOC = {"fr":"fr","en":"en","es":"es","pt":"pt","de":"de","it":"it","ja":"ja","zh":"zh-Hans","tw":"zh-Hant","ar":"ar","hi":"hi","ru":"ru","ko":"ko","tr":"tr","id":"id","pl":"pl","vi":"vi"}

# ------------------------------------------------------------------ habillage
def shell(l, page="sortie"):
    f = f"{page}.html" if l == "fr" else f"{l}/{page}.html"
    c = open(f, encoding="utf-8").read()
    head = c[:c.index('<header class="tete-page')]
    foot = '\n  <div class="pub vide"></div>\n  ' + re.search(r'<script src="[^"]*site\.js[^"]*"></script>', c).group(0) + "\n</body>\n</html>\n"
    head = re.sub(r'<link rel="alternate" hreflang="[^"]*" href="[^"]*"\s*/?>\s*', "", head)
    head = re.sub(r'<script type="application/ld\+json">.*?</script>\s*', "", head, flags=re.S)
    head = re.sub(r'<link rel="canonical" href="[^"]*"\s*/?>', "", head)
    head = re.sub(r'<meta property="og:(url|title|description|image)" content="[^"]*"\s*/?>\s*', "", head)
    head = re.sub(r'<meta name="(description|twitter:title|twitter:description|twitter:image)" content="[^"]*"\s*/?>\s*', "", head)
    head = re.sub(r"<title>.*?</title>", "", head, flags=re.S)
    head = head.replace("<head>", '<head>\n<base href="%s%s">' % (BASE, "" if l == "fr" else l + "/"), 1)
    return head, foot

def page(l, url, title, desc, body, ld, img=None, page_shell="sortie"):
    head, foot = shell(l, page_shell)
    img = img or BASE + f"assets/og/{l}/sortie.jpg"
    metas = (f"<title>{e(title)}</title>\n<meta name=\"description\" content=\"{e(desc)}\">\n<link rel=\"canonical\" href=\"{url}\">\n"
             f"<meta property=\"og:url\" content=\"{url}\"><meta property=\"og:title\" content=\"{e(title)}\"><meta property=\"og:description\" content=\"{e(desc)}\"><meta property=\"og:image\" content=\"{img}\">\n"
             f"<meta name=\"twitter:title\" content=\"{e(title)}\"><meta name=\"twitter:description\" content=\"{e(desc)}\"><meta name=\"twitter:image\" content=\"{img}\">\n"
             + "".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>\n' for x in ld))
    head = head.replace("</head>", metas + "</head>", 1)
    return head + body + foot

def write(path, content):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    open(path, "w", encoding="utf-8").write(ver(content))

def fmt_local(dt, l):
    """Date et heure locales lisibles."""
    d = dt.strftime("%d/%m/%Y") if l in ("fr", "es", "pt", "it", "de", "pl", "ru", "tr", "id", "vi") else dt.strftime("%Y-%m-%d") if l in ("ja", "zh", "tw", "ko") else dt.strftime("%m/%d/%Y") if l == "en" else dt.strftime("%d/%m/%Y")
    return f"{d} {dt.strftime('%H:%M')}"

URLS = []  # (url, lang, prio)

# ------------------------------------------------------------------ 1. pages pays
for slug, l, nom, tz, prix in PAYS:
    t = {k: v.replace("{p}", nom) for k, v in T[l].items()}
    local_b = SORTIE.astimezone(zoneinfo.ZoneInfo(tz))
    b_txt = fmt_local(local_b, l)
    t["r1"] = t["r1"].replace("{b}", b_txt)
    url = f"{BASE}sortie/{slug}.html"
    title = t["h1"] + " | VI Countdown"
    body = f"""
  <header class="tete-page chaud"><div class="wrap"><span class="kicker">{e(t['kick'])}</span><h1>{e(t['h1'])}</h1><p>{e(t['intro'])}</p></div></header>
  <section class="papier"><div class="wrap">
    <div class="rubrique rv"><span class="num">01</span><h2>{e(t['a'])}</h2><p>{e(t['a_i'])}</p></div>
    <p class="display" style="font-size:clamp(3rem,9vw,7rem);line-height:.9;margin:0 0 40px">19.11.2026 · 00:00</p>
    <div class="rubrique rv"><span class="num">02</span><h2>{e(t['b'])}</h2><p>{e(t['b_i'])}</p></div>
    <p class="display" style="font-size:clamp(3rem,9vw,7rem);line-height:.9;margin:0 0 40px">{e(b_txt)}</p>
    <div class="scroll-x rv"><table class="tableau"><tbody>
      <tr><td>{e(t['pre'])}</td><td>{e(t['pre_v'])}</td></tr>
      <tr><td>{e(t['plat'])}</td><td>{e(t['plat_v'])}</td></tr>
      {f"<tr><td>{e(t['prix'])}</td><td>{e(prix)}</td></tr>" if prix else ""}
    </tbody></table></div>
    <p class="verifie">{e(t['verif'])} <span data-verif></span> · <a href="https://www.rockstargames.com/VI" target="_blank" rel="noopener">{e(t['src'])}</a></p>
    <div class="boutons"><a class="btn" href="sortie.html">{e(t['tz'])}</a><a class="btn clair" href="gta6.ics" download>{e(t['cal'])}</a><a class="btn or" href="acheter.html">{e(t['buy'])}</a></div>
  </div></section>
  <section><div class="wrap">
    <div class="rubrique rv"><span class="num">03</span><h2>FAQ</h2></div>
    <details open><summary><b>{e(t['q1'])}</b></summary><p>{e(t['r1'])}</p></details>
    <details><summary><b>{e(t['q2'])}</b></summary><p>{e(t['r2'])}</p></details>
    <details><summary><b>{e(t['q3'])}</b></summary><p>{e(t['r3'])}</p></details>
    <div class="partage"></div>
  </div></section>
"""
    ld = [{"@context": "https://schema.org", "@type": "FAQPage", "inLanguage": LOC[l], "mainEntity": [
            {"@type": "Question", "name": t[q], "acceptedAnswer": {"@type": "Answer", "text": t[r]}} for q, r in (("q1", "r1"), ("q2", "r2"), ("q3", "r3"))]},
          {"@context": "https://schema.org", "@type": "Event", "name": "Grand Theft Auto VI", "startDate": "2026-11-19", "eventStatus": "https://schema.org/EventScheduled",
           "eventAttendanceMode": "https://schema.org/OnlineEventAttendanceMode", "location": {"@type": "VirtualLocation", "url": url}, "organizer": {"@type": "Organization", "name": "Rockstar Games", "url": "https://www.rockstargames.com/VI"},
           "description": t["intro"], "url": url}]
    write(f"sortie/{slug}.html", page(l, url, title, t["intro"], body, ld))
    URLS.append((url, l, "0.8"))

# ------------------------------------------------------------------ 2. questions longue traîne
Q = {"fr": [
 ("taille-gta-6", "Quelle est la taille de GTA 6 ?", "Rockstar n'a pas encore communiqué la taille du téléchargement de GTA 6. Pour comparaison, Red Dead Redemption 2 pesait environ 100 Go et GTA V environ 95 Go sur PS5. Prévois au moins 150 Go libres sur ta console, le préchargement ouvre le 12 novembre 2026."),
 ("gta-6-pc", "GTA 6 sort-il sur PC ?", "Non, pas au lancement du 19 novembre 2026. GTA 6 sort d'abord sur PlayStation 5 et Xbox Series X|S. Rockstar n'a annoncé aucune date pour le PC. Pour GTA V, la version PC était arrivée 17 mois après les consoles."),
 ("gta-6-ps4", "GTA 6 sort-il sur PS4 et Xbox One ?", "Non. GTA 6 est annoncé uniquement sur PS5, PS5 Pro, Xbox Series X et Xbox Series S. Aucune version PS4, Xbox One ou Switch n'est prévue."),
 ("prix-gta-6", "Quel est le prix de GTA 6 ?", "En Europe, l'édition standard est à 79,99 € et l'édition Ultimate numérique à 99,99 €. Au Royaume-Uni, 69,99 £ et 89,99 £. L'édition Ultimate n'existe qu'en numérique."),
 ("precommande-gta-6", "Peut-on précommander GTA 6 ?", "Oui, les précommandes sont ouvertes sur le PlayStation Store, le Microsoft Store et chez les revendeurs (Amazon, Fnac, Leclerc, Micromania). Le préchargement numérique démarre le 12 novembre 2026."),
 ("gta-6-online", "GTA 6 Online sort-il en même temps ?", "Rockstar n'a pas encore détaillé GTA Online pour GTA 6. Pour GTA V, le mode en ligne avait ouvert deux semaines après le jeu solo. Rien d'officiel pour l'instant."),
 ("heure-sortie-gta-6", "À quelle heure sort GTA 6 ?", "Rockstar n'a pas annoncé l'heure de déblocage. Deux scénarios : minuit heure locale (comme GTA V et RDR2 sur console) ou un déblocage mondial simultané. Ce site compte jusqu'à minuit, heure de Paris, et sera corrigé dès l'annonce."),
 ("gta-6-arabe", "GTA 6 sera-t-il traduit en arabe ?", "Non, l'arabe ne fait pas partie des 13 langues annoncées au lancement. Une campagne de joueurs, #GTA6Arabic, demande à Rockstar d'ajouter la langue. Ce site soutient la campagne."),
 ("carte-gta-6", "Quelle est la taille de la carte de GTA 6 ?", "Rockstar n'a donné aucun chiffre officiel. L'État de Leonida comprend au moins six régions montrées dans les trailers : Vice City, les Keys, Grassrivers, Port Gellhorn, Ambrosia et Mount Kalaga. Les comparaisons de taille qui circulent sont des estimations de fans."),
 ("gta-6-report", "GTA 6 va-t-il encore être reporté ?", "La date officielle est le 19 novembre 2026, après deux reports (automne 2025 puis 26 mai 2026). Take-Two a confirmé cette date dans ses résultats financiers. Aucun nouveau report n'a été annoncé."),
 ], "en": [
 ("gta-6-file-size", "How big is GTA 6?", "Rockstar has not announced the GTA 6 download size yet. For comparison, Red Dead Redemption 2 was about 100 GB and GTA V about 95 GB on PS5. Keep at least 150 GB free; preload opens on November 12, 2026."),
 ("gta-6-pc", "Is GTA 6 coming to PC?", "Not at the November 19, 2026 launch. GTA 6 arrives first on PlayStation 5 and Xbox Series X|S. Rockstar has not announced any PC date. GTA V reached PC 17 months after consoles."),
 ("gta-6-ps4", "Is GTA 6 on PS4 or Xbox One?", "No. GTA 6 is announced only for PS5, PS5 Pro, Xbox Series X and Xbox Series S. No PS4, Xbox One or Switch version is planned."),
 ("gta-6-price", "How much does GTA 6 cost?", "In Europe the standard edition is €79.99 and the digital Ultimate edition €99.99. In the UK, £69.99 and £89.99. Rockstar has not published US dollar prices yet. The Ultimate edition is digital only."),
 ("gta-6-preorder", "Can I pre-order GTA 6?", "Yes, pre-orders are open on the PlayStation Store, Microsoft Store and at retailers. Digital preload starts on November 12, 2026."),
 ("gta-6-online", "Does GTA 6 Online launch on the same day?", "Rockstar has not detailed GTA Online for GTA 6 yet. For GTA V, online mode opened two weeks after the single-player game. Nothing official so far."),
 ("gta-6-release-time", "What time does GTA 6 unlock?", "Rockstar has not announced the unlock time. Two scenarios: midnight local time (as with GTA V and RDR2 on consoles) or one simultaneous worldwide unlock. This site counts down to midnight Paris time and will be corrected on announcement."),
 ("gta-6-arabic", "Will GTA 6 be in Arabic?", "No, Arabic is not among the 13 launch languages. A player campaign, #GTA6Arabic, is asking Rockstar to add it. This site supports the campaign."),
 ("gta-6-map-size", "How big is the GTA 6 map?", "Rockstar has given no official figure. The state of Leonida includes at least six regions shown in the trailers: Vice City, the Keys, Grassrivers, Port Gellhorn, Ambrosia and Mount Kalaga. Size comparisons online are fan estimates."),
 ("gta-6-delay", "Will GTA 6 be delayed again?", "The official date is November 19, 2026, after two delays (fall 2025, then May 26, 2026). Take-Two confirmed the date in its financial results. No new delay has been announced."),
 ]}
QT = {"fr": ("Question", "Réponse courte, vérifiée, avec la source. Mise à jour dès que Rockstar parle.", "Toutes les questions", "Faits vérifiés le"),
      "en": ("Question", "Short, verified answer with its source. Updated as soon as Rockstar speaks.", "All questions", "Facts checked on")}
for l, qs in Q.items():
    for slug, q, r in qs:
        url = f"{BASE}{'' if l == 'fr' else l + '/'}q/{slug}.html"
        autres = "".join(f'<li><a href="q/{s}.html">{e(qq)}</a></li>' for s, qq, _ in qs if s != slug)
        body = f"""
  <header class="tete-page rose"><div class="wrap"><span class="kicker">{e(QT[l][0])} · GTA 6</span><h1>{e(q)}</h1><p>{e(QT[l][1])}</p></div></header>
  <section class="papier"><div class="wrap">
    <p class="serif" style="font-size:clamp(1.3rem,2.4vw,1.9rem);max-width:60ch;line-height:1.35">{e(r)}</p>
    <p class="verifie" style="margin-top:28px">{e(QT[l][3])} <span data-verif></span> · <a href="https://www.rockstargames.com/VI" target="_blank" rel="noopener">Rockstar Games</a></p>
    <div class="boutons"><a class="btn" href="faq.html">FAQ</a><a class="btn clair" href="sortie.html">{e(T[l]['tz'])}</a></div>
  </div></section>
  <section><div class="wrap"><div class="rubrique rv"><span class="num">+</span><h2>{e(QT[l][2])}</h2></div><ul class="liste-q">{autres}</ul><div class="partage"></div></div></section>
"""
        ld = [{"@context": "https://schema.org", "@type": "FAQPage", "inLanguage": l, "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": r}}]},
              {"@context": "https://schema.org", "@type": "Article", "headline": q, "inLanguage": l, "dateModified": TODAY.isoformat(), "author": {"@type": "Organization", "name": "OKALAM Studio"}, "publisher": {"@type": "Organization", "name": "VI Countdown"}, "mainEntityOfPage": url}]
        write(("" if l == "fr" else l + "/") + f"q/{slug}.html", page(l, url, q + " | VI Countdown", r[:155], body, ld, img=BASE + f"assets/og/{l}/faq.jpg", page_shell="faq"))
        URLS.append((url, l, "0.7"))

# ------------------------------------------------------------------ 3. comparateur de prix
PRIX = {"fr": dict(t="Prix de GTA 6 : où l'acheter au meilleur prix", i="Les prix officiels par édition et les boutiques. Liens affiliés, même prix pour toi.",
                   rows=[("Édition standard", "79,99 €", "PS5, Xbox Series, boîte ou numérique"), ("Édition Ultimate", "99,99 €", "Numérique uniquement, PS5 et Xbox Series"), ("Coffret collector Vice City Collection", "399,99 €", "Sans le jeu : figurine, lunettes, casquette, sac, pin's, carte. Rockstar Store, un par personne, expédié à partir du 19 novembre")],
                   shops=[("Amazon.fr", "https://www.amazon.fr/s?k=GTA+6+PS5&tag=okalamstudio-21"), ("PlayStation Store", "https://store.playstation.com/fr-fr/search/grand%20theft%20auto%20vi"), ("Xbox Store", "https://www.xbox.com/fr-FR/search?q=grand%20theft%20auto%20vi"), ("Fnac", "https://www.fnac.com/SearchResult/ResultList.aspx?Search=gta+6"), ("Micromania", "https://www.micromania.fr/recherche?q=gta+6"), ("Leclerc", "https://www.e.leclerc/recherche?q=gta+6")],
                   note="Prix annoncés par Rockstar pour l'Europe. Les revendeurs peuvent proposer des remises ; cette page est mise à jour automatiquement."),
        "en": dict(t="GTA 6 price: where to buy it cheapest", i="Official prices per edition and the stores. Affiliate links, same price for you.",
                   rows=[("Standard edition", "€79.99 / £69.99", "PS5, Xbox Series, disc or digital"), ("Ultimate edition", "€99.99 / £89.99", "Digital only, PS5 and Xbox Series"), ("Vice City Collection collector box", "$399.99 / €399.99", "No game included: figure, sunglasses, cap, bag, pins, map. Rockstar Store, one per person, ships from November 19")],
                   shops=[("Amazon", "https://www.amazon.com/s?k=GTA+6+PS5&tag=okalamstudio-21"), ("PlayStation Store", "https://store.playstation.com/en-us/search/grand%20theft%20auto%20vi"), ("Xbox Store", "https://www.xbox.com/en-US/search?q=grand%20theft%20auto%20vi"), ("Best Buy", "https://www.bestbuy.com/site/searchpage.jsp?st=gta+6"), ("GAME (UK)", "https://www.game.co.uk/search?q=gta+6"), ("JB Hi-Fi (AU)", "https://www.jbhifi.com.au/search?query=gta+6")],
                   note="Prices announced by Rockstar. Retailers may discount; this page is updated automatically.")}
for l, p in PRIX.items():
    url = f"{BASE}{'' if l == 'fr' else l + '/'}prix.html"
    rows = "".join(f"<tr><td>{e(a)}</td><td><b>{e(b)}</b></td><td>{e(c)}</td></tr>" for a, b, c in p["rows"])
    shops = "".join(f'<a class="btn clair" href="{u}" target="_blank" rel="noopener sponsored">{e(n)}</a>' for n, u in p["shops"])
    body = f"""
  <header class="tete-page or"><div class="wrap"><span class="kicker">GTA 6 · 19.11.2026</span><h1>{e(p['t'])}</h1><p>{e(p['i'])}</p></div></header>
  <section class="papier"><div class="wrap">
    <div class="scroll-x rv"><table class="tableau"><tbody>{rows}</tbody></table></div>
    <div class="boutons">{shops}</div>
    <p class="verifie" style="margin-top:28px">{e(p['note'])} · <span data-verif></span></p>
    <div class="partage"></div>
  </div></section>
"""
    ld = [{"@context": "https://schema.org", "@type": "Product", "name": "Grand Theft Auto VI", "brand": {"@type": "Brand", "name": "Rockstar Games"},
           "offers": [{"@type": "Offer", "name": "Standard", "priceCurrency": "EUR", "price": "79.99", "availability": "https://schema.org/PreOrder", "url": url},
                      {"@type": "Offer", "name": "Ultimate", "priceCurrency": "EUR", "price": "99.99", "availability": "https://schema.org/PreOrder", "url": url}]}]
    write(("" if l == "fr" else l + "/") + "prix.html", page(l, url, p["t"] + " | VI Countdown", p["i"], body, ld, img=BASE + f"assets/og/{l}/acheter.jpg", page_shell="acheter"))
    URLS.append((url, l, "0.8"))

# ------------------------------------------------------------------ 4. article du jour J-n
def news(l, n=6):
    try: return json.load(open(f"data/news_{l}.json", encoding="utf-8"))[:n]
    except Exception: return []
AJ = {"fr": ("aujourdhui", f"J-{J} avant GTA 6 : le point du jour", f"Ce qui s'est passé aujourd'hui autour de GTA 6, à {J} jours de la sortie, et ce qui est confirmé.", "Dans la presse aujourd'hui", "Ce qui est sûr"),
      "en": ("today", f"{J} days until GTA 6: today's briefing", f"What happened around GTA 6 today, {J} days before launch, and what is confirmed.", "In the press today", "What is certain")}
AJ2 = {"fr": ("Ce que dit la communauté", "Nouveautés merch et collectors", "Le saviez-vous"), "en": ("What the community says", "New merch and collectors", "Did you know")}
FAITS = json.load(open("data/faits.json", encoding="utf-8"))
def liste(f, n=8):
    try: lst = json.load(open(f, encoding="utf-8"))[:n]
    except Exception: return ""
    return "".join(f'<li><span class="kicker">{e(a.get("s", ""))} · {e(a.get("d", ""))}</span><br><a href="{e(a["u"])}" target="_blank" rel="noopener">{e(a["t"])}</a></li>' for a in lst)
for l, (slug, t, i, h2, h3) in AJ.items():
    url = f"{BASE}{'' if l == 'fr' else l + '/'}{slug}.html"
    items = "".join(f'<li><span class="kicker">{e(a.get("src", ""))} · {e(a.get("d", ""))}</span><br><a href="{e(a["u"])}" target="_blank" rel="noopener">{e(a["t"])}</a></li>' for a in news(l))
    faits = T[l]
    body = f"""
  <header class="tete-page image"><img src="assets/jn{'-fr' if l == 'fr' else ''}.jpg" alt="J-{J}" width="1200" height="630"><div class="wrap"><span class="kicker">{e(TODAY.isoformat())}</span><h1>{e(t)}</h1><p>{e(i)}</p></div></header>
  <section class="papier"><div class="wrap"><div class="rubrique rv"><span class="num">01</span><h2>{e(h2)}</h2></div><ul class="liste-q">{items}</ul></div></section>
  <section><div class="wrap"><div class="rubrique rv"><span class="num">02</span><h2>{e(h3)}</h2></div>
    <div class="scroll-x rv"><table class="tableau"><tbody><tr><td>{e(faits['pre'])}</td><td>{e(faits['pre_v'])}</td></tr><tr><td>{e(faits['plat'])}</td><td>{e(faits['plat_v'])}</td></tr></tbody></table></div>
    <div class="boutons"><a class="btn" href="sortie.html">{e(faits['tz'])}</a><a class="btn clair" href="actus.html">Actus</a></div></div></section>
  <section class="papier"><div class="wrap"><div class="rubrique rv"><span class="num">03</span><h2>{e(AJ2[l][0])}</h2></div><ul class="liste-q">{liste("data/communaute.json")}</ul></div></section>
  <section><div class="wrap"><div class="rubrique rv"><span class="num">04</span><h2>{e(AJ2[l][1])}</h2></div><ul class="liste-q">{liste(f"data/merch_{l}.json")}</ul>
    <p class="fait" style="margin-top:36px"><span class="kicker">{e(AJ2[l][2])}</span>{e(FAITS[l][TODAY.toordinal() % len(FAITS[l])])}</p><div class="partage"></div></div></section>
"""
    ld = [{"@context": "https://schema.org", "@type": "NewsArticle", "headline": t, "description": i, "inLanguage": l, "datePublished": TODAY.isoformat() + "T06:00:00+01:00", "dateModified": datetime.datetime.now().isoformat(timespec="seconds"),
           "image": [BASE + f"assets/jn{'-fr' if l == 'fr' else ''}.jpg"], "author": {"@type": "Organization", "name": "OKALAM Studio"}, "publisher": {"@type": "Organization", "name": "VI Countdown", "logo": {"@type": "ImageObject", "url": BASE + "assets/icon-512.png"}}, "mainEntityOfPage": url}]
    write(("" if l == "fr" else l + "/") + f"{slug}.html", page(l, url, t + " | VI Countdown", i, body, ld, img=BASE + f"assets/jn{'-fr' if l == 'fr' else ''}.jpg", page_shell="actus"))
    URLS.append((url, l, "0.9"))


# ------------------------------------------------------------------ 4b. journal : articles rédigés (data/articles.json)
ARTS = json.load(open("data/articles.json", encoding="utf-8")) if os.path.exists("data/articles.json") else []
I18N = {l: json.load(open(f"tools/i18n/{l}.json", encoding="utf-8")) for l in T}
def tr(l, k): return I18N.get(l, {}).get(k) or I18N["en"].get(k) or I18N["fr"].get(k, k)
def art_cle(l): return "idn" if l == "id" else l  # "id" est déjà le champ identifiant de chaque article
def art_lang(a, l): return art_cle(l) if isinstance(a.get(art_cle(l)), dict) else ("en" if isinstance(a.get("en"), dict) else "fr")
def art_url(a, l): return f"{BASE}{'' if l == 'fr' else l + '/'}journal/{a['id']}.html"
def d_fmt(a, l):
    try: return fmt_local(datetime.datetime.fromisoformat(a["date"]), l)
    except Exception: return a.get("date", "")[:10]
for l in T:
    cartes = []
    for a in ARTS:
        al = art_lang(a, l); x = a[al]
        cartes.append(f'<a class="jr-carte rv" href="journal/{a["id"]}.html"><img src="{e(a.get("img") or BASE + "assets/jn.jpg")}" alt="" loading="lazy" width="640" height="360"><span class="k">{e(d_fmt(a, l))}</span><b>{e(x["t"])}</b><p>{e(x["d"])}</p></a>')
        body = f"""
  <header class="tete-page jr-tete"><div class="wrap"><span class="kicker"><span class="direct"><i></i>{e(tr(l, "direct"))}</span> · {e(d_fmt(a, l))}</span><h1>{e(x["t"])}</h1><p class="serif">{e(x["d"])}</p></div></header>
  <section class="papier"><div class="wrap jr-corps">{x["h"]}
    <p class="jr-sources"><b>{e(tr(l, "jr_src"))}</b> {" · ".join(f'<a href="{e(u)}" target="_blank" rel="noopener">{e(u.split("/")[2])}</a>' for u in a.get("src", []))}</p>
    <p class="note jr-signature">{e(tr(l, "jr_auteur"))}</p><div class="partage"></div>
    <div class="boutons"><a class="btn" href="journal.html">{e(tr(l, "jr_suite"))}</a><a class="btn clair" href="actus.html">{e(tr(l, "nav_news"))}</a></div></div></section>
"""
        ld = [{"@context": "https://schema.org", "@type": "NewsArticle", "headline": x["t"], "description": x["d"], "inLanguage": l, "datePublished": a["date"], "dateModified": a.get("maj", a["date"]), "image": [a.get("img") or BASE + "assets/jn.jpg"], "mainEntityOfPage": art_url(a, l),
               "author": {"@type": "Person", "name": "Solange Rocheval", "url": BASE + "apropos.html"}, "publisher": {"@type": "Organization", "name": "VI Countdown", "logo": {"@type": "ImageObject", "url": BASE + "assets/icon-192.png"}}}]
        write(("" if l == "fr" else l + "/") + f"journal/{a['id']}.html", page(l, art_url(a, l), x["t"] + " | VI Countdown", x["d"], body, ld, img=a.get("img"), page_shell="actus"))
        URLS.append((art_url(a, l), l, "0.9"))
    body = f"""
  <header class="tete-page jr-tete"><div class="wrap"><span class="kicker"><span class="direct"><i></i>{e(tr(l, "direct"))}</span> · {e(tr(l, "direct_i"))}</span><h1>{e(tr(l, "jr_h1"))}</h1><p class="serif">{e(tr(l, "jr_i"))}</p></div></header>
  <section class="papier"><div class="wrap"><div class="jr-grille">{"".join(cartes)}</div><div class="partage"></div></div></section>
"""
    url = f"{BASE}{'' if l == 'fr' else l + '/'}journal.html"
    ld = [{"@context": "https://schema.org", "@type": "CollectionPage", "name": tr(l, "mt_journal"), "url": url, "inLanguage": l}]
    write(("" if l == "fr" else l + "/") + "journal.html", page(l, url, tr(l, "mt_journal"), tr(l, "md_journal"), body, ld, page_shell="actus"))
    URLS.append((url, l, "0.9"))

# ------------------------------------------------------------------ 5. sitemap, images, robots, feed
sm = open("sitemap.xml", encoding="utf-8").read()
ajout = "".join(f"  <url><loc>{u}</loc><lastmod>{TODAY.isoformat()}</lastmod><changefreq>daily</changefreq><priority>{p}</priority></url>\n" for u, l, p in URLS)
sm = sm.replace("</urlset>", ajout + "</urlset>")
open("sitemap.xml", "w", encoding="utf-8").write(sm)

imgs = sorted(set(f"assets/og/{f.split('/')[-2]}/{f.split('/')[-1]}" for f in __import__("glob").glob("assets/og/*/*.jpg")))
sx = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">',
      f"  <url><loc>{BASE}</loc><image:image><image:loc>{BASE}assets/jn-fr.jpg</image:loc><image:caption>J-{J} GTA 6</image:caption></image:image><image:image><image:loc>{BASE}assets/jn.jpg</image:loc></image:image><image:image><image:loc>{BASE}assets/badge.png</image:loc></image:image></url>"]
for im in imgs:
    l, pg = im.split("/")[2], im.split("/")[3][:-4]
    sx.append(f"  <url><loc>{BASE}{'' if l == 'fr' else l + '/'}{'' if pg == 'index' else pg + '.html'}</loc><image:image><image:loc>{BASE}{im}</image:loc></image:image></url>")
open("sitemap-images.xml", "w", encoding="utf-8").write("\n".join(sx + ["</urlset>", ""]))
rb = open("robots.txt", encoding="utf-8").read()
if "sitemap-images.xml" not in rb: open("robots.txt", "a", encoding="utf-8").write(f"Sitemap: {BASE}sitemap-images.xml\n")

fx = open("feed.xml", encoding="utf-8").read()
if 'rel="hub"' not in fx:
    fx = fx.replace("<channel>", '<channel>\n<atom:link rel="hub" href="https://pubsubhubbub.appspot.com/"/>', 1)
    if 'xmlns:atom' not in fx: fx = fx.replace("<rss ", '<rss xmlns:atom="http://www.w3.org/2005/Atom" ', 1)
t_fr, i_fr = AJ["fr"][1], AJ["fr"][2]
item = f"<item><title>{e(t_fr)}</title><link>{BASE}aujourdhui.html</link><guid>{BASE}aujourdhui.html#{TODAY.isoformat()}</guid><pubDate>{datetime.datetime.now(datetime.timezone.utc).strftime('%a, %d %b %Y %H:%M:%S +0000')}</pubDate><description>{e(i_fr)}</description></item>\n"
fx = re.sub(r"<item>", item + "<item>", fx, count=1)
for a in reversed(ARTS[:10]):
    if a["id"] not in fx:
        x = a[art_lang(a, "fr")]
        try: pd = datetime.datetime.fromisoformat(a["date"]).astimezone(datetime.timezone.utc).strftime('%a, %d %b %Y %H:%M:%S +0000')
        except Exception: pd = datetime.datetime.now(datetime.timezone.utc).strftime('%a, %d %b %Y %H:%M:%S +0000')
        fx = re.sub(r"<item>", f"<item><title>{e(x['t'])}</title><link>{art_url(a, 'fr')}</link><guid>{art_url(a, 'fr')}</guid><pubDate>{pd}</pubDate><description>{e(x['d'])}</description></item>\n<item>", fx, count=1)
open("feed.xml", "w", encoding="utf-8").write(fx)
print(f"pub: {len(URLS)} pages (J-{J})")
