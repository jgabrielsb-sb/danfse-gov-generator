from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas as rl_canvas

from danfse.domain.models import DanfseData
from danfse.exceptions import PdfRenderError
from danfse.layout.constants import PAGE_HEIGHT, PAGE_WIDTH
from danfse.layout.layout_engine import LayoutPlan
from danfse.rules.formatting.descriptions import normalize_description
from danfse.rules.formatting.primitives import (
    format_date,
    format_datetime,
    format_document,
    format_money,
    truncate,
)
from danfse.renderers.qrcode import QrCodePayload, build_qrcode_image
from danfse.renderers.watermark import draw_watermark


@dataclass(frozen=True)
class PdfRenderOptions:
    watermark_text: str | None = None


def render_pdf(plan: LayoutPlan, output_path: str | Path, *, options: PdfRenderOptions | None = None) -> None:
    options = options or PdfRenderOptions()
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)

    try:
        c = rl_canvas.Canvas(str(out), pagesize=(PAGE_WIDTH, PAGE_HEIGHT))
        draw_watermark(c, options.watermark_text)
        _draw(c, plan.data, plan)
        c.showPage()
        c.save()
    except Exception as exc:
        raise PdfRenderError(f"Failed to render PDF: {output_path}") from exc


def _box_title(c, x: float, y: float, w: float, h: float, title: str) -> None:
    c.setLineWidth(1)
    c.rect(x, y, w, h, stroke=1, fill=0)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(x + 6, y + h - 14, title)


def _draw_kv(c, x: float, y: float, label: str, value: str, *, label_w: float = 120) -> None:
    c.setFont("Helvetica", 9)
    c.drawString(x, y, f"{label}:")
    c.setFont("Helvetica-Bold", 9)
    c.drawString(x + label_w, y, value or "")


def _draw(c, data: DanfseData, plan: LayoutPlan) -> None:
    spec = plan.spec

    # Header
    hb = spec.header
    _box_title(c, hb.x, hb.y, hb.w, hb.h, "DANFSe (versão inicial)")
    c.setFont("Helvetica", 9)
    c.drawString(hb.x + 6, hb.y + hb.h - 30, f"Município: {data.municipality or ''}")
    _draw_kv(c, hb.x + 6, hb.y + hb.h - 48, "NFS-e Nº", data.nfse_number or "")
    _draw_kv(c, hb.x + 6, hb.y + hb.h - 62, "Código verificação", data.verification_code or "")
    _draw_kv(c, hb.x + 6, hb.y + hb.h - 76, "Emissão", format_datetime(data.issue_datetime))
    _draw_kv(c, hb.x + 6, hb.y + hb.h - 90, "Competência", format_date(data.competence_date))

    # Parties
    pb = spec.parties
    _box_title(c, pb.x, pb.y, pb.w, pb.h, "Prestador / Tomador")

    left_x = pb.x + 6
    mid_x = pb.x + pb.w / 2 + 6
    top_y = pb.y + pb.h - 30

    c.setFont("Helvetica-Bold", 9)
    c.drawString(left_x, top_y, "Prestador")
    c.drawString(mid_x, top_y, "Tomador")

    _draw_kv(c, left_x, top_y - 14, "Nome", truncate(data.provider.name, 42))
    _draw_kv(c, left_x, top_y - 28, "Doc", format_document(data.provider.document))
    _draw_kv(c, left_x, top_y - 42, "IM", data.provider.municipal_registration or "")
    _draw_kv(c, left_x, top_y - 56, "Endereço", truncate(data.provider.address, 42))
    _draw_kv(c, left_x, top_y - 70, "Cidade/UF", " / ".join(filter(None, [data.provider.city, data.provider.state])))

    _draw_kv(c, mid_x, top_y - 14, "Nome", truncate(data.taker.name, 42))
    _draw_kv(c, mid_x, top_y - 28, "Doc", format_document(data.taker.document))
    _draw_kv(c, mid_x, top_y - 42, "IM", data.taker.municipal_registration or "")
    _draw_kv(c, mid_x, top_y - 56, "Endereço", truncate(data.taker.address, 42))
    _draw_kv(c, mid_x, top_y - 70, "Cidade/UF", " / ".join(filter(None, [data.taker.city, data.taker.state])))

    # Service
    sb = spec.service
    _box_title(c, sb.x, sb.y, sb.w, sb.h, "Serviço")

    y = sb.y + sb.h - 30
    _draw_kv(c, sb.x + 6, y, "Item lista", data.service_code or "", label_w=90)
    _draw_kv(c, sb.x + 260, y, "CNAE", data.cnae or "", label_w=45)
    _draw_kv(c, sb.x + 420, y, "Município", data.city_service_code or "", label_w=65)

    desc = normalize_description(data.service_description)
    c.setFont("Helvetica", 9)
    c.drawString(sb.x + 6, y - 16, "Discriminação:")
    c.setFont("Helvetica", 9)
    text = c.beginText(sb.x + 6, y - 30)
    text.setLeading(12)
    for line in _wrap(desc, max_chars=120, max_lines=int((sb.h - 60) / 12)):
        text.textLine(line)
    c.drawText(text)

    # Values
    vb = spec.values
    _box_title(c, vb.x, vb.y, vb.w, vb.h, "Valores")
    base_y = vb.y + vb.h - 30
    _draw_kv(c, vb.x + 6, base_y, "Serviços", format_money(data.values.total_services), label_w=90)
    _draw_kv(c, vb.x + 6, base_y - 14, "Deduções", format_money(data.values.deductions), label_w=90)
    _draw_kv(c, vb.x + 6, base_y - 28, "ISS", format_money(data.values.iss), label_w=90)
    _draw_kv(c, vb.x + 6, base_y - 42, "Líquido", format_money(data.values.net_value), label_w=90)

    # QR code (optional)
    if data.qr_code_url:
        img = build_qrcode_image(QrCodePayload(url=data.qr_code_url))
        if img is not None:
            qr_size = 72
            c.drawImage(ImageReader(img), vb.x + vb.w - qr_size - 6, vb.y + 6, qr_size, qr_size)
        else:
            c.setFont("Helvetica", 7)
            c.drawRightString(vb.x + vb.w - 6, vb.y + 10, "Instale extra 'danfse[qrcode]' p/ QRCode")

    # Footer
    fb = spec.footer
    _box_title(c, fb.x, fb.y, fb.w, fb.h, "Observações")
    c.setFont("Helvetica", 8)
    c.drawString(fb.x + 6, fb.y + fb.h - 30, "Implementação mínima. Layout completo será evoluído.")


def _wrap(text: str, *, max_chars: int, max_lines: int) -> list[str]:
    if not text:
        return [""]
    words = text.split()
    lines: list[str] = []
    current: list[str] = []
    for w in words:
        candidate = (" ".join(current + [w])).strip()
        if len(candidate) <= max_chars:
            current.append(w)
            continue
        if current:
            lines.append(" ".join(current))
        current = [w]
        if len(lines) >= max_lines:
            break
    if len(lines) < max_lines and current:
        lines.append(" ".join(current))
    if len(lines) > max_lines:
        lines = lines[:max_lines]
    return lines

