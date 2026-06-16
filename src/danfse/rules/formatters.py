from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Optional


def format_document(doc: Optional[str]) -> str:
    if not doc:
        return ""
    digits = "".join(ch for ch in doc if ch.isdigit())
    if len(digits) == 11:
        return f"{digits[0:3]}.{digits[3:6]}.{digits[6:9]}-{digits[9:11]}"
    if len(digits) == 14:
        return f"{digits[0:2]}.{digits[2:5]}.{digits[5:8]}/{digits[8:12]}-{digits[12:14]}"
    return doc


def format_money(value: Optional[Decimal]) -> str:
    if value is None:
        return ""
    # Brazilian-style display: 1.234,56
    q = value.quantize(Decimal("0.01"))
    s = f"{q:,.2f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def format_datetime(value: Optional[datetime]) -> str:
    if not value:
        return ""
    return value.strftime("%d/%m/%Y %H:%M:%S")


def format_date(value: Optional[date]) -> str:
    if not value:
        return ""
    return value.strftime("%d/%m/%Y")


def truncate(text: Optional[str], max_len: int) -> str:
    if not text:
        return ""
    if len(text) <= max_len:
        return text
    return text[: max(0, max_len - 1)].rstrip() + "…"

