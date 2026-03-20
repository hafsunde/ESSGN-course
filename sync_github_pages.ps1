param(
    [string]$DocsDir = "docs"
)

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
if (-not $repoRoot) {
    $repoRoot = (Get-Location).Path
}

$docsPath = Join-Path $repoRoot $DocsDir
New-Item -ItemType Directory -Path $docsPath -Force | Out-Null

$slideFiles = @(
    "session_1.html",
    "session_2.html"
)

foreach ($slideFile in $slideFiles) {
    $sourcePath = Join-Path $repoRoot $slideFile
    if (-not (Test-Path $sourcePath)) {
        throw "Missing $slideFile. Render or create it before syncing GitHub Pages files."
    }

    $destinationPath = Join-Path $docsPath $slideFile
    Copy-Item -Path $sourcePath -Destination $destinationPath -Force
}

$noJekyllPath = Join-Path $docsPath ".nojekyll"
if (-not (Test-Path $noJekyllPath)) {
    Set-Content -Path $noJekyllPath -Value "Disable Jekyll processing for GitHub Pages."
}

Write-Host "GitHub Pages files synced to $docsPath"
