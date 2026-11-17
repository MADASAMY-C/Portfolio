$ErrorActionPreference = 'Stop'

$projectRoot = Split-Path -Parent $PSScriptRoot
$archivePath = Join-Path $env:TEMP 'postgresql-18.7-1-windows-x64-binaries.zip'
$installRoot = Join-Path $env:LOCALAPPDATA 'PortfolioPostgreSQL\18.7'
$appDataRoot = Join-Path $env:LOCALAPPDATA 'PortfolioPostgreSQL'
$dataRoot = Join-Path $appDataRoot 'data'
$envFile = Join-Path $projectRoot '.env'
$schemaFile = Join-Path $projectRoot 'schema.sql'

if (Test-Path -LiteralPath $dataRoot) {
    throw "Database data folder already exists at '$dataRoot'; refusing to overwrite it."
}
if (Test-Path -LiteralPath $envFile) {
    throw "Project .env already exists; refusing to overwrite credentials."
}
if (-not (Test-Path -LiteralPath $schemaFile -PathType Leaf)) {
    throw "Schema file not found at '$schemaFile'."
}

New-Item -ItemType Directory -Path $appDataRoot -Force | Out-Null
if (-not (Test-Path -LiteralPath $installRoot)) {
    if (-not (Test-Path -LiteralPath $archivePath -PathType Leaf)) {
        throw "PostgreSQL archive not found at '$archivePath'."
    }

    Add-Type -AssemblyName System.IO.Compression.FileSystem
    $archive = [IO.Compression.ZipFile]::OpenRead($archivePath)
    try {
        $runtimePrefixes = @('pgsql/bin/', 'pgsql/lib/', 'pgsql/share/')
        $runtimeEntries = @($archive.Entries | Where-Object {
            $entryName = $_.FullName
            -not $entryName.EndsWith('/') -and
            ($runtimePrefixes | Where-Object { $entryName.StartsWith($_, [StringComparison]::OrdinalIgnoreCase) })
        })
        Write-Host "Extracting $($runtimeEntries.Count) PostgreSQL server runtime files..."

        foreach ($entry in $runtimeEntries) {
            $relativePath = $entry.FullName.Replace('/', [IO.Path]::DirectorySeparatorChar)
            $destination = [IO.Path]::GetFullPath((Join-Path $installRoot $relativePath))
            if (-not $destination.StartsWith($installRoot + [IO.Path]::DirectorySeparatorChar, [StringComparison]::OrdinalIgnoreCase)) {
                throw "Archive entry escapes the PostgreSQL install folder: '$($entry.FullName)'."
            }

            $destinationDirectory = Split-Path -Parent $destination
            [IO.Directory]::CreateDirectory($destinationDirectory) | Out-Null
            [IO.Compression.ZipFileExtensions]::ExtractToFile($entry, $destination, $false)
        }
    }
    finally {
        $archive.Dispose()
    }
}

$postgresBin = Join-Path $installRoot 'pgsql\bin'
$initDb = Join-Path $postgresBin 'initdb.exe'
$pgCtl = Join-Path $postgresBin 'pg_ctl.exe'
$psql = Join-Path $postgresBin 'psql.exe'
$createDb = Join-Path $postgresBin 'createdb.exe'
$logFile = Join-Path $appDataRoot 'postgresql.log'

foreach ($requiredFile in @($initDb, $pgCtl, $psql, $createDb)) {
    if (-not (Test-Path -LiteralPath $requiredFile -PathType Leaf)) {
        throw "Required PostgreSQL executable is missing: '$requiredFile'."
    }
}
$signature = Get-AuthenticodeSignature -FilePath (Join-Path $postgresBin 'postgres.exe')
if ($signature.Status -ne 'Valid') {
    throw "The PostgreSQL server binary signature is not valid ($($signature.Status)); refusing to initialize the database."
}

function New-RandomHexPassword {
    $randomGenerator = [Security.Cryptography.RandomNumberGenerator]::Create()
    try {
        $randomBytes = New-Object byte[] 32
        $randomGenerator.GetBytes($randomBytes)
        return ([BitConverter]::ToString($randomBytes)).Replace('-', '').ToLowerInvariant()
    }
    finally {
        $randomGenerator.Dispose()
    }
}

$postgresPassword = New-RandomHexPassword
$appPassword = New-RandomHexPassword
$passwordFile = Join-Path $env:TEMP ("portfolio-postgres-" + [guid]::NewGuid().ToString('N') + '.txt')
$tempSchemaFile = Join-Path $env:TEMP ("portfolio-schema-" + [guid]::NewGuid().ToString('N') + '.sql')
$previousPgPassword = $env:PGPASSWORD

try {
    [IO.File]::WriteAllText($passwordFile, $postgresPassword, [Text.Encoding]::ASCII)
    $schemaContent = [IO.File]::ReadAllText($schemaFile, [Text.Encoding]::UTF8)
    [IO.File]::WriteAllText($tempSchemaFile, $schemaContent, [Text.UTF8Encoding]::new($false))

    & $initDb -D $dataRoot -U postgres "--pwfile=$passwordFile" --auth-local=scram-sha-256 --auth-host=scram-sha-256 -E UTF8
    if ($LASTEXITCODE -ne 0) {
        throw "PostgreSQL initialization failed with exit code $LASTEXITCODE."
    }

    & $pgCtl -D $dataRoot -l $logFile -o '-h 127.0.0.1 -p 5432' start
    if ($LASTEXITCODE -ne 0) {
        throw "PostgreSQL did not start; see '$logFile' for details."
    }

    $env:PGPASSWORD = $postgresPassword
    $createRoleSql = "CREATE ROLE portfolio_app LOGIN PASSWORD '$appPassword';"
    & $psql -h 127.0.0.1 -p 5432 -U postgres -d postgres -v ON_ERROR_STOP=1 -c $createRoleSql
    if ($LASTEXITCODE -ne 0) {
        throw 'Could not create the application database role.'
    }

    & $createDb -h 127.0.0.1 -p 5432 -U postgres -O portfolio_app portfolio_db
    if ($LASTEXITCODE -ne 0) {
        throw 'Could not create the portfolio_db database.'
    }

    $env:PGPASSWORD = $appPassword
    & $psql -h 127.0.0.1 -p 5432 -U portfolio_app -d portfolio_db -v ON_ERROR_STOP=1 -f $tempSchemaFile
    if ($LASTEXITCODE -ne 0) {
        throw 'Applying schema.sql failed.'
    }

    $databaseUrl = "DATABASE_URL=postgresql://portfolio_app:$appPassword@127.0.0.1:5432/portfolio_db`n"
    [IO.File]::WriteAllText($envFile, $databaseUrl, [Text.UTF8Encoding]::new($false))

    Remove-Item -LiteralPath $archivePath -Force
    Write-Host 'Local PostgreSQL is ready. The portfolio database was initialized and .env was created.'
    Write-Host 'The server listens only on 127.0.0.1:5432.'
    Write-Host 'Use scripts/local_postgres.ps1 -Action start after Windows restarts.'
}
finally {
    if (Test-Path -LiteralPath $passwordFile) {
        Remove-Item -LiteralPath $passwordFile -Force
    }
    if (Test-Path -LiteralPath $tempSchemaFile) {
        Remove-Item -LiteralPath $tempSchemaFile -Force
    }

    if ($null -eq $previousPgPassword) {
        Remove-Item Env:PGPASSWORD -ErrorAction SilentlyContinue
    }
    else {
        $env:PGPASSWORD = $previousPgPassword
    }
}
