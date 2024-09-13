from argparse import ArgumentParser
from PySide6.QtWidgets import QApplication
from wintab.window_main import MainWindow

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--maximize", action="store_true", default=False)
    parser.add_argument("--screen", type=int, default=0)
    args, other = parser.parse_known_args()
    app = QApplication(other)
    window = MainWindow()
    window.setWindowTitle("Deepin Window Manager")
    window.setMinimumSize(400, 600)
    if args.screen:
        window.move_to_screen_center(args.screen)
    if args.maximize:
        window.showMaximized()
    window.show()
    app.exec()
