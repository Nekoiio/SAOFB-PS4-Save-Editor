"""
Small widgets
-------------

ChipEditor: one row per chip (ID dropdown + value textbox).
EquipmentEditor: full editor panel for a single weapon/accessory.
"""

from __future__ import annotations

import traceback
from typing import Any

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QPushButton,
    QComboBox,
    QLineEdit,
    QHBoxLayout,
    QVBoxLayout,
    QFormLayout,
    QMessageBox,
    QGroupBox,
    QFrame,
)

from .catalog import (
    K_WEAPONS,
    K_ACCESSORIES,
    K_CHIPS,
    normalise_catalog,
    format_chip_value,
    parse_chip_value,
)
from .actions import ACTIONS, Action, APPLY_HANDLER
from .adapter import EditorAdapter


class ChipEditor(QGroupBox):
    """
    One row per chip: index label, a ChipID dropdown, and a value textbox
    next to it. `self.rows` holds (id_combo, value_edit) pairs so the parent
    editor can read everything back out (e.g. for the APPLY button).
    """

    changed = Signal()

    def __init__(self, adapter: EditorAdapter, equipment: Any) -> None:
        super().__init__("CHIPS")
        self.adapter = adapter
        self.equipment = equipment
        self.rows: list[tuple[QComboBox, QLineEdit]] = []

        layout = QVBoxLayout(self)
        layout.setSpacing(8)

        chips = getattr(equipment, "chips", [])

        if not chips:
            label = QLabel("No chips found.")
            label.setObjectName("Muted")
            layout.addWidget(label)
            return

        # Try to support either:
        #   K_CHIPS["Weapon"] = {...}
        # or:
        #   K_CHIPS = {...}
        catalog = K_CHIPS
        if isinstance(K_CHIPS, dict) and equipment is not None:
            catalog = K_CHIPS.get(getattr(equipment, "type", ""), K_CHIPS)

        for index, chip in enumerate(chips):
            row = QHBoxLayout()
            row.setSpacing(10)

            index_label = QLabel(f"{index + 1:02d}")
            index_label.setObjectName("Muted")
            index_label.setFixedWidth(24)

            id_combo = QComboBox()
            if isinstance(catalog, dict):
                for chip_id, chip_name in normalise_catalog(catalog):
                    id_combo.addItem(chip_name, chip_id)

            current_id = str(getattr(chip, "chipID", ""))
            current_idx = id_combo.findData(current_id)
            if current_idx >= 0:
                id_combo.setCurrentIndex(current_idx)

            value_edit = QLineEdit(
                format_chip_value(getattr(chip, "chipVal", 0), id_combo.currentText())
            )
            value_edit.setPlaceholderText("Value")
            value_edit.setFixedWidth(90)

            id_combo.currentIndexChanged.connect(
                lambda _i, index=index, combo=id_combo, edit=value_edit: self._id_changed(
                    index, combo, edit
                )
            )
            value_edit.editingFinished.connect(
                lambda index=index, combo=id_combo, edit=value_edit: self._value_changed(
                    index, combo, edit
                )
            )

            row.addWidget(index_label)
            row.addWidget(id_combo, 1)
            row.addWidget(value_edit)
            layout.addLayout(row)

            self.rows.append((id_combo, value_edit))

    def _id_changed(self, index: int, combo: QComboBox, edit: QLineEdit) -> None:
        chip_id = combo.currentData()
        if chip_id is None:
            return
        self.adapter.set_chip(self.equipment, index, str(chip_id))
        chip = self.equipment.chips[index]
        edit.setText(format_chip_value(getattr(chip, "chipVal", 0), combo.currentText()))
        self.changed.emit()

    def _value_changed(self, index: int, combo: QComboBox, edit: QLineEdit) -> None:
        chip_name = combo.currentText()
        try:
            value = parse_chip_value(edit.text(), chip_name)
        except ValueError:
            edit.setText(
                format_chip_value(getattr(self.equipment.chips[index], "chipVal", 0), chip_name)
            )
            return

        self.adapter.set_chip_value(self.equipment, index, value)
        edit.setText(format_chip_value(value, chip_name))
        self.changed.emit()


