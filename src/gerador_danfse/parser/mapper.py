from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

from lxml import etree
from pydantic import BaseModel

from gerador_danfse.domain.models import (
    BeneficioMunicipalDanfse,
    CabecalhoDanfse,
    CanhotoDanfse,
    CbsDanfse,
    ClassificacaoTributariaIbsCbsDanfse,
    CodigoServicoDanfse,
    DanfseData,
    DeducoesReducoesDanfse,
    DestinatarioDanfse,
    DocumentoPessoaDanfse,
    EnderecoDanfse,
    EventoDanfse,
    ExclusoesReducoesBaseCalculoIbsCbsDanfse,
    IbsMunicipalDanfse,
    IbsUfDanfse,
    ImovelDanfse,
    IncidenciaIbsCbsDanfse,
    InformacoesComplementaresDanfse,
    IdentificacaoNfseDanfse,
    IntermediarioDanfse,
    LocalIncidenciaIssqnDanfse,
    LocalPrestacaoDanfse,
    ObraDanfse,
    PedidoDanfse,
    PessoaDanfse,
    PrestadorDanfse,
    RegimeTributarioPrestadorDanfse,
    ServicoPrestadoDanfse,
    StatusVisualDanfse,
    SuspensaoExigibilidadeIssqnDanfse,
    TomadorDanfse,
    TotaisAproximadosTributosDanfse,
    TotaisDanfse,
    TributacaoFederalDanfse,
    TributacaoIbsCbsDanfse,
    TributacaoMunicipalDanfse,
    ValoresServicoDanfse,
)
from gerador_danfse.parser.xml_parser import DanfseParserError, XmlDocument, XmlNavigator


class MissingRequiredNodeError(DanfseParserError):
    """Nó obrigatório não encontrado no XML."""


class InvalidFieldValueError(DanfseParserError):
    """Valor de campo incompatível com o tipo esperado."""


@dataclass(frozen=True)
class DanfseMapperConfig:
    """
    Configurações do mapeamento XML -> domínio.

    A NT informa que NFS-e cancelada/substituída deve receber marca d'água,
    mas a tabela da NT não define os códigos de cStat. Por isso, os conjuntos
    abaixo ficam configuráveis.
    """

    include_canhoto: bool = False
    cancelled_status_codes: frozenset[str] = frozenset()
    replaced_status_codes: frozenset[str] = frozenset()


