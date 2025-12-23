Param(
    [string]$InstallDir = "nomisma"
)

$ErrorActionPreference = "Stop"

$InstallDirInput = Read-Host "Install path [$InstallDir]"
if ($InstallDirInput) {
    $InstallDir = $InstallDirInput
}

$RepoUrl = $env:REPO_URL
if (-not $RepoUrl) {
    $RepoUrl = "https://github.com/nikolareljin/nomisma.git"
}

function Open-Url {
    param([string]$Url)
    try {
        Start-Process $Url
    } catch {
        Write-Host "Open this URL in your browser: $Url"
    }
}

function Require-Command {
    param(
        [string]$CommandName,
        [string]$Url
    )
    if (-not (Get-Command $CommandName -ErrorAction SilentlyContinue)) {
        Write-Host "Missing dependency: $CommandName"
        Open-Url $Url
        exit 1
    }
}

Require-Command -CommandName "git" -Url "https://git-scm.com/downloads"

if (-not (Get-Command "docker" -ErrorAction SilentlyContinue)) {
    Write-Host "Missing dependency: docker"
    Open-Url "https://docs.docker.com/get-docker/"
    exit 1
}

$composeAvailable = $false
try {
    docker compose version | Out-Null
    $composeAvailable = $true
} catch {
    $composeAvailable = $false
}

if (-not $composeAvailable -and (Get-Command "docker-compose" -ErrorAction SilentlyContinue)) {
    $composeAvailable = $true
}

if (-not $composeAvailable) {
    Write-Host "Missing dependency: docker compose"
    Open-Url "https://docs.docker.com/compose/install/"
    exit 1
}

if (Test-Path $InstallDir) {
    Write-Host "Install directory already exists: $InstallDir"
    Write-Host "Remove it or pick a different path."
    exit 1
}

Write-Host "Cloning $RepoUrl into $InstallDir"
git clone $RepoUrl $InstallDir

Set-Location $InstallDir

if (Test-Path ".\update") {
    .\update
} else {
    git submodule update --init --recursive
}

if (-not (Test-Path ".\.env") -and (Test-Path ".\.env.example")) {
    Copy-Item ".\.env.example" ".\.env"
    Write-Host "Created .env from .env.example"
}

Write-Host "Setup complete."
Write-Host "Next steps:"
Write-Host "  cd $InstallDir"
Write-Host "  ./start"
