from __future__ import annotations

from pathlib import Path

from danfse.exceptions import XmlParseError
from danfse.layout.layout_engine import build_layout_plan
from danfse.parser.mapper import map_to_domain
from danfse.parser.xml_parser import parse_xml
from danfse.renderers.pdf_renderer import PdfRenderOptions, render_pdf


def generate_danfse_pdf(xml_input: str | Path, pdf_output: str | Path, *, watermark: str | None = None) -> None:
    """
    Public API: generate a DANFSe PDF from a NFS-e XML file.

    This initial version performs a best-effort extraction of common fields and renders a
    simple A4 single-page PDF. It is designed to evolve towards full official compliance.
    """

    doc = parse_xml(xml_input)
    try:
        data = map_to_domain(doc)
    except Exception as exc:
        raise XmlParseError("Could not map XML into internal models.") from exc

    plan = build_layout_plan(data)
    render_pdf(plan, pdf_output, options=PdfRenderOptions(watermark_text=watermark))

