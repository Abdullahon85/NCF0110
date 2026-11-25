# Build the single NCF image (site + API + SQLite) and push it to a Docker registry.
# Usage (PowerShell, from the repository root, Docker Desktop running):
#   .\deploy\push-images.ps1 -Registry registry.example.uz:5000
# The registry login prompts for user/password; nothing is stored in the repository.
param(
    [Parameter(Mandatory = $true)][string]$Registry,
    [string]$Tag = (git rev-parse --short HEAD)
)
$ErrorActionPreference = "Stop"
Set-Location (Split-Path $PSScriptRoot -Parent)

# docker compose needs an .env file to exist; the build itself uses no secrets.
if (-not (Test-Path .env)) { Copy-Item .env.docker.example .env }

docker login $Registry
if ($LASTEXITCODE -ne 0) { throw "docker login failed" }

$env:REGISTRY = $Registry
$env:TAG = $Tag
docker compose build ncf
if ($LASTEXITCODE -ne 0) { throw "build failed" }

docker tag "${Registry}/ncf:${Tag}" "${Registry}/ncf:latest"
docker push "${Registry}/ncf:${Tag}"
if ($LASTEXITCODE -ne 0) { throw "push ncf:${Tag} failed" }
docker push "${Registry}/ncf:latest"
if ($LASTEXITCODE -ne 0) { throw "push ncf:latest failed" }
Write-Host "Pushed ${Registry}/ncf with tags ${Tag} and latest."
