# Eternal Hat 0→22★ — Starforce Strategy (GMS v269)

**📊 Live report: https://tomerh2001.github.io/eternal-starforce-analysis/**

Exact expected-cost optimization of every safeguard decision when starforcing a
Lv 250 Eternal hat from 0★ to 22★ under the new GMS Star Force system
(v.264 revamp + v.269 Enhancement Mode levels 1–4).

## TL;DR

**Tap bare (Level 1) from 0★ to 19★. Use Enhancement Mode Level 3 at 20★ and 21★.
Never classic Safeguard, never Level 4.**

| Strategy | Expected | Median | p90 | Booms |
|---|---|---|---|---|
| **Optimal — Lv3 @ 20–21★ only** | **75.7b** | 59.2b | 149.7b | ~5.0 |
| No protection anywhere | 77.2b | 56.2b | 166.8b | ~7.4 |
| Safeguard 15–17★ (old habit) | 89.4b | 65.3b | 192.8b | ~4.2 |
| Max protection | 198.6b | 177.6b | 337.3b | 0 |

During **Shining Star Force / Special Sunny Sunday**: drop *all* protection —
expected cost falls to **38.5b (−49%)**.

## Assumptions

- Lv 250 Eternal hat, clean spare price **2.0b** (consumed on every boom via trace transfer)
- **MVP Black** (−10% meso on taps ≤16★), **guild castle Enhancement Altar** (passive Star Catch ×1.05)
- Post-revamp mechanics: fails never drop stars; no boom below 15★;
  boom restores 15–19★→12★, 20★→15★, 21★→17★
- No event in the base case (SSF modeled separately)

The report includes a spare-price sensitivity sweep (0–20b) — the policy for
pricier Eternal pieces flips earlier (Lv2 @ 17★ from ~2.25b, Lv4 @ 20★ from
~4.5b, Lv4 @ 21★ from ~6.5b, classic SG 15–17★ only from ~14b).

## Method

- Star count as a Markov chain; expected cost per policy solved exactly (linear system)
- All 4⁷ = 16,384 per-star policies enumerated; optimum cross-checked with value iteration
- 300,000-trial Monte Carlo for medians, percentiles and boom distributions
- Reproduce: `pip install numpy && python3 analysis/compute.py` (writes `results.json`)

## Data sources

- [GMS v.264 patch notes](https://www.nexon.com/maplestory/news/update/32522/updated-11-14-v-264-every-little-thing-every-precious-thing-patch-notes) — revamp rates, trace restore table
- [GMS v.269 patch notes](https://www.nexon.com/maplestory/news/update/41138/v-269-ride-the-lightning-patch-notes) — Enhancement Mode
- [MapleStory Wiki — Star Force Enhancement](https://maplestorywiki.net/w/Star_Force_Enhancement) — discounts, altar, trace mechanics
- [v269 community starforce calculator](https://starforce.tadeucci.dev/) — in-game measured Mode 2–4 rates and cost multipliers
- [Orange Mushroom — KMS ver. 1.2.401](https://orangemushroom.net/2025/03/20/kms-ver-1-2-401-maplestory-next-destiny-weapon-star-force-reorganization/) — upstream renewal reference

## Caveats

Mode 2–4 rates are community-measured (Mode 1 rates and all costs are
official/verified in-game). The weekly free Trace Restoration (Eternal armor =
2,312 pts vs ~126 pts/week cap) is excluded from the model. Not affiliated with
Nexon.
