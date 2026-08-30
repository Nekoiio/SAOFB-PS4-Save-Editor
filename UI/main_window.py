"""
Main window
-----------
"""

from __future__ import annotations

import traceback
from pathlib import Path

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QFrame,
    QLabel,
    QPushButton,
    QListWidget,
    QListWidgetItem,
    QLineEdit,
    QHBoxLayout,
    QVBoxLayout,
    QSplitter,
    QFileDialog,
    QMessageBox,
    QStatusBar,
    QScrollArea,
)

from .paths import BRAND_IMAGE
from .style import STYLE
from .adapter import EditorAdapter
from .widgets import EquipmentEditor


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        self.adapter = EditorAdapter()
        self.current_editor: EquipmentEditor | None = None

        self.setWindowTitle("FATAL BULLET // SAVE EDITOR")
        self.setMinimumSize(1100, 720)
        self.resize(1280, 800)
        self.setStyleSheet(STYLE)

        self._build_ui()
        self._set_status("Ready — open a save file.")

    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)

        main = QVBoxLayout(central)
        main.setContentsMargins(0, 0, 0, 0)
        main.setSpacing(0)

        # ---------------------------------------------------------------
        # Top bar
        # ---------------------------------------------------------------

        top = QFrame()
        top.setObjectName("TopBar")
        top.setFixedHeight(78)

        top_layout = QHBoxLayout(top)
        top_layout.setContentsMargins(22, 12, 22, 12)
        top_layout.setSpacing(12)

        title_box = QVBoxLayout()
        title_box.setSpacing(2)
        title = QLabel("FATAL BULLET")
        title.setObjectName("Title")

        subtitle = QLabel("SAVE EDITOR  //  GUN GALE ONLINE")
        subtitle.setObjectName("Subtitle")

        title_box.addWidget(title)
        title_box.addWidget(subtitle)

        top_layout.addLayout(title_box)
        top_layout.addStretch()

        self.file_label = QLabel("NO SAVE LOADED")
        self.file_label.setObjectName("Muted")
        top_layout.addWidget(self.file_label)

        open_btn = QPushButton("OPEN SAVE")
        open_btn.clicked.connect(self.open_save)
        top_layout.addWidget(open_btn)

        save_btn = QPushButton("SAVE")
        save_btn.setObjectName("Primary")
        save_btn.clicked.connect(self.save)
        top_layout.addWidget(save_btn)

        main.addWidget(top)

        # ---------------------------------------------------------------
        # Main splitter
        # ---------------------------------------------------------------

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setHandleWidth(1)

        # Sidebar
        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        sidebar.setMinimumWidth(270)
        sidebar.setMaximumWidth(350)

        side_layout = QVBoxLayout(sidebar)
        side_layout.setContentsMargins(14, 18, 14, 14)
        side_layout.setSpacing(10)

        section = QLabel("INVENTORY")
        section.setObjectName("Accent")
        side_layout.addWidget(section)

        search = QLineEdit()
        search.setPlaceholderText("Search equipment...")
        search.textChanged.connect(self._filter_equipment)
        self.search = search
        side_layout.addWidget(search)

        self.list = QListWidget()
        self.list.currentItemChanged.connect(self._equipment_selected)
        side_layout.addWidget(self.list, 1)

        side_footer = QLabel("WEAPONS  •  ACCESSORIES")
        side_footer.setObjectName("Muted")
        side_layout.addWidget(side_footer)

        splitter.addWidget(sidebar)

        # Editor area
        right = QWidget()
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(22, 20, 22, 20)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        self.editor_container = QWidget()
        self.editor_layout = QVBoxLayout(self.editor_container)
        self.editor_layout.setContentsMargins(8, 8, 8, 8)
        self.editor_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.placeholder = QLabel(
            "OPEN A SAVE FILE\n\n"
            "Your equipment and chip inventory will appear here."
        )
        self.placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.placeholder.setObjectName("Muted")
        self.editor_layout.addWidget(self.placeholder)

        scroll.setWidget(self.editor_container)
        right_layout.addWidget(scroll)

        splitter.addWidget(right)
        splitter.setSizes([290, 900])

        main.addWidget(splitter, 1)

        # ---------------------------------------------------------------
        # Brand area in bottom-right
        # ---------------------------------------------------------------

        brand_bar = QFrame()
        brand_bar.setObjectName("TopBar")
        brand_bar.setFixedHeight(52)

        brand_layout = QHBoxLayout(brand_bar)
        brand_layout.setContentsMargins(18, 5, 18, 5)

        self.status_hint = QLabel("READY")
        self.status_hint.setObjectName("Muted")
        brand_layout.addWidget(self.status_hint)

        brand_layout.addStretch()

        brand = QLabel()
        brand.setAlignment(Qt.AlignmentFlag.AlignCenter)

        if BRAND_IMAGE.exists():
            pixmap = QPixmap(str(BRAND_IMAGE))
            if not pixmap.isNull():
                brand.setPixmap(
                    pixmap.scaled(
                        QSize(110, 36),
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation,
                    )
                )
        else:
            brand.setText("Nekoiios")
            brand.setObjectName("Accent")

        brand_layout.addWidget(brand)

        main.addWidget(brand_bar)

        self.setStatusBar(QStatusBar())

    # ------------------------------------------------------------------
    # File handling
    # ------------------------------------------------------------------

    def open_save(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Save File",
            str(Path.home()),
            "Save files (*.sav *.bin);;All files (*)",
        )

        if not path:
            return

        try:
            self.adapter.load(path)
            self.file_label.setText(Path(path).name)
            self._populate_equipment()
            self._set_status(
                f"Loaded {Path(path).name}  •  "
                f"checksum @ {self.adapter.save.checksum_offset:#x}"
            )
        except Exception as exc:
            QMessageBox.critical(
                self,
                "Could not open save",
                f"{exc}\n\n{traceback.format_exc()}",
            )

    def save(self) -> None:
        if self.adapter.save is None:
            QMessageBox.warning(self, "No save", "Open a save file first.")
            return

        if not self.adapter.dirty:
            answer = QMessageBox.question(
                self,
                "No changes",
                "No changes have been made. Save anyway?",
            )
            if answer != QMessageBox.StandardButton.Yes:
                return

        try:
            self.adapter.save_file()
            self._set_status("Saved successfully — checksum updated.")
        except Exception as exc:
            QMessageBox.critical(
                self,
                "Save failed",
                f"{exc}\n\n{traceback.format_exc()}",
            )

    # ------------------------------------------------------------------
    # Inventory
    # ------------------------------------------------------------------

    def _populate_equipment(self) -> None:
        self.list.clear()

        if self.adapter.save is None:
            return

        for kind, index, equipment in self.adapter.all_equipment():
            if len(getattr(equipment, "chips", [])) == 0:
                continue

            item = QListWidgetItem()
            item.setText(
                f"{kind.upper()}  {index + 1:02d}\n"
                f"{getattr(equipment, 'name', 'Unknown')}"
            )
            item.setData(Qt.ItemDataRole.UserRole, (kind, index, equipment))
            self.list.addItem(item)

        self._show_placeholder(
            "Select an item from the inventory.\n\n"
            f"{len(self.adapter.weapons)} weapons  •  "
            f"{len(self.adapter.accessories)} accessories"
        )

    def _filter_equipment(self, text: str) -> None:
        text = text.lower().strip()

        for i in range(self.list.count()):
            item = self.list.item(i)
            item.setHidden(text not in item.text().lower())

    def _equipment_selected(
        self,
        current: QListWidgetItem | None,
        previous: QListWidgetItem | None,
    ) -> None:
        if current is None:
            return

        kind, index, equipment = current.data(Qt.ItemDataRole.UserRole)

        if self.current_editor is not None:
            self.current_editor.deleteLater()
            self.current_editor = None

        self.current_editor = EquipmentEditor(
            self.adapter,
            kind,
            equipment,
        )

        self.current_editor.changed.connect(self._on_changed)

        # Remove placeholder/editor widgets.
        while self.editor_layout.count():
            item = self.editor_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        self.editor_layout.addWidget(self.current_editor)

    def _on_changed(self) -> None:
        self.adapter.mark_dirty()
        self._set_status("Modified — click SAVE to write changes and update checksum.")

    def _show_placeholder(self, text: str) -> None:
        while self.editor_layout.count():
            item = self.editor_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        self.placeholder = QLabel(text)
        self.placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.placeholder.setObjectName("Muted")
        self.editor_layout.addWidget(self.placeholder)

    def _set_status(self, text: str) -> None:
        self.statusBar().showMessage(text)
        self.status_hint.setText(text.upper())
