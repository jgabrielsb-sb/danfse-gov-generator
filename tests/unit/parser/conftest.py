from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture
def gov_fixtures_dir() -> Path:
    return Path(__file__).resolve().parents[2] / "fixtures" / "gov"
