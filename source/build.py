"""Builds the Ninety Sure question bank.
Sources: mledoze/countries (ODbL), Bowserinator/Periodic-Table-JSON (CC BY-SA 3.0),
exact computation, and hand-picked facts in curated.py.
Output: questions.js  (const QUESTIONS=[[id,text,answer,unit,scale,min,max,note,cat],...])"""
import json, math, random, re, subprocess, sys, itertools
from curated import FACTS, YEARS, BIRTHS, UNITS

R = random.Random(20261001)
OUT = []
seen_ids = set()
seen_texts = set()

def fmtn(v):
    if isinstance(v, float) and not v.is_integer():
        if abs(v) >= 100: return f"{v:,.0f}"
        return f"{v:,.4g}"
    return f"{int(v):,}"

def log_domain(ans, r):
    la = math.log10(ans)
    lo = math.floor(la - 1 - r.random() * 1.2)
    hi = math.ceil(la + 1 + r.random() * 1.2)
    return float(10 ** lo), float(10 ** hi)

def year_domain(ans, r):
    if ans >= 1700: span = r.choice([100, 120, 150, 200])
    elif ans >= 1000: span = r.choice([300, 400, 500, 600])
    elif ans >= 0: span = r.choice([600, 800, 1000, 1200])
    else: span = r.choice([1000, 1500, 2000, 3000])
    step = 10 if span <= 200 else 50
    for _ in range(20):
        u = 0.15 + 0.7 * r.random()
        lo = math.floor((ans - span * u) / step) * step
        hi = lo + span
        if hi > 2030: lo -= hi - 2030; hi = 2030
        t = (ans - lo) / span
        if 0.1 <= t <= 0.9: return lo, hi
    return ans - span // 2, ans + span // 2

