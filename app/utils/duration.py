from enum import StrEnum


class DurationUnit(StrEnum):
    """Allowed units for a course's stated duration."""

    HOURS = "hours"
    DAYS = "days"
    WEEKS = "weeks"
    MONTHS = "months"
    YEARS = "years"

STANDARD_UNIT_FACTORS: dict[DurationUnit, int] = {
    DurationUnit.HOURS: 1,
    DurationUnit.DAYS: 24,
    DurationUnit.WEEKS: 24 * 7,
    DurationUnit.MONTHS: 24 * 30,
    DurationUnit.YEARS: 24 * 365,
}


def duration_to_standard_units(value: int, unit: DurationUnit) -> int:
    """Convert to a common scale using 30-day months and 365-day years."""
    return value * STANDARD_UNIT_FACTORS[unit]
