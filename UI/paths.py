"""
Paths
-----

UI/ lives one level below the project root, so ROOT walks up one extra
level compared to the original single-file layout.
"""

from __future__ import annotations

from pathlib import Path

# UI/paths.py -> UI/ -> project root
ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "Data"

ACCESSORIES_JSON = DATA_DIR / "accessories.json"
WEAPONS_JSON = DATA_DIR / "weapons.json"
CHIPS_JSON = DATA_DIR / "chips.json"

# Put your logo/brand image here. PNG/SVG/JPG all work.
BRAND_IMAGE = ROOT / "brand.png"
