from __future__ import annotations

from danfse.rules.field_specs import ENUM_OVERRIDES
from danfse.rules.formatters import display_or_dash, truncate_with_ellipsis
from danfse.rules.xsd_catalog import XsdSchemaCatalog, get_default_catalog


def describe_enum(
    catalog: XsdSchemaCatalog,
    xsd_type: str,
    code: str | None,
    *,
    max_length: int | None = None,
) -> str:
    if code is None or str(code).strip() == "":
        return display_or_dash(None)

    label = catalog.describe_enum(xsd_type, str(code))
    if not label:
        overrides = ENUM_OVERRIDES.get(xsd_type, {})
        label = overrides.get(str(code))

    if not label:
        return display_or_dash(str(code))

    if max_length is not None:
        return truncate_with_ellipsis(label, max_length)
    return label


def describe_field(
    xsd_type: str,
    code: str | None,
    *,
    catalog: XsdSchemaCatalog | None = None,
    max_length: int | None = None,
) -> str:
    catalog = catalog or get_default_catalog()
    return describe_enum(catalog, xsd_type, code, max_length=max_length)


def normalize_description(text: str | None) -> str:
    if not text:
        return ""
    return " ".join(text.split())
