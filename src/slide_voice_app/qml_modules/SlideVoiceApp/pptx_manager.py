"""PPTX Manager for bridging PPTX file operations with QML UI."""

import shutil
from pathlib import Path

from PySide6.QtCore import Property, QObject, QStandardPaths, Signal, Slot
from PySide6.QtQml import QmlElement, QmlSingleton

from slide_voice_app.pptx import PptxPackage, save_pptx_with_audio
from slide_voice_app.pptx.exceptions import (
    InvalidPptxError,
    SlideNotFoundError,
)

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
        self._temp_pptx_path: Path | None = None

    @Property(bool, notify=fileLoadedChanged)
    def fileLoaded(self) -> bool:
        """Whether a PPTX file is currently loaded."""
        return self._temp_pptx_path is not None

    def _unload_file(self):
        """Indicate file is not loaded."""
        self._temp_pptx_path = None
        self.fileLoadedChanged.emit()

    def _get_temp_copy_path(self, source_path: Path) -> Path:
        """Get the temp copy path for a source file."""
        temp_root = QStandardPaths.writableLocation(
            QStandardPaths.StandardLocation.TempLocation
        )
        temp_dir = Path(temp_root) / "slide-voice-app"
        temp_dir.mkdir(parents=True, exist_ok=True)
        return temp_dir / source_path.name

    @Slot(str)
    def openFile(self, file_url: str):
        """Open a PPTX file and load its slide notes.

        Args:
            file_url: string to the .pptx file.
        """
        path = Path(file_url.replace("file://", ""))

        if self._package is not None:
            self._package.close()
            self._package = None

        self._unload_file()

        try:
            self._temp_pptx_path = self._get_temp_copy_path(path)
            shutil.copy2(path, self._temp_pptx_path)
            self._package = PptxPackage.open(self._temp_pptx_path)
            self.fileLoadedChanged.emit()

            notes = self._package.get_all_slide_notes()
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

    @Slot(int, str)
    def saveAudioForSlide(self, slide_index: int, mp3_file_url: str):
        """Insert audio into the current slide of the temp PPTX copy."""
        if not mp3_file_url:
            self.errorOccurred.emit("No audio file provided")
            return

        if self._temp_pptx_path is None:
            self.errorOccurred.emit("No PPTX file loaded")
            return

        try:
            mp3_path = Path(mp3_file_url.replace("file://", ""))
            save_pptx_with_audio(self._temp_pptx_path, slide_index, mp3_path)
        except FileNotFoundError as e:
            self.errorOccurred.emit(f"File not found: {e}")
        except SlideNotFoundError as e:
            self.errorOccurred.emit(str(e))
        except Exception as e:
            self.errorOccurred.emit(f"Failed to save audio: {e}")

    @Slot(str)
    def exportTo(self, output_file_url: str):
        """Copy the temp PPTX to the selected output path."""
        if not output_file_url:
            self.errorOccurred.emit("No output file provided")
            return

        if self._temp_pptx_path is None:
            self.errorOccurred.emit("No PPTX file loaded to export")
            return
        try:
            output_path = Path(output_file_url.replace("file://", ""))
            shutil.copy2(self._temp_pptx_path, output_path)
        except Exception as e:
            self.errorOccurred.emit(f"Failed to export file: {e}")
