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


PARTY_TITLE_ROW_CM = 0.63
PARTY_MESSAGE_ROW_CM = 0.32


def is_party_message_field(key: str) -> bool:
    return key.endswith(".mensagem_nao_identificado") or key.endswith(".mensagem_igual_tomador")


def party_message_field_y_top_cm(*, block_y_top_cm: float, field_spec: FieldSpec, y_shift: float) -> float:
    if is_party_message_field(field_spec.key):
        return block_y_top_cm + y_shift + PARTY_TITLE_ROW_CM
    return field_spec.y_top_cm + y_shift


def party_message_field_height_cm(field_spec: FieldSpec, value: str) -> float:
    return _party_message_row_height_cm(field_spec, value)


def party_nominal_height_cm() -> float:
    return 1.94


def _party_message_row_height_cm(field_spec: FieldSpec, value: str) -> float:
    if not value.strip() or value.strip() == "-":
        return PARTY_MESSAGE_ROW_CM

    cpl = chars_per_line(field_spec.width_cm)
    lines = wrap_lines(value, cpl)
    needed = len(lines) * LINE_HEIGHT_CM + CELL_PADDING_CM
    return max(PARTY_MESSAGE_ROW_CM, needed)


def party_message_block_height_cm(
    block_key: str,
    field_visible: dict[str, bool],
    field_values: dict[str, str],
) -> float:
    """Altura real do bloco em modo mensagem: título (0,63 cm) + linha(s) de mensagem."""
    height_cm = 0.0
    has_title = False

    for field_spec in FIELD_SPECS:
        if field_spec.block != block_key or not field_visible.get(field_spec.key, False):
            continue
        if field_spec.kind == "block_title":
            has_title = True
        elif field_spec.key.endswith(".mensagem_nao_identificado") or field_spec.key.endswith(
            ".mensagem_igual_tomador",
        ):
            height_cm += _party_message_row_height_cm(field_spec, field_values.get(field_spec.key, ""))

    if has_title:
        height_cm += PARTY_TITLE_ROW_CM

    return max(PARTY_TITLE_ROW_CM + PARTY_MESSAGE_ROW_CM, height_cm)


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
            actual_height = party_message_block_height_cm(
                block_key,
                field_visible,
                field_values,
            )
            saved = party_nominal_height_cm() - actual_height
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
