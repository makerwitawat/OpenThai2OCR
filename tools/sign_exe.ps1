param(
    [string]$Path = "dist\OpenThai2OCR.exe",
    [string]$Pfx = $env:SIGN_PFX,
    [string]$Password = $env:SIGN_PFX_PASSWORD,
    [string]$Thumbprint = $env:SIGN_THUMBPRINT,
    [string]$TimestampUrl = $(if ($env:SIGN_TIMESTAMP_URL) { $env:SIGN_TIMESTAMP_URL } else { "http://timestamp.digicert.com" })
)
$ErrorActionPreference = "Stop"

if (-not (Test-Path -LiteralPath $Path)) { throw "ไม่พบไฟล์ที่ต้องเซ็น: $Path" }
$Path = (Resolve-Path -LiteralPath $Path).Path

function Find-SignTool {
    $cmd = Get-Command signtool.exe -ErrorAction SilentlyContinue
    if ($cmd) { return $cmd.Source }
    $roots = @(
        (Join-Path ${env:ProgramFiles(x86)} "Windows Kits\10\bin"),
        (Join-Path $env:ProgramFiles "Windows Kits\10\bin")
    ) | Where-Object { $_ -and (Test-Path -LiteralPath $_) }
    return Get-ChildItem -Path $roots -Filter signtool.exe -Recurse -ErrorAction SilentlyContinue |
        Where-Object { $_.FullName -match "\\x64\\" } |
        Sort-Object FullName -Descending |
        Select-Object -First 1 -ExpandProperty FullName
}

$signtool = Find-SignTool
if (-not $signtool) {
    throw "ไม่พบ signtool.exe — ติดตั้ง Windows SDK หรือเพิ่มโฟลเดอร์ bin ของ SDK ลง PATH"
}

$signArgs = @("sign", "/fd", "SHA256", "/tr", $TimestampUrl, "/td", "SHA256")
if ($Pfx) {
    if (-not (Test-Path -LiteralPath $Pfx)) { throw "ไม่พบไฟล์ .pfx: $Pfx" }
    $signArgs += @("/f", (Resolve-Path -LiteralPath $Pfx).Path)
    if ($Password) { $signArgs += @("/p", $Password) }
} elseif ($Thumbprint) {
    $signArgs += @("/sha1", ($Thumbprint -replace "\s", ""))
} else {
    throw "ต้องระบุ SIGN_PFX (+ SIGN_PFX_PASSWORD) หรือ SIGN_THUMBPRINT ก่อนเซ็นชื่อ"
}
$signArgs += $Path

Write-Host "signtool: $signtool"
& $signtool @signArgs
if ($LASTEXITCODE -ne 0) { throw "signtool sign ล้มเหลว (exit $LASTEXITCODE)" }

& $signtool verify /pa /v $Path
if ($LASTEXITCODE -ne 0) { throw "ตรวจลายเซ็นไม่ผ่าน (exit $LASTEXITCODE)" }

$info = Get-AuthenticodeSignature -LiteralPath $Path
Write-Host ("ลายเซ็น: {0} · ผู้ออก: {1}" -f $info.Status, $info.SignerCertificate.Subject)