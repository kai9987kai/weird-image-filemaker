param(
  [string]$InputDir = ".\best_20_weird",
  [string]$OutputZip = ".\best_20_weird.zip"
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path -LiteralPath $InputDir -PathType Container)) {
  throw "Input directory not found: $InputDir"
}

$files = Get-ChildItem -LiteralPath $InputDir -File
if ($files.Count -eq 0) {
  throw "Input directory has no files: $InputDir"
}

if (Test-Path -LiteralPath $OutputZip) {
  Remove-Item -LiteralPath $OutputZip -Force
}

Compress-Archive -Path (Join-Path $InputDir '*') -DestinationPath $OutputZip -CompressionLevel Optimal

$zipInfo = Get-Item -LiteralPath $OutputZip
Write-Host ("Wrote {0} ({1} bytes) from {2} files" -f $zipInfo.FullName, $zipInfo.Length, $files.Count)
