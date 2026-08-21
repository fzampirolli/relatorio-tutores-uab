#!/usr/bin/env python3
"""Gera modelos/modelo_relatorio_tutoria.pdf — versão em branco do Relatório
Mensal de Atividades de Tutoria UAB, para download na página inicial, como
referência do formato exato que o sistema espera.

Reconstruído a partir da estrutura observada nos PDFs reais do modelo oficial
(ver modelos/mapa_campos.md) — não deriva de nenhum PDF preenchido por um
tutor, para não haver risco de reaproveitar dado real.
"""

import sys
from pathlib import Path

import pymupdf as fitz

BASE_DIR = Path(__file__).resolve().parent.parent
SAIDA = BASE_DIR / "modelos" / "modelo_relatorio_tutoria.pdf"

CSS = """
* { font-family: Arial, sans-serif; }
body { font-size: 10.5px; line-height: 1.35; }
h1 { font-size: 12.5px; text-align: center; margin: 6px 0 2px; }
h2 { font-size: 11px; margin: 10px 0 4px; }
p { margin: 4px 0; }
table { border-collapse: collapse; width: 100%; margin: 6px 0; }
td, th { border: 1px solid #000; padding: 4px 6px; vertical-align: top; }
th { background: #d9d9d9; text-align: left; }
.rotulo { font-weight: bold; width: 90px; }
.linha-branco { border-bottom: 1px solid #000; display: inline-block; min-width: 260px; }
.pequeno { font-size: 9px; color: #333; }
.cabecalho { font-size: 9px; line-height: 1.25; }
.cabecalho b { font-size: 10px; }
"""

CABECALHO = """
<p class="cabecalho">
<b>MINISTÉRIO DA EDUCAÇÃO</b><br>
Fundação Universidade Federal do ABC<br>
Núcleo Educacional de Tecnologias e Línguas – NETEL<br>
Universidade Aberta do Brasil - UAB<br>
Av. dos Estados, 5001 · Bairro Bangú, Santo André - SP · CEP 09210-580<br>
Bloco L · 3º andar · Fone: (11) 3356.7650
</p>
<hr>
"""

PAGINA_1 = CABECALHO + """
<h1>RELATÓRIO MENSAL DE ATIVIDADES DE TUTORIA UAB</h1>
<p style="text-align:right;"><b>MÊS: _______________ ANO: _______</b></p>

<table>
<tr><td class="rotulo">Nome</td><td></td></tr>
<tr><td class="rotulo">CPF</td><td></td></tr>
<tr><td class="rotulo">Curso</td><td></td></tr>
<tr><td class="rotulo">Polo</td><td></td></tr>
</table>

<h2>I - DAS OBRIGAÇÕES ENQUANTO TUTOR (A)</h2>
<p>Conforme o Termo de Compromisso do Bolsista, anexo da Portaria Capes nº 309 de 27 de setembro
de 2024, são obrigações do tutor(a):</p>
<ol>
<li>Mediar a comunicação de conteúdos entre o professor e os cursistas;</li>
<li>Acompanhar as atividades discentes, conforme o cronograma do curso;</li>
<li>Apoiar o professor da disciplina no desenvolvimento das atividades docentes;</li>
<li>Estabelecer contato permanente com os alunos e mediar as atividades discentes;</li>
<li>Colaborar com a coordenação do curso na avaliação dos estudantes;</li>
<li>Participar das atividades de capacitação e atualização promovidas pela Instituição de Ensino;</li>
<li>Elaborar relatórios mensais de acompanhamento dos alunos e encaminhar à coordenadoria de tutoria;</li>
<li>Participar do processo de avaliação do projeto pedagógico sob orientação do Coordenador do Curso e ou Professor Responsável;</li>
<li>Manter regularidade de acesso ao Ambiente Virtual de Aprendizagem (AVA) para acompanhar as atividades discentes, conforme cronograma do curso. Retornar às solicitações dos cursistas no prazo máximo de 24 horas;</li>
<li>Apoiar operacionalmente a coordenação do curso nas atividades presenciais nos polos, em especial na aplicação de avaliações;</li>
<li>Disponibilizar a documentação comprobatória pessoal para o Coordenador de tutoria.</li>
</ol>
"""

