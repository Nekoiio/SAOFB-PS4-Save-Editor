"""
Catalog loading
---------------

Handles reading the JSON catalogs (accessories/weapons/chips) and the
percent/int formatting helpers used by the chip editor.

Important:
    The JSON dictionaries are treated as {internal_id: display_name}. If your
    JSON has the opposite orientation, change `normalise_catalog()`.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

from .paths import ACCESSORIES_JSON, WEAPONS_JSON, CHIPS_JSON


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def normalise_catalog(raw: dict) -> list[tuple[str, str]]:
    """
    Convert a JSON mapping into [(id, display_name), ...].

    Expected:
        {"01": "Example Item", "02": "Another Item"}

    If your JSON is:
        {"Example Item": "01"}

    swap the two values below.
    """
    return sorted(
        [(str(key), str(value)) for key, value in raw.items()],
        key=lambda x: x[1].lower(),
    )


def format_percent(value: Any) -> str:
    """Display a raw float (e.g. 0.753) as a rounded-up percent (e.g. '76%')."""
    try:
        return f"{math.ceil(float(value) * 100)}%"
    except (TypeError, ValueError):
        return str(value)


def parse_percent(text: str) -> float:
    """Turn a user-typed percent ('76', '76%') back into a float (0.76)."""
    return float(text.strip().rstrip("%").strip()) / 100.0


# Chips whose value is a plain integer stat rather than a percentage.
INT_CHIPS: list[str] = ["VIT", "AGI", "DEX", "LUC", "STR", "INT", "Medals Acquired"]


def format_chip_value(value: Any, chip_name: str) -> str:
    """Display a chip's raw value, as an int for INT_CHIPS or a percent otherwise."""
    if chip_name in INT_CHIPS:
        try:
            return str(int(round(float(value))))
        except (TypeError, ValueError):
            return str(value)
    return format_percent(value)


def parse_chip_value(text: str, chip_name: str) -> float:
    """Turn a user-typed value back into the raw float the code side uses."""
    if chip_name in INT_CHIPS:
        return float(text.strip())
    return parse_percent(text)


try:
    K_ACCESSORIES = load_json(ACCESSORIES_JSON)
    K_WEAPONS = load_json(WEAPONS_JSON)
    K_CHIPS = load_json(CHIPS_JSON)
except FileNotFoundError:
    K_ACCESSORIES = {}
    K_WEAPONS = {}
    K_CHIPS = {}
