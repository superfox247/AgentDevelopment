# Universal Test Runner
# Usage: .\scripts\test.ps1 [-Benchmark]
# Runs the full test suite and optional benchmarks.

param (
    [switch]$Benchmark
)

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
Set-Location "$PSScriptRoot/.."

Write-Host "Running Tests..." -ForegroundColor Cyan

# 1. Run Unit/Integration Tests
Write-Host "1. Executing Pytest Suite..." -ForegroundColor Green
uv run pytest
if ($LastExitCode -ne 0) {
    Write-Error "Tests failed!"
    exit $LastExitCode
}

# 2. Run Benchmarks (if requested)
if ($Benchmark) {
    Write-Host "`n2. Running Agent Benchmarks..." -ForegroundColor Green
    uv run scripts/benchmarks/benchmark_models.py
}

Write-Host "`n[SUCCESS] All checks passed!" -ForegroundColor Green
