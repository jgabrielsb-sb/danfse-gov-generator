from __future__ import annotations

from pathlib import Path

import pytest

from danfse.rules.catalog.xsd import XsdSchemaCatalog


@pytest.fixture
def xsd_catalog() -> XsdSchemaCatalog:
    return XsdSchemaCatalog.load_default()


@pytest.fixture
def gov_fixtures_dir() -> Path:
    return Path(__file__).resolve().parents[2] / "fixtures" / "gov"
