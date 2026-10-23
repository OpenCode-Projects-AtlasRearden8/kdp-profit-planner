"""Monthly profit projections."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class MonthProjection:
    month: int
    units: int
    gross_royalty: float
    costs: float
    net: float
    cumulative_net: float

    def as_dict(self) -> dict:
        return {
            "month": self.month,
            "units": self.units,
            "gross_royalty": self.gross_royalty,
            "costs": self.costs,
            "net": self.net,
            "cumulative_net": self.cumulative_net,
        }


def monthly_projection(
    monthly_units: int,
    royalty_per_unit: float,
    months: int = 12,
    growth_rate: float = 0.0,
    monthly_cost: float = 0.0,
    upfront_costs: float = 0.0,
) -> list[MonthProjection]:
    """Project months of earnings, applying `growth_rate` per month
    (0.05 = 5% more units each month). Month 1 carries the upfront costs
    so the projection shows when the backlist turns cumulative profit."""
    if monthly_units < 0:
        raise ValueError("monthly_units cannot be negative")
    if months <= 0:
        raise ValueError("months must be at least 1")
    if monthly_cost < 0:
        raise ValueError("monthly_cost cannot be negative")
    if upfront_costs < 0:
        raise ValueError("upfront_costs cannot be negative")
    if royalty_per_unit < 0:
        raise ValueError("royalty_per_unit cannot be negative")

    cumulative = -round(upfront_costs, 2)
    projections = []
    for month in range(1, months + 1):
        units = int(round(monthly_units * (1 + growth_rate) ** (month - 1)))
        gross = round(units * royalty_per_unit, 2)
        net = round(gross - monthly_cost, 2)
        cumulative = round(cumulative + net, 2)
        projections.append(
            MonthProjection(
                month=month,
                units=units,
                gross_royalty=gross,
                costs=round(monthly_cost, 2),
                net=net,
                cumulative_net=cumulative,
            )
        )
    return projections


def months_to_profit(
    monthly_units: int,
    royalty_per_unit: float,
    upfront_costs: float,
    monthly_cost: float = 0.0,
    max_months: int = 240,
) -> int | None:
    """First month where cumulative net profit turns positive."""
    if upfront_costs <= 0:
        return 0
    monthly_net = (monthly_units * royalty_per_unit) - monthly_cost
    if monthly_net <= 0:
        return None
    months = int(-(-upfront_costs // monthly_net))
    return months if months <= max_months else None
