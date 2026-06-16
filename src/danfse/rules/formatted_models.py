from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class FormattedBaseModel(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class FormattedDocumentoPessoa(FormattedBaseModel):
    cnpj_cpf_nif: str = "-"


class FormattedEndereco(FormattedBaseModel):
    municipio_uf: str = "-"
    codigo_ibge_cep: str = "-"
    endereco: str = "-"


class FormattedPessoa(FormattedBaseModel):
    documento: str = "-"
    inscricao_municipal: str = "-"
    telefone: str = "-"
    nome: str = "-"
    municipio_uf: str = "-"
    codigo_ibge_cep: str = "-"
    endereco: str = "-"
    email: str = "-"


class FormattedRegimeTributarioPrestador(FormattedBaseModel):
    simples_nacional_competencia: str = "-"
    regime_apuracao_tributaria_sn: str = "-"
    regime_especial_tributacao: str = "-"


class FormattedPrestador(FormattedPessoa):
    simples_nacional_competencia: str = "-"
    regime_apuracao_tributaria_sn: str = "-"
    regime_especial_tributacao: str = "-"


class FormattedCabecalho(FormattedBaseModel):
    municipio_ambiente: str = "-"
    ambiente_gerador: str = "-"
    tipo_ambiente: str = "-"
    homologacao_aviso: str = ""


class FormattedIdentificacao(FormattedBaseModel):
    chave_acesso: str = "-"
    numero_nfse: str = "-"
    competencia_nfse: str = "-"
    data_hora_emissao_nfse: str = "-"
    numero_dps: str = "-"
    serie_dps: str = "-"
    data_hora_emissao_dps: str = "-"
    emitente_nfse: str = "-"
    situacao_nfse: str = "-"
    finalidade_nfse: str = "-"
    qr_code_url: str = ""


class FormattedCodigoServico(FormattedBaseModel):
    codigo_tributacao: str = "-"
    codigo_nbs: str = "-"
    descricao_tributacao: str = "-"


class FormattedLocalPrestacao(FormattedBaseModel):
    local_prestacao: str = "-"


class FormattedServico(FormattedBaseModel):
    codigo_tributacao: str = "-"
    codigo_nbs: str = "-"
    local_prestacao: str = "-"
    descricao_tributacao: str = "-"
    descricao_servico: str = "-"


class FormattedValoresServico(FormattedBaseModel):
    valor_servico: str = "-"
    desconto_incondicionado: str = "-"
    desconto_condicionado: str = "-"


class FormattedTributacaoMunicipal(FormattedBaseModel):
    bloco_texto: str = ""
    tipo_tributacao_issqn: str = "-"
    local_incidencia: str = "-"
    regime_especial_tributacao_issqn: str = "-"
    tipo_imunidade_issqn: str = "-"
    suspensao_exigibilidade: str = "-"
    numero_processo_suspensao: str = "-"
    beneficio_municipal: str = "-"
    calculo_beneficio_municipal: str = "-"
    total_deducoes_reducoes: str = "-"
    desconto_incondicionado: str = "-"
    base_calculo_issqn: str = "-"
    aliquota_aplicada: str = "-"
    retencao_issqn: str = "-"
    valor_issqn_apurado: str = "-"


class FormattedTributacaoFederal(FormattedBaseModel):
    valor_retencao_irrf: str = "-"
    valor_retencao_contribuicao_previdenciaria: str = "-"
    valor_retencao_csll: str = "-"
    valor_pis: str = "-"
    valor_cofins: str = "-"
    tipo_retencao_pis_cofins: str = "-"


class FormattedIbsUf(FormattedBaseModel):
    reducao_aliquota: str = "-"
    aliquota: str = "-"
    aliquota_efetiva: str = "-"
    valor: str = "-"


class FormattedIbsMunicipal(FormattedIbsUf):
    pass


class FormattedCbs(FormattedBaseModel):
    reducao_aliquota: str = "-"
    aliquota: str = "-"
    aliquota_efetiva: str = "-"
    valor: str = "-"


class FormattedTributacaoIbsCbs(FormattedBaseModel):
    cst_classificacao: str = "-"
    indicador_operacao_incidencia: str = "-"
    exclusoes_reducoes_base_calculo: str = "-"
    base_calculo_apos_exclusoes: str = "-"
    reducoes_aliquota_ibs_cbs: str = "-"
    aliquotas_ibs: str = "-"
    aliquota_efetiva_ibs_municipal: str = "-"
    valor_ibs_municipal: str = "-"
    aliquota_efetiva_ibs_uf: str = "-"
    valor_ibs_uf: str = "-"
    valor_total_ibs: str = "-"
    aliquota_cbs: str = "-"
    aliquota_efetiva_cbs: str = "-"
    valor_total_cbs: str = "-"


class FormattedTotais(FormattedBaseModel):
    valor_operacao_servico: str = "-"
    desconto_incondicionado: str = "-"
    desconto_condicionado: str = "-"
    total_retencoes: str = "-"
    valor_liquido_nfse: str = "-"
    total_ibs_cbs: str = "-"
    valor_liquido_nfse_mais_ibs_cbs: str = "-"


class FormattedInformacoesComplementares(FormattedBaseModel):
    texto: str = "-"
    totais_aproximados_tributos: str = "-"


class FormattedCanhoto(FormattedBaseModel):
    data_cientificacao: str = "-"
    identificacao_assinatura: str = "-"
    numero_nfse_chave: str = "-"


class FormattedTomador(FormattedPessoa):
    bloco_texto: str = ""


class FormattedDestinatario(FormattedPessoa):
    bloco_texto: str = ""


class FormattedIntermediario(FormattedPessoa):
    bloco_texto: str = ""


class FormattedDanfse(FormattedBaseModel):
    cabecalho: FormattedCabecalho = Field(default_factory=FormattedCabecalho)
    identificacao: FormattedIdentificacao = Field(default_factory=FormattedIdentificacao)
    prestador: FormattedPrestador = Field(default_factory=FormattedPrestador)
    tomador: FormattedTomador | None = None
    destinatario: FormattedDestinatario | None = None
    intermediario: FormattedIntermediario | None = None
    servico: FormattedServico = Field(default_factory=FormattedServico)
    valores_servico: FormattedValoresServico | None = None
    tributacao_municipal: FormattedTributacaoMunicipal | None = None
    tributacao_federal: FormattedTributacaoFederal | None = None
    tributacao_ibs_cbs: FormattedTributacaoIbsCbs | None = None
    totais: FormattedTotais | None = None
    informacoes_complementares: FormattedInformacoesComplementares | None = None
    canhoto: FormattedCanhoto | None = None
    watermark: str = ""
