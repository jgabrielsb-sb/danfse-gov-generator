from __future__ import annotations

from datetime import date
from decimal import Decimal

from danfse.domain.models import (
    CodigoServicoDanfse,
    EnderecoDanfse,
    ExclusoesReducoesBaseCalculoIbsCbsDanfse,
    InformacoesComplementaresDanfse,
    LocalIncidenciaIssqnDanfse,
    LocalPrestacaoDanfse,
    TotaisAproximadosTributosDanfse,
)
from danfse.rules.catalog.field_specs import NT_LIMITS, QR_CODE_BASE_URL
from danfse.rules.formatting.primitives import (
    EMPTY_DISPLAY,
    display_or_dash,
    format_access_key,
    format_cep,
    format_money,
    format_percent,
    format_percent_triple,
    truncate_with_ellipsis,
)


def join_parts(parts: list[str | None], *, separator: str = " / ") -> str:
    cleaned = [part.strip() for part in parts if part and str(part).strip()]
    if not cleaned:
        return EMPTY_DISPLAY
    return separator.join(cleaned)


def format_municipio_uf(
    municipio: str | None,
    uf: str | None,
    *,
    pais: str | None = None,
    max_length: int = NT_LIMITS["address"],
) -> str:
    if pais and pais.strip() and pais.strip() != "105":
        text = join_parts([municipio, pais], separator=" / ")
    else:
        text = join_parts([municipio, uf], separator=" / ")
    return truncate_with_ellipsis(text, max_length)


def format_codigo_ibge_cep(endereco: EnderecoDanfse | None) -> str:
    if endereco is None:
        return EMPTY_DISPLAY

    if endereco.codigo_enderecamento_postal_exterior:
        return display_or_dash(endereco.codigo_enderecamento_postal_exterior)

    ibge = display_or_dash(endereco.codigo_municipio) if endereco.codigo_municipio else None
    cep = format_cep(endereco.cep) if endereco.cep else None

    if ibge == EMPTY_DISPLAY and cep == EMPTY_DISPLAY:
        return EMPTY_DISPLAY
    if ibge == EMPTY_DISPLAY:
        return cep
    if cep == EMPTY_DISPLAY:
        return ibge
    return f"{ibge} / {cep}"


def format_endereco(endereco: EnderecoDanfse | None) -> str:
    if endereco is None:
        return EMPTY_DISPLAY

    street_parts: list[str | None] = [endereco.logradouro]
    if endereco.numero:
        street_parts.append(f"nº {endereco.numero}")
    if endereco.complemento:
        street_parts.append(endereco.complemento)

    street = ", ".join(part.strip() for part in street_parts if part and part.strip())
    if endereco.bairro:
        if street:
            street = f"{street} - {endereco.bairro.strip()}"
        else:
            street = endereco.bairro.strip()

    return truncate_with_ellipsis(street or None, NT_LIMITS["address"])


def format_cabecalho_municipio(
    municipio: str | None,
    uf: str | None,
    *,
    codigo_tributacao_nacional: str | None,
) -> str:
    if codigo_tributacao_nacional == "99":
        return ""
    if not municipio and not uf:
        return EMPTY_DISPLAY
    municipio_part = f"Município: {municipio}" if municipio else None
    return truncate_with_ellipsis(
        join_parts([municipio_part, uf], separator=" / "),
        NT_LIMITS["address"],
    )


def format_codigo_tributacao(codigo: CodigoServicoDanfse | None) -> str:
    if codigo is None:
        return EMPTY_DISPLAY

    nacional = join_parts(
        [codigo.codigo_tributacao_nacional, codigo.descricao_tributacao_nacional],
        separator=" - ",
    )
    municipal = join_parts(
        [codigo.codigo_tributacao_municipal, codigo.descricao_tributacao_municipal],
        separator=" - ",
    )

    if nacional == EMPTY_DISPLAY and municipal == EMPTY_DISPLAY:
        return EMPTY_DISPLAY
    if municipal == EMPTY_DISPLAY:
        return nacional
    if nacional == EMPTY_DISPLAY:
        return municipal
    return f"{nacional} / {municipal}"


