#!/usr/bin/env python3
"""
Generates Open Graph / Twitter Card preview images (1200x630 PNG) for every
page on the site, using the same dark/crimson design system as the site
itself. Run after build.py (needs data/cases.json).

Output: og/cases/<id>.png (one per case) + og/site.png (shared fallback for
every non-case page) + og/freeway-phantom.png (the series page).

Note: rendered in a sandboxed environment without access to Google Fonts, so
these use close local system-font fallbacks (Bitstream Charter / DejaVu Sans
Mono) rather than the site's actual Fraunces/IBM Plex Mono. Re-run this
script from a machine with normal internet access to regenerate with the
real brand fonts if you want a pixel-perfect match.
"""
import json, os, html
from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.abspath(__file__))
CASES = json.load(open(os.path.join(ROOT, "data", "cases.json")))
STATUS_LABEL = {"unsolved": "Unsolved", "cold": "Cold Case", "missing_persons": "Missing Persons"}

CARD_CSS = '''
*{box-sizing:border-box;margin:0;padding:0;}
body{
  width:1200px;height:630px;overflow:hidden;
  background:
    radial-gradient(900px 500px at 15% -10%, rgba(179,32,47,0.14), transparent 60%),
    radial-gradient(700px 400px at 100% 0%, rgba(79,127,146,0.10), transparent 55%),
    #08090b;
  font-family:"Bitstream Charter", Georgia, serif;
  color:#ece9e4;
  display:flex; flex-direction:column; justify-content:space-between;
  padding:56px 64px;
}
.mono{ font-family:"DejaVu Sans Mono", monospace; }
.brand{ display:flex; align-items:center; gap:14px; }
.monogram{
  width:44px; height:44px; border:2px solid #b3202f; color:#d43d4c;
  display:flex; align-items:center; justify-content:center;
  font-family:"DejaVu Sans Mono", monospace; font-size:16px; font-weight:700;
  border-radius:4px; background:rgba(179,32,47,0.08);
}
.brand-name{ font-family:"DejaVu Sans Mono", monospace; font-size:19px; letter-spacing:2px; color:#ece9e4; font-weight:700; }
.main-row{ display:flex; align-items:center; gap:48px; flex:1; }
.text-col{ flex:1; min-width:0; }
.eyebrow{ font-family:"DejaVu Sans Mono", monospace; font-size:19px; letter-spacing:3px; color:#d43d4c; text-transform:uppercase; margin-bottom:18px; }
.case-name{ font-size:64px; line-height:1.08; font-weight:700; margin-bottom:22px; }
.meta-row{ display:flex; align-items:center; gap:18px; flex-wrap:wrap; }
.badge{
  font-family:"DejaVu Sans Mono", monospace; font-size:17px; letter-spacing:1.5px; text-transform:uppercase;
  padding:8px 16px; border-radius:3px; font-weight:700;
  border:2px solid #d43d4c; color:#d43d4c; background:rgba(179,32,47,0.10);
}
.badge.cold{ border-color:#4f7f92; color:#4f7f92; background:rgba(79,127,146,0.10); }
.badge.missing_persons{ border-color:#b98a3d; color:#b98a3d; background:rgba(185,138,61,0.10); }
.meta-text{ font-family:"DejaVu Sans Mono", monospace; font-size:20px; color:#9c9b9d; }
.photo-col{ flex:none; width:340px; height:340px; border-radius:6px; border:2px solid rgba(236,233,228,0.16); overflow:hidden; display:flex; }
.photo-col img{ width:100%; height:100%; object-fit:cover; }
.photo-col.placeholder{ align-items:center; justify-content:center; background:linear-gradient(135deg, rgba(179,32,47,0.18), rgba(185,138,61,0.10)); font-size:120px; font-weight:700; color:#ece9e4; }
.photo-col.two{ width:520px; flex-direction:row; gap:6px; }
.photo-col.two > div{ width:calc(50% - 3px); height:100%; border-radius:4px; overflow:hidden; }
.photo-col.two img{ width:100%; height:100%; object-fit:cover; }
.tagline{ font-size:30px; color:#9c9b9d; line-height:1.35; max-width:900px; }
.footer-line{ display:flex; align-items:center; justify-content:space-between; font-family:"DejaVu Sans Mono", monospace; font-size:17px; color:#6b6a6d; letter-spacing:1px; border-top:1px solid rgba(236,233,228,0.10); padding-top:22px; }
'''

