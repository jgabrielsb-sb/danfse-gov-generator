from __future__ import annotations

CM_PER_INCH = 2.54
PT_PER_INCH = 72.0
CM_TO_PT = PT_PER_INCH / CM_PER_INCH


def cm_to_pt(value_cm: float) -> float:
    return value_cm * CM_TO_PT


def top_left_cm_to_pdf_rect(
    *,
    x_cm: float,
    y_top_cm: float,
    width_cm: float,
    height_cm: float,
    page_height_cm: float,
) -> tuple[float, float, float, float]:
    """Converte coordenadas NT (origem no canto superior esquerdo) para ReportLab (inferior esquerdo)."""
    width_pt = cm_to_pt(width_cm)
    height_pt = cm_to_pt(height_cm)
    x_pt = cm_to_pt(x_cm)
    y_bottom_cm = page_height_cm - y_top_cm - height_cm
    y_pt = cm_to_pt(y_bottom_cm)
    return x_pt, y_pt, width_pt, height_pt
