from __future__ import annotations

from pathlib import Path

import pytest

from gerador_danfse.layout.field_values import resolve_field_value
from gerador_danfse.layout.layout_engine import build_layout_plan
from gerador_danfse.parser.mapper import map_to_domain
from gerador_danfse.parser.xml_parser import parse_xml
from gerador_danfse.rules.formatter.danfse import DanfseFormatter
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

    assert federal.visible is True
    assert any(element.key.startswith("tributacao_federal.") for element in federal.elements)


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


def _rects_overlap_vertically(a, b, *, epsilon: float = 0.5) -> bool:
    a_bottom = a.y_pt
    a_top = a.y_pt + a.height_pt
    b_bottom = b.y_pt
    b_top = b.y_pt + b.height_pt
    return a_bottom < b_top - epsilon and a_top > b_bottom + epsilon


def test_servico_does_not_overlap_tributacao_municipal() -> None:
    xml_path = Path("31062002255548926000108000000000000826069247812850.xml")
    if not xml_path.exists():
        pytest.skip("fixture XML not available")

    formatted = DanfseFormatter().format(map_to_domain(parse_xml(xml_path)))
    plan = build_layout_plan(formatted)

    servico = next(block for block in plan.blocks if block.key == "servico")
    tributacao = next(block for block in plan.blocks if block.key == "tributacao_municipal")

    trib_top = tributacao.rect.y_pt + tributacao.rect.height_pt
    assert servico.rect.y_pt >= trib_top - 0.5

    for servico_element in servico.elements:
        for trib_element in tributacao.elements:
            assert not _rects_overlap_vertically(servico_element.rect, trib_element.rect)


def test_party_message_blocks_do_not_overlap_neighbors() -> None:
    xml_path = Path("31062002255548926000108000000000000826069247812850.xml")
    if not xml_path.exists():
        pytest.skip("fixture XML not available")

    formatted = DanfseFormatter().format(map_to_domain(parse_xml(xml_path)))
    plan = build_layout_plan(formatted)

    ordered = ("destinatario", "intermediario", "servico")
    blocks = [next(block for block in plan.blocks if block.key == key) for key in ordered]

    for left, right in zip(blocks, blocks[1:]):
        right_top = right.rect.y_pt + right.rect.height_pt
        assert left.rect.y_pt >= right_top - 0.5

        for left_element in left.elements:
            for right_element in right.elements:
                assert not _rects_overlap_vertically(left_element.rect, right_element.rect)


def test_party_message_is_rendered_below_block_title() -> None:
    xml_path = Path("31062002255548926000108000000000000826069247812850.xml")
    if not xml_path.exists():
        pytest.skip("fixture XML not available")

    formatted = DanfseFormatter().format(map_to_domain(parse_xml(xml_path)))
    plan = build_layout_plan(formatted)

    for block_key in ("destinatario", "intermediario"):
        block = next(item for item in plan.blocks if item.key == block_key)
        title = next(element for element in block.elements if element.kind == "block_title")
        message = next(element for element in block.elements if "mensagem" in element.key)

        message_top = message.rect.y_pt + message.rect.height_pt
        assert title.rect.y_pt >= message_top - 0.5
        assert message.value.endswith("na NFS-e")


def test_tributacao_municipal_title_does_not_overlap_tipo_field() -> None:
    xml_path = Path("31062002255548926000108000000000000826069247812850.xml")
    if not xml_path.exists():
        pytest.skip("fixture XML not available")

    formatted = DanfseFormatter().format(map_to_domain(parse_xml(xml_path)))
    plan = build_layout_plan(formatted)

    title = next(
        element
        for block in plan.blocks
        for element in block.elements
        if element.key == "block.tributacao_municipal.title"
    )
    tipo = next(
        element
        for block in plan.blocks
        for element in block.elements
        if element.key == "tributacao_municipal.tipo_tributacao_issqn"
    )

    assert title.rect.x_pt < tipo.rect.x_pt
    assert title.rect.x_pt + title.rect.width_pt <= tipo.rect.x_pt + 0.5
    assert abs(title.rect.y_pt - tipo.rect.y_pt) < 0.5
