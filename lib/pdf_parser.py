"""Extração de campos do Relatório Mensal de Atividades de Tutoria UAB.

O texto extraído por PyMuPDF preserva a ordem de leitura mas quebra cada
"célula" de tabela e cada linha de rótulo em uma linha própria (o rótulo
fica numa linha e o valor na(s) linha(s) seguinte(s)). Por isso o parser
trabalha com duas visões do texto:

- ``raw``:  texto por página, concatenado com "\\n" — usado para localizar
  campos onde a quebra de linha rótulo/valor é previsível (Nome, CPF, ...).
- ``flat``: ``raw`` com toda sequência de espaços/quebras de linha colapsada
  em um único espaço — usado para localizar caixas de marcação "( X )",
  que às vezes aparecem com cada palavra da frase em uma linha diferente
  por causa de quebra automática de célula de tabela do Word.
"""

import re

CHECK = r"\(\s*[Xx]\s*\)"


def _flatten(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def extrair_texto_paginas(doc):
    """doc: objeto fitz.Document já aberto. Retorna lista de texto por página."""
    return [page.get_text() for page in doc]


MESES_PT = {
    "janeiro": 1, "fevereiro": 2, "marco": 3, "março": 3, "abril": 4,
    "maio": 5, "junho": 6, "julho": 7, "agosto": 8, "setembro": 9,
    "outubro": 10, "novembro": 11, "dezembro": 12,
}


def normalizar_mes(valor: str):
    """Converte 'julho', 'Julho.', '07', '7' etc. para o número do mês (1-12),
    ou None se não reconhecido."""
    v = valor.strip(" ._-").lower()
    if v.isdigit():
        n = int(v)
        return n if 1 <= n <= 12 else None
    return MESES_PT.get(v)


def extrair_identificacao(raw: str) -> dict:
    campos = {}
    flat = _flatten(raw)

    m = re.search(
        r"MÊS:\s*_*\s*([A-Za-zÇÃÕçãõÁÉÍÓÚáéíóú0-9]+)\s*[_\-,]*\.?\s*ANO:\s*_*\s*(\d{2}\s*\d{2})",
        flat,
    )
    campos["mes"] = m.group(1).strip() if m else ""
    campos["ano"] = re.sub(r"\s+", "", m.group(2)) if m else ""
    campos["mes_numero"] = normalizar_mes(campos["mes"]) if campos["mes"] else None

    m = re.search(r"Nome\s*\n(.+?)\n\s*CPF", raw, re.DOTALL)
    campos["nome"] = m.group(1).strip() if m else ""

    m = re.search(r"CPF\s*\n(.+?)\n\s*Curso", raw, re.DOTALL)
    campos["cpf"] = m.group(1).strip() if m else ""

    # A linha "Polo" e o prefixo "I - " antes de "DAS OBRIGAÇÕES" nem sempre
    # existem (variantes de template, ex.: relatório AEE).
    m = re.search(
        r"Curso\s*\n(.+?)\n\s*(?:Polo\s*\n(.*?)\n\s*)?(?:I\s*-\s*)?DAS OBRIGAÇÕES",
        raw,
        re.DOTALL,
    )
    campos["curso"] = m.group(1).strip() if m else ""
    campos["polo"] = (m.group(2) or "").strip() if m else ""

    return campos


def _janela(flat: str, inicio_pat: str, fim_pat: str) -> str:
    """Recorta o trecho de `flat` entre a primeira ocorrência de inicio_pat
    e a primeira ocorrência de fim_pat depois dela (ou o fim do texto)."""
    m_ini = re.search(inicio_pat, flat)
    if not m_ini:
        return ""
    resto = flat[m_ini.end():]
    m_fim = re.search(fim_pat, resto)
    return resto[: m_fim.start()] if m_fim else resto


def _resposta_marcada(janela: str, opcoes: list) -> str:
    """opcoes: lista de (rotulo, captura_justificativa) na ordem em que
    aparecem no formulário. Retorna o rótulo cuja caixa está marcada com X,
    ou "" se nenhuma."""
    posicoes = []
    for label, _ in opcoes:
        m = re.search(re.escape(label), janela)
        if m:
            posicoes.append((m.start(), label))
    posicoes.sort()

    for i, (pos, label) in enumerate(posicoes):
        prefixo_ini = posicoes[i - 1][0] if i > 0 else 0
        prefixo = janela[prefixo_ini:pos]
        if re.search(CHECK + r"\s*$", prefixo):
            return label
    return ""


def _texto_apos_marcador(janela: str, label_marcado: str, todos_labels: list) -> str:
    """Texto livre digitado logo após o rótulo marcado (ex.: motivo/justificativa),
    até o próximo rótulo de opção, o próximo número de seção, ou o fim da janela.
    Ignora sequências de "_"."""
    m = re.search(re.escape(label_marcado), janela)
    if not m:
        return ""
    resto = janela[m.end():]
    fim = len(resto)
    for lbl in todos_labels:
        if lbl == label_marcado:
            continue
        m2 = re.search(re.escape(lbl), resto)
        if m2:
            fim = min(fim, m2.start())
    trecho = resto[:fim]
    trecho = re.sub(r"_{3,}", " ", trecho)
    trecho = re.sub(r"\s+\d+\s*-?\s*$", "", trecho)  # número da próxima seção que vazou
    return trecho.strip(" .:-\u2014")


# Cada pergunta: início/fim delimitam a janela de busca no texto "achatado".
# opcoes: lista de (rotulo_no_pdf, captura_justificativa).
PERGUNTAS = {
    "ava_regularidade": {
        "inicio": r"Manteve\s+(?:a\s+)?regularidade de acesso ao Ambiente Virtual de Aprendizagem \(AVA\)",
        "fim": r"Respondeu às solicitações individuais",
        "opcoes": [("Sim", False), ("Não, Justifique", True)],
    },
    "ava_prazo_24h": {
        "inicio": r"Respondeu às solicitações individuais dos estudantes no prazo máximo de 24 horas",
        "fim": r"Acompanhou as atividades discentes, corrigiu em até 72 horas",
        "opcoes": [("Sim", False), ("Não, Justifique", True)],
    },
    "ava_correcao_72h": {
        "inicio": r"Acompanhou as atividades discentes, corrigiu em até 72 horas e enviou feedback no\s*prazo estipulado\?",
        "fim": r"Elaborou feedback formativo",
        "opcoes": [("Sim", False), ("Não, Justifique", True)],
    },
    "interagiu_forum": {
        "inicio": r"Interagiu e respondeu todas as mensagens dos discentes no fórum\?",
        "fim": r"BUSCA ATIVA",
        "opcoes": [("Sim", False), ("Não, Justifique", True)],
    },
    "risco_evasao_identificado": {
        "inicio": r"Foram identificados estudantes em situação de risco de evasão ou desistência no\s*período\?",
        "fim": r"A lista de estudantes em risco foi encaminhada",
        "opcoes": [("Sim", False), ("Não", False)],
    },
    "risco_evasao_encaminhado": {
        "inicio": r"A lista de estudantes em risco foi encaminhada à Coordenação de Tutoria no período\?",
        "fim": r"Responda:.*Frequência da busca ativa",
        "opcoes": [
            ("Sim - Data do encaminhamento", False),
            ("Não houve lista", False),
            ("Não foi enviada", True),
        ],
    },
    "alinhamento_pedagogico": {
        "inicio": r"Realizou alinhamento pedagógico com o\(a\) professor\(a\) da disciplina no período\?",
        "fim": r"Descreva brevemente as ações de apoio",
        "opcoes": [("Sim", False), ("Não. Justifique", True)],
    },
    "participou_reunioes": {
        "inicio": r"participou de todas\s+(?:as\s+)?reuniões com a coordenação do curso ou\s*coordenação de tutoria\?",
        "fim": r"Descreva como você interagiu",
        "opcoes": [("Sim", False), ("Não, justifique", True)],
    },
}


def extrair_respostas(raw: str) -> dict:
    flat = _flatten(raw)
    respostas = {}
    for chave, cfg in PERGUNTAS.items():
        janela = _janela(flat, cfg["inicio"], cfg["fim"])
        marcado = _resposta_marcada(janela, cfg["opcoes"])
        justificativa = ""
        captura = dict(cfg["opcoes"]).get(marcado, False)
        if marcado and captura:
            todos_labels = [lbl for lbl, _ in cfg["opcoes"]]
            justificativa = _texto_apos_marcador(janela, marcado, todos_labels)
        respostas[chave] = {"valor": marcado, "justificativa": justificativa}
    return respostas


def parse_relatorio(doc) -> dict:
    """doc: fitz.Document aberto. Retorna dict com identificação + respostas."""
    paginas = extrair_texto_paginas(doc)
    raw = "\n".join(paginas)
    campos = extrair_identificacao(raw)
    campos["respostas"] = extrair_respostas(raw)
    campos["num_paginas"] = len(paginas)
    campos["chars_por_pagina"] = [len(p) for p in paginas]
    return campos
