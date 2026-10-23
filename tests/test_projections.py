import pytest

from kdp_profit_planner.projections import monthly_projection, months_to_profit


def test_flat_projection():
    months = monthly_projection(10, 2.0, months=6)
    assert len(months) == 6
    assert [m.units for m in months] == [10] * 6
    assert [m.gross_royalty for m in months] == [20.0] * 6


def test_growth_compounds():
    months = monthly_projection(100, 1.0, months=3, growth_rate=0.50)
    assert [m.units for m in months] == [100, 150, 225]


def test_upfront_costs_hit_month_one():
    months = monthly_projection(10, 2.0, months=3, upfront_costs=50.0)
    assert months[0].cumulative_net == pytest.approx(-30.0)
    assert months[1].cumulative_net == pytest.approx(-10.0)
    assert months[2].cumulative_net == pytest.approx(10.0)


def test_monthly_costs_subtract():
    months = monthly_projection(10, 2.0, months=2, monthly_cost=5.0)
    assert months[0].net == pytest.approx(15.0)


def test_cumulative_matches_running_net():
    months = monthly_projection(25, 3.58, months=12, upfront_costs=750.0)
    running = -750.0
    for m in months:
        running = round(running + m.net, 2)
        assert m.cumulative_net == pytest.approx(running, abs=0.01)


def test_validation():
    with pytest.raises(ValueError):
        monthly_projection(-1, 2.0)
    with pytest.raises(ValueError):
        monthly_projection(10, 2.0, months=0)
    with pytest.raises(ValueError):
        monthly_projection(10, -1.0)
    with pytest.raises(ValueError):
        monthly_projection(10, 2.0, monthly_cost=-5.0)


def test_months_to_profit():
    # $750 upfront, $20/month net -> month 38 (ceil(750/20)).
    assert months_to_profit(10, 2.0, 750.0) == 38
    assert months_to_profit(10, 2.0, 0.0) == 0


def test_months_to_profit_never_when_net_negative():
    assert months_to_profit(10, 2.0, 750.0, monthly_cost=100.0) is None


def test_months_to_profit_respects_cap():
    assert months_to_profit(10, 2.0, 1_000_000.0, max_months=12) is None
