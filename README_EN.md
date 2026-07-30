# Automated Simplified Chinese Builds for OpenCode CLI / TUI

This community project tracks official [OpenCode releases](https://github.com/anomalyco/opencode/releases), applies reviewed Simplified Chinese translations to the terminal CLI/TUI, validates every known replacement, and publishes portable Windows x64 and Linux x64 builds.

It is unofficial and is not affiliated with the OpenCode team.

## Install

Windows x64:

```powershell
irm https://raw.githubusercontent.com/yuloop/OpenCodeChineseTranslationAuto/main/install.ps1 | iex
opencode-cli download
```

Linux x64 or WSL x64:

```bash
curl -fsSL https://raw.githubusercontent.com/yuloop/OpenCodeChineseTranslationAuto/main/install.sh | bash
opencode-cli download
```

The installers verify the management CLI against the release `SHA256SUMS` file. You may also inspect the scripts first or download assets directly from [Releases](https://github.com/yuloop/OpenCodeChineseTranslationAuto/releases).

## Release policy

The scheduled workflow checks for a new official release every hour. A release is published only when all maintained translation rules match the exact upstream tag. Upstream text changes therefore stop the build until a maintainer reviews and updates the translations; the workflow does not publish a silently incomplete localization.

Current targets:

- Windows x64
- Linux x64, including WSL x64

Translation resources live in `cli-go/internal/core/assets/opencode-i18n`. The release workflow is `.github/workflows/release.yml`.

## Credits and license

This repository continues community work from [1186258278/OpenCodeChineseTranslation](https://github.com/1186258278/OpenCodeChineseTranslation) and [Jarrel2024/OpenCodeChineseTranslation](https://github.com/Jarrel2024/OpenCodeChineseTranslation).

Repository tooling and translation resources are available under the [MIT License](LICENSE). OpenCode itself remains subject to its upstream license.
