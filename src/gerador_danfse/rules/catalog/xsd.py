from __future__ import annotations

import json
from dataclasses import dataclass
from functools import lru_cache
from importlib import resources
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class XsdRestrictions:
    base: str | None = None
    pattern: str | None = None
    max_length: int | None = None
    min_length: int | None = None


class XsdSchemaCatalog:
    """Catálogo de tipos, enums e campos extraídos do XSD NFS-e nacional."""

    def __init__(self, data: dict[str, Any]) -> None:
        self._simple_types: dict[str, dict[str, Any]] = {
            item["name"]: item for item in data.get("simple_types", [])
        }
        self._enum_types: dict[str, dict[str, str]] = {
            item["type"]: item.get("values", {}) for item in data.get("enum_descriptions", [])
        }
        self._field_types: dict[tuple[str, str | None], str] = {}
        for row in data.get("complex_field_descriptions", []):
            key = (row["element"], row.get("complex_type"))
            self._field_types[key] = row["type"]
            self._field_types.setdefault((row["element"], None), row["type"])

    @classmethod
    def from_default(cls) -> XsdSchemaCatalog:
        return cls.load_default()

    @classmethod
    def load_default(cls) -> XsdSchemaCatalog:
        path = Path(__file__).resolve().parent / "data" / "xsd_descriptions.json"
        if path.exists():
            return cls.from_path(path)
        with resources.files("gerador_danfse.rules.catalog.data").joinpath("xsd_descriptions.json").open(
            encoding="utf-8",
        ) as fh:
            return cls(json.load(fh))

    @classmethod
    def from_path(cls, path: str | Path) -> XsdSchemaCatalog:
        with Path(path).open(encoding="utf-8") as fh:
            return cls(json.load(fh))

    def restrictions(self, xsd_type: str) -> XsdRestrictions:
        item = self._simple_types.get(xsd_type, {})
        raw = item.get("restrictions", {})
        max_len = raw.get("maxLength")
        min_len = raw.get("minLength")
        return XsdRestrictions(
            base=raw.get("base"),
            pattern=raw.get("pattern"),
            max_length=int(max_len) if max_len is not None else None,
            min_length=int(min_len) if min_len is not None else None,
        )

    def enum_values(self, xsd_type: str) -> dict[str, str]:
        return dict(self._enum_types.get(xsd_type, {}))

    def describe_enum(self, xsd_type: str, code: str | None) -> str | None:
        if code is None or str(code).strip() == "":
            return None
        values = self.enum_values(xsd_type)
        label = values.get(str(code))
        if label:
            return label
        return None

    def field_type(self, element: str, *, complex_type: str | None = None) -> str | None:
        return self._field_types.get((element, complex_type)) or self._field_types.get(
            (element, None),
        )

    def documentation(self, xsd_type: str) -> str | None:
        item = self._simple_types.get(xsd_type)
        if not item:
            return None
        doc = item.get("documentation")
        return doc if doc else None


@lru_cache(maxsize=1)
def get_default_catalog() -> XsdSchemaCatalog:
    return XsdSchemaCatalog.load_default()
