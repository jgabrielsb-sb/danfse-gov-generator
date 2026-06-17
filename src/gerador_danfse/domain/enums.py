from __future__ import annotations

from enum import Enum


class DocumentType(str, Enum):
    CPF = "CPF"
    CNPJ = "CNPJ"

