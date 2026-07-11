# Cleanup Risk Levels

Use these levels when explaining cleanup choices to Chinese Windows beginners.

## Low Risk

Can be previewed and cleaned with `scripts/clean-safe-items.ps1` after user approval.

- Current user temp folder: `%TEMP%`
- Windows temp folder: `C:\Windows\Temp`
- Browser cache folders such as Chrome/Edge `Cache`, `Code Cache`, `GPUCache`
- Windows Error Reporting cache
- Thumbnail cache
- Recycle Bin, but mention that clearing it is hard to undo

Say: "这些主要是临时缓存，清理后软件可能重新生成。"

## Medium Risk

Do not auto-delete. Ask item-by-item.

- Downloads folder installers, `.zip`, `.rar`, `.7z`, `.iso`
- WeChat/QQ/DingTalk/Feishu cache folders
- Old browser downloads
- Duplicate videos, screen recordings, exported meeting recordings
- Baidu Netdisk/Thunder downloaded files
- Windows update Delivery Optimization cache when not using the dedicated script option

Say: "这些可能有用，我先帮你挑出来，删不删你确认。"

## High Risk

Do not delete. Recommend migration, backup, or app settings changes.

- Documents, pictures, videos, desktop work files
- WeChat/QQ chat files and received files unless the user identifies them as disposable
- Virtual machine disks: `.vhd`, `.vhdx`, `.vmdk`, `.qcow2`
- WSL or Docker data
- Source code/project folders
- Game libraries and save data
- `C:\Windows`, `System32`, `Program Files`, `ProgramData`, driver folders

Say: "这类不是垃圾，不能直接删。可以迁移到 D 盘或让软件改保存位置。"

## Forbidden Defaults

Never suggest beginners manually delete unknown files from system folders. Never use wildcard deletion over broad paths such as `C:\Users\*\AppData` or `C:\ProgramData\*`.