PAGINA_2 = CABECALHO + """
<h2>II - ACOMPANHAMENTO DISCENTE E GERÊNCIA DA TURMA</h2>
<p><b>1 - Responda:</b></p>
<table>
<tr><td>Número total de estudantes sob minha tutoria, no período.</td><td style="width:60px;"></td></tr>
<tr><td>Número de estudantes que formalizaram, por e-mail, a desistência no período.</td><td></td></tr>
<tr><td>Número de estudantes inativos por mais de 30 dias no AVA.</td><td></td></tr>
</table>
<p><b>2 -</b> Lista de alunos do curso, sob a sua responsabilidade, inativos por mais de 30 dias no AVA.</p>
<p>______________________________________________________________________</p>
<p>______________________________________________________________________</p>

<h2>III - USO DO AMBIENTE VIRTUAL DE APRENDIZAGEM (MOODLE)</h2>
<p><b>1 -</b> Manteve regularidade de acesso ao Ambiente Virtual de Aprendizagem (AVA) conforme
cronograma da disciplina?<br>( &nbsp; ) Sim &nbsp;&nbsp;&nbsp; ( &nbsp; ) Não, Justifique.</p>
<p>______________________________________________________________________</p>

<p><b>2 -</b> Respondeu às solicitações individuais dos estudantes no prazo máximo de 24 horas
técnicas, em dias úteis?<br>( &nbsp; ) Sim — Descreva como foi realizado.</p>
<p>______________________________________________________________________</p>
<p>( &nbsp; ) Não, Justifique.</p>
<p>______________________________________________________________________</p>

<p><b>3 -</b> Acompanhou as atividades discentes, corrigiu em até 72 horas e enviou feedback no
prazo estipulado?<br>( &nbsp; ) Sim &nbsp;&nbsp;&nbsp; ( &nbsp; ) Não, Justifique.</p>
<p>______________________________________________________________________</p>
"""

PAGINA_3 = CABECALHO + """
<p><b>4 -</b> Elaborou feedback formativo, indicando avanços, pontos de melhoria e orientação
motivadora?<br>( &nbsp; ) Sim &nbsp;&nbsp;&nbsp; ( &nbsp; ) Posso melhorar &nbsp;&nbsp;&nbsp; ( &nbsp; ) Não. Por quê?</p>
<p>______________________________________________________________________</p>

<p><b>5 -</b> Interagiu e respondeu todas as mensagens dos discentes no fórum?<br>
( &nbsp; ) Sim &nbsp;&nbsp;&nbsp; ( &nbsp; ) Não, Justifique.</p>
<p>______________________________________________________________________</p>

<h2>IV - "BUSCA ATIVA" E PREVENÇÃO QUANTO À EVASÃO</h2>
<p><b>1.</b> Foram identificados estudantes em situação de risco de evasão ou desistência no período?<br>
( &nbsp; ) Sim. Se sim, informar o número de estudantes: _____ &nbsp;&nbsp;&nbsp; ( &nbsp; ) Não</p>

<p><b>2.</b> A lista de estudantes em risco foi encaminhada à Coordenação de Tutoria no período?<br>
( &nbsp; ) Sim - Data do encaminhamento: ___/___/_____<br>
( &nbsp; ) Não houve lista<br>
( &nbsp; ) Não foi enviada. Motivo: ___________________________________________</p>

<p><b>3 - Responda:</b></p>
<table>
<tr><td>Frequência da busca ativa (diária, semanal, quinzenal ou mensal)</td><td style="width:120px;"></td></tr>
<tr><td>Número total de ações de busca ativa realizadas no mês</td><td></td></tr>
<tr><td>Número de estudantes contatados</td><td></td></tr>
<tr><td>Número de estudantes que retornaram após contato</td><td></td></tr>
</table>

<h2>V - APOIO AO PROFESSOR(A) E ARTICULAÇÃO INSTITUCIONAL</h2>
<p><b>1 -</b> Realizou alinhamento pedagógico com o(a) professor(a) da disciplina no período?<br>
( &nbsp; ) Sim &nbsp;&nbsp;&nbsp; ( &nbsp; ) Não. Justifique ___________________________________</p>
"""

