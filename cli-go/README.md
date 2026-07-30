# opencode-cli

`opencode-cli` 是 OpenCode CLI / TUI 汉化版的终端管理工具。它可以取得官方源码、应用内嵌翻译、验证规则、编译，也可以直接下载本仓库发布的预编译汉化版。

## 常用命令

```text
opencode-cli download
opencode-cli update
opencode-cli apply
opencode-cli verify
opencode-cli build
opencode-cli deploy
```

CI 中使用严格门禁：

```bash
opencode-cli apply --dry-run --strict --min-match-rate 1
opencode-cli verify --dry-run
```

## 开发

```bash
go test ./...
go vet ./...
go build -o ../dist/opencode-cli .
```

默认从 `yuloop/OpenCodeChineseTranslationAuto` 下载 Release。派生仓库可通过环境变量覆盖：

```bash
export OPENCODE_I18N_REPO=owner/repository
```

Windows PowerShell 使用 `$env:OPENCODE_I18N_REPO = "owner/repository"`。
