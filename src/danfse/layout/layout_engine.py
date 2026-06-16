from __future__ import annotations

from dataclasses import dataclass

from danfse.domain.models import DanfseData
from danfse.layout.specs import DanfseLayoutSpec, default_layout


@dataclass(frozen=True)
class LayoutPlan:
    spec: DanfseLayoutSpec
    data: DanfseData


def build_layout_plan(data: DanfseData, spec: DanfseLayoutSpec | None = None) -> LayoutPlan:
    return LayoutPlan(spec=spec or default_layout(), data=data)

