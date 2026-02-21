"""Shared XML helper utilities for PPTX manipulation."""

import xml.etree.ElementTree as ET

from .namespaces import NAMESPACE_CT


def ensure_child(
    parent: ET.Element, tag: str, attrs: dict[str, str] | None = None
) -> ET.Element:
    """Find or create a child element with matching attributes.

    Searches for the first child element with the given tag where all
    specified attributes match. If no match is found, creates a new
    child element with the given tag and attributes.

    Args:
        parent: Parent element to search under.
        tag: Fully-qualified tag name.
        attrs: Attributes to match and use when creating a new element.

    Returns:
        The existing or newly created child element.
    """
    for child in parent.findall(tag):
        if attrs and any(child.get(key) != value for key, value in attrs.items()):
            continue

        return child

    return ET.SubElement(parent, tag, attrs or {})


def ensure_content_type_default(
    root: ET.Element, extension: str, content_type: str
) -> None:
    """Add a Default entry to [Content_Types].xml if not present.

    Args:
        root: Root element of [Content_Types].xml.
        extension: File extension.
        content_type: MIME content type.
    """
    for default in root.findall(f"{{{NAMESPACE_CT}}}Default"):
        if default.get("Extension", "").lower() == extension.lower():
            return

    ET.SubElement(
        root,
        f"{{{NAMESPACE_CT}}}Default",
        Extension=extension,
        ContentType=content_type,
    )


def ensure_content_type_override(
    root: ET.Element, part_name: str, content_type: str
) -> None:
    """Add an Override entry to [Content_Types].xml if not present.

    Args:
        root: Root element of [Content_Types].xml.
        part_name: Absolute part path (for example: /ppt/slides/slide1.xml).
        content_type: MIME content type for the part.
    """
    for override in root.findall(f"{{{NAMESPACE_CT}}}Override"):
        if override.get("PartName") == part_name:
            return

    ET.SubElement(
        root,
        f"{{{NAMESPACE_CT}}}Override",
        PartName=part_name,
        ContentType=content_type,
    )
