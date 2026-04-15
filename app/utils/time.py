from datetime import UTC, datetime


def utc_now() -> datetime:
    return datetime.now(UTC)


def utc_date_key(dt: datetime | None = None) -> str:
    t = dt or utc_now()
    return t.strftime("%Y-%m-%d")
