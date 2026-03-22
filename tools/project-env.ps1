[CmdletBinding()]
param(
    [switch]$Apply,
    [switch]$Check,
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$Exec
)

$ErrorActionPreference = "Stop"

function Test-PathSafe {
    param(
        [string]$LiteralPath,
        [ValidateSet("Any", "Leaf", "Container")]
        [string]$Kind = "Any"
    )

    try {
        if ($Kind -eq "Leaf") {
            return Test-Path -LiteralPath $LiteralPath -PathType Leaf
        }
        if ($Kind -eq "Container") {
            return Test-Path -LiteralPath $LiteralPath -PathType Container
        }
        return Test-Path -LiteralPath $LiteralPath
    }
    catch {
        return $false
    }
}

function Resolve-Executable {
    param(
        [string]$Name,
        [string[]]$Candidates
    )

    foreach ($candidate in $Candidates) {
        if ([string]::IsNullOrWhiteSpace($candidate)) {
            continue
        }
        if (Test-PathSafe -LiteralPath $candidate -Kind Leaf) {
            return $candidate
        }
    }

    $command = Get-Command -Name $Name -ErrorAction SilentlyContinue
    if ($command -and $command.Path) {
        return $command.Path
    }
    return $null
}

function Add-PathIfPresent {
    param(
        [System.Collections.Generic.List[string]]$Accumulator,
        [string]$PathValue
    )

    if ([string]::IsNullOrWhiteSpace($PathValue)) {
        return
    }
    if (-not (Test-PathSafe -LiteralPath $PathValue -Kind Container)) {
        return
    }

    $already = $false
    foreach ($existing in $Accumulator) {
        if ($existing -ieq $PathValue) {
            $already = $true
            break
        }
    }
    if (-not $already) {
        $Accumulator.Add($PathValue)
    }
}

$toolCandidates = [ordered]@{
    python   = @(
        "C:\Program Files\Python312\python.exe",
        "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe"
    )
    py       = @(
        "C:\Windows\py.exe",
        "$env:LOCALAPPDATA\Programs\Python\Launcher\py.exe"
    )
    pdflatex = @(
        "C:\Program Files\MiKTeX\miktex\bin\x64\pdflatex.exe",
        "$env:LOCALAPPDATA\Programs\MiKTeX\miktex\bin\x64\pdflatex.exe",
        "$env:APPDATA\TinyTeX\bin\win32\pdflatex.exe"
    )
    xelatex  = @(
        "C:\Program Files\MiKTeX\miktex\bin\x64\xelatex.exe",
        "$env:LOCALAPPDATA\Programs\MiKTeX\miktex\bin\x64\xelatex.exe",
        "$env:APPDATA\TinyTeX\bin\win32\xelatex.exe"
    )
    lualatex = @(
        "C:\Program Files\MiKTeX\miktex\bin\x64\lualatex.exe",
        "$env:LOCALAPPDATA\Programs\MiKTeX\miktex\bin\x64\lualatex.exe",
        "$env:APPDATA\TinyTeX\bin\win32\lualatex.exe"
    )
    initexmf = @(
        "C:\Program Files\MiKTeX\miktex\bin\x64\initexmf.exe",
        "$env:LOCALAPPDATA\Programs\MiKTeX\miktex\bin\x64\initexmf.exe"
    )
    mpm      = @(
        "C:\Program Files\MiKTeX\miktex\bin\x64\mpm.exe",
        "$env:LOCALAPPDATA\Programs\MiKTeX\miktex\bin\x64\mpm.exe"
    )
    quarto   = @(
        "C:\Program Files\Quarto\bin\quarto.exe",
        "$env:LOCALAPPDATA\Programs\Quarto\bin\quarto.exe"
    )
    R        = @(
        "C:\Program Files\R\R-4.5.2\bin\R.exe"
    )
    Rscript  = @(
        "C:\Program Files\R\R-4.5.2\bin\Rscript.exe"
    )
}

$binDirectoryCandidates = @(
    "C:\Program Files\Quarto\bin",
    "C:\Program Files\R\R-4.5.2\bin",
    "C:\Program Files\Python312",
    "C:\Program Files\Python312\Scripts",
    "$env:LOCALAPPDATA\Programs\Python\Python312",
    "$env:LOCALAPPDATA\Programs\Python\Python312\Scripts",
    "$env:LOCALAPPDATA\Programs\Python\Launcher",
    "$env:LOCALAPPDATA\Programs\MiKTeX\miktex\bin\x64",
    "$env:APPDATA\TinyTeX\bin\win32"
)

$resolved = [ordered]@{}
foreach ($name in $toolCandidates.Keys) {
    $resolved[$name] = Resolve-Executable -Name $name -Candidates $toolCandidates[$name]
}

$pathParts = New-Object System.Collections.Generic.List[string]
foreach ($candidateDir in $binDirectoryCandidates) {
    Add-PathIfPresent -Accumulator $pathParts -PathValue $candidateDir
}
foreach ($toolPath in $resolved.Values) {
    if (-not [string]::IsNullOrWhiteSpace($toolPath)) {
        Add-PathIfPresent -Accumulator $pathParts -PathValue (Split-Path -Parent $toolPath)
    }
}
foreach ($existingPart in ($env:Path -split ";")) {
    if (-not [string]::IsNullOrWhiteSpace($existingPart)) {
        Add-PathIfPresent -Accumulator $pathParts -PathValue $existingPart
    }
}

$projectPath = $pathParts -join ";"

$env:PROJECT_PYTHON = $resolved["python"]
$env:PROJECT_PY = $resolved["py"]
$env:PROJECT_PDFLATEX = $resolved["pdflatex"]
$env:PROJECT_XELATEX = $resolved["xelatex"]
$env:PROJECT_LUALATEX = $resolved["lualatex"]
$env:PROJECT_INITEXMF = $resolved["initexmf"]
$env:PROJECT_MPM = $resolved["mpm"]
$env:PROJECT_QUARTO = $resolved["quarto"]
$env:PROJECT_R = $resolved["R"]
$env:PROJECT_RSCRIPT = $resolved["Rscript"]
$env:PROJECT_PATH = $projectPath

if ($Apply -or $Exec.Count -gt 0) {
    $env:Path = $projectPath
}

if ($Check -or (-not $Apply -and $Exec.Count -eq 0)) {
    Write-Host "Project environment summary:"
    foreach ($name in $resolved.Keys) {
        if ($resolved[$name]) {
            Write-Host ("  [ok]   {0,-8} {1}" -f $name, $resolved[$name])
        }
        else {
            Write-Host ("  [miss] {0,-8} not resolved" -f $name)
        }
    }
    Write-Host ""
    Write-Host "Usage examples:"
    Write-Host "  .\tools\project-env.ps1 -Check"
    Write-Host "  .\tools\project-env.ps1 -Apply"
    Write-Host "  .\tools\project-env.ps1 quarto render session_2.qmd"
    Write-Host "  .\tools\project-env.ps1 python --version"
}

if ($Exec.Count -eq 0) {
    return
}

$commandName = $Exec[0]
$commandArgs = @()
if ($Exec.Count -gt 1) {
    $commandArgs = $Exec[1..($Exec.Count - 1)]
}

$useResolvedTool = $false
$commandPath = $commandName
if ($resolved.Contains($commandName) -and $resolved[$commandName]) {
    $useResolvedTool = $true
    $commandPath = $resolved[$commandName]
}

if ($useResolvedTool) {
    & $commandPath @commandArgs
}
else {
    & $commandName @commandArgs
}

if ($MyInvocation.InvocationName -ne ".") {
    exit $LASTEXITCODE
}

