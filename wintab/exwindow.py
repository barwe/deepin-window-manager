import subprocess
from typing import Sequence
from wmctrl import Window, getoutput


class ExWindow(Window):
    wm_class: str
    wm_name: str
    vsc_active: str = None
    vsc_workspace: str = None
    uid: str = None
    is_minimized = False

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
    def list_windows(include=None) -> Sequence["ExWindow"]:
        windows = []
        for d in ExWindow.list():
            if d.desktop == -1:
                continue
            if include and d.wm_class not in include:
                continue

            if d.wm_class == "code.Code":
                a = d.wm_name.split(" - ")
                if len(a) == 3:
                    d.vsc_active = a[0]
                    d.vsc_workspace = a[1]
                elif len(a) == 2:
                    d.vsc_workspace = a[0]

            windows.append(d)
        return sorted(windows, key=lambda d: d.wm_class)
