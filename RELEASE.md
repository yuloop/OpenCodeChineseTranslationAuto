# 发布说明

发布由 [OpenCode Chinese Release](.github/workflows/release.yml) 工作流管理。

## 自动发布

- 每小时第 17 分钟检查 OpenCode 官方最新 Release。
- 若本仓库已存在相同 tag 的 Release，则定时任务直接结束。
- 若尚未发布，则检出官方精确 tag，运行测试和翻译门禁，分别构建 Windows x64、Linux x64。
- 只有已维护翻译规则 100% 命中且所有构建成功时，才会创建 Release。
- Release 附带 `SHA256SUMS`。

## 手动发布

在 GitHub Actions 中选择 `OpenCode Chinese Release` → `Run workflow`：

- `upstream_tag`：要构建的官方 tag；留空表示最新正式版。
- `release_tag`：本仓库使用的 tag；通常留空，与官方 tag 相同。

手动执行相同 tag 会覆盖该 Release 的附件，适合修复构建流程后重新发布。不要把未经验证的分支名填入 tag 参数。

## 产物

| 文件 | 说明 |
|---|---|
| `opencode-cli-windows-amd64.exe` | Windows x64 管理工具 |
| `opencode-cli-linux-amd64` | Linux / WSL x64 管理工具 |
| `opencode-zh-CN-<tag>-windows-x64.zip` | Windows x64 汉化版 OpenCode |
| `opencode-zh-CN-<tag>-linux-x64.zip` | Linux / WSL x64 汉化版 OpenCode |
| `opencode-i18n-tool-<tag>.zip` | 管理工具源码和翻译资源 |
| `SHA256SUMS` | 所有附件的 SHA-256 摘要 |

## 上游文本变化

如果 `Require complete translation match` 失败，不应绕过门禁。请在对应官方 tag 上定位变更，更新 `cli-go/internal/core/assets/opencode-i18n` 中的查找文本和译文，然后本地执行：

```bash
opencode-cli apply --dry-run --strict --min-match-rate 1
opencode-cli verify --dry-run
```

确认通过后再重新运行发布工作流。
