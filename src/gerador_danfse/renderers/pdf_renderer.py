from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas as rl_canvas

from danfse.exceptions import PdfRenderError
from danfse.layout.constants import PAGE_HEIGHT_PT, PAGE_WIDTH_PT
from danfse.layout.models import DanfseLayoutPlan, LayoutElement, PositionedRect
from danfse.renderers.assets import resolve_logo_path
from danfse.renderers.pdf_text import fit_text, wrap_text
from danfse.renderers.qrcode import QrCodePayload, build_qrcode_image
from danfse.renderers.watermark import draw_watermark

LABEL_FONT = "Helvetica"
LABEL_SIZE = 5.5
VALUE_FONT = "Helvetica-Bold"
VALUE_SIZE = 7.0
TITLE_FONT = "Helvetica-Bold"
TITLE_SIZE = 7.0
FIXED_FONT = "Helvetica"
FIXED_SIZE = 6.0
CABECALHO_TITLE_SIZE = 9.0
CABECALHO_SUBTITLE_SIZE = 6.0
CABECALHO_MUNICIPIO_SIZE = 8.0
CABECALHO_AMBIENTE_SIZE = 6.0
CHAVE_FONT = "Courier-Bold"
CHAVE_SIZE = 8.0
CELL_PADDING = 2.5
SHADE_COLOR = colors.HexColor("#E6E6E6")
LINE_COLOR = colors.black


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
    logo_path = resolve_logo_path(options.logo_path)

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
                _draw_element(pdf, element, logo_path=logo_path, line_width=plan.page.inner_line_width_pt)

        pdf.showPage()
        pdf.save()
    except Exception as exc:
        raise PdfRenderError(f"Failed to render PDF: {output_path}") from exc


def _draw_page_border(pdf: rl_canvas.Canvas, plan: DanfseLayoutPlan) -> None:
    rect = plan.page_rect
    pdf.setStrokeColor(LINE_COLOR)
    pdf.setLineWidth(plan.page.border_width_pt)
    pdf.rect(rect.x_pt, rect.y_pt, rect.width_pt, rect.height_pt, stroke=1, fill=0)


def _draw_block_border(pdf: rl_canvas.Canvas, rect: PositionedRect, line_width: float) -> None:
    pdf.setStrokeColor(LINE_COLOR)
    pdf.setLineWidth(line_width)
    pdf.rect(rect.x_pt, rect.y_pt, rect.width_pt, rect.height_pt, stroke=1, fill=0)


def _draw_cell_border(pdf: rl_canvas.Canvas, rect: PositionedRect, line_width: float) -> None:
    pdf.setStrokeColor(LINE_COLOR)
    pdf.setLineWidth(line_width)
    pdf.rect(rect.x_pt, rect.y_pt, rect.width_pt, rect.height_pt, stroke=1, fill=0)


def _draw_homologacao_banner(pdf: rl_canvas.Canvas, text: str) -> None:
    pdf.saveState()
    pdf.setFillColor(colors.HexColor("#FFE6E6"))
    pdf.rect(36, PAGE_HEIGHT_PT - 72, PAGE_WIDTH_PT - 72, 24, stroke=0, fill=1)
    pdf.setFillColor(colors.HexColor("#990000"))
    pdf.setFont(TITLE_FONT, 8)
    pdf.drawCentredString(PAGE_WIDTH_PT / 2, PAGE_HEIGHT_PT - 64, text)
    pdf.restoreState()


