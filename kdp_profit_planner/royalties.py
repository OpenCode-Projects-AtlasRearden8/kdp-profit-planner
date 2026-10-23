"""KDP-style printing cost and royalty math.

Royalty rates reflect Amazon's standard KDP terms: 60% of list price
minus printing cost on the Amazon store; 40% via expanded distribution.
All figures are local estimates for the US marketplace."""

from __future__ import annotations

from dataclasses import dataclass

from .rates import (
    FORMAT_HARDCOVER,
    FORMAT_PAPERBACK,
    INK_BLACK,
    INK_COLOR,
    TrimSize,
    printing_rate,
)

ROYALTY_PAPERBACK_AMAZON = 0.60
ROYALTY_PAPERBACK_EXPANDED = 0.40
ROYALTY_HARDCOVER = 0.60
EXPANDED_DISTRIBUTION = "expanded"
AMAZON_DISTRIBUTION = "amazon"

DISTRIBUTIONS = (AMAZON_DISTRIBUTION, EXPANDED_DISTRIBUTION)


def distribution_royalty_rate(format: str, distribution: str) -> float:
    if distribution not in DISTRIBUTIONS:
        raise ValueError(f"unknown distribution channel: {distribution}")
    if format == FORMAT_HARDCOVER:
        if distribution == EXPANDED_DISTRIBUTION:
            raise ValueError("expanded distribution is not available for hardcover")
        return ROYALTY_HARDCOVER
    if format != FORMAT_PAPERBACK:
        raise ValueError(f"unknown format: {format}")
    return (
        ROYALTY_PAPERBACK_EXPANDED
        if distribution == EXPANDED_DISTRIBUTION
        else ROYALTY_PAPERBACK_AMAZON
    )


def printing_cost(
    pages: int,
    format: str,
    trim: TrimSize | str | None = None,
    ink: str = INK_BLACK,
    large_trim: bool | None = None,
    fixed_cost: float | None = None,
    per_page_cost: float | None = None,
) -> float:
    """Per-unit KDP printing cost for a book."""
    if pages <= 0:
        raise ValueError("pages must be positive")
    from_trim = bool(getattr(trim, "large_trim", False))
    large_effective = from_trim if large_trim is None else bool(large_trim)
    fixed, per_page = printing_rate(
        format, ink, large_effective, fixed_cost, per_page_cost
    )
    return round(fixed + per_page * pages, 2)


@dataclass(frozen=True)
class RoyaltyResult:
    format: str
    distribution: str
    list_price: float
    pages: int
    printing_cost: float
    royalty_rate: float
    royalty: float
    min_list_price: float

    def as_dict(self) -> dict:
        return {
            "format": self.format,
            "distribution": self.distribution,
            "list_price": self.list_price,
            "pages": self.pages,
            "printing_cost": self.printing_cost,
            "royalty_rate": self.royalty_rate,
            "royalty": self.royalty,
            "min_list_price": self.min_list_price,
        }


def royalty_for_price(
    list_price: float,
    pages: int,
    format: str,
    trim: TrimSize | str | None = None,
    ink: str = INK_BLACK,
    distribution: str = AMAZON_DISTRIBUTION,
    fixed_cost: float | None = None,
    per_page_cost: float | None = None,
) -> RoyaltyResult:
    """Compute the royalty earned per unit at a given list price."""
    if list_price <= 0:
        raise ValueError("list_price must be positive")
    cost = printing_cost(
        pages, format, trim, ink, fixed_cost=fixed_cost, per_page_cost=per_page_cost
    )
    rate = distribution_royalty_rate(format, distribution)
    net = 0.0
    if format == FORMAT_HARDCOVER:
        min_price = cost / ROYALTY_HARDCOVER
    else:
        min_price = cost / distribution_royalty_rate(format, AMAZON_DISTRIBUTION)
    if list_price >= min_price:
        net = round(rate * list_price - cost, 2)
    return RoyaltyResult(
        format=format,
        distribution=distribution,
        list_price=round(list_price, 2),
        pages=pages,
        printing_cost=cost,
        royalty_rate=rate,
        royalty=net,
        min_list_price=round(min_price, 2),
    )


def price_scan(
    pages: int,
    format: str,
    start: float,
    end: float,
    step: float,
    trim: TrimSize | str | None = None,
    ink: str = INK_BLACK,
    distribution: str = AMAZON_DISTRIBUTION,
    fixed_cost: float | None = None,
    per_page_cost: float | None = None,
) -> list[RoyaltyResult]:
    """Royalty at each price from start..end inclusive."""
    if start <= 0 or end < start or step <= 0:
        raise ValueError("need 0 < start <= end and step > 0")
    results = []
    price = start
    while price <= end + 1e-9:
        results.append(
            royalty_for_price(
                price,
                pages,
                format,
                trim,
                ink,
                distribution,
                fixed_cost=fixed_cost,
                per_page_cost=per_page_cost,
            )
        )
        price = round(price + step, 2)
    return results
