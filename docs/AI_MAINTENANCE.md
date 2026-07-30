# OpenCode 汉化项目 - AI 维护指南

> 本文档为 AI 助手（如 Claude Code、Cursor 等）提供维护此汉化项目的完整指南。

[![Version](https://img.shields.io/badge/i18n-v7.0-green.svg)](../opencode-i18n/config.json)
[![Coverage](https://img.shields.io/badge/汉化覆盖率-100%25-brightgreen.svg)]()

---

## 📋 项目概述

| 项目 | 说明 |
|------|------|
| **项目名称** | OpenCode 中文汉化版 |
| **原项目** | https://github.com/opencode-ai/opencode |
| **汉化仓库** | https://github.com/yuloop/OpenCodeChineseTranslationAuto |
| **管理工具** | `opencode-cli` (Go 二进制) |
| **当前版本** | v8.6+ |

---

## 📂 目录结构

```
OpenCodeChineseTranslation/
├── cli-go/                      # Go CLI 管理工具 ⭐
│   └── internal/core/assets/opencode-i18n/  # 汉化配置(内嵌) ⭐
│       ├── config.json          # 主配置文件
│       ├── dialogs/             # 对话框翻译配置 (21个)
│       ├── routes/              # 路由翻译配置 (6个)
│       ├── components/          # 组件翻译配置 (6个)
│       ├── common/              # 通用翻译配置 (10个)
│       └── app.json             # 应用根配置
├── scripts/                     # 辅助脚本
│   └── patch-build-ts.py        # CI 中移除 win32-arm64 目标
├── install.ps1                  # Windows 安装脚本
├── install.sh                   # Linux/macOS 安装脚本
├── build.ps1 / build.sh         # 本地编译脚本
├── .github/workflows/
│   └── release.yml              # 统一 CI/CD ⭐
└── docs/                        # 文档
    ├── AI_MAINTENANCE.md        # 本文档
    ├── ANTIGRAVITY_INTEGRATION.md  # Antigravity 集成指南
    └── SCREENSHOTS.md           # 功能截图
```

---

## 🚀 快速开始

### 1. 安装管理工具

```powershell
# Windows
powershell -c "irm https://raw.githubusercontent.com/yuloop/OpenCodeChineseTranslationAuto/main/install.ps1 | iex"
```

```bash
# Linux/macOS
curl -fsSL https://raw.githubusercontent.com/yuloop/OpenCodeChineseTranslationAuto/main/install.sh | bash
```

### 2. 使用方法

```bash
# 启动交互式菜单
opencode-cli
```

**环境要求（仅编译需要）：**

| 工具 | 版本要求 | 说明 |
|------|----------|------|
| Go | >= 1.21 | CLI 工具编译 |
| Bun | >= 1.3.8 | OpenCode 构建（需与上游版本匹配） |
| Git | latest | 版本控制 |

### 3. 完整工作流

```bash
# 交互式菜单（推荐）
opencode-cli

# 或直接执行
opencode-cli download   # 下载预编译版
opencode-cli update     # 更新源码
opencode-cli apply      # 应用汉化
opencode-cli verify     # 验证
opencode-cli build      # 编译
opencode-cli deploy     # 部署
```

---

## 🛠️ opencodenpm 命令参考

| 命令 | 说明 |
|------|------|
| `opencode-cli` | 启动交互式管理菜单 |
| `opencode-cli download` | 下载预编译汉化版 |
| `opencode-cli update` | 更新 OpenCode 源码 |
| `opencode-cli apply` | 应用汉化配置 |
| `opencode-cli verify` | 验证汉化覆盖率 |
| `opencode-cli build` | 编译构建 OpenCode |
| `opencode-cli deploy` | 部署到系统 PATH |
| `opencode-cli diagnose` | 诊断修复版本冲突、环境问题 |
| `opencode-cli uninstall` | 卸载清理 |
| `opencode-cli antigravity` | 配置本地 AI 代理 |

### 常用命令示例

```bash
# 下载预编译版（无需编译环境）
opencode-cli download

# 源码方式
opencode-cli update               # 更新到指定版本
opencode-cli apply                # 应用汉化
opencode-cli verify --detailed    # 详细验证

# 编译部署
opencode-cli build                # 编译当前平台
opencode-cli deploy               # 部署全局命令
```

---

## 🔧 汉化配置详解

### 配置文件结构

主配置文件 `cli-go/internal/core/assets/opencode-i18n/config.json`:

```json
{
  "version": "6.0",
  "description": "OpenCode 中文汉化配置文件（模块化结构）",
  "lastUpdate": "2026-01-16",
  "testPassRate": "100%",
  "supportedCommit": "99a1e73fa1bd5c92c02abd8a20b0e274d5b0d214",
  "maintainer": {
    "name": "CodeCreator",
    "github": "https://github.com/yuloop/OpenCodeChineseTranslationAuto"
  },
  "modules": {
    "dialogs": ["dialogs/dialog-agent.json", ...],
    "routes": ["routes/route-footer.json", ...],
    "components": ["components/autocomplete.json", ...],
    "common": ["common/app-messages.json", ...],
    "root": ["app.json"]
  }
}
```

### 翻译配置文件格式

每个翻译配置文件格式如下：

```json
{
  "file": "src/cli/cmd/tui/dialogs/xxx.tsx",
  "description": "文件描述",
  "note": "翻译注意事项",
  "replacements": {
    "Original Text": "翻译文本",
    "Another Text": "另一个翻译"
  }
}
```

### 模块分类

| 模块 | 目录 | 文件数 | 说明 |
|------|------|--------|------|
| **dialogs** | `dialogs/` | 21 | 对话框组件翻译 |
| **routes** | `routes/` | 6 | 路由页面翻译 |
| **components** | `components/` | 6 | UI 组件翻译 |
| **common** | `common/` | 10 | 通用文本翻译 |
| **root** | `/` | 1 | 应用根配置 |

---

## 📝 翻译规范

### 命名规范

| 类型 | 文件名格式 | 示例 |
|------|------------|------|
| 对话框 | `dialog-{name}.json` | `dialog-status.json` |
| 路由 | `route-{name}.json` | `route-sidebar.json` |
| 组件 | `component-{name}.json` | `component-question.json` |
| 通用 | `{category}-{name}.json` | `app-messages.json` |

### 翻译原则

1. **只翻译用户可见文本**
   - ✅ UI 文本、按钮、提示信息
   - ❌ 函数名、变量名、类型名
   - ❌ 日志输出（除非面向用户）

2. **保持技术术语一致性**

   | 英文 | 中文 |
   |------|------|
   | MCP Server | MCP 服务器 |
   | LSP Server | LSP 服务器 |
   | Plugin | 插件 |
   | Formatter | 格式化器 |
   | Session | 会话 |
   | Agent | 智能体 |
   | Provider | 提供商 |
   | Model | 模型 |
   | Context | 上下文 |
   | Prompt | 提示词 |

3. **匹配完整上下文**
   - 包含必要的 HTML/JSX 标签
   - 示例: `</text>` 而非单独的 `text`

---

## 🔄 更新流程

### 场景一：OpenCode 发布了新版本

```bash
# 1. 下载预编译版（或更新源码后自己编译）
opencode-cli download

# 2. 验证汉化
opencode-cli verify

# 3. 或用 Go CLI 本地构建
opencode-cli update
opencode-cli apply
opencode-cli verify --detailed
opencode-cli build
```

### 场景二：新增/修改翻译配置

1. **编辑配置文件**
   ```bash
   # 位置: cli-go/internal/core/assets/opencode-i18n/ 下对应目录
   # 格式: JSON，无注释，UTF-8 编码
   ```

2. **测试配置**
   ```bash
   opencode-cli apply
   opencode-cli verify --detailed
   ```

3. **更新版本号**
   ```bash
   # 编辑 cli-go/internal/core/version.go
   # 更新 VERSION 常量
   ```

4. **重新编译 CLI**
   ```bash
   cd cli-go && go build -o opencode-cli.exe .
   ```

5. **提交更改**
   ```bash
   git add cli-go/
   git commit -m "feat(i18n): 更新汉化配置到 vX.X"
   git push
   ```

---

## 🐛 常见问题排查

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| `[原文不存在]` | 源文件已更新，模式不匹配 | 检查源文件，更新翻译配置 |
| `验证失败` | 配置模式与源文件不符 | `opencode-cli verify --detailed` 查看详情 |
| `路径错误` | 源码路径配置错误 | 检查配置文件中的 `file` 字段 |
| `编译失败` | 环境问题 | `opencode-cli diagnose` 检查环境 |
| `汉化未生效` | 未应用汉化 | `opencode-cli apply` 重新应用 |

---

## 🤖 自动化构建 (CI/CD)

本项目使用 GitHub Actions 实现自动化构建和发布。

### 工作流概览

| 工作流 | 文件 | 触发条件 | 说明 |
|--------|------|----------|------|
| **Release** | `release.yml` | Schedule / Tag 推送 / Workflow Dispatch | 检测上游新 release 并自动构建 |

### Release Build (自动跟进构建)

Release Build 会**每 30 分钟**自动检测上游 `anomalyco/opencode` 的最新 release tag，发现新版本时自动触发构建。

**工作原理：**

1. **检测上游 release**（schedule 触发）
   - 通过 GitHub API 获取 `anomalyco/opencode` 的最新 release tag
   - 与本地记录的上次构建 tag 对比
   - 新 tag 则继续构建，否则跳过

2. **构建流程**
   - 编译 Go CLI 工具（3 平台: windows-amd64, darwin-arm64, linux-amd64）
   - 克隆上游指定 tag 的源码
   - 用 `scripts/patch-build-ts.py` 移除不支持的 win32-arm64 目标
   - 编译 OpenCode（5 平台: 不含 win32-arm64）
   - 生成包含上游更新日志的 Release Notes
   - 打包并发布到对应 tag

3. **触发方式**

```bash
# 检测上游最新 release 并自动构建
# （schedule 每 30 分钟自动执行）

# 手动触发指定上游版本
gh workflow run release.yml -f upstream_tag=v1.18.2

# 手动触发并指定自定义发布 tag
gh workflow run release.yml -f upstream_tag=v1.18.2 -f release_tag=v1.18.2
```

**Release Notes 内容：**
- 构建信息（上游版本、构建时间）
- 下载链接表格（5 平台）
- **OpenCode 官方 Release Notes**（自动抓取上游 release body）
- 使用说明

**兼容性说明：**
- Bun 1.3.8 不支持 `win32-arm64` 交叉编译，已从 `allTargets` 移除
- OpenCode CLI 工具仅构建 `win32-amd64`、`darwin-arm64`、`linux-amd64` 三平台

---

## 📦 发布流程

### 1. 更新版本信息

编辑 `cli-go/internal/core/version.go`:

```go
const VERSION = "8.7.0"
```

### 2. 完整测试

```bash
# 验证汉化
opencode-cli verify --detailed

# 本地编译测试
opencode-cli update
opencode-cli apply
opencode-cli build
opencode-cli deploy
```

### 3. 提交发布

```bash
git add .
git commit -m "release(cli): v8.7.0 - 更新说明"
git tag v8.7.0
git push && git push --tags
```

> CI 检测到 `v*` tag 推送后会自动触发构建并发布 Release。

---

## 🔗 相关资源

| 链接 | 说明 |
|------|------|
| [OpenCode 官方](https://github.com/opencode-ai/opencode) | 原项目仓库 |
| [汉化项目 GitHub](https://github.com/yuloop/OpenCodeChineseTranslationAuto) | 本项目 |
| [Antigravity 集成](./ANTIGRAVITY_INTEGRATION.md) | 本地 AI 网关配置 |
| [问题反馈](https://github.com/yuloop/OpenCodeChineseTranslationAuto/issues) | 提交 Issue |

---

## 📊 汉化覆盖统计

| 模块 | 文件数 | 覆盖内容 | 状态 |
|------|--------|----------|------|
| dialogs | 21 | 所有对话框组件 | ✅ 100% |
| routes | 6 | 页面路由文本 | ✅ 100% |
| components | 6 | UI 组件文本 | ✅ 100% |
| common | 10 | 通用提示信息 | ✅ 100% |
| **总计** | **44** | **全部模块** | ✅ **100%** |

---

> **最后更新**: 2026-01-18
> **维护者**: CodeCreator
> **汉化版本**: v7.0
