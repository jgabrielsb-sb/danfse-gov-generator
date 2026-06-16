# src/danfse/domain/models.py

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field


class DanfseBaseModel(BaseModel):
    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        str_strip_whitespace=True,
    )


# ============================================================
# Common value objects
# ============================================================

class DocumentoPessoaDanfse(DanfseBaseModel):
    cnpj: str | None = None
    cpf: str | None = None
    nif: str | None = None


class EnderecoDanfse(DanfseBaseModel):
    codigo_municipio: str | None = None
    municipio: str | None = None
    uf: str | None = None
    pais: str | None = None

    cep: str | None = None
    codigo_enderecamento_postal_exterior: str | None = None

    logradouro: str | None = None
    numero: str | None = None
    complemento: str | None = None
    bairro: str | None = None


class PessoaDanfse(DanfseBaseModel):
    documento: DocumentoPessoaDanfse | None = None

    inscricao_municipal: str | None = None
    telefone: str | None = None
    nome: str | None = None

    endereco: EnderecoDanfse | None = None

    email: str | None = None


# ============================================================
# Header / Identificação da NFS-e
# ============================================================

class CabecalhoDanfse(DanfseBaseModel):
    """
    Dados usados no cabeçalho direito do DANFSe.

    A logomarca, textos fixos e estilos não pertencem ao domínio,
    pois são recursos/layout, não dados extraídos do XML.
    """

    municipio_emitente: str | None = None
    uf_emitente: str | None = None

    ambiente_gerador: str | None = Field(default=None, description="ambGer")
    tipo_ambiente: str | None = Field(default=None, description="tpAmb")


class IdentificacaoNfseDanfse(DanfseBaseModel):
    """
    Bloco Dados da NFS-e.
    """

    chave_acesso: str | None = Field(
        default=None,
        description='NFSe/infNFSe/@id sem o prefixo "NFS"',
    )

    numero_nfse: str | None = Field(default=None, description="nNFSe")
    competencia_nfse: date | None = Field(default=None, description="dCompet")
    data_hora_emissao_nfse: datetime | None = Field(default=None, description="dhProc")

    numero_dps: str | None = Field(default=None, description="nDPS")
    serie_dps: str | None = Field(default=None, description="serie")
    data_hora_emissao_dps: datetime | None = Field(default=None, description="dhEmi")

    emitente_nfse: str | None = Field(default=None, description="tpEmit")
    situacao_nfse: str | None = Field(default=None, description="cStat")
    finalidade_nfse: str | None = Field(default=None, description="finNFSe")


# ============================================================
# Prestador / Fornecedor
# ============================================================

class RegimeTributarioPrestadorDanfse(DanfseBaseModel):
    simples_nacional_competencia: str | None = Field(
        default=None,
        description="opSimpNac",
    )

    regime_apuracao_tributaria_sn: str | None = Field(
        default=None,
        description="regApTribSN",
    )

    regime_especial_tributacao: str | None = Field(
        default=None,
        description="regEspTrib",
    )


class PrestadorDanfse(PessoaDanfse):
    regime_tributario: RegimeTributarioPrestadorDanfse | None = None


# ============================================================
# Tomador / Destinatário / Intermediário
# ============================================================

class TomadorDanfse(PessoaDanfse):
    pass


class DestinatarioDanfse(PessoaDanfse):
    """
    Destinatário da operação.

    Na NT, o destinatário não possui campo de inscrição municipal no bloco,
    mas herdamos de PessoaDanfse como opcional para manter a estrutura simples.
    O renderer/layout simplesmente não usa esse campo para destinatário.
    """

    pass


class IntermediarioDanfse(PessoaDanfse):
    pass


# ============================================================
# Serviço Prestado
# ============================================================

class CodigoServicoDanfse(DanfseBaseModel):
    codigo_tributacao_nacional: str | None = Field(default=None, description="cTribNac")
    codigo_tributacao_municipal: str | None = Field(default=None, description="cTribMun")

    descricao_tributacao_nacional: str | None = Field(default=None, description="xTribNac")
    descricao_tributacao_municipal: str | None = Field(default=None, description="xTribMun")

    codigo_nbs: str | None = Field(default=None, description="cNBS")


class LocalPrestacaoDanfse(DanfseBaseModel):
    codigo_municipio: str | None = None
    municipio: str | None = None
    uf: str | None = None
    pais: str | None = None

    local_prestacao_texto: str | None = Field(
        default=None,
        description="xLocPrestacao",
    )

    codigo_pais_prestacao: str | None = Field(
        default=None,
        description="cPaisPrestacao",
    )


