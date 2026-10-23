# kdp-profit-planner

Author-tool CLI that turns a word count into a KDP publishing plan.

Estimate page counts by trim size, walk through paperback and hardcover
royalty math across price points, see printing costs, work out
break-even units, compare list-price scenarios for a series launch, and
project monthly profits — all computed locally on your machine. No
accounts, no network calls, no data leaves the folder.

Built by [Asdale Dynamics, LLC](https://dylanasdale.github.io) — beginner
friendly AI education, in plain English, step by step, never condescending.
This is a planning and estimating tool; it is not affiliated with Amazon,
and its numbers are estimates, not guarantees. Verify final figures in
your KDP account before you price a book.

## Install

Requires Python 3.9+.

```bash
pip install .
```

For development:

```bash
pip install -e .
pip install pytest
```

## Quick start

```bash
# Page counts for an 80,000-word manuscript, across every trim size
kdp-profit-planner pages 80000

# Printing cost for a 280-page paperback
kdp-profit-planner cost --pages 280

# Royalty per unit at $12.99
kdp-profit-planner royalty --price 12.99 --pages 280

# Scan royalties from $7.99 to $15.99 in $1.00 steps
kdp-profit-planner prices --pages 280 --from 7.99 --to 15.99 --step 1.00

# Break-even units on $500 of upfront editing/cover costs
kdp-profit-planner breakeven --upfront 500 --price 9.99 --pages 280

# Compare list prices for a 3-book series launch
kdp-profit-planner compare \
  --books "AI Tools 101:280,Agents for Everyone:320,Local AI at Home:300" \
  --prices 9.99,12.99,14.99 --units-per-book 40

# Project 12 months of earnings at 25 units/month
kdp-profit-planner project --units 25 --price 12.99 --pages 280 --months 12

# Full plan: word count + price -> pages, costs, royalties, projections
kdp-profit-planner plan 80000 --trim 6x9 --price 12.99 --upfront 750 --units 25
```

## The math, in plain English

- **Page count** = `ceil(words / words-per-page)` for your trim size,
  plus front matter (title page, TOC, and so on), rounded up to an even
  page count. Words-per-page estimates assume a typical 11 pt KDP
  interior; a real layout can drift either way.
- **Printing cost** = fixed cost + per-page cost. Based on Amazon KDP's
  publicly listed US rates (June 2023 update), for example a standard
  black-ink paperback is `$0.85 + $0.012/page`, and a hardcover is
  `$5.65 + $0.012/page`. Use `--fixed-cost`/`--per-page` to override.
- **Royalty** = `rate x list price - printing cost`. Amazon pays a 60%
  royalty on paperbacks and hardcovers sold through the Amazon store,
  and 40% for paperback expanded distribution.
- **Minimum price** = `printing cost / 0.60`. Below this, Amazon does
  not pay a royalty at all.
- **Break-even units** = `ceil(upfront cost / royalty per unit)`.
- **Monthly projection** = units x royalty per month, with an optional
  growth rate; month 1 carries your upfront costs so you can see when
  the book turns cumulative profit.

## Commands

| Command    | What it does                                          |
| ---------- | ----------------------------------------------------- |
| `trims`    | List supported trim sizes and words-per-page estimates |
| `pages`    | Estimate page counts from a word count               |
| `cost`     | Per-unit printing cost                               |
| `royalty`  | Royalty per unit at a list price                     |
| `prices`   | Scan royalties across a price range                  |
| `breakeven`| Units needed to cover upfront costs                  |
| `compare`  | Series launch price scenarios                        |
| `project`  | Monthly royalty projections                          |
| `plan`     | One-command full publishing plan                     |

Run `kdp-profit-planner <command> --help` for every option.

## Python API

```python
from kdp_profit_planner import estimate_pages, royalty_for_price, breakeven_units

pages = estimate_pages(80000, "6x9")          # 280
r = royalty_for_price(12.99, pages, "paperback")
units = breakeven_units(750.0, r.royalty)     # 210
```

## Why local-first

Your manuscript plans, pricing strategy, and production budgets are
business information. This tool runs entirely in your terminal: there is
no API key, no telemetry, and no upload of anything, ever.

## Testing

```bash
pytest
```

## License

MIT — see [LICENSE](LICENSE). Copyright (c) 2026 Asdale Dynamics, LLC.
