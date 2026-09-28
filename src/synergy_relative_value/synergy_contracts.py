from __future__ import annotations
from typing import Any

from .core import fit_pair

CONTRACT_ID = "synergy.trading.relative-value-signal/v1"
AUTHORITY = "relative_value_research"


def relative_value_signal_payload(
    *,
    observation_id: str,
    symbol_x: str,
    symbol_y: str,
    x_history: list[float],
    y_history: list[float],
    x_now: float,
    y_now: float,
) -> dict[str, Any]:
    if not observation_id.strip():
        raise ValueError("observation_id required")
    model = fit_pair(x_history, y_history)
    z = model.zscore(float(x_now), float(y_now))
    return {
        "observation_id": observation_id,
        "symbol_x": symbol_x.upper(),
        "symbol_y": symbol_y.upper(),
        "alpha": model.alpha,
        "beta": model.beta,
        "spread_mean": model.spread_mean,
        "spread_std": model.spread_std,
        "zscore": z,
        "authorization": False,
        "requires_domain_validation": True,
    }
