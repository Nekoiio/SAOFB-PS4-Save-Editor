
from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from UI.main_window import MainWindow


def main() -> None:
    app = QApplication(sys.argv)
    app.setApplicationName("Fatal Bullet Save Editor")
    app.setOrganizationName("Obi ASM")

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
