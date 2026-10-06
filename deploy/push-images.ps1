# Build the backend and frontend images and push them to a Docker registry.
# Usage (PowerShell, from the repository root, Docker Desktop running):
#   .\deploy\push-images.ps1 -Registry registry.example.uz:5000
# The registry login prompts for user/password; nothing is stored in the repository.
param(
    [Parameter(Mandatory = $true)][string]$Registry,
    [string]$Tag = (git rev-parse --short HEAD)
)
$ErrorActionPreference = "Stop"
Set-Location (Split-Path $PSScriptRoot -Parent)

# docker compose needs an .env file to exist; build itself uses no secrets.
if (-not (Test-Path .env)) { Copy-Item .env.docker.example .env }

docker login $Registry
if ($LASTEXITCODE -ne 0) { throw "docker login failed" }

$env:REGISTRY = $Registry
$env:TAG = $Tag
docker compose build backend frontend
if ($LASTEXITCODE -ne 0) { throw "build failed" }

foreach ($name in "ncf-backend", "ncf-frontend") {
    docker tag "${Registry}/${name}:${Tag}" "${Registry}/${name}:latest"
    docker push "${Registry}/${name}:${Tag}"
    if ($LASTEXITCODE -ne 0) { throw "push ${name}:${Tag} failed" }
    docker push "${Registry}/${name}:latest"
    if ($LASTEXITCODE -ne 0) { throw "push ${name}:latest failed" }
}
Write-Host "Pushed ${Registry}/ncf-backend and ncf-frontend with tags ${Tag} and latest."
