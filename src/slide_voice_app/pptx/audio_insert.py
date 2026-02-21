"""Insert audio into PPTX slides with autoplay on slide start."""

import hashlib
import re
import uuid
import xml.etree.ElementTree as ET
from importlib.resources import files
from pathlib import Path

from .namespaces import (
    NAMESPACE_A,
    NAMESPACE_A16,
    NAMESPACE_CT,
    NAMESPACE_P,
    NAMESPACE_P14,
    NAMESPACE_R,
    NAMESPACE_RELS,
    REL_TYPE_AUDIO,
    REL_TYPE_IMAGE,
    REL_TYPE_MEDIA,
)
from .rels import (
    add_relationship,
    find_relationship_by_type_and_target,
)
from .xml_helper import ensure_child, ensure_content_type_default

DEFAULT_ICON_X = 5730875
DEFAULT_ICON_Y = 3063875
DEFAULT_ICON_CX = 730250
DEFAULT_ICON_CY = 730250

DEFAULT_VOLUME = 80000


def _get_narration_icon_bytes() -> bytes:
    """Load the bundled narration icon PNG bytes.

    Returns:
        PNG image data as bytes.
    """

    return (
        files("slide_voice_app.pptx")
        .joinpath("resources", "narration-icon.png")
        .read_bytes()
    )


def _find_media_files(media_dir: Path, prefix: str, ext: str) -> list[str]:
    """Find existing media files matching prefix and extension.

    Args:
        media_dir: Path to ppt/media directory.
        prefix: Filename prefix.
        ext: File extension without dot.

    Returns:
        List of filenames, not full paths.
    """
    pattern = re.compile(rf"^{prefix}(\d+)\.{ext}$")

    return [
        file_path.name
        for file_path in media_dir.iterdir()
        if file_path.is_file() and pattern.match(file_path.name)
    ]


def _next_media_filename(existing: list[str], prefix: str, ext: str) -> str:
    """Allocate next available media filename.

    Args:
        existing: List of existing media filenames.
        prefix: Filename prefix.
        ext: File extension without dot.

    Returns:
        Next available filename like 'media1.mp3'.
    """
    pattern = re.compile(rf"^{prefix}(\d+)\.{ext}$")
    max_num = max(
        [int(m.group(1)) for name in existing if (m := pattern.match(name))], default=0
    )

    return f"{prefix}{max_num + 1}.{ext}"


def _find_existing_media_by_hash(
    media_dir: Path, existing: list[str], target_hash: str
) -> str | None:
    """Find an existing media file with matching hash, return filename or None.

    Args:
        media_dir: Path to ppt/media directory.
        existing: List of existing media filenames.
        target_hash: SHA-256 hash to match against.

    Returns:
        Filename if found, None otherwise.
    """
    for name in existing:
        file_path = media_dir / name

        if (
            file_path.exists()
            and hashlib.sha256(file_path.read_bytes()).hexdigest() == target_hash
        ):
            return name

    return None


def _get_max_shape_id(slide_root: ET.Element) -> int:
    """Scan slide XML for maximum shape/target id values.

    Args:
        slide_root: Root element of the slide XML.

    Returns:
        Maximum shape ID found, or 0 if none found.
    """
    targets = [("cNvPr", "id"), ("spTgt", "spid")]
    found_ids = [
        int(val)
        for tag, attr in targets
        for elem in slide_root.findall(f".//{{{NAMESPACE_P}}}{tag}[@{attr}]")
        if (val := elem.get(attr))
    ]

    return max(found_ids, default=0)


def _get_max_ctn_id(slide_root: ET.Element) -> int:
    """Scan slide timing nodes for maximum cTn id values.

    Args:
        slide_root: Root element of the slide XML.

    Returns:
        Maximum cTn ID found, or 0 if none found.
    """
    ids = (
        int(val)
        for elem in slide_root.findall(f".//{{{NAMESPACE_P}}}cTn[@id]")
        if (val := elem.get("id")) is not None
    )

    return max(ids, default=0)


