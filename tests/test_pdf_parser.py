import os

import pymupdf as fitz

from lib import pdf_parser

FIXTURES = os.path.join(os.path.dirname(__file__), "fixtures", "samples")


def _parse(nome_arquivo):
    doc = fitz.open(os.path.join(FIXTURES, nome_arquivo))
    try:
        return pdf_parser.parse_relatorio(doc)
    finally:
        doc.close()


def test_identificacao_basica():
    d = _parse("francisco_completo_assinado.pdf")
    assert d["nome"] == "Francisco Batista do Nascimento"
    assert d["cpf"] == "368.671.968-10"
    assert d["curso"] == "Especialização em Ensino de Química"
    assert d["polo"] == "Diadema e Jd São Carlos"
    assert d["mes_numero"] == 7
    assert d["ano"] == "2026"


def test_polo_pode_ficar_vazio():
    d = _parse("ana_polo_vazio_assinado.pdf")
    assert d["nome"] == "Ana Paula Cleto Marolla"
    assert d["polo"] == ""


def test_mes_numerico_diverge_do_esperado():
    d = _parse("elaine_mes_divergente.pdf")
    assert d["mes"] == "06"
    assert d["mes_numero"] == 6
    assert d["ano"] == "2026"


def test_respostas_sim_nao_francisco():
    d = _parse("francisco_completo_assinado.pdf")
    r = d["respostas"]
    assert r["ava_regularidade"]["valor"] == "Sim"
    assert r["risco_evasao_identificado"]["valor"] == "Não"
    assert r["risco_evasao_encaminhado"]["valor"] == "Não foi enviada"
    assert "consegui entrar em contato" in r["risco_evasao_encaminhado"]["justificativa"]


def test_respostas_sim_nao_ana():
    d = _parse("ana_polo_vazio_assinado.pdf")
    r = d["respostas"]
    assert r["risco_evasao_identificado"]["valor"] == "Sim"
    assert r["risco_evasao_encaminhado"]["valor"] == "Não foi enviada"


def test_normalizar_mes_aceita_variantes():
    assert pdf_parser.normalizar_mes("julho") == 7
    assert pdf_parser.normalizar_mes("Julho.") == 7
    assert pdf_parser.normalizar_mes("JULHO") == 7
    assert pdf_parser.normalizar_mes("07") == 7
    assert pdf_parser.normalizar_mes("7") == 7
    assert pdf_parser.normalizar_mes("13") is None
    assert pdf_parser.normalizar_mes("mesinventado") is None
