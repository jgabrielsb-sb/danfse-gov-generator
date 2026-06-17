from __future__ import annotations

from danfse.domain.models import (
    DanfseData,
    PessoaDanfse,
    PrestadorDanfse,
    TributacaoFederalDanfse,
    TributacaoIbsCbsDanfse,
    TributacaoMunicipalDanfse,
)
from danfse.rules.formatting.composite import (
    format_aliquotas_ibs,
    format_beneficio_municipal,
    format_cabecalho_municipio,
    format_canhoto_numero_chave,
    format_codigo_ibge_cep,
    format_codigo_nbs,
    format_codigo_tributacao,
    format_cst_classificacao,
    format_deducoes_reducoes,
    format_descricao_tributacao,
    format_endereco,
    format_exclusoes_reducoes_base,
    format_informacoes_complementares,
    format_local_incidencia,
    format_local_prestacao,
    format_municipio_uf,
    format_qr_code_url,
    format_reducoes_aliquota_ibs,
    format_suspensao_exigibilidade,
)
from danfse.rules.catalog.field_specs import NT_LIMITS
from danfse.rules.catalog.xsd import XsdSchemaCatalog, get_default_catalog
from danfse.rules.formatting.descriptions import describe_field
from danfse.rules.models.formatted import (
    FormattedCabecalho,
    FormattedCanhoto,
    FormattedDanfse,
    FormattedDestinatario,
    FormattedIdentificacao,
    FormattedInformacoesComplementares,
    FormattedIntermediario,
    FormattedPrestador,
    FormattedServico,
    FormattedTomador,
    FormattedTotais,
    FormattedTributacaoFederal,
    FormattedTributacaoIbsCbs,
    FormattedTributacaoMunicipal,
    FormattedValoresServico,
)
from danfse.rules.formatting.primitives import (
    display_or_dash,
    format_access_key,
    format_date,
    format_datetime,
    format_documento_pessoa,
    format_money,
    format_percent,
    truncate_with_ellipsis,
)
from danfse.rules.formatting.suppression import (
    format_pis_cofins_retention_label,
    resolve_destinatario_bloco,
    resolve_homologacao_aviso,
    resolve_intermediario_bloco,
    resolve_tomador_bloco,
    resolve_tributacao_municipal_bloco,
    resolve_watermark,
    should_render_party_block,
    should_render_tributacao_municipal,
)


