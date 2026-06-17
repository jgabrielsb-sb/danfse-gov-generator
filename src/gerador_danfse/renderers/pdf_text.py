from __future__ import annotations

from reportlab.pdfbase.pdfmetrics import stringWidth


def fit_text(text: str, font_name: str, font_size: float, max_width: float) -> str:
    if not text or max_width <= 0:
        return text
    if stringWidth(text, font_name, font_size) <= max_width:
        return text

    ellipsis = "..."
    trimmed = text
    while trimmed and stringWidth(trimmed + ellipsis, font_name, font_size) > max_width:
        trimmed = trimmed[:-1].rstrip()
    return (trimmed + ellipsis) if trimmed else ellipsis


def wrap_text(
    text: str,
    font_name: str,
    font_size: float,
    max_width: float,
    *,
    max_lines: int | None = None,
) -> list[str]:
    if not text:
        return [""]

    paragraphs = text.splitlines() or [""]
    lines: list[str] = []

    for paragraph in paragraphs:
        words = paragraph.split()
        if not words:
            lines.append("")
            continue

        current: list[str] = []
        for word in words:
            candidate = " ".join(current + [word]).strip()
            if current and stringWidth(candidate, font_name, font_size) > max_width:
                lines.append(" ".join(current))
                current = [word]
            else:
                current.append(word)

            if max_lines is not None and len(lines) >= max_lines:
                return lines[:max_lines]

        if current:
            lines.append(" ".join(current))

    if max_lines is not None:
        return lines[:max_lines]
    return lines or [""]
