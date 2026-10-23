import pytest

from kdp_profit_planner.rates import FORMAT_PAPERBACK
from kdp_profit_planner.scenarios import Book, compare_series_prices


BOOKS = [
    Book("AI Tools 101", 280),
    Book("Agents for Everyone", 320),
    Book("Local AI at Home", 300),
]


def _scenario(**kwargs):
    return compare_series_prices(BOOKS, [12.99], **kwargs)[0]


def test_one_scenario_per_price():
    scenarios = compare_series_prices(BOOKS, [9.99, 12.99, 14.99])
    assert [s.list_price for s in scenarios] == [9.99, 12.99, 14.99]


def test_duplicate_prices_are_deduplicated_and_sorted():
    scenarios = compare_series_prices(BOOKS, [12.99, 9.99, 12.99, 9.99])
    assert [s.list_price for s in scenarios] == [9.99, 12.99]


def test_totals_sum_per_book():
    scenario = _scenario()
    assert scenario.total_printing_cost == pytest.approx(
        sum(b.printing_cost for b in scenario.per_book)
    )
    assert scenario.total_profit == pytest.approx(
        sum(b.profit for b in scenario.per_book)
    )


def test_higher_price_yields_higher_royalty():
    cheap = compare_series_prices(BOOKS, [9.99], profit_units=40)[0]
    mid = _scenario(profit_units=40)
    assert mid.total_royalty_per_launch > cheap.total_royalty_per_launch


def test_upfront_costs_flow_into_breakeven():
    scenario = _scenario(upfront_cost_per_book=750.0, profit_units=40)
    for book in scenario.per_book:
        assert book.breakeven_units > 0
        assert book.profit == pytest.approx(
            round(40 * book.royalty_per_unit - 750.0, 2)
        )


def test_zero_upfront_breakeven_is_zero():
    scenario = _scenario()
    for book in scenario.per_book:
        assert book.breakeven_units == 0
        assert book.profit == pytest.approx(
            round(0 * book.royalty_per_unit, 2)
        )


def test_min_list_price_from_print_costs():
    scenario = _scenario()
    for book in scenario.per_book:
        assert book.min_list_price == pytest.approx(
            book.printing_cost / 0.60, abs=0.01
        )


def test_empty_inputs_rejected():
    with pytest.raises(ValueError):
        compare_series_prices([], [9.99])
    with pytest.raises(ValueError):
        compare_series_prices(BOOKS, [])


def test_format_flows_through():
    scenario = _scenario(format=FORMAT_PAPERBACK)
    for book in scenario.per_book:
        assert book.printing_cost > 0
