#!/usr/bin/env python3
"""
"Visual Story" cards (1408x768 PNG, landscape comic-panel style) for every case.

Everything factual on a card (name, age, year, place, summary sentence, status,
unanswered question) is pulled from data/cases.json, i.e. the case's own
verified text. The artwork is SYMBOLIC: scene illustrations chosen by keyword
from the case text (road, river, house, police car, ...), plus a faceless
silhouette in the portrait panel. No real person's face or likeness is drawn,
and no violence is depicted. Every card carries the line:
  "Illustrations are symbolic, drawn to give a visual sense of the story.
   They are not depictions of the real people or events."

Usage: python3 generate_story_cards.py [case-id ...]    (default: all)
Output: social/story/<id>.png
"""
import json, os, re, sys, html
from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.abspath(__file__))
CASES = json.load(open(os.path.join(ROOT, "data", "cases.json")))
if isinstance(CASES, dict):
    CASES = CASES.get("cases", CASES)
OUT = os.path.join(ROOT, "social", "story")
os.makedirs(OUT, exist_ok=True)

DOMAIN = "unsolvedblackcases.com"
STATUS_BADGE = {"unsolved": "UNSOLVED", "unresolved": "NO CONVICTION"}


# ----------------------------------------------------------------- text utils
def clip(text, limit):
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
    return text[:limit].rsplit(" ", 1)[0].rstrip(",;:") + "…"


# --------------------------------------------------------------- SVG scenery
# Each motif draws into a 400x260 box. Palette is shared with the site.
SKY = '''<defs><linearGradient id="sk" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0b1626"/><stop offset="1" stop-color="#2b3f5c"/></linearGradient></defs>
<rect width="400" height="260" fill="url(#sk)"/><circle cx="330" cy="50" r="22" fill="#f3ead7"/><circle cx="338" cy="44" r="20" fill="#14243a" opacity=".35"/>
<g fill="#f3ead7" opacity=".7"><circle cx="40" cy="30" r="1.6"/><circle cx="110" cy="55" r="1.4"/><circle cx="190" cy="22" r="1.8"/><circle cx="250" cy="60" r="1.3"/><circle cx="60" cy="90" r="1.2"/></g>'''


def car(x, y, s=1.0, fill="#1a1a22", lights=False):
    g = f'<g transform="translate({x},{y}) scale({s})">'
    g += f'<path d="M0 40 L12 40 L28 14 Q32 8 40 8 L96 8 Q106 8 112 16 L128 36 L150 40 Q158 42 158 50 L158 58 L0 58 Z" fill="{fill}"/>'
    g += '<path d="M36 16 L46 16 L46 36 L22 36 Z M54 16 L96 16 L112 36 L54 36 Z" fill="#8fb4cf" opacity=".55"/>'
    g += '<circle cx="36" cy="60" r="13" fill="#0a0a0f"/><circle cx="36" cy="60" r="5" fill="#777"/><circle cx="122" cy="60" r="13" fill="#0a0a0f"/><circle cx="122" cy="60" r="5" fill="#777"/>'
    if lights:
        g += '<rect x="56" y="0" width="22" height="9" rx="3" fill="#e0242f"/><rect x="82" y="0" width="22" height="9" rx="3" fill="#2f7be0"/>'
        g += '<circle cx="67" cy="4" r="26" fill="#e0242f" opacity=".25"/><circle cx="93" cy="4" r="26" fill="#2f7be0" opacity=".25"/>'
    return g + '</g>'


