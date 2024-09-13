from PySide6.QtWidgets import QPushButton
from PySide6.QtCore import Signal


class AppButton(QPushButton):
    clicked2 = Signal(str, bool)

    def __init__(self, label: str, wm_class: str, active=False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_activated = False
        self.wm_class = wm_class
        self.setText(label)
        self.clicked.connect(self.on_clicked)
        self.activate(active)

    def __hash__(self) -> int:
        return hash(self.wm_class)

    def activate(self, _bool: bool):
        self.is_activated = _bool
        color = "#eb5a46" if _bool else "none"
        self.setStyleSheet("QPushButton { background-color: %s; }" % color)

    def on_clicked(self):
        self.activate(not self.is_activated)
        self.clicked2.emit(self.wm_class, self.is_activated)
