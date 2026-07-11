# Chinese Windows App Patterns

Use this reference when scan results include common Chinese apps.

## WeChat

Common paths:

- `%USERPROFILE%\Documents\WeChat Files`
- `%APPDATA%\Tencent\WeChat`
- `%LOCALAPPDATA%\Tencent\WeChat`

Likely cause: chat files, received files, images, videos, and cache. Do not auto-delete chat files. Prefer guiding the user to WeChat settings to move the file location to another drive, then clean old large files with confirmation.

## QQ

Common paths:

- `%USERPROFILE%\Documents\Tencent Files`
- `%APPDATA%\Tencent\QQ`
- `%LOCALAPPDATA%\Tencent\QQ`

Treat similarly to WeChat. Received files may be important.

## Enterprise WeChat / WXWork

Common paths:

- `%APPDATA%\Tencent\WXWork`
- `%LOCALAPPDATA%\Tencent\WXWork`
- `%USERPROFILE%\Documents\WXWork`

Work chat files can be important. Avoid deletion unless the user confirms specific files.

## DingTalk

Common paths:

- `%APPDATA%\DingTalk`
- `%LOCALAPPDATA%\DingTalk`
- `%USERPROFILE%\Documents\DingTalk`

Cache may be cleanable inside the app. Work files need confirmation.

## Feishu / Lark

Common paths:

- `%APPDATA%\Feishu`
- `%LOCALAPPDATA%\Feishu`
- `%APPDATA%\LarkShell`
- `%LOCALAPPDATA%\Lark`

Prefer app settings or item-by-item deletion.

## Baidu Netdisk

Common paths:

- `%USERPROFILE%\BaiduNetdiskDownload`
- `%APPDATA%\baidu\BaiduNetdisk`
- `%LOCALAPPDATA%\baidu\BaiduNetdisk`

Downloaded files are user data, not cache. Suggest moving the download directory to another drive.

## Thunder

Common paths:

- `%APPDATA%\Thunder Network`
- `%LOCALAPPDATA%\Thunder Network`
- `%USERPROFILE%\Downloads\Thunder`

Downloaded videos/installers may be large. Ask before deleting.

## WPS

Common paths:

- `%APPDATA%\Kingsoft`
- `%LOCALAPPDATA%\Kingsoft`
- `%USERPROFILE%\Documents\WPS Cloud Files`

Cloud files and local documents are user data. Avoid automatic deletion.

## Tencent Meeting

Common paths:

- `%APPDATA%\Tencent\WeMeet`
- `%LOCALAPPDATA%\Tencent\WeMeet`

Meeting recordings can be large and should be confirmed before deletion.
