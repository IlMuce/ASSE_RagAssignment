param(
    [string]$PythonPath = "",
    [string]$LlmModel = "deepseek-r1:1.5b",
    [string]$EmbeddingModel = "qwen3-embedding:0.6b"
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

$baseScriptDir = Join-Path $repoRoot "part1_base"
$baseScriptPath = Join-Path $baseScriptDir "OllamaSimpleRAG.py"
$jsonDir = Join-Path $repoRoot "test_inputs\json_cases"
$outputDir = Join-Path $repoRoot "outputs\part1"

New-Item -ItemType Directory -Force -Path $outputDir | Out-Null

$runs = @(
    @{
        Name = "prompt_1_base"
        InputFile = Join-Path $jsonDir "prompt_1_population.json"
    },
    @{
        Name = "prompt_2_base"
        InputFile = Join-Path $jsonDir "prompt_2_gender.json"
    },
    @{
        Name = "prompt_3_base"
        InputFile = Join-Path $jsonDir "prompt_3_population_gdp.json"
    }
)

foreach ($run in $runs) {
    $logPath = Join-Path $outputDir "$($run.Name).log"

    Write-Host ""
    Write-Host "=== Running $($run.Name) ==="
    Write-Host "Input: $($run.InputFile)"
    Write-Host "Log:   $logPath"

    & $PythonPath $baseScriptPath `
        --input-file $run.InputFile `
        --llm-model $LlmModel `
        --embedding-model $EmbeddingModel |
        Tee-Object -FilePath $logPath
}

Write-Host ""
Write-Host "Part 1 runs completed. Logs saved in: $outputDir"
