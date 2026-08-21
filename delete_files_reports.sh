#!/usr/bin/env bash
# Cron de segurança: remove pastas órfãs em tmp/ deixadas por execuções que
# falharam ou foram interrompidas antes do upload.php conseguir limpá-las.
# Nada em tmp/ deveria sobreviver mais que alguns minutos em uso normal.
#
# Sugestão de crontab (a cada 30 min):
#   */30 * * * * /caminho/para/relatorio-tutores-uab/delete_files_reports.sh >> /caminho/para/relatorio-tutores-uab/logs/limpeza.log 2>&1

set -euo pipefail
cd "$(dirname "$0")"

IDADE_MINIMA_MINUTOS=60

if [ -d tmp ]; then
    find tmp -mindepth 1 -maxdepth 1 -type d -mmin "+${IDADE_MINIMA_MINUTOS}" -print -exec rm -rf {} \;
fi
