#Requires -Version 5.1
[CmdletBinding()]
param(
    [switch]$Apply,

    [ValidateRange(0, 30)]
    [int]$OlderThanDays = 2,

    [switch]$SkipBrowserCache,

    [switch]$SkipRecycleBin,

    [switch]$IncludeWindowsUpdateCache,

    [string]$LogPath = ""
)

$ErrorActionPreference = "SilentlyContinue"
$cutoff = (Get-Date).AddDays(-1 * $OlderThanDays)

function Format-Bytes {
    param([Nullable[Int64]]$Bytes)
    if ($null -eq $Bytes -or $Bytes -le 0) { return "0 B" }
    $units = @("B", "KB", "MB", "GB", "TB")
    $value = [double]$Bytes
    $index = 0
    while ($value -ge 1024 -and $index -lt ($units.Count - 1)) {
        $value = $value / 1024
        $index++
    }
    return ("{0:N2} {1}" -f $value, $units[$index])
}

function Get-FolderSizeBytes {
    param([string]$LiteralPath)
    if ([string]::IsNullOrWhiteSpace($LiteralPath) -or -not (Test-Path -LiteralPath $LiteralPath)) {
        return [int64]0
    }

    $size = [int64]0
    try {
        $size = [int64]((Get-ChildItem -LiteralPath $LiteralPath -Force -Recurse -File -ErrorAction SilentlyContinue |
            Where-Object { -not ($_.Attributes -band [IO.FileAttributes]::ReparsePoint) } |
            Measure-Object -Property Length -Sum).Sum)
    } catch {
        return $size
    }
    return $size
}

