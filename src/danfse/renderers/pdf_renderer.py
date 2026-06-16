from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas as rl_canvas

from danfse.exceptions import PdfRenderError
from danfse.layout.constants import PAGE_HEIGHT_PT, PAGE_WIDTH_PT
from danfse.layout.models import DanfseLayoutPlan, LayoutElement
from danfse.renderers.qrcode import QrCodePayload, build_qrcode_image
from danfse.renderers.watermark import draw_watermark


@dataclass(frozen=True)
class PdfRenderOptions:
    watermark_text: str | None = None
    logo_path: str | Path | None = None


def render_pdf(
    plan: DanfseLayoutPlan,
    output_path: str | Path,
    *,
    options: PdfRenderOptions | None = None,
) -> None:
    options = options or PdfRenderOptions()
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)

    try:
        pdf = rl_canvas.Canvas(str(out), pagesize=(PAGE_WIDTH_PT, PAGE_HEIGHT_PT))
        watermark = options.watermark_text if options.watermark_text is not None else plan.watermark
        draw_watermark(pdf, watermark or None)
        _draw_page_border(pdf, plan)
        if plan.homologacao_aviso:
            _draw_homologacao_banner(pdf, plan.homologacao_aviso)
        for block in plan.blocks:
            if not block.visible:
                continue
            _draw_block_border(pdf, block.rect, plan.page.inner_line_width_pt)
            for element in block.elements:
                _draw_element(pdf, element, logo_path=options.logo_path)
        pdf.showPage()
        pdf.save()
    except Exception as exc:
        raise PdfRenderError(f"Failed to render PDF: {output_path}") from exc


def _draw_page_border(pdf: rl_canvas.Canvas, plan: DanfseLayoutPlan) -> None:
    rect = plan.page_rect
    pdf.setLineWidth(plan.page.border_width_pt)
    pdf.rect(rect.x_pt, rect.y_pt, rect.width_pt, rect.height_pt, stroke=1, fill=0)


def _draw_block_border(pdf: rl_canvas.Canvas, rect, line_width: float) -> None:
    pdf.setLineWidth(line_width)
    pdf.rect(rect.x_pt, rect.y_pt, rect.width_pt, rect.height_pt, stroke=1, fill=0)


def _draw_homologacao_banner(pdf: rl_canvas.Canvas, text: str) -> None:
    pdf.saveState()
    pdf.setFillColorRGB(1, 0.9, 0.9)
    pdf.rect(36, PAGE_HEIGHT_PT - 72, PAGE_WIDTH_PT - 72, 24, stroke=0, fill=1)
    pdf.setFillColorRGB(0.6, 0, 0)
    pdf.setFont("Helvetica-Bold", 8)
    pdf.drawCentredString(PAGE_WIDTH_PT / 2, PAGE_HEIGHT_PT - 64, text)
    pdf.restoreState()


def _draw_element(
    pdf: rl_canvas.Canvas,
    element: LayoutElement,
    *,
    logo_path: str | Path | None,
) -> None:
    if element.shaded:
        pdf.saveState()
        pdf.setFillColorRGB(0.92, 0.92, 0.92)
        pdf.rect(element.rect.x_pt, element.rect.y_pt, element.rect.width_pt, element.rect.height_pt, fill=1, stroke=0)
        pdf.restoreState()

    if element.kind == "image":
        if logo_path:
            pdf.drawImage(
                ImageReader(str(logo_path)),
                element.rect.x_pt,
                element.rect.y_pt,
                element.rect.width_pt,
                element.rect.height_pt,
                preserveAspectRatio=True,
                mask="auto",
            )
        return

    if element.kind == "qrcode":
        _draw_qrcode(pdf, element)
        return

    if element.kind == "block_title":
        _draw_block_title(pdf, element)
        return

    if element.kind == "fixed_text":
        _draw_fixed_text(pdf, element)
        return

    _draw_labeled_value(pdf, element)


def _draw_block_title(pdf: rl_canvas.Canvas, element: LayoutElement) -> None:
    pdf.setFont("Helvetica-Bold", 7)
    pdf.drawString(
        element.rect.x_pt + 2,
        element.rect.y_pt + element.rect.height_pt - 9,
        element.value,
    )


def _draw_fixed_text(pdf: rl_canvas.Canvas, element: LayoutElement) -> None:
    lines = element.value.splitlines() or [""]
    if element.multiline:
        _draw_multiline(pdf, element, lines, font_name="Helvetica", font_size=6, start_y=None)
        return
    pdf.setFont("Helvetica", 6)
    pdf.drawString(
        element.rect.x_pt + 2,
        element.rect.y_pt + element.rect.height_pt - 8,
        lines[0],
    )


def _draw_labeled_value(pdf: rl_canvas.Canvas, element: LayoutElement) -> None:
    top_y = element.rect.y_pt + element.rect.height_pt
    if element.label:
        pdf.setFont("Helvetica", 5.5)
        pdf.drawString(element.rect.x_pt + 2, top_y - 7, element.label)
        value_top = top_y - 14
    else:
        value_top = top_y - 8

    value = element.value
    if element.max_chars is not None and len(value) > element.max_chars:
        value = value[: element.max_chars]

    if element.multiline:
        _draw_multiline(
            pdf,
            element,
            _wrap_text(value, element.max_chars),
            font_name="Helvetica-Bold",
            font_size=6.5,
            start_y=value_top,
        )
        return

    pdf.setFont("Helvetica-Bold", 6.5)
    pdf.drawString(element.rect.x_pt + 2, value_top - 7, value)


def _draw_multiline(
    pdf: rl_canvas.Canvas,
    element: LayoutElement,
    lines: list[str],
    *,
    font_name: str,
    font_size: float,
    start_y: float | None = None,
) -> None:
    leading = font_size + 2
    max_lines = max(1, int(element.rect.height_pt // leading))
    lines = lines[:max_lines]
    y = start_y if start_y is not None else element.rect.y_pt + element.rect.height_pt - 8
    text_obj = pdf.beginText(element.rect.x_pt + 2, y)
    text_obj.setFont(font_name, font_size)
    text_obj.setLeading(leading)
    for line in lines:
        text_obj.textLine(line)
    pdf.drawText(text_obj)


def _draw_qrcode(pdf: rl_canvas.Canvas, element: LayoutElement) -> None:
    if not element.value:
        return
    image = build_qrcode_image(QrCodePayload(url=element.value))
    if image is None:
        pdf.setFont("Helvetica", 5)
        pdf.drawString(
            element.rect.x_pt,
            element.rect.y_pt + element.rect.height_pt / 2,
            "QR indisponível",
        )
        return
    pdf.drawImage(
        ImageReader(image),
        element.rect.x_pt,
        element.rect.y_pt,
        element.rect.width_pt,
        element.rect.height_pt,
        preserveAspectRatio=True,
        mask="auto",
    )


def _wrap_text(text: str, max_chars: int | None) -> list[str]:
    if not text:
        return [""]
    width = max_chars or 120
    words = text.split()
    lines: list[str] = []
    current: list[str] = []
    for word in words:
        candidate = " ".join(current + [word]).strip()
        if len(candidate) <= width:
            current.append(word)
            continue
        if current:
            lines.append(" ".join(current))
        current = [word]
    if current:
        lines.append(" ".join(current))
    return lines or [""]
