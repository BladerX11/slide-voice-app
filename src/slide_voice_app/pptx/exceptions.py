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


class RelationshipIdNotFoundError(PptxError):
    """Raised when a required relationship ID is not found."""

    def __init__(self, source: str, rid: str) -> None:
        self.source = source
        self.rid = rid
        super().__init__(
            f"Relationship ID '{rid}' not found in relationships source '{source}'."
        )


class RelationshipTargetNotFoundError(PptxError):
    """Raised when a relationship target path resolves to a missing file."""

    def __init__(self, source: str, target: str) -> None:
        self.source = source
        self.target = target
        super().__init__(
            "Relationship target "
            f"'{target}' not found from relationships source '{source}'."
        )


class RelsNotFoundError(PptxError):
    """Raised when a .rels file does not exist in the PPTX archive."""

    def __init__(self, rels_path: str) -> None:
        self.rels_path = rels_path
        super().__init__(f"Relationships file not found in PPTX: '{rels_path}'")
