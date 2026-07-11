"""
Starforce 0->22 exact optimization: Lv250 Eternal hat, GMS v269 system.
MVP Black (10% <=16*), guild altar star-catch (x1.05), replacement 2b.

Data sources (cross-verified):
- Rates: GMS v.264 patch notes (official) == maplestorywiki == tadeucci rates.js
- Cost formula: tadeucci simulator.js (in-game verified at lv250) == misaomaki
- Enhancement Mode table: tadeucci rates.js (in-game measured, v269)
- Boom restore stars: v.264 patch notes (15-19->12, 20->15, 21->17)
"""
import numpy as np, json, itertools

LT = 250            # level tier = floor(250/10)*10
RC = 2.0e9          # replacement cost (clean eternal hat)
CATCH = 1.05
TARGET = 22

# ---- base success rates (index = current star) --------------------------------
SUCC_BASE = [.95,.90,.85,.85,.80,.75,.70,.65,.60,.55,.50,.45,.40,.35,.30,
             .30,.30,.15,.15,.15,.30,.15]
BOOM_BASE = [0]*15 + [.021,.021,.068,.068,.085,.105,.1275]

# ---- cost coefficients ---------------------------------------------------------
COEF = {}
for s in range(10): COEF[s] = (2500, 1.0, 1.0)
COEF[10] = (40000,2.7,1.0); COEF[11] = (22000,2.7,1.0); COEF[12] = (15000,2.7,1.0)
COEF[13] = (11000,2.7,1.0); COEF[14] = (7500,2.7,1.0)
COEF[15] = (20000,2.7,1.0); COEF[16] = (20000,2.7,1.0)
COEF[17] = (20000,2.7,4/3); COEF[18] = (20000,2.7,20/7); COEF[19] = (20000,2.7,40/9)
COEF[20] = (20000,2.7,1.0); COEF[21] = (20000,2.7,8/5)

def base_cost(s):
    div, expo, mult = COEF[s]
    raw = mult * LT**3 * (s+1)**expo / div + 10
    return 100.0 * round(raw)

# ---- enhancement mode table: star -> option -> (cost_mult, succ, boom) ---------
# 15-17*: M1/M2/M3 + SG (classic safeguard = 0% boom, +2x base surcharge)
# 18-21*: M1/M2/M3/M4
EM = {
 15: {'M1':(1,.30,.021),'M2':(1.5,.30,.014),'M3':(2.5,.30,.007),'SG':('SG',.30,0.0)},
 16: {'M1':(1,.30,.021),'M2':(1.5,.30,.014),'M3':(2.5,.30,.007),'SG':('SG',.30,0.0)},
 17: {'M1':(1,.15,.068),'M2':(1.5,.15,.0425),'M3':(2.5,.15,.017),'SG':('SG',.15,0.0)},
 18: {'M1':(1,.15,.068),'M2':(2,.12,.044),'M3':(3.5,.10,.018),'M4':(6.5,.08,0.0)},
 19: {'M1':(1,.15,.085),'M2':(2,.12,.0616),'M3':(3.5,.10,.036),'M4':(6.5,.08,0.0)},
 20: {'M1':(1,.30,.105),'M2':(2,.25,.075),'M3':(3.5,.20,.04),'M4':(6.5,.15,0.0)},
 21: {'M1':(1,.15,.1275),'M2':(2,.12,.088),'M3':(3.5,.10,.045),'M4':(6.5,.08,0.0)},
}
DECISION_STARS = list(range(15, 22))
OPTIONS = {s: list(EM[s].keys()) for s in DECISION_STARS}

def boom_to(s):
    if s < 20: return 12
    if s == 20: return 15
    return 17

MVP = 0.10  # MVP Black, taps at star <= 16

def tap_params(s, opt, event='none'):
    """-> (tap_cost, p_succ, p_maint, p_boom) with MVP/guild-catch/event applied.
    event: 'none' | '30off' (cost -30% only) | 'ssf' (cost -30% AND boom -30%)."""
    cost_ev = event in ('ssf', '30off')
    boom_ev = event == 'ssf'
    if s < 15:
        mult = 1.0 - (MVP if s <= 16 else 0.0)
        if cost_ev: mult -= 0.30
        succ, boom = SUCC_BASE[s], 0.0
    else:
        cm, succ, boom = EM[s][opt]
        if cm == 'SG':   # classic safeguard: surcharge on top, never discounted
            mult = 1.0 - (MVP if s <= 16 else 0.0)
            if cost_ev: mult -= 0.30
            mult += 2.0
        else:
            mult = cm - (MVP if s <= 16 else 0.0)
            if cost_ev: mult *= 0.70
        if boom_ev:  # 30% boom reduction at <=21*
            boom *= 0.70
    # guild altar star catch
    s2 = min(1.0, succ * CATCH)
    maint = 1.0 - succ - boom
    left = 1.0 - s2
    tot = maint + boom
    if tot > 0: maint, boom = maint*left/tot, boom*left/tot
    else: maint, boom = left, 0.0
    cost = round(base_cost(s) * mult)
    return cost, s2, maint, boom

