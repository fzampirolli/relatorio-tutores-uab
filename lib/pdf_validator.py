"""Valida se um PDF é um Relatório Mensal de Atividades de Tutoria UAB
processável, e calcula um score de confiança de extração.

Não tentamos alcançar 100% de acerto por regex — o mesmo modelo circula em
variantes ligeiramente diferentes por curso/polo (redação, numeração de
seção, presença ou não do campo "Polo") e alguns tutores preenchem o PDF de
forma manuscrita ou o entregam como foto. Em vez disso, cada relatório recebe
um score objetivo e qualquer relatório abaixo do limiar de confiança é
marcado para revisão manual no relatório final, em vez de aparecer como se
tivesse sido auditado com sucesso.
"""

from lib.pdf_parser import PERGUNTAS
from lib.schema import ResultadoValidacao

MARCADORES_MODELO = [
    "MINISTÉRIO DA EDUCAÇÃO",
    "UNIVERSIDADE ABERTA DO BRASIL",
    "RELATÓRIO MENSAL DE ATIVIDADES DE TUTORIA",
    "DECLARAÇÕES FORMAIS",
]

MIN_CHARS_POR_PAGINA = 200  # abaixo disso, a página provavelmente não tem camada de texto (scan/foto)

# pesos do score de confiança de extração (somam 1.0)
PESO_IDENTIFICACAO = 0.5
PESO_MARCADORES = 0.2
PESO_PERGUNTAS = 0.3

LIMIAR_VALIDO = 0.6


def _tem_camada_de_texto(chars_por_pagina: list) -> bool:
    if not chars_por_pagina:
        return False
    media = sum(chars_por_pagina) / len(chars_por_pagina)
    return media >= MIN_CHARS_POR_PAGINA


def _score_marcadores(raw_upper: str) -> float:
    encontrados = sum(1 for m in MARCADORES_MODELO if m in raw_upper)
    return encontrados / len(MARCADORES_MODELO)


def _score_identificacao(campos: dict) -> float:
    obrigatorios = ["nome", "cpf", "curso"]
    presentes = sum(1 for c in obrigatorios if campos.get(c))
    mes_ok = 1 if campos.get("mes_numero") else 0
    return (presentes + mes_ok) / (len(obrigatorios) + 1)


def _score_perguntas(respostas: dict) -> float:
    if not respostas:
        return 0.0
    detectadas = sum(1 for r in respostas.values() if r["valor"])
    return detectadas / len(PERGUNTAS)


def validar(campos: dict, raw: str, assinado: bool) -> ResultadoValidacao:
    motivos = []

    if not _tem_camada_de_texto(campos.get("chars_por_pagina", [])):
        motivos.append(
            "PDF sem camada de texto suficiente — provável digitalização, foto ou "
            "documento manuscrito. Não é possível extrair os dados automaticamente."
        )
        return ResultadoValidacao(valido=False, score=0.0, motivos=motivos)

    raw_upper = raw.upper()
    score_marc = _score_marcadores(raw_upper)
    if score_marc < 1.0:
        motivos.append(
            f"Apenas {score_marc:.0%} dos marcadores esperados do modelo oficial foram "
            "encontrados no PDF — pode ser um modelo desatualizado ou fora do padrão."
        )

    score_ident = _score_identificacao(campos)
    if score_ident < 1.0:
        faltando = [c for c in ("nome", "cpf", "curso") if not campos.get(c)]
        if not campos.get("mes_numero"):
            faltando.append("mês/ano")
        motivos.append("Campos de identificação não encontrados: " + ", ".join(faltando))

    score_perg = _score_perguntas(campos.get("respostas", {}))
    if score_perg < 1.0:
        motivos.append(
            f"{score_perg:.0%} das perguntas de sim/não do formulário foram reconhecidas "
            "automaticamente; o restante requer conferência manual."
        )

    if not assinado:
        motivos.append("Relatório sem assinatura digital (ITI/GOV.BR) no PDF.")

    score = (
        PESO_IDENTIFICACAO * score_ident
        + PESO_MARCADORES * score_marc
        + PESO_PERGUNTAS * score_perg
    )

    return ResultadoValidacao(valido=score >= LIMIAR_VALIDO, score=round(score, 2), motivos=motivos)


def documento_assinado(doc) -> bool:
    """Verifica campos de assinatura digital reais no AcroForm do PDF (não
    depende de OCR/carimbo visual, que é uma imagem e não aparece no texto
    extraído). O nome do campo de assinatura (ex.: "Signature1") é apenas o
    identificador interno do widget no PDF, não o nome do signatário — para
    validar a identidade do certificado seria necessário um parser de
    assinatura ICP-Brasil (ex.: pyHanko), fora do escopo desta versão."""
    for page in doc:
        for widget in page.widgets() or []:
            if widget.field_type_string == "Signature" and widget.is_signed:
                return True
    return False
