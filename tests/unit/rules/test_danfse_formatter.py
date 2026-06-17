from __future__ import annotations

from pathlib import Path

import pytest

from gerador_danfse.parser.mapper import map_to_domain
from gerador_danfse.parser.xml_parser import parse_xml
from gerador_danfse.rules.formatter.danfse import DanfseFormatter
from gerador_danfse.rules.models.formatted import FormattedDanfse
from tests.unit.rules.expected_formatted import EXPECTED_FORMATTED_BY_FIXTURE

FORMAT_GOV_FIXTURE_CASES = [
    pytest.param(Path(fixture_path).name, expected, id=Path(fixture_path).stem)
    for fixture_path, expected in EXPECTED_FORMATTED_BY_FIXTURE.items()
]


def test_expected_formatted_registry_covers_all_gov_fixtures(gov_fixtures_dir: Path) -> None:
    fixture_names = {path.name for path in gov_fixtures_dir.glob("*.xml")}
    registry_names = {Path(path).name for path in EXPECTED_FORMATTED_BY_FIXTURE}

    assert registry_names == fixture_names


@pytest.mark.parametrize(("xml_name", "expected"), FORMAT_GOV_FIXTURE_CASES)
def test_format_gov_fixture_matches_expected(
    gov_fixtures_dir: Path,
    xml_name: str,
    expected: FormattedDanfse,
) -> None:
    data = map_to_domain(parse_xml(gov_fixtures_dir / xml_name))
    actual = DanfseFormatter().format(data)

    assert actual.model_dump(mode="json") == expected.model_dump(mode="json")


def test_op_simp_nac_truncates_long_enum_to_37_chars() -> None:
    from gerador_danfse.domain.models import (
        CabecalhoDanfse,
        DanfseData,
        DocumentoPessoaDanfse,
        IdentificacaoNfseDanfse,
        PrestadorDanfse,
        RegimeTributarioPrestadorDanfse,
        ServicoPrestadoDanfse,
    )

    data = DanfseData(
        cabecalho=CabecalhoDanfse(tipo_ambiente="1"),
        identificacao=IdentificacaoNfseDanfse(numero_nfse="1"),
        prestador=PrestadorDanfse(
            documento=DocumentoPessoaDanfse(cnpj="29154166000144"),
            regime_tributario=RegimeTributarioPrestadorDanfse(
                simples_nacional_competencia="3",
            ),
        ),
        servico=ServicoPrestadoDanfse(),
    )

    formatted = DanfseFormatter().format(data)
    assert len(formatted.prestador.simples_nacional_competencia) == 37
    assert formatted.prestador.simples_nacional_competencia.endswith("...")
