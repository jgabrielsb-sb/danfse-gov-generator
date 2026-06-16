from __future__ import annotations

import re

from danfse.layout.specs import BLOCK_SPECS, FIELD_SPECS, FieldSpec

# Alturas aproximadas alinhadas ao renderer (pt → cm).
LINE_HEIGHT_CM = 0.32
LABEL_ROW_CM = 0.30
CELL_PADDING_CM = 0.10


def wrap_lines(text: str, chars_per_line: int) -> list[str]:
    if not text:
        return [""]

    lines: list[str] = []
    for paragraph in re.split(r"\r?\n", text):
        if not paragraph.strip():
            lines.append("")
            continue
        words = paragraph.split()
        current: list[str] = []
        for word in words:
            candidate = " ".join(current + [word]).strip()
            if current and len(candidate) > chars_per_line:
                lines.append(" ".join(current))
                current = [word]
            else:
                current.append(word)
        if current:
            lines.append(" ".join(current))
    return lines or [""]


def chars_per_line(width_cm: float, *, font_size_pt: float = 6.5) -> int:
    # Heurística: Courier/Helvetica ~0.5× font_size pt por caractere médio.
    width_pt = width_cm * 28.35
    return max(8, int(width_pt / (font_size_pt * 0.52)))


def estimate_field_height_cm(field_spec: FieldSpec, value: str) -> float:
    base = field_spec.height_cm
    if not field_spec.multiline or not value.strip() or value.strip() == "-":
        return base

    cpl = chars_per_line(field_spec.width_cm)
    lines = wrap_lines(value, cpl)
    content_height = len(lines) * LINE_HEIGHT_CM
    label_height = LABEL_ROW_CM if field_spec.label else 0.0
    needed = label_height + content_height + CELL_PADDING_CM

    if field_spec.dynamic_height:
        return max(base, needed)
    return max(base, min(needed, base))  # multiline fixo: não expande além do spec


def estimate_block_height_cm(
    block_key: str,
    fields: list[tuple[FieldSpec, str]],
    *,
    nominal_height_cm: float,
    dynamic_height: bool,
) -> float:
    if not fields:
        return nominal_height_cm

    block_fields = [(spec, value) for spec, value in fields if spec.block == block_key]
    if not block_fields:
        return nominal_height_cm

    y_tops = [spec.y_top_cm for spec, _ in block_fields]
    block_y_top = min(y_tops)
    bottoms: list[float] = []

    for spec, value in block_fields:
        height = estimate_field_height_cm(spec, value)
        bottoms.append(spec.y_top_cm + height)

    content_bottom = max(bottoms)
    nominal_bottom = block_y_top + nominal_height_cm

    if dynamic_height:
        return max(nominal_height_cm, content_bottom - block_y_top)

    return nominal_height_cm


def party_message_height_cm() -> float:
    return 0.32


def party_nominal_height_cm() -> float:
    return 1.94


def compute_block_y_shifts(
    visible_blocks: dict[str, bool],
    field_visible: dict[str, bool],
    field_values: dict[str, str],
    party_message_blocks: set[str],
) -> dict[str, float]:
    """
    Calcula deslocamento vertical acumulado (cm) por bloco.
    Blocos posteriores são empurrados quando blocos dinâmicos crescem ou encolhem.
    """
    shifts: dict[str, float] = {}
    cumulative_shift = 0.0

    fields_by_block: dict[str, list[tuple[FieldSpec, str]]] = {}
    for field_spec in FIELD_SPECS:
        if not field_visible.get(field_spec.key, True):
            continue
        value = field_values.get(field_spec.key, "")
        fields_by_block.setdefault(field_spec.block, []).append((field_spec, value))

    for block_spec in BLOCK_SPECS:
        shifts[block_spec.key] = cumulative_shift

        if not visible_blocks.get(block_spec.key, True):
            continue

        block_key = block_spec.key
        block_fields = fields_by_block.get(block_key, [])

        if block_key in party_message_blocks:
            saved = party_nominal_height_cm() - party_message_height_cm()
            cumulative_shift -= saved
            continue

        if not block_spec.dynamic_height:
            continue

        visible_fields = [
            (spec, value)
            for spec, value in block_fields
            if field_visible.get(spec.key, True)
        ]
        actual_height = estimate_block_height_cm(
            block_key,
            visible_fields,
            nominal_height_cm=block_spec.height_cm,
            dynamic_height=True,
        )
        growth = actual_height - block_spec.height_cm
        if growth > 0:
            cumulative_shift += growth

    return shifts


def field_height_cm(field_spec: FieldSpec, value: str) -> float:
    if field_spec.dynamic_height and field_spec.multiline:
        return estimate_field_height_cm(field_spec, value)
    return field_spec.height_cm
