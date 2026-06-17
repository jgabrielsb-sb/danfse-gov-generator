from __future__ import annotations

from gerador_danfse.layout.coordinates import cm_to_pt
from gerador_danfse.layout.layout_engine import build_layout_plan
from gerador_danfse.layout.models import DanfseLayoutPlan

PAGE_WIDTH_PT = cm_to_pt(21.0)
PAGE_HEIGHT_PT = cm_to_pt(29.7)

__all__ = [
    "DanfseLayoutPlan",
    "PAGE_HEIGHT_PT",
    "PAGE_WIDTH_PT",
    "build_layout_plan",
]
