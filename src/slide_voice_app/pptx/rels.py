"""Relationship (.rels) file management for PPTX."""

import xml.etree.ElementTree as ET
from pathlib import Path
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


def read_rels_path(rels_path: Path) -> ET.Element:
    """Read and parse a relationship (.rels) part from disk.

    Args:
        rels_path: Path to the .rels part.

    Returns:
        Parsed XML Element of the relationships.

    Raises:
        RelsNotFoundError: If the .rels file does not exist on disk.
    """
    if not rels_path.exists():
        raise RelsNotFoundError(str(rels_path))

    return ET.fromstring(rels_path.read_bytes())


def get_relationships_target_by_type(
    rels_element: ET.Element,
    rel_type: str,
) -> list[str]:
    """Find all relationships matching a specific type.

    Args:
        rels_element: Parsed .rels XML element.
        rel_type: Relationship type URI to find.

    Returns:
        List of matching relationship with targets.
    """
    return [
        target
        for rel in rels_element.findall(".//r:Relationship", namespaces=NSMAP_RELS)
        if rel.get("Type") == rel_type and (target := rel.get("Target"))
    ]


def find_relationship_by_type_and_target(
    rels_element: ET.Element,
    rel_type: str,
    target: str,
) -> str | None:
    """Find existing relationship with matching type and target, return rId or None.

    Args:
        rels_element: Parsed .rels XML element.
        rel_type: Relationship type URI.
        target: Target path for the relationship.

    Returns:
        Relationship ID (rId) if found, None otherwise.
    """
    for rel in rels_element.findall(".//r:Relationship", namespaces=NSMAP_RELS):
        if rel.get("Type") == rel_type and rel.get("Target") == target:
            return rel.get("Id")

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
