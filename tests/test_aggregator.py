import os

import pymupdf as fitz

from lib import aggregator, pdf_parser, pdf_validator

FIXTURES = os.path.join(os.path.dirname(__file__), "fixtures", "samples")


def _montar(nome_arquivo, pasta_origem, mes_referencia=7, ano_referencia=2026):
    doc = fitz.open(os.path.join(FIXTURES, nome_arquivo))
    try:
        campos = pdf_parser.parse_relatorio(doc)
        raw = "\n".join(pdf_parser.extrair_texto_paginas(doc))
        assinado = pdf_validator.documento_assinado(doc)
        validacao = pdf_validator.validar(campos, raw, assinado)
        return aggregator.montar_relatorio(
            campos, nome_arquivo, pasta_origem, validacao, assinado,
            mes_referencia, ano_referencia,
        )
    finally:
        doc.close()


def _codigos(relatorio):
    return {p.codigo for p in relatorio.pendencias}


def test_relatorio_sem_assinatura_gera_pendencia_critica():
    r = _montar("teonia_sem_assinatura.pdf", "IEMT")
    assert "sem_assinatura" in _codigos(r)
    assert r.tem_pendencia_critica


def test_risco_evasao_nao_comunicado_e_critico():
    # Ana identificou risco de evasão (IV.1 = Sim) mas a lista não foi
    # encaminhada à coordenação (IV.2 = "Não foi enviada") — contradição real
    # observada no lote de julho/2026.
    r = _montar("ana_polo_vazio_assinado.pdf", "IEMT")
    assert "risco_evasao_nao_comunicado" in _codigos(r)
    assert r.tem_pendencia_critica


def test_risco_evasao_nao_identificado_nao_gera_a_pendencia():
    # Francisco respondeu "Não" para risco de evasão identificado — a regra
    # não deve disparar nesse caso.
    r = _montar("francisco_completo_assinado.pdf", "EQ")
    assert "risco_evasao_nao_comunicado" not in _codigos(r)


def test_mes_divergente_e_critico():
    r = _montar("elaine_mes_divergente.pdf", "C10", mes_referencia=7, ano_referencia=2026)
    assert "mes_divergente" in _codigos(r)
    assert r.tem_pendencia_critica


def test_polo_vazio_e_apenas_aviso():
    r = _montar("ana_polo_vazio_assinado.pdf", "IEMT")
    codigos = {p.codigo: p.severidade for p in r.pendencias}
    assert codigos.get("polo_vazio") == "aviso"


def test_foto_sem_texto_vira_pdf_nao_processavel():
    r = _montar("foto_sem_texto.pdf", "EQ")
    assert "pdf_nao_processavel" in _codigos(r)
    assert r.tem_pendencia_critica


def test_agregar_lote_resume_corretamente():
    relatorios = [
        _montar("francisco_completo_assinado.pdf", "EQ"),
        _montar("teonia_sem_assinatura.pdf", "IEMT"),
        _montar("ana_polo_vazio_assinado.pdf", "IEMT"),
    ]
    resumo = aggregator.agregar_lote(relatorios)
    assert resumo["total"] == 3
    assert resumo["sem_assinatura"] == 1
    assert resumo["por_pasta"]["IEMT"]["total"] == 2
    assert resumo["duplicados"] == []