def format_codigo_nbs(codigo: CodigoServicoDanfse | None) -> str:
    if codigo is None or not codigo.codigo_nbs:
        return EMPTY_DISPLAY
    return display_or_dash(codigo.codigo_nbs)


def format_descricao_tributacao(codigo: CodigoServicoDanfse | None) -> str:
    if codigo is None:
        return EMPTY_DISPLAY

    parts: list[str] = []
    if codigo.descricao_tributacao_nacional:
        parts.append(codigo.descricao_tributacao_nacional.strip())
    if codigo.descricao_tributacao_municipal:
        parts.append(codigo.descricao_tributacao_municipal.strip())

    if not parts:
        return EMPTY_DISPLAY
    return truncate_with_ellipsis(" / ".join(parts), NT_LIMITS["tributacao_desc"])


def format_local_prestacao(local: LocalPrestacaoDanfse | None) -> str:
    if local is None:
        return EMPTY_DISPLAY

    if local.local_prestacao_texto:
        return truncate_with_ellipsis(local.local_prestacao_texto, NT_LIMITS["address"])

    if local.pais and local.pais.strip() not in {"", "105"}:
        return truncate_with_ellipsis(
            join_parts([local.municipio, local.pais], separator=" / "),
            NT_LIMITS["address"],
        )

    return format_municipio_uf(local.municipio, local.uf, pais=local.pais)


def format_local_incidencia(local: LocalIncidenciaIssqnDanfse | None) -> str:
    if local is None:
        return EMPTY_DISPLAY

    if local.local_incidencia_texto:
        return truncate_with_ellipsis(local.local_incidencia_texto, NT_LIMITS["address"])

    if local.pais and local.pais.strip() not in {"", "105"}:
        return truncate_with_ellipsis(
            join_parts([local.municipio, local.pais], separator=" / "),
            NT_LIMITS["address"],
        )

    return format_municipio_uf(local.municipio, local.uf, pais=local.pais)


def format_cst_classificacao(cst: str | None, classificacao: str | None) -> str:
    return join_parts([cst, classificacao], separator=" / ")


def format_exclusoes_reducoes_base(
    exclusoes: ExclusoesReducoesBaseCalculoIbsCbsDanfse | None,
) -> str:
    if exclusoes is None:
        return EMPTY_DISPLAY

    if exclusoes.valor_total_exclusoes_reducoes is not None:
        return format_money(exclusoes.valor_total_exclusoes_reducoes)

    total = Decimal("0")
    has_value = False
    for value in (
        exclusoes.desconto_incondicionado,
        exclusoes.valor_calculo_reembolso_repasse_ressarcimento,
        exclusoes.valor_issqn,
        exclusoes.valor_pis,
        exclusoes.valor_cofins,
    ):
        if value is not None:
            total += value
            has_value = True

    if not has_value:
        return EMPTY_DISPLAY
    return format_money(total)


def format_reducoes_aliquota_ibs(
    uf: Decimal | None,
    municipal: Decimal | None,
    cbs: Decimal | None,
) -> str:
    return format_percent_triple(uf, municipal, cbs)


def format_aliquotas_ibs(uf: Decimal | None, municipal: Decimal | None) -> str:
    left = format_percent(uf) if uf is not None else EMPTY_DISPLAY
    right = format_percent(municipal) if municipal is not None else EMPTY_DISPLAY
    return f"{left} / {right}"


def format_canhoto_numero_chave(numero_nfse: str | None, chave: str | None) -> str:
    return join_parts(
        [display_or_dash(numero_nfse), format_access_key(chave)],
        separator=" / ",
    )


def format_qr_code_url(chave: str | None) -> str:
    key = format_access_key(chave)
    if key == EMPTY_DISPLAY:
        return ""
    return f"{QR_CODE_BASE_URL}{key}"


