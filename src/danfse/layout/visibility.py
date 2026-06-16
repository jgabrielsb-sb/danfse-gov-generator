from __future__ import annotations

from danfse.layout.specs import FieldSpec
from danfse.rules.formatting.primitives import EMPTY_DISPLAY
from danfse.rules.models.formatted import FormattedDanfse

PARTY_BLOCKS = frozenset({"tomador", "destinatario", "intermediario"})
MESSAGE_FIELD_SUFFIXES = (
    ".mensagem_nao_identificado",
    ".mensagem_igual_tomador",
)
OPTIONAL_SECTION_BLOCKS = frozenset({
    "tributacao_federal",
    "tributacao_ibs_cbs",
    "informacoes_complementares",
    "canhoto",
})


def has_meaningful_value(value: str | None) -> bool:
    if value is None:
        return False
    text = value.strip()
    return bool(text) and text != EMPTY_DISPLAY


def party_has_message(data: FormattedDanfse, block: str) -> bool:
    party = getattr(data, block, None)
    return party is not None and bool(party.bloco_texto.strip())


def section_is_present(data: FormattedDanfse, block: str) -> bool:
    if block == "tributacao_municipal":
        trib = data.tributacao_municipal
        return trib is not None and not bool(trib.bloco_texto.strip())
    if block in OPTIONAL_SECTION_BLOCKS:
        return getattr(data, block, None) is not None
    return True


def is_block_visible(data: FormattedDanfse, block_key: str, *, optional: bool) -> bool:
    if block_key in OPTIONAL_SECTION_BLOCKS:
        return getattr(data, block_key, None) is not None
    if block_key in PARTY_BLOCKS:
        return getattr(data, block_key, None) is not None
    if block_key == "tributacao_municipal":
        return data.tributacao_municipal is not None
    if optional:
        return section_is_present(data, block_key)
    return True


def is_field_visible(spec: FieldSpec, data: FormattedDanfse, value: str) -> bool:
    if spec.key.startswith("block."):
        return True

    if spec.kind == "image":
        return spec.key == "assets.logo_nfse"

    block = spec.block

    if block in PARTY_BLOCKS:
        if party_has_message(data, block):
            if spec.key == f"{block}.mensagem_nao_identificado":
                return True
            if spec.key.startswith("block."):
                return spec.key == f"block.{block}.title"
            return False
        if spec.key.endswith(MESSAGE_FIELD_SUFFIXES):
            return False

    if block == "tributacao_municipal" and data.tributacao_municipal is not None:
        if data.tributacao_municipal.bloco_texto.strip():
            return spec.key in {
                "block.tributacao_municipal.title",
                "tributacao_municipal.mensagem_nao_sujeita_issqn",
            }

    if block in OPTIONAL_SECTION_BLOCKS and getattr(data, block, None) is None:
        return False

    if spec.kind in {"fixed_text", "block_title", "qrcode"}:
        if spec.kind == "qrcode":
            return has_meaningful_value(value)
        return True

    if spec.optional and not has_meaningful_value(value):
        return False

    return True