class ServicoPrestadoDanfse(DanfseBaseModel):
    codigo_servico: CodigoServicoDanfse | None = None
    local_prestacao: LocalPrestacaoDanfse | None = None

    descricao_servico: str | None = Field(default=None, description="xDescServ")


# ============================================================
# Tributação Municipal - ISSQN
# ============================================================

class LocalIncidenciaIssqnDanfse(DanfseBaseModel):
    codigo_municipio: str | None = None
    municipio: str | None = None
    uf: str | None = None
    pais: str | None = None

    local_incidencia_texto: str | None = Field(
        default=None,
        description="xLocIncid",
    )

    codigo_pais_resultado: str | None = Field(
        default=None,
        description="cPaisResult",
    )


class SuspensaoExigibilidadeIssqnDanfse(DanfseBaseModel):
    tipo_suspensao: str | None = Field(default=None, description="tpSusp")
    numero_processo: str | None = Field(default=None, description="nProcesso")


class BeneficioMunicipalDanfse(DanfseBaseModel):
    tipo_beneficio_municipal: str | None = Field(default=None, description="tpBM")

    valor_calculo_beneficio_municipal: Decimal | None = Field(
        default=None,
        description="vCalcBM",
    )

    valor_reducao_bc_beneficio_municipal: Decimal | None = Field(
        default=None,
        description="vRedBCBM",
    )


class DeducoesReducoesDanfse(DanfseBaseModel):
    """
    Campos usados para total de deduções/reduções no bloco ISSQN.

    A NT permite origem em vDR ou em vCalcDR + vCalcReeRepRes,
    dependendo do grupo disponível no XML.
    """

    valor_deducoes_reducoes: Decimal | None = Field(default=None, description="vDR")

    valor_calculo_deducoes_reducoes: Decimal | None = Field(
        default=None,
        description="vCalcDR",
    )

    valor_calculo_reembolso_repasse_ressarcimento: Decimal | None = Field(
        default=None,
        description="vCalcReeRepRes",
    )


class TributacaoMunicipalDanfse(DanfseBaseModel):
    tipo_tributacao_issqn: str | None = Field(default=None, description="tribISSQN")

    local_incidencia: LocalIncidenciaIssqnDanfse | None = None

    regime_especial_tributacao_issqn: str | None = Field(
        default=None,
        description="regEspTrib",
    )

    tipo_imunidade_issqn: str | None = Field(
        default=None,
        description="tpImunidade",
    )

    suspensao_exigibilidade: SuspensaoExigibilidadeIssqnDanfse | None = None
    beneficio_municipal: BeneficioMunicipalDanfse | None = None
    deducoes_reducoes: DeducoesReducoesDanfse | None = None

    desconto_incondicionado: Decimal | None = Field(
        default=None,
        description="vDescIncond",
    )

    base_calculo_issqn: Decimal | None = Field(default=None, description="vBC")
    aliquota_aplicada: Decimal | None = Field(default=None, description="pAliqAplic")

    retencao_issqn: str | None = Field(default=None, description="tpRetISSQN")

    valor_issqn_apurado: Decimal | None = Field(default=None, description="vISSQN")

    operacao_sujeita_issqn: bool | None = None


# ============================================================
# Tributação Federal - Exceto CBS
# ============================================================

class TributacaoFederalDanfse(DanfseBaseModel):
    valor_retencao_irrf: Decimal | None = Field(default=None, description="vRetIRRF")

    valor_retencao_contribuicao_previdenciaria: Decimal | None = Field(
        default=None,
        description="vRetCP",
    )

    valor_retencao_csll: Decimal | None = Field(
        default=None,
        description="vRetCSLL",
    )

    valor_pis_debito_apuracao_propria: Decimal | None = Field(
        default=None,
        description="vPis",
    )

    valor_cofins_debito_apuracao_propria: Decimal | None = Field(
        default=None,
        description="vCofins",
    )

    tipo_retencao_pis_cofins: str | None = Field(
        default=None,
        description="tpRetPisCofins",
    )


# ============================================================
# Tributação IBS / CBS
# ============================================================

class IncidenciaIbsCbsDanfse(DanfseBaseModel):
    indicador_operacao: str | None = Field(default=None, description="cIndOp")

    codigo_localidade_incidencia: str | None = Field(
        default=None,
        description="cLocalidadeIncid",
    )

    localidade_incidencia: str | None = Field(
        default=None,
        description="xLocalidadeIncid",
    )

    uf_incidencia: str | None = None


class ClassificacaoTributariaIbsCbsDanfse(DanfseBaseModel):
    cst: str | None = Field(default=None, description="CST")

    codigo_classificacao_tributaria: str | None = Field(
        default=None,
        description="cClassTrib",
    )