def _create_pic_element(
    spid: int,
    name: str,
    media_rid: str,
    audio_rid: str,
    image_rid: str,
    x: int = DEFAULT_ICON_X,
    y: int = DEFAULT_ICON_Y,
    cx: int = DEFAULT_ICON_CX,
    cy: int = DEFAULT_ICON_CY,
) -> ET.Element:
    """Create a p:pic element for the audio icon.

    Args:
        spid: Shape ID for the picture element.
        name: Name attribute for the picture.
        media_rid: Relationship ID for the media file.
        audio_rid: Relationship ID for the audio file.
        image_rid: Relationship ID for the icon image.
        x: X coordinate for icon position (EMU).
        y: Y coordinate for icon position (EMU).
        cx: Width of icon (EMU).
        cy: Height of icon (EMU).

    Returns:
        The created p:pic ElementTree element.
    """
    ET.register_namespace("p", NAMESPACE_P)
    ET.register_namespace("a", NAMESPACE_A)
    ET.register_namespace("r", NAMESPACE_R)
    ET.register_namespace("p14", NAMESPACE_P14)
    ET.register_namespace("a16", NAMESPACE_A16)

    pic = ET.Element(f"{{{NAMESPACE_P}}}pic")

    nv_pic_pr = ET.SubElement(pic, f"{{{NAMESPACE_P}}}nvPicPr")
    c_nv_pr = ET.SubElement(
        nv_pic_pr, f"{{{NAMESPACE_P}}}cNvPr", id=str(spid), name=name
    )
    ET.SubElement(
        c_nv_pr,
        f"{{{NAMESPACE_A}}}hlinkClick",
        {f"{{{NAMESPACE_R}}}id": "", "action": "ppaction://media"},
    )
    ext_lst = ET.SubElement(c_nv_pr, f"{{{NAMESPACE_A}}}extLst")
    ext = ET.SubElement(
        ext_lst,
        f"{{{NAMESPACE_A}}}ext",
        uri="{FF2B5EF4-FFF2-40B4-BE49-F238E27FC236}",
    )
    ET.SubElement(
        ext,
        f"{{{NAMESPACE_A16}}}creationId",
        id=f"{{{str(uuid.uuid4()).upper()}}}",
    )
    c_nv_pic_pr = ET.SubElement(nv_pic_pr, f"{{{NAMESPACE_P}}}cNvPicPr")
    ET.SubElement(c_nv_pic_pr, f"{{{NAMESPACE_A}}}picLocks", noChangeAspect="1")
    nv_pr = ET.SubElement(nv_pic_pr, f"{{{NAMESPACE_P}}}nvPr")
    ET.SubElement(
        nv_pr, f"{{{NAMESPACE_A}}}audioFile", {f"{{{NAMESPACE_R}}}link": audio_rid}
    )
    nv_ext_lst = ET.SubElement(nv_pr, f"{{{NAMESPACE_P}}}extLst")
    nv_ext = ET.SubElement(
        nv_ext_lst,
        f"{{{NAMESPACE_P}}}ext",
        uri="{DAA4B4D4-6D71-4841-9C94-3DE7FCFB9230}",
    )
    ET.SubElement(
        nv_ext, f"{{{NAMESPACE_P14}}}media", {f"{{{NAMESPACE_R}}}embed": media_rid}
    )

    blip_fill = ET.SubElement(pic, f"{{{NAMESPACE_P}}}blipFill")
    ET.SubElement(
        blip_fill, f"{{{NAMESPACE_A}}}blip", {f"{{{NAMESPACE_R}}}embed": image_rid}
    )
    stretch = ET.SubElement(blip_fill, f"{{{NAMESPACE_A}}}stretch")
    ET.SubElement(stretch, f"{{{NAMESPACE_A}}}fillRect")

    sp_pr = ET.SubElement(pic, f"{{{NAMESPACE_P}}}spPr")
    xfrm = ET.SubElement(sp_pr, f"{{{NAMESPACE_A}}}xfrm")
    ET.SubElement(xfrm, f"{{{NAMESPACE_A}}}off", x=str(x), y=str(y))
    ET.SubElement(xfrm, f"{{{NAMESPACE_A}}}ext", cx=str(cx), cy=str(cy))
    prst_geom = ET.SubElement(sp_pr, f"{{{NAMESPACE_A}}}prstGeom", prst="rect")
    ET.SubElement(prst_geom, f"{{{NAMESPACE_A}}}avLst")

    return pic


def _get_common_timing_prefix(slide_root: ET.Element) -> ET.Element:
    """Ensure timing prefix exists and return the root childTnLst.

    Path: p:timing/p:tnLst/p:par/p:cTn/p:childTnLst

    Args:
        slide_root: Root element of the slide XML.

    Returns:
        The childTnLst element for appending audio nodes.
    """
    p = NAMESPACE_P
    timing = ensure_child(slide_root, f"{{{p}}}timing", {})
    tn_lst = ensure_child(timing, f"{{{p}}}tnLst", {})
    par = ensure_child(tn_lst, f"{{{p}}}par", {})
    c_tn_root = ensure_child(
        par,
        f"{{{p}}}cTn",
        {
            "dur": "indefinite",
            "restart": "never",
            "nodeType": "tmRoot",
        },
    )

    if c_tn_root.get("id") is None:
        max_id = _get_max_ctn_id(slide_root)
        c_tn_root.set("id", str(max_id + 1))

    child_tn_lst = ensure_child(c_tn_root, f"{{{p}}}childTnLst", {})

    return child_tn_lst


