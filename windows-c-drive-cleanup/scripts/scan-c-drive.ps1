#Requires -Version 5.1
[CmdletBinding()]
param(
    [ValidatePattern('^[A-Za-z]$')]
    [string]$DriveLetter = "C",

    [ValidateRange(5, 100)]
    [int]$TopCount = 20,

    [ValidateRange(50, 4096)]
    [int]$LargeFileMB = 500,

    [switch]$FullDriveLargeFileScan,

    [string]$OutputPath = ""
)

$ErrorActionPreference = "SilentlyContinue"
$driveName = $DriveLetter.ToUpperInvariant()
$driveRoot = "$driveName`:\"

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

function New-SizeRecord {
    param(
        [string]$Name,
        [string]$Path,
        [string]$Category,
        [string]$Risk = "只读统计"
    )

    $bytes = Get-FolderSizeBytes -LiteralPath $Path
    [pscustomobject]@{
        name = $Name
        category = $Category
        path = $Path
        bytes = $bytes
        size = Format-Bytes $bytes
        risk = $Risk
        exists = (Test-Path -LiteralPath $Path)
    }
}

function Add-ExistingSizeRecord {
    param(
        [System.Collections.Generic.List[object]]$List,
        [string]$Name,
        [string]$Path,
        [string]$Category,
        [string]$Risk = "只读统计"
    )
    if (-not [string]::IsNullOrWhiteSpace($Path) -and (Test-Path -LiteralPath $Path)) {
        $List.Add((New-SizeRecord -Name $Name -Path $Path -Category $Category -Risk $Risk)) | Out-Null
    }
}

function Get-InstalledAppsOnC {
    $registryPaths = @(
        "HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\*",
        "HKLM:\Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\*",
        "HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\*"
    )

    $items = foreach ($path in $registryPaths) {
        Get-ItemProperty -Path $path -ErrorAction SilentlyContinue |
            Where-Object {
                $_.DisplayName -and $_.InstallLocation -and
                ($_.InstallLocation -like "$driveName`:\*")
            } |
            Select-Object DisplayName, DisplayVersion, Publisher, InstallLocation
    }

    $items |
        Sort-Object DisplayName -Unique |
        Select-Object -First 80
}

function Get-LargeFiles {
    param([string[]]$Roots)

    $threshold = [int64]$LargeFileMB * 1MB
    $results = New-Object System.Collections.Generic.List[object]

    foreach ($root in $Roots) {
        if (-not (Test-Path -LiteralPath $root)) { continue }
        Get-ChildItem -LiteralPath $root -Force -Recurse -File -ErrorAction SilentlyContinue |
            Where-Object {
                $_.Length -ge $threshold -and
                -not ($_.Attributes -band [IO.FileAttributes]::ReparsePoint)
            } |
            Sort-Object Length -Descending |
            Select-Object -First $TopCount |
            ForEach-Object {
                $results.Add([pscustomobject]@{
                    name = $_.Name
                    path = $_.FullName
                    bytes = [int64]$_.Length
                    size = Format-Bytes $_.Length
                    last_write_time = $_.LastWriteTime.ToString("yyyy-MM-dd HH:mm:ss")
                    note = "大文件不是垃圾，删除前必须确认用途"
                }) | Out-Null
            }
    }

    $results | Sort-Object bytes -Descending | Select-Object -First $TopCount
}

$drive = Get-CimInstance Win32_LogicalDisk -Filter "DeviceID='$driveName`:'"
if (-not $drive) {
    Write-Error "没有找到 $driveName 盘。"
    exit 1
}

$userProfile = $env:USERPROFILE
$appData = $env:APPDATA
$localAppData = $env:LOCALAPPDATA
$programData = $env:ProgramData

