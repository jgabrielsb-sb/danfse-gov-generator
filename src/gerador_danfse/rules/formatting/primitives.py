from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Any

from danfse.domain.models import DocumentoPessoaDanfse

EMPTY_DISPLAY = "-"
ELLIPSIS = "..."


def display_or_dash(value: str | None) -> str:
    if value is None:
        return EMPTY_DISPLAY
    text = str(value).strip()
    return text if text else EMPTY_DISPLAY


def truncate_with_ellipsis(text: str | None, max_len: int) -> str:
    if not text:
        return EMPTY_DISPLAY
    if len(text) <= max_len:
        return text
    if max_len <= len(ELLIPSIS):
        return ELLIPSIS[:max_len]
    return text[: max_len - len(ELLIPSIS)] + ELLIPSIS


def format_cnpj(value: str | None) -> str:
    digits = _only_digits(value)
    if len(digits) == 14:
        return f"{digits[0:2]}.{digits[2:5]}.{digits[5:8]}/{digits[8:12]}-{digits[12:14]}"
    return display_or_dash(value)


def format_cpf(value: str | None) -> str:
    digits = _only_digits(value)
    if len(digits) == 11:
        return f"{digits[0:3]}.{digits[3:6]}.{digits[6:9]}-{digits[9:11]}"
    return display_or_dash(value)


def format_nif(value: str | None) -> str:
    return display_or_dash(value)


def format_documento_pessoa(documento: DocumentoPessoaDanfse | None) -> str:
    if documento is None:
        return EMPTY_DISPLAY
    if documento.cnpj:
        return format_cnpj(documento.cnpj)
    if documento.cpf:
        return format_cpf(documento.cpf)
    if documento.nif:
        return format_nif(documento.nif)
    return EMPTY_DISPLAY


def format_cep(value: str | None) -> str:
    digits = _only_digits(value)
    if len(digits) == 8:
        return f"{digits[0:2]}.{digits[2:5]}-{digits[5:8]}"
    return display_or_dash(value)


def format_access_key(value: str | None) -> str:
    if not value:
        return EMPTY_DISPLAY
    text = value.strip()
    if text.startswith("NFS"):
        text = text[3:]
    digits = _only_digits(text)
    return digits if digits else display_or_dash(value)


def format_date(value: date | None) -> str:
    if value is None:
        return EMPTY_DISPLAY
    return value.strftime("%d/%m/%Y")


def format_datetime(value: datetime | None) -> str:
    if value is None:
        return EMPTY_DISPLAY
    return value.strftime("%d/%m/%Y %H:%M:%S")


def format_money(value: Decimal | None) -> str:
    if value is None:
        return EMPTY_DISPLAY
    q = value.quantize(Decimal("0.01"))
    s = f"{q:,.2f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def format_percent(value: Decimal | None, *, suffix: str = "%") -> str:
    if value is None:
        return EMPTY_DISPLAY
    q = value.quantize(Decimal("0.01"))
    s = f"{q:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"{s}{suffix}" if suffix else s


def format_percent_pair(left: Decimal | None, right: Decimal | None) -> str:
    return f"{format_percent(left)} / {format_percent(right)}"


def format_percent_triple(
    a: Decimal | None,
    b: Decimal | None,
    c: Decimal | None,
) -> str:
    return f"{format_percent(a)} / {format_percent(b)} / {format_percent(c)}"


def format_by_xsd_type(xsd_type: str, value: Any) -> str:
    if value is None:
        return EMPTY_DISPLAY

    if xsd_type in {"TSCNPJ"}:
        return format_cnpj(str(value))
    if xsd_type in {"TSCPF"}:
        return format_cpf(str(value))
    if xsd_type in {"TSNIF"}:
        return format_nif(str(value))
    if xsd_type in {"TSCEP"}:
        return format_cep(str(value))
    if xsd_type in {"TSData"}:
        if isinstance(value, date):
            return format_date(value)
        return display_or_dash(str(value))
    if xsd_type in {"TSDateTimeUTC"}:
        if isinstance(value, datetime):
            return format_datetime(value)
        return display_or_dash(str(value))
    if xsd_type in {"TSDec15V2", "TSDec1V2", "TSDec3V2"}:
        if isinstance(value, Decimal):
            return format_money(value)
        return format_money(Decimal(str(value)))
    if xsd_type in {"TSDec2V2"}:
        if isinstance(value, Decimal):
            return format_percent(value)
        return format_percent(Decimal(str(value)))
    if xsd_type in {"TSIdNFSe"}:
        return format_access_key(str(value))

    if isinstance(value, Decimal):
        return format_money(value)
    if isinstance(value, datetime):
        return format_datetime(value)
    if isinstance(value, date):
        return format_date(value)
    return display_or_dash(str(value))


def _only_digits(value: str | None) -> str:
    if not value:
        return ""
    return "".join(ch for ch in value if ch.isdigit())


# Aliases legados usados pelo pdf_renderer (integração completa em tarefa futura).
def truncate(text: str | None, max_len: int) -> str:
    if not text:
        return ""
    if len(text) <= max_len:
        return text
    return truncate_with_ellipsis(text, max_len)


def format_document(value: str | None) -> str:
    return display_or_dash(value)
