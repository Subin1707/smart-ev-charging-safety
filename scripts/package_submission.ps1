param(
    [string]$OutputPath = "dist\smart-ev-charging-safety-submission.zip"
)

$ErrorActionPreference = "Stop"

$root = Resolve-Path (Join-Path $PSScriptRoot "..")
$outputFullPath = Join-Path $root $OutputPath
$staging = Join-Path $root "dist\submission_staging"

$topLevelDirs = @(
    "bridge",
    "data",
    "database",
    "docker",
    "docs",
    "evidence",
    "formal",
    "fuzz",
    "generated",
    "generator",
    "reports",
    "scenarios",
    "scripts",
    "spec_generator",
    "specification",
    "src",
    "static_analysis",
    "teacher_specs",
    "tests",
    "verification",
    "web"
)

$topLevelFiles = @(
    ".dockerignore",
    ".env.example",
    ".gitignore",
    "build.bat",
    "docker-compose.yml",
    "Makefile",
    "package-lock.json",
    "README.md",
    "requirements.txt",
    "run_tests.bat",
    "verify-all.bat"
)

$excludedDirNames = @(
    ".git",
    ".pytest-temp",
    ".pytest-tmp",
    ".pytest_cache",
    ".tmp_probe",
    ".tmp_production_full_run",
    ".tmp_production_unit_run",
    ".tmp_production_unit_run2",
    ".tmp_production_unit_run3",
    ".tmp_spec_generator_tests",
    "__pycache__",
    "node_modules",
    "node_modules.locked",
    "dist",
    "build",
    ".runtime"
)

$excludedFileExtensions = @(
    ".exe",
    ".dll",
    ".pdb",
    ".lib",
    ".obj",
    ".o",
    ".pyc",
    ".log",
    ".msi",
    ".node"
)

$excludedFileNames = @(
    ".env",
    "gd96_sanitized",
    "package-lock.tmp"
)

function Get-RelativePathFromRoot {
    param([string]$Path)

    $rootText = $root.ToString().TrimEnd('\', '/')
    if ($Path.StartsWith($rootText, [System.StringComparison]::OrdinalIgnoreCase)) {
        return $Path.Substring($rootText.Length).TrimStart('\', '/')
    }

    return $Path
}

function Test-IncludedFile {
    param([System.IO.FileInfo]$File)

    if ($excludedFileNames -contains $File.Name) {
        return $false
    }

    if ($excludedFileExtensions -contains $File.Extension.ToLowerInvariant()) {
        return $false
    }

    $relative = Get-RelativePathFromRoot $File.FullName
    $parts = $relative -split '[\\/]'
    foreach ($part in $parts) {
        if ($excludedDirNames -contains $part) {
            return $false
        }
    }

    return $true
}

if (Test-Path $staging) {
    Remove-Item -LiteralPath $staging -Recurse -Force
}
New-Item -ItemType Directory -Path $staging | Out-Null

foreach ($file in $topLevelFiles) {
    $source = Join-Path $root $file
    if (Test-Path $source) {
        Copy-Item -LiteralPath $source -Destination (Join-Path $staging $file)
    }
}

foreach ($dir in $topLevelDirs) {
    $sourceDir = Join-Path $root $dir
    if (-not (Test-Path $sourceDir)) {
        continue
    }

    Get-ChildItem -LiteralPath $sourceDir -Recurse -File -Force -ErrorAction SilentlyContinue |
        Where-Object { Test-IncludedFile $_ } |
        ForEach-Object {
            $relative = Get-RelativePathFromRoot $_.FullName
            $destination = Join-Path $staging $relative
            $destinationDir = Split-Path -Parent $destination
            if (-not (Test-Path $destinationDir)) {
                New-Item -ItemType Directory -Path $destinationDir -Force | Out-Null
            }
            Copy-Item -LiteralPath $_.FullName -Destination $destination
        }
}

$outputDir = Split-Path -Parent $outputFullPath
if (-not (Test-Path $outputDir)) {
    New-Item -ItemType Directory -Path $outputDir -Force | Out-Null
}
if (Test-Path $outputFullPath) {
    Remove-Item -LiteralPath $outputFullPath -Force
}

Compress-Archive -Path (Join-Path $staging "*") -DestinationPath $outputFullPath -Force

Add-Type -AssemblyName System.IO.Compression.FileSystem
$zipItem = Get-Item -LiteralPath $outputFullPath
$zip = [System.IO.Compression.ZipFile]::OpenRead($zipItem.FullName)
try {
    $entryCount = $zip.Entries.Count
}
finally {
    $zip.Dispose()
}

Write-Host "Created: $($zipItem.FullName)"
Write-Host "Size MB: $([Math]::Round($zipItem.Length / 1MB, 2))"
Write-Host "Entries: $entryCount"
Write-Host "Excluded: .env, node_modules, pytest caches, __pycache__, binaries, logs, temporary runtime artifacts"
