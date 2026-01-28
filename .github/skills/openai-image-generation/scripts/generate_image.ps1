#!/usr/bin/env pwsh
<#
generate_image.ps1 - OpenAI Images API helper

- Reads OPENAI_API_KEY from environment
- Saves generated PNG files to the current working directory (or -OutDir)
- Supports gpt-image-1 (base64 output) and dall-e-3 (url or base64_json)

Docs:
- https://platform.openai.com/docs/api-reference/images
#>

param(
  [Parameter(Mandatory=$true)][string]$Prompt,
  [string]$Model = $(if ($env:OPENAI_IMAGE_MODEL) { $env:OPENAI_IMAGE_MODEL } else { "gpt-image-1" }),
  [string]$Size  = $(if ($env:OPENAI_IMAGE_SIZE) { $env:OPENAI_IMAGE_SIZE } else { "auto" }),
  [int]$N        = $(if ($env:OPENAI_IMAGE_N) { [int]$env:OPENAI_IMAGE_N } else { 1 }),
  [string]$Quality = $env:OPENAI_IMAGE_QUALITY,
  [string]$Style   = $env:OPENAI_IMAGE_STYLE,
  [string]$OutDir = ".",
  [string]$OutPrefix = "generated",
  [switch]$VerboseOutput
)

function Get-UtcStamp {
  return (Get-Date).ToUniversalTime().ToString("yyyyMMdd-HHmmss")
}

$ApiKey = $env:OPENAI_API_KEY
if ([string]::IsNullOrWhiteSpace($ApiKey)) {
  Write-Error "OPENAI_API_KEY is not set."
  exit 2
}

$BaseUrl = $(if ($env:OPENAI_BASE_URL) { $env:OPENAI_BASE_URL.TrimEnd("/") } else { "https://api.openai.com" })
$Endpoint = "$BaseUrl/v1/images"

$Payload = [ordered]@{
  model  = $Model
  prompt = $Prompt
  size   = $Size
  n      = $N
}

if (-not [string]::IsNullOrWhiteSpace($Quality)) { $Payload.quality = $Quality }
if (-not [string]::IsNullOrWhiteSpace($Style))   { $Payload.style   = $Style }

# dall-e-3 supports response_format; gpt-image models always return base64.
if ($Model -like "dall-e*") {
  $Payload.response_format = "b64_json"
}

$Headers = @{
  Authorization = "Bearer $ApiKey"
  "Content-Type" = "application/json"
}

if ($VerboseOutput) {
  Write-Host "Endpoint: $Endpoint"
  Write-Host "Payload:"
  $Payload | ConvertTo-Json -Depth 10 | Write-Host
}

try {
  $Resp = Invoke-RestMethod -Method Post -Uri $Endpoint -Headers $Headers -Body ($Payload | ConvertTo-Json -Depth 10) -TimeoutSec 120
} catch {
  Write-Error "ERROR calling Images API: $($_.Exception.Message)"
  exit 3
}

if ($null -eq $Resp.data -or $Resp.data.Count -eq 0) {
  Write-Error "ERROR: No images returned."
  exit 4
}

if (-not (Test-Path $OutDir)) { New-Item -ItemType Directory -Path $OutDir | Out-Null }

$Stamp = Get-UtcStamp
$Saved = @()
$Index = 0

foreach ($Item in $Resp.data) {
  $Index++
  $OutName = "$OutPrefix-$Stamp-$Index.png"
  $OutPath = Join-Path $OutDir $OutName

  if ($Item.PSObject.Properties.Name -contains "b64_json") {
    $Bytes = [System.Convert]::FromBase64String($Item.b64_json)
    [System.IO.File]::WriteAllBytes($OutPath, $Bytes)
  } elseif ($Item.PSObject.Properties.Name -contains "url") {
    Invoke-WebRequest -Uri $Item.url -OutFile $OutPath -TimeoutSec 120 | Out-Null
  } else {
    Write-Error ("ERROR: Unexpected item keys: " + ($Item.PSObject.Properties.Name -join ","))
    exit 5
  }

  $Saved += $OutPath
}

# Print saved files (one per line)
$Saved | ForEach-Object { Write-Output $_ }
