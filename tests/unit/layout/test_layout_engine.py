from __future__ import annotations

from pathlib import Path

import pytest

from danfse.layout.field_values import resolve_field_value
from danfse.layout.layout_engine import build_layout_plan
from danfse.parser.mapper import map_to_domain
from danfse.parser.xml_parser import parse_xml
from danfse.rules.formatter.danfse import DanfseFormatter
from tests.unit.rules.expected_formatted import EXPECTED_FORMATTED_BY_FIXTURE


@pytest.fixture
def formatted_gov_1() -> object:
    return DanfseFormatter().format(
        map_to_domain(parse_xml(Path("tests/fixtures/gov/nota_gov_1_29154166000144.xml"))),
    )


def test_build_layout_plan_contains_identificacao_fields(formatted_gov_1) -> None:
    plan = build_layout_plan(formatted_gov_1)
    keys = {element.key for block in plan.blocks for element in block.elements}

    assert "identificacao.numero_nfse" in keys
    assert "identificacao.emitente_nfse" in keys
    assert "prestador.documento" in keys


def test_destinatario_message_mode_hides_data_fields(formatted_gov_1) -> None:
    plan = build_layout_plan(formatted_gov_1)
    dest_elements = next(block.elements for block in plan.blocks if block.key == "destinatario")
    keys = {element.key for element in dest_elements}

    assert "destinatario.mensagem_nao_identificado" in keys
    assert "destinatario.documento" not in keys
    message = next(element for element in dest_elements if element.key == "destinatario.mensagem_nao_identificado")
    assert message.value.startswith("Destinatário")


def test_optional_tributacao_federal_block_hidden(formatted_gov_1) -> None:
    plan = build_layout_plan(formatted_gov_1)
    federal = next(block for block in plan.blocks if block.key == "tributacao_federal")

    assert federal.visible is False
    assert federal.elements == ()


def test_field_positions_use_pdf_coordinates(formatted_gov_1) -> None:
    plan = build_layout_plan(formatted_gov_1)
    chave = next(
        element
        for block in plan.blocks
        for element in block.elements
        if element.key == "identificacao.chave_acesso"
    )

    assert chave.rect.x_pt > 0
    assert chave.rect.y_pt > 0
    assert chave.rect.width_pt > 0
    assert chave.rect.height_pt > 0


@pytest.mark.parametrize("fixture_path", list(EXPECTED_FORMATTED_BY_FIXTURE.keys()))
def test_build_layout_plan_for_all_gov_fixtures(fixture_path: str) -> None:
    xml_path = Path(fixture_path)
    formatted = DanfseFormatter().format(map_to_domain(parse_xml(xml_path)))
    plan = build_layout_plan(formatted)

    assert plan.formatted == formatted
    assert plan.blocks
    assert any(block.visible for block in plan.blocks)


def test_resolve_field_value_maps_servico_fields() -> None:
    formatted = EXPECTED_FORMATTED_BY_FIXTURE["tests/fixtures/gov/nota_gov_1_29154166000144.xml"]

    assert resolve_field_value("servico.codigo_nbs", formatted) == "114021100"
    assert "170101" in resolve_field_value("servico.codigo_tributacao_nacional_municipal", formatted)
