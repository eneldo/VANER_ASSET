param(
    [Parameter(Mandatory = $true)]
    [string]$Tag,

    [string]$OutputDirectory = "backups/releases"
)

$ErrorActionPreference = "Stop"

git rev-parse --verify "refs/tags/$Tag" | Out-Null
if ($LASTEXITCODE -ne 0) {
    throw "No existe la etiqueta $Tag"
}

$repositoryRoot = (git rev-parse --show-toplevel).Trim()
$absoluteOutput = Join-Path $repositoryRoot $OutputDirectory
New-Item -ItemType Directory -Force -Path $absoluteOutput | Out-Null

$safeTag = $Tag -replace '[^A-Za-z0-9._-]', '-'
$bundlePath = Join-Path $absoluteOutput "$safeTag.bundle"
$archivePath = Join-Path $absoluteOutput "$safeTag-source.zip"
$manifestPath = Join-Path $absoluteOutput "$safeTag-manifest.txt"

git bundle create $bundlePath --all
if ($LASTEXITCODE -ne 0) {
    throw "No se pudo crear el bundle Git"
}

git archive --format=zip --output=$archivePath $Tag
if ($LASTEXITCODE -ne 0) {
    throw "No se pudo crear el archivo fuente"
}

$commit = (git rev-list -n 1 $Tag).Trim()
$createdAt = Get-Date -Format "yyyy-MM-ddTHH:mm:ssK"
$bundleHash = (Get-FileHash -Algorithm SHA256 $bundlePath).Hash
$archiveHash = (Get-FileHash -Algorithm SHA256 $archivePath).Hash

@(
    "tag=$Tag"
    "commit=$commit"
    "created_at=$createdAt"
    "bundle_sha256=$bundleHash"
    "source_zip_sha256=$archiveHash"
) | Set-Content -LiteralPath $manifestPath -Encoding utf8

Write-Output "Snapshot creado en $absoluteOutput"
Write-Output "Bundle: $bundlePath"
Write-Output "Codigo: $archivePath"
Write-Output "Manifiesto: $manifestPath"