# ---- exact expected cost for a fixed policy ------------------------------------
def solve_policy(policy, rc=RC, event='none', extras=False):
    """policy: dict star->opt for 15..21. Exact E[cost 0->22], via linear solve."""
    P = {}
    for s in range(TARGET):
        opt = policy[s] if s in policy else None
        P[s] = tap_params(s, opt, event)
    # unknowns E[12..21]
    idx = {s: i for i, s in enumerate(range(12, 22))}
    n = len(idx)
    A = np.zeros((n, n)); b = np.zeros(n)
    for s in range(12, 22):
        c, ps, pm, pb = P[s]
        i = idx[s]
        A[i, i] += (1 - pm)
        if s + 1 < 22: A[i, idx[s+1]] -= ps
        if pb > 0:
            A[i, idx[boom_to(s)]] -= pb
            b[i] += pb * rc
        b[i] += c
    E = np.linalg.solve(A, b)
    Emap = {s: E[idx[s]] for s in range(12, 22)}
    Emap[22] = 0.0
    for s in range(11, -1, -1):
        c, ps, pm, pb = P[s]
        Emap[s] = c / ps + Emap[s+1]
    if not extras:
        return Emap[0]
    # expected taps & booms from 0: same system, different rewards
    def solve_reward(reward):  # reward(s, P[s]) = per-visit expected reward
        A2 = np.zeros((n, n)); b2 = np.zeros(n)
        for s in range(12, 22):
            c, ps, pm, pb = P[s]
            i = idx[s]
            A2[i, i] += (1 - pm)
            if s+1 < 22: A2[i, idx[s+1]] -= ps
            if pb > 0: A2[i, idx[boom_to(s)]] -= pb
            b2[i] += reward(s, P[s])
        V = np.linalg.solve(A2, b2)
        Vm = {s: V[idx[s]] for s in range(12, 22)}; Vm[22] = 0.0
        for s in range(11, -1, -1):
            c, ps, pm, pb = P[s]
            Vm[s] = reward(s, P[s]) / ps + Vm[s+1]
        return Vm[0]
    taps  = solve_reward(lambda s, p: 1.0)
    booms = solve_reward(lambda s, p: p[3])
    meso_taps = solve_reward(lambda s, p: p[0])       # enhancement meso only
    return dict(E=Emap[0], Emap=Emap, taps=taps, booms=booms,
                meso_taps=meso_taps, spare_cost=booms*rc)

# ---- exhaustive enumeration -----------------------------------------------------
def enumerate_policies(rc=RC, event='none'):
    best, best_pol, results = None, None, []
    combos = itertools.product(*[OPTIONS[s] for s in DECISION_STARS])
    for combo in combos:
        pol = dict(zip(DECISION_STARS, combo))
        E = solve_policy(pol, rc, event)
        results.append((E, combo))
        if best is None or E < best: best, best_pol = E, pol
    results.sort(key=lambda t: t[0])
    return best, best_pol, results

# ---- value iteration (for sensitivity sweep; cross-checked vs enumeration) -----
def value_iter(rc, event='none'):
    params = {s: {opt: tap_params(s, opt, event) for opt in OPTIONS[s]}
              for s in DECISION_STARS}
    sub = {s: tap_params(s, None, event) for s in range(15)}
    E = np.zeros(TARGET + 1)
    for _ in range(100000):
        new = E.copy()
        for s in range(TARGET - 1, -1, -1):
            if s < 15:
                c, ps, pm, pb = sub[s]
                new[s] = (c + ps * new[s+1]) / (1 - pm)
            else:
                vals = []
                for opt, (c, ps, pm, pb) in params[s].items():
                    v = (c + ps * new[s+1] + pb * (rc + new[boom_to(s)])) / (1 - pm)
                    vals.append(v)
                new[s] = min(vals)
        if np.max(np.abs(new - E)) < 1.0: E = new; break
        E = new
    choice = {}
    for s in DECISION_STARS:
        best_o, best_v = None, None
        for opt, (c, ps, pm, pb) in params[s].items():
            v = (c + ps * E[s+1] + pb * (rc + E[boom_to(s)])) / (1 - pm)
            if best_v is None or v < best_v - 1e-9: best_v, best_o = v, opt
        choice[s] = best_o
    return E[0], choice

