# Holiday calendars

Improving Guatemala follows the Improving US holiday calendar, including company days such as
the Improving Summit and the day after Thanksgiving. The calendar is selected by `country` in
the user config (default `us`).

Files: `data/holidays/<calendar>-<year>.toml`, e.g. `us-2026.toml`:

    [[holiday]]
    date = 2026-11-26
    name = "Thanksgiving Day"

The loader merges all years for a calendar. A holiday on a weekday:
- is skipped in the Workday plan (0 hours), and
- makes the week not a "full week", so there is no Engage full-week entry.

## Adding next year (do this each December, when HR publishes the list)

1. RED: add a test in `tests/test_holidays.py` listing the new dates, like
   `test_shipped_us_2026_calendar_has_all_nine_improving_holidays`. Run it and see it fail.
2. GREEN: create `data/holidays/us-<year>.toml`.
3. Add a CHANGELOG entry and open a PR titled `holidays: us <year>`.

Use observed dates, e.g. "Independence Day (Observed)" on Fri Jul 3, 2026. Enter the day
people actually take off.

## Another office or calendar

Add `<code>-<year>.toml`. Users of that office set `country = "<code>"` in their config.
