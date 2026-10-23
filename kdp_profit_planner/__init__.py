"""kdp-profit-planner: a local-first KDP publishing plan calculator.

Turns a word count into page counts by trim size, printing costs,
paperback/hardcover royalties, break-even units, series price
scenarios, and monthly profit projections. No network access, ever.

Copyright (c) 2026 Asdale Dynamics, LLC. MIT licensed.
"""

from .breakeven import breakeven_units, profit_at_units
from .pages import estimate_pages
from .projections import monthly_projection, months_to_profit
from .rates import FORMAT_HARDCOVER, FORMAT_PAPERBACK, INK_BLACK, INK_COLOR, TRIMS
from .royalties import price_scan, printing_cost, royalty_for_price
from .scenarios import Book, SeriesScenario, compare_series_prices
from .version import __version__

__all__ = [
    "__version__",
    "Book",
    "SeriesScenario",
    "TRIMS",
    "FORMAT_PAPERBACK",
    "FORMAT_HARDCOVER",
    "INK_BLACK",
    "INK_COLOR",
    "breakeven_units",
    "compare_series_prices",
    "estimate_pages",
    "monthly_projection",
    "months_to_profit",
    "price_scan",
    "printing_cost",
    "profit_at_units",
    "royalty_for_price",
]
