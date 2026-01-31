"""Relationship (.rels) file management for PPTX."""

import xml.etree.ElementTree as ET
from zipfile import ZipFile

from .exceptions import RelsNotFoundError
from .namespaces import NAMESPACE_RELS, NSMAP_RELS


def read_rels(zip_file: ZipFile, rels_path: str) -> ET.Element:
    """Read and parse a relationship (.rels) part.

    Args:
        zip_file: Open ZipFile instance.
        rels_path: Path to the .rels part.

    Returns:
        Parsed XML Element of the relationships.

    Raises:
        RelsNotFoundError: If the .rels file does not exist in the archive.
    """
    try:
        content = zip_file.read(rels_path)
    except Exception as e:
        raise RelsNotFoundError(rels_path) from e

    return ET.fromstring(content)


def get_relationship_target(
    rels_element: ET.Element,
    rel_type: str,
) -> str | None:
    """Find a relationship target by type.

    Args:
        rels_element: Parsed .rels XML element.
        rel_type: Relationship type URI to find.

    Returns:
        Target path if found, None otherwise.
    """
    for rel in rels_element.findall(".//r:Relationship", namespaces=NSMAP_RELS):
        if rel.get("Type") == rel_type:
            return rel.get("Target")

    return None


def get_next_rid(rels_element: ET.Element) -> str:
    """Get the next available relationship ID.

    Args:
        rels_element: Parsed .rels XML element.

    Returns:
        Next available rId.
    """
    ids = [
        rel.get("Id")
        for rel in rels_element.findall(".//r:Relationship", namespaces=NSMAP_RELS)
        if rel.get("Id") is not None
    ]
    nums = [
        int(rid[3:])
        for rid in ids
        if isinstance(rid, str) and rid.startswith("rId") and rid[3:].isdigit()
    ]
    return f"rId{max(nums, default=0) + 1}"


def add_relationship(
    rels_element: ET.Element,
    rel_type: str,
    target: str,
    rid: str | None = None,
) -> str:
    """Add a new relationship to a .rels element.

    Args:
        rels_element: Parsed .rels XML element to modify.
        rel_type: Relationship type URI.
        target: Target path (relative).
        rid: Optional specific rId to use; auto-generated if None.

    Returns:
        The relationship ID used.
    """
    if rid is None:
        rid = get_next_rid(rels_element)

    rel = ET.SubElement(
        rels_element,
        f"{{{NAMESPACE_RELS}}}Relationship",
    )
    rel.set("Id", rid)
    rel.set("Type", rel_type)
    rel.set("Target", target)

    return rid
