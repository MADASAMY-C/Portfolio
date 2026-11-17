param(
    [ValidateSet('start', 'stop', 'status')]
    [string]$Action = 'start'
)

$ErrorActionPreference = 'Stop'
$appDataRoot = Join-Path $env:LOCALAPPDATA 'PortfolioPostgreSQL'
$dataRoot = Join-Path $appDataRoot 'data'
$postgresBin = Join-Path $appDataRoot '18.7\pgsql\bin'
$pgCtl = Join-Path $postgresBin 'pg_ctl.exe'
$logFile = Join-Path $appDataRoot 'postgresql.log'

if (-not (Test-Path -LiteralPath $pgCtl -PathType Leaf)) {
    throw "PostgreSQL is not installed at '$postgresBin'."
}
if (-not (Test-Path -LiteralPath (Join-Path $dataRoot 'PG_VERSION') -PathType Leaf)) {
    throw "PostgreSQL data folder is not initialized at '$dataRoot'."
}

switch ($Action) {
    'start' {
        & $pgCtl -D $dataRoot status *> $null
        if ($LASTEXITCODE -eq 0) {
            Write-Host 'Local PostgreSQL is already running.'
            break
        }

        & $pgCtl -D $dataRoot -l $logFile -o '-h 127.0.0.1 -p 5432' start
        if ($LASTEXITCODE -ne 0) {
            throw "PostgreSQL did not start. See '$logFile' for details."
        }
    }
    'stop' {
        & $pgCtl -D $dataRoot stop -m fast
        if ($LASTEXITCODE -ne 0) {
            throw 'PostgreSQL did not stop cleanly.'
        }
    }
    'status' {
        & $pgCtl -D $dataRoot status
        if ($LASTEXITCODE -ne 0) {
            throw 'Local PostgreSQL is not running.'
        }
    }
}