$knownFolders = New-Object System.Collections.Generic.List[object]
$knownFolderMap = @(
    @{ Name = "桌面"; Path = (Join-Path $userProfile "Desktop"); Category = "用户文件" },
    @{ Name = "下载"; Path = (Join-Path $userProfile "Downloads"); Category = "用户文件" },
    @{ Name = "文档"; Path = (Join-Path $userProfile "Documents"); Category = "用户文件" },
    @{ Name = "图片"; Path = (Join-Path $userProfile "Pictures"); Category = "用户文件" },
    @{ Name = "视频"; Path = (Join-Path $userProfile "Videos"); Category = "用户文件" },
    @{ Name = "音乐"; Path = (Join-Path $userProfile "Music"); Category = "用户文件" }
)
foreach ($item in $knownFolderMap) {
    Add-ExistingSizeRecord -List $knownFolders -Name $item.Name -Path $item.Path -Category $item.Category -Risk "用户文件，不能自动删除"
}

$cleanupCandidates = New-Object System.Collections.Generic.List[object]
$candidatePaths = @(
    @{ Name = "当前用户临时文件"; Path = $env:TEMP; Category = "低风险缓存" },
    @{ Name = "Windows 临时文件"; Path = (Join-Path $env:SystemRoot "Temp"); Category = "低风险缓存" },
    @{ Name = "Windows 错误报告"; Path = (Join-Path $localAppData "Microsoft\Windows\WER"); Category = "低风险缓存" },
    @{ Name = "Delivery Optimization 下载缓存"; Path = (Join-Path $programData "Microsoft\Windows\DeliveryOptimization\Cache"); Category = "需管理员确认" },
    @{ Name = "回收站"; Path = "$driveRoot`$Recycle.Bin"; Category = "低风险但不可恢复" }
)
foreach ($item in $candidatePaths) {
    Add-ExistingSizeRecord -List $cleanupCandidates -Name $item.Name -Path $item.Path -Category $item.Category -Risk "可清理候选，执行前仍需预览"
}

$browserBases = @(
    @{ Name = "Chrome"; Base = (Join-Path $localAppData "Google\Chrome\User Data") },
    @{ Name = "Edge"; Base = (Join-Path $localAppData "Microsoft\Edge\User Data") },
    @{ Name = "360 极速浏览器"; Base = (Join-Path $localAppData "360Chrome\Chrome\User Data") }
)
foreach ($browser in $browserBases) {
    if (-not (Test-Path -LiteralPath $browser.Base)) { continue }
    Get-ChildItem -LiteralPath $browser.Base -Directory -ErrorAction SilentlyContinue |
        ForEach-Object {
            foreach ($cacheName in @("Cache", "Code Cache", "GPUCache")) {
                Add-ExistingSizeRecord -List $cleanupCandidates -Name "$($browser.Name) $($_.Name) $cacheName" -Path (Join-Path $_.FullName $cacheName) -Category "浏览器缓存" -Risk "低风险缓存"
            }
        }
}

$chineseApps = New-Object System.Collections.Generic.List[object]
$appCandidates = @(
    @{ Name = "微信文件"; Paths = @((Join-Path $userProfile "Documents\WeChat Files"), (Join-Path $appData "Tencent\WeChat"), (Join-Path $localAppData "Tencent\WeChat")) },
    @{ Name = "QQ 文件"; Paths = @((Join-Path $userProfile "Documents\Tencent Files"), (Join-Path $appData "Tencent\QQ"), (Join-Path $localAppData "Tencent\QQ")) },
    @{ Name = "企业微信"; Paths = @((Join-Path $appData "Tencent\WXWork"), (Join-Path $localAppData "Tencent\WXWork"), (Join-Path $userProfile "Documents\WXWork")) },
    @{ Name = "钉钉"; Paths = @((Join-Path $appData "DingTalk"), (Join-Path $localAppData "DingTalk"), (Join-Path $userProfile "Documents\DingTalk")) },
    @{ Name = "飞书/Lark"; Paths = @((Join-Path $appData "Feishu"), (Join-Path $localAppData "Feishu"), (Join-Path $appData "LarkShell"), (Join-Path $localAppData "Lark")) },
    @{ Name = "百度网盘"; Paths = @((Join-Path $appData "baidu\BaiduNetdisk"), (Join-Path $localAppData "baidu\BaiduNetdisk"), (Join-Path $userProfile "BaiduNetdiskDownload")) },
    @{ Name = "迅雷"; Paths = @((Join-Path $appData "Thunder Network"), (Join-Path $localAppData "Thunder Network"), (Join-Path $userProfile "Downloads\Thunder")) },
    @{ Name = "WPS"; Paths = @((Join-Path $appData "Kingsoft"), (Join-Path $localAppData "Kingsoft"), (Join-Path $userProfile "Documents\WPS Cloud Files")) },
    @{ Name = "腾讯会议"; Paths = @((Join-Path $appData "Tencent\WeMeet"), (Join-Path $localAppData "Tencent\WeMeet")) }
)
foreach ($app in $appCandidates) {
    foreach ($path in $app.Paths) {
        Add-ExistingSizeRecord -List $chineseApps -Name $app.Name -Path $path -Category "中文常见软件" -Risk "多为用户数据或缓存，不能自动删除"
    }
}

