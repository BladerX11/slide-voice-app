"""Custom exceptions for PPTX operations."""


class PptxError(Exception):
    """Base exception for all PPTX-related errors."""

    pass


class SlideNotFoundError(PptxError):
    """Raised when a requested slide does not exist."""

    def __init__(self, slide_index: int, total_slides: int) -> None:
        self.slide_index = slide_index
        self.total_slides = total_slides
        super().__init__(
            f"Slide index {slide_index} out of range. "
            f"Presentation has {total_slides} slide(s)."
        )


class NotesNotFoundError(PptxError):
    """Raised when slide notes are requested but do not exist."""

    def __init__(self, slide_index: int) -> None:
        self.slide_index = slide_index
        super().__init__(f"Slide notes not found for slide {slide_index}.")


class InvalidPptxError(PptxError):
    """Raised when the PPTX file is malformed or invalid."""

    def __init__(self, path: str, reason: str) -> None:
        self.path = path
        self.reason = reason
        super().__init__(f"Invalid PPTX file '{path}': {reason}")


class RelationshipNotFoundError(PptxError):
    """Raised when a required relationship is not found."""

    def __init__(self, source: str, rel_type: str) -> None:
        self.source = source
        self.rel_type = rel_type
        super().__init__(f"Relationship of type '{rel_type}' not found in '{source}'.")


class RelsNotFoundError(PptxError):
    """Raised when a .rels file does not exist in the PPTX archive."""

    def __init__(self, rels_path: str) -> None:
        self.rels_path = rels_path
        super().__init__(f"Relationships file not found in PPTX: '{rels_path}'")
