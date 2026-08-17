# Install the OpenCode Chinese TUI (preview) or management CLI (stable) on Windows x64.
param(
    [string]$Version = "",
    [switch]$Preview
)

$ErrorActionPreference = "Stop"
# 预览版指示：-Preview 参数，或由 install-preview.ps1 注入的 $script:Preview
$IsPreview = $Preview -or [bool]$script:Preview
$Repo = if ($env:OPENCODE_I18N_REPO) { $env:OPENCODE_I18N_REPO } else { "yuloop/OpenCodeChineseTranslationAuto" }

try {
    [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
    $OutputEncoding = [System.Text.Encoding]::UTF8
} catch {
    # Older hosts can continue with their current console encoding.
}

if (-not [Environment]::Is64BitOperatingSystem) {
    throw "仅支持 64 位 Windows。"
}
if ($env:PROCESSOR_ARCHITECTURE -eq "ARM64") {
    throw "当前自动发布暂不提供 Windows ARM64，请使用 Windows x64 或 WSL x64。"
}

# 预览版装到独立目录，与正式版互不覆盖
$InstallDir = if ($IsPreview) {
    Join-Path $env:LOCALAPPDATA "opencode-i18n-preview"
} else {
    Join-Path $env:USERPROFILE ".opencode-i18n"
}
$BinDir = Join-Path $InstallDir "bin"
$ExePath = Join-Path $BinDir "opencode.exe"
New-Item -ItemType Directory -Force -Path $BinDir | Out-Null

if ($IsPreview) {
    if (-not $Version) {
        Write-Host "正在查询最新预览版..." -ForegroundColor Yellow
        try {
            $Releases = Invoke-RestMethod `
                -Headers @{ Accept = "application/vnd.github+json"; "User-Agent" = "opencode-i18n-installer" } `
                -Uri "https://api.github.com/repos/$Repo/releases?per_page=10"
            $Release = $Releases | Where-Object { $_.prerelease -and $_.tag_name -like "*-cn-nightly*" } | Select-Object -First 1
            if (-not $Release) {
                throw "未找到 -cn-nightly 预览版 Release"
            }
            $Version = $Release.tag_name
        } catch {
            throw "无法读取最新预览版，请检查 GitHub 连接或使用 -Version 指定 tag。`n$($_.Exception.Message)"
        }
    }
} elseif (-not $Version) {
    Write-Host "正在查询最新版本..." -ForegroundColor Yellow
    try {
        $Release = Invoke-RestMethod `
            -Headers @{ Accept = "application/vnd.github+json"; "User-Agent" = "opencode-i18n-installer" } `
            -Uri "https://api.github.com/repos/$Repo/releases/latest"
        $Version = $Release.tag_name
    } catch {
        throw "无法读取最新版本，请检查 GitHub 连接或使用 -Version 指定版本。`n$($_.Exception.Message)"
    }
}

$AssetName = if ($IsPreview) {
    "opencode-zh-CN-$Version-windows-x64.zip"
} else {
    "opencode-cli-windows-amd64.exe"
}

$BaseUrl = "https://github.com/$Repo/releases/download/$Version"
$TempRoot = Join-Path ([IO.Path]::GetTempPath()) "opencode-i18n-$PID"
$TempExe = Join-Path $TempRoot $AssetName
$TempSums = Join-Path $TempRoot "SHA256SUMS"
New-Item -ItemType Directory -Force -Path $TempRoot | Out-Null

try {
    Write-Host "下载 $Repo $Version..." -ForegroundColor Yellow
    Invoke-WebRequest -Uri "$BaseUrl/$AssetName" -OutFile $TempExe
    Invoke-WebRequest -Uri "$BaseUrl/SHA256SUMS" -OutFile $TempSums

    $Pattern = "^([0-9a-fA-F]{64})\s+\*?$([regex]::Escape($AssetName))$"
    $ChecksumLine = Get-Content -LiteralPath $TempSums | Where-Object { $_ -match $Pattern } | Select-Object -First 1
    if (-not $ChecksumLine) {
        throw "SHA256SUMS 中找不到 $AssetName"
    }

    $Expected = ([regex]::Match($ChecksumLine, $Pattern).Groups[1].Value).ToLowerInvariant()
    $Actual = (Get-FileHash -Algorithm SHA256 -LiteralPath $TempExe).Hash.ToLowerInvariant()
    if ($Expected -ne $Actual) {
        throw "SHA-256 校验失败。期望 $Expected，实际 $Actual"
    }

    if ($IsPreview) {
        $TempExtract = Join-Path $TempRoot "extract"
        Expand-Archive -LiteralPath $TempExe -DestinationPath $TempExtract
        $ExtractedExe = Join-Path $TempExtract "opencode.exe"
        if (-not (Test-Path -LiteralPath $ExtractedExe)) {
            throw "压缩包中未找到 opencode.exe"
        }
        Move-Item -Force -LiteralPath $ExtractedExe -Destination $ExePath
    } else {
        $Backup = "$ExePath.old"
        if (Test-Path -LiteralPath $Backup) {
            Remove-Item -Force -LiteralPath $Backup
        }
        if (Test-Path -LiteralPath $ExePath) {
            Move-Item -Force -LiteralPath $ExePath -Destination $Backup
        }
        Move-Item -Force -LiteralPath $TempExe -Destination $ExePath
    }
} finally {
    if (Test-Path -LiteralPath $TempRoot) {
        Remove-Item -Recurse -Force -LiteralPath $TempRoot
    }
}

$UserPath = [Environment]::GetEnvironmentVariable("Path", "User")
$PathEntries = @($UserPath -split ";" | Where-Object { $_ })
if ($PathEntries -notcontains $BinDir) {
    $NewPath = (@($BinDir) + $PathEntries) -join ";"
    [Environment]::SetEnvironmentVariable("Path", $NewPath, "User")
}

Write-Host "安装完成：$ExePath" -ForegroundColor Green
if ($IsPreview) {
    Write-Host "重新打开终端后运行：opencode（预览版与正式版安装目录隔离，重跑同一命令即更新）" -ForegroundColor Cyan
} else {
    Write-Host "重新打开终端后运行：opencode-cli" -ForegroundColor Cyan
}