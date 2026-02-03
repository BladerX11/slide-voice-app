"""Main PPTX package interface."""

import xml.etree.ElementTree as ET
from os import path
from pathlib import Path
from typing import Self
from zipfile import ZipFile

from .exceptions import (
    InvalidPptxError,
    NotesNotFoundError,
    SlideNotFoundError,
)
from .namespaces import NSMAP_RELS, REL_TYPE_NOTES_SLIDE, REL_TYPE_SLIDE
from .notes import extract_notes_text
from .rels import (
    get_relationship_target,
    read_rels,
)


class PptxPackage:
    """Interface for reading and manipulating PPTX files.

    This class provides a high-level API for working with PowerPoint files,
    handling the underlying ZIP structure and XML parsing.
    """

    def __init__(self, zip_file: ZipFile, path: Path):
        """Initialize PptxPackage.

        Args:
            zip_file: Open ZipFile instance.
            path: Path to the source file.
        """
        self._zip = zip_file
        self._path = path
        self._slide_paths = None

    @classmethod
    def open(cls, path: Path) -> Self:
        """Open a PPTX file for reading.

        Args:
            path: Path to the .pptx file.

        Returns:
            PptxPackage instance.

        Raises:
            InvalidPptxError: If the file is not a valid PPTX.
            FileNotFoundError: If the file doesn't exist.
        """
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        try:
            zip_file = ZipFile(path, "r")
        except Exception as e:
            raise InvalidPptxError(str(path), f"Cannot open as ZIP: {e}") from e

        if "ppt/presentation.xml" not in zip_file.namelist():
            zip_file.close()
            raise InvalidPptxError(str(path), "Missing ppt/presentation.xml")

        return cls(zip_file, path)

    def close(self):
        """Close the PPTX file."""
        self._zip.close()

    @property
    def slide_count(self) -> int:
        """Get the number of slides in the presentation."""
        return len(self._get_slide_paths())

    def _get_slide_paths(self) -> list[str]:
        """Get ordered list of slide part paths.

        Returns:
            List of slide paths.

        Raises:
            RelsNotFoundError: If presentation relationships are missing.
        """
        if self._slide_paths is not None:
            return self._slide_paths

        rels = read_rels(self._zip, "ppt/_rels/presentation.xml.rels")
        targets = [
            rel.get("Target")
            for rel in rels.findall(
                f".//r:Relationship[@Type='{REL_TYPE_SLIDE}']", NSMAP_RELS
            )
            if rel.get("Target") is not None
        ]
        slides = []

        for target in targets:
            target_str = str(target)

            if "slides/slide" not in target_str:
                continue

            full_path = f"ppt/{target_str}"
            slide_num = int(full_path.split("slide")[-1].replace(".xml", ""))
            slides.append((slide_num, full_path))

        slides.sort(key=lambda x: x[0])
        self._slide_paths = [path for _, path in slides]
        return self._slide_paths

    def _get_slide_path(self, slide_index: int) -> str:
        """Get the path for a slide by index.

        Args:
            slide_index: Zero-based slide index.

        Returns:
            Path to the slide XML.

        Raises:
            RelsNotFoundError: If presentation relationships are missing.
            SlideNotFoundError: If index is out of range.
        """
        paths = self._get_slide_paths()

        if slide_index < 0 or slide_index >= len(paths):
            raise SlideNotFoundError(slide_index, len(paths))

        return paths[slide_index]

    def get_slide_notes(self, slide_index: int) -> str:
        """Get the notes text for a slide.

        Args:
            slide_index: Zero-based slide index.

        Returns:
            Notes text as plain string

        Raises:
            RelsNotFoundError: If presentation or slide relationships are missing.
            SlideNotFoundError: If slide index is out of range.
        """
        slide_path = self._get_slide_path(slide_index)
        slide_filename = slide_path.split("/")[-1]
        slide_rels_path = f"ppt/slides/_rels/{slide_filename}.rels"
        slide_rels = read_rels(self._zip, slide_rels_path)
        notes_target = get_relationship_target(slide_rels, REL_TYPE_NOTES_SLIDE)

        if notes_target is None:
            return ""

        notes_path = path.normpath(path.join(path.dirname(slide_path), notes_target))

        try:
            notes_content = self._zip.read(notes_path)
        except Exception as e:
            raise NotesNotFoundError(slide_index) from e

        notes_element = ET.fromstring(notes_content)
        return extract_notes_text(notes_element)

    def get_all_slide_notes(self) -> list[str]:
        """Get notes for all slides.

        Returns:
            List of notes text (or None) for each slide, in order.
        """
        return [self.get_slide_notes(i) for i in range(self.slide_count)]
