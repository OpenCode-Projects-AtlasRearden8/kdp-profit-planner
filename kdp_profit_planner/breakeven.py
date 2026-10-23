"""Break-even units: how many sales to recover upfront production costs."""

from __future__ import annotations

from math import ceil


def breakeven_units(fixed_costs: float, royalty_per_unit: float) -> int:
    """Number of units needed so cumulative royalties cover fixed costs.

    Returns 0 when there are no fixed costs. Raises ValueError if the
    royalty is not positive while fixed costs are outstanding.
    """
    if fixed_costs < 0:
        raise ValueError("fixed_costs cannot be negative")
    if fixed_costs == 0:
        return 0
    if royalty_per_unit <= 0:
        raise ValueError(
            "royalty_per_unit must be positive to break even (raise the list price)"
        )
    return ceil(fixed_costs / royalty_per_unit)


def profit_at_units(
    units: int, royalty_per_unit: float, fixed_costs: float = 0.0
) -> float:
    """Total profit after a given number of unit sales."""
    if units < 0:
        raise ValueError("units cannot be negative")
    return round(units * royalty_per_unit - fixed_costs, 2)
