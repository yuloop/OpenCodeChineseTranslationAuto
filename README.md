# OpenCode CLI / TUI 简体中文自动构建

[![CI](https://github.com/yuloop/OpenCodeChineseTranslationAuto/actions/workflows/ci.yml/badge.svg)](https://github.com/yuloop/OpenCodeChineseTranslationAuto/actions/workflows/ci.yml)
[![Auto Release](https://github.com/yuloop/OpenCodeChineseTranslationAuto/actions/workflows/release.yml/badge.svg)](https://github.com/yuloop/OpenCodeChineseTranslationAuto/actions/workflows/release.yml)
[![Latest Release](https://img.shields.io/github/v/release/yuloop/OpenCodeChineseTranslationAuto?label=最新版)](https://github.com/yuloop/OpenCodeChineseTranslationAuto/releases/latest)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

这是面向终端的 OpenCode CLI / TUI 社区汉化版，不是网页翻译或桌面壳。

仓库每小时检查一次 [OpenCode 官方 Release](https://github.com/anomalyco/opencode/releases)，自动取得对应源码、应用简体中文翻译、构建便携二进制并发布到 [Releases](https://github.com/yuloop/OpenCodeChineseTranslationAuto/releases)。

> 非官方项目，与 OpenCode 官方团队没有隶属关系。账号、模型配置和工作目录格式均沿用官方 OpenCode。

## 支持平台

| 平台 | 汉化版 OpenCode | 管理工具 |
|---|---:|---:|
| Windows x64 | ✅ | ✅ |
| Linux x64 / WSL x64 | ✅ | ✅ |
| Windows ARM64、macOS、Linux ARM64 | 暂未自动发布 | 暂未自动发布 |

## 快速安装

### 正式版（跟随官方 Release）

安装的是 `opencode-cli` 管理工具；随后用它下载经过校验的汉化版 OpenCode。

### Windows x64

```powershell
irm https://raw.githubusercontent.com/yuloop/OpenCodeChineseTranslationAuto/main/install.ps1 | iex
```

重新打开终端后：

```powershell
opencode-cli download
opencode
```

### Linux x64 / WSL x64

```bash
curl -fsSL https://raw.githubusercontent.com/yuloop/OpenCodeChineseTranslationAuto/main/install.sh | bash
```

重新打开终端后：

```bash
opencode-cli download
opencode
```

不希望通过管道执行脚本时，可以先下载并检查 `install.ps1` 或 `install.sh`，也可以直接从 Releases 下载对应压缩包。安装脚本会同时下载 `SHA256SUMS` 并校验管理工具。

### 实时预览版（dev 分支，每日多次更新）

> 预览版安装到独立目录（Linux `~/.opencode-i18n-preview`、Windows `%LOCALAPPDATA%\opencode-i18n-preview`），与正式版互不影响；重跑同一命令即更新。上游 `dev` 每有新提交就发布新 tag，Releases 页面只保留最新 1 个预览条目。

Windows PowerShell：

```powershell
powershell -Command "irm https://raw.githubusercontent.com/yuloop/OpenCodeChineseTranslationAuto/main/install-preview.ps1 | iex"
```

Linux / WSL：

```bash
curl -fsSL https://raw.githubusercontent.com/yuloop/OpenCodeChineseTranslationAuto/main/install.sh | bash -s -- --preview
```

安装的是汉化版 OpenCode TUI 本体，重新打开终端后直接运行 `opencode`。

## 自动汉化怎样工作

```text
官方 OpenCode Release
        ↓ 每小时检查
检出精确 tag 的官方源码
        ↓
497 条已维护翻译规则执行 100% 匹配门禁
        ↓ 通过
构建 Windows x64 / Linux x64
        ↓
生成 SHA256SUMS 并发布 Release
```

- 自动化不会偷偷修改用户机器上的官方安装。
- 翻译以源码字符串替换规则维护，当前基线为 OpenCode `v1.18.9`。
- 上游改动导致任何已知规则失配时，流水线会失败并停止发布；维护者确认新文案后再更新规则。这比在字符串变化后继续发布“半汉化”版本更可靠。
- 这里的“自动汉化”是自动跟踪、套用已审核译文、验证、构建和发布，不是未经审核地把新文本直接交给机器翻译。

手动运行发布任务时，可在 Actions 的 `OpenCode Chinese Release` 工作流里指定官方 tag；留空会使用最新正式版。

## 本地维护

要求：Go 版本以 [`cli-go/go.mod`](cli-go/go.mod) 为准；只有编译 OpenCode 时才需要官方仓库声明的 Bun 版本。

```bash
cd cli-go
go test ./...
go vet ./...
go build -o ../dist/opencode-cli .
```

验证翻译与某个官方源码版本是否完全匹配：

```bash
export OPENCODE_SOURCE_DIR=/path/to/opencode
./dist/opencode-cli apply --dry-run --strict --min-match-rate 1
./dist/opencode-cli verify --dry-run
```

翻译资源位于 [`cli-go/internal/core/assets/opencode-i18n`](cli-go/internal/core/assets/opencode-i18n)，发布流程位于 [`.github/workflows/release.yml`](.github/workflows/release.yml)。

## 来源与许可

本项目延续并维护以下社区工作的代码和翻译资源：

- [1186258278/OpenCodeChineseTranslation](https://github.com/1186258278/OpenCodeChineseTranslation)
- [Jarrel2024/OpenCodeChineseTranslation](https://github.com/Jarrel2024/OpenCodeChineseTranslation)

OpenCode 本体由其官方仓库维护，并按其自身许可证发布。本仓库中的自动化、管理工具和翻译资源按 [MIT License](LICENSE) 提供。
