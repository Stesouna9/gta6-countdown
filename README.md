# VI Countdown — gtavifrance.com

Independent GTA 6 countdown and fact page in 17 languages (French, English, Spanish, Portuguese, German, Italian, Japanese, Chinese, Arabic, Hindi, Russian, Korean, Turkish, Indonesian, Polish, Vietnamese). Release time in 45 countries, verified facts with sources, news updated twice a day, free widget for streams.

Live: https://gtavifrance.com/ · English: https://gtavifrance.com/en/

## Free public API (no key)

`GET https://gtavifrance.com/api/gta6.json`

```json
{ "release": "2026-11-19", "preload": "2026-11-12", "days_left": 43, "platforms": ["PS5", "Xbox Series X|S"], "updated": "..." }
```

Cached 30 minutes. Please link back to gtavifrance.com if you use it.

## Embeds

- Widget (iframe or OBS browser source, `?t=1` for transparent background): `https://gtavifrance.com/widget.html`
- Daily badge (PNG, updated automatically): `https://gtavifrance.com/assets/badge.png`
- RSS: `https://gtavifrance.com/feed.xml` · ICS calendar: `https://gtavifrance.com/gta6.ics`

## How it is built

Static site. `tools/update.py` fetches news, `tools/images.py` renders the daily poster, `tools/prerender.py` generates one HTML copy per language with structured data, `tools/pub.py` generates country, question and daily pages. A GitHub Action runs it twice a day and pings IndexNow and WebSub.

Made by OKALAM Studio, Nantes. Fan site, not affiliated with Rockstar Games or Take-Two Interactive.
