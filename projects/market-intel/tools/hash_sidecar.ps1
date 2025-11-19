param([Parameter(Mandatory=$true)][string]$Path)
if (-not (Test-Path $Path)) { Write-Error "not found: $Path"; exit 3 }
$bytes = [System.IO.File]::ReadAllBytes($Path)
$sha = [System.Security.Cryptography.SHA256]::Create()
$hash = ($sha.ComputeHash($bytes) | ForEach-Object ToString x2) -join ""
$meta = @{
  source_url = ""
  collected_at = (Get-Date).ToUniversalTime().ToString("s") + "Z"
  collector = "unknown"
  hash_sha256 = $hash
} | ConvertTo-Json -Compress
$meta | Out-File -FilePath "$Path.meta.json" -Encoding utf8
Write-Output "wrote $Path.meta.json"