def _draw_element(
    pdf: rl_canvas.Canvas,
    element: LayoutElement,
    *,
    logo_path: str | Path | None,
    line_width: float,
) -> None:
    if element.shaded:
        pdf.saveState()
        pdf.setFillColor(SHADE_COLOR)
        pdf.rect(element.rect.x_pt, element.rect.y_pt, element.rect.width_pt, element.rect.height_pt, fill=1, stroke=0)
        pdf.restoreState()

    if element.kind != "image":
        _draw_cell_border(pdf, element.rect, line_width)

    if element.kind == "image":
        _draw_logo(pdf, element, logo_path)
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

    if element.key in {
        "cabecalho.municipio_emitente",
        "cabecalho.ambiente_gerador",
        "cabecalho.tipo_ambiente",
    }:
        _draw_cabecalho_identificacao(pdf, element)
        return

    if element.key == "identificacao.chave_acesso":
        _draw_chave_acesso(pdf, element)
        return

    _draw_labeled_value(pdf, element)


def _inner_width(rect: PositionedRect) -> float:
    return max(4.0, rect.width_pt - (2 * CELL_PADDING))


def _draw_logo(
    pdf: rl_canvas.Canvas,
    element: LayoutElement,
    logo_path: str | Path | None,
) -> None:
    _draw_cell_border(pdf, element.rect, 0.5)

    if logo_path:
        pdf.drawImage(
            ImageReader(str(logo_path)),
            element.rect.x_pt + CELL_PADDING,
            element.rect.y_pt + CELL_PADDING,
            element.rect.width_pt - (2 * CELL_PADDING),
            element.rect.height_pt - (2 * CELL_PADDING),
            preserveAspectRatio=True,
            anchor="sw",
            mask="auto",
        )
        return

    pdf.saveState()
    pdf.setFillColor(colors.HexColor("#1B4F72"))
    pdf.rect(element.rect.x_pt, element.rect.y_pt, element.rect.width_pt, element.rect.height_pt, fill=1, stroke=0)
    pdf.setFillColor(colors.white)
    pdf.setFont(TITLE_FONT, 11)
    pdf.drawCentredString(
        element.rect.x_pt + element.rect.width_pt / 2,
        element.rect.y_pt + element.rect.height_pt / 2 - 4,
        "NFS-e",
    )
    pdf.setFont(LABEL_FONT, 6)
    pdf.drawCentredString(
        element.rect.x_pt + element.rect.width_pt / 2,
        element.rect.y_pt + element.rect.height_pt / 2 - 16,
        "Nacional",
    )
    pdf.restoreState()


def _draw_block_title(pdf: rl_canvas.Canvas, element: LayoutElement) -> None:
    pdf.setFont(TITLE_FONT, TITLE_SIZE)
    pdf.setFillColor(colors.black)
    text = fit_text(element.value, TITLE_FONT, TITLE_SIZE, _inner_width(element.rect))
    pdf.drawString(
        element.rect.x_pt + CELL_PADDING,
        element.rect.y_pt + element.rect.height_pt - TITLE_SIZE - CELL_PADDING,
        text,
    )


def _draw_cabecalho_identificacao(pdf: rl_canvas.Canvas, element: LayoutElement) -> None:
    inner_w = _inner_width(element.rect)
    if element.key == "cabecalho.municipio_emitente":
        font_name, font_size = VALUE_FONT, CABECALHO_MUNICIPIO_SIZE
    else:
        font_name, font_size = FIXED_FONT, CABECALHO_AMBIENTE_SIZE

    text = fit_text(element.value, font_name, font_size, inner_w)
    pdf.setFont(font_name, font_size)
    pdf.setFillColor(colors.black)
    pdf.drawString(
        element.rect.x_pt + CELL_PADDING,
        element.rect.y_pt + (element.rect.height_pt - font_size) / 2,
        text,
    )


