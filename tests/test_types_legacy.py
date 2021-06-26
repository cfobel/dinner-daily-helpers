import dinner_daily_helpers as ddh
import dinner_daily_helpers.scrape
import dinner_daily_helpers.types.legacy
import pytest
from pathlib import Path

fixtures_root = Path(__file__).parent.joinpath("fixtures")


def _test_from_legacy_round_trip(legacy_menu: ddh.types.legacy.LegacyMenu):
    menu = ddh.types.legacy.from_legacy(legacy_menu)
    legacy_menu_converted = ddh.types.legacy.to_legacy(menu)
    assert legacy_menu == legacy_menu_converted


@pytest.mark.parametrize("path", fixtures_root.glob("legacy_menus/*.json"))
def test_from_legacy_round_trip(path: Path):
    legacy_menu = ddh.types.legacy.LegacyMenu.parse_file(path)
    _test_from_legacy_round_trip(legacy_menu)


@pytest.mark.parametrize("path", fixtures_root.glob("weeks/*.json"))
def test_to_legacy(path: Path):
    week = ddh.types.week.Week.parse_file(path)
    legacy = ddh.types.legacy.to_legacy(week.menu)
    expected_legacy = ddh.types.legacy.LegacyMenu.parse_file(
        fixtures_root.joinpath("legacy_menus", path.name)
    )
    assert legacy == expected_legacy
