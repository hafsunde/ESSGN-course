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

$htmlFiles = Get-ChildItem -Path $repoRoot -File -Filter "*.html" |
    Where-Object {
        $_.DirectoryName -eq $repoRoot -and
        $_.BaseName -notlike "*preview"
    }

if (-not $htmlFiles) {
    throw "No top-level HTML files found in $repoRoot to sync."
}

$stalePreviewFiles = Get-ChildItem -Path $docsPath -File -Filter "*preview.html" -ErrorAction SilentlyContinue
foreach ($stalePreviewFile in $stalePreviewFiles) {
    Remove-Item -Path $stalePreviewFile.FullName -Force
}

$stalePreviewDirs = Get-ChildItem -Path $docsPath -Directory -Filter "*preview_files" -ErrorAction SilentlyContinue
foreach ($stalePreviewDir in $stalePreviewDirs) {
    Remove-Item -Path $stalePreviewDir.FullName -Recurse -Force
}

$syncedPaths = @()

foreach ($htmlFile in $htmlFiles) {
    $sourcePath = $htmlFile.FullName
    $destinationPath = Join-Path $docsPath $htmlFile.Name
    Copy-Item -Path $sourcePath -Destination $destinationPath -Force
    $syncedPaths += $htmlFile.Name

    $supportDirName = "{0}_files" -f $htmlFile.BaseName
    $supportDirPath = Join-Path $repoRoot $supportDirName
    if (Test-Path $supportDirPath) {
        $destinationSupportDir = Join-Path $docsPath $supportDirName
        if (Test-Path $destinationSupportDir) {
            Remove-Item -Path $destinationSupportDir -Recurse -Force
        }

        Copy-Item -Path $supportDirPath -Destination $destinationSupportDir -Recurse -Force
        $syncedPaths += $supportDirName
    }
}

$noJekyllPath = Join-Path $docsPath ".nojekyll"
if (-not (Test-Path $noJekyllPath)) {
    Set-Content -Path $noJekyllPath -Value "Disable Jekyll processing for GitHub Pages."
}

Write-Host "GitHub Pages files synced to $docsPath"
Write-Host ("Synced: " + ($syncedPaths -join ", "))