PAGINA_4 = CABECALHO + """
<p><b>2 -</b> Descreva brevemente as ações de apoio realizadas (ex.: planejamento de mediação,
esclarecimento de critérios avaliativos, organização de fóruns, orientação aos estudantes):</p>
<p>______________________________________________________________________</p>
<p>______________________________________________________________________</p>

<p><b>3 -</b> Durante o mês, participou de todas reuniões com a coordenação do curso ou
coordenação de tutoria?<br>
( &nbsp; ) Sim &nbsp;&nbsp;&nbsp; ( &nbsp; ) Não, justifique sua falta e descreva como compensou essa demanda.</p>
<p>______________________________________________________________________</p>

<p><b>4 -</b> Descreva como você interagiu, durante o período, com:</p>
<p>A. A coordenação do Curso: ____________________________________________</p>
<p>B. Os/as professores/as da disciplina: __________________________________</p>
<p>C. A coordenação de Tutoria: ___________________________________________</p>
<p>D. A coordenação de Polo: ______________________________________________</p>
<p>E. Outros: _________________________________________________________</p>

<p><b>5 -</b> Contribuiu com discussões ou avaliações do Projeto Pedagógico do Curso no período?<br>
( &nbsp; ) Sim &nbsp;&nbsp;&nbsp; ( &nbsp; ) Não &nbsp;&nbsp;&nbsp; ( &nbsp; ) Não se aplica</p>

<h2>VI - FORMAÇÃO CONTINUADA</h2>
<p><b>1 -</b> Houve oferta ou convocação para atividades de formação continuada no período?<br>
( &nbsp; ) Sim &nbsp;&nbsp;&nbsp; ( &nbsp; ) Não</p>

<p><b>2 -</b> Participou das atividades convocadas?<br>
( &nbsp; ) Sim &nbsp;&nbsp;&nbsp; ( &nbsp; ) Não &nbsp;&nbsp;&nbsp; ( &nbsp; ) Não se aplica</p>
"""

PAGINA_5 = CABECALHO + """
<p>Se não participou, justificar:</p>
<p>______________________________________________________________________</p>

<h2>VII – ATIVIDADES PRESENCIAIS</h2>
<p><b>1 -</b> Compareceu aos encontros presencial e/ou aplicação de avaliações e atividades
presenciais quando solicitado?<br>
( &nbsp; ) Sim &nbsp;&nbsp;&nbsp; ( &nbsp; ) Não houve &nbsp;&nbsp;&nbsp; ( &nbsp; ) Houve, mas não participei. Justifique:_______________</p>

<h2>VIII - OBSERVAÇÕES E REGISTROS RELEVANTES</h2>
<p><b>1 -</b> Apresente sugestões, observações, problemas ou algo relevante que ocorreu durante o mês.</p>
<p>______________________________________________________________________</p>
<p>______________________________________________________________________</p>

<h2>IX – DECLARAÇÕES FORMAIS</h2>
<p>Assinale com (X) o que for verdadeiro:</p>
<p>( &nbsp; ) Declaro que as informações apresentadas neste relatório são verdadeiras e refletem
fielmente as atividades realizadas no período indicado.</p>
<p>( &nbsp; ) Declaro estar ciente das atribuições previstas no Termo de Compromisso do Bolsista,
conforme a Portaria CAPES nº 309/2024.</p>
<p>( &nbsp; ) Declaro o cumprimento integral da carga horária semanal de 20 horas, prevista no Edital.</p>
<p>( &nbsp; ) Declaro que mantenho atualizada minha documentação comprobatória junto à
Coordenação de Tutoria.</p>

<p style="margin-top:24px;">Santo André, ____ / ____ / ________</p>

<p style="margin-top:36px;">__________________________________</p>
<p><b>Assinatura digital Tutor(a) Bolsista</b><br>
<span class="pequeno">assinaturas devem ser feitas na plataforma ITI/GOV.BR</span></p>
"""

PAGINAS = [PAGINA_1, PAGINA_2, PAGINA_3, PAGINA_4, PAGINA_5]


def gerar():
    doc = fitz.open()
    margem = 42
    for i, conteudo in enumerate(PAGINAS, start=1):
        page = doc.new_page(width=595, height=842)  # A4
        rect = fitz.Rect(margem, margem, 595 - margem, 842 - margem - 16)
        spare, scale = page.insert_htmlbox(rect, conteudo, css=CSS)
        if spare == -1:
            sys.stderr.write(f"aviso: conteúdo da página {i} não coube integralmente (scale={scale})\n")
        page.insert_text((595 / 2 - 5, 842 - margem + 4), str(i), fontsize=9, color=(0.3, 0.3, 0.3))

    doc.set_metadata({
        "title": "Modelo — Relatório Mensal de Atividades de Tutoria UAB",
        "author": "SITE/UAB - UFABC",
        "subject": "Modelo em branco para preenchimento pelos tutores UAB",
    })
    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(SAIDA))
    doc.close()
    print(f"gerado: {SAIDA} ({SAIDA.stat().st_size} bytes)")


if __name__ == "__main__":
    gerar()