class ExclusoesReducoesBaseCalculoIbsCbsDanfse(DanfseBaseModel):
    """
    Campos usados no somatório de exclusões/reduções da base de cálculo IBS/CBS.

    Pela NT, o campo exibido é um somatório envolvendo:
    vDescIncond + vCalcReeRepRes + vISSQN + vPIS + vCOFINS.
    """

    desconto_incondicionado: Decimal | None = Field(
        default=None,
        description="vDescIncond",
    )

    valor_calculo_reembolso_repasse_ressarcimento: Decimal | None = Field(
        default=None,
        description="vCalcReeRepRes",
    )

    valor_issqn: Decimal | None = Field(default=None, description="vISSQN")
    valor_pis: Decimal | None = Field(default=None, description="vPIS")
    valor_cofins: Decimal | None = Field(default=None, description="vCOFINS")

    valor_total_exclusoes_reducoes: Decimal | None = None


class IbsUfDanfse(DanfseBaseModel):
    reducao_aliquota_ibs_uf: Decimal | None = Field(
        default=None,
        description="pRedAliqUF",
    )

    aliquota_ibs_uf: Decimal | None = Field(default=None, description="pIBSUF")

    aliquota_efetiva_ibs_uf: Decimal | None = Field(
        default=None,
        description="pAliqEfetUF",
    )

    valor_ibs_uf: Decimal | None = Field(default=None, description="vIBSUF")


class IbsMunicipalDanfse(DanfseBaseModel):
    reducao_aliquota_ibs_municipal: Decimal | None = Field(
        default=None,
        description="pRedAliqMun",
    )

    aliquota_ibs_municipal: Decimal | None = Field(
        default=None,
        description="pIBSMun",
    )

    aliquota_efetiva_ibs_municipal: Decimal | None = Field(
        default=None,
        description="pAliqEfetMun",
    )

    valor_ibs_municipal: Decimal | None = Field(
        default=None,
        description="vIBSMun",
    )


class CbsDanfse(DanfseBaseModel):
    reducao_aliquota_cbs: Decimal | None = Field(
        default=None,
        description="pRedAliqCBS",
    )

    aliquota_cbs: Decimal | None = Field(default=None, description="pCBS")

    aliquota_efetiva_cbs: Decimal | None = Field(
        default=None,
        description="pAliqEfetCBS",
    )

    valor_cbs: Decimal | None = Field(default=None, description="vCBS")


class TributacaoIbsCbsDanfse(DanfseBaseModel):
    classificacao_tributaria: ClassificacaoTributariaIbsCbsDanfse | None = None
    incidencia: IncidenciaIbsCbsDanfse | None = None

    exclusoes_reducoes_base_calculo: (
        ExclusoesReducoesBaseCalculoIbsCbsDanfse | None
    ) = None

    base_calculo_apos_exclusoes_reducoes: Decimal | None = Field(
        default=None,
        description="vBC",
    )

    ibs_uf: IbsUfDanfse | None = None
    ibs_municipal: IbsMunicipalDanfse | None = None
    cbs: CbsDanfse | None = None

    valor_total_ibs: Decimal | None = Field(default=None, description="vIBSTot")
    valor_total_cbs: Decimal | None = Field(default=None, description="vCBS")


# ============================================================
# Valor Total da NFS-e
# ============================================================

class ValoresServicoDanfse(DanfseBaseModel):
    valor_servico: Decimal | None = Field(default=None, description="vServ")

    desconto_incondicionado: Decimal | None = Field(
        default=None,
        description="vDescIncond",
    )

    desconto_condicionado: Decimal | None = Field(
        default=None,
        description="vDescCond",
    )


class TotaisDanfse(DanfseBaseModel):
    valor_operacao_servico: Decimal | None = Field(default=None, description="vServ")

    desconto_incondicionado: Decimal | None = Field(
        default=None,
        description="vDescIncond",
    )

    desconto_condicionado: Decimal | None = Field(
        default=None,
        description="vDescCond",
    )

    total_retencoes_issqn_federais: Decimal | None = Field(
        default=None,
        description="vTotalRet",
    )

    valor_liquido_nfse: Decimal | None = Field(default=None, description="vLiq")

    total_ibs_cbs: Decimal | None = Field(
        default=None,
        description="vIBSTot + vCBS",
    )

    valor_liquido_nfse_mais_ibs_cbs: Decimal | None = Field(
        default=None,
        description="vTotNF",
    )


# ============================================================
# Informações Complementares
# ============================================================

class ObraDanfse(DanfseBaseModel):
    codigo_obra: str | None = Field(default=None, description="cObra")


