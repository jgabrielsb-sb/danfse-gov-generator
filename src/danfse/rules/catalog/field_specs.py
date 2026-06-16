from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DanfseFieldSpec:
    domain_path: str
    element: str
    xsd_type: str
    nt_max_length: int | None = None
    complex_type: str | None = None


# Mapeamento principal domínio → XSD para enums e primitivos usados no DANFSe.
FIELD_SPECS: dict[str, DanfseFieldSpec] = {
    "cabecalho.ambiente_gerador": DanfseFieldSpec(
        "cabecalho.ambiente_gerador", "ambGer", "TSAmbGeradorNFSe", 37,
    ),
    "cabecalho.tipo_ambiente": DanfseFieldSpec(
        "cabecalho.tipo_ambiente", "tpAmb", "TSTipoAmbiente", 37,
    ),
    "identificacao.emitente_nfse": DanfseFieldSpec(
        "identificacao.emitente_nfse", "tpEmit", "TSEmitenteDPS", 37,
    ),
    "identificacao.situacao_nfse": DanfseFieldSpec(
        "identificacao.situacao_nfse", "cStat", "TStat", 37,
    ),
    "identificacao.finalidade_nfse": DanfseFieldSpec(
        "identificacao.finalidade_nfse", "finNFSe", "TSFinNFSe", 37,
    ),
    "prestador.regime.simples_nacional": DanfseFieldSpec(
        "prestador.regime.simples_nacional", "opSimpNac", "TSOpSimpNac", 37,
    ),
    "prestador.regime.regime_apuracao": DanfseFieldSpec(
        "prestador.regime.regime_apuracao", "regApTribSN", "TSRegimeApuracaoSimpNac", 77,
    ),
    "prestador.regime.regime_especial": DanfseFieldSpec(
        "prestador.regime.regime_especial", "regEspTrib", "TSRegEspTrib", 37,
    ),
    "tributacao_municipal.tipo_tributacao": DanfseFieldSpec(
        "tributacao_municipal.tipo_tributacao", "tribISSQN", "TSTribISSQN", 37,
    ),
    "tributacao_municipal.regime_especial": DanfseFieldSpec(
        "tributacao_municipal.regime_especial", "regEspTrib", "TSRegEspTrib", 37,
    ),
    "tributacao_municipal.tipo_imunidade": DanfseFieldSpec(
        "tributacao_municipal.tipo_imunidade", "tpImunidade", "TSTipoImunidadeISSQN", 37,
    ),
    "tributacao_municipal.suspensao": DanfseFieldSpec(
        "tributacao_municipal.suspensao", "tpSusp", "TSOpExigSuspensa", 37,
    ),
    "tributacao_municipal.beneficio": DanfseFieldSpec(
        "tributacao_municipal.beneficio", "tpBM", "TSOpTipoBM", 37,
    ),
    "tributacao_municipal.retencao": DanfseFieldSpec(
        "tributacao_municipal.retencao", "tpRetISSQN", "TSTipoRetISSQN", 37,
    ),
    "tributacao_federal.tp_ret_pis_cofins": DanfseFieldSpec(
        "tributacao_federal.tp_ret_pis_cofins", "tpRetPisCofins", "TSTipoRetPISCofins", 35,
    ),
}

# Override manual para finNFSe (ausente no JSON XSD extraído).
ENUM_OVERRIDES: dict[str, dict[str, str]] = {
    "TSFinNFSe": {
        "0": "NFS-e regular",
        "1": "NFS-e de crédito",
        "2": "NFS-e de débito",
    },
}

NT_LIMITS = {
    "enum_short": 37,
    "address": 77,
    "tributacao_desc": 167,
    "servico_desc": 1297,
    "info_compl": 1997,
}

QR_CODE_BASE_URL = "https://www.nfse.gov.br/ConsultaPublica/?tpc=1&chave="
