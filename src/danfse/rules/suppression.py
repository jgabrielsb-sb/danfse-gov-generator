from __future__ import annotations

from typing import Optional


def display_or_blank(value: Optional[str]) -> str:
    return (value or "").strip()

