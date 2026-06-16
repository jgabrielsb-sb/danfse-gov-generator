from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from typing import Optional

from danfse.domain.models import DanfseData, Party, ServiceValues
from danfse.parser.xml_parser import XmlDocument, _find_first_text


def _parse_decimal(value: Optional[str]) -> Optional[Decimal]:
    if not value:
        return None
    try:
        normalized = value.replace(".", "").replace(",", ".") if value.count(",") == 1 else value
        return Decimal(normalized)
    except (InvalidOperation, ValueError):
        return None


def _parse_datetime(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    # Common: 2026-06-16T12:34:56 or 2026-06-16
    for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            dt = datetime.strptime(value, fmt)
            return dt
        except ValueError:
            pass
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def _parse_date(value: Optional[str]) -> Optional[date]:
    dt = _parse_datetime(value)
    return dt.date() if dt else None


def map_to_domain(doc: XmlDocument) -> DanfseData:
    r = doc.root

    nfse_number = _find_first_text(r, ["Numero", "NumeroNfse", "NumeroNFS-e"])
    verification_code = _find_first_text(r, ["CodigoVerificacao", "CodigoVerificacaoNfse"])
    issue_dt = _parse_datetime(_find_first_text(r, ["DataEmissao", "DataEmissaoNfse", "DataHoraEmissao"]))
    competence = _parse_date(_find_first_text(r, ["Competencia", "DataCompetencia"]))

    provider = Party(
        name=_find_first_text(r, ["RazaoSocialPrestador", "RazaoSocial", "NomePrestador"]),
        document=_find_first_text(r, ["CnpjPrestador", "Cnpj", "CpfCnpjPrestador", "CpfPrestador"]),
        municipal_registration=_find_first_text(r, ["InscricaoMunicipalPrestador", "InscricaoMunicipal"]),
        address=_find_first_text(r, ["EnderecoPrestador", "Endereco"]),
        city=_find_first_text(r, ["MunicipioPrestador", "CidadePrestador", "Municipio"]),
        state=_find_first_text(r, ["UfPrestador", "UF"]),
    )

    taker = Party(
        name=_find_first_text(r, ["RazaoSocialTomador", "NomeTomador", "RazaoSocialTomadorServico"]),
        document=_find_first_text(r, ["CnpjTomador", "CpfTomador", "CpfCnpjTomador", "CpfCnpjTomadorServico"]),
        municipal_registration=_find_first_text(r, ["InscricaoMunicipalTomador", "InscricaoMunicipalTomador"]),
        address=_find_first_text(r, ["EnderecoTomador", "EnderecoTomadorServico"]),
        city=_find_first_text(r, ["MunicipioTomador", "CidadeTomador"]),
        state=_find_first_text(r, ["UfTomador", "UfTomadorServico"]),
    )

    service_description = _find_first_text(r, ["Discriminacao", "Descricao", "DescricaoServico"])
    service_code = _find_first_text(r, ["ItemListaServico", "CodigoServico", "Codigo"])
    cnae = _find_first_text(r, ["CodigoCnae", "Cnae"])
    city_service_code = _find_first_text(r, ["CodigoMunicipio", "CodigoMunicipioPrestacao", "CodigoMunicipioIncidencia"])

    values = ServiceValues(
        total_services=_parse_decimal(_find_first_text(r, ["ValorServicos", "ValorServico", "ValorServ"])),
        iss=_parse_decimal(_find_first_text(r, ["ValorIss", "ValorISS", "ValorIssqn"])),
        deductions=_parse_decimal(_find_first_text(r, ["ValorDeducoes", "Deducoes", "ValorDeducao"])),
        net_value=_parse_decimal(_find_first_text(r, ["ValorLiquidoNfse", "ValorLiquido", "ValorNfse"])),
    )

    municipality = _find_first_text(r, ["NomeMunicipio", "MunicipioPrestacao", "Municipio"])
    qr_code_url = _find_first_text(r, ["QrCode", "QRCode", "UrlQrCode", "LinkQrCode"])

    return DanfseData(
        nfse_number=nfse_number,
        verification_code=verification_code,
        issue_datetime=issue_dt,
        competence_date=competence,
        provider=provider,
        taker=taker,
        service_description=service_description,
        service_code=service_code,
        cnae=cnae,
        city_service_code=city_service_code,
        values=values,
        municipality=municipality,
        qr_code_url=qr_code_url,
    )

