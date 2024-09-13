import subprocess
from typing import Sequence
from wmctrl import Window, getoutput
from .app_conf import better_window


class ExWindow(Window):
    wm_class: str
    wm_name: str

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data: dict[str, str] = {}
        self.is_minimized = False

    def xdt_maximize(self):
        self.is_minimized = False
        subprocess.call(["xdotool", "windowactivate", self.id])

    def xdt_minimize(self):
        subprocess.call(["xdotool", "windowminimize", self.id])
        self.is_minimized = True

    def xdt_move(self, x, y):
        self.unmaximize()
        return super().move(x, y)

    @classmethod
    def list(cls) -> Sequence["ExWindow"]:
        out = getoutput("wmctrl -l -G -p -x")
        windows = []
        for line in out.splitlines():
            parts = line.split(None, 9)
            parts = list(map(str.strip, parts))
            parts[1:7] = list(map(int, parts[1:7]))
            if len(parts) == 9:  # title is missing
                parts.append("")
            elif len(parts) != 10:
                continue  # something was wrong
            windows.append(cls(*parts))
        return windows

    @staticmethod
    def list_windows(include) -> Sequence["ExWindow"]:
        windows = []
        include = include or []
        for win in ExWindow.list():
            if win.desktop == -1:
                continue
            if win.wm_class not in include:
                continue
            windows.append(better_window(win))
        return sorted(windows, key=lambda d: d.wm_class)
