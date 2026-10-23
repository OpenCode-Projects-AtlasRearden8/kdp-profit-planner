import pytest

from kdp_profit_planner.pages import (
    FRONT_MATTER_PAGES,
    estimate_pages,
    page_count_flags,
)
from kdp_profit_planner.rates import TRIMS


def test_estimate_pages_60k_words_6x9():
    # 60,000 / 300 words per page = 200 body pages + 12 front matter.
    assert estimate_pages(60_000, "6x9") == 212


def test_estimate_pages_80k_words_6x9():
    # 80,000 / 300 = 266.67 -> 267 body pages + 12 = 279 -> rounded even.
    assert estimate_pages(80_000, "6x9") == 280


def test_exact_division_is_exact():
    # 30,000 / 300 = 100 body pages + 12 front matter = 112.
    assert estimate_pages(30_000, "6x9") == FRONT_MATTER_PAGES + 100


def test_round_to_even_can_be_disabled():
    assert estimate_pages(80_000, "6x9", round_to_even=False) == 279


def test_front_matter_override():
    assert estimate_pages(30_000, "6x9", front_matter_pages=0) == 100


def test_every_trim_size_is_estimable():
    for name in TRIMS:
        pages = estimate_pages(10_000, name)
        assert pages >= 24


def test_larger_trims_use_fewer_pages():
    small = estimate_pages(60_000, "5x8")
    large = estimate_pages(60_000, "8.5x11")
    assert large < small


def test_zero_words_raises():
    with pytest.raises(ValueError):
        estimate_pages(0, "6x9")


def test_unknown_trim_raises():
    with pytest.raises(ValueError, match="unknown trim"):
        estimate_pages(10_000, "7x7")


def test_page_count_flags():
    assert page_count_flags(300, "paperback") == []
    notes = page_count_flags(10, "paperback")
    assert notes and "minimum" in notes[0]
    notes = page_count_flags(900, "paperback")
    assert notes and "maximum" in notes[0]
    assert page_count_flags(76, "hardcover") == []
