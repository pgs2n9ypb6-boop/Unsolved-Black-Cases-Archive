#!/usr/bin/env python3
"""
Rough-draft social cards (1080x1350 PNG, portrait) for every case, in a
comic-panel style aimed at a younger audience. Built ONLY from the case's own
verified text in data/cases.json. No AI-generated faces or likenesses: the
portrait panel is typographic (initials + years), never a drawn person.

Usage: python3 generate_social_cards.py [case-id ...]   (default: all)
Output: social/cases/<id>.png
"""
import json, os, re, sys, html
from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.abspath(__file__))
CASES = json.load(open(os.path.join(ROOT, "data", "cases.json")))
if isinstance(CASES, dict):
    CASES = CASES.get("cases", CASES)
OUT = os.path.join(ROOT, "social", "cases")
os.makedirs(OUT, exist_ok=True)

PHOTOS = os.path.join(ROOT, "social", "photos")
os.makedirs(PHOTOS, exist_ok=True)
try:
    CREDITS = json.load(open(os.path.join(PHOTOS, "credits.json")))
except Exception:
    CREDITS = {}


def photo_for(c):
    """Optional portrait. ONLY real, rights-cleared photos are ever used:
    social/photos/<id>.(jpg|jpeg|png|webp) AND an entry in
    social/photos/credits.json {"<id>": "Photo: family of X, used with permission"}.
    A photo without a credit line is ignored (with a warning)."""
    import base64, mimetypes
    for ext in ("jpg", "jpeg", "png", "webp"):
        f = os.path.join(PHOTOS, f"{c['id']}.{ext}")
        if os.path.exists(f):
            if not CREDITS.get(c["id"]):
                print("SKIPPED photo (no credit in credits.json):", c["id"])
                return None, None
            mime = mimetypes.guess_type(f)[0] or "image/jpeg"
            return "data:%s;base64,%s" % (mime, base64.b64encode(open(f, "rb").read()).decode()), CREDITS[c["id"]]
    return None, None


STATUS = {"unsolved": "UNSOLVED", "unresolved": "NO CONVICTION"}


def clip(text, limit):
    """Trim to whole sentences within `limit` chars; fall back to a word cut."""
    text = re.sub(r"\s+", " ", text or "").strip()
    if len(text) <= limit:
        return text
    sents = re.split(r"(?<=[.?!])\s+(?=[A-Z“\"])", text)
    out = ""
    for s in sents:
        if len(out) + len(s) + (1 if out else 0) <= limit:
            out = (out + " " + s).strip()
        else:
            break
    if out:
        return out
    cut = text[:limit].rsplit(" ", 1)[0].rstrip(",;:")
    return cut + "…"


def initials(name):
    name = re.split(r"[,&]", name)[0]
    parts = [p for p in re.split(r"[\s\"“”()]+", name) if p and p[0].isalpha()]
    return (parts[0][0] + (parts[-1][0] if len(parts) > 1 else "")).upper()


def hook(c):
    n = c["name"].split(" (")[0]
    if len(n) > 24:
        return "WHO KILLED THEM?" if c["status"] == "unsolved" else "WHO IS ACCOUNTABLE?"
    return f"WHAT HAPPENED TO {n.upper()}?" if c["caseType"] == "missing_persons" and c["status"] != "unresolved" \
        else (f"WHO KILLED {n.upper()}?" if c["status"] == "unsolved" else f"WHO IS ACCOUNTABLE FOR {n.upper()}’S DEATH?")


