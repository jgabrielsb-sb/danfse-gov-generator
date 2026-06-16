from __future__ import annotations

from typing import Optional


def normalize_description(text: Optional[str]) -> str:
    if not text:
        return ""
    # Minimal normalization: collapse whitespace.
    return " ".join(text.split())

