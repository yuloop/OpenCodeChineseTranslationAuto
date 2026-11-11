# OpenCode CLI / TUI 简体中文自动构建

[![CI](https://github.com/yuloop/OpenCodeChineseTranslationAuto/actions/workflows/ci.yml/badge.svg)](https://github.com/yuloop/OpenCodeChineseTranslationAuto/actions/workflows/ci.yml)
[![Auto Release](https://github.com/yuloop/OpenCodeChineseTranslationAuto/actions/workflows/release.yml/badge.svg)](https://github.com/yuloop/OpenCodeChineseTranslationAuto/actions/workflows/release.yml)
[![Latest Release](https://img.shields.io/github/v/release/yuloop/OpenCodeChineseTranslationAuto?label=最新版)](https://github.com/yuloop/OpenCodeChineseTranslationAuto/releases/latest)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## 汉化版与官方版差异

和上游官方版（anomalyco/opencode）相比，本仓库做了以下改进与补充：

| 维度 | 官方版（anomalyco/opencode） | 本仓库（汉化版） |
|---|---|---|
| 界面语言 | 已包含基础 zh-CN.json（19种语言） | 补充约 70 处终端交互翻译词条 |
| 构建自动化 | 无 | 自动同步上游 Release → 构建+发布（每天 1 次） |
| 一键安装 | 无 | install.sh / install.ps1 / install-preview.ps1 |
| V2 汉化线 | 无 | 跟随上游 v2.x tag（当前 v2.2.7），每天 1 次自动构建 |
| 发布平台 | 源码为主 | Linux x64 + Windows x64 便携二进制 |
| 翻译门禁 | 无 | 100% 匹配门禁后才允许发布 |
| upstream 追踪 | — | 每天 3 次检查上游、1 次检查官方 Release |

> **版本线说明**：上游已把主线切到 v2.x（当前 v2.2.7），v1 线停在 v1.19.5 不再更新，所以本仓库的例行发布也分两条：`release.yml` 跟随上游 `releases/latest`（目前仍指向 v1.19.5，没有新版本时自动跳过构建），`opencode-cn-v2-nightly.yml` 跟随上游最新 v2.x tag。

> 非官方项目，与 OpenCode 官方团队没有隶属关系。账号、模型配置和工作目录格式均沿用官方 OpenCode。

## 支持平台

| 平台 | 汉化版 OpenCode | 管理工具 |
|---|---:|---:|
| Windows x64 |  |  |
| Linux x64 / WSL x64 |  |  |
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

### 实时预览版（dev 分支，每日多次更新）

> 预览版安装到独立目录（Linux ~/.opencode-i18n-preview、Windows %LOCALAPPDATA%\opencode-i18n-preview），与正式版互不影响。

```powershell
powershell -Command "irm https://raw.githubusercontent.com/yuloop/OpenCodeChineseTranslationAuto/main/install-preview.ps1 | iex"
```

```bash
curl -fsSL https://raw.githubusercontent.com/yuloop/OpenCodeChineseTranslationAuto/main/install.sh | bash -s -- --preview
```

## 自动构建流程

```text
官方 OpenCode Release
        ↓ 定时检查（cron 见下表）
检出精确 tag 的官方源码
        ↓
注入汉化翻译词条（100% 匹配门禁）
        ↓
构建 Linux x64 + Windows x64 二进制
        ↓
发布到 GitHub Releases
```

### 定时频率（UTC，括号内为北京时间）

| 流水线 | cron | 频率 |
|---|---|---|
| `opencode-cn-sync.yml`（同步上游 dev） | `5 6,14,22 * * *` | 每天 3 次（14:05 / 22:05 / 06:05） |
| `release.yml`（跟随上游正式 Release） | `41 2 * * *` | 每天 1 次（10:41） |
| `opencode-cn-autoheal.yml`（汉化自愈） | `25 3,15 * * *` | 每天 2 次（11:25 / 23:25） |
| `opencode-cn-v2-nightly.yml`（V2 汉化构建） | `23 23 * * *` | 每天 1 次（07:23） |

同一槽位若已有更早一轮跑过（含人工或本机兜底补跑），后到的定时运行会被 workflow 内的 `slot-guard` 自动取消，避免重复构建。

本地修改文件：`packages/web/src/content/i18n/zh-CN.json`（+ 73 处词条）、`install.sh`、`install.ps1`、`install-preview.ps1`、`.github/workflows/*`

## 许可证

MIT — 与官方 OpenCode 保持一致。

汉化翻译文件由 yuloop 社区维护，遵循原项目的 MIT 许可证。
