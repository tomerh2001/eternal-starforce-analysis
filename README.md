# Eternal Hat 0→22★ — Starforce Strategy (GMS v269)

**📊 Live report: https://tomerh2001.github.io/eternal-starforce-analysis/**

**Interactive calculator + analysis.** Exact expected-cost optimization of every
safeguard decision under the new GMS Star Force system (v.264 revamp + v.269
Enhancement Mode levels 1–4), solved live in the browser — value iteration for
the optimal per-star policy, exact linear solves per strategy, and a 50k-run
Monte Carlo for the spreads. Every assumption is adjustable and settings are
encoded into the URL, so a shared link carries them:

- **Event**: 30% off + boom −30% (SSF / Special Sunny Sunday, default) · 30% off only · no event
- **MVP tier** (none / 3% / 5% / 10%), **Star Catch** on/off (guild altar)
- **Spare cost** (0–30b), **item level** (100–300), **star range** (from/to, up to 22★)

Defaults model the way people actually starforce: during the full 30% event.

## TL;DR

**During the event: no safeguard, no modes — Level 1 at every star.**
Protection isn't even good tail insurance there (the p90 doesn't improve).

| Strategy · event on | Expected | Median | p90 | Booms |
|---|---|---|---|---|
| **All bare (optimal)** | **38.5b** | 28.6b | 81.2b | ~3.8 |
| Lv3 @ 20–21★ | 43.5b | 35.2b | 83.1b | ~2.7 |
| Safeguard 15–17★ (old habit) | 50.2b | 37.3b | 104.9b | ~2.4 |
| Max protection | 140.5b | 125.8b | 237.6b | 0 |

**Off-event** (side info — every tap costs ~2×): Level 3 at 20★ and 21★, bare
everywhere else — 75.7b expected. **If the event is cost-only 30% off** (no boom
reduction): Lv2 @ 17★ + Lv3 @ 20–21★ — 55.4b expected.

## Assumptions

- Lv 250 Eternal hat, clean spare price **2.0b** (consumed on every boom via trace transfer)
- **MVP Black** (−10% meso on taps ≤16★), **guild castle Enhancement Altar** (passive Star Catch ×1.05)
- Post-revamp mechanics: fails never drop stars; no boom below 15★;
  boom restores 15–19★→12★, 20★→15★, 21★→17★
- Event modeled per v.269: 30% off cost (multiplicative on the full mode cost,
  safeguard surcharge excluded) + 30% lower destruction ≤21★

The report includes spare-price sensitivity sweeps for both scenarios — during
the event protection only starts at ~3.25b spares (Lv2 @ 17★); off-event it
starts at ~1.5b (Lv3 @ 20–21★).

## Method

- Star count as a Markov chain; expected cost per policy solved exactly (linear system)
- All 4⁷ = 16,384 per-star policies enumerated per scenario; optima cross-checked with value iteration
- 300,000-trial Monte Carlo for medians, percentiles and boom distributions
- Reproduce offline: `pip install numpy && cd analysis && python3 run_scenarios.py` (writes `results2.json`) — the page's in-browser solver is cross-validated against this reference implementation (159 checks)

## Data sources

- [GMS v.264 patch notes](https://www.nexon.com/maplestory/news/update/32522/updated-11-14-v-264-every-little-thing-every-precious-thing-patch-notes) — revamp rates, trace restore table
- [GMS v.269 patch notes](https://www.nexon.com/maplestory/news/update/41138/v-269-ride-the-lightning-patch-notes) — Enhancement Mode, Special Sunny Sunday perks
- [MapleStory Wiki — Star Force Enhancement](https://maplestorywiki.net/w/Star_Force_Enhancement) — discounts, altar, trace mechanics
- [v269 community starforce calculator](https://starforce.tadeucci.dev/) — in-game measured Mode 2–4 rates and cost multipliers
- [Orange Mushroom — KMS ver. 1.2.401](https://orangemushroom.net/2025/03/20/kms-ver-1-2-401-maplestory-next-destiny-weapon-star-force-reorganization/) — upstream renewal reference

## Caveats

Mode 2–4 rates are community-measured (Mode 1 rates and all costs are
official/verified in-game). The weekly free Trace Restoration (Eternal armor =
2,312 pts vs ~126 pts/week cap) is excluded from the model. The rarer 5/10/15
Sunny Sunday is not modeled. Not affiliated with Nexon.