def initials_for(name):
    stop = {"and", "&", "jr", "sr", "iii", "ii"}
    tokens = [t.strip(".") for t in name.split() if t.strip(".").lower() not in stop and len(t.strip(".")) > 1]
    if not tokens:
        return "?"
    if len(tokens) == 1:
        return tokens[0][0].upper()
    return (tokens[0][0] + tokens[-1][0]).upper()

def photo_html(c):
    photos = c.get("victimPhotos") or []
    if len(photos) == 1:
        return f'<div class="photo-col"><img src="{html.escape(photos[0]["url"])}"></div>'
    if len(photos) >= 2:
        imgs = "".join(f'<div><img src="{html.escape(p["url"])}"></div>' for p in photos[:2])
        return f'<div class="photo-col two">{imgs}</div>'
    return f'<div class="photo-col placeholder">{initials_for(c["name"])}</div>'

def case_card_html(c):
    status = c["status"]
    label = STATUS_LABEL.get(status, "Unsolved")
    meta = f'{c["year"] or "Year not available"} \u00b7 {(c.get("city") or "")}{", " + c["state"] if c.get("state") else ""}'
    return f'''<html><head><style>{CARD_CSS}</style></head><body>
  <div class="brand"><div class="monogram">UBCA</div><div class="brand-name">UNSOLVED BLACK CASES ARCHIVE</div></div>
  <div class="main-row">
    <div class="text-col">
      <div class="eyebrow">Case File #{c['caseNumber']}</div>
      <div class="case-name">{html.escape(c['name'])}</div>
      <div class="meta-row">
        <span class="badge {status}">{label}</span>
        <span class="meta-text">{html.escape(meta)}</span>
      </div>
    </div>
    {photo_html(c)}
  </div>
  <div class="footer-line"><span>PUBLIC-RECORD RESEARCH ARCHIVE</span><span>unsolved-black-cases-archive.vercel.app</span></div>
</body></html>'''

def generic_card_html(eyebrow, title, tagline):
    return f'''<html><head><style>{CARD_CSS}</style></head><body>
  <div class="brand"><div class="monogram">UBCA</div><div class="brand-name">UNSOLVED BLACK CASES ARCHIVE</div></div>
  <div class="main-row">
    <div class="text-col">
      <div class="eyebrow">{html.escape(eyebrow)}</div>
      <div class="case-name" style="font-size:56px;">{html.escape(title)}</div>
      <div class="tagline">{html.escape(tagline)}</div>
    </div>
  </div>
  <div class="footer-line"><span>PUBLIC-RECORD RESEARCH ARCHIVE</span><span>unsolved-black-cases-archive.vercel.app</span></div>
</body></html>'''

def freeway_phantom_html():
    return f'''<html><head><style>{CARD_CSS}</style></head><body>
  <div class="brand"><div class="monogram">UBCA</div><div class="brand-name">UNSOLVED BLACK CASES ARCHIVE</div></div>
  <div class="main-row">
    <div class="text-col">
      <div class="eyebrow">Case Series</div>
      <div class="case-name">The Freeway Phantom</div>
      <div class="meta-row">
        <span class="badge unsolved">Unsolved</span>
        <span class="meta-text">1971\u20131972 \u00b7 Washington, D.C. \u00b7 6 victims</span>
      </div>
    </div>
  </div>
  <div class="footer-line"><span>PUBLIC-RECORD RESEARCH ARCHIVE</span><span>unsolved-black-cases-archive.vercel.app</span></div>
</body></html>'''

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1200, "height": 630})

        for c in CASES:
            page.set_content(case_card_html(c))
            page.wait_for_timeout(150)
            out = os.path.join(ROOT, "og", "cases", f"{c['id']}.png")
            page.screenshot(path=out)
            print("wrote", os.path.relpath(out, ROOT))

        page.set_content(freeway_phantom_html())
        page.wait_for_timeout(150)
        out = os.path.join(ROOT, "og", "freeway-phantom.png")
        page.screenshot(path=out)
        print("wrote", os.path.relpath(out, ROOT))

        page.set_content(generic_card_html(
            "Public-Record Research Archive",
            "Unsolved Black Cases Archive",
            "Documenting unsolved cases involving Black victims. Seeking answers, amplifying overlooked stories."))
        page.wait_for_timeout(150)
        out = os.path.join(ROOT, "og", "site.png")
        page.screenshot(path=out)
        print("wrote", os.path.relpath(out, ROOT))

        browser.close()

if __name__ == "__main__":
    main()
