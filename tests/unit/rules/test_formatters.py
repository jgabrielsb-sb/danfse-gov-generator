from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

import pytest

from danfse.rules.formatters import (
    EMPTY_DISPLAY,
    display_or_dash,
    format_access_key,
    format_by_xsd_type,
    format_cep,
    format_cnpj,
    format_cpf,
    format_date,
    format_datetime,
    format_money,
    format_percent,
    truncate_with_ellipsis,
)


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (None, EMPTY_DISPLAY),
        ("", EMPTY_DISPLAY),
        ("  ", EMPTY_DISPLAY),
        ("texto", "texto"),
    ],
)
def test_display_or_dash(value: str | None, expected: str) -> None:
    assert display_or_dash(value) == expected


def test_truncate_with_ellipsis_uses_ascii_dots() -> None:
    assert truncate_with_ellipsis("abcdefghij", 7) == "abcd..."
    assert "…" not in truncate_with_ellipsis("abcdefghij", 7)


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("29154166000144", "29.154.166/0001-44"),
        (None, EMPTY_DISPLAY),
    ],
)
def test_format_cnpj(value: str | None, expected: str) -> None:
    assert format_cnpj(value) == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("12345678901", "123.456.789-01"),
        (None, EMPTY_DISPLAY),
    ],
)
def test_format_cpf(value: str | None, expected: str) -> None:
    assert format_cpf(value) == expected


def test_format_cep() -> None:
    assert format_cep("57300100") == "57.300-100"


def test_format_access_key_strips_nfs_prefix() -> None:
    assert format_access_key("NFS12345678901234567890123456789012345678901234567890") == (
        "12345678901234567890123456789012345678901234567890"
    )


def test_format_date_and_datetime() -> None:
    assert format_date(date(2026, 2, 23)) == "23/02/2026"
    assert format_datetime(datetime(2026, 2, 23, 16, 51, 42)) == "23/02/2026 16:51:42"


def test_format_money_brazilian() -> None:
    assert format_money(Decimal("1000.00")) == "1.000,00"
    assert format_money(Decimal("20.10")) == "20,10"


def test_format_percent() -> None:
    assert format_percent(Decimal("2.01")) == "2,01%"


@pytest.mark.parametrize(
    ("xsd_type", "value", "expected"),
    [
        ("TSCNPJ", "29154166000144", "29.154.166/0001-44"),
        ("TSCEP", "57300100", "57.300-100"),
        ("TSDec15V2", Decimal("1000.00"), "1.000,00"),
        ("TSDec2V2", Decimal("2.01"), "2,01%"),
        ("TSData", date(2026, 2, 23), "23/02/2026"),
        ("TSDateTimeUTC", datetime(2026, 2, 23, 16, 51, 42), "23/02/2026 16:51:42"),
    ],
)
def test_format_by_xsd_type(xsd_type: str, value, expected: str) -> None:
    assert format_by_xsd_type(xsd_type, value) == expected
