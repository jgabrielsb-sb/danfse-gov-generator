from __future__ import annotations

import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from danfse.exceptions import XmlParseError


@dataclass(frozen=True)
class XmlDocument:
    root: ET.Element


def parse_xml(xml_path: str | Path) -> XmlDocument:
    try:
        path = Path(xml_path)
        data = path.read_bytes()
    except OSError as exc:
        raise XmlParseError(f"Could not read XML file: {xml_path}") from exc

    try:
        root = ET.fromstring(data)
    except ET.ParseError as exc:
        raise XmlParseError("Invalid XML content.") from exc

    return XmlDocument(root=root)


def _find_first_text(root: ET.Element, candidates: list[str]) -> Optional[str]:
    """
    Best-effort lookup: finds first element whose *local name* matches one of candidates.
    This makes the minimal implementation tolerant to namespaces and vendor variations.
    """

    wanted = {c.lower() for c in candidates}
    for el in root.iter():
        if "}" in el.tag:
            local = el.tag.rsplit("}", 1)[1]
        else:
            local = el.tag
        if local.lower() in wanted:
            text = (el.text or "").strip()
            if text:
                return text
    return None

