from __future__ import annotations

from pathlib import Path

from gerador_danfse.exceptions import XmlParseError
from gerador_danfse.layout.layout_engine import build_layout_plan
from gerador_danfse.parser.mapper import map_to_domain
from gerador_danfse.parser.xml_parser import parse_xml
from gerador_danfse.renderers.pdf_renderer import PdfRenderOptions, render_pdf
from gerador_danfse.rules.formatter.danfse import DanfseFormatter


def generate_danfse_pdf(xml_input: str | Path, pdf_output: str | Path, *, watermark: str | None = None) -> None:
    """
    Public API: generate a DANFSe PDF from a NFS-e XML file.
    """

    doc = parse_xml(xml_input)
    try:
        data = map_to_domain(doc)
    except Exception as exc:
        raise XmlParseError("Could not map XML into internal models.") from exc

    formatted = DanfseFormatter().format(data)
    plan = build_layout_plan(formatted)
    render_pdf(
        plan,
        pdf_output,
        options=PdfRenderOptions(watermark_text=watermark),
    )

if __name__ == "__main__":
    xml_path = Path("nota_danfse_exemplo_sanitizada.xml")
    output_path = Path("nota_danfse_exemplo_sanitizada.pdf")
    generate_danfse_pdf(xml_path, output_path)