def _get_or_create_command_parent(slide_root: ET.Element) -> ET.Element:
    """Find or create the childTnLst where command nodes should be appended.

    Path: p:timing/p:tnLst/p:par/p:cTn/p:childTnLst/
          p:seq/p:cTn/p:childTnLst/p:par/p:cTn/p:childTnLst

    Args:
        slide_root: Root element of the slide XML.

    Returns:
        The childTnLst element for appending command nodes.
    """
    p = NAMESPACE_P
    root_child_tn_lst = _get_common_timing_prefix(slide_root)

    seq = ensure_child(
        root_child_tn_lst,
        f"{{{p}}}seq",
        {"concurrent": "1", "nextAc": "seek"},
    )
    c_tn_seq = ensure_child(
        seq,
        f"{{{p}}}cTn",
        {"dur": "indefinite", "nodeType": "mainSeq"},
    )

    if c_tn_seq.get("id") is None:
        max_id = _get_max_ctn_id(slide_root)
        c_tn_seq.set("id", str(max_id + 1))

    child_tn_lst = ensure_child(c_tn_seq, f"{{{p}}}childTnLst", {})
    par = ensure_child(child_tn_lst, f"{{{p}}}par", {})
    c_tn_inner = ensure_child(par, f"{{{p}}}cTn", {"fill": "hold"})

    if c_tn_inner.get("id") is None:
        max_id = _get_max_ctn_id(slide_root)
        c_tn_inner.set("id", str(max_id + 1))

    st_cond_lst = ensure_child(c_tn_inner, f"{{{p}}}stCondLst", {})
    ensure_child(st_cond_lst, f"{{{p}}}cond", {"delay": "indefinite"})
    cond_on_begin = ensure_child(
        st_cond_lst,
        f"{{{p}}}cond",
        {"evt": "onBegin", "delay": "0"},
    )
    ensure_child(cond_on_begin, f"{{{p}}}tn", {"val": c_tn_seq.get("id", "")})

    command_parent = ensure_child(c_tn_inner, f"{{{p}}}childTnLst", {})

    prev_cond_lst = ensure_child(seq, f"{{{p}}}prevCondLst", {})
    cond_prev = ensure_child(
        prev_cond_lst,
        f"{{{p}}}cond",
        {"evt": "onPrev", "delay": "0"},
    )
    tgt_prev = ensure_child(cond_prev, f"{{{p}}}tgtEl", {})
    ensure_child(tgt_prev, f"{{{p}}}sldTgt", {})

    next_cond_lst = ensure_child(seq, f"{{{p}}}nextCondLst", {})
    cond_next = ensure_child(
        next_cond_lst,
        f"{{{p}}}cond",
        {"evt": "onNext", "delay": "0"},
    )
    tgt_next = ensure_child(cond_next, f"{{{p}}}tgtEl", {})
    ensure_child(tgt_next, f"{{{p}}}sldTgt", {})

    return command_parent


def _get_or_create_audio_parent(slide_root: ET.Element) -> ET.Element:
    """Find or create the childTnLst where audio nodes should be appended.

    Path: p:timing/p:tnLst/p:par/p:cTn/p:childTnLst

    Args:
        slide_root: Root element of the slide XML.

    Returns:
        The childTnLst element for appending audio nodes.
    """
    return _get_common_timing_prefix(slide_root)


def _get_or_create_pic_parent(slide_root: ET.Element) -> ET.Element:
    """Find or create the spTree where pic nodes should be appended.

    Path: p:cSld/p:spTree

    Args:
        slide_root: Root element of the slide XML.

    Returns:
        The spTree element for appending pic nodes.
    """
    p = NAMESPACE_P
    c_sld = ensure_child(slide_root, f"{{{p}}}cSld", {})
    sp_tree = ensure_child(c_sld, f"{{{p}}}spTree", {})
    return sp_tree


