param(
    [string]$PythonPath = "",
    [string]$LlmModel = "deepseek-r1:1.5b",
    [string]$EmbeddingModel = "qwen3-embedding:0.6b",
    [int]$TopK = 3
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

$topkScriptDir = Join-Path $repoRoot "part2_topk"
$topkScriptPath = Join-Path $topkScriptDir "OllamaTopKRAG.py"
$jsonDir = Join-Path $repoRoot "test_inputs\json_cases"
$outputDir = Join-Path $repoRoot "outputs\part2"

New-Item -ItemType Directory -Force -Path $outputDir | Out-Null

$runs = @(
    @{
        Name = "prompt_1_topk"
        InputFile = Join-Path $jsonDir "prompt_1_population.json"
    },
    @{
        Name = "prompt_2_topk"
        InputFile = Join-Path $jsonDir "prompt_2_gender.json"
    },
    @{
        Name = "prompt_3_topk"
        InputFile = Join-Path $jsonDir "prompt_3_population_gdp.json"
    }
)

foreach ($run in $runs) {
    $logPath = Join-Path $outputDir "$($run.Name).log"

    Write-Host ""
    Write-Host "=== Running $($run.Name) ==="
    Write-Host "Input: $($run.InputFile)"
    Write-Host "Log:   $logPath"
    Write-Host "Top-K: $TopK"

    & $PythonPath $topkScriptPath `
        --input-file $run.InputFile `
        --llm-model $LlmModel `
        --embedding-model $EmbeddingModel `
        --top-k $TopK |
        Tee-Object -FilePath $logPath
}

Write-Host ""
Write-Host "Part 2 runs completed. Logs saved in: $outputDir"
