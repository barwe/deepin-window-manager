from collections import defaultdict
from typing import List, DefaultDict, Sequence
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QScrollArea
from screeninfo import Monitor, get_monitors
from .ex import exlist
from .exwindow import ExWindow
from .button_window import WindowButton
from .button_monitor import MonitorButton

ACTIVE_MONITOR: Monitor = None
ACTIVE_WINDOW: ExWindow = None


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._monitor_buttons: List[MonitorButton] = []
        self._window_buttons: List[WindowButton] = []
        self._window_buttons_container = QScrollArea()
        self._previous_windows: str = None
        self.setup_ui()
        self.watch_window_changes()

    def setup_ui(self):
        layout = QVBoxLayout()
        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)
        layout.addWidget(self.create_monitor_buttons_container())
        layout.addWidget(self.create_window_buttons_container())

    def create_monitor_buttons_container(self):
        global ACTIVE_MONITOR

        y_groups: DefaultDict[int, List[Monitor]] = defaultdict(list)
        for monitor in get_monitors():
            y_groups[monitor.y].append(monitor)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self._monitor_buttons = []
        for y in sorted(y_groups.keys()):
            h_layout = QHBoxLayout()
            h_layout.setContentsMargins(0, 0, 0, 0)
            for monitor in sorted(y_groups[y], key=lambda m: m.x):
                button = MonitorButton(monitor)
                button.setFixedHeight(40)
                button.activated.connect(self.set_activated_monitor)
                self._monitor_buttons.append(button)
                h_layout.addWidget(button)
                if ACTIVE_MONITOR is None:
                    ACTIVE_MONITOR = button.monitor
                    button.activate(True)
            layout.addLayout(h_layout)

        container = QWidget()
        container.setLayout(layout)

        return container

    def create_window_buttons_container(self, windows: Sequence[ExWindow] = None):
        windows = windows or self.list_windows()[1]
        self._window_buttons = []

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 4, 0)
        for win in windows:
            button = WindowButton(win)
            button.setFixedHeight(48)
            button.activated.connect(self.set_activated_window)
            layout.addWidget(button)
            self._window_buttons.append(button)
        layout.addStretch()

        container = QWidget()
        container.setLayout(layout)

        scroll_area = self._window_buttons_container
        scroll_area.setWidget(container)
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("QScrollArea { border: none; }")

        return scroll_area

    def set_activated_monitor(self, monitor: Monitor):
        global ACTIVE_MONITOR
        if monitor == ACTIVE_MONITOR:
            return
        else:
            ACTIVE_MONITOR = monitor

        for btn in self._window_buttons:
            btn.activate(False)

        # 设置窗口按钮的激活状态
        for btn in self._monitor_buttons:
            btn.activate(btn.monitor == monitor)

        if ACTIVE_WINDOW:
            ACTIVE_WINDOW.is_minimized = True

    def set_activated_window(self, win: ExWindow):
        global ACTIVE_WINDOW
        # 切换窗口状态
        if win == ACTIVE_WINDOW:
            if btn := exlist.get(self._window_buttons, lambda d: d.win == win):
                btn.activate(not btn.is_activated)
            if win.is_minimized:
                win.xdt_move(ACTIVE_MONITOR.x, ACTIVE_MONITOR.y)
                win.xdt_maximize()
            else:
                win.xdt_minimize()
        # 切换窗口
        else:
            ACTIVE_WINDOW = win
            for btn in self._window_buttons:
                btn.activate(btn.win == win)
            win.xdt_move(ACTIVE_MONITOR.x, ACTIVE_MONITOR.y)
            win.xdt_maximize()

    def watch_window_changes(self):
        timer = QTimer(self)
        timer.setInterval(2000)
        timer.timeout.connect(self.rerender_window_buttons_container)
        timer.start()

    def rerender_window_buttons_container(self):
        is_windows_updated, windows = self.list_windows()
        if not is_windows_updated:
            return

        old_layout = self._window_buttons_container.layout()
        if old_layout:
            QWidget().setLayout(old_layout)
        self.create_window_buttons_container(windows)
        self._window_buttons_container.update()

    def list_windows(self):
        windows = ExWindow.list_windows(["code.Code"])
        flag = " ".join(sorted([w.wm_name for w in windows]))
        if flag == self._previous_windows:
            return False, windows
        self._previous_windows = flag
        return True, windows

    def move_to_screen_center(self, index: int):
        size = self.size()
        monitor = get_monitors()[index]
        x = (monitor.width - size.width()) / 2
        y = (monitor.height - size.height()) / 2
        self.move(x + monitor.x, y + monitor.y)