class DanfseFormatter:
    def __init__(self, catalog: XsdSchemaCatalog | None = None) -> None:
        self._catalog = catalog or get_default_catalog()

    def format(self, data: DanfseData) -> FormattedDanfse:
        codigo_servico = data.servico.codigo_servico if data.servico else None
        c_trib_nac = (
            codigo_servico.codigo_tributacao_nacional if codigo_servico is not None else None
        )
        competencia = (
            data.identificacao.competencia_nfse if data.identificacao is not None else None
        )

        cabecalho = self._format_cabecalho(data, c_trib_nac)
        identificacao = self._format_identificacao(data)
        prestador = self._format_prestador(data.prestador)
        tomador = self._format_tomador(data)
        destinatario = self._format_destinatario(data)
        intermediario = self._format_intermediario(data)
        servico = self._format_servico(data)
        valores_servico = self._format_valores_servico(data)
        tributacao_municipal = self._format_tributacao_municipal(data)
        tributacao_federal = self._format_tributacao_federal(data, competencia)
        tributacao_ibs_cbs = self._format_tributacao_ibs_cbs(data)
        totais = self._format_totais(data)
        informacoes_complementares = self._format_informacoes_complementares(data, competencia)
        canhoto = self._format_canhoto(data)

        return FormattedDanfse(
            cabecalho=cabecalho,
            identificacao=identificacao,
            prestador=prestador,
            tomador=tomador,
            destinatario=destinatario,
            intermediario=intermediario,
            servico=servico,
            valores_servico=valores_servico,
            tributacao_municipal=tributacao_municipal,
            tributacao_federal=tributacao_federal,
            tributacao_ibs_cbs=tributacao_ibs_cbs,
            totais=totais,
            informacoes_complementares=informacoes_complementares,
            canhoto=canhoto,
            watermark=resolve_watermark(data.status_visual),
        )

    def _describe(
        self,
        xsd_type: str,
        code: str | None,
        *,
        max_length: int | None = NT_LIMITS["enum_short"],
    ) -> str:
        return describe_field(
            xsd_type,
            code,
            catalog=self._catalog,
            max_length=max_length,
        )

    def _format_cabecalho(
        self,
        data: DanfseData,
        c_trib_nac: str | None,
    ) -> FormattedCabecalho:
        cab = data.cabecalho
        return FormattedCabecalho(
            municipio_ambiente=format_cabecalho_municipio(
                cab.municipio_emitente if cab else None,
                cab.uf_emitente if cab else None,
                codigo_tributacao_nacional=c_trib_nac,
            ),
            ambiente_gerador=self._describe(
                "TSAmbGeradorNFSe",
                cab.ambiente_gerador if cab else None,
            ),
            tipo_ambiente=self._describe(
                "TSTipoAmbiente",
                cab.tipo_ambiente if cab else None,
            ),
            homologacao_aviso=resolve_homologacao_aviso(data.status_visual),
        )

    def _format_identificacao(self, data: DanfseData) -> FormattedIdentificacao:
        ident = data.identificacao
        chave = format_access_key(ident.chave_acesso)
        return FormattedIdentificacao(
            chave_acesso=chave,
            numero_nfse=display_or_dash(ident.numero_nfse),
            competencia_nfse=format_date(ident.competencia_nfse),
            data_hora_emissao_nfse=format_datetime(ident.data_hora_emissao_nfse),
            numero_dps=display_or_dash(ident.numero_dps),
            serie_dps=display_or_dash(ident.serie_dps),
            data_hora_emissao_dps=format_datetime(ident.data_hora_emissao_dps),
            emitente_nfse=self._describe("TSEmitenteDPS", ident.emitente_nfse),
            situacao_nfse=self._describe("TStat", ident.situacao_nfse),
            finalidade_nfse=self._describe("TSFinNFSe", ident.finalidade_nfse),
            qr_code_url=format_qr_code_url(ident.chave_acesso),
        )

    def _format_pessoa_fields(self, pessoa: PessoaDanfse) -> dict[str, str]:
        endereco = pessoa.endereco
        return {
            "documento": format_documento_pessoa(pessoa.documento),
            "inscricao_municipal": display_or_dash(pessoa.inscricao_municipal),
            "telefone": display_or_dash(pessoa.telefone),
            "nome": truncate_with_ellipsis(pessoa.nome, NT_LIMITS["address"]),
            "municipio_uf": format_municipio_uf(
                endereco.municipio if endereco else None,
                endereco.uf if endereco else None,
                pais=endereco.pais if endereco else None,
            ),
            "codigo_ibge_cep": format_codigo_ibge_cep(endereco),
            "endereco": format_endereco(endereco),
            "email": display_or_dash(pessoa.email),
        }

    def _format_prestador(self, prestador: PrestadorDanfse) -> FormattedPrestador:
        fields = self._format_pessoa_fields(prestador)
        regime = prestador.regime_tributario
        return FormattedPrestador(
            **fields,
            simples_nacional_competencia=self._describe(
                "TSOpSimpNac",
                regime.simples_nacional_competencia if regime else None,
            ),
            regime_apuracao_tributaria_sn=self._describe(
                "TSRegimeApuracaoSimpNac",
                regime.regime_apuracao_tributaria_sn if regime else None,
                max_length=NT_LIMITS["address"],
            ),
            regime_especial_tributacao=self._describe(
                "TSRegEspTrib",
                regime.regime_especial_tributacao if regime else None,
            ),
        )

    def _format_tomador(self, data: DanfseData) -> FormattedTomador | None:
        bloco = resolve_tomador_bloco(data.status_visual)
        if not should_render_party_block(data.status_visual, "tomador"):
            return FormattedTomador(bloco_texto=bloco)
        if data.tomador is None:
            return FormattedTomador(bloco_texto=bloco)
        return FormattedTomador(
            **self._format_pessoa_fields(data.tomador),
            bloco_texto=bloco,
        )

    def _format_destinatario(self, data: DanfseData) -> FormattedDestinatario | None:
        bloco = resolve_destinatario_bloco(data.status_visual)
        if not should_render_party_block(data.status_visual, "destinatario"):
            return FormattedDestinatario(bloco_texto=bloco)
        if data.destinatario is None:
            return FormattedDestinatario(bloco_texto=bloco)
        return FormattedDestinatario(
            **self._format_pessoa_fields(data.destinatario),
            bloco_texto=bloco,
        )

    def _format_intermediario(self, data: DanfseData) -> FormattedIntermediario | None:
        bloco = resolve_intermediario_bloco(data.status_visual)
        if not should_render_party_block(data.status_visual, "intermediario"):
            return FormattedIntermediario(bloco_texto=bloco)
        if data.intermediario is None:
            return FormattedIntermediario(bloco_texto=bloco)
        return FormattedIntermediario(
            **self._format_pessoa_fields(data.intermediario),
            bloco_texto=bloco,
        )

    def _format_servico(self, data: DanfseData) -> FormattedServico:
        servico = data.servico
        codigo = servico.codigo_servico if servico else None
        return FormattedServico(
            codigo_tributacao=format_codigo_tributacao(codigo),
            codigo_nbs=format_codigo_nbs(codigo),
            local_prestacao=format_local_prestacao(
                servico.local_prestacao if servico else None,
            ),
            descricao_tributacao=format_descricao_tributacao(codigo),
            descricao_servico=truncate_with_ellipsis(
                servico.descricao_servico if servico else None,
                NT_LIMITS["servico_desc"],
            ),
        )

    def _format_valores_servico(self, data: DanfseData) -> FormattedValoresServico | None:
        valores = data.valores_servico
        if valores is None:
            return None
        return FormattedValoresServico(
            valor_servico=format_money(valores.valor_servico),
            desconto_incondicionado=format_money(valores.desconto_incondicionado),
            desconto_condicionado=format_money(valores.desconto_condicionado),
        )

    def _format_tributacao_municipal(
        self,
        data: DanfseData,
    ) -> FormattedTributacaoMunicipal | None:
        bloco = resolve_tributacao_municipal_bloco(data.status_visual)
        trib = data.tributacao_municipal
        if not should_render_tributacao_municipal(data):
            return FormattedTributacaoMunicipal(bloco_texto=bloco)

        if trib is None:
            return FormattedTributacaoMunicipal(bloco_texto=bloco)

        susp = trib.suspensao_exigibilidade
        benef = trib.beneficio_municipal
        ded = trib.deducoes_reducoes

        beneficio, calculo_beneficio = format_beneficio_municipal(
            self._describe("TSOpTipoBM", benef.tipo_beneficio_municipal if benef else None),
            valor_calculo=benef.valor_calculo_beneficio_municipal if benef else None,
            valor_reducao_bc=benef.valor_reducao_bc_beneficio_municipal if benef else None,
        )

        return FormattedTributacaoMunicipal(
            bloco_texto=bloco,
            tipo_tributacao_issqn=self._describe("TSTribISSQN", trib.tipo_tributacao_issqn),
            local_incidencia=format_local_incidencia(trib.local_incidencia),
            regime_especial_tributacao_issqn=self._describe(
                "TSRegEspTrib",
                trib.regime_especial_tributacao_issqn,
            ),
            tipo_imunidade_issqn=self._describe(
                "TSTipoImunidadeISSQN",
                trib.tipo_imunidade_issqn,
            ),
            suspensao_exigibilidade=self._describe(
                "TSOpExigSuspensa",
                susp.tipo_suspensao if susp else None,
            ),
            numero_processo_suspensao=display_or_dash(
                susp.numero_processo if susp else None,
            ),
            beneficio_municipal=beneficio,
            calculo_beneficio_municipal=calculo_beneficio,
            total_deducoes_reducoes=format_deducoes_reducoes(
                ded.valor_deducoes_reducoes if ded else None,
                ded.valor_calculo_deducoes_reducoes if ded else None,
                ded.valor_calculo_reembolso_repasse_ressarcimento if ded else None,
            ),
            desconto_incondicionado=format_money(trib.desconto_incondicionado),
            base_calculo_issqn=format_money(trib.base_calculo_issqn),
            aliquota_aplicada=format_percent(trib.aliquota_aplicada),
            retencao_issqn=self._describe("TSTipoRetISSQN", trib.retencao_issqn),
            valor_issqn_apurado=format_money(trib.valor_issqn_apurado),
        )

    def _format_tributacao_federal(
        self,
        data: DanfseData,
        competencia,
    ) -> FormattedTributacaoFederal | None:
        trib: TributacaoFederalDanfse | None = data.tributacao_federal
        if trib is None:
            return None

        label = self._describe("TSTipoRetPISCofins", trib.tipo_retencao_pis_cofins)
        return FormattedTributacaoFederal(
            valor_retencao_irrf=format_money(trib.valor_retencao_irrf),
            valor_retencao_contribuicao_previdenciaria=format_money(
                trib.valor_retencao_contribuicao_previdenciaria,
            ),
            valor_retencao_csll=format_money(trib.valor_retencao_csll),
            valor_pis=format_money(trib.valor_pis_debito_apuracao_propria),
            valor_cofins=format_money(trib.valor_cofins_debito_apuracao_propria),
            tipo_retencao_pis_cofins=format_pis_cofins_retention_label(
                trib.tipo_retencao_pis_cofins,
                competencia=competencia,
                label=label,
            ),
        )

    def _format_tributacao_ibs_cbs(
        self,
        data: DanfseData,
    ) -> FormattedTributacaoIbsCbs | None:
        trib: TributacaoIbsCbsDanfse | None = data.tributacao_ibs_cbs
        if trib is None:
            return None

        classificacao = trib.classificacao_tributaria
        incidencia = trib.incidencia
        ibs_uf = trib.ibs_uf
        ibs_mun = trib.ibs_municipal
        cbs = trib.cbs

        return FormattedTributacaoIbsCbs(
            cst_classificacao=format_cst_classificacao(
                classificacao.cst if classificacao else None,
                classificacao.codigo_classificacao_tributaria if classificacao else None,
            ),
            indicador_operacao_incidencia=display_or_dash(
                incidencia.indicador_operacao if incidencia else None,
            ),
            exclusoes_reducoes_base_calculo=format_exclusoes_reducoes_base(
                trib.exclusoes_reducoes_base_calculo,
            ),
            base_calculo_apos_exclusoes=format_money(
                trib.base_calculo_apos_exclusoes_reducoes,
            ),
            reducoes_aliquota_ibs_cbs=format_reducoes_aliquota_ibs(
                ibs_uf.reducao_aliquota_ibs_uf if ibs_uf else None,
                ibs_mun.reducao_aliquota_ibs_municipal if ibs_mun else None,
                cbs.reducao_aliquota_cbs if cbs else None,
            ),
            aliquotas_ibs=format_aliquotas_ibs(
                ibs_uf.aliquota_ibs_uf if ibs_uf else None,
                ibs_mun.aliquota_ibs_municipal if ibs_mun else None,
            ),
            aliquota_efetiva_ibs_municipal=format_percent(
                ibs_mun.aliquota_efetiva_ibs_municipal if ibs_mun else None,
            ),
            valor_ibs_municipal=format_money(
                ibs_mun.valor_ibs_municipal if ibs_mun else None,
            ),
            aliquota_efetiva_ibs_uf=format_percent(
                ibs_uf.aliquota_efetiva_ibs_uf if ibs_uf else None,
            ),
            valor_ibs_uf=format_money(ibs_uf.valor_ibs_uf if ibs_uf else None),
            valor_total_ibs=format_money(trib.valor_total_ibs),
            aliquota_cbs=format_percent(cbs.aliquota_cbs if cbs else None),
            aliquota_efetiva_cbs=format_percent(cbs.aliquota_efetiva_cbs if cbs else None),
            valor_total_cbs=format_money(trib.valor_total_cbs),
        )

    def _format_totais(self, data: DanfseData) -> FormattedTotais | None:
        totais = data.totais
        if totais is None:
            return None
        return FormattedTotais(
            valor_operacao_servico=format_money(totais.valor_operacao_servico),
            desconto_incondicionado=format_money(totais.desconto_incondicionado),
            desconto_condicionado=format_money(totais.desconto_condicionado),
            total_retencoes=format_money(totais.total_retencoes_issqn_federais),
            valor_liquido_nfse=format_money(totais.valor_liquido_nfse),
            total_ibs_cbs=format_money(totais.total_ibs_cbs),
            valor_liquido_nfse_mais_ibs_cbs=format_money(
                totais.valor_liquido_nfse_mais_ibs_cbs,
            ),
        )

    def _format_informacoes_complementares(
        self,
        data: DanfseData,
        competencia,
    ) -> FormattedInformacoesComplementares | None:
        info = data.informacoes_complementares
        if info is None:
            return None
        texto, totais = format_informacoes_complementares(info, competencia=competencia)
        return FormattedInformacoesComplementares(
            texto=texto,
            totais_aproximados_tributos=totais,
        )

    def _format_canhoto(self, data: DanfseData) -> FormattedCanhoto | None:
        canhoto = data.canhoto
        if canhoto is None:
            return None
        return FormattedCanhoto(
            data_cientificacao=format_date(canhoto.data_cientificacao),
            identificacao_assinatura=display_or_dash(canhoto.identificacao_assinatura),
            numero_nfse_chave=format_canhoto_numero_chave(
                canhoto.numero_nfse,
                canhoto.chave_acesso,
            ),
        )
