from __future__ import annotations

from pathlib import Path

from danfse import generate_danfse_pdf


def test_generate_pdf_creates_file(tmp_path: Path) -> None:
    xml = tmp_path / "invoice.xml"
    pdf = tmp_path / "danfse.pdf"

    xml.write_text(
        """<?xml version="1.0" encoding="utf-8"?>
<Nfse>
  <Numero>123</Numero>
  <CodigoVerificacao>ABC123</CodigoVerificacao>
  <DataEmissao>2026-06-16T12:34:56</DataEmissao>
  <Competencia>2026-06-01</Competencia>
  <RazaoSocialPrestador>ACME Serviços LTDA</RazaoSocialPrestador>
  <CnpjPrestador>12345678000199</CnpjPrestador>
  <InscricaoMunicipalPrestador>12345</InscricaoMunicipalPrestador>
  <RazaoSocialTomador>Cliente Exemplo</RazaoSocialTomador>
  <CpfTomador>12345678901</CpfTomador>
  <Discriminacao>Serviços prestados conforme contrato.</Discriminacao>
  <ItemListaServico>0107</ItemListaServico>
  <ValorServicos>100.00</ValorServicos>
  <ValorIss>5.00</ValorIss>
  <ValorLiquidoNfse>95.00</ValorLiquidoNfse>
</Nfse>
""",
        encoding="utf-8",
    )

    generate_danfse_pdf(xml, pdf)
    assert pdf.exists()
    assert pdf.stat().st_size > 500

