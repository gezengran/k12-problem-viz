"""CLI entry: export Live Photo for compound-growth."""

from paths import ami_dir

from compound_growth.constants import CASE_ID
from compound_growth.viz import export_live_demo


def main() -> None:
    pvt = export_live_demo(ami_dir(CASE_ID))
    print(f"Exported Live Photo: {pvt}")


if __name__ == "__main__":
    main()
