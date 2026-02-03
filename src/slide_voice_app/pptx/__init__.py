"""PPTX manipulation module for reading and writing PowerPoint files."""

from .audio_insert import save_pptx_with_audio
from .package import PptxPackage

__all__ = [
    "PptxPackage",
    "save_pptx_with_audio",
]
