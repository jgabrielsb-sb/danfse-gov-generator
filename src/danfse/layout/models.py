from __future__ import annotations

from dataclasses import dataclass, field

from danfse.layout.specs import PageSpec, RenderKind
from danfse.rules.models.formatted import FormattedDanfse


@dataclass(frozen=True)
class PositionedRect:
    x_pt: float
    y_pt: float
    width_pt: float
    height_pt: float


@dataclass(frozen=True)
class LayoutElement:
    key: str
    block: str
    kind: RenderKind
    rect: PositionedRect
    label: str | None = None
    value: str = ""
    shaded: bool = False
    multiline: bool = False
    max_chars: int | None = None


@dataclass(frozen=True)
class LayoutBlock:
    key: str
    rect: PositionedRect
    elements: tuple[LayoutElement, ...] = ()
    visible: bool = True


@dataclass(frozen=True)
class DanfseLayoutPlan:
    page: PageSpec
    formatted: FormattedDanfse
    blocks: tuple[LayoutBlock, ...] = ()
    page_rect: PositionedRect = field(default_factory=lambda: PositionedRect(0, 0, 0, 0))
    watermark: str = ""
    homologacao_aviso: str = ""
