"""Renderiza o relatório final de auditoria (HTML autocontido, sem
dependências externas) a partir da lista de RelatorioTutor já processados."""

from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

TEMPLATE_DIR = Path(__file__).resolve().parent.parent / "modelos"


def _severidade_ordem(pendencia):
    return 0 if pendencia.severidade == "critica" else 1


def construir_html(relatorios: list, resumo: dict, mes_referencia: int, ano_referencia: int,
                    nome_lote: str, gerado_em: str) -> str:
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATE_DIR)),
        autoescape=select_autoescape(["html"]),
    )
    template = env.get_template("template_relatorio.html.j2")

    relatorios_ordenados = sorted(
        relatorios,
        key=lambda r: (not r.tem_pendencia_critica, r.pasta_origem, r.nome or r.arquivo_origem),
    )
    for r in relatorios_ordenados:
        r.pendencias.sort(key=_severidade_ordem)

    return template.render(
        relatorios=relatorios_ordenados,
        resumo=resumo,
        mes_referencia=mes_referencia,
        ano_referencia=ano_referencia,
        nome_lote=nome_lote,
        gerado_em=gerado_em,
    )
