import pytest

from kdp_profit_planner.breakeven import breakeven_units, profit_at_units


def test_simple_breakeven():
    # $500 upfront at $2.50 royalty per unit -> 200 units.
    assert breakeven_units(500.0, 2.50) == 200


def test_breakeven_rounds_up():
    assert breakeven_units(500.0, 3.0) == 167


def test_no_upfront_means_zero():
    assert breakeven_units(0.0, 2.50) == 0


def test_zero_royalty_cannot_breakeven():
    with pytest.raises(ValueError):
        breakeven_units(500.0, 0.0)


def test_negative_fixed_costs_rejected():
    with pytest.raises(ValueError):
        breakeven_units(-10, 2.50)


def test_profit_at_units():
    assert profit_at_units(100, 2.0, 150.0) == pytest.approx(50.0)


def test_negative_units_rejected():
    with pytest.raises(ValueError):
        profit_at_units(-1, 2.0)