def m_road(): return SKY + '<polygon points="0,170 400,150 400,260 0,260" fill="#14161c"/><polygon points="0,200 400,185 400,198 0,215" fill="#22252d"/><g fill="#d9b24a"><rect x="30" y="206" width="40" height="4"/><rect x="130" y="203" width="40" height="4"/><rect x="230" y="199" width="40" height="4"/></g>' + car(120, 130, 1.25)
def m_police(): return SKY + '<polygon points="0,170 400,160 400,260 0,260" fill="#14161c"/><g fill="#d9b24a"><rect x="30" y="214" width="40" height="4"/><rect x="150" y="211" width="40" height="4"/></g>' + car(110, 125, 1.35, "#222b38", True)
def m_house(): return SKY + '<rect y="190" width="400" height="70" fill="#101a12"/><polygon points="90,110 200,50 310,110" fill="#2a1f1c"/><rect x="105" y="108" width="190" height="95" fill="#3a2b27"/><rect x="130" y="130" width="42" height="36" fill="#f0c25a"/><rect x="228" y="130" width="42" height="36" fill="#f0c25a" opacity=".35"/><rect x="186" y="148" width="28" height="55" fill="#171010"/><polygon points="20,190 40,110 60,190" fill="#0b1c10"/><polygon points="345,190 365,120 385,190" fill="#0b1c10"/>'
def m_water():
    w = ''.join(f'<path d="M0 {180+i*22} Q50 {170+i*22} 100 {180+i*22} T200 {180+i*22} T300 {180+i*22} T400 {180+i*22}" stroke="#7fb0d0" stroke-width="3" fill="none" opacity="{.8-i*.2}"/>' for i in range(4))
    return SKY + '<rect y="170" width="400" height="90" fill="#12304a"/>' + w + '<rect y="120" width="400" height="12" fill="#0a0d12"/><g fill="none" stroke="#0a0d12" stroke-width="8"><path d="M30 132 Q85 190 140 132"/><path d="M140 132 Q195 190 250 132"/><path d="M250 132 Q305 190 360 132"/></g><g fill="#0a0d12"><rect x="26" y="100" width="8" height="40"/><rect x="136" y="100" width="8" height="40"/><rect x="246" y="100" width="8" height="40"/><rect x="356" y="100" width="8" height="40"/></g>'
