import sys
from pathlib import Path

from PySide6.QtGui import QGuiApplication
from PySide6.QtCore import QUrl
from PySide6.QtQml import QQmlApplicationEngine


def main():
    app = QGuiApplication()
    engine = QQmlApplicationEngine()
    qml_file = Path(__file__).parent / "ui" / "Main.qml"
    engine.load(QUrl.fromLocalFile(qml_file))

    if not engine.rootObjects():
        sys.exit(-1)

    exit_code = app.exec()
    del engine
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
