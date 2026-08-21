<?php
declare(strict_types=1);
$ano_atual = date("Y");
?>
<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Auditoria de Relatórios de Tutores UAB</title>
<meta name="description" content="Envie o zip mensal dos relatórios de tutoria UAB/UFABC e receba um relatório de auditoria em HTML com pendências, gráficos e detalhamento por tutor.">
<style>
  :root {
    --bg: #f5f6f8; --panel: #ffffff; --text: #14181f; --muted: #5b6472; --muted-2: #838ea1;
    --border: #e1e4e9; --accent: #1d4ed8; --accent-bg: #eef2ff;
    --aviso-bg: #fff6e0; --aviso: #8a5a00;
    --ok-bg: #e8f5e9; --ok: #1e7d32;
  }
  * { box-sizing: border-box; }
  body {
    margin: 0; background: var(--bg); color: var(--text);
    font-family: -apple-system, "Segoe UI", Roboto, Arial, sans-serif;
    line-height: 1.5;
  }
  a { color: var(--accent); }

  .topo-institucional {
    background: var(--text); color: #cfd6e4; font-size: 0.78rem;
    padding: 6px 20px; text-align: center;
  }
  .topo-institucional a { color: #fff; text-decoration: none; }
  .topo-institucional a:hover { text-decoration: underline; }

  header.hero {
    background: linear-gradient(135deg, #1d4ed8 0%, #1e3a8a 100%);
    color: #fff; padding: 48px 20px 40px; text-align: center;
  }
  header.hero h1 { margin: 0 0 10px; font-size: 1.7rem; }
  header.hero p { margin: 0 auto; max-width: 640px; color: #dbe4ff; font-size: 1rem; }

  main { max-width: 880px; margin: -28px auto 0; padding: 0 20px 56px; }

  .grade { display: grid; grid-template-columns: 1fr; gap: 20px; }
  @media (min-width: 800px) { .grade { grid-template-columns: 1.1fr 1fr; align-items: start; } }

  .painel {
    background: var(--panel); border: 1px solid var(--border); border-radius: 14px;
    padding: 28px; box-shadow: 0 10px 30px rgba(20,24,31,0.06);
  }

  h2 { font-size: 1.1rem; margin: 0 0 10px; }
  h3 { font-size: 0.95rem; margin: 22px 0 8px; color: var(--muted); }
  p { color: var(--text); }
  p.sub { color: var(--muted); font-size: 0.92rem; }

  ul.links-relacionados { list-style: none; margin: 0; padding: 0; }
  ul.links-relacionados li { margin-bottom: 6px; font-size: 0.9rem; }
  ul.links-relacionados a { text-decoration: none; }
  ul.links-relacionados a:hover { text-decoration: underline; }

  label { display: block; font-weight: 600; font-size: 0.85rem; margin: 18px 0 6px; }
  label:first-of-type { margin-top: 0; }
  input[type=file], select, input[type=number] {
    width: 100%; padding: 10px; border: 1px solid #c7cbd3; border-radius: 8px;
    font-size: 0.95rem; box-sizing: border-box; background: #fff; color: var(--text);
  }
  .linha { display: flex; gap: 12px; }
  .linha > div { flex: 1; }
  button {
    margin-top: 22px; width: 100%; padding: 12px; border: 0; border-radius: 8px;
    background: var(--accent); color: #fff; font-size: 1rem; font-weight: 600; cursor: pointer;
  }
  button:hover { background: #1e40af; }

  .aviso { background: var(--aviso-bg); color: var(--aviso); border-radius: 8px; padding: 10px 14px; font-size: 0.85rem; margin-top: 16px; }
  .info-caixa {
    background: var(--accent-bg); border-radius: 10px; padding: 14px 16px; font-size: 0.86rem;
    color: #1e3a8a; margin-top: 14px;
  }
  .info-caixa strong { display: block; margin-bottom: 4px; }
  .privacidade {
    background: var(--ok-bg); color: #14532d; border-radius: 10px; padding: 14px 16px;
    font-size: 0.86rem; margin-top: 12px;
  }
  .privacidade strong { display: block; margin-bottom: 4px; color: var(--ok); }

  code {
    background: #eef0f3; border-radius: 4px; padding: 1px 5px; font-size: 0.85em;
  }

  footer {
    border-top: 1px solid var(--border); margin-top: 40px; padding: 28px 20px;
    text-align: center; color: var(--muted-2); font-size: 0.82rem;
  }
  footer p { margin: 4px 0; color: inherit; }
  footer a { color: var(--muted); }

  @media (prefers-color-scheme: dark) {
    :root {
      --bg: #0f1115; --panel: #171a21; --text: #e9ecf2; --muted: #a7afc0; --muted-2: #7a8296;
      --border: #262b35; --accent-bg: #1b2440; --aviso-bg: #332a0c; --ok-bg: #12301f;
    }
    input[type=file], select, input[type=number] { background: #10131a; color: var(--text); border-color: #333a48; }
    code { background: #232833; }
  }

  /* --- overlay de progresso (upload + processamento) --- */
  .overlay-progresso {
    position: fixed; inset: 0; z-index: 100;
    background: rgba(15,17,21,0.55); backdrop-filter: blur(3px);
    display: none; align-items: center; justify-content: center; padding: 20px;
  }
  .overlay-progresso.visivel { display: flex; }
  .cartao-progresso {
    background: var(--panel); border-radius: 18px; padding: 36px 40px;
    max-width: 380px; width: 100%; text-align: center;
    box-shadow: 0 24px 60px rgba(0,0,0,0.3);
    animation: entrada-cartao .25s ease;
  }
  @keyframes entrada-cartao {
    from { opacity: 0; transform: translateY(8px) scale(.98); }
    to { opacity: 1; transform: translateY(0) scale(1); }
  }

  .anel-progresso { position: relative; width: 116px; height: 116px; margin: 0 auto 22px; }
  .anel-progresso svg { width: 100%; height: 100%; transform: rotate(-90deg); }
  .anel-progresso .trilho { fill: none; stroke: var(--accent-bg); stroke-width: 8; }
  .anel-progresso .traco {
    fill: none; stroke: var(--accent); stroke-width: 8; stroke-linecap: round;
    stroke-dasharray: 327; stroke-dashoffset: 327; transition: stroke-dashoffset .25s ease;
  }
  .anel-progresso.indeterminado .traco {
    stroke-dashoffset: 245; animation: girar-anel 1.1s linear infinite;
    transform-origin: 50% 50%;
  }
  .anel-progresso.sucesso .traco { stroke: var(--ok); stroke-dashoffset: 0; }
  .anel-progresso.erro .traco { stroke: #d03b3b; stroke-dashoffset: 0; }
  @keyframes girar-anel { to { transform: rotate(360deg); } }

  .anel-progresso .conteudo {
    position: absolute; inset: 0; display: flex; align-items: center; justify-content: center;
    font-size: 1.15rem; font-weight: 700; color: var(--text);
  }
  .anel-progresso .icone-check, .anel-progresso .icone-erro {
    font-size: 2.1rem; display: none;
  }
  .anel-progresso.sucesso .conteudo .porcentagem { display: none; }
  .anel-progresso.sucesso .conteudo .icone-check { display: block; animation: surgir-icone .3s ease; }
  .anel-progresso.erro .conteudo .porcentagem { display: none; }
  .anel-progresso.erro .conteudo .icone-erro { display: block; animation: surgir-icone .3s ease; }
  @keyframes surgir-icone {
    from { opacity: 0; transform: scale(.5); }
    to { opacity: 1; transform: scale(1); }
  }

  .cartao-progresso h3 { margin: 0 0 6px; font-size: 1.05rem; }
  .cartao-progresso .status-etapa {
    color: var(--muted); font-size: 0.88rem; min-height: 20px;
    transition: opacity .2s ease;
  }
  .cartao-progresso .erro-detalhe {
    color: #d03b3b; font-size: 0.85rem; margin-top: 10px; display: none;
  }
  .cartao-progresso button.cancelar, .cartao-progresso button.fechar {
    margin-top: 20px; width: auto; padding: 8px 18px; font-size: 0.85rem;
    background: transparent; border: 1px solid var(--border); color: var(--muted);
  }
  .cartao-progresso button.cancelar:hover, .cartao-progresso button.fechar:hover { background: var(--bg); }
  .cartao-progresso button.abrir {
    margin-top: 20px; margin-right: 10px; width: auto; padding: 8px 18px; font-size: 0.85rem;
  }
  .cartao-progresso button.fechar { margin-top: 20px; }
</style>
</head>
<body>

<div class="topo-institucional">
  <a href="https://www.ufabc.edu.br/" target="_blank" rel="noopener">UFABC</a> ·
  <a href="https://site.ufabc.edu.br/uab-2/sobre-uab" target="_blank" rel="noopener">Universidade Aberta do Brasil (UAB)</a> ·
  NETEL — Núcleo Educacional de Tecnologias e Línguas
</div>

<header class="hero">
  <h1>Auditoria de Relatórios de Tutores UAB</h1>
  <p>
    Envie o .zip mensal com os relatórios de tutoria e receba, em segundos, um
    relatório de auditoria com gráficos, pendências e detalhamento por tutor —
    sem nada armazenado neste servidor depois do download.
  </p>
</header>

<main>
  <div class="grade">

    <div class="painel">
      <h2>Sobre a UAB na UFABC</h2>
      <p class="sub">
        A Universidade Aberta do Brasil (UAB) é um sistema integrado por
        universidades públicas que amplia e interioriza a formação em nível
        superior, com prioridade para a formação inicial de professores da
        educação básica e a formação continuada de profissionais da educação.
        Na UFABC, o programa oferece cursos a distância desde 2010, com apoio
        de tutores e polos presenciais que dão suporte pedagógico aos
        cursistas.
      </p>

      <h3>Links relacionados</h3>
      <ul class="links-relacionados">
        <li>🔗 <a href="https://site.ufabc.edu.br/uab-2/sobre-uab" target="_blank" rel="noopener">Sobre a UAB — site oficial UFABC</a></li>
        <li>🔗 <a href="https://site.ufabc.edu.br/uab-2/cursos-de-especializacao" target="_blank" rel="noopener">Cursos de especialização UAB/UFABC</a></li>
        <li>🔗 <a href="https://site.ufabc.edu.br/uab-2/equipe-uab-ufabc" target="_blank" rel="noopener">Equipe UAB/UFABC</a></li>
        <li>🔗 <a href="https://www.gov.br/capes/pt-br/acesso-a-informacao/acoes-e-programas/articulacao-e-inovacao-em-educacao-aberta/sistema-universidade-aberta-do-brasil" target="_blank" rel="noopener">Sistema UAB — CAPES (nacional)</a></li>
        <li>🔗 <a href="https://www.ufabc.edu.br/" target="_blank" rel="noopener">Site institucional da UFABC</a></li>
      </ul>

      <h3>Sobre esta ferramenta</h3>
      <p class="sub">
        O sistema valida cada PDF contra o modelo oficial do Relatório Mensal
        de Atividades de Tutoria, identifica pendências (assinatura digital
        ausente, mês divergente, risco de evasão não comunicado, respostas
        sem justificativa, entre outras) e gera um único arquivo HTML com
        gráficos e tabelas para auditoria — pensado para a coordenação
        conferir o mês todo em minutos, não relatório por relatório.
      </p>
    </div>

    <div class="painel">
      <h2>Gerar relatório de auditoria</h2>

      <form id="form-upload" action="upload.php" method="post" enctype="multipart/form-data">
        <label for="zip_relatorios">Arquivo .zip com os relatórios</label>
        <input type="file" id="zip_relatorios" name="zip_relatorios" accept=".zip" required>

        <div class="linha">
          <div>
            <label for="mes_referencia">Mês de referência</label>
            <select id="mes_referencia" name="mes_referencia" required>
              <option value="1">Janeiro</option>
              <option value="2">Fevereiro</option>
              <option value="3">Março</option>
              <option value="4">Abril</option>
              <option value="5">Maio</option>
              <option value="6">Junho</option>
              <option value="7">Julho</option>
              <option value="8">Agosto</option>
              <option value="9">Setembro</option>
              <option value="10">Outubro</option>
              <option value="11">Novembro</option>
              <option value="12">Dezembro</option>
            </select>
          </div>
          <div>
            <label for="ano_referencia">Ano de referência</label>
            <input type="number" id="ano_referencia" name="ano_referencia" min="2020" max="2100" required>
          </div>
        </div>

        <p class="aviso" id="sugestao" hidden></p>

        <button type="submit" id="botao-enviar">Gerar relatório de auditoria</button>
      </form>

      <div class="info-caixa">
        <strong>📦 Formato esperado do .zip</strong>
        Um arquivo como <code>Relatórios de Atividades Tutores - julho-26.zip</code>,
        contendo uma subpasta para cada curso/polo (ex.: <code>C10/</code>,
        <code>EQ/</code>, <code>TSI/</code>) e, dentro de cada uma, os PDFs dos
        relatórios de tutoria no modelo oficial — um por tutor. PDFs fora do
        modelo (foto, digitalização, preenchido à mão) são identificados e
        listados à parte para revisão manual.
        <br><br>
        📄 <a href="modelos/modelo_relatorio_tutoria.pdf" download>Baixar modelo em branco do relatório (PDF)</a>
      </div>

      <div class="privacidade">
        <strong>🔒 Privacidade dos dados enviados</strong>
        O zip enviado é extraído, processado e <strong>apagado do servidor
        imediatamente após a geração do relatório</strong> — sucesso ou erro.
        Nada do conteúdo permanece armazenado aqui depois que o HTML é
        devolvido para download; o único registro que fica é uma linha de log
        por execução (data/hora e contagem de pendências, sem dados pessoais).
      </div>
    </div>

  </div>
</main>

<footer>
  <p>relatorio-tutores-uab · Software livre sob <a href="https://www.gnu.org/licenses/agpl-3.0.html" target="_blank" rel="noopener">licença GNU AGPLv3</a></p>
  <p>© <?= htmlspecialchars($ano_atual) ?> Francisco de Assis Zampirolli — <a href="https://sites.google.com/site/fzampirolli/" target="_blank" rel="noopener">sites.google.com/site/fzampirolli</a></p>
  <p>NETEL/UAB — UFABC · Av. dos Estados, 5001, Bloco L, 3º andar · Santo André - SP</p>
</footer>

<div class="overlay-progresso" id="overlay-progresso">
  <div class="cartao-progresso">
    <div class="anel-progresso" id="anel-progresso">
      <svg viewBox="0 0 120 120">
        <circle class="trilho" cx="60" cy="60" r="52"></circle>
        <circle class="traco" cx="60" cy="60" r="52"></circle>
      </svg>
      <div class="conteudo">
        <span class="porcentagem" id="texto-porcentagem">0%</span>
        <span class="icone-check">✓</span>
        <span class="icone-erro">✕</span>
      </div>
    </div>
    <h3 id="titulo-progresso">Enviando arquivo…</h3>
    <p class="status-etapa" id="status-etapa">Preparando envio…</p>
    <p class="erro-detalhe" id="erro-detalhe"></p>
    <button type="button" class="cancelar" id="botao-cancelar">Cancelar</button>
    <button type="button" class="abrir" id="botao-abrir" style="display:none;">Abrir relatório</button>
    <button type="button" class="fechar" id="botao-fechar" style="display:none;">Fechar</button>
  </div>
</div>

<script>
// Sugere mês/ano a partir do nome do arquivo (ex.: "julho-26", "Julho_2026",
// "07-2026"). O usuário sempre confere/corrige antes de enviar — o campo
// nunca é preenchido de forma oculta.
(function () {
  const MESES = ["janeiro","fevereiro","março","abril","maio","junho",
                 "julho","agosto","setembro","outubro","novembro","dezembro"];

  const fileInput = document.getElementById("zip_relatorios");
  const mesSelect = document.getElementById("mes_referencia");
  const anoInput = document.getElementById("ano_referencia");
  const aviso = document.getElementById("sugestao");

  fileInput.addEventListener("change", function () {
    if (!fileInput.files.length) return;
    const nome = fileInput.files[0].name.toLowerCase();

    let mesEncontrado = null;
    for (let i = 0; i < MESES.length; i++) {
      if (nome.includes(MESES[i]) || nome.includes(MESES[i].slice(0, 3))) {
        mesEncontrado = i + 1;
        break;
      }
    }

    let anoEncontrado = null;
    const m4 = nome.match(/20\d{2}/);
    const m2 = nome.match(/-(\d{2})(?:\.zip)?$/);
    if (m4) {
      anoEncontrado = parseInt(m4[0], 10);
    } else if (m2) {
      anoEncontrado = 2000 + parseInt(m2[1], 10);
    }

    if (mesEncontrado) mesSelect.value = String(mesEncontrado);
    if (anoEncontrado) anoInput.value = String(anoEncontrado);

    if (mesEncontrado || anoEncontrado) {
      aviso.hidden = false;
      aviso.textContent = "Mês/ano sugeridos a partir do nome do arquivo — confira antes de enviar.";
    } else {
      aviso.hidden = false;
      aviso.textContent = "Não foi possível sugerir o mês/ano pelo nome do arquivo — preencha manualmente.";
    }
  });
})();

// Envio via XHR: mostra progresso real do upload, depois uma animação de
// processamento, e dispara o download do HTML resultante — sem precisar
// mudar nada no upload.php (ele continua devolvendo o arquivo pronto).
(function () {
  const MESES_NOME = ["janeiro","fevereiro","março","abril","maio","junho",
                       "julho","agosto","setembro","outubro","novembro","dezembro"];
  const ETAPAS_PROCESSAMENTO = [
    "Extraindo os PDFs do zip…",
    "Validando o modelo oficial…",
    "Aplicando as regras de auditoria…",
    "Montando o relatório…",
  ];

  const form = document.getElementById("form-upload");
  const overlay = document.getElementById("overlay-progresso");
  const anel = document.getElementById("anel-progresso");
  const textoPorcentagem = document.getElementById("texto-porcentagem");
  const titulo = document.getElementById("titulo-progresso");
  const statusEtapa = document.getElementById("status-etapa");
  const erroDetalhe = document.getElementById("erro-detalhe");
  const botaoCancelar = document.getElementById("botao-cancelar");
  const botaoAbrir = document.getElementById("botao-abrir");
  const botaoFechar = document.getElementById("botao-fechar");
  const botaoEnviar = document.getElementById("botao-enviar");

  const CIRCUNFERENCIA = 327;
  let xhrAtual = null;
  let cicloEtapas = null;
  let fase = "enviando"; // "enviando" | "processando"
  let urlRelatorioAtual = null;

  function revogarUrlAtual() {
    if (urlRelatorioAtual) {
      URL.revokeObjectURL(urlRelatorioAtual);
      urlRelatorioAtual = null;
    }
  }

  function circunferenciaPara(percentual) {
    return CIRCUNFERENCIA - (CIRCUNFERENCIA * percentual / 100);
  }

  function resetarOverlay() {
    anel.classList.remove("indeterminado", "sucesso", "erro");
    anel.querySelector(".traco").style.strokeDashoffset = String(CIRCUNFERENCIA);
    textoPorcentagem.textContent = "0%";
    erroDetalhe.style.display = "none";
    erroDetalhe.textContent = "";
    botaoCancelar.style.display = "";
    botaoAbrir.style.display = "none";
    botaoFechar.style.display = "none";
    if (cicloEtapas) { clearInterval(cicloEtapas); cicloEtapas = null; }
    revogarUrlAtual();
  }

  function mostrarOverlay() {
    resetarOverlay();
    fase = "enviando";
    overlay.classList.add("visivel");
    titulo.textContent = "Enviando arquivo…";
    statusEtapa.textContent = "Preparando envio…";
  }

  function esconderOverlay() {
    overlay.classList.remove("visivel");
    revogarUrlAtual();
  }

  function iniciarEtapaProcessamento() {
    if (fase === "processando") return; // evita duplicar o intervalo se o evento de progresso repetir em 100%
    fase = "processando";
    anel.classList.add("indeterminado");
    textoPorcentagem.textContent = "";
    titulo.textContent = "Processando os relatórios…";
    botaoCancelar.style.display = "none";
    let i = 0;
    statusEtapa.textContent = ETAPAS_PROCESSAMENTO[0];
    cicloEtapas = setInterval(function () {
      i = (i + 1) % ETAPAS_PROCESSAMENTO.length;
      statusEtapa.style.opacity = 0;
      setTimeout(function () {
        statusEtapa.textContent = ETAPAS_PROCESSAMENTO[i];
        statusEtapa.style.opacity = 1;
      }, 200);
    }, 1700);
  }

  function nomeArquivoSaida() {
    const mes = parseInt(document.getElementById("mes_referencia").value, 10);
    const ano = document.getElementById("ano_referencia").value;
    const mesStr = String(mes).padStart(2, "0");
    return "auditoria-tutores-" + mesStr + "-" + ano + ".html";
  }

  function mostrarSucesso(url) {
    if (cicloEtapas) { clearInterval(cicloEtapas); cicloEtapas = null; }
    urlRelatorioAtual = url;
    anel.classList.remove("indeterminado");
    anel.classList.add("sucesso");
    titulo.textContent = "Relatório gerado!";
    statusEtapa.textContent = "O download já começou — ou abra direto abaixo.";
    botaoAbrir.style.display = "";
    botaoFechar.style.display = "";
  }

  function extrairMensagemErro(textoResposta) {
    try {
      const doc = new DOMParser().parseFromString(textoResposta, "text/html");
      const p = doc.querySelector("p");
      return p ? p.textContent : "Ocorreu um erro ao processar o relatório.";
    } catch (e) {
      return "Ocorreu um erro ao processar o relatório.";
    }
  }

  function mostrarErro(mensagem) {
    if (cicloEtapas) { clearInterval(cicloEtapas); cicloEtapas = null; }
    anel.classList.remove("indeterminado");
    anel.classList.add("erro");
    titulo.textContent = "Não foi possível gerar o relatório";
    statusEtapa.textContent = "";
    erroDetalhe.textContent = mensagem;
    erroDetalhe.style.display = "block";
    botaoCancelar.style.display = "none";
    botaoFechar.style.display = "";
  }

  form.addEventListener("submit", function (evento) {
    evento.preventDefault();
    if (!form.reportValidity()) return;

    mostrarOverlay();
    botaoEnviar.disabled = true;

    const dados = new FormData(form);
    const xhr = new XMLHttpRequest();
    xhrAtual = xhr;

    xhr.upload.addEventListener("progress", function (e) {
      if (!e.lengthComputable || fase !== "enviando") return;
      const pct = Math.round((e.loaded / e.total) * 100);
      textoPorcentagem.textContent = pct + "%";
      anel.querySelector(".traco").style.strokeDashoffset = String(circunferenciaPara(pct));
      statusEtapa.textContent = "Enviando… " + pct + "%";
      if (pct >= 100) iniciarEtapaProcessamento();
    });

    xhr.responseType = "blob";

    xhr.addEventListener("load", function () {
      botaoEnviar.disabled = false;
      if (xhr.status === 200) {
        const url = URL.createObjectURL(xhr.response);
        mostrarSucesso(url);
        const a = document.createElement("a");
        a.href = url;
        a.download = nomeArquivoSaida();
        document.body.appendChild(a);
        a.click();
        a.remove();
        // a URL fica viva até o usuário clicar "Abrir relatório" ou "Fechar"
        // (revogada em revogarUrlAtual) — não some sozinha.
      } else {
        // resposta de erro vem como HTML; precisa ler o blob como texto.
        const leitor = new FileReader();
        leitor.onload = function () { mostrarErro(extrairMensagemErro(leitor.result)); };
        leitor.onerror = function () { mostrarErro("Ocorreu um erro ao processar o relatório."); };
        leitor.readAsText(xhr.response);
      }
    });

    xhr.addEventListener("error", function () {
      botaoEnviar.disabled = false;
      mostrarErro("Falha de conexão com o servidor. Verifique sua internet e tente novamente.");
    });

    xhr.addEventListener("abort", function () {
      botaoEnviar.disabled = false;
      esconderOverlay();
    });

    xhr.open("POST", form.getAttribute("action"));
    xhr.send(dados);
  });

  botaoCancelar.addEventListener("click", function () {
    if (xhrAtual) xhrAtual.abort();
  });

  botaoAbrir.addEventListener("click", function () {
    if (urlRelatorioAtual) window.open(urlRelatorioAtual, "_blank");
  });

  botaoFechar.addEventListener("click", esconderOverlay);
})();
</script>
</body>
</html>
