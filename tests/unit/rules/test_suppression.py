from __future__ import annotations

from datetime import date

from danfse.rules.suppression import (
    MSG_OPERACAO_NAO_SUJEITA_ISSQN,
    MSG_TOMADOR_NAO_IDENTIFICADO,
    format_pis_cofins_retention_label,
    should_show_pis_cofins_retention,
)


def test_should_show_pis_cofins_retention_until_2026() -> None:
    assert should_show_pis_cofins_retention(date(2026, 12, 31)) is True
    assert should_show_pis_cofins_retention(date(2027, 1, 1)) is False


def test_format_pis_cofins_retention_label_suppressed_after_cutoff() -> None:
    assert format_pis_cofins_retention_label("1", competencia=date(2027, 1, 1), label="Retido") == "-"


def test_format_pis_cofins_retention_label_before_cutoff() -> None:
    assert format_pis_cofins_retention_label("1", competencia=date(2026, 1, 1), label="Retido") == "Retido"


def test_party_messages() -> None:
    assert "Tomador" in MSG_TOMADOR_NAO_IDENTIFICADO
    assert "ISSQN" in MSG_OPERACAO_NAO_SUJEITA_ISSQN
