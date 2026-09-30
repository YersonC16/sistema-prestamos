from datetime import datetime, timezone


def utc_now() -> datetime:
    """Fecha y hora actual en UTC, con zona horaria."""
    return datetime.now(timezone.utc)