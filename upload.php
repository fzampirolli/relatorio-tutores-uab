<?php
declare(strict_types=1);

set_time_limit(300); // lotes grandes (até 500 pdfs) podem levar mais que o default de 30s

function paginaErro(string $mensagem): void
{
    http_response_code(400);
    header("Content-Type: text/html; charset=utf-8");
    echo "<!DOCTYPE html><html lang='pt-BR'><head><meta charset='utf-8'>"
        . "<title>Erro — Auditoria de Relatórios de Tutores UAB</title></head><body>"
        . "<div style='max-width:560px;margin:60px auto;font-family:sans-serif'>"
        . "<h1>Não foi possível gerar o relatório</h1><p>" . htmlspecialchars($mensagem) . "</p>"
        . "<p><a href='index.php'>Voltar</a></p></div></body></html>";
}

function removerDiretorio(string $dir): void
{
    if (!is_dir($dir)) {
        return;
    }
    $itens = scandir($dir);
    foreach ($itens as $item) {
        if ($item === "." || $item === "..") {
            continue;
        }
        $caminho = $dir . DIRECTORY_SEPARATOR . $item;
        is_dir($caminho) ? removerDiretorio($caminho) : unlink($caminho);
    }
    rmdir($dir);
}

if ($_SERVER["REQUEST_METHOD"] !== "POST") {
    paginaErro("Método não permitido.");
    exit;
}

if (!isset($_FILES["zip_relatorios"]) || $_FILES["zip_relatorios"]["error"] !== UPLOAD_ERR_OK) {
    paginaErro("Nenhum arquivo válido foi enviado. Verifique o tamanho do zip e tente novamente.");
    exit;
}

$nomeOriginal = $_FILES["zip_relatorios"]["name"];
if (strtolower(pathinfo($nomeOriginal, PATHINFO_EXTENSION)) !== "zip") {
    paginaErro("O arquivo enviado precisa ser um .zip.");
    exit;
}

$mesReferencia = filter_input(INPUT_POST, "mes_referencia", FILTER_VALIDATE_INT, [
    "options" => ["min_range" => 1, "max_range" => 12],
]);
$anoReferencia = filter_input(INPUT_POST, "ano_referencia", FILTER_VALIDATE_INT, [
    "options" => ["min_range" => 2020, "max_range" => 2100],
]);
if ($mesReferencia === null || $mesReferencia === false || $anoReferencia === null || $anoReferencia === false) {
    paginaErro("Mês/ano de referência inválidos.");
    exit;
}

$baseDir = __DIR__;
$idExecucao = date("Y-m-d_His") . "_" . bin2hex(random_bytes(4));
$dirTrabalho = $baseDir . "/tmp/" . $idExecucao;
$dirUploads = $dirTrabalho . "/uploads";

if (!mkdir($dirUploads, 0770, true)) {
    paginaErro("Falha ao preparar diretório temporário no servidor.");
    exit;
}

$nomeSanitizado = preg_replace('/[^A-Za-z0-9._-]/', "_", basename($nomeOriginal));
$caminhoZip = $dirUploads . "/" . $nomeSanitizado;

if (!move_uploaded_file($_FILES["zip_relatorios"]["tmp_name"], $caminhoZip)) {
    removerDiretorio($dirTrabalho);
    paginaErro("Falha ao salvar o arquivo enviado.");
    exit;
}

$caminhoSaida = $dirTrabalho . "/auditoria.html";

$comando = sprintf(
    "bash %s %s %d %d %s %s 2>&1",
    escapeshellarg($baseDir . "/run_script.sh"),
    escapeshellarg($caminhoZip),
    $mesReferencia,
    $anoReferencia,
    escapeshellarg($dirTrabalho),
    escapeshellarg($caminhoSaida)
);

$saidaComando = [];
$codigoSaida = 0;
exec($comando, $saidaComando, $codigoSaida);

if ($codigoSaida !== 0 || !is_file($caminhoSaida)) {
    $mensagem = $codigoSaida === 1
        ? "O zip enviado não pôde ser processado (verifique se contém PDFs válidos no modelo oficial)."
        : "Ocorreu um erro interno ao processar os relatórios. Tente novamente ou contate o suporte.";
    removerDiretorio($dirTrabalho);
    paginaErro($mensagem);
    exit;
}

$html = file_get_contents($caminhoSaida);
removerDiretorio($dirTrabalho);

$nomeDownload = sprintf("auditoria-tutores-%02d-%d.html", $mesReferencia, $anoReferencia);
header("Content-Type: text/html; charset=utf-8");
header("Content-Disposition: attachment; filename=\"" . $nomeDownload . "\"");
header("Content-Length: " . strlen($html));
echo $html;
