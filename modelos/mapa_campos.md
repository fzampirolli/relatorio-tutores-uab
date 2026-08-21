# Mapa de campos — Relatório Mensal de Atividades de Tutoria UAB

Este documento descreve os rótulos fixos do modelo oficial e como cada um é
extraído em `lib/pdf_parser.py`. Foi calibrado contra os 45 PDFs reais do
lote de julho/2026 (ver `tests/fixtures/samples/`), não apenas contra o
modelo "limpo".

## Como o texto é extraído

O PyMuPDF preserva a ordem de leitura, mas quebra cada rótulo e valor de
tabela em linhas separadas — por exemplo:

```
Nome
Francisco Batista do Nascimento
CPF
368.671.968-10
```

Por isso `pdf_parser.py` trabalha com duas visões do texto: `raw` (por
página, com quebras de linha preservadas — usado para Nome/CPF/Curso/Polo) e
`flat` (tudo em uma linha só, espaços colapsados — usado para localizar
caixas de marcação `( X )`, que às vezes aparecem com cada palavra da frase
em uma linha diferente por causa de quebra automática de célula do Word).

## Identificação (tabela "Dados do Bolsista")

| Campo | Regra                                                       | Observações reais do lote de teste                          |
|-------|--------------------------------------------------------------|---------------------------------------------------------------|
| Nome  | entre rótulo `Nome` e `CPF`                                  | sempre presente nos 45 PDFs testados                          |
| CPF   | entre rótulo `CPF` e `Curso`                                  | formatos `000.000.000-00` e `00000000000` (sem pontuação), ambos aceitos como texto livre — sem validação de dígito verificador nesta versão |
| Curso | entre rótulo `Curso` e (`Polo` ou o próximo `DAS OBRIGAÇÕES`) | —                                                              |
| Polo  | entre rótulo `Polo` e `I - DAS OBRIGAÇÕES` (ou variante sem "I -") | **pode estar ausente do modelo** (ex.: relatórios AEE) ou ser deixado em branco pelo tutor — os dois casos geram o mesmo aviso `polo_vazio`, e não são distinguidos nesta versão |
| Mês/Ano | linha `MÊS: ___ ANO: ____` logo abaixo do título           | aceita mês por extenso (`Julho`), abreviado, numérico (`06`), com sublinhados de preenchimento (`__Agosto___`), separado por vírgula ou hífen, e ano com espaço espúrio no meio (`20 26`) — tudo isso foi observado em produção |

## Perguntas de sim/não usadas nas regras de pendência

Cada pergunta é localizada por uma "janela" de texto entre uma frase-âncora
de início e uma de fim (`lib/pdf_parser.py:PERGUNTAS`). Dentro da janela, o
rótulo cuja caixa `( X )` está marcada é identificado pela posição do `(X)`
imediatamente antes do texto do rótulo.

| Chave interna | Pergunta no PDF (seção) | Opções reconhecidas |
|---|---|---|
| `ava_regularidade` | III.1 — Manteve regularidade de acesso ao AVA? | Sim / Não, Justifique |
| `ava_prazo_24h` | III.2 — Respondeu em até 24h? | Sim / Não, Justifique |
| `ava_correcao_72h` | III.3 — Corrigiu em até 72h? | Sim / Não, Justifique |
| `interagiu_forum` | III.5 — Interagiu no fórum? | Sim / Não, Justifique |
| `risco_evasao_identificado` | IV.1 — Risco de evasão identificado? | Sim / Não |
| `risco_evasao_encaminhado` | IV.2 — Lista de risco encaminhada à coordenação? | Sim - Data / Não houve lista / Não foi enviada (+ motivo) |
| `alinhamento_pedagogico` | V.1 — Alinhamento pedagógico com o professor? | Sim / Não. Justifique |
| `participou_reunioes` | V.3 — Participou das reuniões de coordenação? | Sim / Não, justifique |

Quando nenhuma opção é reconhecida (ex.: tutor não marcou nenhuma caixa, ou
a redação da pergunta nesse PDF específico não bate com a âncora), a
resposta fica vazia e vira um **aviso** de "conferir manualmente", em vez de
ser tratada como se fosse "Não" — evitar falso positivo é mais importante
que maximizar cobertura.

## Assinatura digital

**Não é extraída do texto nem de imagem.** O carimbo visual "Documento
assinado digitalmente / Verifique em validar.iti.gov.br" é uma **imagem**
inserida no PDF pela plataforma gov.br — ele não aparece na camada de texto
extraída pelo PyMuPDF. Em vez disso, `pdf_validator.documento_assinado()`
verifica estruturalmente se existe um **campo de assinatura no AcroForm do
PDF** (`widget.field_type_string == "Signature"` e `widget.is_signed`), o
que é o que realmente indica que a plataforma gov.br processou uma
assinatura ICP-Brasil sobre aquele documento. Essa checagem foi validada
contra um caso real no próprio lote de teste (`Teônia_Julho2026.pdf`, sem
nenhum campo de assinatura).

O nome do campo de assinatura (`Signature1`) é só o identificador interno do
widget — **não** é o nome do signatário. Validar a identidade do
certificado exigiria um parser de assinatura ICP-Brasil completo (ex.:
biblioteca `pyHanko`), fora do escopo desta versão.

## Variante "AEE" (Atendimento Educacional Especializado) — limitação conhecida

Tutores de AEE (identificados no lote de teste pelos relatórios do polo
Geoprocessamento com "_AEE_" no nome do arquivo, ou com o título
"RELATÓRIO MENSAL DE ATIVIDADES DE TUTORIA **AEE** - UAB") usam um modelo
com redação e estrutura diferentes: não há a seção "II - Acompanhamento
discente e gerência da turma" com contagem de estudantes, o texto das
perguntas de sim/não muda ligeiramente ("do/a discente" em vez de "dos
estudantes"), e a identificação do aluno é individual, não por turma.

**Nesta versão, o parser não é calibrado para a variante AEE.** Os campos de
identificação (Nome/CPF/Curso) ainda são extraídos corretamente porque usam
os mesmos rótulos, mas as perguntas de sim/não específicas ficam sem
resposta identificada — o que já reduz o *score de confiança* do relatório e
o sinaliza para revisão manual, em vez de apresentar dados incorretos como
se fossem confiáveis. Extensão futura: detectar a variante pelo marcador de
título e aplicar um segundo conjunto de âncoras de regex específico para
AEE.

## Score de confiança de extração

Cada relatório recebe um score de 0 a 1 (`pdf_validator.validar()`),
combinando:

- 50% — completude da identificação (nome, CPF, curso, mês/ano)
- 20% — presença dos marcadores fixos do modelo oficial (cabeçalho MEC/UAB)
- 30% — % das 8 perguntas de sim/não reconhecidas automaticamente

Relatórios com score abaixo de `LIMIAR_VALIDO` (0.6) são tratados como "não
processados" no relatório de auditoria — recomendação de revisão manual do
PDF original, e não de correção automática do texto.
