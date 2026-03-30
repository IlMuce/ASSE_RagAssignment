param(
    [string]$PythonPath = "",
    [string]$LlmModel = "deepseek-r1:1.5b",
    [string]$EmbeddingModel = "qwen3-embedding:0.6b",
    [ValidateSet("ollama", "gemini")]
    [string]$Provider = "ollama",
    [string]$ApiEnvFile = "",
    [double]$Temperature = 0.2,
    [string]$OutputSubdir = "",
    [int]$ChunkSize = 0,
    [int]$ChunkOverlap = 0
)

$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Split-Path -Parent $scriptDir

if (-not $PythonPath) {
    $PythonPath = Join-Path $repoRoot ".venv\Scripts\python.exe"
}

if (-not (Test-Path $PythonPath)) {
    throw "Python executable not found at: $PythonPath"
}

$pdfScriptDir = Join-Path $repoRoot "part3_pdf"
$pdfScriptPath = Join-Path $pdfScriptDir "OllamaPDFRAG.py"
$jsonDir = Join-Path $repoRoot "test_inputs\pdf"

if (-not $OutputSubdir) {
    $safeLlm = ($LlmModel -replace '[:/\\ ]', '_')
    $safeEmbedding = ($EmbeddingModel -replace '[:/\\ ]', '_')
    $OutputSubdir = "${safeEmbedding}__${safeLlm}"
}

$outputDir = Join-Path $repoRoot "outputs\part3\$OutputSubdir"

New-Item -ItemType Directory -Force -Path $outputDir | Out-Null

$runs = @(
    @{
        Name = "prompt_1_architecture"
        InputFile = Join-Path $jsonDir "prompt_1_architecture.json"
    },
    @{
        Name = "prompt_2_manual_work"
        InputFile = Join-Path $jsonDir "prompt_2_manual_work.json"
    },
    @{
        Name = "prompt_3_limitations"
        InputFile = Join-Path $jsonDir "prompt_3_limitations.json"
    }
)

foreach ($run in $runs) {
    $logPath = Join-Path $outputDir "$($run.Name).log"

    Write-Host ""
    Write-Host "=== Running $($run.Name) ==="
    Write-Host "Input: $($run.InputFile)"
    Write-Host "Log:   $logPath"
    Write-Host "Provider: $Provider"
    Write-Host "LLM:   $LlmModel"
    Write-Host "Embed: $EmbeddingModel"
    Write-Host "Temp:  $Temperature"
    if ($ChunkSize -gt 0) { Write-Host "Chunk: $ChunkSize" }
    if ($ChunkOverlap -gt 0) { Write-Host "Overlap: $ChunkOverlap" }

    $cmd = @(
        $pdfScriptPath,
        "--input-file", $run.InputFile,
        "--provider", $Provider,
        "--llm-model", $LlmModel,
        "--embedding-model", $EmbeddingModel,
        "--temperature", $Temperature
    )

    if ($ApiEnvFile) {
        $cmd += @("--api-env-file", $ApiEnvFile)
    }

    if ($ChunkSize -gt 0) {
        $cmd += @("--chunk-size", $ChunkSize)
    }
    if ($ChunkOverlap -gt 0) {
        $cmd += @("--chunk-overlap", $ChunkOverlap)
    }

    & $PythonPath @cmd | Tee-Object -FilePath $logPath
}

Write-Host ""
Write-Host "Part 3 runs completed. Logs saved in: $outputDir"
