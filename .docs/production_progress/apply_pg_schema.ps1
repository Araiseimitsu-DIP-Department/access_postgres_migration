#!/usr/bin/env pwsh
# Applies schema_pg_english_v1.sql using PRODUCTION_PROGRESS_DB from project .env
# Usage: pwsh ./.docs/production_progress/apply_pg_schema.ps1

$ErrorActionPreference = "Stop"

$ScriptDir = $PSScriptRoot
$ProjectRoot = (Resolve-Path (Join-Path $ScriptDir "..\..")).Path
$EnvFile = Join-Path $ProjectRoot ".env"

if (-not (Test-Path $EnvFile)) {
    Write-Error ".env が見つかりません: $EnvFile"
    exit 2
}

$dsnLine = Get-Content $EnvFile |
    Where-Object {
        ($_ -match '^\s*PRODUCTION_PROGRESS_DB\s*=' -or $_ -match '^\s*PRODUCTION_PROGRESS_PG_DSN\s*=') `
            -and $_ -notmatch '^\s*#'
    } |
    Select-Object -First 1

if (-not $dsnLine) {
    Write-Error '.env に PRODUCTION_PROGRESS_DB= または PRODUCTION_PROGRESS_PG_DSN= の行がありません。'
    exit 2
}

$dsn = ($dsnLine -split '=', 2)[1].Trim().Trim('"')

if (-not ($dsn -match '^postgresql://')) {
    Write-Error 'PostgreSQL URI は postgresql:// で始まる必要があります。'
    exit 2
}

$SqlPath = Join-Path $ScriptDir "schema_pg_english_v1.sql"
if (-not (Test-Path $SqlPath)) {
    Write-Error "SQL がありません: $SqlPath"
    exit 2
}

Write-Host "Applying schema: $SqlPath"
& psql $dsn -v ON_ERROR_STOP=1 -f $SqlPath
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "Done."
