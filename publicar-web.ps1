[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$ApiUrl,
    [Parameter(Mandatory = $true)]
    [ValidatePattern('^[a-z0-9]+(?:-[a-z0-9]+)*$')]
    [string]$Proyecto,
    [switch]$SoloPreparar,
    [switch]$CrearProyecto
)

$ErrorActionPreference = 'Stop'
$direccionApi = $null
if (-not [Uri]::TryCreate($ApiUrl.Trim(), [UriKind]::Absolute, [ref]$direccionApi) -or
    $direccionApi.Scheme -ne 'https' -or $direccionApi.IsLoopback -or
    $direccionApi.UserInfo -or $direccionApi.Query -or $direccionApi.Fragment -or
    $direccionApi.AbsolutePath -ne '/') {
    throw 'ApiUrl debe ser la URL HTTPS pública del backend, sin /api, credenciales ni parámetros.'
}
if ($Proyecto.Length -gt 58) { throw 'El nombre del proyecto debe tener como máximo 58 caracteres.' }
if ($CrearProyecto -and $SoloPreparar) { throw 'SoloPreparar no puede crear un proyecto externo.' }

$origenApi = $direccionApi.GetLeftPart([UriPartial]::Authority)
$origenWeb = "https://$Proyecto.pages.dev"
$carpetaFrontend = Join-Path $PSScriptRoot 'frontend'
if (-not (Get-Command npm.cmd -ErrorAction SilentlyContinue)) { throw 'Falta Node.js con npm en este equipo.' }
if (-not (Test-Path -LiteralPath (Join-Path $carpetaFrontend 'node_modules'))) {
    throw 'Primero instala las dependencias: entra a frontend y ejecuta npm ci.'
}

if (-not $SoloPreparar) {
    Write-Host 'Comprobando el backend público...'
    $salud = Invoke-RestMethod -Uri "$origenApi/health" -TimeoutSec 120
    if ($salud.status -ne 'ok') { throw 'El backend no devolvió el estado esperado.' }
    try {
        $cors = Invoke-WebRequest -Uri "$origenApi/health" -Method Options -UseBasicParsing -TimeoutSec 30 -Headers @{
            Origin = $origenWeb
            'Access-Control-Request-Method' = 'GET'
        }
        if ($cors.Headers['Access-Control-Allow-Origin'] -ne $origenWeb) { throw 'Origen no autorizado.' }
    } catch {
        throw "Configura CORS_ORIGINS=$origenWeb en el backend y vuelve a desplegarlo antes de publicar la interfaz."
    }
}

$apiAnterior = [Environment]::GetEnvironmentVariable('VITE_API_URL', 'Process')
Push-Location -LiteralPath $carpetaFrontend
try {
    $env:VITE_API_URL = $origenApi
    & npm.cmd run build
    if ($LASTEXITCODE -ne 0) { throw 'La compilación falló. No se publicó nada.' }
    $archivosJs = Get-ChildItem -LiteralPath (Join-Path $carpetaFrontend 'dist/assets') -Filter '*.js' -File
    if (-not ($archivosJs | Select-String -SimpleMatch $origenApi -Quiet)) {
        throw 'No se pudo verificar la dirección del backend dentro de la interfaz compilada.'
    }
    if ($SoloPreparar) {
        Write-Host "Interfaz preparada en: $(Join-Path $carpetaFrontend 'dist')"
        Write-Host 'No se publicó nada ni se consultó el backend.'
    } else {
        if ($CrearProyecto) {
            & npx.cmd --yes wrangler@4 pages project create $Proyecto --production-branch main
            if ($LASTEXITCODE -ne 0) { throw 'No se creó el proyecto. Si ya existe, ejecuta sin CrearProyecto.' }
        }
        & npx.cmd --yes wrangler@4 pages deploy dist --project-name $Proyecto --branch main
        if ($LASTEXITCODE -ne 0) { throw 'Cloudflare no confirmó la publicación. Revisa la sesión y la salida de Wrangler.' }
        Write-Host "Cloudflare confirmó la publicación. Abre: $origenWeb"
    }
} finally {
    [Environment]::SetEnvironmentVariable('VITE_API_URL', $apiAnterior, 'Process')
    Pop-Location
}
