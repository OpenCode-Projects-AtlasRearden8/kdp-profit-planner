"""Page count estimation from a word count."""

from __future__ import annotations

from math import ceil

from .rates import FORMAT_HARDCOVER, FORMAT_PAPERBACK, TRIMS, TrimSize

FRONT_MATTER_PAGES = 12


def estimate_pages(
    word_count: int,
    trim: TrimSize | str,
    front_matter_pages: int = FRONT_MATTER_PAGES,
    round_to_even: bool = True,
) -> int:
    """Estimate the final page count for a manuscript."""
    if word_count <= 0:
        raise ValueError("word_count must be positive")
    if isinstance(trim, str):
        try:
            trim = TRIMS[trim.lower()]
        except KeyError:
            raise ValueError(f"unknown trim size: {trim}") from None
    body = ceil(word_count / trim.words_per_page)
    pages = body + front_matter_pages
    if round_to_even and pages % 2 == 1:
        pages += 1
    return pages


PAGE_LIMITS = {
    FORMAT_PAPERBACK: (24, 828),
    FORMAT_HARDCOVER: (75, 240),
}


def page_count_flags(pages: int, format: str) -> list[str]:
    """Notes about whether a page count fits KDP format limits."""
    low, high = PAGE_LIMITS[format]
    notes = []
    if pages < low:
        notes.append(f"below KDP minimum of {low} pages for {format}")
    if pages > high:
        notes.append(f"above KDP maximum of {high} pages for {format}")
    return notes
