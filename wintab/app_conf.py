from typing import TYPE_CHECKING
from collections import OrderedDict

if TYPE_CHECKING:
    from .exwindow import ExWindow


def code_code(win: "ExWindow"):
    a = win.wm_name.split(" - ")
    if len(a) == 3:
        win.data["left_text"] = a[1]
        win.data["right_text"] = a[0]
    elif len(a) == 2:
        win.data["left_text"] = a[0]


def google_chrome(win: "ExWindow"):
    a = win.wm_name.split(" - ")
    win.data["left_text"] = " - ".join(a[:-1])


def deepin_terminal(win: "ExWindow"):
    a = win.wm_name.split(" - ")
    win.data["left_text"] = " - ".join(a[:-1])


APPS = OrderedDict(
    [
        ("code.Code", {"f": code_code, "t": "VSCode"}),
        ("google-chrome.Google-chrome", {"f": google_chrome, "t": "Chrome"}),
        ("deepin-terminal.deepin-terminal", {"f": deepin_terminal, "t": "Deepin Terminal"}),
    ]
)


def better_window(win: "ExWindow"):
    d = APPS.get(win.wm_class, {})
    d["f"](win)
    if win.wm_class != "code.Code":
        lt = win.data["left_text"]
        win.data["left_text"] = f"{d['t']} - {lt}"
    return win
