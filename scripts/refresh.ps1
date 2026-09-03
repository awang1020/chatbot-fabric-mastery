#requires -Version 7.0
<#
.SYNOPSIS
    One-command weekly refresh for Ask Fabric Mastery.

.DESCRIPTION
    1. Re-fetches the Substack archive (your latest posts included)
    2. Shows you which markdowns changed
    3. Commits + pushes to main if there's anything new
    The GitHub Actions workflow then rebuilds the Chroma index, the Docker
    image, and rolls a new Container App revision (~7 min total).

.PARAMETER DryRun
    Run the ingestion locally but skip git commit + push. Useful to preview
    what would be added before publishing.

.EXAMPLE
    pwsh ./scripts/refresh.ps1
    # The one-liner you run every Tuesday after publishing on Substack.

.EXAMPLE
    pwsh ./scripts/refresh.ps1 -DryRun
    # Look at the new posts without shipping them yet.
#>
[CmdletBinding()]
param(
    [switch]$DryRun
)

$ErrorActionPreference = 'Stop'

# Locate the repo root (this script lives in <repo>/scripts).
$repo = Split-Path -Parent $PSScriptRoot
Set-Location $repo

Write-Host ''
Write-Host '=== Ask Fabric Mastery - weekly refresh ===' -ForegroundColor Cyan
Write-Host "repo : $repo"
Write-Host ''

# 1. Activate venv -----------------------------------------------------------
$venv = Join-Path $repo '.venv\Scripts\Activate.ps1'
if (-not (Test-Path $venv)) {
    Write-Host "Virtualenv not found at $venv" -ForegroundColor Red
    Write-Host "Run: python -m venv .venv ; .\.venv\Scripts\Activate.ps1 ; pip install -r requirements.txt"
    exit 1
}
. $venv

# 2. Re-ingest the Substack archive -----------------------------------------
Write-Host '--- [1/3] Ingesting Substack archive ---' -ForegroundColor Yellow
python -m scripts.ingest_substack --skip-paywalled --delay 0.4
if ($LASTEXITCODE -ne 0) {
    Write-Host 'Ingestion failed. Aborting.' -ForegroundColor Red
    exit 1
}

# 3. Show diff --------------------------------------------------------------
Write-Host ''
Write-Host '--- [2/3] Local changes ---' -ForegroundColor Yellow
$changed = git status --porcelain data/newsletters
if (-not $changed) {
    Write-Host 'Nothing new since the last run. App is already up to date.' -ForegroundColor Green
    exit 0
}
Write-Host $changed
$newFiles  = ($changed | Where-Object { $_ -match '^\?\?' } | Measure-Object).Count
$modFiles  = ($changed | Where-Object { $_ -match '^\sM' -or $_ -match '^M' } | Measure-Object).Count
Write-Host ("  -> new: {0} / updated: {1}" -f $newFiles, $modFiles)

if ($DryRun) {
    Write-Host ''
    Write-Host 'Dry-run requested. Skipping git commit + push.' -ForegroundColor DarkYellow
    Write-Host 'Re-run without -DryRun to publish.' -ForegroundColor DarkYellow
    exit 0
}

# 4. Commit + push ----------------------------------------------------------
Write-Host ''
Write-Host '--- [3/3] Publishing to GitHub ---' -ForegroundColor Yellow
git add data/newsletters
$stamp = Get-Date -Format 'yyyy-MM-dd'
git commit -m "data: weekly newsletter refresh $stamp" --quiet
git push origin main --quiet
if ($LASTEXITCODE -ne 0) {
    Write-Host 'Push failed. Run `git status` to inspect.' -ForegroundColor Red
    exit 1
}

Write-Host ''
Write-Host 'Done. GitHub Actions is now rebuilding the index + image.' -ForegroundColor Green
Write-Host 'Watch live  : gh run watch --repo awang1020/chatbot-fabric-mastery'
Write-Host 'App URL     : https://chat.antoinewang-tech.com/'
Write-Host 'Landing     : https://awang1020.github.io/chatbot-fabric-mastery/'
Write-Host ''
