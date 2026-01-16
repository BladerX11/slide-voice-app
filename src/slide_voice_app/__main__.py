import sys

from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine

import slide_voice_app.rc_resources  # noqa: F401 # pyright: ignore [reportUnusedImport]


def main():
    app = QGuiApplication()
    engine = QQmlApplicationEngine()
    engine.load(":/ui/Main.qml")

    if not engine.rootObjects():
        sys.exit(-1)

    exit_code = app.exec()
    del engine
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