def m_field(): return SKY + '<rect y="140" width="400" height="120" fill="#2c2a14"/>' + ''.join(f'<path d="M0 {150+i*18} L400 {146+i*18}" stroke="#4a4620" stroke-width="3"/>' for i in range(6)) + '<g stroke="#0a0d12" stroke-width="4"><path d="M20 150 V110 M80 148 V108 M140 147 V107 M200 146 V106 M260 145 V105 M320 144 V104 M380 143 V103"/><path d="M10 120 H395" stroke-width="3"/></g>'
def m_jail(): return '<rect width="400" height="260" fill="#1b1f27"/><rect x="40" y="25" width="320" height="210" fill="#30384a"/><rect x="62" y="45" width="276" height="170" fill="#e9c46a" opacity=".22"/><g fill="#0b0d12">' + ''.join(f'<rect x="{70+i*36}" y="25" width="10" height="210"/>' for i in range(8)) + '<rect x="40" y="95" width="320" height="10"/><rect x="40" y="165" width="320" height="10"/></g>'
def m_woods(): return SKY + '<rect y="200" width="400" height="60" fill="#0b140c"/>' + ''.join(f'<polygon points="{x-30},210 {x},{h} {x+30},210" fill="#0d1e12"/><polygon points="{x-24},170 {x},{h+25} {x+24},170" fill="#12301a"/>' for x, h in [(30,70),(100,40),(170,85),(250,50),(320,75),(375,95)]) + '<g fill="#0a0d12"><rect x="94" y="205" width="12" height="30"/><rect x="244" y="205" width="12" height="30"/></g>'
def m_hospital(): return SKY + '<rect y="205" width="400" height="55" fill="#101319"/><rect x="100" y="80" width="200" height="125" fill="#d6dde6"/><g fill="#f0c25a"><rect x="116" y="100" width="22" height="18"/><rect x="154" y="100" width="22" height="18"/><rect x="224" y="100" width="22" height="18"/><rect x="262" y="100" width="22" height="18"/><rect x="116" y="140" width="22" height="18"/><rect x="262" y="140" width="22" height="18"/></g><rect x="180" y="140" width="40" height="65" fill="#394658"/><rect x="190" y="52" width="20" height="46" fill="#c62f3c"/><rect x="177" y="65" width="46" height="20" fill="#c62f3c"/>'
def m_fire(): return SKY + '<rect y="205" width="400" height="55" fill="#101319"/><rect x="110" y="110" width="180" height="95" fill="#1d1511"/><path d="M150 205 Q135 150 165 120 Q165 150 185 135 Q180 90 215 65 Q215 120 245 135 Q260 160 250 205 Z" fill="#e8601c"/><path d="M175 205 Q170 165 195 145 Q200 170 215 160 Q230 185 222 205 Z" fill="#f6c453"/><circle cx="200" cy="60" r="70" fill="#e8601c" opacity=".12"/>'
def m_school(): return SKY + '<rect y="205" width="400" height="55" fill="#101319"/><rect x="90" y="110" width="220" height="95" fill="#5d3b30"/><polygon points="90,110 200,70 310,110" fill="#3a2520"/><g fill="#f0c25a" opacity=".85"><rect x="110" y="130" width="24" height="26"/><rect x="150" y="130" width="24" height="26"/><rect x="226" y="130" width="24" height="26"/><rect x="266" y="130" width="24" height="26"/></g><rect x="184" y="150" width="32" height="55" fill="#1a0f0c"/><rect x="332" y="60" width="4" height="145" fill="#999"/><rect x="336" y="62" width="34" height="22" fill="#c62f3c"/>'
def m_store(): return SKY + '<rect y="205" width="400" height="55" fill="#101319"/><rect x="80" y="100" width="240" height="105" fill="#2d3748"/><g>' + ''.join(f'<rect x="{80+i*30}" y="100" width="30" height="26" fill="{"#c62f3c" if i%2==0 else "#f3ead7"}"/>' for i in range(8)) + '</g><rect x="105" y="140" width="80" height="65" fill="#f0c25a" opacity=".75"/><rect x="215" y="140" width="80" height="65" fill="#f0c25a" opacity=".5"/>'
def m_city(): return SKY + '<rect y="215" width="400" height="45" fill="#0b0e14"/>' + ''.join(f'<rect x="{x}" y="{y}" width="{w}" height="{215-y}" fill="#141c2b"/>' + ''.join(f'<rect x="{x+6+(k%3)*((w-12)//3)}" y="{y+10+(k//3)*20}" width="7" height="9" fill="#f0c25a" opacity=".7"/>' for k in range(9) if y+10+(k//3)*20 < 205) for x, y, w in [(10,120,60),(80,80,55),(145,140,50),(205,60,60),(275,110,55),(335,150,55)])
def m_missing(): return SKY + '<polygon points="0,260 400,260 215,140 185,140" fill="#161922"/><g fill="#d9b24a"><polygon points="198,150 202,150 204,165 196,165"/><polygon points="194,180 206,180 210,205 190,205"/><polygon points="186,225 214,225 224,260 176,260"/></g><text x="200" y="118" text-anchor="middle" font-size="96" font-weight="700" fill="#f3ead7" opacity=".9" font-family="DejaVu Sans Condensed">?</text>'
def m_files(): return '<rect width="400" height="260" fill="#cdb48a"/><g><rect x="30" y="120" width="150" height="110" fill="#a8825a" stroke="#6b4f33" stroke-width="4"/><rect x="60" y="145" width="90" height="26" fill="#e9dcc2"/><rect x="215" y="120" width="150" height="110" fill="#b48d63" stroke="#6b4f33" stroke-width="4"/><rect x="245" y="145" width="90" height="26" fill="#e9dcc2"/><rect x="60" y="85" width="100" height="40" fill="#e9dcc2" transform="rotate(-6 110 105)"/><rect x="235" y="82" width="100" height="40" fill="#f6efdc" transform="rotate(5 285 100)"/></g><circle cx="200" cy="60" r="30" fill="none" stroke="#17324a" stroke-width="9"/><line x1="222" y1="82" x2="256" y2="116" stroke="#17324a" stroke-width="11" stroke-linecap="round"/>'
def m_scales(): return '<rect width="400" height="260" fill="#17324a"/><g stroke="#f3ead7" stroke-width="7" fill="none" stroke-linecap="round"><path d="M200 40 V210"/><path d="M110 70 H290"/><path d="M110 70 L80 140 M110 70 L140 140 M290 70 L260 140 M290 70 L320 140"/><path d="M70 140 H150 Q110 175 70 140Z M250 140 H330 Q290 175 250 140Z" fill="#f3ead7"/><path d="M150 215 H250"/></g>'

MOTIFS = [  # (name, keywords, drawer) in priority order
    ("water", r"\b(river|creek|lake|bayou|ocean|canal|pond|drown\w*|bridge|reservoir|bay)\b", m_water),
    ("fire", r"\b(fire|arson|burned|bomb\w*|explosi\w*|blast)\b", m_fire),
    ("jail", r"\b(jail|prison|cell|custody|detention|inmate)\b", m_jail),
    ("hospital", r"\b(hospital|emergency room|clinic|medical center)\b", m_hospital),
    ("police", r"\b(police|officer|officers|deputy|deputies|sheriff|trooper|patrol|cruiser|swat|marshal)\b", m_police),
    ("woods", r"\b(woods|forest|swamp|wooded|trail|ditch|marsh)\b", m_woods),
    ("field", r"\b(farm|field|plantation|sharecropp\w*|cotton|rural|county road|pasture)\b", m_field),
    ("school", r"\b(school|campus|college|university|classroom)\b", m_school),
    ("house", r"\b(home|house|apartment|porch|door|bedroom|residence|driveway|yard)\b", m_house),
    ("store", r"\b(store|shop|restaurant|bar|club|market|gas station|motel|diner|casino)\b", m_store),
    ("road", r"\b(car|truck|vehicle|highway|road|street|driving|drove|traffic|interstate|bus)\b", m_road),
]


def pick_scenes(c):
    if c["caseType"] == "missing_persons":
        first = m_missing
    else:
        first = None
    text = " ".join([c.get("summary") or ""] + (c.get("known") or [])[:3]).lower()
    found = []
    for name, rx, fn in MOTIFS:
        m = re.search(rx, text)
        if m:
            found.append((m.start(), name, fn))
    # earliest mention in the text first
    found.sort(key=lambda t: t[0])
    fns = []
    if first:
        fns.append(first)
    for _, name, fn in found:
        if fn not in fns:
            fns.append(fn)
    for dflt in (m_city, m_road):
        if len(fns) < 2 and dflt not in fns:
            fns.append(dflt)
    return fns[0], fns[1]


def svg(inner, cls=""):
    return f'<svg class="art {cls}" viewBox="0 0 400 260" preserveAspectRatio="xMidYMid slice">{inner}</svg>'


# faceless bust: solid black head, no features
BUST = '''<svg class="bust" viewBox="0 0 200 220"><path d="M20 220 Q22 150 100 140 Q178 150 180 220Z" fill="#17324a"/><path d="M85 140 L100 175 L115 140Z" fill="#f3ead7"/><ellipse cx="100" cy="86" rx="46" ry="54" fill="#050507"/></svg>'''


def hook(c):
    n = c["name"].split(" (")[0]
    if c["caseType"] == "missing_persons":
        return "WHAT HAPPENED TO THEM?" if len(n) > 24 else f"WHAT HAPPENED TO {n.upper()}?"
    if len(n) > 24:
        return "WHO KILLED THEM?" if c["status"] == "unsolved" else "WHO IS ACCOUNTABLE?"
    return f"WHO KILLED {n.upper()}?" if c["status"] == "unsolved" else f"WHO IS ACCOUNTABLE FOR {n.upper()}’S DEATH?"


def card(c):
    e = html.escape
    a, b = pick_scenes(c)
    where = ", ".join(x for x in [c.get("city"), c.get("state")] if x).upper()
    agebit = f"AGE {c['age']}" if c.get("age") else ""
    sub = " · ".join(x for x in [str(c["year"]) if c.get("year") else "", agebit] if x)
    kind = "MISSING PERSON" if c["caseType"] == "missing_persons" else "HOMICIDE"
    q = (c.get("unanswered") or [""])[0]
    if c["status"] == "unresolved":
        invest = "CHARGES WERE FILED — BUT NO CONVICTION"
        invest_art = m_scales()
    elif c["caseType"] == "missing_persons":
        invest = "NEVER FOUND — THE CASE IS STILL OPEN"
        invest_art = m_files()
    else:
        invest = "THE CASE REMAINS UNSOLVED"
        invest_art = m_files()
    hk = hook(c)
    import datetime
    yrs = datetime.date.today().year - int(c["year"]) if c.get("year") else None
    if yrs is None:
        years_txt = "A CASE STILL OPEN"
    elif c["caseType"] == "missing_persons":
        years_txt = f"{yrs} YEARS MISSING" if yrs > 0 else "RECENTLY MISSING"
    elif c["status"] == "unresolved":
        years_txt = f"{yrs} YEARS, NO CONVICTION" if yrs > 0 else "NO CONVICTION YET"
    else:
        years_txt = f"{yrs} YEARS UNSOLVED" if yrs > 0 else "NEW CASE"
    return f'''<!doctype html><meta charset="utf-8"><style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{width:1408px;height:768px;overflow:hidden;position:relative;background:#0d1117;
 font-family:"DejaVu Sans Condensed","DejaVu Sans",sans-serif;color:#f3ead7}}
.dots{{position:absolute;inset:0;background-image:radial-gradient(rgba(243,234,215,.06) 2px,transparent 2.5px);background-size:16px 16px}}
.p{{position:absolute;border:5px solid #f3ead7;overflow:hidden}}
.art{{position:absolute;inset:0;width:100%;height:100%}}
.tag{{font-family:"DejaVu Sans Mono",monospace;font-weight:700;letter-spacing:3px;font-size:17px}}
.bar{{position:absolute;left:0;right:0;background:#f3ead7;color:#0d1117;font-weight:700;padding:5px 14px;font-size:21px;letter-spacing:1px;z-index:3}}
#p1{{left:12px;top:12px;width:410px;height:330px;background:#7d1a24}}
#p1 .nm{{position:absolute;left:20px;top:44px;width:236px;font-weight:700;text-transform:uppercase;line-height:1.0}}
#p1 .sub{{position:absolute;left:20px;bottom:18px;font-weight:700;color:#f6c9a0;font-size:25px;width:230px;line-height:1.2}}
#p1 .bust{{position:absolute;right:0;bottom:0;width:150px;height:165px}}
#p1 .tag{{position:absolute;left:20px;top:14px;color:#f6c9a0}}
#hd{{left:432px;top:12px;width:964px;height:62px;background:#0d1117;display:flex;align-items:center;padding:0 22px;font-weight:700;letter-spacing:1px;text-transform:uppercase;white-space:nowrap}}
#sa{{left:432px;top:82px;width:470px;height:260px;background:#17324a}}
#wh{{left:912px;top:82px;width:484px;height:260px;background:#17324a;padding:16px 20px}}
#wh .tag{{color:#f6c9a0;margin-bottom:8px}}
#wh .t{{font-size:25px;line-height:1.28;font-weight:600}}
#sb{{left:12px;top:352px;width:410px;height:262px;background:#17324a}}
#iv{{left:432px;top:352px;width:470px;height:262px;background:#17324a}}
#iv .bar{{bottom:0;font-size:22px;text-align:center;background:#0d1117;color:#f3ead7;border-top:4px solid #f3ead7;padding:9px 10px}}
#qu{{left:912px;top:352px;width:484px;height:262px;background:#f3ead7;color:#0d1117;padding:16px 22px}}
#qu .tag{{color:#7d1a24;margin-bottom:8px}}
#qu .t{{font-size:28px;line-height:1.25;font-weight:700}}
#hk{{left:12px;top:624px;width:1384px;height:96px;background:#0d1117;display:flex;align-items:center;justify-content:space-between;padding:0 28px}}
#hk .h{{font-weight:700;color:#f6c9a0;white-space:nowrap;display:inline-block}}
#hk .r{{text-align:right;font-family:"DejaVu Sans Mono",monospace;font-size:22px;line-height:1.5}}
.badge{{display:inline-block;background:#f3ead7;color:#7d1a24;padding:3px 12px;font-weight:700;letter-spacing:3px}}
#ds{{position:absolute;left:14px;right:14px;top:726px;font-size:15px;line-height:1.25;color:#9aa3b2;text-align:center}}
.burst{{position:absolute;left:14px;bottom:14px;z-index:3;background:#f3ead7;color:#0d1117;font-weight:700;font-size:21px;padding:8px 14px;border:4px solid #0d1117;transform:rotate(-2deg);max-width:300px}}
</style><div class="dots"></div>
<div class="p" id="p1"><div class="tag">CASE #{e(str(c['caseNumber']))} · {kind}</div><div class="nm fit" data-max="52" data-min="24" data-h="205">{e(c['name'])}</div><div class="sub">{e(sub)}</div>{BUST}</div>
<div class="p" id="hd">{e(c['name'])}&nbsp;— case file</div>
<div class="p" id="sa">{svg(a())}<div class="bar">{e(where)}{(" — " + str(c["year"])) if c.get("year") else ""}</div></div>
<div class="p" id="wh"><div class="tag">WHAT HAPPENED</div><div class="t fit" data-max="25" data-min="15">{e(clip(c['summary'], 400))}</div></div>
<div class="p" id="sb">{svg(b())}<div class="burst">{e(years_txt)}</div></div>
<div class="p" id="iv">{svg(invest_art)}<div class="bar">{e(invest)}</div></div>
<div class="p" id="qu"><div class="tag">STILL UNANSWERED</div><div class="t fit" data-max="28" data-min="18">{e(clip(q, 230))}</div></div>
<div class="p" id="hk"><div class="h fitw" data-max="54" data-min="26">{e(hk)}</div><div class="r"><span class="badge">{STATUS_BADGE.get(c['status'], '')}</span><br>{DOMAIN}</div></div>
<div id="ds">Illustrations are symbolic, drawn to give a visual sense of the story. They are not depictions of the real people or events. Facts come from the case file at {DOMAIN}.</div>
'''


FIT_JS = """() => {
  const bad = [];
  document.querySelectorAll('.fit').forEach(el => {
    const box = el.parentElement;
    let fs = parseFloat(el.dataset.max), min = parseFloat(el.dataset.min);
    const lim = () => el.dataset.h ? el.scrollHeight > parseFloat(el.dataset.h)
                  : box.scrollHeight > box.clientHeight + 2;
    el.style.fontSize = fs + 'px';
    while (lim() && fs > min) { fs -= 1; el.style.fontSize = fs + 'px'; }
    if (lim()) bad.push(box.id);
  });
  document.querySelectorAll('.fitw').forEach(el => {
    let fs = parseFloat(el.dataset.max);
    el.style.fontSize = fs + 'px';
    while (el.scrollWidth > (parseFloat(el.dataset.w)||960) && fs > parseFloat(el.dataset.min)) { fs -= 1; el.style.fontSize = fs + 'px'; }
  });
  return bad;
}"""


def main():
    ids = set(sys.argv[1:])
    todo = [c for c in CASES if not ids or c["id"] in ids]
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 1408, "height": 768})
        for c in todo:
            pg.set_content(card(c))
            bad = pg.evaluate(FIT_JS)
            if bad:
                print("OVERFLOW", c["id"], bad)
            pg.screenshot(path=os.path.join(OUT, c["id"] + ".png"))
        b.close()
    print("wrote", len(todo), "cards to", OUT)


main()
