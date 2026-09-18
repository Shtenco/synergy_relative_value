from __future__ import annotations

from dataclasses import dataclass
from threading import RLock
from typing import Callable, TypeVar
import time

T = TypeVar("T")


class CircuitOpenError(RuntimeError):
    pass


@dataclass(frozen=True)
class RetryPolicy:
    max_attempts: int = 3
    base_delay_seconds: float = 0.05
    max_delay_seconds: float = 1.0
    retry_exceptions: tuple[type[BaseException], ...] = (TimeoutError, ConnectionError)

    def call(self, fn: Callable[[], T]) -> T:
        if self.max_attempts < 1:
            raise ValueError("max_attempts must be >= 1")
        for attempt in range(1, self.max_attempts + 1):
            try:
                return fn()
            except self.retry_exceptions:
                if attempt >= self.max_attempts:
                    raise
                delay = min(self.max_delay_seconds, self.base_delay_seconds * (2 ** (attempt - 1)))
                if delay > 0:
                    time.sleep(delay)
        raise RuntimeError("unreachable")


class CircuitBreaker:
    def __init__(self, *, failure_threshold: int = 5, recovery_seconds: float = 30.0) -> None:
        if failure_threshold < 1 or recovery_seconds < 0:
            raise ValueError("invalid circuit breaker settings")
        self.failure_threshold = failure_threshold
        self.recovery_seconds = recovery_seconds
        self.failures = 0
        self.opened_at: float | None = None
        self._lock = RLock()

    def call(self, fn: Callable[[], T], *, now: float | None = None) -> T:
        current = time.monotonic() if now is None else now
        with self._lock:
            if self.opened_at is not None and current - self.opened_at < self.recovery_seconds:
                raise CircuitOpenError("circuit is open")
        try:
            value = fn()
        except Exception:
            with self._lock:
                self.failures += 1
                if self.failures >= self.failure_threshold:
                    self.opened_at = current
            raise
        with self._lock:
            self.failures = 0
            self.opened_at = None
        return value