class DanfseMapper:
    """
    Mapeia XML NFS-e nacional para DanfseData.

    Concentra os caminhos/tags do leiaute; a navegação genérica fica em XmlNavigator.
    """

    def __init__(self, config: DanfseMapperConfig | None = None) -> None:
        self.config = config or DanfseMapperConfig()

    def map_to_domain(self, doc: XmlDocument) -> DanfseData:
        root = XmlNavigator(doc.root)

        inf_nfse_el = self._require_node(self._find_inf_nfse(root), "infNFSe")
        inf_dps_el = self._require_node(
            root.at("DPS", "infDPS").node or root.find("infDPS").node,
            "DPS/infDPS",
        )

        nfse = XmlNavigator(inf_nfse_el)
        dps = XmlNavigator(inf_dps_el)

        prest_node = self._require_node(dps.at("prest").node, "infDPS/prest")
        serv_node = self._require_node(dps.at("serv").node, "infDPS/serv")

        identificacao = self._map_identificacao(nfse, dps)
        cabecalho = self._map_cabecalho(nfse, dps)

        prestador = self._map_prestador(XmlNavigator(prest_node), nfse.at("emit"), nfse)

        tomador = self._map_optional_person(dps.at("toma").node, TomadorDanfse)

        ibscbs_dps = dps.at("IBSCBS")
        destinatario = self._map_optional_person(
            ibscbs_dps.at("dest").node if ibscbs_dps.node is not None else None,
            DestinatarioDanfse,
        )

        intermediario = self._map_optional_person(dps.at("interm").node, IntermediarioDanfse)

        servico = self._map_servico(nfse, dps, XmlNavigator(serv_node))
        valores_servico = self._map_valores_servico(dps)

        tributacao_municipal = self._map_tributacao_municipal(nfse, dps)
        tributacao_federal = self._map_tributacao_federal(dps)
        tributacao_ibs_cbs = self._map_tributacao_ibs_cbs(nfse, dps)
        totais = self._map_totais(nfse, dps, tributacao_ibs_cbs)
        informacoes_complementares = self._map_informacoes_complementares(nfse, dps)

        canhoto = self._map_canhoto(identificacao) if self.config.include_canhoto else None

        status_visual = self._map_status_visual(
            identificacao=identificacao,
            cabecalho=cabecalho,
            tomador=tomador,
            destinatario=destinatario,
            intermediario=intermediario,
            tributacao_municipal=tributacao_municipal,
        )

        return DanfseData(
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
            status_visual=status_visual,
        )

    # ============================================================
    # Root discovery
    # ============================================================

    def _find_inf_nfse(self, root: XmlNavigator) -> etree._Element | None:
        if root.local_name == "infNFSe":
            return root.node

        if root.local_name == "NFSe":
            return root.at("infNFSe").node

        return root.find("infNFSe").node

    def _require_node(self, node: etree._Element | None, label: str) -> etree._Element:
        if node is None:
            raise MissingRequiredNodeError(f"Nó {label} não encontrado no XML.")
        return node

    # ============================================================
    # Main blocks
    # ============================================================

    def _map_cabecalho(
        self,
        nfse: XmlNavigator,
        dps: XmlNavigator,
    ) -> CabecalhoDanfse | None:
        ender_nac = nfse.at("emit", "enderNac")

        cabecalho = CabecalhoDanfse(
            municipio_emitente=(
                nfse.text("xLocEmi")
                or ender_nac.text("xMun")
                or ender_nac.text("xCidade")
            ),
            uf_emitente=ender_nac.text("UF"),
            ambiente_gerador=nfse.text("ambGer"),
            tipo_ambiente=dps.text("tpAmb"),
        )

        return self._none_if_empty(cabecalho)

    def _map_identificacao(
        self,
        nfse: XmlNavigator,
        dps: XmlNavigator,
    ) -> IdentificacaoNfseDanfse:
        access_key = nfse.attr("Id") or nfse.attr("id")

        return IdentificacaoNfseDanfse(
            chave_acesso=self._normalize_access_key(access_key),
            numero_nfse=nfse.text("nNFSe"),
            competencia_nfse=self._date(dps.text("dCompet")),
            data_hora_emissao_nfse=self._datetime(nfse.text("dhProc")),
            numero_dps=dps.text("nDPS"),
            serie_dps=dps.text("serie"),
            data_hora_emissao_dps=self._datetime(dps.text("dhEmi")),
            emitente_nfse=dps.text("tpEmit"),
            situacao_nfse=nfse.text("cStat"),
            finalidade_nfse=dps.find("IBSCBS", "finNFSe").value(),
        )

    def _map_prestador(
        self,
        prest: XmlNavigator,
        emit: XmlNavigator,
        nfse: XmlNavigator,
    ) -> PrestadorDanfse:
        base = self._map_pessoa(prest, PrestadorDanfse)

        reg_trib = prest.at("regTrib")
        regime = RegimeTributarioPrestadorDanfse(
            simples_nacional_competencia=reg_trib.text("opSimpNac"),
            regime_apuracao_tributaria_sn=reg_trib.text("regApTribSN"),
            regime_especial_tributacao=reg_trib.text("regEspTrib"),
        )

        prestador = base.model_copy(
            update={
                "regime_tributario": self._none_if_empty(regime),
            },
        )
        prestador = self._enrich_prestador_from_emit(prestador, emit, nfse)
        return prestador

    def _enrich_prestador_from_emit(
        self,
        prestador: PrestadorDanfse,
        emit: XmlNavigator,
        nfse: XmlNavigator,
    ) -> PrestadorDanfse:
        if emit.node is None:
            return prestador

        emit_pessoa = self._map_pessoa(emit, PrestadorDanfse)
        updates: dict[str, Any] = {}

        if not prestador.nome and emit_pessoa.nome:
            updates["nome"] = emit_pessoa.nome
        if not prestador.telefone and emit_pessoa.telefone:
            updates["telefone"] = emit_pessoa.telefone
        if not prestador.email and emit_pessoa.email:
            updates["email"] = emit_pessoa.email
        if not prestador.inscricao_municipal and emit_pessoa.inscricao_municipal:
            updates["inscricao_municipal"] = emit_pessoa.inscricao_municipal
        if prestador.documento is None and emit_pessoa.documento is not None:
            updates["documento"] = emit_pessoa.documento
        if prestador.endereco is None and emit_pessoa.endereco is not None:
            updates["endereco"] = emit_pessoa.endereco

        prestador = prestador.model_copy(update=updates) if updates else prestador

        if prestador.endereco is not None and not prestador.endereco.municipio:
            municipio = nfse.text("xLocEmi")
            if municipio:
                prestador = prestador.model_copy(
                    update={
                        "endereco": prestador.endereco.model_copy(
                            update={"municipio": municipio},
                        ),
                    },
                )

        return prestador

    def _map_optional_person(
        self,
        node: etree._Element | None,
        model_cls: type[PessoaDanfse],
    ) -> Any | None:
        if node is None:
            return None

        pessoa = self._map_pessoa(XmlNavigator(node), model_cls)
        return self._none_if_empty(pessoa)

    def _map_pessoa(
        self,
        person: XmlNavigator,
        model_cls: type[PessoaDanfse],
    ) -> Any:
        documento = DocumentoPessoaDanfse(
            cnpj=person.text("CNPJ"),
            cpf=person.text("CPF"),
            nif=person.text("NIF"),
        )

        endereco = self._map_endereco(person.at("end"))
        if endereco is None:
            endereco = self._map_endereco(person.at("enderNac"))

        return model_cls(
            documento=self._none_if_empty(documento),
            inscricao_municipal=person.text("IM"),
            telefone=person.text("fone"),
            nome=person.text("xNome"),
            endereco=endereco,
            email=person.text("email"),
        )

    def _map_endereco(self, end: XmlNavigator) -> EnderecoDanfse | None:
        if end.node is None:
            return None

        if end.local_name == "enderNac":
            end_nac = end
            end_ext = XmlNavigator(None)
            outer = end
        else:
            end_nac = end.at("endNac")
            end_ext = end.at("endExt")
            outer = end

        endereco = EnderecoDanfse(
            codigo_municipio=end_nac.text("cMun") or end_ext.text("cMun"),
            municipio=(
                end_nac.text("xMun")
                or end_ext.text("xCidade")
                or end_ext.text("xMun")
            ),
            uf=end_nac.text("UF") or end_ext.text("UF"),
            pais=end_ext.text("xPais") or end_ext.text("cPais"),
            cep=end_nac.text("CEP"),
            codigo_enderecamento_postal_exterior=end_ext.text("cEndPost"),
            logradouro=outer.text("xLgr"),
            numero=outer.text("nro"),
            complemento=outer.text("xCpl"),
            bairro=outer.text("xBairro"),
        )

        return self._none_if_empty(endereco)

    def _map_servico(
        self,
        nfse: XmlNavigator,
        dps: XmlNavigator,
        serv: XmlNavigator,
    ) -> ServicoPrestadoDanfse:
        c_serv = serv.at("cServ")
        loc_prest = serv.at("locPrest")

        codigo_servico = CodigoServicoDanfse(
            codigo_tributacao_nacional=c_serv.text("cTribNac") or nfse.text("cTribNac"),
            codigo_tributacao_municipal=c_serv.text("cTribMun") or nfse.text("cTribMun"),
            descricao_tributacao_nacional=c_serv.text("xTribNac") or nfse.text("xTribNac"),
            descricao_tributacao_municipal=c_serv.text("xTribMun") or nfse.text("xTribMun"),
            codigo_nbs=c_serv.text("cNBS"),
        )

        local_prestacao = LocalPrestacaoDanfse(
            codigo_municipio=loc_prest.text("cLocPrestacao") or loc_prest.text("cMun"),
            municipio=loc_prest.text("xLocPrestacao") or nfse.text("xLocPrestacao"),
            uf=loc_prest.text("UF") or nfse.text("UF"),
            pais=loc_prest.text("cPaisPrestacao") or nfse.text("cPaisPrestacao"),
            local_prestacao_texto=loc_prest.text("xLocPrestacao") or nfse.text("xLocPrestacao"),
            codigo_pais_prestacao=loc_prest.text("cPaisPrestacao"),
        )

        return ServicoPrestadoDanfse(
            codigo_servico=self._none_if_empty(codigo_servico),
            local_prestacao=self._none_if_empty(local_prestacao),
            descricao_servico=c_serv.text("xDescServ"),
        )

    def _map_valores_servico(self, dps: XmlNavigator) -> ValoresServicoDanfse | None:
        valores = dps.at("valores")
        serv_prest = valores.at("vServPrest")
        desc = valores.at("vDescCondIncond")

        model = ValoresServicoDanfse(
            valor_servico=self._decimal(serv_prest.text("vServ")),
            desconto_incondicionado=self._decimal(desc.text("vDescIncond")),
            desconto_condicionado=self._decimal(desc.text("vDescCond")),
        )

        return self._none_if_empty(model)

    # ============================================================
    # Tributação Municipal ISSQN
    # ============================================================

    def _map_tributacao_municipal(
        self,
        nfse: XmlNavigator,
        dps: XmlNavigator,
    ) -> TributacaoMunicipalDanfse | None:
        valores_dps = dps.at("valores")
        trib_mun = valores_dps.at("trib", "tribMun")

        if trib_mun.node is None:
            return None

        prest = dps.at("prest")
        reg_trib = prest.at("regTrib")
        valores_nfse = nfse.at("valores")
        ibscbs_nfse = nfse.at("IBSCBS")
        ibscbs_valores = ibscbs_nfse.at("valores")
        desc = valores_dps.at("vDescCondIncond")

        local_incidencia = LocalIncidenciaIssqnDanfse(
            codigo_municipio=trib_mun.text("cMunIncid"),
            municipio=nfse.text("xLocIncid") or trib_mun.text("xLocIncid"),
            uf=trib_mun.text("UF"),
            pais=trib_mun.text("cPaisResult"),
            local_incidencia_texto=nfse.text("xLocIncid") or trib_mun.text("xLocIncid"),
            codigo_pais_resultado=trib_mun.text("cPaisResult"),
        )

        exig_susp = trib_mun.at("exigSusp")
        suspensao = SuspensaoExigibilidadeIssqnDanfse(
            tipo_suspensao=exig_susp.text("tpSusp"),
            numero_processo=exig_susp.text("nProcesso"),
        )

        bm = trib_mun.at("BM")
        beneficio = BeneficioMunicipalDanfse(
            tipo_beneficio_municipal=valores_nfse.text("tpBM"),
            valor_calculo_beneficio_municipal=self._decimal(valores_nfse.text("vCalcBM")),
            valor_reducao_bc_beneficio_municipal=self._decimal(bm.text("vRedBCBM")),
        )

        v_ded_red = valores_dps.at("vDedRed")
        deducoes = DeducoesReducoesDanfse(
            valor_deducoes_reducoes=self._decimal(v_ded_red.text("vDR")),
            valor_calculo_deducoes_reducoes=self._decimal(valores_nfse.text("vCalcDR")),
            valor_calculo_reembolso_repasse_ressarcimento=self._decimal(
                ibscbs_valores.text("vCalcReeRepRes"),
            ),
        )

        model = TributacaoMunicipalDanfse(
            tipo_tributacao_issqn=trib_mun.text("tribISSQN"),
            local_incidencia=self._none_if_empty(local_incidencia),
            regime_especial_tributacao_issqn=reg_trib.text("regEspTrib"),
            tipo_imunidade_issqn=trib_mun.text("tpImunidade"),
            suspensao_exigibilidade=self._none_if_empty(suspensao),
            beneficio_municipal=self._none_if_empty(beneficio),
            deducoes_reducoes=self._none_if_empty(deducoes),
            desconto_incondicionado=self._decimal(desc.text("vDescIncond")),
            base_calculo_issqn=self._decimal(valores_nfse.text("vBC")),
            aliquota_aplicada=self._decimal(valores_nfse.text("pAliqAplic")),
            retencao_issqn=trib_mun.text("tpRetISSQN"),
            valor_issqn_apurado=self._decimal(valores_nfse.text("vISSQN")),
            operacao_sujeita_issqn=True,
        )

        return self._none_if_empty(model)

    # ============================================================
    # Tributação Federal
    # ============================================================

    def _map_tributacao_federal(self, dps: XmlNavigator) -> TributacaoFederalDanfse | None:
        trib_fed = dps.at("valores", "trib", "tribFed")
        if trib_fed.node is None:
            return None

        piscofins = trib_fed.at("piscofins")

        return TributacaoFederalDanfse(
            valor_retencao_irrf=self._decimal(trib_fed.text("vRetIRRF")),
            valor_retencao_contribuicao_previdenciaria=self._decimal(trib_fed.text("vRetCP")),
            valor_retencao_csll=self._decimal(trib_fed.text("vRetCSLL")),
            valor_pis_debito_apuracao_propria=self._decimal(piscofins.text("vPis")),
            valor_cofins_debito_apuracao_propria=self._decimal(piscofins.text("vCofins")),
            tipo_retencao_pis_cofins=piscofins.text("tpRetPisCofins"),
        )

    # ============================================================
    # IBS / CBS
    # ============================================================

    def _map_tributacao_ibs_cbs(
        self,
        nfse: XmlNavigator,
        dps: XmlNavigator,
    ) -> TributacaoIbsCbsDanfse | None:
        ibscbs_dps = dps.at("IBSCBS")
        ibscbs_nfse = nfse.at("IBSCBS")

        if ibscbs_dps.node is None and ibscbs_nfse.node is None:
            return None

        dps_valores = ibscbs_dps.at("valores")
        g_ibs_cbs = dps_valores.at("trib", "gIBSCBS")

        nfse_valores = ibscbs_nfse.at("valores")
        nfse_uf = nfse_valores.at("uf")
        nfse_mun = nfse_valores.at("mun")
        nfse_fed = nfse_valores.at("fed")

        tot_cibs = ibscbs_nfse.at("totCIBS")
        g_ibs = tot_cibs.at("gIBS")
        g_ibs_mun_tot = g_ibs.at("gIBSMunTot")
        g_ibs_uf_tot = g_ibs.at("gIBSUFTot")
        g_cbs = tot_cibs.at("gCBS")

        valores_dps = dps.at("valores")
        desc = valores_dps.at("vDescCondIncond")
        piscofins = valores_dps.at("trib", "tribFed", "piscofins")
        valores_nfse = nfse.at("valores")

        v_desc_incond = self._decimal(desc.text("vDescIncond"))
        v_calc_ree = self._decimal(nfse_valores.text("vCalcReeRepRes"))
        v_issqn = self._decimal(valores_nfse.text("vISSQN"))
        v_pis = self._decimal(piscofins.text("vPis") or piscofins.text("vPIS"))
        v_cofins = self._decimal(piscofins.text("vCofins") or piscofins.text("vCOFINS"))

        exclusoes = ExclusoesReducoesBaseCalculoIbsCbsDanfse(
            desconto_incondicionado=v_desc_incond,
            valor_calculo_reembolso_repasse_ressarcimento=v_calc_ree,
            valor_issqn=v_issqn,
            valor_pis=v_pis,
            valor_cofins=v_cofins,
            valor_total_exclusoes_reducoes=self._sum_decimals(
                v_desc_incond,
                v_calc_ree,
                v_issqn,
                v_pis,
                v_cofins,
            ),
        )

        classificacao = ClassificacaoTributariaIbsCbsDanfse(
            cst=g_ibs_cbs.text("CST"),
            codigo_classificacao_tributaria=g_ibs_cbs.text("cClassTrib"),
        )

        incidencia = IncidenciaIbsCbsDanfse(
            indicador_operacao=ibscbs_dps.text("cIndOp"),
            codigo_localidade_incidencia=(
                ibscbs_nfse.text("cLocalidadeIncid") or ibscbs_dps.text("cLocalidadeIncid")
            ),
            localidade_incidencia=(
                ibscbs_nfse.text("xLocalidadeIncid") or ibscbs_dps.text("xLocalidadeIncid")
            ),
            uf_incidencia=ibscbs_nfse.text("UF") or ibscbs_dps.text("UF"),
        )

        ibs_uf = IbsUfDanfse(
            reducao_aliquota_ibs_uf=self._decimal(nfse_uf.text("pRedAliqUF")),
            aliquota_ibs_uf=self._decimal(nfse_uf.text("pIBSUF")),
            aliquota_efetiva_ibs_uf=self._decimal(nfse_uf.text("pAliqEfetUF")),
            valor_ibs_uf=self._decimal(g_ibs_uf_tot.text("vIBSUF")),
        )

        ibs_mun = IbsMunicipalDanfse(
            reducao_aliquota_ibs_municipal=self._decimal(nfse_mun.text("pRedAliqMun")),
            aliquota_ibs_municipal=self._decimal(nfse_mun.text("pIBSMun")),
            aliquota_efetiva_ibs_municipal=self._decimal(nfse_mun.text("pAliqEfetMun")),
            valor_ibs_municipal=self._decimal(g_ibs_mun_tot.text("vIBSMun")),
        )

        cbs = CbsDanfse(
            reducao_aliquota_cbs=self._decimal(nfse_fed.text("pRedAliqCBS")),
            aliquota_cbs=self._decimal(nfse_fed.text("pCBS")),
            aliquota_efetiva_cbs=self._decimal(nfse_fed.text("pAliqEfetCBS")),
            valor_cbs=self._decimal(g_cbs.text("vCBS")),
        )

        model = TributacaoIbsCbsDanfse(
            classificacao_tributaria=self._none_if_empty(classificacao),
            incidencia=self._none_if_empty(incidencia),
            exclusoes_reducoes_base_calculo=self._none_if_empty(exclusoes),
            base_calculo_apos_exclusoes_reducoes=self._decimal(nfse_valores.text("vBC")),
            ibs_uf=self._none_if_empty(ibs_uf),
            ibs_municipal=self._none_if_empty(ibs_mun),
            cbs=self._none_if_empty(cbs),
            valor_total_ibs=self._decimal(g_ibs.text("vIBSTot")),
            valor_total_cbs=self._decimal(g_cbs.text("vCBS")),
        )

        return self._none_if_empty(model)

    # ============================================================
    # Totais
    # ============================================================

    def _map_totais(
        self,
        nfse: XmlNavigator,
        dps: XmlNavigator,
        tributacao_ibs_cbs: TributacaoIbsCbsDanfse | None,
    ) -> TotaisDanfse | None:
        valores_dps = dps.at("valores")
        serv_prest = valores_dps.at("vServPrest")
        desc = valores_dps.at("vDescCondIncond")
        valores_nfse = nfse.at("valores")
        tot_cibs = nfse.at("IBSCBS", "totCIBS")

        v_ibs = tributacao_ibs_cbs.valor_total_ibs if tributacao_ibs_cbs is not None else None
        v_cbs = tributacao_ibs_cbs.valor_total_cbs if tributacao_ibs_cbs is not None else None

        model = TotaisDanfse(
            valor_operacao_servico=self._decimal(serv_prest.text("vServ")),
            desconto_incondicionado=self._decimal(desc.text("vDescIncond")),
            desconto_condicionado=self._decimal(desc.text("vDescCond")),
            total_retencoes_issqn_federais=self._decimal(valores_nfse.text("vTotalRet")),
            valor_liquido_nfse=self._decimal(valores_nfse.text("vLiq")),
            total_ibs_cbs=self._sum_decimals(v_ibs, v_cbs),
            valor_liquido_nfse_mais_ibs_cbs=self._decimal(tot_cibs.text("vTotNF")),
        )

        return self._none_if_empty(model)

    # ============================================================
    # Informações complementares
    # ============================================================

    def _map_informacoes_complementares(
        self,
        nfse: XmlNavigator,
        dps: XmlNavigator,
    ) -> InformacoesComplementaresDanfse | None:
        serv = dps.at("serv")
        info_compl = serv.at("infoCompl")
        subst = dps.at("subst")
        obra_node = serv.at("obra")
        atv_evento = serv.at("atvEvento")
        imovel_node = dps.at("IBSCBS", "imovel")

        tot_trib = dps.at("valores", "trib", "totTrib")
        v_tot_trib = tot_trib.at("vTotTrib")
        p_tot_trib = tot_trib.at("pTotTrib")

        obra = ObraDanfse(codigo_obra=obra_node.text("cObra"))
        imovel = ImovelDanfse(inscricao_imobiliaria_fiscal=imovel_node.text("inscImobFisc"))
        evento = EventoDanfse(identificacao_atividade_evento=atv_evento.text("idAtvEvt"))
        pedido = PedidoDanfse(
            numero_pedido=info_compl.text("xPed"),
            item_pedido=info_compl.at("gItemPed").text("xItemPed"),
        )

        totais_aproximados = TotaisAproximadosTributosDanfse(
            valor_total_tributos_federais=self._decimal(v_tot_trib.text("vTotTribFed")),
            valor_total_tributos_estaduais=self._decimal(v_tot_trib.text("vTotTribEst")),
            valor_total_tributos_municipais=self._decimal(v_tot_trib.text("vTotTribMun")),
            percentual_total_tributos_federais=self._decimal(p_tot_trib.text("pTotTribFed")),
            percentual_total_tributos_estaduais=self._decimal(p_tot_trib.text("pTotTribEst")),
            percentual_total_tributos_municipais=self._decimal(p_tot_trib.text("pTotTribMun")),
        )

        model = InformacoesComplementaresDanfse(
            informacoes_complementares=info_compl.text("xInfComp"),
            chave_nfse_substituida=subst.text("chSubstda"),
            documento_referenciado=info_compl.text("docRef"),
            obra=self._none_if_empty(obra),
            imovel=self._none_if_empty(imovel),
            evento=self._none_if_empty(evento),
            documento_tecnico=info_compl.text("idDocTec"),
            pedido=self._none_if_empty(pedido),
            outras_informacoes=nfse.text("xOutInf"),
            informacoes_administracao_tributaria_municipal=None,
            totais_aproximados_tributos=self._none_if_empty(totais_aproximados),
        )

        return self._none_if_empty(model)

    # ============================================================
    # Canhoto / Status
    # ============================================================

    def _map_canhoto(self, identificacao: IdentificacaoNfseDanfse) -> CanhotoDanfse:
        return CanhotoDanfse(
            data_cientificacao=None,
            identificacao_assinatura=None,
            numero_nfse=identificacao.numero_nfse,
            chave_acesso=identificacao.chave_acesso,
        )

    def _map_status_visual(
        self,
        identificacao: IdentificacaoNfseDanfse,
        cabecalho: CabecalhoDanfse | None,
        tomador: TomadorDanfse | None,
        destinatario: DestinatarioDanfse | None,
        intermediario: IntermediarioDanfse | None,
        tributacao_municipal: TributacaoMunicipalDanfse | None,
    ) -> StatusVisualDanfse:
        cstat = identificacao.situacao_nfse

        return StatusVisualDanfse(
            is_homologacao=cabecalho is not None and cabecalho.tipo_ambiente == "2",
            is_cancelada=cstat in self.config.cancelled_status_codes if cstat is not None else False,
            is_substituida=cstat in self.config.replaced_status_codes if cstat is not None else False,
            tomador_nao_identificado=tomador is None,
            destinatario_nao_identificado=destinatario is None,
            destinatario_igual_tomador=self._same_person(tomador, destinatario),
            intermediario_nao_identificado=intermediario is None,
            operacao_nao_sujeita_issqn=tributacao_municipal is None,
        )

    def _same_person(
        self,
        first: PessoaDanfse | None,
        second: PessoaDanfse | None,
    ) -> bool:
        if first is None or second is None:
            return False

        first_doc = first.documento
        second_doc = second.documento

        if first_doc is None or second_doc is None:
            return False

        return (
            first_doc.cnpj is not None and first_doc.cnpj == second_doc.cnpj
        ) or (
            first_doc.cpf is not None and first_doc.cpf == second_doc.cpf
        ) or (
            first_doc.nif is not None and first_doc.nif == second_doc.nif
        )

    # ============================================================
    # Conversions
    # ============================================================

    def _normalize_access_key(self, value: str | None) -> str | None:
        if value is None:
            return None

        value = value.strip()

        if value.startswith("NFS"):
            return value[3:]

        return value

    def _date(self, value: str | None) -> date | None:
        if value is None:
            return None

        try:
            if "T" in value:
                return self._datetime(value).date()  # type: ignore[union-attr]

            return date.fromisoformat(value)
        except ValueError as exc:
            raise InvalidFieldValueError(f"Data inválida: {value}") from exc

    def _datetime(self, value: str | None) -> datetime | None:
        if value is None:
            return None

        normalized = value.replace("Z", "+00:00")

        try:
            return datetime.fromisoformat(normalized)
        except ValueError as exc:
            raise InvalidFieldValueError(f"Data/hora inválida: {value}") from exc

    def _decimal(self, value: str | None) -> Decimal | None:
        if value is None:
            return None

        normalized = value.strip().replace(",", ".")

        if normalized == "":
            return None

        try:
            return Decimal(normalized)
        except InvalidOperation as exc:
            raise InvalidFieldValueError(f"Decimal inválido: {value}") from exc

    def _sum_decimals(self, *values: Decimal | None) -> Decimal | None:
        valid_values = [value for value in values if value is not None]

        if not valid_values:
            return None

        return sum(valid_values, Decimal("0"))

    # ============================================================
    # Empty model handling
    # ============================================================

    def _none_if_empty(self, value: Any) -> Any | None:
        if self._has_value(value):
            return value

        return None

    def _has_value(self, value: Any) -> bool:
        if value is None:
            return False

        if isinstance(value, str):
            return value.strip() != ""

        if isinstance(value, bool):
            return True

        if isinstance(value, Decimal):
            return True

        if isinstance(value, date | datetime):
            return True

        if isinstance(value, BaseModel):
            return any(self._has_value(field_value) for field_value in value.__dict__.values())

        if isinstance(value, list | tuple | set):
            return any(self._has_value(item) for item in value)

        if isinstance(value, dict):
            return any(self._has_value(item) for item in value.values())

        return True


# Aliases de compatibilidade
DanfseXmlParserConfig = DanfseMapperConfig


class DanfseXmlParser:
    """Fachada: carrega XML e delega o mapeamento ao DanfseMapper."""

    def __init__(self, config: DanfseMapperConfig | None = None) -> None:
        self.config = config or DanfseMapperConfig()
        self._mapper = DanfseMapper(self.config)

    def parse(self, source: bytes | str | Path) -> DanfseData:
        from gerador_danfse.parser.xml_parser import parse_xml

        return self._mapper.map_to_domain(parse_xml(source))


def map_to_domain(
    doc: XmlDocument,
    config: DanfseMapperConfig | None = None,
) -> DanfseData:
    """Mapeia um XmlDocument para DanfseData."""
    return DanfseMapper(config).map_to_domain(doc)
