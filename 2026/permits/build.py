import json, os

OUT = "."
os.makedirs(OUT, exist_ok=True)

SOURCE = ("Source: Freedom of Information response, long-term employment permit submissions "
          "1 January to 22 October 2026. Graphic: The Quarry")

# role rows: (approved, rejected, withdrawn, awaiting)
SECTORS = [
    ("Health and social care", 131, 0, 7, 126),
    ("Hospitality", 64, 4, 5, 105),
    ("Accountancy", 60, 0, 6, 94),
    ("Out of policy", 6, 3, 1, 88),
    ("Construction", 18, 1, 1, 30),
    ("Education (all phases)", 29, 0, 0, 5),
    ("Fund services", 15, 0, 1, 15),
    ("Legal services", 21, 0, 0, 7),
    ("Other sectors (16)", 75, 1, 6, 75),
]
TOTAL = (419, 9, 27, 545)
IN_POLICY = tuple(t - o for t, o in zip(TOTAL, SECTORS[3][1:]))
OUT_POLICY = SECTORS[3][1:]

ROLES = [
    ("Regulated health professional", 95, 0, 3, 66),
    ("Audit manager / associate", 31, 0, 2, 30),
    ("Sous chef / senior sous / second chef", 16, 3, 2, 33),
    ("Support worker (residential, respite, community)", 13, 0, 0, 32),
    ("Audit assistant", 6, 0, 2, 34),
    ("Assistant general manager (hotel, restaurant, bar)", 14, 0, 0, 24),
    ("Healthcare assistant", 11, 0, 3, 18),
    ("Senior carer (residential / nursing home)", 11, 0, 1, 8),
    ("Law firm associate / assistant", 16, 0, 0, 4),
    ("Advisory manager / associate (accountancy)", 10, 0, 1, 9),
    ("Secondary class teacher", 18, 0, 0, 1),
    ("Head chef", 4, 0, 0, 15),
]

REJECTIONS = [
    ("Out-of-policy posts", "Out of policy", 3),
    ("Sous chef / senior sous / second chef", "Hospitality", 3),
    ("Night manager", "Hospitality", 1),
    ("Stonemason foreman", "Construction", 1),
    ("Retail store supervisor / assistant manager", "Retail", 1),
]

# sanity checks against the FoI totals
assert tuple(sum(r[i] for r in SECTORS) for i in range(1, 5)) == TOTAL
assert sum(TOTAL) == 1000
assert sum(r[2] for r in REJECTIONS) == TOTAL[1]

CSS = """
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600&family=Space+Grotesk:wght@600;700&display=swap');
:root{--ink:#111;--approved:#60A07D;--awaiting:#111;--withdrawn:#b9b9b0;--rejected:#c8553d;--track:rgba(0,0,0,.06);--muted:#4a4a4a}
*{box-sizing:border-box}
html,body{margin:0;background:transparent;color:var(--ink);font-family:Poppins,system-ui,sans-serif}
.chart{max-width:720px;margin:0 auto;padding:16px}
h2{font-family:'Space Grotesk',sans-serif;font-weight:700;font-size:clamp(1.15rem,3.6vw,1.55rem);line-height:1.2;margin:0 0 6px}
.dek{font-size:.88rem;line-height:1.45;color:var(--muted);margin:0 0 14px}
.legend{display:flex;flex-wrap:wrap;gap:6px 16px;font-size:.8rem;margin:0 0 14px;padding:0;list-style:none}
.legend li{display:flex;align-items:center;gap:6px}
.sw{width:12px;height:12px;border-radius:2px;display:inline-block;flex:none}
.approved{background:var(--approved)}.awaiting{background:var(--awaiting)}
.withdrawn{background:var(--withdrawn)}.rejected{background:var(--rejected)}
.source{font-size:.7rem;color:var(--muted);margin-top:14px;line-height:1.4}
.note{font-size:.75rem;color:var(--muted);margin-top:8px;line-height:1.4}
.rows{display:flex;flex-direction:column;gap:12px}
.row .lab{font-size:.82rem;font-weight:500;margin-bottom:4px;display:flex;justify-content:space-between;gap:10px}
.row .lab span:last-child{font-weight:400;color:var(--muted);white-space:nowrap}
.bar{display:flex;height:20px;background:var(--track);border-radius:2px;overflow:hidden}
.bar div{height:100%}
.bar div+div{box-shadow:inset 1px 0 0 rgba(255,255,255,.5)}
"""

HEIGHT_JS = """
<script>
(function(){var id=%s;function post(){try{parent.postMessage({type:'quarry-chart-height',id:id,height:document.documentElement.scrollHeight},'*')}catch(e){}}
window.addEventListener('load',post);if(window.ResizeObserver)new ResizeObserver(post).observe(document.body);})();
</script>"""

LEGEND = """<ul class="legend">
<li><span class="sw approved"></span>Approved</li>
<li><span class="sw rejected"></span>Rejected</li>
<li><span class="sw withdrawn"></span>Withdrawn</li>
<li><span class="sw awaiting"></span>Awaiting decision</li>
</ul>"""

KEYS = ["approved", "rejected", "withdrawn", "awaiting"]
NAMES = ["approved", "rejected", "withdrawn", "awaiting decision"]


def page(slug, title, body):
    html = f"""<!doctype html>
<html lang="en-GB"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<style>{CSS}</style></head>
<body><div class="chart">
{body}
<p class="source">{SOURCE}</p>
</div>{HEIGHT_JS % json.dumps(slug)}</body></html>"""
    with open(f"{OUT}/{slug}.html", "w") as f:
        f.write(html)


