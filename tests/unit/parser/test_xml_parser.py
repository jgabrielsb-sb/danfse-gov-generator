from __future__ import annotations

from pathlib import Path

import pytest

from gerador_danfse.domain.models import DanfseData
from gerador_danfse.parser.mapper import map_to_domain
from gerador_danfse.parser.xml_parser import parse_xml
from tests.unit.parser.expected_domain import EXPECTED_BY_FIXTURE

PARSE_GOV_FIXTURE_CASES = [
    pytest.param(Path(fixture_path).name, expected, id=Path(fixture_path).stem)
    for fixture_path, expected in EXPECTED_BY_FIXTURE.items()
]


def test_expected_registry_covers_all_gov_fixtures(gov_fixtures_dir: Path) -> None:
    fixture_names = {path.name for path in gov_fixtures_dir.glob("*.xml")}
    registry_names = {Path(path).name for path in EXPECTED_BY_FIXTURE}

    assert registry_names == fixture_names


@pytest.mark.parametrize(("xml_name", "expected"), PARSE_GOV_FIXTURE_CASES)
def test_parse_gov_fixture_maps_to_expected_domain(
    gov_fixtures_dir: Path,
    xml_name: str,
    expected: DanfseData,
) -> None:
    actual = map_to_domain(parse_xml(gov_fixtures_dir / xml_name))

    assert actual.model_dump(mode="json", exclude_none=True) == expected.model_dump(
        mode="json",
        exclude_none=True,
    )
