from __future__ import annotations

from datetime import date

from gerador_danfse.domain.models import DanfseData, StatusVisualDanfse
from gerador_danfse.rules.catalog.field_specs import NT_LIMITS
from gerador_danfse.rules.formatting.primitives import EMPTY_DISPLAY, display_or_dash

MSG_TOMADOR_NAO_IDENTIFICADO = "Tomador do Serviço não identificado na NFS-e"
MSG_DESTINATARIO_NAO_IDENTIFICADO = "Destinatário da operação não identificado na NFS-e"
MSG_DESTINATARIO_IGUAL_TOMADOR = "Destinatário da operação igual ao Tomador do Serviço"
MSG_INTERMEDIARIO_NAO_IDENTIFICADO = "Intermediário do Serviço não identificado na NFS-e"
MSG_OPERACAO_NAO_SUJEITA_ISSQN = "Operação não sujeita ao ISSQN"
MSG_HOMOLOGACAO = (
    "DOCUMENTO EMITIDO EM AMBIENTE DE HOMOLOGAÇÃO - SEM VALOR FISCAL"
)

WATERMARK_CANCELADA = "CANCELADA"
WATERMARK_SUBSTITUIDA = "SUBSTITUÍDA"

PIS_COFINS_RETENTION_CUTOFF = date(2026, 12, 31)


def should_show_pis_cofins_retention(competencia: date | None) -> bool:
    if competencia is None:
        return True
    return competencia <= PIS_COFINS_RETENTION_CUTOFF


def resolve_watermark(status: StatusVisualDanfse) -> str:
    if status.is_cancelada:
        return WATERMARK_CANCELADA
    if status.is_substituida:
        return WATERMARK_SUBSTITUIDA
    return ""


def resolve_homologacao_aviso(status: StatusVisualDanfse) -> str:
    return MSG_HOMOLOGACAO if status.is_homologacao else ""


def resolve_tomador_bloco(status: StatusVisualDanfse) -> str:
    if status.tomador_nao_identificado:
        return truncate_party_message(MSG_TOMADOR_NAO_IDENTIFICADO)
    return ""


def resolve_destinatario_bloco(status: StatusVisualDanfse) -> str:
    if status.destinatario_nao_identificado:
        return truncate_party_message(MSG_DESTINATARIO_NAO_IDENTIFICADO)
    if status.destinatario_igual_tomador:
        return truncate_party_message(MSG_DESTINATARIO_IGUAL_TOMADOR)
    return ""


def resolve_intermediario_bloco(status: StatusVisualDanfse) -> str:
    if status.intermediario_nao_identificado:
        return truncate_party_message(MSG_INTERMEDIARIO_NAO_IDENTIFICADO)
    return ""


def resolve_tributacao_municipal_bloco(status: StatusVisualDanfse) -> str:
    if status.operacao_nao_sujeita_issqn:
        return MSG_OPERACAO_NAO_SUJEITA_ISSQN
    return ""


def should_render_party_block(status: StatusVisualDanfse, party: str) -> bool:
    if party == "tomador":
        return not status.tomador_nao_identificado
    if party == "destinatario":
        return (
            not status.destinatario_nao_identificado
            and not status.destinatario_igual_tomador
        )
    if party == "intermediario":
        return not status.intermediario_nao_identificado
    return True


def should_render_tributacao_municipal(data: DanfseData) -> bool:
    return not data.status_visual.operacao_nao_sujeita_issqn


def truncate_party_message(message: str) -> str:
    if len(message) <= NT_LIMITS["address"]:
        return message
    return message[: NT_LIMITS["address"] - 3].rstrip() + "..."


def format_pis_cofins_retention_label(
    code: str | None,
    *,
    competencia: date | None,
    label: str,
) -> str:
    if not should_show_pis_cofins_retention(competencia):
        return EMPTY_DISPLAY
    if not label:
        return display_or_dash(code)
    return label
