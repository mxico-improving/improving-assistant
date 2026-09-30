from datetime import date
from pathlib import Path

from improving_assistant.holidays import load_holidays

REPO_HOLIDAYS = Path(__file__).resolve().parents[1] / "data" / "holidays"


def test_loads_holidays_from_toml_file(tmp_path):
    f = tmp_path / "gt-2099.toml"
    f.write_text('[[holiday]]\ndate = 2099-01-01\nname = "Año Nuevo"\n', encoding="utf-8")

    assert load_holidays(tmp_path, country="gt") == {date(2099, 1, 1): "Año Nuevo"}


def test_only_loads_files_for_requested_country(tmp_path):
    (tmp_path / "gt-2099.toml").write_text('[[holiday]]\ndate = 2099-01-01\nname = "GT"\n')
    (tmp_path / "us-2099.toml").write_text('[[holiday]]\ndate = 2099-07-04\nname = "US"\n')

    assert load_holidays(tmp_path, country="gt") == {date(2099, 1, 1): "GT"}


def test_merges_multiple_years(tmp_path):
    (tmp_path / "gt-2098.toml").write_text('[[holiday]]\ndate = 2098-12-25\nname = "A"\n')
    (tmp_path / "gt-2099.toml").write_text('[[holiday]]\ndate = 2099-12-25\nname = "B"\n')

    assert set(load_holidays(tmp_path, country="gt")) == {date(2098, 12, 25), date(2099, 12, 25)}


def test_shipped_us_2026_calendar_has_all_nine_improving_holidays():
    hols = {d: n for d, n in load_holidays(REPO_HOLIDAYS, country="us").items() if d.year == 2026}

    assert sorted(hols) == [
        date(2026, 1, 1), date(2026, 2, 20), date(2026, 5, 25), date(2026, 7, 3),
        date(2026, 9, 7), date(2026, 11, 26), date(2026, 11, 27), date(2026, 12, 24),
        date(2026, 12, 25),
    ]


def test_no_guatemalan_calendar_is_shipped():
    assert load_holidays(REPO_HOLIDAYS, country="gt") == {}
