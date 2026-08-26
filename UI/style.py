"""
Styling — Fatal Bullet / GGO theme
-----------------------------------

Palette pulled from the box art: near-black gunmetal backgrounds, a hot
crosshair-red accent (instead of the old cyan), and cool steel-grey text.
"""

STYLE = """
QMainWindow, QWidget {
    background: #0a0a0c;
    color: #ece7e6;
    font-family: "Segoe UI";
    font-size: 10pt;
}

QFrame#TopBar {
    background: #111013;
    border-bottom: 1px solid #2a1417;
}

QFrame#Sidebar {
    background: #0d0c0e;
    border-right: 1px solid #2a1417;
}

QFrame#Card, QGroupBox {
    background: #151316;
    border: 1px solid #2b2124;
    border-radius: 10px;
}

QGroupBox {
    margin-top: 14px;
    padding: 18px 12px 12px 12px;
    font-weight: 600;
    letter-spacing: 0.5px;
    color: #cbb8bb;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 6px;
    color: #ff3b40;
}

QLabel#Title {
    color: #f7f2f2;
    font-size: 19pt;
    font-weight: 700;
    letter-spacing: 0.5px;
}

QLabel#Subtitle {
    color: #83777a;
    font-size: 9pt;
    letter-spacing: 1px;
}

QLabel#Accent {
    color: #ff3b40;
    font-weight: 700;
    letter-spacing: 1px;
}

QLabel#Muted {
    color: #7d7275;
}

QPushButton {
    background: #1a1719;
    border: 1px solid #34272a;
    border-radius: 7px;
    padding: 9px 16px;
    color: #e5dcdc;
}

QPushButton:hover {
    background: #221b1d;
    border-color: #ff3b40;
    color: #ffffff;
}

QPushButton:pressed {
    background: #150f11;
}

QPushButton#Primary {
    background: #c81f27;
    color: #fff5f5;
    border: none;
    font-weight: 700;
    letter-spacing: 0.5px;
}

QPushButton#Primary:hover {
    background: #ff3b40;
}

QPushButton#Primary:pressed {
    background: #a3141b;
}

QPushButton#Danger {
    background: #23131a;
    border-color: #55212b;
    color: #e7a9ae;
}

QPushButton#Danger:hover {
    border-color: #ff3b40;
    color: #ffffff;
}

QComboBox, QLineEdit {
    background: #1c181a;
    border: 1px solid #35282b;
    border-radius: 6px;
    padding: 7px 9px;
    color: #ece7e6;
    selection-background-color: #c81f27;
}

QComboBox:hover, QLineEdit:hover {
    border-color: #ff3b40;
}

QComboBox::drop-down {
    border: none;
    width: 22px;
}

QComboBox QAbstractItemView {
    background: #141115;
    color: #ece7e6;
    border: 1px solid #34272a;
    selection-background-color: #7a1218;
    selection-color: #ffffff;
    outline: none;
}

QListWidget {
    background: transparent;
    border: none;
    outline: none;
}

QListWidget::item {
    padding: 10px;
    margin: 2px 4px;
    border-radius: 6px;
    color: #b3a6a8;
}

QListWidget::item:hover {
    background: #1b1518;
}

QListWidget::item:selected {
    background: #2a1216;
    color: #ff6b6f;
    border-left: 3px solid #ff3b40;
}

QScrollArea {
    border: none;
}

QScrollBar:vertical {
    background: transparent;
    width: 10px;
    margin: 0;
}

QScrollBar::handle:vertical {
    background: #34272a;
    border-radius: 5px;
    min-height: 24px;
}

QScrollBar::handle:vertical:hover {
    background: #ff3b40;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
}

QStatusBar {
    background: #08070a;
    color: #786c6f;
    border-top: 1px solid #221417;
}

QToolButton {
    background: transparent;
    border: none;
    color: #8a7c7f;
    padding: 6px;
}

QToolButton:hover {
    color: #ff3b40;
}
"""
