"""Price-scenario comparison, sized for a series launch."""

from __future__ import annotations

from dataclasses import dataclass

from .breakeven import breakeven_units, profit_at_units
from .royalties import AMAZON_DISTRIBUTION, INK_BLACK, royalty_for_price
from .rates import FORMAT_PAPERBACK, TrimSize


@dataclass(frozen=True)
class Book:
    title: str
    pages: int  # already-estimated page count


@dataclass(frozen=True)
class BookScenario:
    title: str
    pages: int
    list_price: float
    printing_cost: float
    royalty_per_unit: float
    min_list_price: float
    breakeven_units: int | None
    profit_units: int
    profit: float

    def as_dict(self) -> dict:
        return {
            "title": self.title,
            "pages": self.pages,
            "list_price": self.list_price,
            "printing_cost": self.printing_cost,
            "royalty_per_unit": self.royalty_per_unit,
            "min_list_price": self.min_list_price,
            "breakeven_units": self.breakeven_units,
            "profit_units": self.profit_units,
            "profit": self.profit,
        }


@dataclass(frozen=True)
class SeriesScenario:
    list_price: float
    book_count: int
    total_printing_cost: float
    total_royalty_per_launch: float
    per_book: list[BookScenario]

    @property
    def total_profit(self) -> float:
        return round(sum(b.profit for b in self.per_book), 2)


def compare_series_prices(
    books: list[Book],
    list_prices: list[float],
    upfront_cost_per_book: float = 0.0,
    profit_units: int = 0,
    format: str = FORMAT_PAPERBACK,
    trim: TrimSize | str | None = None,
    ink: str = INK_BLACK,
    distribution: str = AMAZON_DISTRIBUTION,
    fixed_cost: float | None = None,
    per_page_cost: float | None = None,
) -> list[SeriesScenario]:
    """One SeriesScenario per candidate list price; profit is the launch
    royalty minus upfront production costs at the expected unit sales."""
    if not books:
        raise ValueError("books list cannot be empty")
    if not list_prices:
        raise ValueError("list_prices cannot be empty")
    large_trim = bool(getattr(trim, "large_trim", False))
    scenarios = []
    for price in sorted(set(round(p, 2) for p in list_prices)):
        per_book: list[BookScenario] = []
        for book in books:
            result = royalty_for_price(
                price,
                book.pages,
                format,
                trim,
                ink,
                distribution,
                fixed_cost=fixed_cost,
                per_page_cost=per_page_cost,
            )
            upfront = round(upfront_cost_per_book, 2)
            be = breakeven_units(upfront, result.royalty) if result.royalty > 0 else None
            per_book.append(
                BookScenario(
                    title=book.title,
                    pages=book.pages,
                    list_price=price,
                    printing_cost=result.printing_cost,
                    royalty_per_unit=result.royalty,
                    min_list_price=result.min_list_price,
                    breakeven_units=be,
                    profit_units=profit_units,
                    profit=profit_at_units(
                        profit_units, result.royalty, upfront
                    ),
                )
            )
        scenarios.append(
            SeriesScenario(
                list_price=price,
                book_count=len(books),
                total_printing_cost=round(
                    sum(b.printing_cost for b in per_book), 2
                ),
                total_royalty_per_launch=round(
                    sum(b.royalty_per_unit * profit_units for b in per_book), 2
                ),
                per_book=per_book,
            )
        )
    return scenarios