# ---- Monte Carlo ----------------------------------------------------------------
def monte_carlo(policy, trials=300_000, rc=RC, event='none', seed=7):
    rng = np.random.default_rng(seed)
    cost = np.zeros(TARGET, dtype=np.float64)
    ps = np.zeros(TARGET); psm = np.zeros(TARGET)
    bto = np.zeros(TARGET, dtype=np.int64)
    for s in range(TARGET):
        c, a, m, b = tap_params(s, policy.get(s), event)
        cost[s], ps[s], psm[s], bto[s] = c, a, a + m, boom_to(s)
    star = np.zeros(trials, dtype=np.int64)
    total = np.zeros(trials); booms = np.zeros(trials, dtype=np.int64)
    taps = np.zeros(trials, dtype=np.int64)
    per_star_spend = np.zeros(TARGET)
    active = np.arange(trials)
    it = 0
    while active.size and it < 500000:
        it += 1
        st = star[active]
        total[active] += cost[st]
        np.add.at(per_star_spend, st, cost[st])
        taps[active] += 1
        r = rng.random(active.size)
        succ = r < ps[st]
        boom = r >= psm[st]
        star[active[succ]] += 1
        bidx = active[boom]
        star[bidx] = bto[st[boom]]
        booms[bidx] += 1
        total[bidx] += rc
        done = star[active] >= TARGET
        active = active[~done]
    return dict(total=total, booms=booms, taps=taps, per_star_spend=per_star_spend / trials)

def pct(a, q): return float(np.percentile(a, q))

# =============================== RUN =============================================
if __name__ == '__main__':
    out = {}

    # base cost table
    out['base_costs'] = {s: base_cost(s) for s in range(TARGET)}

    # option table (cost + rates after MVP/catch), for display
    opt_table = {}
    for s in DECISION_STARS:
        opt_table[s] = {}
        for opt in OPTIONS[s]:
            c, a, m, b = tap_params(s, opt)
            opt_table[s][opt] = dict(cost=c, succ=a, maint=m, boom=b)
    out['options'] = opt_table

    print('=== enumerating 4^7 policies (base, RC=2b) ===')
    bestE, bestPol, ranking = enumerate_policies()
    viE, viPol = value_iter(RC)
    print('enumeration best:', bestE/1e9, bestPol)
    print('value-iter  best:', viE/1e9, viPol)
    assert abs(bestE - viE) < 5e6, 'VI vs enumeration mismatch'

    named = {
        'optimal': bestPol,
        'no_protection': {s: 'M1' for s in DECISION_STARS},
        'classic_sg_15_17': {15:'SG',16:'SG',17:'SG',18:'M1',19:'M1',20:'M1',21:'M1'},
        'max_protection': {15:'SG',16:'SG',17:'SG',18:'M4',19:'M4',20:'M4',21:'M4'},
    }
    out['policies'] = {}
    for name, pol in named.items():
        ex = solve_policy(pol, extras=True)
        mc = monte_carlo(pol, trials=300_000)
        t = mc['total']
        out['policies'][name] = dict(
            policy={str(s): pol[s] for s in DECISION_STARS},
            E=ex['E'], taps=ex['taps'], booms=ex['booms'],
            meso_taps=ex['meso_taps'], spare_cost=ex['spare_cost'],
            mc_mean=float(t.mean()), median=pct(t,50), p10=pct(t,10),
            p25=pct(t,25), p75=pct(t,75), p90=pct(t,90), p99=pct(t,99),
            boom_mean=float(mc['booms'].mean()),
            boom_dist=np.bincount(mc['booms'], minlength=16)[:16].tolist(),
            per_star_spend=mc['per_star_spend'].tolist(),
            hist=np.histogram(np.clip(t, 0, 200e9), bins=80, range=(0, 200e9))[0].tolist(),
        )
        print(f"{name:18s} E={ex['E']/1e9:7.2f}b  med={pct(t,50)/1e9:7.2f}b  "
              f"p90={pct(t,90)/1e9:7.2f}b  booms={ex['booms']:.2f}")

    # top-10 policies
    out['top10'] = [dict(E=E, policy=dict(zip(map(str, DECISION_STARS), combo)))
                    for E, combo in ranking[:10]]
    # how much worse are single-star deviations from optimal?
    dev = {}
    for s in DECISION_STARS:
        dev[str(s)] = {}
        for opt in OPTIONS[s]:
            pol = dict(bestPol); pol[s] = opt
            dev[str(s)][opt] = solve_policy(pol)
    out['deviations'] = dev

    print('=== sensitivity sweep: replacement cost 0..20b ===')
    grid = [i * 0.25e9 for i in range(0, 81)]
    sens = []
    for rc in grid:
        E, choice = value_iter(rc)
        sens.append(dict(rc=rc, E=E, choice={str(s): choice[s] for s in DECISION_STARS}))
    out['sensitivity'] = sens

    print('=== SSF event scenario ===')
    ssfE, ssfPol = value_iter(RC, event='ssf')
    ex = solve_policy(ssfPol, event='ssf', extras=True)
    mc = monte_carlo(ssfPol, trials=300_000, event='ssf')
    t = mc['total']
    out['ssf'] = dict(policy={str(s): ssfPol[s] for s in DECISION_STARS},
                      E=ex['E'], taps=ex['taps'], booms=ex['booms'],
                      median=pct(t,50), p90=pct(t,90),
                      no_prot_E=solve_policy({s:'M1' for s in DECISION_STARS}, event='ssf'))
    print('SSF optimal:', ssfE/1e9, ssfPol)

    with open('results.json', 'w') as f:
        json.dump(out, f)
    print('saved results.json')