function Test-DangerousPath {
    param([string]$LiteralPath)
    if ([string]::IsNullOrWhiteSpace($LiteralPath)) { return $true }

    $full = [IO.Path]::GetFullPath($LiteralPath).TrimEnd('\')
    $dangerous = @(
        [IO.Path]::GetPathRoot($full).TrimEnd('\'),
        $env:SystemRoot.TrimEnd('\'),
        (Join-Path $env:SystemRoot "System32").TrimEnd('\'),
        $env:ProgramFiles.TrimEnd('\'),
        ${env:ProgramFiles(x86)}.TrimEnd('\'),
        $env:ProgramData.TrimEnd('\'),
        $env:USERPROFILE.TrimEnd('\'),
        (Join-Path $env:USERPROFILE "Documents").TrimEnd('\'),
        (Join-Path $env:USERPROFILE "Desktop").TrimEnd('\'),
        (Join-Path $env:USERPROFILE "Downloads").TrimEnd('\')
    ) | Where-Object { $_ }

    foreach ($item in $dangerous) {
        if ($full.Equals($item, [StringComparison]::OrdinalIgnoreCase)) {
            return $true
        }
    }
    return $false
}

function Remove-DirectoryContentsSafe {
    param(
        [string]$Label,
        [string]$Path,
        [string]$Risk = "低风险缓存"
    )

    if (-not (Test-Path -LiteralPath $Path)) {
        return [pscustomobject]@{
            label = $Label
            path = $Path
            risk = $Risk
            mode = if ($Apply) { "apply" } else { "preview" }
            before_bytes = 0
            after_bytes = 0
            freed_bytes = 0
            before = "0 B"
            freed = "0 B"
            status = "不存在，跳过"
        }
    }

    if (Test-DangerousPath -LiteralPath $Path) {
        return [pscustomobject]@{
            label = $Label
            path = $Path
            risk = "已拦截"
            mode = if ($Apply) { "apply" } else { "preview" }
            before_bytes = 0
            after_bytes = 0
            freed_bytes = 0
            before = "0 B"
            freed = "0 B"
            status = "路径过于敏感，脚本已拒绝处理"
        }
    }

    $before = Get-FolderSizeBytes -LiteralPath $Path
    $status = "预览：不会删除"
    $after = $before

    if ($Apply) {
        $items = Get-ChildItem -LiteralPath $Path -Force -ErrorAction SilentlyContinue |
            Where-Object {
                -not ($_.Attributes -band [IO.FileAttributes]::ReparsePoint) -and
                $_.LastWriteTime -lt $cutoff
            }

        foreach ($item in $items) {
            Remove-Item -LiteralPath $item.FullName -Recurse -Force -ErrorAction SilentlyContinue
        }

        $after = Get-FolderSizeBytes -LiteralPath $Path
        $status = "已清理；被占用或较新的文件会保留"
    }

    [pscustomobject]@{
        label = $Label
        path = $Path
        risk = $Risk
        mode = if ($Apply) { "apply" } else { "preview" }
        before_bytes = $before
        after_bytes = $after
        freed_bytes = [math]::Max(0, $before - $after)
        before = Format-Bytes $before
        freed = Format-Bytes ([math]::Max(0, $before - $after))
        status = $status
    }
}

function Clear-RecycleBinSafe {
    param([string]$DriveLetter = "C")

    $path = "$DriveLetter`:\`$Recycle.Bin"
    $before = Get-FolderSizeBytes -LiteralPath $path
    $after = $before
    $status = "预览：不会清空回收站"

    if ($Apply) {
        Clear-RecycleBin -DriveLetter $DriveLetter -Force -ErrorAction SilentlyContinue
        $after = Get-FolderSizeBytes -LiteralPath $path
        $status = "已尝试清空回收站；权限不足的项目会保留"
    }

    [pscustomobject]@{
        label = "回收站"
        path = $path
        risk = "低风险但清空后不易恢复"
        mode = if ($Apply) { "apply" } else { "preview" }
        before_bytes = $before
        after_bytes = $after
        freed_bytes = [math]::Max(0, $before - $after)
        before = Format-Bytes $before
        freed = Format-Bytes ([math]::Max(0, $before - $after))
        status = $status
    }
}

function Get-BrowserCacheTargets {
    $targets = New-Object System.Collections.Generic.List[object]
    $browserBases = @(
        @{ Name = "Chrome"; Base = (Join-Path $env:LOCALAPPDATA "Google\Chrome\User Data") },
        @{ Name = "Edge"; Base = (Join-Path $env:LOCALAPPDATA "Microsoft\Edge\User Data") },
        @{ Name = "360 极速浏览器"; Base = (Join-Path $env:LOCALAPPDATA "360Chrome\Chrome\User Data") }
    )

    foreach ($browser in $browserBases) {
        if (-not (Test-Path -LiteralPath $browser.Base)) { continue }
        Get-ChildItem -LiteralPath $browser.Base -Directory -ErrorAction SilentlyContinue |
            ForEach-Object {
                foreach ($cacheName in @("Cache", "Code Cache", "GPUCache")) {
                    $cachePath = Join-Path $_.FullName $cacheName
                    if (Test-Path -LiteralPath $cachePath) {
                        $targets.Add([pscustomobject]@{
                            Label = "$($browser.Name) $($_.Name) $cacheName"
                            Path = $cachePath
                            Risk = "低风险浏览器缓存"
                        }) | Out-Null
                    }
                }
            }
    }
    $targets
}

function Test-IsAdministrator {
    $identity = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($identity)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

$records = New-Object System.Collections.Generic.List[object]

$targets = @(
    @{ Label = "当前用户临时文件"; Path = $env:TEMP; Risk = "低风险临时文件" },
    @{ Label = "Windows 临时文件"; Path = (Join-Path $env:SystemRoot "Temp"); Risk = "低风险临时文件" },
    @{ Label = "Windows 错误报告"; Path = (Join-Path $env:LOCALAPPDATA "Microsoft\Windows\WER"); Risk = "低风险诊断缓存" },
    @{ Label = "缩略图缓存"; Path = (Join-Path $env:LOCALAPPDATA "Microsoft\Windows\Explorer"); Risk = "低风险缓存" }
)

foreach ($target in $targets) {
    $records.Add((Remove-DirectoryContentsSafe -Label $target.Label -Path $target.Path -Risk $target.Risk)) | Out-Null
}

if (-not $SkipBrowserCache) {
    foreach ($target in Get-BrowserCacheTargets) {
        $records.Add((Remove-DirectoryContentsSafe -Label $target.Label -Path $target.Path -Risk $target.Risk)) | Out-Null
    }
}

if (-not $SkipRecycleBin) {
    $records.Add((Clear-RecycleBinSafe -DriveLetter "C")) | Out-Null
}

if ($IncludeWindowsUpdateCache) {
    $updateCache = Join-Path $env:ProgramData "Microsoft\Windows\DeliveryOptimization\Cache"
    if (Test-IsAdministrator) {
        $records.Add((Remove-DirectoryContentsSafe -Label "Windows 更新传递优化缓存" -Path $updateCache -Risk "需管理员权限的系统缓存")) | Out-Null
    } else {
        $cacheSize = Get-FolderSizeBytes -LiteralPath $updateCache
        $records.Add([pscustomobject]@{
            label = "Windows 更新传递优化缓存"
            path = $updateCache
            risk = "需管理员权限"
            mode = if ($Apply) { "apply" } else { "preview" }
            before_bytes = $cacheSize
            after_bytes = $cacheSize
            freed_bytes = 0
            before = Format-Bytes $cacheSize
            freed = "0 B"
            status = "当前不是管理员，已跳过"
        }) | Out-Null
    }
}

$totalBefore = [int64](($records | Measure-Object -Property before_bytes -Sum).Sum)
$totalFreed = [int64](($records | Measure-Object -Property freed_bytes -Sum).Sum)

if ([string]::IsNullOrWhiteSpace($LogPath)) {
    $LogPath = Join-Path $env:TEMP ("c-drive-cleanup-{0}.json" -f (Get-Date -Format "yyyyMMdd-HHmmss"))
}

$log = [ordered]@{
    generated_at = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
    mode = if ($Apply) { "apply" } else { "preview" }
    older_than_days = $OlderThanDays
    total_candidate_bytes = $totalBefore
    total_candidate = Format-Bytes $totalBefore
    total_freed_bytes = $totalFreed
    total_freed = Format-Bytes $totalFreed
    note = if ($Apply) { "已执行低风险清理。锁定文件、较新文件和权限不足项目会保留。" } else { "预览模式，没有删除任何文件。确认后加 -Apply 执行。" }
    items = @($records)
}

$log | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $LogPath -Encoding UTF8

Write-Host ""
if ($Apply) {
    Write-Host "=== C 盘低风险清理完成 ===" -ForegroundColor Cyan
    Write-Host ("本轮释放：{0}" -f (Format-Bytes $totalFreed))
} else {
    Write-Host "=== C 盘低风险清理预览 ===" -ForegroundColor Cyan
    Write-Host ("预计候选：{0}" -f (Format-Bytes $totalBefore))
    Write-Host "当前没有删除任何文件。确认后重新运行并加上 -Apply。"
}
Write-Host ("日志文件：{0}" -f $LogPath)
Write-Host ""

$records |
    Sort-Object before_bytes -Descending |
    ForEach-Object {
        if ($Apply) {
            Write-Host ("- {0}: 释放 {1} / 原有 {2}  {3}" -f $_.label, $_.freed, $_.before, $_.status)
        } else {
            Write-Host ("- {0}: 可检查 {1}  {2}" -f $_.label, $_.before, $_.path)
        }
    }

Write-Host ""
Write-Host "提示：聊天文件、下载目录、大文件、虚拟机镜像不属于本脚本自动清理范围，需要单独确认。" -ForegroundColor Yellow
