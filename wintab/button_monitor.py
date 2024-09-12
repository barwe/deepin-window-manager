from PySide6.QtWidgets import QPushButton
from PySide6.QtCore import Signal
from screeninfo import Monitor


class MonitorButton(QPushButton):
    activated = Signal(Monitor)

    def __init__(self, monitor: Monitor, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_activated = False
        self.monitor = monitor
        self.setText(monitor.name)
        self.clicked.connect(lambda: self.activated.emit(monitor))

    def activate(self, _bool: bool):
        self.is_activated = _bool
        color = "#2ecc71" if _bool else "none"
        self.setStyleSheet("QPushButton { background-color: %s; }" % color)
