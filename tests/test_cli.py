import pytest

from kdp_profit_planner.cli import main, parse_books, parse_prices


def run_cli(capsys, *argv):
    code = main(list(argv))
    out = capsys.readouterr().out
    return code, out


def test_trims_command(capsys):
    code, out = run_cli(capsys, "trims")
    assert code == 0
    assert "6x9" in out
    assert "300" in out


def test_pages_command(capsys):
    code, out = run_cli(capsys, "pages", "80000")
    assert code == 0
    assert "280" in out  # 6x9 estimate
    assert "5x8" in out


def test_pages_single_trim(capsys):
    code, out = run_cli(capsys, "pages", "80000", "--trim", "6x9")
    assert code == 0
    assert out.count("\n") == 3  # header + rule + one row


def test_pages_rejects_bad_words(capsys):
    code = main(["pages", "0"])
    err = capsys.readouterr().err
    assert code == 2
    assert "error" in err


def test_cost_command(capsys):
    code, out = run_cli(capsys, "cost", "--pages", "280")
    assert code == 0
    assert "$4.21" in out


def test_royalty_command(capsys):
    code, out = run_cli(capsys, "royalty", "--price", "12.99", "--pages", "280")
    assert code == 0
    assert "$3.58" in out


def test_royalty_warns_below_minimum(capsys):
    code, out = run_cli(capsys, "royalty", "--price", "3.00", "--pages", "280")
    assert code == 0
    assert "WARNING" in out


def test_prices_command(capsys):
    code, out = run_cli(capsys, "prices", "--pages", "280", "--from", "9.99", "--to", "11.99")
    assert code == 0
    assert "9.99" in out and "11.99" in out
    assert "NO" in out or "yes" in out


def test_prices_bad_order_errors(capsys):
    main(["prices", "--pages", "280", "--from", "11.99", "--to", "9.99"])
    err = capsys.readouterr().err
    assert "error" in err


def test_breakeven_command(capsys):
    code, out = run_cli(
        capsys,
        "breakeven",
        "--upfront",
        "500",
        "--price",
        "12.99",
        "--pages",
        "280",
    )
    assert code == 0
    # 500 / 3.58 = 139.7 -> 140 units.
    assert "140" in out


def test_compare_command(capsys):
    code, out = run_cli(
        capsys,
        "compare",
        "--books",
        "AI Tools 101:280,Local AI at Home:300",
        "--prices",
        "9.99,12.99",
        "--units-per-book",
        "40",
    )
    assert code == 0
    assert "Series of 2 books at $12.99" in out
    assert "AI Tools 101" in out


def test_compare_bad_book_spec_errors(capsys):
    main(["compare", "--books", "no-pages-here", "--prices", "9.99"])
    err = capsys.readouterr().err
    assert "error" in err


def test_project_command(capsys):
    code, out = run_cli(
        capsys,
        "project",
        "--units",
        "25",
        "--price",
        "12.99",
        "--pages",
        "280",
        "--months",
        "3",
        "--upfront",
        "750",
    )
    assert code == 0
    assert "cumulative profit from month 9" in out


def test_project_unprofitable_price_errors(capsys):
    main(["project", "--units", "25", "--price", "3.00", "--pages", "280"])
    err = capsys.readouterr().err
    assert "error" in err


def test_plan_command(capsys):
    code, out = run_cli(
        capsys,
        "plan",
        "80000",
        "--trim",
        "6x9",
        "--price",
        "12.99",
        "--upfront",
        "750",
        "--units",
        "25",
    )
    assert code == 0
    assert "estimated page count: 280" in out
    assert "$4.21" in out
    assert "$3.58" in out
    assert "$324.00" in out
    assert "cumulative profit from month 9" in out


def test_plan_high_page_count_notes(capsys):
    code, out = run_cli(capsys, "plan", "500000", "--trim", "6x9", "--price", "14.99")
    assert code == 0
    assert "note:" in out


def test_plan_bad_trim_errors(capsys):
    main(["plan", "80000", "--trim", "7x7x7", "--price", "12.99"])
    err = capsys.readouterr().err
    assert "error" in err


def test_version(capsys):
    with pytest.raises(SystemExit) as exc:
        main(["--version"])
    assert exc.value.code == 0


def test_parse_books():
    books = parse_books("One:280, Two:300 ,Three:310")
    assert [(b.title, b.pages) for b in books] == [
        ("One", 280),
        ("Two", 300),
        ("Three", 310),
    ]


def test_parse_books_rejects_garbage():
    with pytest.raises(ValueError):
        parse_books("One:abc")


def test_parse_prices():
    assert parse_prices("9.99, 12.99, 14.99") == [9.99, 12.99, 14.99]
    with pytest.raises(ValueError):
        parse_prices("9.99,cheap")
