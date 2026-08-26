"""
Action system
-------------

To connect a function to an object, register it in ACTIONS below. Example:

    def give_max_chips(editor, equipment):
        for chip in equipment.chips:
            chip.chipVal = 1.0

    ACTIONS = {
        "Max Chip Values": give_max_chips,
    }

The function receives (editor, selected_equipment).
"""

from __future__ import annotations

from typing import Any, Callable, TYPE_CHECKING

if TYPE_CHECKING:
    from .adapter import EditorAdapter

Action = Callable[["EditorAdapter", Any], None]


def example_action(editor: "EditorAdapter", equipment: Any) -> None:
    """
    Example of connecting a function to an object.

    Replace this with one of your real modification functions.
    """
    if equipment is None:
        return

    # This is deliberately conservative: it only changes attributes that
    # already exist on your object.
    for chip in getattr(equipment, "chips", []):
        if hasattr(chip, "chipVal"):
            chip.chipVal = 1.0

    editor.mark_dirty()


ACTIONS: dict[str, Action] = {
    # Add your real functions here:
    # "Max Chip Values": example_action,
}


def apply_equipment_data(adapter: "EditorAdapter", equipment: Any, data: dict) -> None:
    """
    Called when the user clicks "APPLY" on an equipment editor.

    `data` bundles everything needed to write the change back to the save:

        {
            "kind": "Weapon" | "Accessory",
            "name": <display name currently shown in the item box>,
            "internal_id": <catalog id backing that name>,
            "chips": [
                {"index": 0, "chip_id": "...", "chip_value": "..."},
                ...
            ],
        }
    """
    print(data)


# Swap this for your real "commit to save" function.
APPLY_HANDLER: Callable[["EditorAdapter", Any, dict], None] = apply_equipment_data
