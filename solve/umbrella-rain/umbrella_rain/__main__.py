"""CLI entry: conda run -n math python -m umbrella_rain (from solve/umbrella-rain on PYTHONPATH)."""

from umbrella_rain.solve_all import format_report, solve_all


def main() -> None:
    print(format_report(solve_all()))


if __name__ == "__main__":
    main()
