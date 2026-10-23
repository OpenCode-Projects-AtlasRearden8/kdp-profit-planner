"""Command-line interface for kdp-profit-planner."""

from __future__ import annotations

import argparse
import sys

from .breakeven import breakeven_units, profit_at_units
from .pages import FRONT_MATTER_PAGES, estimate_pages, page_count_flags
from .projections import monthly_projection, months_to_profit
from .rates import FORMAT_HARDCOVER, FORMAT_PAPERBACK, INK_BLACK, INK_COLOR, TRIMS
from .royalties import (
    DISTRIBUTIONS,
    EXPANDED_DISTRIBUTION,
    price_scan,
    printing_cost,
    royalty_for_price,
)
from .scenarios import Book, compare_series_prices

PROGRAM = "kdp-profit-planner"

FORMATS = (FORMAT_PAPERBACK, FORMAT_HARDCOVER)


def money(value: float) -> str:
    return f"${value:,.2f}"


def print_table(headers: list[str], rows: list[list[str]]) -> None:
    widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(cell))
    fmt = "  ".join(f"{{:<{w}}}" for w in widths)
    print(fmt.format(*headers))
    print(fmt.format(*["-" * w for w in widths]))
    for row in rows:
        print(fmt.format(*row))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog=PROGRAM,
        description=(
            "Turn a word count into a KDP publishing plan: page counts, "
            "printing costs, royalties, break-even units, series price "
            "scenarios, and monthly projections. All math runs locally."
        ),
    )
    parser.add_argument(
        "--version", action="version", version=f"{PROGRAM} 0.1.0"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("trims", help="list supported trim sizes")
    p.set_defaults(func=cmd_trims)

    p = sub.add_parser(
        "pages",
        help="estimate page counts from a word count across trim sizes",
    )
    p.add_argument("word_count", type=int)
    p.add_argument(
        "--trim",
        action="append",
        default=[],
        help="limit to this trim size (repeatable)",
    )
    p.add_argument(
        "--front-matter",
        type=int,
        default=FRONT_MATTER_PAGES,
        help="additional pages for title page, TOC, etc. (default 12)",
    )
    p.set_defaults(func=cmd_pages)

    p = sub.add_parser("cost", help="per-unit printing cost")
    p.add_argument("--pages", type=int, required=True)
    p.add_argument("--format", default=FORMAT_PAPERBACK, choices=FORMATS)
    p.add_argument("--ink", default=INK_BLACK, choices=(INK_BLACK, INK_COLOR))
    p.add_argument("--fixed-cost", type=float, help="override fixed printing cost")
    p.add_argument(
        "--per-page", type=float, help="override per-page printing cost"
    )
    _add_trim_option(p)
    p.set_defaults(func=cmd_cost)

    p = sub.add_parser("royalty", help="royalty per unit at a list price")
    p.add_argument("--price", type=float, required=True)
    p.add_argument("--pages", type=int, required=True)
    p.add_argument("--format", default=FORMAT_PAPERBACK, choices=FORMATS)
    p.add_argument("--ink", default=INK_BLACK, choices=(INK_BLACK, INK_COLOR))
    p.add_argument(
        "--distribution",
        default="amazon",
        choices=DISTRIBUTIONS,
        help="amazon (60%% rate) or expanded (40%% rate, paperback only)",
    )
    p.add_argument("--fixed-cost", type=float)
    p.add_argument("--per-page", type=float)
    _add_trim_option(p)
    p.set_defaults(func=cmd_royalty)

    p = sub.add_parser(
        "prices", help="scan royalties across a range of list prices"
    )
    p.add_argument("--pages", type=int, required=True)
    p.add_argument("--from", dest="start", type=float, required=True)
    p.add_argument("--to", dest="end", type=float, required=True)
    p.add_argument("--step", type=float, default=0.50)
    p.add_argument("--format", default=FORMAT_PAPERBACK, choices=FORMATS)
    p.add_argument("--ink", default=INK_BLACK, choices=(INK_BLACK, INK_COLOR))
    p.add_argument("--distribution", default="amazon", choices=DISTRIBUTIONS)
    p.add_argument("--fixed-cost", type=float)
    p.add_argument("--per-page", type=float)
    _add_trim_option(p)
    p.set_defaults(func=cmd_prices)

    p = sub.add_parser("breakeven", help="units needed to cover upfront costs")
    p.add_argument("--upfront", type=float, required=True, help="US$ of editing, cover, ads, etc.")
    p.add_argument("--price", type=float, required=True)
    p.add_argument("--pages", type=int, required=True)
    p.add_argument("--format", default=FORMAT_PAPERBACK, choices=FORMATS)
    p.add_argument("--ink", default=INK_BLACK, choices=(INK_BLACK, INK_COLOR))
    p.add_argument("--fixed-cost", type=float)
    p.add_argument("--per-page", type=float)
    _add_trim_option(p)
    p.set_defaults(func=cmd_breakeven)

    p = sub.add_parser(
        "compare",
        help="compare list-price scenarios for a series launch",
    )
    p.add_argument(
        "--books",
        required=True,
        help="comma-separated Title:pagecount entries, e.g. 'Book One:280,Book Two:310'",
    )
    p.add_argument(
        "--prices",
        required=True,
        help="comma-separated candidate list prices, e.g. '9.99,12.99'",
    )
    p.add_argument(
        "--upfront-per-book",
        type=float,
        default=0.0,
        help="US$ upfront production cost per book (default 0)",
    )
    p.add_argument(
        "--units-per-book",
        type=int,
        default=0,
        help="expected units sold per book for the profit scenario (default 0)",
    )
    p.add_argument("--format", default=FORMAT_PAPERBACK, choices=FORMATS)
    p.add_argument("--fixed-cost", type=float)
    p.add_argument("--per-page", type=float)
    p.set_defaults(func=cmd_compare)

    p = sub.add_parser(
        "project", help="project monthly royalties over time"
    )
    p.add_argument("--units", type=int, required=True, help="expected units sold per month")
    p.add_argument("--price", type=float, required=True)
    p.add_argument("--pages", type=int, required=True)
    p.add_argument("--months", type=int, default=12)
    p.add_argument(
        "--growth", type=float, default=0.0, help="monthly unit growth, e.g. 0.05 for 5%%"
    )
    p.add_argument("--monthly-cost", type=float, default=0.0, help="US$ ongoing monthly costs (e.g. ads)")
    p.add_argument(
        "--upfront",
        type=float,
        default=0.0,
        help="US$ upfront costs booked against month 1 (default 0)",
    )
    p.add_argument("--format", default=FORMAT_PAPERBACK, choices=FORMATS)
    p.add_argument("--ink", default=INK_BLACK, choices=(INK_BLACK, INK_COLOR))
    p.add_argument("--fixed-cost", type=float)
    p.add_argument("--per-page", type=float)
    _add_trim_option(p)
    p.set_defaults(func=cmd_project)

    p = sub.add_parser(
        "plan", help="full publishing plan from a word count and a price"
    )
    p.add_argument("word_count", type=int)
    p.add_argument("--trim", default="6x9")
    p.add_argument("--price", type=float, required=True)
    p.add_argument(
        "--upfront", type=float, default=0.0, help="US$ upfront production costs (default 0)"
    )
    p.add_argument(
        "--units", type=int, default=0, help="expected monthly unit sales (default 0)"
    )
    p.add_argument("--months", type=int, default=12,
                   help="projection horizon in months (default 12)")
    p.add_argument("--growth", type=float, default=0.0)
    p.set_defaults(func=cmd_plan)

    return parser


def parse_books(spec: str) -> list[Book]:
    books = []
    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue
        title, _, pages_text = part.rpartition(":")
        try:
            pages = int(pages_text)
        except ValueError:
            raise ValueError(
                f"book entry must look like 'Title:280', got: {part!r}"
            ) from None
        books.append(Book(title=title or pages_text, pages=pages))
    if not books:
        raise ValueError("no books found in spec")
    return books


def parse_prices(spec: str) -> list[float]:
    prices = []
    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue
        try:
            prices.append(float(part))
        except ValueError:
            raise ValueError(f"invalid price: {part!r}") from None
    if not prices:
        raise ValueError("no prices found in spec")
    return prices


def validate_page_count(pages: int, format: str) -> int:
    if pages <= 0:
        raise ValueError("--pages must be positive")
    return pages


def _cost_kwargs(args) -> dict:
    return {
        "fixed_cost": getattr(args, "fixed_cost", None),
        "per_page_cost": getattr(args, "per_page", None),
    }


def _trim_arg(name: str | None):
    if name is None:
        return None
    if name not in TRIMS:
        raise ValueError(f"unknown trim size: {name}")
    return TRIMS[name]


def _add_trim_option(p: argparse.ArgumentParser) -> None:
    p.add_argument(
        "--trim",
        default=None,
        help="trim size (only the standard/large print-cost tier matters)",
    )


def cmd_trims(args) -> None:
    rows = [
        [name, trim.label, f"{trim.words_per_page}"]
        for name, trim in TRIMS.items()
    ]
    print_table(
        ["trim", "size", "est. words/page 11pt"], rows
    )


def cmd_pages(args) -> None:
    if args.word_count <= 0:
        raise ValueError("word_count must be positive")
    trims = args.trim or list(TRIMS)
    rows = []
    for name in trims:
        if name not in TRIMS:
            raise ValueError(f"unknown trim size: {name}")
        pages = estimate_pages(args.word_count, name, args.front_matter)
        rows.append(
            [name, f"{pages}", *(page_count_flags(pages, FORMAT_PAPERBACK) or ["fits KDP limits"])]
        )
    print_table(["trim", "est. pages", "notes"], rows)


def cmd_cost(args) -> None:
    pages = validate_page_count(args.pages, args.format)
    cost = printing_cost(
        pages, args.format, _trim_arg(args.trim), args.ink, **_cost_kwargs(args)
    )
    print(f"{args.format} / {args.ink} ink, {pages} pages: {money(cost)} per unit")


def cmd_royalty(args) -> None:
    pages = validate_page_count(args.pages, args.format)
    result = royalty_for_price(
        args.price,
        pages,
        args.format,
        trim=_trim_arg(args.trim),
        ink=args.ink,
        distribution=args.distribution,
        **_cost_kwargs(args),
    )
    rate_pct = int(result.royalty_rate * 100)
    print(
        f"list price {money(result.list_price)} -> {money(result.royalty)} "
        f"royalty per unit"
    )
    print(
        f"({rate_pct}% rate, printing {money(result.printing_cost)}, "
        f"distribution: {result.distribution})"
    )
    if result.royalty <= 0:
        print(
            f"WARNING: price is below the break-even list price of "
            f"{money(result.min_list_price)}"
        )


def cmd_prices(args) -> None:
    pages = validate_page_count(args.pages, args.format)
    results = price_scan(
        pages,
        args.format,
        args.start,
        args.end,
        args.step,
        trim=_trim_arg(args.trim),
        ink=args.ink,
        distribution=args.distribution,
        **_cost_kwargs(args),
    )
    rows = [
        [
            money(r.list_price),
            money(r.printing_cost),
            f"{int(r.royalty_rate * 100)}%",
            money(r.royalty),
            money(r.min_list_price),
            "yes" if r.royalty > 0 else "NO",
        ]
        for r in results
    ]
    print_table(
        ["list price", "printing", "rate", "royalty/unit", "min price", "profitable"],
        rows,
    )


def cmd_breakeven(args) -> None:
    pages = validate_page_count(args.pages, args.format)
    result = royalty_for_price(
        args.price,
        pages,
        args.format,
        trim=_trim_arg(args.trim),
        ink=args.ink,
        **_cost_kwargs(args),
    )
    if result.royalty <= 0:
        raise ValueError(
            f"list price {money(result.list_price)} produces no royalty; "
            f"minimum profitable price is {money(result.min_list_price)}"
        )
    units = breakeven_units(args.upfront, result.royalty)
    print(f"royalty per unit at {money(result.list_price)}: {money(result.royalty)}")
    print(
        f"break-even units for {money(args.upfront)} upfront: {units}"
    )
    print(
        f"profit at 2x break-even ({units * 2} units): "
        f"{money(profit_at_units(units * 2, result.royalty, args.upfront))}"
    )


def cmd_compare(args) -> None:
    books = parse_books(args.books)
    prices = parse_prices(args.prices)
    scenarios = compare_series_prices(
        books,
        prices,
        upfront_cost_per_book=args.upfront_per_book,
        profit_units=args.units_per_book,
        format=args.format,
        **_cost_kwargs(args),
    )
    for scenario in scenarios:
        print(
            f"\nSeries of {scenario.book_count} books at {money(scenario.list_price)}"
        )
        rows = []
        for b in scenario.per_book:
            be = str(b.breakeven_units) if b.breakeven_units is not None else "never"
            rows.append(
                [
                    b.title,
                    str(b.pages),
                    money(b.printing_cost),
                    money(b.royalty_per_unit),
                    money(b.min_list_price),
                    be,
                    money(b.profit),
                ]
            )
        print_table(
            [
                "book",
                "pages",
                "printing",
                "royalty/unit",
                "min price",
                "break-even units",
                f"profit at {scenario.per_book[0].profit_units}/book",
            ],
            rows,
        )
        print(
            f"series total: launch royalties {money(scenario.total_royalty_per_launch)}, "
            f"profit {money(scenario.total_profit)}"
        )


def cmd_project(args) -> None:
    pages = validate_page_count(args.pages, args.format)
    result = royalty_for_price(
        args.price,
        pages,
        args.format,
        trim=_trim_arg(args.trim),
        ink=args.ink,
        **_cost_kwargs(args),
    )
    if result.royalty <= 0:
        raise ValueError(
            f"list price {money(result.list_price)} does not produce a royalty; "
            f"minimum profitable price is {money(result.min_list_price)}"
        )
    projections = monthly_projection(
        args.units,
        result.royalty,
        months=args.months,
        growth_rate=args.growth,
        monthly_cost=args.monthly_cost,
        upfront_costs=args.upfront,
    )
    rows = [
        [
            str(m.month),
            str(m.units),
            money(m.gross_royalty),
            money(m.costs),
            money(m.net),
            money(m.cumulative_net),
        ]
        for m in projections
    ]
    print_table(
        ["month", "units", "royalty", "costs", "net", "cumulative"],
        rows,
    )
    milestone = months_to_profit(args.units, result.royalty, args.upfront, args.monthly_cost)
    if milestone == 0:
        print("cumulative profit from month 1 (no upfront costs)")
    elif milestone is None:
        print("cumulative profit never turns positive with these inputs")
    else:
        print(f"cumulative profit from month {milestone}")


def cmd_plan(args) -> None:
    if args.word_count <= 0:
        raise ValueError("word_count must be positive")
    if args.trim not in TRIMS:
        raise ValueError(f"unknown trim size: {args.trim}")
    trim = TRIMS[args.trim]
    pages = estimate_pages(args.word_count, trim)
    print(f"Publishing plan: ~{args.word_count:,} words, {trim.label}")
    print(f"  estimated page count: {pages}")
    flags = page_count_flags(pages, FORMAT_PAPERBACK)
    for flag in flags:
        print(f"  note: {flag}")

    result = royalty_for_price(args.price, pages, FORMAT_PAPERBACK, trim=trim)
    print(f"  paperback printing cost: {money(result.printing_cost)} per unit")
    print(
        f"  royalty at {money(result.list_price)}: {money(result.royalty)} per unit "
        f"(minimum viable price {money(result.min_list_price)})"
    )
    if result.royalty <= 0:
        print("  ^ raise the price: this does not earn royalties")
        return

    be_units = breakeven_units(args.upfront, result.royalty)
    hit = profit_at_units(args.units, result.royalty, args.upfront)
    print(
        f"  break-even on {money(args.upfront)} upfront: {be_units} units; "
        f"profit after {args.units} monthly units: {money(hit)}"
    )

    if args.units:
        projections = monthly_projection(
            args.units,
            result.royalty,
            months=args.months,
            growth_rate=args.growth,
            upfront_costs=args.upfront,
        )
        total_units = sum(m.units for m in projections)
        year_end = round(sum(m.net for m in projections) - args.upfront, 2)
        print(
            f"  next {args.months} months: {total_units} units, "
            f"net after upfront {money(year_end)}"
        )
        milestone = months_to_profit(args.units, result.royalty, args.upfront)
        if milestone == 0:
            print("  cumulative profit from month 1 (no upfront costs)")
        elif milestone is not None:
            print(f"  cumulative profit from month {milestone}")
        else:
            print("  cumulative profit never turns positive with these inputs")
        print(f"  month {args.months} royalty: {money(projections[-1].net)}")


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        args.func(args)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
