from __future__ import annotations

from typing import Optional


def draw_watermark(canvas, text: Optional[str]) -> None:
    if not text:
        return
    canvas.saveState()
    canvas.setFillGray(0.85)
    canvas.setFont("Helvetica-Bold", 48)
    canvas.translate(200, 350)
    canvas.rotate(30)
    canvas.drawString(0, 0, text)
    canvas.restoreState()

