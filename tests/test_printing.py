import pytest

from kdp_profit_planner.rates import (
    FORMAT_HARDCOVER,
    FORMAT_PAPERBACK,
    INK_BLACK,
    INK_COLOR,
    printing_rate,
)
from kdp_profit_planner.royalties import (
    AMAZON_DISTRIBUTION,
    EXPANDED_DISTRIBUTION,
    distribution_royalty_rate,
    price_scan,
    printing_cost,
    royalty_for_price,
)
from kdp_profit_planner.scenarios import Book


def test_paperback_black_ink_standard():
    # 280-page standard black-ink paperback: 0.85 + 0.012 * 280 = 4.21.
    assert printing_cost(280, FORMAT_PAPERBACK) == pytest.approx(4.21)


def test_paperback_large_trim_has_higher_fixed_cost():
    assert printing_cost(280, FORMAT_PAPERBACK) == pytest.approx(4.21)
    assert printing_cost(280, FORMAT_PAPERBACK, large_trim=True) == pytest.approx(
        4.36
    )


def test_hardcover_fixed_cost():
    # 120-page hardcover: 5.65 + 0.012 * 120 = 7.09.
    assert printing_cost(120, FORMAT_HARDCOVER) == pytest.approx(7.09)


def test_color_costs_more():
    assert printing_cost(280, FORMAT_PAPERBACK, ink=INK_COLOR) > printing_cost(
        280, FORMAT_PAPERBACK, ink=INK_BLACK
    )


def test_page_must_be_positive():
    with pytest.raises(ValueError):
        printing_cost(0, FORMAT_PAPERBACK)


def test_rate_overrides():
    fixed, per_page = printing_rate(
        FORMAT_PAPERBACK, INK_BLACK, False, fixed_cost=1.50, per_page_cost=0.020
    )
    assert fixed == 1.50
    assert per_page == 0.020


def test_partial_overrides_fall_back_to_table():
    with pytest.raises(ValueError):
        printing_rate(FORMAT_PAPERBACK, "silk", False, fixed_cost=1.0)
