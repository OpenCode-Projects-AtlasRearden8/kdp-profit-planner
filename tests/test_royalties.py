import pytest

from kdp_profit_planner.rates import FORMAT_HARDCOVER, FORMAT_PAPERBACK
from kdp_profit_planner.royalties import (
    AMAZON_DISTRIBUTION,
    EXPANDED_DISTRIBUTION,
    distribution_royalty_rate,
    price_scan,
    royalty_for_price,
)


def test_amazon_rate_is_60_percent():
    assert distribution_royalty_rate(FORMAT_PAPERBACK, AMAZON_DISTRIBUTION) == 0.60
    assert distribution_royalty_rate(FORMAT_HARDCOVER, AMAZON_DISTRIBUTION) == 0.60


def test_expanded_distribution_is_40_percent():
    assert distribution_royalty_rate(FORMAT_PAPERBACK, EXPANDED_DISTRIBUTION) == 0.40


def test_hardcover_has_no_expanded_distribution():
    with pytest.raises(ValueError):
        distribution_royalty_rate(FORMAT_HARDCOVER, EXPANDED_DISTRIBUTION)


def test_royalty_math_paperback():
    # 280-page paperback prints for 4.21; 60% of 12.99 = 7.794 -> 3.58.
    result = royalty_for_price(12.99, 280, FORMAT_PAPERBACK)
    assert result.printing_cost == pytest.approx(4.21)
    assert result.royalty == pytest.approx(3.58)
    assert result.royalty_rate == 0.60


def test_royalty_math_hardcover():
    # 120-page hardcover prints for 7.09; 60% of 24.99 = 14.994 -> 7.90.
    result = royalty_for_price(24.99, 120, FORMAT_HARDCOVER)
    assert result.printing_cost == pytest.approx(7.09)
    assert result.royalty == pytest.approx(7.90)


def test_expanded_distribution_royalty():
    result = royalty_for_price(
        12.99, 280, FORMAT_PAPERBACK, distribution=EXPANDED_DISTRIBUTION
    )
    # 40% of 12.99 = 5.196 -> 0.99 net of the 4.21 print cost.
    assert result.royalty == pytest.approx(0.99)


def test_min_list_price_is_print_cost_over_60_percent():
    result = royalty_for_price(
        12.99, 280, FORMAT_PAPERBACK, distribution=EXPANDED_DISTRIBUTION
    )
    assert result.min_list_price == pytest.approx(4.21 / 0.60, abs=0.01)


def test_price_below_minimum_pays_nothing():
    result = royalty_for_price(5.00, 280, FORMAT_PAPERBACK)
    assert result.royalty == 0.0
    assert result.list_price < result.min_list_price


def test_royalty_is_zero_exactly_at_min_price():
    result = royalty_for_price(4.21 / 0.60, 280, FORMAT_PAPERBACK)
    assert result.royalty <= 0.01


def test_negative_price_rejected():
    with pytest.raises(ValueError):
        royalty_for_price(-1, 280, FORMAT_PAPERBACK)


def test_price_scan_is_inclusive_and_ordered():
    results = price_scan(280, FORMAT_PAPERBACK, 9.99, 12.99, 1.00)
    prices = [r.list_price for r in results]
    assert prices == [9.99, 10.99, 11.99, 12.99]
    assert all(a.royalty < b.royalty for a, b in zip(results, results[1:]))


def test_price_scan_validates_arguments():
    with pytest.raises(ValueError):
        price_scan(280, FORMAT_PAPERBACK, 12.99, 9.99, 1.00)
    with pytest.raises(ValueError):
        price_scan(280, FORMAT_PAPERBACK, 9.99, 12.99, 0)
