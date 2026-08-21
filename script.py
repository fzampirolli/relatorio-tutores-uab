#!/usr/bin/env python3
"""Ponto de entrada do pipeline de auditoria de relatórios de tutores UAB.

Uso:
    python3 script.py <zip_enviado> <mes_referencia:1-12> <ano_referencia> \\
                       <diretorio_trabalho> <caminho_html_saida>

Lê o zip enviado pelo formulário, extrai e valida cada PDF, aplica as regras
de pendência e escreve o relatório final em HTML no caminho indicado.
Também grava uma linha em logs/execucoes.log — a única informação que
persiste no servidor além do próprio código.

Códigos de saída: 0 = sucesso, 1 = entrada inválida (zip/args), 2 = erro
interno inesperado.
"""

import os
import sys
import time
import traceback
from datetime import datetime, timedelta, timezone
from pathlib import Path

try:
    from zoneinfo import ZoneInfo
    FUSO_BRASIL = ZoneInfo("America/Sao_Paulo")
except Exception:
    # Fallback se o banco de fusos IANA não estiver instalado no servidor.
    # Brasil (região de São Paulo) não observa mais horário de verão desde 2019,
    # então UTC-3 fixo é correto o ano todo.
    FUSO_BRASIL = timezone(timedelta(hours=-3))

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

import pymupdf as fitz  # noqa: E402

from lib import aggregator, pdf_parser, pdf_validator, report_builder, zip_handler  # noqa: E402

LOG_PATH = BASE_DIR / "logs" / "execucoes.log"


def log(status: str, detalhes: str) -> None:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(FUSO_BRASIL).strftime("%Y-%m-%dT%H:%M:%S%z")
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(f"{timestamp} | STATUS={status} | {detalhes}\n")


def processar(caminho_zip: str, mes_referencia: int, ano_referencia: int,
              diretorio_trabalho: str) -> tuple:
    nome_lote = os.path.basename(caminho_zip)
    diretorio_extracao = os.path.join(diretorio_trabalho, "extraido")

    extraidos = zip_handler.extrair_pdfs(caminho_zip, diretorio_extracao)

    relatorios = []
    for caminho_pdf, subpasta in extraidos:
        doc = fitz.open(caminho_pdf)
        try:
            campos = pdf_parser.parse_relatorio(doc)
            raw = "\n".join(pdf_parser.extrair_texto_paginas(doc))
            assinado = pdf_validator.documento_assinado(doc)
            validacao = pdf_validator.validar(campos, raw, assinado)
        finally:
            doc.close()

        relatorio = aggregator.montar_relatorio(
            campos,
            arquivo_origem=os.path.basename(caminho_pdf),
            pasta_origem=subpasta,
            validacao=validacao,
            assinado=assinado,
            mes_referencia=mes_referencia,
            ano_referencia=ano_referencia,
        )
        relatorios.append(relatorio)

    resumo = aggregator.agregar_lote(relatorios)
    gerado_em = datetime.now(FUSO_BRASIL).strftime("%d/%m/%Y %H:%M")
    html = report_builder.construir_html(
        relatorios, resumo, mes_referencia, ano_referencia, nome_lote, gerado_em
    )
    return html, resumo


def main() -> int:
    if len(sys.argv) != 6:
        sys.stderr.write(
            "uso: script.py <zip> <mes_referencia:1-12> <ano_referencia> "
            "<diretorio_trabalho> <caminho_html_saida>\n"
        )
        return 1

    caminho_zip, mes_ref_s, ano_ref_s, diretorio_trabalho, caminho_saida = sys.argv[1:6]

    try:
        mes_referencia = int(mes_ref_s)
        ano_referencia = int(ano_ref_s)
        if not (1 <= mes_referencia <= 12):
            raise ValueError("mês de referência fora do intervalo 1-12")
    except ValueError as e:
        sys.stderr.write(f"parâmetros de mês/ano inválidos: {e}\n")
        log("ERRO", f"lote={os.path.basename(caminho_zip)} motivo=parametros_invalidos")
        return 1

    inicio = time.monotonic()
    try:
        html, resumo = processar(caminho_zip, mes_referencia, ano_referencia, diretorio_trabalho)
    except zip_handler.ZipInvalido as e:
        sys.stderr.write(f"zip inválido: {e}\n")
        log("ERRO", f"lote={os.path.basename(caminho_zip)} motivo=zip_invalido detalhe=\"{e}\"")
        return 1
    except Exception:
        sys.stderr.write("erro interno inesperado:\n")
        sys.stderr.write(traceback.format_exc())
        log("ERRO", f"lote={os.path.basename(caminho_zip)} motivo=erro_interno")
        return 2

    os.makedirs(os.path.dirname(caminho_saida) or ".", exist_ok=True)
    with open(caminho_saida, "w", encoding="utf-8") as f:
        f.write(html)

    duracao = time.monotonic() - inicio
    log(
        "OK",
        f"lote={os.path.basename(caminho_zip)} referencia={mes_referencia:02d}/{ano_referencia} "
        f"total={resumo['total']} criticas={resumo['com_pendencia_critica']} "
        f"sem_assinatura={resumo['sem_assinatura']} nao_processados={resumo['nao_processados']} "
        f"duracao={duracao:.1f}s",
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
