# src/danfse/layout/specs.py

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


RenderKind = Literal[
    "text",
    "block_title",
    "fixed_text",
    "image",
    "qrcode",
]


@dataclass(frozen=True)
class PageSpec:
    width_cm: float
    height_cm: float
    orientation: Literal["portrait", "landscape"]
    border_width_pt: float
    inner_line_width_pt: float


@dataclass(frozen=True)
class BlockSpec:
    key: str
    x_cm: float
    y_top_cm: float
    width_cm: float
    height_cm: float
    optional: bool = False
    dynamic_height: bool = False


@dataclass(frozen=True)
class FieldSpec:
    key: str
    block: str
    label: str | None
    x_cm: float
    y_top_cm: float
    width_cm: float
    height_cm: float
    max_chars: int | None = None
    kind: RenderKind = "text"
    shaded: bool = False
    multiline: bool = False
    optional: bool = False
    dynamic_height: bool = False
    fixed_text: str | None = None
    notes: str | None = None


PAGE_SPEC = PageSpec(
    width_cm=21.0,
    height_cm=29.7,
    orientation="portrait",
    border_width_pt=1.0,
    inner_line_width_pt=0.5,
)


BLOCK_SPECS: list[BlockSpec] = [
    BlockSpec("cabecalho", 0.30, 0.30, 20.40, 1.16),
    BlockSpec("dados_nfse", 0.30, 1.48, 20.40, 2.84),
    BlockSpec("prestador", 0.30, 4.34, 20.40, 2.58),
    BlockSpec("tomador", 0.30, 6.92, 20.40, 1.94, dynamic_height=True),
    BlockSpec("destinatario", 0.30, 8.86, 20.40, 1.94, dynamic_height=True),
    BlockSpec("intermediario", 0.30, 10.80, 20.40, 1.94, dynamic_height=True),
    BlockSpec("servico", 0.30, 12.74, 20.40, 1.69, dynamic_height=True),
    BlockSpec("tributacao_municipal", 0.30, 14.43, 20.40, 2.59, dynamic_height=True),
    BlockSpec("tributacao_federal", 0.30, 17.02, 20.40, 1.30),
    BlockSpec("tributacao_ibs_cbs", 0.30, 18.32, 20.40, 2.58),
    BlockSpec("totais", 0.30, 20.90, 20.40, 1.37),
    BlockSpec("informacoes_complementares", 0.30, 22.27, 20.40, 5.83, dynamic_height=True),
    BlockSpec("canhoto", 0.30, 28.10, 20.40, 0.67, optional=True),
]