class ImovelDanfse(DanfseBaseModel):
    inscricao_imobiliaria_fiscal: str | None = Field(
        default=None,
        description="inscImobFisc",
    )


class EventoDanfse(DanfseBaseModel):
    identificacao_atividade_evento: str | None = Field(
        default=None,
        description="idAtvEvt",
    )


class PedidoDanfse(DanfseBaseModel):
    numero_pedido: str | None = Field(default=None, description="xPed")
    item_pedido: str | None = Field(default=None, description="xItemPed")


class TotaisAproximadosTributosDanfse(DanfseBaseModel):
    """
    Totais aproximados dos tributos conforme Lei nº 12.741/2012.

    A NT permite valores monetários OU percentuais.
    """

    valor_total_tributos_federais: Decimal | None = Field(
        default=None,
        description="vTotTribFed",
    )

    valor_total_tributos_estaduais: Decimal | None = Field(
        default=None,
        description="vTotTribEst",
    )

    valor_total_tributos_municipais: Decimal | None = Field(
        default=None,
        description="vTotTribMun",
    )

    percentual_total_tributos_federais: Decimal | None = Field(
        default=None,
        description="pTotTribFed",
    )

    percentual_total_tributos_estaduais: Decimal | None = Field(
        default=None,
        description="pTotTribEst",
    )

    percentual_total_tributos_municipais: Decimal | None = Field(
        default=None,
        description="pTotTribMun",
    )


class InformacoesComplementaresDanfse(DanfseBaseModel):
    informacoes_complementares: str | None = Field(
        default=None,
        description="xInfComp",
    )

    chave_nfse_substituida: str | None = Field(
        default=None,
        description="chSubstda",
    )

    documento_referenciado: str | None = Field(
        default=None,
        description="docRef",
    )

    obra: ObraDanfse | None = None
    imovel: ImovelDanfse | None = None
    evento: EventoDanfse | None = None

    documento_tecnico: str | None = Field(
        default=None,
        description="idDocTec",
    )

    pedido: PedidoDanfse | None = None

    outras_informacoes: str | None = Field(
        default=None,
        description="xOutInf",
    )

    informacoes_administracao_tributaria_municipal: str | None = None

    totais_aproximados_tributos: TotaisAproximadosTributosDanfse | None = None


# ============================================================
# Canhoto
# ============================================================

class CanhotoDanfse(DanfseBaseModel):
    """
    Bloco opcional.

    A NT define o canhoto como opcional. Alguns campos, como data de
    cientificação e assinatura, não necessariamente vêm do XML da NFS-e.
    Por isso, eles podem ser preenchidos por configuração externa ou
    simplesmente omitidos.
    """

    data_cientificacao: date | None = None
    identificacao_assinatura: str | None = None

    numero_nfse: str | None = None
    chave_acesso: str | None = None


# ============================================================
# Status / Flags visuais
# ============================================================

class StatusVisualDanfse(DanfseBaseModel):
    """
    Flags derivadas dos campos do XML.

    Elas facilitam decisões de renderização:
    - aviso de homologação;
    - marca d'água CANCELADA;
    - marca d'água SUBSTITUÍDA;
    - mensagem de destinatário igual ao tomador.
    """

    is_homologacao: bool = False
    is_cancelada: bool = False
    is_substituida: bool = False

    tomador_nao_identificado: bool = False
    destinatario_nao_identificado: bool = False
    destinatario_igual_tomador: bool = False
    intermediario_nao_identificado: bool = False

    operacao_nao_sujeita_issqn: bool = False


# ============================================================
# Modelo principal
# ============================================================

class DanfseData(DanfseBaseModel):
    """
    Modelo principal necessário para gerar o DANFSe.

    Este objeto deve ser retornado pelo mapper depois da leitura do XML.
    """

    cabecalho: CabecalhoDanfse | None = None
    identificacao: IdentificacaoNfseDanfse

    prestador: PrestadorDanfse

    tomador: TomadorDanfse | None = None
    destinatario: DestinatarioDanfse | None = None
    intermediario: IntermediarioDanfse | None = None

    servico: ServicoPrestadoDanfse

    valores_servico: ValoresServicoDanfse | None = None

    tributacao_municipal: TributacaoMunicipalDanfse | None = None
    tributacao_federal: TributacaoFederalDanfse | None = None
    tributacao_ibs_cbs: TributacaoIbsCbsDanfse | None = None

    totais: TotaisDanfse | None = None

    informacoes_complementares: InformacoesComplementaresDanfse | None = None

    canhoto: CanhotoDanfse | None = None

    status_visual: StatusVisualDanfse = Field(
        default_factory=StatusVisualDanfse,
    )