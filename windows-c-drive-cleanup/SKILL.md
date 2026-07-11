---
name: windows-c-drive-cleanup
description: "Help Chinese Windows beginners clean the C drive safely with PowerShell. Use when the user wants to free space on Windows C:, asks why C: is full, needs Chinese-localized cleanup for WeChat/QQ/DingTalk/Feishu/Baidu Netdisk/Thunder/WPS/browser caches, or needs step-by-step C drive cleanup with habit fixes. Prioritize releasing space, then explain major causes and prevention."
---

# Windows C Drive Cleanup

## Core Promise

Help Chinese Windows beginners clean C drive space first, then briefly explain what caused the space pressure and how to prevent it from coming back.

Operate like a careful assistant, not a lecture. Keep language simple, Chinese by default, and avoid long filesystem jargon unless it changes a decision.

## Safety Rules

- Start with low-risk cleanup whenever reasonable; do not turn the session into diagnosis-only work.
- Never delete user documents, photos, videos, desktop files, downloads, chat files, project folders, virtual disks, or app data without explicit item-by-item confirmation.
- Treat `C:\Windows`, `C:\Windows\System32`, `C:\Program Files`, `C:\Program Files (x86)`, `C:\ProgramData`, recovery partitions, driver folders, registry data, and unknown `AppData` folders as protected.
- Prefer PowerShell scripts in this skill over improvised delete commands.
- Run cleanup scripts in preview mode first unless the user has already clearly asked to execute cleanup.
- Before any actual deletion, show what will be cleaned, why it is low risk, and that locked files may be skipped.
- If elevation is needed, explain it in Chinese and continue with non-admin cleanup if possible.
- After cleanup, re-check free space and summarize released space.

## Workflow

1. Confirm the machine is Windows and the target is C drive if unclear.
2. Run safe cleanup first when the user wants immediate help:
   ```powershell
   powershell -ExecutionPolicy Bypass -File "$env:USERPROFILE\.codex\skills\windows-c-drive-cleanup\scripts\clean-safe-items.ps1"
   ```
3. Show the preview in Chinese. If it only contains low-risk items and the user approves, run:
   ```powershell
   powershell -ExecutionPolicy Bypass -File "$env:USERPROFILE\.codex\skills\windows-c-drive-cleanup\scripts\clean-safe-items.ps1" -Apply
   ```
4. Run the scanner to identify remaining large sources:
   ```powershell
   powershell -ExecutionPolicy Bypass -File "$env:USERPROFILE\.codex\skills\windows-c-drive-cleanup\scripts\scan-c-drive.ps1"
   ```
5. Explain results as "主要是谁占了 C 盘", not as raw path dumps.
6. Suggest the next round:
   - Low risk: continue safe cache cleanup.
   - Medium risk: ask before deleting app caches, old installers, or duplicate downloads.
   - High risk: suggest migration or user review, not deletion.
7. End with at most three prevention suggestions, chosen from the user's actual results.

## Script Resources

- `scripts/clean-safe-items.ps1`: Low-risk cleanup helper. Defaults to preview mode. Requires `-Apply` to delete.
- `scripts/scan-c-drive.ps1`: Read-only scanner for disk pressure, common Chinese apps, cleanup candidates, large user files, and C-installed apps.

When paths differ, read the script and adapt only the invocation parameters. Do not rewrite bulk deletion logic inline.

## Reference Resources

- `references/cleanup-risk-levels.md`: Use when deciding what can be auto-cleaned, what needs confirmation, and what must be protected.
- `references/chinese-windows-apps.md`: Use when interpreting WeChat, QQ, DingTalk, Feishu, Baidu Netdisk, Thunder, WPS, Tencent Meeting, browser, and similar local app data.
- `references/habit-diagnosis.md`: Use after cleanup to give short, practical prevention advice.

Load only the reference needed for the current decision.

## Reporting Style

Use short Chinese summaries:

- "先帮你做一轮低风险清理，主要清临时文件、回收站和浏览器缓存。"
- "这轮预计可清理约 X GB。确认后我再执行。"
- "清理后 C 盘多出了 X GB。剩下的大头是微信文件和下载目录。"
- "这些不是垃圾，我不会直接删：照片、聊天文件、虚拟机镜像、项目文件。"

Avoid scaring the user. Avoid telling beginners to manually search and delete unknown system folders.
