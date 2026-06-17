from __future__ import annotations

from collections.abc import Callable

from danfse.rules.formatting.primitives import EMPTY_DISPLAY
from danfse.rules.models.formatted import FormattedDanfse

ValueGetter = Callable[[FormattedDanfse], str | None]


def _dash(value: str | None) -> str:
    if value is None:
        return EMPTY_DISPLAY
    text = value.strip()
    return text if text else EMPTY_DISPLAY


def _party_attr(block: str, attr: str) -> ValueGetter:
    def getter(data: FormattedDanfse) -> str | None:
        party = getattr(data, block, None)
        if party is None:
            return None
        return getattr(party, attr, None)

    return getter


FIELD_VALUE_GETTERS: dict[str, ValueGetter] = {
    "cabecalho.municipio_emitente": lambda d: d.cabecalho.municipio_ambiente,
    "cabecalho.ambiente_gerador": lambda d: d.cabecalho.ambiente_gerador,
    "cabecalho.tipo_ambiente": lambda d: d.cabecalho.tipo_ambiente,
    "identificacao.chave_acesso": lambda d: d.identificacao.chave_acesso,
    "identificacao.numero_nfse": lambda d: d.identificacao.numero_nfse,
    "identificacao.competencia_nfse": lambda d: d.identificacao.competencia_nfse,
    "identificacao.data_hora_emissao_nfse": lambda d: d.identificacao.data_hora_emissao_nfse,
    "identificacao.numero_dps": lambda d: d.identificacao.numero_dps,
    "identificacao.serie_dps": lambda d: d.identificacao.serie_dps,
    "identificacao.data_hora_emissao_dps": lambda d: d.identificacao.data_hora_emissao_dps,
    "identificacao.emitente_nfse": lambda d: d.identificacao.emitente_nfse,
    "identificacao.situacao_nfse": lambda d: d.identificacao.situacao_nfse,
    "identificacao.finalidade_nfse": lambda d: d.identificacao.finalidade_nfse,
    "identificacao.qrcode": lambda d: d.identificacao.qr_code_url,
    "prestador.documento": _party_attr("prestador", "documento"),
    "prestador.inscricao_municipal": _party_attr("prestador", "inscricao_municipal"),
    "prestador.telefone": _party_attr("prestador", "telefone"),
    "prestador.nome": _party_attr("prestador", "nome"),
    "prestador.municipio_uf": _party_attr("prestador", "municipio_uf"),
    "prestador.codigo_ibge_cep": _party_attr("prestador", "codigo_ibge_cep"),
    "prestador.endereco": _party_attr("prestador", "endereco"),
    "prestador.email": _party_attr("prestador", "email"),
    "prestador.simples_nacional_competencia": _party_attr("prestador", "simples_nacional_competencia"),
    "prestador.regime_apuracao_tributaria_sn": _party_attr("prestador", "regime_apuracao_tributaria_sn"),
    "tomador.documento": _party_attr("tomador", "documento"),
    "tomador.inscricao_municipal": _party_attr("tomador", "inscricao_municipal"),
    "tomador.telefone": _party_attr("tomador", "telefone"),
    "tomador.nome": _party_attr("tomador", "nome"),
    "tomador.municipio_uf": _party_attr("tomador", "municipio_uf"),
    "tomador.codigo_ibge_cep": _party_attr("tomador", "codigo_ibge_cep"),
    "tomador.endereco": _party_attr("tomador", "endereco"),
    "tomador.email": _party_attr("tomador", "email"),
    "destinatario.documento": _party_attr("destinatario", "documento"),
    "destinatario.telefone": _party_attr("destinatario", "telefone"),
    "destinatario.nome": _party_attr("destinatario", "nome"),
    "destinatario.municipio_uf": _party_attr("destinatario", "municipio_uf"),
    "destinatario.codigo_ibge_cep": _party_attr("destinatario", "codigo_ibge_cep"),
    "destinatario.endereco": _party_attr("destinatario", "endereco"),
    "destinatario.email": _party_attr("destinatario", "email"),
    "intermediario.documento": _party_attr("intermediario", "documento"),
    "intermediario.inscricao_municipal": _party_attr("intermediario", "inscricao_municipal"),
    "intermediario.telefone": _party_attr("intermediario", "telefone"),
    "intermediario.nome": _party_attr("intermediario", "nome"),
    "intermediario.municipio_uf": _party_attr("intermediario", "municipio_uf"),
    "intermediario.codigo_ibge_cep": _party_attr("intermediario", "codigo_ibge_cep"),
    "intermediario.endereco": _party_attr("intermediario", "endereco"),
    "intermediario.email": _party_attr("intermediario", "email"),
    "servico.codigo_tributacao_nacional_municipal": lambda d: d.servico.codigo_tributacao,
    "servico.codigo_nbs": lambda d: d.servico.codigo_nbs,
    "servico.local_prestacao_uf_pais": lambda d: d.servico.local_prestacao,
    "servico.descricao_codigo_tributacao": lambda d: d.servico.descricao_tributacao,
    "servico.descricao_servico": lambda d: d.servico.descricao_servico,
    "tributacao_municipal.tipo_tributacao_issqn": lambda d: _section(d.tributacao_municipal, "tipo_tributacao_issqn"),
    "tributacao_municipal.local_incidencia_uf_pais": lambda d: _section(d.tributacao_municipal, "local_incidencia"),
    "tributacao_municipal.regime_especial_tributacao_issqn": lambda d: _section(
        d.tributacao_municipal, "regime_especial_tributacao_issqn",
    ),
    "tributacao_municipal.tipo_imunidade_issqn": lambda d: _section(d.tributacao_municipal, "tipo_imunidade_issqn"),
    "tributacao_municipal.suspensao_exigibilidade": lambda d: _section(d.tributacao_municipal, "suspensao_exigibilidade"),
    "tributacao_municipal.numero_processo_suspensao": lambda d: _section(
        d.tributacao_municipal, "numero_processo_suspensao",
    ),
    "tributacao_municipal.beneficio_municipal": lambda d: _section(d.tributacao_municipal, "beneficio_municipal"),
    "tributacao_municipal.calculo_bm": lambda d: _section(d.tributacao_municipal, "calculo_beneficio_municipal"),
    "tributacao_municipal.total_deducoes_reducoes": lambda d: _section(
        d.tributacao_municipal, "total_deducoes_reducoes",
    ),
    "tributacao_municipal.desconto_incondicionado": lambda d: _section(
        d.tributacao_municipal, "desconto_incondicionado",
    ),
    "tributacao_municipal.base_calculo_issqn": lambda d: _section(d.tributacao_municipal, "base_calculo_issqn"),
    "tributacao_municipal.aliquota_aplicada": lambda d: _section(d.tributacao_municipal, "aliquota_aplicada"),
    "tributacao_municipal.retencao_issqn": lambda d: _section(d.tributacao_municipal, "retencao_issqn"),
    "tributacao_municipal.valor_issqn_apurado": lambda d: _section(d.tributacao_municipal, "valor_issqn_apurado"),
    "tributacao_federal.valor_retencao_irrf": lambda d: _section(d.tributacao_federal, "valor_retencao_irrf"),
    "tributacao_federal.valor_retencao_contribuicao_previdenciaria": lambda d: _section(
        d.tributacao_federal, "valor_retencao_contribuicao_previdenciaria",
    ),
    "tributacao_federal.valor_retencao_csll": lambda d: _section(d.tributacao_federal, "valor_retencao_csll"),
    "tributacao_federal.valor_pis_debito_apuracao_propria": lambda d: _section(d.tributacao_federal, "valor_pis"),
    "tributacao_federal.valor_cofins_debito_apuracao_propria": lambda d: _section(d.tributacao_federal, "valor_cofins"),
    "tributacao_federal.tipo_retencao_pis_cofins": lambda d: _section(d.tributacao_federal, "tipo_retencao_pis_cofins"),
    "tributacao_ibs_cbs.cst_cclass_trib": lambda d: _section(d.tributacao_ibs_cbs, "cst_classificacao"),
    "tributacao_ibs_cbs.indicador_operacao_incidencia": lambda d: _section(
        d.tributacao_ibs_cbs, "indicador_operacao_incidencia",
    ),
    "tributacao_ibs_cbs.exclusoes_reducoes_base_calculo": lambda d: _section(
        d.tributacao_ibs_cbs, "exclusoes_reducoes_base_calculo",
    ),
    "tributacao_ibs_cbs.base_calculo_apos_exclusoes_reducoes": lambda d: _section(
        d.tributacao_ibs_cbs, "base_calculo_apos_exclusoes",
    ),
    "tributacao_ibs_cbs.reducao_aliquota_ibs_cbs": lambda d: _section(
        d.tributacao_ibs_cbs, "reducoes_aliquota_ibs_cbs",
    ),
    "tributacao_ibs_cbs.aliquota_ibs_uf_mun": lambda d: _section(d.tributacao_ibs_cbs, "aliquotas_ibs"),
    "tributacao_ibs_cbs.aliquota_efetiva_municipal_ibs": lambda d: _section(
        d.tributacao_ibs_cbs, "aliquota_efetiva_ibs_municipal",
    ),
    "tributacao_ibs_cbs.valor_apurado_municipal_ibs": lambda d: _section(d.tributacao_ibs_cbs, "valor_ibs_municipal"),
    "tributacao_ibs_cbs.aliquota_efetiva_estadual_ibs": lambda d: _section(
        d.tributacao_ibs_cbs, "aliquota_efetiva_ibs_uf",
    ),
    "tributacao_ibs_cbs.valor_apurado_estadual_ibs": lambda d: _section(d.tributacao_ibs_cbs, "valor_ibs_uf"),
    "tributacao_ibs_cbs.valor_total_ibs": lambda d: _section(d.tributacao_ibs_cbs, "valor_total_ibs"),
    "tributacao_ibs_cbs.aliquota_cbs": lambda d: _section(d.tributacao_ibs_cbs, "aliquota_cbs"),
    "tributacao_ibs_cbs.aliquota_efetiva_cbs": lambda d: _section(d.tributacao_ibs_cbs, "aliquota_efetiva_cbs"),
    "tributacao_ibs_cbs.valor_total_cbs": lambda d: _section(d.tributacao_ibs_cbs, "valor_total_cbs"),
    "totais.valor_operacao_servico": lambda d: _section(d.totais, "valor_operacao_servico"),
    "totais.desconto_incondicionado": lambda d: _section(d.totais, "desconto_incondicionado"),
    "totais.desconto_condicionado": lambda d: _section(d.totais, "desconto_condicionado"),
    "totais.total_retencoes_issqn_federais": lambda d: _section(d.totais, "total_retencoes"),
    "totais.valor_liquido_nfse": lambda d: _section(d.totais, "valor_liquido_nfse"),
    "totais.total_ibs_cbs": lambda d: _section(d.totais, "total_ibs_cbs"),
    "totais.valor_liquido_nfse_mais_ibs_cbs": lambda d: _section(d.totais, "valor_liquido_nfse_mais_ibs_cbs"),
    "informacoes_complementares.texto": lambda d: _section(d.informacoes_complementares, "texto"),
    "canhoto.data_cientificacao": lambda d: _section(d.canhoto, "data_cientificacao"),
    "canhoto.identificacao_assinatura": lambda d: _section(d.canhoto, "identificacao_assinatura"),
    "canhoto.numero_nfse_chave_nfse": lambda d: _section(d.canhoto, "numero_nfse_chave"),
}


def _section(section, attr: str) -> str | None:
    if section is None:
        return None
    return getattr(section, attr, None)


def resolve_field_value(key: str, data: FormattedDanfse) -> str:
    if key.endswith(".mensagem_nao_identificado") or key.endswith(".mensagem_igual_tomador"):
        block = key.split(".", 1)[0]
        party = getattr(data, block, None)
        if party is not None and party.bloco_texto:
            return party.bloco_texto
        return EMPTY_DISPLAY

    if key == "tributacao_municipal.mensagem_nao_sujeita_issqn":
        trib = data.tributacao_municipal
        if trib is not None and trib.bloco_texto:
            return trib.bloco_texto
        return EMPTY_DISPLAY

    getter = FIELD_VALUE_GETTERS.get(key)
    if getter is None:
        return EMPTY_DISPLAY
    return _dash(getter(data))