def bar(vals, scale):
    segs = []
    for k, n, v in zip(KEYS, NAMES, vals):
        if v:
            segs.append(f'<div class="{k}" style="width:{v / scale * 100:.3f}%" title="{v} {n}"></div>')
    return f'<div class="bar">{"".join(segs)}</div>'


def stacked_rows(rows, scale_to_max=True):
    mx = max(sum(r[1:]) for r in rows)
    out = []
    for name, *vals in rows:
        tot = sum(vals)
        pct = round(vals[3] / tot * 100)
        out.append(f'<div class="row"><div class="lab"><span>{name}</span>'
                   f'<span>{tot} · {pct}% awaiting</span></div>{bar(vals, mx if scale_to_max else tot)}</div>')
    return '<div class="rows">' + "".join(out) + "</div>"


# 1. Waffle: one square per application
cells = []
for k, n, v in zip(["awaiting", "approved", "withdrawn", "rejected"],
                   ["Awaiting decision", "Approved", "Withdrawn", "Rejected"],
                   [TOTAL[3], TOTAL[0], TOTAL[2], TOTAL[1]]):
    cells += [f'<i class="{k}"></i>'] * v
waffle = f"""
<style>
.waffle{{display:grid;grid-template-columns:repeat(40,1fr);grid-template-rows:repeat(25,auto);grid-auto-flow:column;gap:2px}}
.waffle i{{aspect-ratio:1;border-radius:1px;display:block}}
.big{{display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin:0 0 14px}}
.big div{{font-size:.75rem;line-height:1.3;color:var(--muted)}}
.big b{{display:block;font-family:'Space Grotesk',sans-serif;font-size:clamp(1.3rem,5vw,1.9rem);color:var(--ink);line-height:1.1}}
.big span.sw{{margin-right:4px;vertical-align:-1px}}
@media(max-width:420px){{.waffle{{gap:1px}}.big{{grid-template-columns:repeat(2,1fr)}}}}
</style>
<h2>More than half of this year's permit applications are still awaiting a decision</h2>
<p class="dek">All 1,000 long-term employment permit applications submitted between 1 January and 22 October 2026. Each square is one application.</p>
<div class="big">
<div><b>545</b><span class="sw awaiting"></span>Awaiting decision</div>
<div><b>419</b><span class="sw approved"></span>Approved</div>
<div><b>27</b><span class="sw withdrawn"></span>Withdrawn</div>
<div><b>9</b><span class="sw rejected"></span>Rejected</div>
</div>
<div class="waffle" role="img" aria-label="545 awaiting decision, 419 approved, 27 withdrawn, 9 rejected">{''.join(cells)}</div>
<p class="note">Of the 428 applications decided, 9 (2%) were rejected.</p>
"""
page("1-outcomes-waffle", "Permit application outcomes", waffle)

# 2. Sectors
page("2-sectors", "Permit applications by sector", f"""
<h2>Health, hospitality and accountancy account for six in ten applications</h2>
<p class="dek">Long-term employment permit applications by sector and outcome, 1 January to 22 October 2026.</p>
{LEGEND}
{stacked_rows(SECTORS)}
<p class="note">Education combines further, primary, secondary, special educational needs, music and education services. Other sectors include fiduciary, compliance, facilities, banking, law enforcement, retail and transport.</p>
""")

# 3. In policy vs out of policy (100% bars)
page("3-out-of-policy", "Out-of-policy applications", f"""
<h2>Nine in ten out-of-policy applications are still waiting</h2>
<p class="dek">Share of applications awaiting a decision for posts on the in-policy list compared with posts outside it, 1 January to 22 October 2026.</p>
{LEGEND}
{stacked_rows([("In-policy posts", *IN_POLICY), ("Out-of-policy posts", *OUT_POLICY)], scale_to_max=False)}
<p class="note">Bars show the share of each group. In-policy: {sum(IN_POLICY)} applications. Out-of-policy: {sum(OUT_POLICY)} applications.</p>
""")

# 4. Roles
page("4-top-roles", "Most-requested roles", f"""
<h2>Health professionals, auditors and chefs top the list</h2>
<p class="dek">The roles with the most long-term employment permit applications, 1 January to 22 October 2026.</p>
{LEGEND}
{stacked_rows(ROLES)}
<p class="note">Roles with 19 or more applications. A further 98 applications were for posts outside the in-policy list.</p>
""")

# 5. Rejections table
rows = "".join(f"<tr><td>{r}</td><td>{s}</td><td>{n}</td></tr>" for r, s, n in REJECTIONS)
page("5-rejections", "Rejected applications", f"""
<style>
table{{width:100%;border-collapse:collapse;font-size:.85rem}}
th{{text-align:left;font-weight:600;font-size:.75rem;text-transform:uppercase;letter-spacing:.04em;border-bottom:2px solid var(--ink);padding:6px 8px 6px 0}}
td{{padding:9px 8px 9px 0;border-bottom:1px solid rgba(0,0,0,.12);vertical-align:top}}
th:last-child,td:last-child{{text-align:right;padding-right:0}}
tfoot td{{font-weight:600;border-bottom:none;border-top:2px solid var(--ink)}}
</style>
<h2>Nine applications refused</h2>
<p class="dek">Every rejected long-term employment permit application, 1 January to 22 October 2026, out of 428 decided.</p>
<table><thead><tr><th>Role</th><th>Sector</th><th>Rejected</th></tr></thead>
<tbody>{rows}</tbody><tfoot><tr><td>Total</td><td></td><td>9</td></tr></tfoot></table>
""")

print("in policy", IN_POLICY, sum(IN_POLICY), "out", OUT_POLICY)
print(os.listdir(OUT))
