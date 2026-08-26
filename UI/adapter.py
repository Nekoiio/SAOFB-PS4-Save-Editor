"""
Adapter
-------

Thin layer between Qt and your SaveFile. This is where your
binary-format-specific mutation code should live.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

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

    def _locate_equipment(self, equipment: Any) -> tuple[str | None, int | None]:
        """Find which list (weapons/accessories) an Equipment instance came
        from and its index within that list, so SaveFile methods that work
        by (type, index) can be called from a widget that only holds a
        reference to the object itself.
        """
        for i, obj in enumerate(self.weapons):
            if obj is equipment:
                return "Weapon", i
        for i, obj in enumerate(self.accessories):
            if obj is equipment:
                return "Accessory", i
        return None, None

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

        Writes the new chip ID directly into the save's binary data via
        SaveFile.modify_chip_by_index(), which also re-resolves chipName
        against the K_CHIPS catalog for you.
        """
        if self.save is None:
            return

        equipment_type, equipment_index = self._locate_equipment(equipment)
        if equipment_type is None:
            return

        try:
            self.save.modify_chip_by_index(
                equipment_type, equipment_index, index, chip_id=chip_id
            )
        except (IndexError, ValueError) as exc:
            print(f"[X] Could not set chip: {exc}")
            return

        self.mark_dirty()

    def set_chip_value(self, equipment: Any, index: int, value: str) -> None:
        """
        Hook for writing a chip's value (chipVal) separately from its ID.

        Writes directly into the save's binary data via
        SaveFile.modify_chip_by_index().
        """
        if self.save is None:
            return

        equipment_type, equipment_index = self._locate_equipment(equipment)
        if equipment_type is None:
            return

        try:
            parsed_value = float(value)
        except (TypeError, ValueError):
            print(f"[X] Chip value must be numeric, got: {value!r}")
            return

        try:
            self.save.modify_chip_by_index(
                equipment_type, equipment_index, index, value=parsed_value
            )
        except (IndexError, ValueError) as exc:
            print(f"[X] Could not set chip value: {exc}")
            return

        self.mark_dirty()
