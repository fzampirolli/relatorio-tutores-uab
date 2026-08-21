"""Extração segura do zip enviado pelo usuário.

Protege contra:
- zip-slip (entradas com "../" que escapam do diretório de destino)
- zip-bomb (limite de nº de arquivos e de tamanho total descomprimido)
- arquivos que não são PDF de verdade (checa a assinatura binária %PDF-,
  não apenas a extensão .pdf do nome do arquivo)
"""

import os
import zipfile

MAX_ARQUIVOS = 500
MAX_TAMANHO_TOTAL_DESCOMPRIMIDO = 300 * 1024 * 1024  # 300 MB
MAX_TAMANHO_POR_ARQUIVO = 20 * 1024 * 1024  # 20 MB
PDF_MAGIC = b"%PDF-"


class ZipInvalido(Exception):
    pass


def _destino_seguro(diretorio_base: str, nome_entrada: str) -> str:
    destino = os.path.normpath(os.path.join(diretorio_base, nome_entrada))
    if not destino.startswith(os.path.normpath(diretorio_base) + os.sep):
        raise ZipInvalido(f"Entrada de zip fora do diretório de destino: {nome_entrada!r}")
    return destino


def extrair_pdfs(caminho_zip: str, diretorio_destino: str) -> list:
    """Extrai apenas os arquivos .pdf válidos do zip para diretorio_destino,
    preservando a subpasta (curso/polo) de origem. Retorna lista de
    (caminho_absoluto, subpasta_origem)."""
    if not zipfile.is_zipfile(caminho_zip):
        raise ZipInvalido("O arquivo enviado não é um .zip válido.")

    extraidos = []
    with zipfile.ZipFile(caminho_zip) as zf:
        entradas = [i for i in zf.infolist() if not i.is_dir()]

        if len(entradas) > MAX_ARQUIVOS:
            raise ZipInvalido(f"Zip contém {len(entradas)} arquivos (limite: {MAX_ARQUIVOS}).")

        tamanho_total = sum(i.file_size for i in entradas)
        if tamanho_total > MAX_TAMANHO_TOTAL_DESCOMPRIMIDO:
            raise ZipInvalido("Tamanho total descomprimido do zip excede o limite permitido.")

        os.makedirs(diretorio_destino, exist_ok=True)

        for info in entradas:
            if not info.filename.lower().endswith(".pdf"):
                continue
            if info.file_size > MAX_TAMANHO_POR_ARQUIVO:
                continue
            if os.path.isabs(info.filename) or ".." in info.filename.split("/"):
                raise ZipInvalido(f"Entrada de zip suspeita: {info.filename!r}")

            destino = _destino_seguro(diretorio_destino, info.filename)
            os.makedirs(os.path.dirname(destino), exist_ok=True)

            with zf.open(info) as origem, open(destino, "wb") as saida:
                cabecalho = origem.read(len(PDF_MAGIC))
                if cabecalho != PDF_MAGIC:
                    continue  # não é um PDF de verdade (extensão renomeada); ignora
                saida.write(cabecalho)
                saida.write(origem.read())

            # Usa só o nome da pasta imediata (curso/polo), não o caminho completo —
            # zips reais costumam ter uma pasta "wrapper" com o nome do próprio zip
            # antes da pasta do curso (ex.: "Relatórios ... - julho-26/C10/arquivo.pdf").
            subpasta = os.path.basename(os.path.dirname(info.filename)) or "(raiz)"
            extraidos.append((destino, subpasta))

    if not extraidos:
        raise ZipInvalido("Nenhum arquivo .pdf válido foi encontrado dentro do zip.")

    return extraidos