def card(c):
    e = html.escape
    where = ", ".join(x for x in [c.get("city"), c.get("state")] if x)
    age = f"AGE {c['age']}" if c.get("age") else ""
    kind = "MISSING" if c["caseType"] == "missing_persons" else "KILLED"
    q = (c.get("unanswered") or [""])[0]
    photo, credit = photo_for(c)
    photo_html = (f'<div class="ph"><img src="{photo}"><div class="cr">{e(credit)}</div></div>' if photo else "")
    ini_html = "" if photo else f'<div class="ini">{e(initials(c["name"]))}</div>'
    maxw = 640 if photo else 780
    name = c["name"]
    nsize = 112 if len(name) <= 14 else 92 if len(name) <= 22 else 72 if len(name) <= 34 else 56
    return f'''<!doctype html><meta charset="utf-8"><style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{width:1080px;height:1350px;overflow:hidden;background:#0d1117;
 font-family:"DejaVu Sans Condensed","DejaVu Sans",sans-serif;color:#f3ead7;position:relative}}
.dots{{position:absolute;inset:0;background-image:radial-gradient(rgba(243,234,215,.07) 2px,transparent 2.5px);background-size:18px 18px}}
.p{{position:absolute;border:6px solid #f3ead7;overflow:hidden;padding:30px 34px}}
.tag{{font-family:"DejaVu Sans Mono",monospace;font-size:26px;letter-spacing:4px;font-weight:700;margin-bottom:14px}}
#a{{left:30px;top:30px;width:1020px;height:470px;background:#7d1a24;transform:rotate(-.6deg)}}
#a .big{{font-size:{nsize}px;line-height:.98;font-weight:700;text-transform:uppercase;letter-spacing:1px;margin-top:6px;max-width:{maxw}px}}
#a .meta{{max-width:{maxw}px;font-size:38px;margin-top:24px;font-weight:700;color:#f6c9a0}}
#a .ini{{position:absolute;right:20px;bottom:-60px;font-size:300px;z-index:0;font-weight:700;color:rgba(243,234,215,.14);line-height:1}}
#a .yr{{position:absolute;right:34px;top:26px;font-size:34px;font-family:"DejaVu Sans Mono",monospace;background:#f3ead7;color:#7d1a24;padding:6px 16px;font-weight:700}}
#a .ph{{position:absolute;right:34px;top:90px;width:300px;height:330px;border:5px solid #f3ead7;background:#000}}
#a .ph img{{width:100%;height:100%;object-fit:cover;display:block}}
#a .ph .cr{{position:absolute;left:0;right:0;bottom:0;background:rgba(13,17,23,.85);font-size:15px;padding:4px 8px;line-height:1.2}}
#a .yr{{z-index:2}}
#b{{left:30px;top:520px;width:1020px;height:330px;background:#17324a;transform:rotate(.4deg)}}
#b .t{{font-size:38px;line-height:1.28;font-weight:600}}
#c{{left:30px;top:870px;width:1020px;height:290px;background:#f3ead7;color:#0d1117;transform:rotate(-.3deg)}}
#c .tag{{color:#7d1a24}}
#c .t{{font-size:38px;line-height:1.26;font-weight:700}}
#d{{left:30px;top:1180px;width:1020px;height:140px;background:#0d1117;display:flex;align-items:center;justify-content:space-between;padding:0 34px}}
#d .h{{font-size:{44 if len(hook(c))<34 else 36}px;font-weight:700;color:#f6c9a0;max-width:640px;line-height:1.05}}
#d .u{{text-align:right;font-family:"DejaVu Sans Mono",monospace;font-size:24px;line-height:1.4}}
.badge{{display:inline-block;background:#f3ead7;color:#7d1a24;padding:4px 14px;font-weight:700;letter-spacing:3px;font-family:"DejaVu Sans Mono",monospace;font-size:26px}}
</style><div class="dots"></div>
<div class="p" id="a"><div class="yr">{c['year']}</div>
 <div class="tag">CASE #{e(str(c['caseNumber']))} &middot; {kind}</div>
 <div class="big">{e(name)}</div>
 <div class="meta">{e(where.upper())}{(" &middot; " + age) if age else ""}</div>
 {ini_html}{photo_html}</div>
<div class="p" id="b"><div class="tag" style="color:#f6c9a0">WHAT WE KNOW</div><div class="t">{e(clip(c['summary'], 270))}</div></div>
<div class="p" id="c"><div class="tag">STILL UNANSWERED</div><div class="t">{e(clip(q, 190))}</div></div>
<div class="p" id="d"><div class="h">{e(hook(c))}</div>
 <div class="u"><span class="badge">{STATUS.get(c['status'],'')}</span><br>unsolvedblackcases.com</div></div>
'''


def main():
    ids = set(sys.argv[1:])
    todo = [c for c in CASES if not ids or c["id"] in ids]
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 1080, "height": 1350})
        for c in todo:
            pg.set_content(card(c))
            over = pg.evaluate("""() => {
              const bad = [];
              for (const id of ['b','c']) {
                const p = document.getElementById(id), t = p.querySelector('.t');
                let fs = parseFloat(getComputedStyle(t).fontSize);
                while (p.scrollHeight > p.clientHeight + 2 && fs > 24) { fs -= 2; t.style.fontSize = fs + 'px'; }
                if (p.scrollHeight > p.clientHeight + 2) bad.push(id);
              }
              const a = document.getElementById('a'), big = a.querySelector('.big'), m = a.querySelector('.meta');
              if (big.getBoundingClientRect().bottom > m.getBoundingClientRect().top - 4) bad.push('a');
              return bad;
            }""")
            if over:
                print("OVERFLOW", c["id"], over)
            pg.screenshot(path=os.path.join(OUT, c["id"] + ".png"))
        b.close()
    print("wrote", len(todo), "cards to", OUT)


main()
