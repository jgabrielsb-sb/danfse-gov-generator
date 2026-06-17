from __future__ import annotations

from pathlib import Path

from gerador_danfse.layout.layout_engine import build_layout_plan
from gerador_danfse.parser.mapper import map_to_domain
from gerador_danfse.parser.xml_parser import parse_xml
from gerador_danfse.renderers.assets import default_logo_path
from gerador_danfse.rules.formatter.danfse import DanfseFormatter


def test_build_layout_plan_includes_logo_element() -> None:
    formatted = DanfseFormatter().format(
        map_to_domain(parse_xml(Path("tests/fixtures/gov/nota_gov_1_29154166000144.xml"))),
    )
    plan = build_layout_plan(formatted)
    keys = {element.key for block in plan.blocks for element in block.elements}

    assert "assets.logo_nfse" in keys


def test_default_logo_path_exists() -> None:
    path = default_logo_path()
    assert path is not None
    assert path.exists()
