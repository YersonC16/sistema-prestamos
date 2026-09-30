import time

from app.core.config import settings


class LoginAttemptTracker:
    """Limita los intentos fallidos de inicio de sesión por correo.
    Vive en memoria: se reinicia cuando se reinicia el servicio."""

    def __init__(self, max_attempts: int, lock_seconds: int):
        self._max_attempts = max_attempts
        self._lock_seconds = lock_seconds
        self._failures: dict[str, list[float]] = {}
        self._locked_until: dict[str, float] = {}

    def seconds_locked(self, key: str) -> int:
        until = self._locked_until.get(key)
        if until is None:
            return 0
        remaining = until - time.monotonic()
        if remaining <= 0:
            self._locked_until.pop(key, None)
            self._failures.pop(key, None)
            return 0
        return int(remaining) + 1

    def register_failure(self, key: str) -> bool:
        """Devuelve True si con este fallo la cuenta queda bloqueada."""
        now = time.monotonic()
        window_start = now - self._lock_seconds
        attempts = [t for t in self._failures.get(key, []) if t > window_start]
        attempts.append(now)
        self._failures[key] = attempts
        if len(attempts) >= self._max_attempts:
            self._locked_until[key] = now + self._lock_seconds
            return True
        return False

    def register_success(self, key: str) -> None:
        self._failures.pop(key, None)
        self._locked_until.pop(key, None)

    def reset_all(self) -> None:
        self._failures.clear()
        self._locked_until.clear()


login_tracker = LoginAttemptTracker(settings.login_max_attempts, settings.login_lock_seconds)