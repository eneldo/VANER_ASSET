param(
    [string]$Tag = "v1.0.14",
    [string]$SupportBranch = "support/sgaholding-v1",
    [string]$ClientBranch = "client/nuevo-cliente-v2",
    [string]$Remote = "origin"
)

$ErrorActionPreference = "Stop"
$env:GIT_PAGER = "cat"
$env:PAGER = "cat"

function Invoke-Git {
    param([string[]]$GitArguments)

    & git --no-pager @GitArguments
    if ($LASTEXITCODE -ne 0) {
        throw "Fallo git $($GitArguments -join ' ')"
    }
}

function Assert-ReferenceAbsent {
    param([string]$Reference)

    & git --no-pager show-ref --verify --quiet $Reference
    if ($LASTEXITCODE -eq 0) {
        throw "La referencia $Reference ya existe; no se sobrescribira"
    }
}

$branch = (git branch --show-current).Trim()
if ($branch -ne "main") {
    throw "Ejecute este script desde main; rama actual: $branch"
}

Assert-ReferenceAbsent "refs/tags/$Tag"
Assert-ReferenceAbsent "refs/heads/$SupportBranch"
Assert-ReferenceAbsent "refs/heads/$ClientBranch"

python scripts/verify_repository_security.py
if ($LASTEXITCODE -ne 0) {
    throw "El control de seguridad del repositorio fallo"
}

Invoke-Git @("diff", "--check")
Invoke-Git @("add", "-A")

$forbiddenEnvironmentFiles = @(
    git --no-pager diff --cached --diff-filter=AMCR --name-only |
        Where-Object { $_ -match '(^|/)\.env($|\.)' -and $_ -ne '.env.example' }
)
if ($forbiddenEnvironmentFiles.Count -gt 0) {
    throw "Archivos de entorno no permitidos: $($forbiddenEnvironmentFiles -join ', ')"
}

Invoke-Git @("diff", "--cached", "--check")
Invoke-Git @("commit", "-m", "release: congelar entrega SGAHolding v1.0.14")

$releaseCommit = (git rev-parse HEAD).Trim()
Invoke-Git @("tag", "-a", $Tag, "-m", "SGAHolding $Tag - entrega congelada")
Invoke-Git @("branch", $SupportBranch, $releaseCommit)
Invoke-Git @("branch", $ClientBranch, $releaseCommit)

& scripts/create_release_snapshot.ps1 -Tag $Tag
if ($LASTEXITCODE -ne 0) {
    throw "No se pudo crear el snapshot de la etiqueta"
}

Invoke-Git @("push", $Remote, "main")
Invoke-Git @("push", $Remote, $Tag)
Invoke-Git @("push", "--set-upstream", $Remote, $SupportBranch)
Invoke-Git @("push", "--set-upstream", $Remote, $ClientBranch)
Invoke-Git @("switch", $ClientBranch)

Write-Output "Release publicado: $Tag -> $releaseCommit"
Write-Output "Rama activa: $ClientBranch"
