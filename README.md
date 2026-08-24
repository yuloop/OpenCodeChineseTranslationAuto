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
| 构建自动化 | 无 | 每小时自动同步上游 Release → 构建+发布 |
| 一键安装 | 无 | install.sh / install.ps1 / install-preview.ps1 |
| 预览版（Nightly） | 无 | 跟随上游 dev 分支，4次/天自动构建 |
| 发布平台 | 源码为主 | Linux x64 + Windows x64 便携二进制 |
| 翻译门禁 | 无 | 100% 匹配门禁后才允许发布 |
| upstream 追踪 | — | 每小时检查官方 Release |

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
        ↓ 每小时检查
检出精确 tag 的官方源码
        ↓
注入汉化翻译词条（100% 匹配门禁）
        ↓
构建 Linux x64 + Windows x64 二进制
        ↓
发布到 GitHub Releases
```

本地修改文件：`packages/web/src/content/i18n/zh-CN.json`（+ 73 处词条）、`install.sh`、`install.ps1`、`install-preview.ps1`、`.github/workflows/*`

## 许可证

MIT — 与官方 OpenCode 保持一致。

汉化翻译文件由 yuloop 社区维护，遵循原项目的 MIT 许可证。
