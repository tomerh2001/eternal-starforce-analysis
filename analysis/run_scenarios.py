"""Full analysis for both scenarios: EVENT (ssf, primary) and off-event (secondary),
plus a cost-only 30%-off variant summary. Writes results2.json."""
import json, numpy as np
from compute import (tap_params, solve_policy, enumerate_policies, value_iter,
                     monte_carlo, base_cost, DECISION_STARS, OPTIONS, RC, TARGET, pct)

STARS = [str(s) for s in DECISION_STARS]

def full_scenario(event, named_policies, sweep=True):
    out = {}
    bestE, bestPol, ranking = enumerate_policies(RC, event)
    viE, viPol = value_iter(RC, event)
    assert abs(bestE - viE) < 5e6, (bestE, viE)
    out['optimalPolicy'] = {str(s): bestPol[s] for s in DECISION_STARS}
    out['top3'] = [dict(E=E, policy=dict(zip(STARS, c))) for E, c in ranking[:3]]

    pols = dict(named_policies); pols['optimal'] = bestPol
    out['policies'] = {}
    for name, pol in pols.items():
        ex = solve_policy(pol, RC, event, extras=True)
        mc = monte_carlo(pol, trials=300_000, event=event)
        t = mc['total']
        out['policies'][name] = dict(
            policy={str(s): pol[s] for s in DECISION_STARS},
            E=ex['E'], taps=ex['taps'], booms=ex['booms'],
            meso_taps=ex['meso_taps'], spare_cost=ex['spare_cost'],
            median=pct(t,50), p10=pct(t,10), p25=pct(t,25), p75=pct(t,75),
            p90=pct(t,90), p99=pct(t,99),
            boom_dist=np.bincount(mc['booms'], minlength=16)[:16].tolist(),
            per_star_spend=mc['per_star_spend'].tolist(),
            hist=np.histogram(np.clip(t,0,200e9), bins=80, range=(0,200e9))[0].tolist())
        print(f"[{event}] {name:16s} E={ex['E']/1e9:7.2f}b med={pct(t,50)/1e9:7.2f}b "
              f"p90={pct(t,90)/1e9:7.2f}b booms={ex['booms']:.2f}")

    dev = {}
    for s in DECISION_STARS:
        dev[str(s)] = {}
        for opt in OPTIONS[s]:
            pol = dict(bestPol); pol[s] = opt
            dev[str(s)][opt] = solve_policy(pol, RC, event)
    out['deviations'] = dev

    if sweep:
        seg = {s: [] for s in STARS}
        cur = {s: None for s in STARS}; start = {s: 0 for s in STARS}
        grid = [i*0.25e9 for i in range(81)]
        for rc in grid:
            _, choice = value_iter(rc, event)
            for s in STARS:
                c = choice[int(s)]
                if cur[s] is None: cur[s], start[s] = c, rc
                elif c != cur[s]:
                    seg[s].append([start[s], rc, cur[s]]); cur[s], start[s] = c, rc
        for s in STARS: seg[s].append([start[s], 20e9, cur[s]])
        out['sensitivity'] = seg

    # option table as modeled under this event
    out['options'] = {s: {o: dict(zip(('cost','succ','maint','boom'),
                     tap_params(int(s), o, event))) for o in OPTIONS[int(s)]} for s in STARS}
    return out

M1 = {s: 'M1' for s in DECISION_STARS}
OFFPOL = {15:'M1',16:'M1',17:'M1',18:'M1',19:'M1',20:'M3',21:'M3'}
named_event = {'no_protection': M1, 'off_event_policy': OFFPOL,
               'classic_sg_15_17': {15:'SG',16:'SG',17:'SG',18:'M1',19:'M1',20:'M1',21:'M1'},
               'max_protection': {15:'SG',16:'SG',17:'SG',18:'M4',19:'M4',20:'M4',21:'M4'}}
named_base = {'no_protection': M1,
              'classic_sg_15_17': {15:'SG',16:'SG',17:'SG',18:'M1',19:'M1',20:'M1',21:'M1'},
              'max_protection': {15:'SG',16:'SG',17:'SG',18:'M4',19:'M4',20:'M4',21:'M4'}}

res = {}
print('=== EVENT (30% off + 30% boom reduction) ===')
res['event'] = full_scenario('ssf', named_event, sweep=True)
print('=== OFF-EVENT ===')
res['base'] = full_scenario('none', named_base, sweep=True)

print('=== 30% off only (no boom reduction) ===')
E30, pol30 = value_iter(RC, '30off')
ex30 = solve_policy(pol30, RC, '30off', extras=True)
mc30 = monte_carlo(pol30, trials=200_000, event='30off')
res['off30'] = dict(policy={str(s): pol30[s] for s in DECISION_STARS}, E=ex30['E'],
                    booms=ex30['booms'], taps=ex30['taps'],
                    median=pct(mc30['total'],50), p90=pct(mc30['total'],90))
print('30off optimal:', E30/1e9, pol30)

res['base_costs'] = {str(s): base_cost(s) for s in range(TARGET)}
json.dump(res, open('results2.json','w'))
print('saved results2.json')
