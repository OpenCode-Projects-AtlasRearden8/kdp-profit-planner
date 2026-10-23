# STATUS.md

## What was built

**kdp-profit-planner** — an installable, local-first Python CLI that turns
a raw word count into a KDP publishing plan. Built by Asdale Dynamics, LLC
as a small-business/author tool. All math runs on the machine: no network
calls, no accounts, no API keys, no telemetry, no personal data anywhere
in the codebase.

Features:

- **`pages`** — estimate final page counts from a word count across 12
  supported trim sizes (words/page tables, front matter, even-page
  rounding, KDP page-limit warnings).
- **`cost`** — per-unit KDP printing costs by format (paperback/hardcover),
  ink (black/color), and trim tier (standard/large), with overrides.
- **`royalty`** — royalty per unit at a list price, 60% Amazon rate (40%
  paperback expanded distribution), with minimum-viable-price warnings.
- **`prices`** — royalty scan across a price range, one row per price
  point with a profitable/unprofitable flag.
- **`breakeven`** — units needed to cover upfront production costs
  (editing, cover, ads) plus profit at 2x break-even.
- **`compare`** — series launch price scenarios: per-book printing cost,
  royalty, minimum price, break-even units, and launch totals per
  candidate list price.
- **`project`** — monthly royalty projections with optional growth rate,
  ongoing monthly costs, and upfront costs booked against month 1.
- **`plan`** — one command: word count + trim + price -> page estimate,
  printing cost, royalty, break-even, and a monthly projection.
- **`trims`** — reference table of trim sizes and words/page estimates.

Reference rates (editable in `kdp_profit_planner/rates.py` and at runtime
via `--fixed-cost`/`--per-page`): KDP US print-cost rates as publicly
listed in the June 2023 update — paperback black ink `$0.85 + $0.012/page`
(standard trim), hardcover `$5.65 + $0.012/page`, color variants included.
Royalty = 60% of list minus printing cost on the Amazon store; 40% for
paperback expanded distribution.

## Layout

```
kdp_profit_planner/   package (rates, pages, printing, royalties,
                      breakeven, scenarios, projections, CLI)
tests/                pytest suite (75 tests)
pyproject.toml        packaging + entry point
LICENSE               MIT, Copyright (c) 2026 Asdale Dynamics, LLC
README.md             usage and plain-English math explainer
```

## How to run

```bash
pip install .            # or: pip install -e . for development
kdp-profit-planner --help
kdp-profit-planner plan 80000 --trim 6x9 --price 12.99 --upfront 750 --units 25
python -m kdp_profit_planner trims    # module entry also works
pytest                                  # run the test suite
```

Worst-case estimate for the flagship playbook: an 80,000-word manuscript
at 6x9 (~280 pages) priced at $12.99 prints for $4.21, earns $3.58/unit,
breaks even on $750 upfront after 210 units, and turns cumulative profit
around month 9 at a steady 25 units/month.

## Verification results

- `python3 -m pytest -q` → **75 passed** (unit tests for every module +
  end-to-end CLI tests via the argument parser, including error paths).
- Console script `kdp-profit-planner` verified installed via
  `pip install -e .`; exercised `--version`, `trims`, `pages`, `plan`,
  `compare`, `project`, `royalty`, `cost`, `prices`, `breakeven`, plus
  Python API calls and `python -m kdp_profit_planner`.
- Error paths verified: bad prices/word counts page limits return exit
  code 2 with a readable message on stderr; expanded-distribution
  hardcover is rejected.

## Known gaps

- Print-cost constants reflect KDP's published June 2023 US rates;
  Amazon updates these periodically and marketplace rates outside the US
  differ. Re-check against the KDP printing-cost page before pricing, or
  override with `--fixed-cost`/`--per-page`.
- Words-per-page figures are heuristic estimates for a typical 11 pt
  KDP interior; real page counts depend on font, leading, and graphics.
- `months_to_profit` (and the milestone line in `project`) uses a
  flat-rate heuristic; with a positive growth rate the actual crossover
  happens earlier than shown.
- Expanded distribution modeling is paperback-only, matching KDP eligibility.
- No ebook/Kindle (70% / 35%) royalty model yet, and no delivery-fee
  modeling for large ebook files.
