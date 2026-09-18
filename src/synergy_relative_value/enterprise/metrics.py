from __future__ import annotations

from collections import defaultdict
from threading import RLock
from typing import Mapping


def _labels(labels: Mapping[str, str] | None) -> tuple[tuple[str, str], ...]:
    return tuple(sorted((str(k), str(v)) for k, v in (labels or {}).items()))


def _label_text(labels: tuple[tuple[str, str], ...]) -> str:
    if not labels:
        return ""
    escaped = [f'{k}="{v.replace(chr(92), chr(92)*2).replace(chr(34), chr(92)+chr(34))}"' for k, v in labels]
    return "{" + ",".join(escaped) + "}"


class MetricsRegistry:
    def __init__(self, *, namespace: str = "synergy") -> None:
        self.namespace = namespace.replace("-", "_")
        self._counters = defaultdict(float)
        self._hist_count = defaultdict(int)
        self._hist_sum = defaultdict(float)
        self._gauges = {}
        self._lock = RLock()

    def inc(self, name: str, value: float = 1.0, *, labels: Mapping[str, str] | None = None) -> None:
        with self._lock:
            self._counters[(name, _labels(labels))] += float(value)

    def observe(self, name: str, value: float, *, labels: Mapping[str, str] | None = None) -> None:
        key = (name, _labels(labels))
        with self._lock:
            self._hist_count[key] += 1
            self._hist_sum[key] += float(value)

    def set_gauge(self, name: str, value: float, *, labels: Mapping[str, str] | None = None) -> None:
        with self._lock:
            self._gauges[(name, _labels(labels))] = float(value)

    def render_prometheus(self) -> str:
        lines: list[str] = []
        with self._lock:
            for (name, labels), value in sorted(self._counters.items()):
                lines.append(f"{self.namespace}_{name}{_label_text(labels)} {value}")
            for (name, labels), count in sorted(self._hist_count.items()):
                lines.append(f"{self.namespace}_{name}_count{_label_text(labels)} {count}")
                lines.append(f"{self.namespace}_{name}_sum{_label_text(labels)} {self._hist_sum[(name, labels)]}")
            for (name, labels), value in sorted(self._gauges.items()):
                lines.append(f"{self.namespace}_{name}{_label_text(labels)} {value}")
        return "\n".join(lines) + ("\n" if lines else "")
