
from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from UI.main_window import MainWindow


def main() -> None:
    app = QApplication(sys.argv)
    app.setApplicationName("Fatal Bullet Save Editor")
    app.setOrganizationName("Nekoiio")

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()


"""
Couple ISSUES:
Core.Classes.Save.update_checksum <- #*Needs to be looked at it seems like the checksums first byte is being cutoff at write time



"""