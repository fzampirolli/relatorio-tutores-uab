<?php
declare(strict_types=1);
?>
<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Auditoria de Relatórios de Tutores UAB</title>
<style>
  body { font-family: -apple-system, "Segoe UI", Roboto, Arial, sans-serif; background: #f5f6f8; color: #1c2331; margin: 0; }
  main { max-width: 560px; margin: 60px auto; background: #fff; border: 1px solid #e1e4e9; border-radius: 12px; padding: 32px; }
  h1 { font-size: 1.3rem; margin-top: 0; }
  p.desc { color: #5b6472; font-size: 0.92rem; }
  label { display: block; font-weight: 600; font-size: 0.85rem; margin: 18px 0 6px; }
  input[type=file], select, input[type=number] {
    width: 100%; padding: 10px; border: 1px solid #c7cbd3; border-radius: 8px; font-size: 0.95rem; box-sizing: border-box;
  }
  .linha { display: flex; gap: 12px; }
  .linha > div { flex: 1; }
  button {
    margin-top: 24px; width: 100%; padding: 12px; border: 0; border-radius: 8px;
    background: #1d4ed8; color: #fff; font-size: 1rem; font-weight: 600; cursor: pointer;
  }
  button:hover { background: #1e40af; }
  .aviso { background: #fff6e0; color: #8a5a00; border-radius: 8px; padding: 10px 14px; font-size: 0.85rem; margin-top: 18px; }
</style>
</head>
<body>
<main>
  <h1>Auditoria de Relatórios de Tutores UAB</h1>
  <p class="desc">
    Envie o .zip com os relatórios mensais dos tutores (o mesmo modelo padrão
    do formulário oficial). O sistema valida cada PDF, identifica pendências
    e gera um relatório de auditoria em HTML para download — nenhum arquivo
    enviado permanece armazenado neste servidor.
  </p>

  <form action="upload.php" method="post" enctype="multipart/form-data">
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

    <button type="submit">Gerar relatório de auditoria</button>
  </form>
</main>

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
</script>
</body>
</html>
