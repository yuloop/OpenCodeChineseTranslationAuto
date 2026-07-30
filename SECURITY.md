# Security

## 报告问题

请不要在公开 Issue 中提交访问令牌、Cookie、账号配置、模型密钥或包含私有代码的日志。安全问题可通过 GitHub Security Advisory 的私密报告功能提交；普通缺陷请使用 Issues。

## 发布完整性

- 自动发布只从 `anomalyco/opencode` 的精确 Release tag 构建。
- 翻译规则必须全部匹配才允许发布。
- 发布附件同时生成 `SHA256SUMS`；安装脚本在替换现有管理工具前进行校验，并保留一个 `.old` 备份。
- 工作流使用 GitHub 提供的短期令牌，不需要仓库长期保存个人访问令牌。

使用任何远程安装脚本前，仍建议先阅读脚本内容。
