# Être cité par les IA (GEO) — mécanique et règles, 22/10/2026

| IA | Index de recherche | Robot | Levier |
|---|---|---|---|
| ChatGPT | Bing (+ son propre OAI-SearchBot) | OAI-SearchBot, ChatGPT-User | Bing Webmaster + IndexNow (fait) |
| Gemini | Google | Googlebot | Search Console, classement Google |
| Claude | Brave Search | Claude-SearchBot, Claude-User | search.brave.com/submit-url (fait 22/10, 11 pages) |
| Grok | X + web | xAI-SearchBot, GrokBot | posts @gtavifrancecom avec lien, mentions sur X |

Comment elles choisissent : l'IA reformule la question en 2-4 requêtes web, prend les 5-10 premiers résultats, garde ceux dont le TITRE et le PREMIER PARAGRAPHE répondent mot pour mot, récents et datés.

Règles d'écriture appliquées au site :
1. Titre = la question des gens + la réponse (« Heure de sortie de GTA 6 en France : minuit, le 19 novembre »).
2. Première phrase visible = réponse courte complète, chiffres compris.
3. Date de mise à jour visible + dateModified JSON-LD ; FAQPage sur les pages pratiques.
4. Entité claire : NewsMediaOrganization + sameAs (X, Discord) sur l'accueil ; « site d'actualité GTA 6 en français » dans titre et description.
5. Être mentionné ailleurs (listes « meilleurs sites », X, presse) : c'est ce qui manque pour la question « meilleur site ».

Mesure : tâche gtavifrance-test-ia (lundi 10 h), résultats dans docs/TEST_IA.md. 22/10 : 0/4.
