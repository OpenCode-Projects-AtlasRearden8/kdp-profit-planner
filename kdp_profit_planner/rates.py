"""Reference rates: trim sizes, words-per-page estimates, and KDP-style
US printing cost tables. All numbers live in this module so they stay
inspectable and overridable; nothing is fetched from the network."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TrimSize:
    name: str
    width_in: float
    height_in: float
    words_per_page: int
    large_trim: bool

    @property
    def label(self) -> str:
        size = f"{self.width_in:g} x {self.height_in:g}"
        return f"{size} in ({'large' if self.large_trim else 'standard'} trim)"


# Rough words per page for a typical KDP interior: 11 pt serif, single
# spaced lines with leading, modest margins. Estimates only; a real
# manuscript will vary with font, line spacing, and graphics.
TRIMS: dict[str, TrimSize] = {
    "5x8": TrimSize("5x8", 5.0, 8.0, 200, False),
    "5.25x8": TrimSize("5.25x8", 5.25, 8.0, 215, False),
    "5.5x8.5": TrimSize("5.5x8.5", 5.5, 8.5, 250, False),
    "6x9": TrimSize("6x9", 6.0, 9.0, 300, False),
    "6.14x9.21": TrimSize("6.14x9.21", 6.14, 9.21, 320, True),
    "6.69x9.61": TrimSize("6.69x9.61", 6.69, 9.61, 360, True),
    "7x10": TrimSize("7x10", 7.0, 10.0, 400, True),
    "7.44x9.69": TrimSize("7.44x9.69", 7.44, 9.69, 420, True),
    "7.5x9.25": TrimSize("7.5x9.25", 7.5, 9.25, 430, True),
    "8x10": TrimSize("8x10", 8.0, 10.0, 480, True),
    "8.25x11": TrimSize("8.25x11", 8.25, 11.0, 520, True),
    "8.5x11": TrimSize("8.5x11", 8.5, 11.0, 550, True),
}

INK_BLACK = "black"
INK_COLOR = "color"

FORMAT_PAPERBACK = "paperback"
FORMAT_HARDCOVER = "hardcover"

# KDP-style US printing cost, revised June 2023:
# cost = fixed + per_page * page_count.
_PRINTING_US: dict[tuple[str, str, bool], tuple[float, float]] = {
    (FORMAT_PAPERBACK, INK_BLACK, False): (0.85, 0.012),
    (FORMAT_PAPERBACK, INK_BLACK, True): (1.00, 0.012),
    (FORMAT_PAPERBACK, INK_COLOR, False): (0.85, 0.0575),
    (FORMAT_PAPERBACK, INK_COLOR, True): (1.00, 0.0575),
    (FORMAT_HARDCOVER, INK_BLACK, False): (5.65, 0.012),
    (FORMAT_HARDCOVER, INK_COLOR, False): (8.87, 0.065),
}

PAPERBACK_MIN_PAGES = 24
HARDCOVER_MIN_PAGES = 75
PAPERBACK_MAX_PAGES = 828
HARDCOVER_MAX_PAGES = 240


def printing_rate(
    format: str,
    ink: str = INK_BLACK,
    large_trim: bool = False,
    fixed_cost: float | None = None,
    per_page_cost: float | None = None,
) -> tuple[float, float]:
    """Return (fixed, per_page) printing costs, falling back to the US
    table unless both overrides are supplied."""
    if fixed_cost is not None and per_page_cost is not None:
        return float(fixed_cost), float(per_page_cost)
    key = (format, ink, large_trim if format == FORMAT_PAPERBACK else False)
    if key not in _PRINTING_US:
        raise ValueError(f"no printing rate for {format}/{ink}")
    return _PRINTING_US[key]
