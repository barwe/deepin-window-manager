import os
import sys
import time
import subprocess
from xuse.more import loop
from watchdog.observers import Observer
from watchdog.events import FileSystemEvent
from watchdog.events import FileSystemEventHandler

ROOT_DIR = os.path.dirname(__file__)

ENTRYPOINT = "run.py"
WATCHINGS = [
    os.path.join(ROOT_DIR, "wintab"),
]


class app:
    process: subprocess.Popen[bytes] = None

    @staticmethod
    def start():
        if app.is_running():
            return
        app.process = subprocess.Popen(["python", ENTRYPOINT, *sys.argv[1:]])
        loop.wait(lambda: not app.is_running(), timeout=5)

    @staticmethod
    def stop():
        if app.is_running():
            app.process.kill()
        loop.wait(lambda: app.is_running(), timeout=5)

    @staticmethod
    def restart():
        app.stop()
        app.start()

    @staticmethod
    def is_running():
        if app.process:
            return app.process.poll() is None
        return False


class MyHandler(FileSystemEventHandler):
    def on_modified(self, event: FileSystemEvent):
        if event.src_path.endswith(".py"):
            app.restart()


def monitor():
    event_handler = MyHandler()
    observer = Observer()
    for dp in WATCHINGS:
        observer.schedule(event_handler, dp, recursive=True)

    app.start()
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        app.stop()
        observer.stop()

    observer.join()


if __name__ == "__main__":
    app.start()
    monitor()
