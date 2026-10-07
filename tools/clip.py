#!/usr/bin/env python3
"""Clip vertical 1080x1920 de 8 s (Shorts, TikTok, Reels) à partir de l'affiche du jour.
   Sortie : assets/clip-fr.mp4, assets/clip-en.mp4 (hors git). Lancé chaque matin sur le serveur (cron)."""
import datetime, os, subprocess
from PIL import Image, ImageDraw, ImageFont
J = (datetime.date(2026, 11, 19) - datetime.date.today()).days
FONT = "tools/fonts/Anton-Regular.ttf"
for l, src, txt in (("fr", "assets/jn-fr.jpg", "gtavifrance.com"), ("en", "assets/jn.jpg", "gtavifrance.com/en")):
    im = Image.open(src).convert("RGB")
    w, h = im.size; s = max(1080 / w, 1920 / h)
    im = im.resize((round(w * s), round(h * s)), Image.LANCZOS)
    x0, y0 = (im.width - 1080) // 2, (im.height - 1920) // 2
    im = im.crop((x0, y0, x0 + 1080, y0 + 1920))
    d = ImageDraw.Draw(im); f = ImageFont.truetype(FONT, 56)
    tw = d.textlength(txt, font=f)
    d.rectangle((0, 1920 - 230, 1080, 1920 - 110), fill=(22, 17, 29))
    d.text(((1080 - tw) / 2, 1920 - 212), txt, font=f, fill=(242, 232, 213))
    frame = f"/tmp/clip-{l}.png"; im.save(frame)
    out = f"assets/clip-{l}.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-loop", "1", "-i", frame, "-t", "8",
                    "-vf", "zoompan=z='min(zoom+0.0008,1.12)':d=200:s=1080x1920:fps=25", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", "25", "-movflags", "+faststart", out], check=True)
    os.remove(frame); print(out, os.path.getsize(out) // 1024, "ko")