def _compute_next_delay(cmd_parent: ET.Element) -> int:
    """Compute delay for new command based on existing playFrom commands.

    Delay increments by 1 for each existing command.

    Args:
        cmd_parent: The childTnLst element containing command nodes.

    Returns:
        Delay for the next audio command.
    """
    p = NAMESPACE_P
    max_delay = -1

    for cond in cmd_parent.findall(
        f".//{{{p}}}par/{{{p}}}cTn/{{{p}}}stCondLst/{{{p}}}cond[@delay]"
    ):
        s = cond.get("delay", "")

        if s.isdigit():
            max_delay = max(max_delay, int(s))

    return max_delay + 1


def _create_command_node(spid: int, delay: int, base_id: int) -> ET.Element:
    """Create a p:par command node for autoplay.

    Args:
        spid: Shape ID to target with the command.
        delay: The index of command within its parent.
        base_id: Starting ID for timing node IDs.

    Returns:
        The created command node element.
    """
    p = NAMESPACE_P

    par = ET.Element(f"{{{p}}}par")
    c_tn_outer = ET.SubElement(par, f"{{{p}}}cTn", id=str(base_id), fill="hold")

    st_cond_lst = ET.SubElement(c_tn_outer, f"{{{p}}}stCondLst")
    ET.SubElement(st_cond_lst, f"{{{p}}}cond", delay=str(delay))

    child_tn_lst = ET.SubElement(c_tn_outer, f"{{{p}}}childTnLst")
    inner_par = ET.SubElement(child_tn_lst, f"{{{p}}}par")
    c_tn_inner = ET.SubElement(
        inner_par,
        f"{{{p}}}cTn",
        id=str(base_id + 1),
        presetID="1",
        presetClass="mediacall",
        presetSubtype="0",
        fill="hold",
        nodeType="afterEffect",
    )

    st_cond_lst_inner = ET.SubElement(c_tn_inner, f"{{{p}}}stCondLst")
    ET.SubElement(st_cond_lst_inner, f"{{{p}}}cond", delay="0")

    child_tn_lst_inner = ET.SubElement(c_tn_inner, f"{{{p}}}childTnLst")
    cmd = ET.SubElement(
        child_tn_lst_inner, f"{{{p}}}cmd", type="call", cmd="playFrom(0.0)"
    )

    c_bhvr = ET.SubElement(cmd, f"{{{p}}}cBhvr")
    ET.SubElement(
        c_bhvr,
        f"{{{p}}}cTn",
        id=str(base_id + 2),
        dur=str(1),
        fill="hold",
    )
    tgt_el = ET.SubElement(c_bhvr, f"{{{p}}}tgtEl")
    ET.SubElement(tgt_el, f"{{{p}}}spTgt", spid=str(spid))

    return par


def _create_audio_node(
    spid: int, timing_id: int, volume: int = DEFAULT_VOLUME
) -> ET.Element:
    """Create a p:audio node for the media.

    Args:
        spid: Shape ID of the audio icon.
        timing_id: ID for the timing node.
        volume: Audio volume level (default: 80000).

    Returns:
        The created audio node element.
    """
    p = NAMESPACE_P

    audio = ET.Element(f"{{{p}}}audio")
    c_media_node = ET.SubElement(
        audio, f"{{{p}}}cMediaNode", vol=str(volume), showWhenStopped="0"
    )

    c_tn = ET.SubElement(
        c_media_node, f"{{{p}}}cTn", id=str(timing_id), fill="hold", display="0"
    )

    st_cond_lst = ET.SubElement(c_tn, f"{{{p}}}stCondLst")
    ET.SubElement(st_cond_lst, f"{{{p}}}cond", delay="indefinite")

    end_cond_lst = ET.SubElement(c_tn, f"{{{p}}}endCondLst")
    cond = ET.SubElement(end_cond_lst, f"{{{p}}}cond", evt="onStopAudio", delay="0")
    tgt_el = ET.SubElement(cond, f"{{{p}}}tgtEl")
    ET.SubElement(tgt_el, f"{{{p}}}sldTgt")

    tgt_el_2 = ET.SubElement(c_media_node, f"{{{p}}}tgtEl")
    ET.SubElement(tgt_el_2, f"{{{p}}}spTgt", spid=str(spid))

    return audio