class EquipmentEditor(QWidget):
    changed = Signal()

    def __init__(self, adapter: EditorAdapter, kind: str, equipment: Any) -> None:
        super().__init__()
        self.adapter = adapter
        self.kind = kind
        self.equipment = equipment

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(14)

        header = QFrame()
        header.setObjectName("Card")
        h = QHBoxLayout(header)
        h.setContentsMargins(18, 14, 18, 14)

        title = QLabel(getattr(equipment, "name", "Unknown"))
        title.setObjectName("Title")
        title.setStyleSheet("font-size: 15pt;")

        type_label = QLabel(kind.upper())
        type_label.setObjectName("Accent")

        h.addWidget(title)
        h.addStretch()
        h.addWidget(type_label)

        root.addWidget(header)

        identity = QGroupBox("EQUIPMENT")
        form = QFormLayout(identity)
        form.setSpacing(10)

        self.name_combo = QComboBox()
        self.name_combo.setEditable(True)

        catalog = K_WEAPONS if kind == "Weapon" else K_ACCESSORIES

        for internal_id, display_name in normalise_catalog(catalog):
            self.name_combo.addItem(display_name, internal_id)

        current_name = str(getattr(equipment, "name", ""))
        idx = self.name_combo.findText(current_name, Qt.MatchFlag.MatchFixedString)
        if idx >= 0:
            self.name_combo.setCurrentIndex(idx)
        else:
            self.name_combo.setEditText(current_name)

        self.name_combo.currentTextChanged.connect(self._name_changed)

        form.addRow("Item", self.name_combo)

        chip_count = QLabel(str(len(getattr(equipment, "chips", []))))
        form.addRow("Chips", chip_count)

        size = QLabel(str(getattr(equipment, "size", "—")))
        form.addRow("Binary size", size)

        root.addWidget(identity)

        self.chip_editor = ChipEditor(adapter, equipment)
        self.chip_editor.changed.connect(self.changed.emit)
        root.addWidget(self.chip_editor)

        actions = QGroupBox("ACTIONS")
        action_layout = QHBoxLayout(actions)
        action_layout.setSpacing(10)

        for action_name, action in ACTIONS.items():
            button = QPushButton(action_name)
            button.clicked.connect(
                lambda checked=False, action=action: self._run_action(action)
            )
            action_layout.addWidget(button)

        action_layout.addStretch()

        apply_button = QPushButton("APPLY")
        apply_button.setObjectName("Primary")
        apply_button.clicked.connect(self._apply_data)
        action_layout.addWidget(apply_button)

        root.addWidget(actions)
        root.addStretch()

    def _name_changed(self, text: str) -> None:
        if not text:
            return

        internal_id = self.name_combo.currentData()

        # If the user typed a display name rather than selecting an item,
        # fall back to the text itself.
        if internal_id is None:
            internal_id = text

        self.adapter.set_equipment_name(self.equipment, str(internal_id))
        self.changed.emit()

    def _run_action(self, action: Action) -> None:
        try:
            action(self.adapter, self.equipment)
            self.changed.emit()
        except Exception as exc:
            QMessageBox.critical(
                self,
                "Action failed",
                f"{exc}\n\n{traceback.format_exc()}",
            )

    def _gather_data(self) -> dict:
        """Collect everything on screen needed to edit this object."""
        internal_id = self.name_combo.currentData()
        if internal_id is None:
            internal_id = self.name_combo.currentText()

        return {
            "kind": self.kind,
            "name": self.name_combo.currentText(),
            "internal_id": internal_id,
            "chips": [
                {
                    "index": i,
                    "chip_id": combo.currentData(),
                    "chip_value": self._safe_parse_value(combo.currentText(), edit.text()),
                }
                for i, (combo, edit) in enumerate(self.chip_editor.rows)
            ],
        }

    @staticmethod
    def _safe_parse_value(chip_name: str, text: str) -> float | str:
        try:
            return parse_chip_value(text, chip_name)
        except ValueError:
            return text

    def _apply_data(self) -> None:
        try:
            APPLY_HANDLER(self.adapter, self.equipment, self._gather_data())
            self.changed.emit()
        except Exception as exc:
            QMessageBox.critical(
                self,
                "Apply failed",
                f"{exc}\n\n{traceback.format_exc()}",
            )
