""""
binary-format-specific mutation code should live.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .catalog import K_CHIPS

from Core.Classes.Objects import Equipment, Accessory, Weapon, Chip
from Core.Classes.Save import SaveFile


class EditorAdapter:
    def __init__(self) -> None:
        self.save: Any = None
        self.path: Path | None = None
        self.dirty = False

    @property
    def weapons(self) -> list:
        return getattr(self.save, "weapons", []) if self.save else []

    @property
    def accessories(self) -> list:
        return getattr(self.save, "accessories", []) if self.save else []

    def load(self, path: str) -> None:
        if SaveFile is None:
            raise RuntimeError(
                "Could not import Core.Classes.Save.SaveFile.\n"
                "Run this from your project root and make sure Core/Classes/Save.py exists."
            )

        self.path = Path(path)
        self.save = SaveFile(str(self.path))
        self.dirty = False

    def mark_dirty(self) -> None:
        self.dirty = True

    def save_file(self, path: str | None = None) -> None:
        if self.save is None:
            raise RuntimeError("No save file is loaded.")

        self.save.save(path)
        if path:
            self.path = Path(path)
        self.dirty = False

    def all_equipment(self) -> list:
        return [
            ("Weapon", i, obj)
            for i, obj in enumerate(self.weapons)
        ] + [
            ("Accessory", i, obj)
            for i, obj in enumerate(self.accessories)
        ]

    def set_equipment_name(self, equipment: Any, internal_id: str) -> None:
        """
        Hook for your actual binary mutation.

        Your current Equipment object stores the translated name in
        `self.name`, so this updates that attribute as well. If your binary
        representation requires changing the underlying bytearray, replace
        this method with that logic.
        """
        equipment.name = internal_id
        self.mark_dirty()

    def set_chip(self, equipment: Any, index: int, chip_id: str) -> None:
        """
        Hook for replacing a chip.

        Your current Chip class derives chipName from chipID, so this updates
        chipID/chipName. Replace/extend this method if you also need to write
        the binary bytes in SaveFile.data.
        """
        chips = getattr(equipment, "chips", [])
        if not (0 <= index < len(chips)):
            return

        chip = chips[index]
        chip.chipID = chip_id

        try:
            chip.chipName = K_CHIPS[equipment.type][chip_id]
        except (KeyError, AttributeError):
            try:
                chip.chipName = K_CHIPS[chip_id]
            except (KeyError, TypeError):
                chip.chipName = chip_id

        self.mark_dirty()

    def set_chip_value(self, equipment: Any, index: int, value: str) -> None:
        """
        Hook for writing a chip's value (chipVal) separately from its ID.
        """
        chips = getattr(equipment, "chips", [])
        if not (0 <= index < len(chips)):
            return

        chip = chips[index]
        try:
            chip.chipVal = float(value)
        except (TypeError, ValueError):
            chip.chipVal = value

        self.mark_dirty()
