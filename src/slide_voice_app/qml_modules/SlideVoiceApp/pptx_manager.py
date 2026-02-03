"""PPTX Manager for bridging PPTX file operations with QML UI."""

from pathlib import Path

from PySide6.QtCore import Property, QObject, Signal, Slot
from PySide6.QtQml import QmlElement, QmlSingleton

from slide_voice_app.pptx import PptxPackage
from slide_voice_app.pptx.exceptions import InvalidPptxError

QML_IMPORT_NAME = "SlideVoiceApp"
QML_IMPORT_MAJOR_VERSION = 1


@QmlElement
@QmlSingleton
class PPTXManager(QObject):
    """Manages PPTX file operations for the QML UI."""

    slidesLoaded = Signal(list)
    errorOccurred = Signal(str)
    fileLoadedChanged = Signal()

    def __init__(self, parent: QObject | None = None):
        super().__init__(parent)
        self._package: PptxPackage | None = None
        self._file_loaded: bool = False

    @Property(bool, notify=fileLoadedChanged)
    def fileLoaded(self) -> bool:
        """Whether a PPTX file is currently loaded."""
        return self._file_loaded

    def _unload_file(self):
        """Indicate file is not loaded."""
        self._file_loaded = False
        self.fileLoadedChanged.emit()

    @Slot(str)
    def openFile(self, file_url: str):
        """Open a PPTX file and load its slide notes.

        Args:
            file_url: string to the .pptx file.
        """
        path = Path(file_url.replace("file://", ""))
        self.closeFile()

        try:
            self._package = PptxPackage.open(path)
            notes = self._package.get_all_slide_notes()

            self._file_loaded = True
            self.fileLoadedChanged.emit()

            slides_data = [{"notes": note} for note in notes]
            self.slidesLoaded.emit(slides_data)

        except FileNotFoundError:
            self._unload_file()
            self.errorOccurred.emit(f"File not found: {path}")
        except InvalidPptxError as e:
            self._unload_file()
            self.errorOccurred.emit(str(e))
        except Exception as e:
            self._unload_file()
            self.errorOccurred.emit(f"Failed to open file: {e}")

    @Slot()
    def closeFile(self):
        """Close the currently open PPTX file."""
        if self._package is not None:
            self._package.close()
            self._package = None

        self._unload_file()
