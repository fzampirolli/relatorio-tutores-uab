import os

import pymupdf as fitz

from lib import pdf_parser, pdf_validator

FIXTURES = os.path.join(os.path.dirname(__file__), "fixtures", "samples")


def _validar(nome_arquivo):
    doc = fitz.open(os.path.join(FIXTURES, nome_arquivo))
    try:
        campos = pdf_parser.parse_relatorio(doc)
        raw = "\n".join(pdf_parser.extrair_texto_paginas(doc))
        assinado = pdf_validator.documento_assinado(doc)
        return pdf_validator.validar(campos, raw, assinado), assinado
    finally:
        doc.close()


def test_pdf_assinado_digitalmente_e_detectado():
    _, assinado = _validar("francisco_completo_assinado.pdf")
    assert assinado is True


def test_pdf_sem_assinatura_e_detectado():
    _, assinado = _validar("teonia_sem_assinatura.pdf")
    assert assinado is False


def test_pdf_normal_e_considerado_valido():
    resultado, _ = _validar("francisco_completo_assinado.pdf")
    assert resultado.valido is True
    assert resultado.score >= pdf_validator.LIMIAR_VALIDO


def test_foto_sem_camada_de_texto_e_rejeitada():
    resultado, _ = _validar("foto_sem_texto.pdf")
    assert resultado.valido is False
    assert resultado.score == 0.0
    assert any("camada de texto" in m for m in resultado.motivos)


def test_modelo_aee_gera_score_mais_baixo_mas_nao_zero():
    # Variante ainda não totalmente calibrada (ver modelos/mapa_campos.md) —
    # continua "válida" (o texto existe e a identificação básica funciona),
    # mas com score reduzido por causa das perguntas de sim/não não reconhecidas.
    resultado, _ = _validar("adriana_modelo_aee.pdf")
    assert resultado.score < 1.0
    assert resultado.score > 0.0