def add_audio_to_slide(
    work_path: Path,
    slide_part_path: str,
    mp3_path: Path,
) -> None:
    """Insert audio into an extracted slide workspace.

    Args:
        work_path: Extracted PPTX workspace root directory.
        slide_part_path: OOXML slide path (e.g. ppt/slides/slide1.xml).
        mp3_path: Path to the MP3 audio file to insert.

    Raises:
        FileNotFoundError: If input files don't exist.
    """
    if not work_path.exists() or not work_path.is_dir():
        raise FileNotFoundError(f"Workspace not found: {work_path}")

    if not mp3_path.exists():
        raise FileNotFoundError(f"MP3 file not found: {mp3_path}")

    mp3_data = mp3_path.read_bytes()
    mp3_hash = hashlib.sha256(mp3_data).hexdigest()

    icon_data = _get_narration_icon_bytes()
    icon_hash = hashlib.sha256(icon_data).hexdigest()

    ET.register_namespace("", NAMESPACE_CT)
    ET.register_namespace("p", NAMESPACE_P)
    ET.register_namespace("a", NAMESPACE_A)
    ET.register_namespace("p14", NAMESPACE_P14)
    ET.register_namespace("a16", NAMESPACE_A16)

    slide_path = work_path / slide_part_path

    if not slide_path.exists():
        raise FileNotFoundError(f"Slide not found in workspace: {slide_part_path}")

    media_dir = work_path / "ppt/media"
    media_dir.mkdir(parents=True, exist_ok=True)

    existing_mp3s = _find_media_files(media_dir, "media", "mp3")
    existing_pngs = _find_media_files(media_dir, "image", "png")

    mp3_filename = _find_existing_media_by_hash(media_dir, existing_mp3s, mp3_hash)
    icon_filename = _find_existing_media_by_hash(media_dir, existing_pngs, icon_hash)

    if mp3_filename is None:
        mp3_filename = _next_media_filename(existing_mp3s, "media", "mp3")
        (media_dir / mp3_filename).write_bytes(mp3_data)

    if icon_filename is None:
        icon_filename = _next_media_filename(existing_pngs, "image", "png")
        (media_dir / icon_filename).write_bytes(icon_data)

    ct_path = work_path / "[Content_Types].xml"
    ct_root = ET.fromstring(ct_path.read_bytes())
    ensure_content_type_default(ct_root, "mp3", "audio/mpeg")
    ensure_content_type_default(ct_root, "png", "image/png")
    ct_path.write_bytes(ET.tostring(ct_root, encoding="UTF-8", xml_declaration=True))

    slide_filename = Path(slide_part_path).name
    rels_dir = work_path / "ppt/slides/_rels"
    rels_dir.mkdir(parents=True, exist_ok=True)
    slide_rels_path = rels_dir / f"{slide_filename}.rels"

    if slide_rels_path.exists():
        rels_root = ET.fromstring(slide_rels_path.read_bytes())
    else:
        rels_root = ET.Element(f"{{{NAMESPACE_RELS}}}Relationships")

    media_target = f"../media/{mp3_filename}"
    icon_target = f"../media/{icon_filename}"

    media_rid = find_relationship_by_type_and_target(
        rels_root, REL_TYPE_MEDIA, media_target
    )
    audio_rid = find_relationship_by_type_and_target(
        rels_root, REL_TYPE_AUDIO, media_target
    )
    image_rid = find_relationship_by_type_and_target(
        rels_root, REL_TYPE_IMAGE, icon_target
    )

    if media_rid is None:
        media_rid = add_relationship(rels_root, REL_TYPE_MEDIA, media_target)

    if audio_rid is None:
        audio_rid = add_relationship(rels_root, REL_TYPE_AUDIO, media_target)

    if image_rid is None:
        image_rid = add_relationship(rels_root, REL_TYPE_IMAGE, icon_target)

    ET.register_namespace("", NAMESPACE_RELS)
    slide_rels_path.write_bytes(
        ET.tostring(rels_root, encoding="UTF-8", xml_declaration=True)
    )

    slide_root = ET.fromstring(slide_path.read_bytes())
    spid = _get_max_shape_id(slide_root) + 1

    sp_tree = _get_or_create_pic_parent(slide_root)
    pic = _create_pic_element(
        spid=spid,
        name=mp3_path.stem,
        media_rid=media_rid,
        audio_rid=audio_rid,
        image_rid=image_rid,
    )
    sp_tree.append(pic)

    cmd_parent = _get_or_create_command_parent(slide_root)
    audio_parent = _get_or_create_audio_parent(slide_root)

    cmd_base_id = _get_max_ctn_id(slide_root) + 1
    delay = _compute_next_delay(cmd_parent)
    cmd_node = _create_command_node(spid, delay, cmd_base_id)
    cmd_parent.insert(0, cmd_node)

    audio_ctn_id = _get_max_ctn_id(slide_root) + 1
    audio_node = _create_audio_node(spid, audio_ctn_id)
    audio_parent.insert(0, audio_node)

    slide_path.write_bytes(
        ET.tostring(slide_root, encoding="UTF-8", xml_declaration=True)
    )
