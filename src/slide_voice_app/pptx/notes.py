"""Notes extraction from PPTX slides."""

import xml.etree.ElementTree as ET

from .namespaces import NSMAP


def extract_notes_text(notes_element: ET.Element) -> str:
    """Extract plain text from a notes slide XML element.

    Finds the body placeholder shape and extracts all text content.

    Args:
        notes_element: Parsed notesSlide XML element.

    Returns:
        Plain text content of the notes, with paragraphs joined by newlines.
    """
    paragraphs = []

    for shape in notes_element.findall(".//p:sp", namespaces=NSMAP):
        if not shape.findall(".//p:ph[@type='body']", namespaces=NSMAP):
            continue

        paragraphs.extend(_extract_paragraphs(shape))

    return "\n".join(paragraphs)


def _extract_paragraphs(shape_element: ET.Element) -> list[str]:
    """Extract paragraph texts from a shape element.

    Args:
        shape_element: Shape XML element containing text body.

    Returns:
        List of paragraph strings.
    """
    paragraphs = []
    p_elements = shape_element.findall(".//a:p", namespaces=NSMAP)

    for p_elem in p_elements:
        text_elements = p_elem.findall(".//a:t", namespaces=NSMAP)
        para_text = "".join((t.text or "") for t in text_elements)
        paragraphs.append(para_text)

    return paragraphs
