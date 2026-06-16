from __future__ import annotations

from dataclasses import dataclass

from danfse.layout.constants import MARGIN_X, MARGIN_Y, PAGE_HEIGHT, PAGE_WIDTH


@dataclass(frozen=True)
class Box:
    x: float
    y: float
    w: float
    h: float


@dataclass(frozen=True)
class DanfseLayoutSpec:
    """
    Minimal layout spec (not full official compliance yet).
    Coordinates: ReportLab uses a bottom-left origin.
    """

    header: Box
    parties: Box
    service: Box
    values: Box
    footer: Box


def default_layout() -> DanfseLayoutSpec:
    content_w = PAGE_WIDTH - 2 * MARGIN_X
    top = PAGE_HEIGHT - MARGIN_Y

    header_h = 95
    parties_h = 140
    values_h = 90
    footer_h = 60
    service_h = (top - MARGIN_Y) - (header_h + parties_h + values_h + footer_h)

    header = Box(MARGIN_X, top - header_h, content_w, header_h)
    parties = Box(MARGIN_X, header.y - parties_h, content_w, parties_h)
    service = Box(MARGIN_X, parties.y - service_h, content_w, service_h)
    values = Box(MARGIN_X, service.y - values_h, content_w, values_h)
    footer = Box(MARGIN_X, values.y - footer_h, content_w, footer_h)

    return DanfseLayoutSpec(header=header, parties=parties, service=service, values=values, footer=footer)