def _draw_fixed_text(pdf: rl_canvas.Canvas, element: LayoutElement) -> None:
    inner_w = _inner_width(element.rect)
    if element.key == "cabecalho.titulo":
        lines = element.value.splitlines() or [""]
        font_sizes = [
            CABECALHO_TITLE_SIZE if index == 0 else CABECALHO_SUBTITLE_SIZE
            for index in range(len(lines))
        ]
        line_gap = 2.0
        total_height = sum(font_sizes) + line_gap * max(0, len(lines) - 1)
        baseline_y = element.rect.y_pt + (element.rect.height_pt + total_height) / 2
        for index, line in enumerate(lines):
            baseline_y -= font_sizes[index]
            pdf.setFont(TITLE_FONT, font_sizes[index])
            pdf.setFillColor(colors.black)
            pdf.drawCentredString(
                element.rect.x_pt + element.rect.width_pt / 2,
                baseline_y,
                line,
            )
            baseline_y -= line_gap
        return

    lines = wrap_text(
        element.value,
        FIXED_FONT,
        FIXED_SIZE,
        inner_w,
        max_lines=max(1, int(element.rect.height_pt // (FIXED_SIZE + 2))),
    )
    _draw_lines(
        pdf,
        element,
        lines,
        font_name=FIXED_FONT,
        font_size=FIXED_SIZE,
        start_y=element.rect.y_pt + element.rect.height_pt - FIXED_SIZE - CELL_PADDING,
    )


def _draw_chave_acesso(pdf: rl_canvas.Canvas, element: LayoutElement) -> None:
    top_y = element.rect.y_pt + element.rect.height_pt
    if element.label:
        pdf.setFont(LABEL_FONT, LABEL_SIZE)
        pdf.drawString(element.rect.x_pt + CELL_PADDING, top_y - LABEL_SIZE - 1, element.label)

    pdf.setFont(CHAVE_FONT, CHAVE_SIZE)
    chave = fit_text(element.value, CHAVE_FONT, CHAVE_SIZE, _inner_width(element.rect))
    pdf.drawCentredString(
        element.rect.x_pt + element.rect.width_pt / 2,
        element.rect.y_pt + element.rect.height_pt / 2 - 2,
        chave,
    )


def _draw_labeled_value(pdf: rl_canvas.Canvas, element: LayoutElement) -> None:
    top_y = element.rect.y_pt + element.rect.height_pt
    inner_w = _inner_width(element.rect)

    if element.label:
        label = fit_text(element.label, LABEL_FONT, LABEL_SIZE, inner_w)
        pdf.setFont(LABEL_FONT, LABEL_SIZE)
        pdf.drawString(element.rect.x_pt + CELL_PADDING, top_y - LABEL_SIZE - 1, label)
        value_y = top_y - LABEL_SIZE - VALUE_SIZE - 3
    else:
        value_y = top_y - VALUE_SIZE - CELL_PADDING

    value = element.value
    if element.multiline:
        max_lines = max(1, int((value_y - element.rect.y_pt) // (VALUE_SIZE + 2)))
        lines = wrap_text(value, VALUE_FONT, VALUE_SIZE, inner_w, max_lines=max_lines)
        _draw_lines(pdf, element, lines, font_name=VALUE_FONT, font_size=VALUE_SIZE, start_y=value_y)
        return

    pdf.setFont(VALUE_FONT, VALUE_SIZE)
    pdf.drawString(
        element.rect.x_pt + CELL_PADDING,
        value_y,
        fit_text(value, VALUE_FONT, VALUE_SIZE, inner_w),
    )


def _draw_lines(
    pdf: rl_canvas.Canvas,
    element: LayoutElement,
    lines: list[str],
    *,
    font_name: str,
    font_size: float,
    start_y: float,
) -> None:
    leading = font_size + 2
    text_obj = pdf.beginText(element.rect.x_pt + CELL_PADDING, start_y)
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
        pdf.setFont(LABEL_FONT, 5)
        pdf.drawString(
            element.rect.x_pt + CELL_PADDING,
            element.rect.y_pt + element.rect.height_pt / 2,
            "Instale extra danfse[qrcode]",
        )
        return
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)
    pdf.drawImage(
        ImageReader(buffer),
        element.rect.x_pt,
        element.rect.y_pt,
        element.rect.width_pt,
        element.rect.height_pt,
        preserveAspectRatio=True,
        mask="auto",
    )
