$ErrorActionPreference = 'Stop'
$root = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
Push-Location -LiteralPath $root
try {
    & python scripts/verify_all.py --stage bmc-test
    $verificationExit = $LASTEXITCODE
} finally {
    Pop-Location
}
exit $verificationExit
