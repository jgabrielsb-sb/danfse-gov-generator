from __future__ import annotations

from pathlib import Path

from gerador_danfse.api import generate_danfse_pdf


def test_generate_danfse_pdf_writes_file(tmp_path: Path) -> None:
    xml = Path("tests/fixtures/gov/nota_gov_1_29154166000144.xml")
    pdf = tmp_path / "out.pdf"
    generate_danfse_pdf(xml, pdf)

    assert pdf.exists()
    assert pdf.stat().st_size > 1000