$largeFileRoots = @($userProfile)
if ($FullDriveLargeFileScan) {
    $largeFileRoots = @($driveRoot)
}
$largeFiles = @(Get-LargeFiles -Roots $largeFileRoots)
$installedOnC = @(Get-InstalledAppsOnC)

$report = [ordered]@{
    generated_at = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
    note = "本报告只读扫描，不会删除任何文件。"
    drive = [ordered]@{
        letter = "$driveName`:"
        total_bytes = [int64]$drive.Size
        free_bytes = [int64]$drive.FreeSpace
        used_bytes = [int64]($drive.Size - $drive.FreeSpace)
        total = Format-Bytes $drive.Size
        free = Format-Bytes $drive.FreeSpace
        used = Format-Bytes ($drive.Size - $drive.FreeSpace)
        free_percent = if ($drive.Size -gt 0) { [math]::Round(($drive.FreeSpace / $drive.Size) * 100, 2) } else { 0 }
    }
    cleanup_candidates = @($cleanupCandidates | Sort-Object bytes -Descending)
    known_folders = @($knownFolders | Sort-Object bytes -Descending)
    chinese_apps = @($chineseApps | Sort-Object bytes -Descending)
    large_files = $largeFiles
    installed_apps_on_c = $installedOnC
    installed_apps_on_c_count = $installedOnC.Count
    scan_scope = if ($FullDriveLargeFileScan) { "全 C 盘大文件扫描，可能较慢" } else { "当前用户目录大文件扫描" }
}

if ([string]::IsNullOrWhiteSpace($OutputPath)) {
    $OutputPath = Join-Path $env:TEMP ("c-drive-scan-{0}.json" -f (Get-Date -Format "yyyyMMdd-HHmmss"))
}

$report | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $OutputPath -Encoding UTF8

Write-Host ""
Write-Host "=== C 盘只读体检完成 ===" -ForegroundColor Cyan
Write-Host ("C 盘容量：总计 {0}，剩余 {1}（{2}%）" -f $report.drive.total, $report.drive.free, $report.drive.free_percent)
Write-Host ("报告文件：{0}" -f $OutputPath)
Write-Host ""

Write-Host "可清理候选（预估）："
$cleanupCandidates |
    Sort-Object bytes -Descending |
    Select-Object -First 8 |
    ForEach-Object { Write-Host ("- {0}: {1}  {2}" -f $_.name, $_.size, $_.path) }

Write-Host ""
Write-Host "用户文件夹占用："
$knownFolders |
    Sort-Object bytes -Descending |
    ForEach-Object { Write-Host ("- {0}: {1}  {2}" -f $_.name, $_.size, $_.path) }

if ($chineseApps.Count -gt 0) {
    Write-Host ""
    Write-Host "中文常见软件占用："
    $chineseApps |
        Sort-Object bytes -Descending |
        Select-Object -First 10 |
        ForEach-Object { Write-Host ("- {0}: {1}  {2}" -f $_.name, $_.size, $_.path) }
}

if ($largeFiles.Count -gt 0) {
    Write-Host ""
    Write-Host "大文件提示（不是垃圾，删除前要确认）："
    $largeFiles |
        Select-Object -First 8 |
        ForEach-Object { Write-Host ("- {0}: {1}  {2}" -f $_.name, $_.size, $_.path) }
}

Write-Host ""
Write-Host "下一步：先用 clean-safe-items.ps1 做低风险清理；聊天文件、下载文件和大文件必须单独确认。" -ForegroundColor Yellow