def format_beneficio_municipal(
    tipo: str | None,
    *,
    valor_calculo: Decimal | None,
    valor_reducao_bc: Decimal | None,
) -> tuple[str, str]:
    tipo_text = display_or_dash(tipo)
    if valor_calculo is not None:
        return tipo_text, format_money(valor_calculo)
    if valor_reducao_bc is not None:
        return tipo_text, format_money(valor_reducao_bc)
    return tipo_text, EMPTY_DISPLAY


def format_deducoes_reducoes(
    valor_deducoes: Decimal | None,
    valor_calculo: Decimal | None,
    valor_reembolso: Decimal | None,
) -> str:
    if valor_deducoes is not None:
        return format_money(valor_deducoes)
    if valor_calculo is not None:
        return format_money(valor_calculo)
    if valor_reembolso is not None:
        return format_money(valor_reembolso)
    return EMPTY_DISPLAY


def format_suspensao_exigibilidade(tipo: str | None, numero_processo: str | None) -> str:
    return join_parts([tipo, numero_processo], separator=" / ")


def format_totais_aproximados_tributos(
    totais: TotaisAproximadosTributosDanfse | None,
) -> str:
    if totais is None:
        return EMPTY_DISPLAY

    if any(
        value is not None
        for value in (
            totais.valor_total_tributos_federais,
            totais.valor_total_tributos_estaduais,
            totais.valor_total_tributos_municipais,
        )
    ):
        return join_parts(
            [
                format_money(totais.valor_total_tributos_federais),
                format_money(totais.valor_total_tributos_estaduais),
                format_money(totais.valor_total_tributos_municipais),
            ],
            separator=" / ",
        )

    if any(
        value is not None
        for value in (
            totais.percentual_total_tributos_federais,
            totais.percentual_total_tributos_estaduais,
            totais.percentual_total_tributos_municipais,
        )
    ):
        return join_parts(
            [
                format_percent(totais.percentual_total_tributos_federais),
                format_percent(totais.percentual_total_tributos_estaduais),
                format_percent(totais.percentual_total_tributos_municipais),
            ],
            separator=" / ",
        )

    return EMPTY_DISPLAY


def format_informacoes_complementares(
    info: InformacoesComplementaresDanfse | None,
    *,
    competencia: date | None = None,
) -> tuple[str, str]:
    if info is None:
        return EMPTY_DISPLAY, EMPTY_DISPLAY

    parts: list[str] = []

    if info.informacoes_complementares:
        parts.append(info.informacoes_complementares.strip())

    if info.chave_nfse_substituida:
        parts.append(f"NFS-e substituída: {format_access_key(info.chave_nfse_substituida)}")

    if info.documento_referenciado:
        parts.append(f"Documento referenciado: {info.documento_referenciado.strip()}")

    if info.obra and info.obra.codigo_obra:
        parts.append(f"Obra: {info.obra.codigo_obra.strip()}")

    if info.imovel and info.imovel.inscricao_imobiliaria_fiscal:
        parts.append(f"Inscrição imobiliária fiscal: {info.imovel.inscricao_imobiliaria_fiscal.strip()}")

    if info.evento and info.evento.identificacao_atividade_evento:
        parts.append(f"Evento: {info.evento.identificacao_atividade_evento.strip()}")

    if info.documento_tecnico:
        parts.append(f"Documento técnico: {info.documento_tecnico.strip()}")

    if info.pedido:
        pedido_parts = join_parts(
            [info.pedido.numero_pedido, info.pedido.item_pedido],
            separator=" / ",
        )
        if pedido_parts != EMPTY_DISPLAY:
            parts.append(f"Pedido: {pedido_parts}")

    if info.outras_informacoes:
        parts.append(info.outras_informacoes.strip())

    if info.informacoes_administracao_tributaria_municipal:
        parts.append(info.informacoes_administracao_tributaria_municipal.strip())

    texto = " | ".join(parts) if parts else EMPTY_DISPLAY
    texto = truncate_with_ellipsis(texto, NT_LIMITS["info_compl"])

    totais = format_totais_aproximados_tributos(info.totais_aproximados_tributos)
    return texto, totais