FIELD_SPECS: list[FieldSpec] = [
    # ============================================================
    # Cabeçalho
    # ============================================================

    FieldSpec(
        key="assets.logo_nfse",
        block="cabecalho",
        label=None,
        x_cm=0.49,
        y_top_cm=0.44,
        width_cm=4.00,
        height_cm=0.85,
        kind="image",
    ),
    FieldSpec(
        key="cabecalho.titulo",
        block="cabecalho",
        label=None,
        x_cm=5.41,
        y_top_cm=0.30,
        width_cm=10.19,
        height_cm=1.16,
        kind="fixed_text",
        shaded=True,
        fixed_text="DANFSe v2.0\nDocumento Auxiliar da NFS-e",
        notes="Centralizar texto no quadro.",
    ),
    FieldSpec(
        key="cabecalho.municipio_emitente",
        block="cabecalho",
        label=None,
        x_cm=15.62,
        y_top_cm=0.30,
        width_cm=5.09,
        height_cm=0.64,
        max_chars=37,
    ),
    FieldSpec(
        key="cabecalho.ambiente_gerador",
        block="cabecalho",
        label=None,
        x_cm=15.62,
        y_top_cm=0.97,
        width_cm=5.09,
        height_cm=0.24,
        max_chars=37,
    ),
    FieldSpec(
        key="cabecalho.tipo_ambiente",
        block="cabecalho",
        label=None,
        x_cm=15.62,
        y_top_cm=1.22,
        width_cm=5.09,
        height_cm=0.24,
        max_chars=37,
    ),

    # ============================================================
    # Dados da NFS-e
    # ============================================================

    FieldSpec(
        key="identificacao.chave_acesso",
        block="dados_nfse",
        label="CHAVE DE ACESSO DA NFS-e",
        x_cm=0.30,
        y_top_cm=1.48,
        width_cm=15.30,
        height_cm=0.77,
        max_chars=50,
    ),
    FieldSpec(
        key="identificacao.numero_nfse",
        block="dados_nfse",
        label="NÚMERO DA NFS-e",
        x_cm=0.30,
        y_top_cm=2.27,
        width_cm=5.09,
        height_cm=0.67,
        max_chars=13,
    ),
    FieldSpec(
        key="identificacao.competencia_nfse",
        block="dados_nfse",
        label="COMPETÊNCIA DA NFS-e",
        x_cm=5.41,
        y_top_cm=2.27,
        width_cm=5.09,
        height_cm=0.67,
        max_chars=10,
        notes="Formato DD/MM/AAAA.",
    ),
    FieldSpec(
        key="identificacao.data_hora_emissao_nfse",
        block="dados_nfse",
        label="DATA E HORA DA EMISSÃO DA NFS-e",
        x_cm=10.51,
        y_top_cm=2.27,
        width_cm=5.09,
        height_cm=0.67,
        max_chars=19,
        notes="Formato DD/MM/AAAA hh:mm:ss.",
    ),
    FieldSpec(
        key="identificacao.numero_dps",
        block="dados_nfse",
        label="NÚMERO DA DPS",
        x_cm=0.30,
        y_top_cm=2.96,
        width_cm=5.09,
        height_cm=0.67,
        max_chars=15,
    ),
    FieldSpec(
        key="identificacao.serie_dps",
        block="dados_nfse",
        label="SÉRIE DA DPS",
        x_cm=5.41,
        y_top_cm=2.96,
        width_cm=5.09,
        height_cm=0.67,
        max_chars=5,
    ),
    FieldSpec(
        key="identificacao.data_hora_emissao_dps",
        block="dados_nfse",
        label="DATA E HORA DA EMISSÃO DA DPS",
        x_cm=10.51,
        y_top_cm=2.96,
        width_cm=5.09,
        height_cm=0.67,
        max_chars=19,
        notes="Formato DD/MM/AAAA hh:mm:ss.",
    ),
    FieldSpec(
        key="identificacao.emitente_nfse",
        block="dados_nfse",
        label="EMITENTE DA NFS-e",
        x_cm=0.30,
        y_top_cm=3.65,
        width_cm=5.09,
        height_cm=0.67,
        max_chars=13,
        shaded=True,
    ),
    FieldSpec(
        key="identificacao.situacao_nfse",
        block="dados_nfse",
        label="SITUAÇÃO DA NFS-e",
        x_cm=5.41,
        y_top_cm=3.65,
        width_cm=5.09,
        height_cm=0.67,
        max_chars=40,
    ),
    FieldSpec(
        key="identificacao.finalidade_nfse",
        block="dados_nfse",
        label="FINALIDADE",
        x_cm=10.51,
        y_top_cm=3.65,
        width_cm=5.09,
        height_cm=0.67,
        max_chars=40,
    ),
    FieldSpec(
        key="identificacao.qrcode",
        block="dados_nfse",
        label=None,
        x_cm=17.48,
        y_top_cm=1.67,
        width_cm=1.52,
        height_cm=1.52,
        kind="qrcode",
    ),
    FieldSpec(
        key="identificacao.qrcode_texto",
        block="dados_nfse",
        label=None,
        x_cm=15.80,
        y_top_cm=3.36,
        width_cm=4.72,
        height_cm=0.68,
        kind="fixed_text",
        multiline=True,
        fixed_text=(
            "A autenticidade desta NFS-e pode ser verificada pela leitura "
            "deste código QR ou pela consulta da chave de acesso no portal "
            "nacional da NFS-e"
        ),
    ),

    # ============================================================
    # Prestador / Fornecedor
    # ============================================================

    FieldSpec(
        key="block.prestador.title",
        block="prestador",
        label=None,
        x_cm=0.30,
        y_top_cm=4.34,
        width_cm=5.09,
        height_cm=0.63,
        kind="block_title",
        shaded=True,
        fixed_text="PRESTADOR / FORNECEDOR",
    ),
    FieldSpec("prestador.documento", "prestador", "CNPJ / CPF / NIF", 5.41, 4.34, 5.09, 0.63, 40),
    FieldSpec("prestador.inscricao_municipal", "prestador", "INDICADOR MUNICIPAL (INSCRIÇÃO)", 10.51, 4.34, 5.09, 0.63, 15),
    FieldSpec("prestador.telefone", "prestador", "TELEFONE", 15.62, 4.34, 5.09, 0.63, 20),
    FieldSpec("prestador.nome", "prestador", "NOME / NOME EMPRESARIAL", 0.30, 4.98, 10.19, 0.63, 80),
    FieldSpec("prestador.municipio_uf", "prestador", "MUNICÍPIO / SIGLA UF", 10.51, 4.98, 5.09, 0.63, 37),
    FieldSpec("prestador.codigo_ibge_cep", "prestador", "CÓDIGO IBGE / CEP", 15.62, 4.98, 5.09, 0.63, 21),
    FieldSpec("prestador.endereco", "prestador", "ENDEREÇO", 0.30, 5.62, 10.19, 0.63, 80, optional=True),
    FieldSpec("prestador.email", "prestador", "EMAIL", 10.51, 5.62, 10.19, 0.63, 80, optional=True),
    FieldSpec("prestador.simples_nacional_competencia", "prestador", "SIMPLES NACIONAL NA DATA DE COMPETÊNCIA", 0.30, 6.28, 5.09, 0.63, 40),
    FieldSpec("prestador.regime_apuracao_tributaria_sn", "prestador", "REGIME DE APURAÇÃO TRIBUTÁRIA PELO SN", 10.51, 6.28, 10.19, 0.63, 80),

    # ============================================================
    # Tomador / Adquirente
    # ============================================================

    FieldSpec("block.tomador.title", "tomador", None, 0.30, 6.92, 5.09, 0.63, kind="block_title", shaded=True, fixed_text="TOMADOR / ADQUIRENTE"),
    FieldSpec("tomador.documento", "tomador", "CNPJ / CPF / NIF", 5.41, 6.92, 5.09, 0.63, 40),
    FieldSpec("tomador.inscricao_municipal", "tomador", "INDICADOR MUNICIPAL (INSCRIÇÃO)", 10.51, 6.92, 5.09, 0.63, 15),
    FieldSpec("tomador.telefone", "tomador", "TELEFONE", 15.62, 6.92, 5.09, 0.63, 20),
    FieldSpec("tomador.nome", "tomador", "NOME / NOME EMPRESARIAL", 0.30, 7.56, 10.19, 0.63, 80),
    FieldSpec("tomador.municipio_uf", "tomador", "MUNICÍPIO / SIGLA UF", 10.51, 7.56, 5.09, 0.63, 37),
    FieldSpec("tomador.codigo_ibge_cep", "tomador", "CÓDIGO IBGE / CEP", 15.62, 7.56, 5.09, 0.63, 21),
    FieldSpec("tomador.endereco", "tomador", "ENDEREÇO", 0.30, 8.22, 10.19, 0.63, 80, optional=True),
    FieldSpec("tomador.email", "tomador", "E-MAIL", 10.51, 8.22, 10.19, 0.63, 80, optional=True),
    FieldSpec(
        key="tomador.mensagem_nao_identificado",
        block="tomador",
        label=None,
        x_cm=0.30,
        y_top_cm=6.92,
        width_cm=20.40,
        height_cm=0.32,
        kind="fixed_text",
        optional=True,
        fixed_text="TOMADOR/ADQUIRENTE DA OPERAÇÃO NÃO IDENTIFICADO NA NFS-e",
    ),

    # ============================================================
    # Destinatário da Operação
    # ============================================================

    FieldSpec("block.destinatario.title", "destinatario", None, 0.30, 8.86, 5.09, 0.63, kind="block_title", shaded=True, fixed_text="DESTINATÁRIO DA OPERAÇÃO"),
    FieldSpec("destinatario.documento", "destinatario", "CNPJ / CPF / NIF", 5.41, 8.86, 5.09, 0.63, 40),
    FieldSpec("destinatario.telefone", "destinatario", "TELEFONE", 15.62, 8.86, 5.09, 0.63, 20),
    FieldSpec("destinatario.nome", "destinatario", "NOME / NOME EMPRESARIAL", 0.30, 9.50, 10.19, 0.63, 80),
    FieldSpec("destinatario.municipio_uf", "destinatario", "MUNICÍPIO / SIGLA UF", 10.51, 9.50, 5.09, 0.63, 37),
    FieldSpec("destinatario.codigo_ibge_cep", "destinatario", "CÓDIGO IBGE / CEP", 15.62, 9.50, 5.09, 0.63, 21),
    FieldSpec("destinatario.endereco", "destinatario", "ENDEREÇO", 0.30, 10.16, 10.19, 0.63, 80, optional=True),
    FieldSpec("destinatario.email", "destinatario", "E-MAIL", 10.51, 10.16, 10.19, 0.63, 80, optional=True),
    FieldSpec(
        key="destinatario.mensagem_nao_identificado",
        block="destinatario",
        label=None,
        x_cm=0.30,
        y_top_cm=8.86,
        width_cm=20.40,
        height_cm=0.32,
        kind="fixed_text",
        optional=True,
        fixed_text="DESTINATÁRIO DA OPERAÇÃO NÃO IDENTIFICADO NA NFS-e",
    ),
    FieldSpec(
        key="destinatario.mensagem_igual_tomador",
        block="destinatario",
        label=None,
        x_cm=0.30,
        y_top_cm=8.86,
        width_cm=20.40,
        height_cm=0.32,
        kind="fixed_text",
        optional=True,
        fixed_text="O DESTINATÁRIO É O PRÓPRIO TOMADOR/ADQUIRENTE DA OPERAÇÃO",
    ),

    # ============================================================
    # Intermediário da Operação
    # ============================================================

    FieldSpec("block.intermediario.title", "intermediario", None, 0.30, 10.80, 5.09, 0.63, kind="block_title", shaded=True, fixed_text="INTERMEDIÁRIO DA OPERAÇÃO"),
    FieldSpec("intermediario.documento", "intermediario", "CNPJ / CPF / NIF", 5.41, 10.80, 5.09, 0.63, 40),
    FieldSpec("intermediario.inscricao_municipal", "intermediario", "INDICADOR MUNICIPAL (INSCRIÇÃO)", 10.51, 10.80, 5.09, 0.63, 15),
    FieldSpec("intermediario.telefone", "intermediario", "TELEFONE", 15.62, 10.80, 5.09, 0.63, 20),
    FieldSpec("intermediario.nome", "intermediario", "NOME / NOME EMPRESARIAL", 0.30, 11.44, 10.19, 0.63, 80),
    FieldSpec("intermediario.municipio_uf", "intermediario", "MUNICÍPIO / SIGLA UF", 10.51, 11.44, 5.09, 0.63, 37),
    FieldSpec("intermediario.codigo_ibge_cep", "intermediario", "CÓDIGO IBGE / CEP", 15.62, 11.44, 5.09, 0.63, 21),
    FieldSpec("intermediario.endereco", "intermediario", "ENDEREÇO", 0.30, 12.09, 10.19, 0.63, 80, optional=True),
    FieldSpec("intermediario.email", "intermediario", "E-MAIL", 10.51, 12.09, 10.19, 0.63, 80, optional=True),
    FieldSpec(
        key="intermediario.mensagem_nao_identificado",
        block="intermediario",
        label=None,
        x_cm=0.30,
        y_top_cm=10.80,
        width_cm=20.40,
        height_cm=0.32,
        kind="fixed_text",
        optional=True,
        fixed_text="INTERMEDIÁRIO DA OPERAÇÃO NÃO IDENTIFICADO NA NFS-e",
    ),

    # ============================================================
    # Serviço Prestado
    # ============================================================

    FieldSpec("block.servico.title", "servico", None, 0.30, 12.74, 5.09, 0.63, kind="block_title", shaded=True, fixed_text="SERVIÇO PRESTADO"),
    FieldSpec("servico.codigo_tributacao_nacional_municipal", "servico", "CÓDIGO DE TRIBUTAÇÃO NACIONAL / MUNICIPAL", 5.41, 12.74, 5.09, 0.63, 14),
    FieldSpec("servico.codigo_nbs", "servico", "CÓDIGO DA NBS", 10.51, 12.74, 5.09, 0.63, 9),
    FieldSpec("servico.local_prestacao_uf_pais", "servico", "LOCAL DA PRESTAÇÃO / SIGLA UF / PAÍS", 15.62, 12.74, 5.09, 0.63, 42),
    FieldSpec("servico.descricao_codigo_tributacao", "servico", None, 0.30, 13.39, 20.40, 0.38, 170, multiline=True),
    FieldSpec(
        key="servico.descricao_servico",
        block="servico",
        label="DESCRIÇÃO DO SERVIÇO",
        x_cm=0.30,
        y_top_cm=13.79,
        width_cm=20.40,
        height_cm=0.63,
        max_chars=1300,
        multiline=True,
        dynamic_height=True,
        notes="Pode receber altura extra quando blocos forem suprimidos.",
    ),

    # ============================================================
    # Tributação Municipal - ISSQN
    # ============================================================

    FieldSpec("block.tributacao_municipal.title", "tributacao_municipal", None, 0.30, 14.43, 5.09, 0.63, kind="block_title", shaded=True, fixed_text="TRIBUTAÇÃO MUNICIPAL (ISSQN)"),
    FieldSpec("tributacao_municipal.tipo_tributacao_issqn", "tributacao_municipal", "TIPO DE TRIBUTAÇÃO DO ISSQN", 5.41, 14.43, 5.09, 0.63, 21),
    FieldSpec("tributacao_municipal.local_incidencia_uf_pais", "tributacao_municipal", "MUNICÍPIO / SIGLA UF / PAÍS DA INCIDÊNCIA DO ISSQN", 10.51, 14.43, 10.19, 0.63, 42),
    FieldSpec("tributacao_municipal.regime_especial_tributacao_issqn", "tributacao_municipal", "REGIME ESPECIAL DE TRIBUTAÇÃO DO ISSQN", 0.30, 15.08, 5.09, 0.63, 27, optional=True),
    FieldSpec("tributacao_municipal.tipo_imunidade_issqn", "tributacao_municipal", "TIPO DE IMUNIDADE DO ISSQN", 5.41, 15.08, 5.09, 0.63, 40, optional=True),
    FieldSpec("tributacao_municipal.suspensao_exigibilidade", "tributacao_municipal", "SUSPENSÃO DA EXIGIBILIDADE DO ISSQN", 10.51, 15.08, 5.09, 0.63, 40, optional=True),
    FieldSpec("tributacao_municipal.numero_processo_suspensao", "tributacao_municipal", "NÚMERO PROCESSO SUSPENSÃO", 15.62, 15.08, 5.09, 0.63, 30, optional=True),
    FieldSpec("tributacao_municipal.beneficio_municipal", "tributacao_municipal", "BENEFÍCIO MUNICIPAL", 0.30, 15.73, 5.09, 0.63, 40, optional=True),
    FieldSpec("tributacao_municipal.calculo_bm", "tributacao_municipal", "CÁLCULO DO BM", 5.41, 15.73, 5.09, 0.63, optional=True),
    FieldSpec("tributacao_municipal.total_deducoes_reducoes", "tributacao_municipal", "TOTAL DEDUÇÕES/REDUÇÕES", 10.51, 15.73, 5.09, 0.63, optional=True),
    FieldSpec("tributacao_municipal.desconto_incondicionado", "tributacao_municipal", "DESCONTO INCONDICIONADO", 15.62, 15.73, 5.09, 0.63, optional=True),
    FieldSpec("tributacao_municipal.base_calculo_issqn", "tributacao_municipal", "BC ISSQN", 0.30, 16.37, 5.09, 0.63),
    FieldSpec("tributacao_municipal.aliquota_aplicada", "tributacao_municipal", "ALÍQUOTA APLICADA", 5.41, 16.37, 5.09, 0.63),
    FieldSpec("tributacao_municipal.retencao_issqn", "tributacao_municipal", "RETENÇÃO DO ISSQN", 10.51, 16.37, 5.09, 0.63, 25),
    FieldSpec("tributacao_municipal.valor_issqn_apurado", "tributacao_municipal", "ISSQN APURADO", 15.62, 16.37, 5.09, 0.63),
    FieldSpec(
        key="tributacao_municipal.mensagem_nao_sujeita_issqn",
        block="tributacao_municipal",
        label=None,
        x_cm=0.30,
        y_top_cm=14.43,
        width_cm=20.40,
        height_cm=0.32,
        kind="fixed_text",
        optional=True,
        fixed_text="TRIBUTAÇÃO MUNICIPAL (ISSQN) - OPERAÇÃO NÃO SUJEITA AO ISSQN",
    ),

    # ============================================================
    # Tributação Federal - Exceto CBS
    # ============================================================

    FieldSpec("block.tributacao_federal.title", "tributacao_federal", None, 0.30, 17.02, 5.09, 0.63, kind="block_title", shaded=True, fixed_text="TRIBUTAÇÃO FEDERAL (EXCETO CBS)"),
    FieldSpec("tributacao_federal.valor_retencao_irrf", "tributacao_federal", "IRRF", 5.41, 17.02, 5.09, 0.63),
    FieldSpec("tributacao_federal.valor_retencao_contribuicao_previdenciaria", "tributacao_federal", "CONTRIBUIÇÃO PREVIDENCIÁRIA - RETIDA", 10.51, 17.02, 5.09, 0.63),
    FieldSpec("tributacao_federal.valor_retencao_csll", "tributacao_federal", "CONTRIBUIÇÕES SOCIAIS - RETIDAS", 15.62, 17.02, 5.09, 0.63),
    FieldSpec("tributacao_federal.valor_pis_debito_apuracao_propria", "tributacao_federal", "PIS - DÉBITO APURAÇÃO PRÓPRIA", 0.30, 17.67, 5.09, 0.63, optional=True),
    FieldSpec("tributacao_federal.valor_cofins_debito_apuracao_propria", "tributacao_federal", "COFINS - DÉBITO APURAÇÃO PRÓPRIA", 5.41, 17.67, 5.09, 0.63, optional=True),
    FieldSpec("tributacao_federal.tipo_retencao_pis_cofins", "tributacao_federal", "DESCRIÇÃO CONTRIB. SOCIAIS - RETIDAS", 10.51, 17.67, 10.19, 0.63, 35, optional=True),

    # ============================================================
    # Tributação IBS / CBS
    # ============================================================

    FieldSpec("block.tributacao_ibs_cbs.title", "tributacao_ibs_cbs", None, 0.30, 18.32, 5.09, 0.63, kind="block_title", shaded=True, fixed_text="TRIBUTAÇÃO IBS / CBS"),
    FieldSpec("tributacao_ibs_cbs.cst_cclass_trib", "tributacao_ibs_cbs", "CST / cClassTrib", 5.41, 18.32, 5.09, 0.63, 12),
    FieldSpec("tributacao_ibs_cbs.indicador_operacao_incidencia", "tributacao_ibs_cbs", "INDICADOR DE OPERAÇÃO / CÓDIGO IBGE INCIDÊNCIA / MUNICÍPIO INCIDÊNCIA / SIGLA UF", 10.51, 18.32, 10.19, 0.63, 56),
    FieldSpec("tributacao_ibs_cbs.exclusoes_reducoes_base_calculo", "tributacao_ibs_cbs", "EXCLUSÕES E REDUÇÕES DA BASE DE CÁLCULO", 0.30, 18.96, 5.09, 0.63),
    FieldSpec("tributacao_ibs_cbs.base_calculo_apos_exclusoes_reducoes", "tributacao_ibs_cbs", "BASE DE CÁLCULO APÓS EXCLUSÕES E REDUÇÕES", 5.41, 18.96, 5.09, 0.63),
    FieldSpec("tributacao_ibs_cbs.reducao_aliquota_ibs_cbs", "tributacao_ibs_cbs", "RED. ALÍQUOTA IBS / RED. ALÍQUOTA CBS", 10.51, 18.96, 5.09, 0.63),
    FieldSpec("tributacao_ibs_cbs.aliquota_ibs_uf_mun", "tributacao_ibs_cbs", "ALÍQUOTA - IBS UF / IBS MUN", 15.62, 18.96, 5.09, 0.63),
    FieldSpec("tributacao_ibs_cbs.aliquota_efetiva_municipal_ibs", "tributacao_ibs_cbs", "ALÍQ. EFETIVA MUNICIPAL - IBS", 0.30, 19.61, 5.09, 0.63),
    FieldSpec("tributacao_ibs_cbs.valor_apurado_municipal_ibs", "tributacao_ibs_cbs", "VALOR APURADO MUNICIPAL - IBS", 5.41, 19.61, 5.09, 0.63),
    FieldSpec("tributacao_ibs_cbs.aliquota_efetiva_estadual_ibs", "tributacao_ibs_cbs", "ALÍQ. EFETIVA ESTADUAL - IBS", 10.51, 19.61, 5.09, 0.63),
    FieldSpec("tributacao_ibs_cbs.valor_apurado_estadual_ibs", "tributacao_ibs_cbs", "VALOR APURADO ESTADUAL - IBS", 15.62, 19.61, 5.09, 0.63),
    FieldSpec("tributacao_ibs_cbs.valor_total_ibs", "tributacao_ibs_cbs", "VALOR TOTAL APURADO - IBS", 0.30, 20.26, 5.09, 0.63),
    FieldSpec("tributacao_ibs_cbs.aliquota_cbs", "tributacao_ibs_cbs", "ALÍQUOTA - CBS", 5.41, 20.26, 5.09, 0.63),
    FieldSpec("tributacao_ibs_cbs.aliquota_efetiva_cbs", "tributacao_ibs_cbs", "ALÍQUOTA EFETIVA - CBS", 10.51, 20.26, 5.09, 0.63),
    FieldSpec("tributacao_ibs_cbs.valor_total_cbs", "tributacao_ibs_cbs", "VALOR TOTAL APURADO - CBS", 15.62, 20.26, 5.09, 0.63),

    # ============================================================
    # Valor Total da NFS-e
    # ============================================================

    FieldSpec("block.totais.title", "totais", None, 0.30, 20.90, 5.09, 0.67, kind="block_title", shaded=True, fixed_text="VALOR TOTAL DA NFS-e"),
    FieldSpec("totais.valor_operacao_servico", "totais", "VALOR DA OPERAÇÃO / SERVIÇO", 5.41, 20.90, 5.09, 0.67),
    FieldSpec("totais.desconto_incondicionado", "totais", "DESCONTO INCONDICIONADO", 10.51, 20.90, 5.09, 0.67),
    FieldSpec("totais.desconto_condicionado", "totais", "DESCONTO CONDICIONADO", 15.62, 20.90, 5.09, 0.67),
    FieldSpec("totais.total_retencoes_issqn_federais", "totais", "TOTAL DAS RETENÇÕES (ISSQN / FEDERAIS)", 0.30, 21.59, 5.09, 0.67),
    FieldSpec("totais.valor_liquido_nfse", "totais", "VALOR LÍQUIDO DA NFS-e", 5.41, 21.59, 5.09, 0.67),
    FieldSpec("totais.total_ibs_cbs", "totais", "TOTAL DO IBS/CBS", 10.51, 21.59, 5.09, 0.67),
    FieldSpec("totais.valor_liquido_nfse_mais_ibs_cbs", "totais", "VALOR LÍQUIDO DA NFS-e + IBS/CBS", 15.62, 21.59, 5.09, 0.67, shaded=True),

    # ============================================================
    # Informações Complementares
    # ============================================================

    FieldSpec(
        key="block.informacoes_complementares.title",
        block="informacoes_complementares",
        label=None,
        x_cm=0.30,
        y_top_cm=22.27,
        width_cm=20.40,
        height_cm=0.39,
        kind="block_title",
        shaded=True,
        fixed_text="INFORMAÇÕES COMPLEMENTARES",
    ),
    FieldSpec(
        key="informacoes_complementares.texto",
        block="informacoes_complementares",
        label=None,
        x_cm=0.30,
        y_top_cm=22.68,
        width_cm=20.40,
        height_cm=5.42,
        max_chars=2000,
        multiline=True,
        dynamic_height=True,
        notes=(
            "A tabela informa altura mínima de 0,39 cm; para renderização, "
            "o campo deve ocupar o espaço disponível até o canhoto."
        ),
    ),

    # ============================================================
    # Canhoto
    # ============================================================

    FieldSpec("block.canhoto.title", "canhoto", None, 0.30, 28.10, 20.40, 0.67, kind="block_title", shaded=True, fixed_text="CANHOTO", optional=True),
    FieldSpec("canhoto.data_cientificacao", "canhoto", "DATA CIENTIFICAÇÃO", 0.30, 28.10, 5.09, 0.67, optional=True),
    FieldSpec("canhoto.identificacao_assinatura", "canhoto", "IDENTIFICAÇÃO E ASSINATURA", 5.41, 28.10, 5.09, 0.67, optional=True),
    FieldSpec("canhoto.numero_nfse_chave_nfse", "canhoto", "Nº NFS-e / CHAVE NFS-e", 10.51, 28.10, 10.19, 0.67, 66, optional=True),
]


FIELD_BY_KEY: dict[str, FieldSpec] = {
    field.key: field for field in FIELD_SPECS
}

BLOCK_BY_KEY: dict[str, BlockSpec] = {
    block.key: block for block in BLOCK_SPECS
}