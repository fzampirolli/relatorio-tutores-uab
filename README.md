# relatorio-tutores-uab

Auditoria automática dos Relatórios Mensais de Atividades de Tutoria UAB
(SITE/UFABC — Superintendência de Inovações e Tecnologias Educacionais).
Recebe um `.zip` com os relatórios em PDF enviados pelos
tutores, valida se cada PDF é o modelo oficial, extrai os campos relevantes
e gera um relatório de auditoria em HTML — com destaque para pendências
(sem assinatura, mês divergente, risco de evasão não comunicado à
coordenação, respostas negativas sem justificativa, etc.).

**Nada do que é enviado ou gerado permanece no servidor.** O único dado
persistente é uma linha por execução em `logs/execucoes.log`.

Deploy público em `mctest.ufabc.edu.br`, no mesmo padrão do
[AcompanhaTutorUAB](https://github.com/fzampirolli/AcompanhaTutorUAB): PHP
como camada web (sem framework), delegando o processamento a um script
Python via shell.

## Como funciona

```
index.php  →  upload.php  →  run_script.sh  →  script.py
 (form)        (recebe o        (valida args,      (extrai zip, valida e
                zip, chama       chama o venv        analisa cada PDF,
                o script,        do projeto)          gera o HTML final)
                devolve o
                HTML, apaga
                tudo)
```

1. `index.php` — formulário público (sem login): upload do `.zip` + mês/ano
   de referência do lote (sugerido automaticamente a partir do nome do
   arquivo, mas sempre conferido/corrigido pelo usuário antes de enviar).
2. `upload.php` — salva o zip em `tmp/<execução>/`, chama `run_script.sh`,
   devolve o HTML gerado como download, e **apaga o diretório temporário
   inteiro em seguida**, sucesso ou erro.
3. `script.py` (via `lib/`) —
   - `zip_handler.py`: extrai só `.pdf` de verdade (checa a assinatura
     binária `%PDF-`, não a extensão), com proteção contra zip-slip e
     zip-bomb.
   - `pdf_parser.py`: extrai Nome/CPF/Curso/Polo/Mês/Ano e as respostas de
     sim/não relevantes para auditoria.
   - `pdf_validator.py`: calcula um *score de confiança* de extração por
     PDF e verifica a assinatura digital pelo AcroForm do PDF (não por
     OCR/imagem — ver `modelos/mapa_campos.md`).
   - `aggregator.py`: aplica as regras de pendência e monta o resumo do
     lote.
   - `report_builder.py`: renderiza `modelos/template_relatorio.html.j2`
     em um HTML autocontido (CSS inline, sem dependências externas).

Veja `modelos/mapa_campos.md` para o mapeamento completo de campos, as
variações reais de formatação encontradas em produção (mês por extenso,
numérico, com sublinhados de preenchimento, etc.) e as limitações
conhecidas (variante "AEE" ainda não é totalmente calibrada).

## Deploy no mctest

### Arquitetura real do servidor (descoberta em produção, ago/2026)

`mctest.ufabc.edu.br` (porta 443, Apache real) é um proxy reverso: a raiz
vai para Django (`127.0.0.1:8080`), mas alguns paths — `/UAB/`, `/ENEM/`,
`/LabMoodle/`, `/lattes2memorial/`, e agora `/relatorio-tutores-uab/` —
têm uma exceção em `/etc/apache2/sites-enabled/mctest.conf` apontando para
uma **segunda instância Apache** em `127.0.0.1:8000`, que serve estático/PHP
direto de `/var/www/html/<projeto>/` (qualquer subpasta ali já funciona
nessa porta interna, sem config adicional por projeto). Um novo projeto
PHP precisa de duas linhas em `mctest.conf`, no bloco `<VirtualHost *:443>`,
**antes** do `ProxyPass / http://127.0.0.1:8080/` global:

```apache
ProxyPass /relatorio-tutores-uab/ http://127.0.0.1:8000/relatorio-tutores-uab/
ProxyPassReverse /relatorio-tutores-uab/ http://127.0.0.1:8000/relatorio-tutores-uab/
```

A instância da porta 8000 não tem `<VirtualHost>` próprio (cai no bloco
global `<Directory /var/www/>` do `apache2.conf`, que tem `AllowOverride
None` por padrão no Ubuntu) — **o `.htaccess` deste projeto é ignorado
nessa instância.** Por isso existe também um `conf-available` dedicado:
bloqueia dotfiles (`.git`, `.htaccess`, `.user.ini`) só para esse diretório,
sem mexer no comportamento global:

```bash
cat > /etc/apache2/conf-available/relatorio-tutores-uab-security.conf <<'EOF'
<Directory /var/www/html/relatorio-tutores-uab>
    <FilesMatch "^\.(git|htaccess|htpasswd|user\.ini)">
        Require all denied
    </FilesMatch>
</Directory>
<DirectoryMatch "/var/www/html/relatorio-tutores-uab/\.git">
    Require all denied
</DirectoryMatch>
EOF
a2enconf relatorio-tutores-uab-security
apache2ctl configtest && systemctl reload apache2
```

### ⚠️ Nunca clone o git direto dentro do docroot

Na primeira tentativa de deploy isso foi feito (`git clone` direto em
`/var/www/html/relatorio-tutores-uab/`) e, por causa do `AllowOverride
None` acima, o `.git/` ficou **publicamente baixável** por HTTP até ser
percebido e removido — incluindo os PDFs de teste com CPF real do
histórico. O `conf-available` acima cobre esse caso mesmo que aconteça de
novo, mas o padrão de deploy correto evita o problema por completo:

```bash
# clona/atualiza FORA do docroot, uma vez só:
mkdir -p /home/operador/deploy
cd /home/operador/deploy
git clone https://github.com/fzampirolli/relatorio-tutores-uab.git   # primeira vez
# nas próximas vezes:  cd relatorio-tutores-uab && git pull

# sincroniza só os arquivos pro docroot, sem o .git/, preservando
# venv/, tmp/ e logs/ já existentes lá:
rsync -a --delete \
  --exclude='.git' --exclude='venv' --exclude='tmp' --exclude='logs' \
  /home/operador/deploy/relatorio-tutores-uab/ /var/www/html/relatorio-tutores-uab/

chown -R www-data:www-data /var/www/html/relatorio-tutores-uab
```

### Pré-requisitos no servidor

- PHP com `exec()` habilitado (mesma configuração já usada pelo
  AcompanhaTutorUAB).
- Python 3.9+ com um virtualenv em `./venv` contendo as dependências de
  `requirements.txt` (`run_script.sh` usa `./venv/bin/python3` se existir,
  senão cai para `python3` do sistema):

  ```bash
  python3 -m venv venv
  ./venv/bin/pip install -r requirements.txt
  ```

- `.user.ini` já resolve `upload_max_filesize`/`post_max_size`/`max_execution_time`
  para lotes reais (~13 MB) — mas depende de `user_ini.cache_ttl` (até 5 min
  para valer após deploy) e é ignorado sob `AllowOverride None`/php-fpm sem
  suporte a `.user.ini`; confirme testando um upload real depois do deploy.
- Cron de segurança (limpa `tmp/` órfã de execuções que travaram):

  ```
  */30 * * * * /caminho/para/relatorio-tutores-uab/delete_files_reports.sh >> /caminho/para/relatorio-tutores-uab/logs/limpeza.log 2>&1
  ```

## Rodando localmente

```bash
python3 -m venv venv
./venv/bin/pip install -r requirements.txt -r requirements-dev.txt  # dev inclui pytest
./venv/bin/pytest tests/ -v

# processar um zip manualmente, sem PHP:
./venv/bin/python3 script.py caminho/lote.zip 7 2026 /tmp/trabalho saida.html
```

### Testando o fluxo completo (PHP + Python) sem instalar nada no sistema

Se você não tem PHP instalado localmente (e não quer instalar via `apt`),
suba um container efêmero com Docker — ele não deixa nada no seu sistema:

```bash
docker run --rm -p 8000:8000 -v "$PWD":/app -w /app php:8.2-cli bash -c "
  apt-get update -qq && apt-get install -y -qq python3 python3-venv >/dev/null &&
  python3 -m venv venv && ./venv/bin/pip install -q -r requirements.txt &&
  php -d upload_max_filesize=25M -d post_max_size=30M -d max_execution_time=300 -S 0.0.0.0:8000
"
```

Depois, em outro terminal: abra `http://localhost:8000` no navegador e faça
o upload normalmente, ou simule via curl (útil para automatizar testes):

```bash
curl -o auditoria.html \
  -F "zip_relatorios=@caminho/lote.zip;type=application/zip" \
  -F "mes_referencia=7" -F "ano_referencia=2026" \
  http://localhost:8000/upload.php
```

Os `-d upload_max_filesize=25M -d post_max_size=30M` acima **são
obrigatórios** — o default do PHP (`post_max_size=8M`) rejeita silenciosamente
lotes reais (~13 MB) antes mesmo de chegar em `upload.php`. Confirme que o
`php.ini` do mctest tem esses mesmos limites elevados (ver seção "Deploy no
mctest" acima).

## Aviso sobre os fixtures de teste

`tests/fixtures/samples/` contém PDFs reais (nome, CPF, curso) extraídos do
lote de julho/2026 para calibrar e testar o parser contra casos de
produção — não são sintéticos. Se este repositório for publicado, considere
mantê-lo **privado** ou substituir os fixtures por dados fictícios
equivalentes.