def temp_domain(ans, r):
    span = r.choice([1000, 1500, 2000, 3000, 4000])
    span = max(span, int(abs(ans) * 1.6 // 100 * 100) + 500)
    for _ in range(30):
        u = 0.15 + 0.7 * r.random()
        lo = math.floor((ans - span * u) / 100) * 100
        if lo < -273: lo = -273
        hi = lo + span
        t = (ans - lo) / span
        if 0.1 <= t <= 0.9: return lo, hi
        if lo == -273: span = max(300, int((ans + 273) / 0.3))
    return -273, -273 + span

def add(id_, text, ans, unit, scale, lo, hi, note, cat):
    if id_ in seen_ids: raise SystemExit('duplicate id ' + id_)
    if text in seen_texts: return  # same question already in the bank
    seen_texts.add(text)
    seen_ids.add(id_)
    t = (math.log(ans / lo) / math.log(hi / lo)) if scale == 'log' else (ans - lo) / (hi - lo)
    if not (0.04 < t < 0.96): raise SystemExit(f'answer too close to edge: {id_} t={t:.3f}')
    OUT.append([id_, text, ans, unit, scale, lo, hi, note, cat])

# ---------- 1. the original 67 questions (kept exactly) ----------
html = open('original_questions.html').read()
m = re.search(r'const Q=\[\n(.*?)\n\];', html, re.S)
orig = json.loads(subprocess.run(['node', '-e', 'const Q=[' + m.group(1) + '];console.log(JSON.stringify(Q))'], capture_output=True, text=True, check=True).stdout)
for q in orig:
    cat = 'history' if q[4] == 'year' else 'facts'
    add(q[0], q[1], q[2], q[3], q[4], q[5], q[6], q[7], cat)

# ---------- 2. hand-picked facts ----------
for f in FACTS:
    id_, text, ans, unit, scale, note = f[:6]
    if scale == 'lin': lo, hi = f[6], f[7]
    else: lo, hi = log_domain(ans, R)
    add(id_, text, ans, unit, scale, lo, hi, note, 'facts')
for id_, text, year, note in YEARS:
    lo, hi = year_domain(year, R); add(id_, text, year, 'year', 'year', lo, hi, note, 'history')
for id_, name, year, note in BIRTHS:
    lo, hi = year_domain(year, R)
    yr = f"{-year} BC" if year < 0 else str(year)
    add(id_, f'In what year was {name} born?', year, 'year', 'year', lo, hi, note or f'{yr}.', 'history')
for id_, text, ans, unit, note in UNITS:
    lo, hi = log_domain(ans, R); add(id_, text, ans, unit, 'log', lo, hi, note, 'numbers')

# ---------- 3. countries (mledoze/countries, ODbL) ----------
C = json.load(open('data/countries.json'))
un = [c for c in C if c.get('unMember') and c.get('area', 0) > 0]
by3 = {c['cca3']: c['name']['common'] for c in C}
sovereign = {c['cca3'] for c in C if c.get('unMember') or c['cca3'] in ('VAT','PSE','XKX','TWN','ESH')}
real_states = {c['cca3'] for c in C if c.get('unMember') or c['cca3'] in ('VAT',)}
un_sorted = sorted(un, key=lambda c: -c['area'])
rank = {c['cca3']: i + 1 for i, c in enumerate(un_sorted)}
def ordinal(n): return f"{n}{'th' if 11 <= n % 100 <= 13 else {1:'st',2:'nd',3:'rd'}.get(n % 10, 'th')}"
for c in un:
    name = c['name']['common']; a = c['area']; rk = rank[c['cca3']]
    lo, hi = log_domain(a, R)
    note = f"{fmtn(a)} km² in total. That makes it the {ordinal(rk)} largest of {len(un)} UN member states." if rk > 1 else f"{fmtn(a)} km², the largest country on Earth."
    add('area_' + c['cca3'].lower(), f'How big is {name}?', a, 'km²', 'log', lo, hi, note, 'world')
for c in un:
    nb = [x for x in (c.get('borders') or []) if x in real_states]
    if len(nb) < 2: continue
    names = sorted(by3.get(x, x) for x in nb)
    lst = ', '.join(names[:-1]) + ' and ' + names[-1]
    add('bord_' + c['cca3'].lower(), f"How many countries share a land border with {c['name']['common']}?", len(nb), 'countries', 'lin', 0, 20,
        f'{len(nb)}: {lst}. Territories and disputed areas are not counted.', 'world')

# ---------- 4. elements (Periodic-Table-JSON, CC BY-SA 3.0) ----------
E = json.load(open('data/PeriodicTableJSON.json'))['elements']
skip_phase = {6, 33}   # carbon and arsenic turn straight to gas at normal pressure
for e in E:
    z, nm, sym = e['number'], e['name'], e['symbol']
    if z > 118: continue
    if z >= 3:
        lo, hi = 1.0, 1000.0
        add(f'z_{sym.lower()}', f'What is the atomic number of {nm.lower()}?', z, '(its number of protons)', 'log', lo, hi,
            f'{nm} ({sym}) is element {z}.', 'science')
    if z > 92 or z in skip_phase: continue
    if e.get('melt') and e['phase'] in ('Solid', 'Liquid'):
        mc = round(e['melt'] - 273.15)
        if mc > -200:
            lo, hi = temp_domain(mc, R)
            add(f'mp_{sym.lower()}', f'At what temperature does {nm.lower()} melt?', mc, '°C', 'lin', lo, hi,
                f'About {fmtn(mc)} °C.' + (' It is one of only two elements that are liquid at room temperature.' if z in (35, 80) else ''), 'science')
    if e.get('boil') and e['phase'] in ('Solid', 'Liquid'):
        bc = round(e['boil'] - 273.15)
        if bc > -200:
            lo, hi = temp_domain(bc, R)
            add(f'bp_{sym.lower()}', f'At what temperature does {nm.lower()} boil?', bc, '°C', 'lin', lo, hi, f'About {fmtn(bc)} °C.', 'science')
    if e['phase'] == 'Solid' and e.get('density') and z <= 92:
        d = round(e['density'], 3 if e['density'] < 1 else 2)
        lo, hi = log_domain(d, R)
        add(f'den_{sym.lower()}', f'How dense is {nm.lower()}? (Water is 1.)', d, 'grams per cm³', 'log', lo, hi,
            f'About {d:g} g/cm³, so {"lighter" if d < 1 else f"{d:g} times heavier"} than the same amount of water.' if d >= 1 else f'About {d:g} g/cm³, so it would float on water.', 'science')

# ---------- 5. straight-line distances between cities (computed) ----------
CITIES = {
 'Tokyo':(35.68,139.69),'Delhi':(28.61,77.21),'Shanghai':(31.23,121.47),'São Paulo':(-23.55,-46.63),'Mexico City':(19.43,-99.13),
 'Cairo':(30.04,31.24),'Mumbai':(19.08,72.88),'Beijing':(39.90,116.41),'Dhaka':(23.81,90.41),'New York':(40.71,-74.01),
 'Karachi':(24.86,67.01),'Buenos Aires':(-34.60,-58.38),'Istanbul':(41.01,28.98),'Lagos':(6.52,3.38),'Manila':(14.60,120.98),
 'Rio de Janeiro':(-22.91,-43.17),'Los Angeles':(34.05,-118.24),'Moscow':(55.76,37.62),'Paris':(48.86,2.35),'London':(51.51,-0.13),
 'Bangkok':(13.76,100.50),'Jakarta':(-6.21,106.85),'Lima':(-12.05,-77.04),'Seoul':(37.57,126.98),'Johannesburg':(-26.20,28.05),
 'Nairobi':(-1.29,36.82),'Sydney':(-33.87,151.21),'Auckland':(-36.85,174.76),'Singapore':(1.35,103.82),'Dubai':(25.20,55.27),
 'Rome':(41.90,12.50),'Madrid':(40.42,-3.70),'Berlin':(52.52,13.40),'Toronto':(43.65,-79.38),'Chicago':(41.88,-87.63),
 'Vancouver':(49.28,-123.12),'Honolulu':(21.31,-157.86),'Reykjavík':(64.15,-21.94),'Cape Town':(-33.92,18.42),'Santiago':(-33.45,-70.67),
 'Bogotá':(4.71,-74.07),'Tehran':(35.69,51.39),'Stockholm':(59.33,18.07),'Athens':(37.98,23.73),'Anchorage':(61.22,-149.90),
 'Hong Kong':(22.32,114.17),'Helsinki':(60.17,24.94),'Lisbon':(38.72,-9.14),'Havana':(23.11,-82.37),'Addis Ababa':(9.03,38.74),
 'Kinshasa':(-4.44,15.27),'Perth':(-31.95,115.86),'Melbourne':(-37.81,144.96),'Warsaw':(52.23,21.01),'Kyiv':(50.45,30.52),
}
def hav(a, b):
    (la1, lo1), (la2, lo2) = a, b
    p1, p2 = math.radians(la1), math.radians(la2)
    dp, dl = p2 - p1, math.radians(lo2 - lo1)
    h = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * 6371.0088 * math.asin(math.sqrt(h))
pairs = [(a, b) for a, b in itertools.combinations(CITIES, 2) if hav(CITIES[a], CITIES[b]) >= 500]
R.shuffle(pairs)
use = {c: 0 for c in CITIES}; chosen = []
for a, b in pairs:
    if use[a] >= 18 or use[b] >= 18: continue
    chosen.append((a, b)); use[a] += 1; use[b] += 1
    if len(chosen) >= 440: break
def slug(s): return re.sub(r'[^a-z]', '', s.lower().replace('ã', 'a').replace('á', 'a').replace('í', 'i'))
for a, b in chosen:
    if R.random() < 0.5: a, b = b, a
    d = round(hav(CITIES[a], CITIES[b]) / 10) * 10
    lo, hi = log_domain(d, R)
    add(f'd_{slug(a)}_{slug(b)}', f'How far is it from {a} to {b}, in a straight line?', d, 'kilometres', 'log', lo, hi,
        f'About {fmtn(d)} km as the crow flies. Flights and roads are longer.', 'distance')

# ---------- 6. numbers you can estimate (computed exactly) ----------
def addnum(id_, text, ans, unit, note):
    lo, hi = log_domain(ans, R); add(id_, text, ans, unit, 'log', lo, hi, note, 'numbers')
made = set()
def prod(kind, n, alo, ahi, blo, bhi):
    k = 0
    while k < n:
        a, b = R.randint(alo, ahi), R.randint(blo, bhi)
        if a % 10 == 0 or b % 10 == 0 or (a, b) in made: continue
        made.add((a, b)); k += 1
        addnum(f'm_{a}x{b}', f'What is {a:,} × {b:,}?', a * b, '', f'{a:,} × {b:,} = {a*b:,}.')
prod('22', 60, 12, 99, 12, 99); prod('32', 60, 101, 999, 12, 99); prod('33', 35, 101, 999, 101, 999)
k = 0
while k < 50:
    p = R.choice([5, 12, 15, 17, 23, 35, 45, 65, 72, 85, 8, 3, 28, 64])
    base = R.choice([400, 650, 1200, 2400, 3600, 4800, 7500, 8600, 12000, 25000, 48000, 90000, 150000, 320000])
    if (p, base) in made: continue
    made.add((p, base)); k += 1
    v = p * base / 100
    addnum(f'pct_{p}_{base}', f'What is {p}% of {base:,}?', v, '', f'{p}% of {base:,} is {fmtn(v)}.')
for n in range(10, 41): addnum(f'pow2_{n}', f'What is 2 to the power of {n} (2 multiplied by itself {n} times)?', 2 ** n, '', f'2^{n} = {2**n:,}.')
for n in range(5, 21): addnum(f'pow3_{n}', f'What is 3 to the power of {n}?', 3 ** n, '', f'3^{n} = {3**n:,}.')
for n in range(5, 13): addnum(f'pow5_{n}', f'What is 5 to the power of {n}?', 5 ** n, '', f'5^{n} = {5**n:,}.')
for n in range(4, 11): addnum(f'pow7_{n}', f'What is 7 to the power of {n}?', 7 ** n, '', f'7^{n} = {7**n:,}.')
for a in R.sample([x for x in range(13, 100) if x % 10], 40): addnum(f'sq_{a}', f'What is {a} × {a} ({a} squared)?', a * a, '', f'{a}² = {a*a:,}.')
for a in range(11, 31): addnum(f'cube_{a}', f'What is {a} × {a} × {a} ({a} cubed)?', a ** 3, '', f'{a}³ = {a**3:,}.')
for n in range(6, 16): addnum(f'fact_{n}', f'What is {n} factorial ({" × ".join(str(i) for i in range(n, 0, -1)) if n <= 8 else f"{n} × {n-1} × … × 1"})?', math.factorial(n), '', f'{n}! = {math.factorial(n):,}. It is the number of ways to put {n} things in order.')
TIME = [('seconds', 'hours', 3600), ('seconds', 'days', 86400), ('seconds', 'weeks', 604800), ('minutes', 'days', 1440), ('minutes', 'weeks', 10080), ('hours', 'weeks', 168), ('minutes', 'years', 525600), ('seconds', 'years', 31536000)]
for small, big, f in TIME:
    for n in R.sample([2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 15, 20, 25, 30, 50, 100], 5 if big != 'years' else 3):
        if big == 'years' and n > 30: continue
        addnum(f't_{small}_{n}{big}', f'How many {small} are in {n} {big}' + (' (of 365 days)?' if big == 'years' else '?'), n * f, small, f'{n} × {f:,} = {n*f:,} {small}.')
for a, b in [(1000000, 37), (500000, 13), (100000, 7), (250000, 17), (1000000, 64), (750000, 29), (90000, 11), (360000, 23), (1000, 3.7), (5000000, 365)]:
    v = round(a / b, 1)
    addnum(f'div_{a}_{str(b).replace(".","p")}', f'What is {a:,} ÷ {b:g}?', v, '', f'{a:,} ÷ {b:g} ≈ {fmtn(v)}.')

# ---------- order: spread categories evenly so every day gets a mix ----------
cats = {}
for q in OUT: cats.setdefault(q[8], []).append(q)
for k in cats: R.shuffle(cats[k])
total = len(OUT); taken = {k: 0 for k in cats}; order = []
while len(order) < total:
    # pick the category furthest behind its fair share
    k = min((k for k in cats if taken[k] < len(cats[k])), key=lambda k: (taken[k] + 0.5) / len(cats[k]))
    order.append(cats[k][taken[k]]); taken[k] += 1

with open('questions.js', 'w') as f:
    f.write('/* Ninety Sure question bank: %d questions. Generated by build.py. */\n' % total)
    f.write('const QUESTIONS=' + json.dumps(order, ensure_ascii=False, separators=(',', ':')) + ';\n')
print('total', total, {k: len(v) for k, v in cats.items()})
