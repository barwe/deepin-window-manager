from PySide6.QtWidgets import QHBoxLayout, QPushButton, QLabel
from PySide6.QtCore import Signal
from wintab.exwindow import ExWindow


class WindowButton(QPushButton):

    activated = Signal(ExWindow)

    def __init__(self, win: ExWindow, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_activated = False
        self.win = win
        self.clicked.connect(lambda: self.activated.emit(win))
        self.setup_ui()

    def activate(self, _bool: bool):
        self.is_activated = _bool
        color = "#2ecc71" if _bool else "none"
        self.setStyleSheet("QPushButton { background-color: %s; }" % color)

    def setup_ui(self):
        win = self.win
        layout = QHBoxLayout()
        if win.wm_class == "code.Code":
            layout.addWidget(QLabel(win.vsc_workspace))
            layout.addStretch()
            layout.addWidget(QLabel(win.vsc_active))
        else:
            layout.addWidget(QLabel(win.wm_name))
            layout.addStretch()
        self.setLayout(layout)