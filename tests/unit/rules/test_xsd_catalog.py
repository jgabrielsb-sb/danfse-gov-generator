from __future__ import annotations

from gerador_danfse.rules.catalog.xsd import XsdSchemaCatalog


def test_catalog_loads_default(xsd_catalog: XsdSchemaCatalog) -> None:
    assert xsd_catalog.enum_values("TSTribISSQN")
    assert xsd_catalog.restrictions("TSCNPJ").pattern == "[0-9]{14}"


def test_describe_enum_trib_issqn(xsd_catalog: XsdSchemaCatalog) -> None:
    assert xsd_catalog.describe_enum("TSTribISSQN", "1") == "Operação tributável"


def test_describe_enum_emitente(xsd_catalog: XsdSchemaCatalog) -> None:
    assert xsd_catalog.describe_enum("TSEmitenteDPS", "1") == "Prestador"


def test_field_type_lookup(xsd_catalog: XsdSchemaCatalog) -> None:
    assert xsd_catalog.field_type("tpEmit") == "TSEmitenteDPS"


def test_unknown_enum_returns_none(xsd_catalog: XsdSchemaCatalog) -> None:
    assert xsd_catalog.describe_enum("TSTribISSQN", "999") is None
