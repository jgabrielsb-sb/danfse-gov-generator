from __future__ import annotations

from danfse.layout.coordinates import cm_to_pt, top_left_cm_to_pdf_rect
from danfse.layout.field_values import resolve_field_value
from danfse.layout.models import DanfseLayoutPlan, LayoutBlock, LayoutElement, PositionedRect
from danfse.layout.specs import BLOCK_SPECS, FIELD_SPECS, PAGE_SPEC
from danfse.layout.visibility import is_block_visible, is_field_visible
from danfse.rules.models.formatted import FormattedDanfse


def build_layout_plan(formatted: FormattedDanfse) -> DanfseLayoutPlan:
    page = PAGE_SPEC
    page_rect = PositionedRect(
        x_pt=cm_to_pt(0.30),
        y_pt=cm_to_pt(0.30),
        width_pt=cm_to_pt(page.width_cm - 0.60),
        height_pt=cm_to_pt(page.height_cm - 0.60),
    )

    blocks: list[LayoutBlock] = []
    for block_spec in BLOCK_SPECS:
        block_visible = is_block_visible(formatted, block_spec.key, optional=block_spec.optional)
        block_rect = _rect_from_cm(
            x_cm=block_spec.x_cm,
            y_top_cm=block_spec.y_top_cm,
            width_cm=block_spec.width_cm,
            height_cm=block_spec.height_cm,
            page_height_cm=page.height_cm,
        )

        elements: list[LayoutElement] = []
        if block_visible:
            for field_spec in FIELD_SPECS:
                if field_spec.block != block_spec.key:
                    continue

                value = _resolve_value(field_spec, formatted)
                if not is_field_visible(field_spec, formatted, value):
                    continue

                elements.append(
                    LayoutElement(
                        key=field_spec.key,
                        block=field_spec.block,
                        kind=field_spec.kind,
                        rect=_rect_from_cm(
                            x_cm=field_spec.x_cm,
                            y_top_cm=field_spec.y_top_cm,
                            width_cm=field_spec.width_cm,
                            height_cm=field_spec.height_cm,
                            page_height_cm=page.height_cm,
                        ),
                        label=field_spec.label,
                        value=value,
                        shaded=field_spec.shaded,
                        multiline=field_spec.multiline,
                        max_chars=field_spec.max_chars,
                    ),
                )

        blocks.append(
            LayoutBlock(
                key=block_spec.key,
                rect=block_rect,
                elements=tuple(elements),
                visible=block_visible,
            ),
        )

    return DanfseLayoutPlan(
        page=page,
        formatted=formatted,
        blocks=tuple(blocks),
        page_rect=page_rect,
        watermark=formatted.watermark,
        homologacao_aviso=formatted.cabecalho.homologacao_aviso,
    )


def _resolve_value(field_spec, formatted: FormattedDanfse) -> str:
    if field_spec.key.endswith(".mensagem_nao_identificado") or field_spec.key.endswith(
        ".mensagem_igual_tomador",
    ) or field_spec.key == "tributacao_municipal.mensagem_nao_sujeita_issqn":
        return resolve_field_value(field_spec.key, formatted)
    if field_spec.fixed_text and field_spec.kind in {"fixed_text", "block_title"}:
        return field_spec.fixed_text
    return resolve_field_value(field_spec.key, formatted)


def _rect_from_cm(
    *,
    x_cm: float,
    y_top_cm: float,
    width_cm: float,
    height_cm: float,
    page_height_cm: float,
) -> PositionedRect:
    x_pt, y_pt, width_pt, height_pt = top_left_cm_to_pdf_rect(
        x_cm=x_cm,
        y_top_cm=y_top_cm,
        width_cm=width_cm,
        height_cm=height_cm,
        page_height_cm=page_height_cm,
    )
    return PositionedRect(x_pt=x_pt, y_pt=y_pt, width_pt=width_pt, height_pt=height_pt)
