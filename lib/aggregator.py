"""Constrói um RelatorioTutor a partir dos campos extraídos de um PDF,
aplica as regras de pendência, e produz o resumo agregado do lote."""

from lib.schema import Pendencia, RelatorioTutor


def _pendencias_resposta(chave: str, rotulo: str, resposta: dict) -> list:
    """Sinaliza pergunta marcada como 'Não'/negativa sem justificativa preenchida."""
    valor = resposta.get("valor", "")
    justificativa = resposta.get("justificativa", "")
    if not valor:
        return [Pendencia(
            f"{chave}_nao_identificada", "aviso",
            f'"{rotulo}": resposta não identificada automaticamente — conferir manualmente no PDF.',
        )]
    eh_negativa = valor.lower().startswith(("não", "nao"))
    if eh_negativa and not justificativa:
        return [Pendencia(
            f"{chave}_sem_justificativa", "aviso",
            f'"{rotulo}": marcado "{valor}" sem justificativa preenchida no relatório.',
        )]
    return []


PERGUNTAS_ROTULO = {
    "ava_regularidade": "Manteve regularidade de acesso ao AVA",
    "ava_prazo_24h": "Respondeu em até 24h",
    "ava_correcao_72h": "Corrigiu em até 72h",
    "interagiu_forum": "Interagiu no fórum",
    "alinhamento_pedagogico": "Alinhamento pedagógico com o professor",
    "participou_reunioes": "Participou das reuniões de coordenação",
}


def montar_relatorio(campos: dict, arquivo_origem: str, pasta_origem: str,
                      validacao, assinado: bool, mes_referencia: int, ano_referencia: int) -> RelatorioTutor:
    r = RelatorioTutor(
        arquivo_origem=arquivo_origem,
        pasta_origem=pasta_origem,
        validacao=validacao,
        nome=campos.get("nome", ""),
        cpf=campos.get("cpf", ""),
        curso=campos.get("curso", ""),
        polo=campos.get("polo", ""),
        mes=campos.get("mes", ""),
        ano=campos.get("ano", ""),
        assinado=assinado,
        respostas=campos.get("respostas", {}),
    )

    pendencias = []

    if not validacao.valido:
        pendencias.append(Pendencia(
            "pdf_nao_processavel", "critica",
            "PDF não pôde ser validado como o modelo oficial (ver motivos da validação) "
            "— possivelmente digitalizado, foto, ou fora do padrão.",
        ))

    if not assinado:
        pendencias.append(Pendencia(
            "sem_assinatura", "critica",
            "Relatório sem assinatura digital ITI/GOV.BR.",
        ))

    if not r.polo:
        pendencias.append(Pendencia(
            "polo_vazio", "aviso",
            "Campo 'Polo' não preenchido (ou ausente nesta variante do modelo).",
        ))

    mes_num = campos.get("mes_numero")
    if mes_num and (mes_num != mes_referencia or (campos.get("ano") and campos["ano"] != str(ano_referencia))):
        pendencias.append(Pendencia(
            "mes_divergente", "critica",
            f"Relatório indica {campos.get('mes')}/{campos.get('ano')}, mas o lote é de "
            f"referência {mes_referencia:02d}/{ano_referencia}.",
        ))
    elif not mes_num:
        pendencias.append(Pendencia(
            "mes_nao_identificado", "aviso",
            "Não foi possível identificar o campo MÊS/ANO do relatório.",
        ))

    for chave, rotulo in PERGUNTAS_ROTULO.items():
        pendencias.extend(_pendencias_resposta(chave, rotulo, r.respostas.get(chave, {})))

    risco_id = r.respostas.get("risco_evasao_identificado", {}).get("valor", "")
    risco_enc = r.respostas.get("risco_evasao_encaminhado", {}).get("valor", "")
    if risco_id == "Sim" and risco_enc and risco_enc != "Sim - Data do encaminhamento":
        pendencias.append(Pendencia(
            "risco_evasao_nao_comunicado", "critica",
            "Risco de evasão identificado, mas a lista não foi encaminhada à Coordenação de "
            f'Tutoria (resposta: "{risco_enc}").',
        ))

    r.pendencias = pendencias
    return r


def agregar_lote(relatorios: list) -> dict:
    """Resumo do lote inteiro para o cabeçalho do relatório final."""
    total = len(relatorios)
    com_pendencia_critica = sum(1 for r in relatorios if r.tem_pendencia_critica)
    sem_assinatura = sum(1 for r in relatorios if not r.assinado)
    nao_processados = sum(1 for r in relatorios if not r.validacao.valido)

    por_pasta = {}
    for r in relatorios:
        por_pasta.setdefault(r.pasta_origem, {"total": 0, "pendencias_criticas": 0})
        por_pasta[r.pasta_origem]["total"] += 1
        if r.tem_pendencia_critica:
            por_pasta[r.pasta_origem]["pendencias_criticas"] += 1

    cpfs = {}
    duplicados = []
    for r in relatorios:
        if not r.cpf:
            continue
        cpfs.setdefault(r.cpf, []).append(r.arquivo_origem)
    for cpf, arquivos in cpfs.items():
        if len(arquivos) > 1:
            duplicados.append({"cpf": cpf, "arquivos": arquivos})

    return {
        "total": total,
        "com_pendencia_critica": com_pendencia_critica,
        "sem_assinatura": sem_assinatura,
        "nao_processados": nao_processados,
        "por_pasta": por_pasta,
        "duplicados": duplicados,
    }
