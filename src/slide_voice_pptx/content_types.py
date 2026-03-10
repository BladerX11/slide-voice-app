"""Helpers for reading and updating `[Content_Types].xml`."""

import xml.etree.ElementTree as ET
from pathlib import Path

from .namespaces import NAMESPACE_CT, NSMAP_CT
from .xpath import (
    XPATH_CT_DEFAULT_BY_EXTENSION,
    XPATH_CT_OVERRIDE_BY_PATH_NAME,
)


def _read_content_types_root(work_dir: Path) -> ET.Element:
    """Read and parse `[Content_Types].xml` from a workspace."""
    return ET.fromstring((work_dir / "[Content_Types].xml").read_bytes())


def _write_content_types_root(work_dir: Path, root: ET.Element) -> None:
    """Write a parsed `[Content_Types].xml` root back to a workspace."""
    ET.register_namespace("", NAMESPACE_CT)
    (work_dir / "[Content_Types].xml").write_bytes(
        ET.tostring(root, encoding="UTF-8", xml_declaration=True)
    )


def _ensure_content_type_default(
    root: ET.Element, extension: str, content_type: str
) -> None:
    """Add a Default entry to `[Content_Types].xml` if not present."""
    if (
        root.find(
            XPATH_CT_DEFAULT_BY_EXTENSION.format(extension=extension),
            namespaces=NSMAP_CT,
        )
        is not None
    ):
        return

    ET.SubElement(
        root,
        f"{{{NAMESPACE_CT}}}Default",
        Extension=extension,
        ContentType=content_type,
    )


def _ensure_content_type_override(
    root: ET.Element, path_name: str, content_type: str
) -> None:
    """Add an Override entry to `[Content_Types].xml` if not present."""
    if (
        root.find(
            XPATH_CT_OVERRIDE_BY_PATH_NAME.format(path_name=path_name),
            namespaces=NSMAP_CT,
        )
    ) is not None:
        return

    ET.SubElement(
        root,
        f"{{{NAMESPACE_CT}}}Override",
        PartName=path_name,
        ContentType=content_type,
    )


def ensure_content_type_defaults(
    work_dir: Path,
    entries: set[tuple[str, str]],
) -> None:
    """Ensure multiple Default entries exist in `[Content_Types].xml`."""
    root = _read_content_types_root(work_dir)

    for extension, content_type in entries:
        _ensure_content_type_default(root, extension, content_type)

    _write_content_types_root(work_dir, root)


def ensure_content_type_overrides(
    work_dir: Path,
    entries: set[tuple[str, str]],
) -> None:
    """Ensure multiple Override entries exist in `[Content_Types].xml`."""
    root = _read_content_types_root(work_dir)

    for path_name, content_type in entries:
        _ensure_content_type_override(root, path_name, content_type)

    _write_content_types_root(work_dir, root)


def remove_content_type_default_if_unused(
    work_dir: Path,
    media_dir: Path,
    extension: str,
) -> None:
    """Remove a Default entry when no files use the extension."""
    if any(media_dir.glob(f"*.{extension}")):
        return

    root = _read_content_types_root(work_dir)
    default_tag = f"{{{NAMESPACE_CT}}}Default"
    removed = False

    for default in list(root.findall(default_tag)):
        if default.get("Extension") != extension:
            continue

        root.remove(default)
        removed = True

    if removed:
        _write_content_types_root(work_dir, root)
