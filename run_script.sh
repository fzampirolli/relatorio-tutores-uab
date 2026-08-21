#!/usr/bin/env bash
# Wrapper chamado pelo upload.php. Valida os argumentos e delega o
# processamento ao script.py, usando o venv do projeto se existir.
#
# Uso: run_script.sh <zip> <mes_referencia:1-12> <ano_referencia> <diretorio_trabalho> <caminho_html_saida>

set -euo pipefail
cd "$(dirname "$0")"

if [ "$#" -ne 5 ]; then
    echo "run_script.sh: esperado 5 argumentos, recebido $#" >&2
    exit 1
fi

if [ -x "./venv/bin/python3" ]; then
    PYTHON_BIN="./venv/bin/python3"
else
    PYTHON_BIN="python3"
fi

exec "$PYTHON_BIN" ./script.py "$1" "$2" "$3" "$4" "$5"
