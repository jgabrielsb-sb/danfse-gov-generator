from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class QrCodePayload:
    url: str


def can_render_qrcode() -> bool:
    try:
        import qrcode  # noqa: F401

        return True
    except Exception:
        return False


def build_qrcode_image(payload: Optional[QrCodePayload]):
    """
    Returns a PIL Image (if qrcode extra is installed), else None.
    """
    if not payload or not payload.url:
        return None
    if not can_render_qrcode():
        return None
    import qrcode  # type: ignore

    qr = qrcode.QRCode(border=1, box_size=4)
    qr.add_data(payload.url)
    qr.make(fit=True)
    return qr.make_image(fill_color="black", back_color="white")

