# opencode V2 汉化 · 锚点别名迁移报告

- 生成方式:`python3 tools/v2_anchor_migrate.py --source-dir <v2.0.12 检出>`(只读 V2 源码与 V1 词表,V1 词表零改动)
- 上游对象:`anomalyco/opencode` tag `v2.0.12`(2670273ff17d)
- V1 词表:`cli-go/internal/core/assets/opencode-i18n`(版本 6.2,497 条)
- V2 专用资产:`cli-go/internal/core/assets/opencode-i18n-v2`(由本工具生成,加载器按 layout 自动选择)

## ① 度量:改前 vs 改后(同一命令,同一 V2 源码树)

```bash
OPENCODE_SOURCE_DIR=<v2.0.12 检出> ./opencode-cli apply --dry-run --strict --min-match-rate 1
```

| 口径 | 改前(origin/main) | 改后(本分支) |
|---|---|---|
| 替换匹配 | 154/497 (31.0%) | 246/497 (49.5%) |
| 匹配率 | 31.0% | 49.5% |
| 文件统计 | 26 成功, 21 跳过, 7 失败 | 39 成功, 17 跳过, 6 失败 |
| strict 门禁(100%) | 未通过(要求 100%) | 未通过(要求 100%;V2 阈值策略不在本单范围) |

> 分母不变:V2 资产保留全部 497 条条目(迁移不动的保留旧锚点,继续计未匹配),因此前后匹配率可直接对比;
> V2 门禁阈值策略(阶梯/双轨)不在本单范围,本单只交付锚点迁移与度量。

V1 线回归(同一命令,V1 门禁 `--min-match-rate 1` 不变,源码=上游 dev):

| 口径 | 改前(origin/main 二进制) | 改后(本分支二进制) |
|---|---|---|
| V1 替换匹配 | 497/497 (100.0%), rc=0 | 497/497 (100.0%), rc=0 |

## ② 条目变更统计

| 分类 | 条数 | 占比 | 说明 |
|---|---|---|---|
| kept(锚点不变) | 152 | 30.6% | V1 目标路径在 V2 仍在且条目命中 |
| moved(重新锚定) | 92 | 18.5% | 唯一命中 39 条;聚类/路径消歧 53 条 |
| deferred(待人工确认) | 253 | 50.9% | V2 全树 0 命中 217 条;仅宇宙外命中 17 条;多候选并列 8 条;简单词无同规则共识 3 条;弱证据 1 条;标识符碰撞 7 条 |
| **合计** | **497** | 100% | |

## ③ 逐规则迁移表(旧位置 → 新位置 → 匹配依据)

| 规则(V1) | 条数 | kept | moved | deferred | 迁移去向(新锚点: 条数) |
|---|---|---|---|---|---|
| `app.json` | 1 | 1 | 0 | 0 | - |
| `common/app-messages.json` | 10 | 8 | 0 | 2 | `packages/tui/src/app.tsx(保留旧锚点)` × 2 |
| `common/common-toast.json` | 1 | 1 | 0 | 0 | - |
| `common/error-messages.json` | 5 | 1 | 0 | 4 | `packages/tui/src/app.tsx(保留旧锚点)` × 4 |
| `common/fatal-error.json` | 9 | 7 | 0 | 2 | `packages/tui/src/component/error-component.tsx(保留旧锚点)` × 2 |
| `common/local-context.json` | 6 | 3 | 0 | 3 | `packages/tui/src/context/local.tsx(保留旧锚点)` × 3 |
| `common/share-error.json` | 1 | 0 | 0 | 1 | `packages/tui/src/routes/session/index.tsx(保留旧锚点)` × 1 |
| `common/system-prompt.json` | 1 | 0 | 0 | 1 | `packages/opencode/src/session/system.ts(保留旧锚点)` × 1 |
| `components/autocomplete.json` | 1 | 0 | 0 | 1 | `packages/tui/src/component/prompt/autocomplete.tsx(保留旧锚点)` × 1 |
| `components/command-panel.json` | 39 | 29 | 1 | 9 | `packages/tui/src/app.tsx(保留旧锚点)` × 9; `packages/tui/src/config/v1/keybind.ts` × 1 |
| `components/component-prompt.json` | 12 | 11 | 0 | 1 | `packages/tui/src/component/prompt/index.tsx(保留旧锚点)` × 1 |
| `components/component-question.json` | 6 | 0 | 4 | 2 | `packages/tui/src/mini/footer.form.tsx` × 1; `packages/tui/src/routes/session/form.tsx` × 3; `packages/tui/src/routes/session/question.tsx(保留旧锚点)` × 2 |
| `components/component-sidebar.json` | 0 | 0 | 0 | 0 | - |
| `components/component-tips.json` | 99 | 0 | 0 | 99 | `packages/tui/src/feature-plugins/home/tips-view.tsx(保留旧锚点)` × 99 |
| `components/inline-tools.json` | 14 | 9 | 0 | 5 | `packages/tui/src/routes/session/index.tsx(保留旧锚点)` × 5 |
| `components/sidebar-lsp.json` | 2 | 0 | 0 | 2 | `packages/tui/src/feature-plugins/sidebar/lsp.tsx(保留旧锚点)` × 2 |
| `dialogs/cli-error.json` | 9 | 0 | 8 | 1 | `packages/opencode/src/cli/error.ts(保留旧锚点)` × 1; `packages/tui/src/util/error.ts` × 8 |
| `dialogs/cli-footer-command.json` | 29 | 0 | 24 | 5 | `packages/opencode/src/cli/cmd/run/footer.command.tsx(保留旧锚点)` × 5; `packages/tui/src/component/dialog-skill.tsx` × 1; `packages/tui/src/config/keybind.ts` × 1; `packages/tui/src/mini/footer.command.tsx` × 22 |
| `dialogs/cli-footer-view.json` | 15 | 0 | 8 | 7 | `packages/opencode/src/cli/cmd/run/footer.view.tsx(保留旧锚点)` × 7; `packages/tui/src/component/prompt/index.tsx` × 2; `packages/tui/src/config/keybind.ts` × 1; `packages/tui/src/mini/footer.view.tsx` × 5 |
| `dialogs/cli-permission-ui.json` | 6 | 0 | 5 | 1 | `packages/opencode/src/cli/cmd/run/footer.permission.tsx(保留旧锚点)` × 1; `packages/tui/src/mini/footer.permission.tsx` × 5 |
| `dialogs/cli-permission.json` | 7 | 0 | 6 | 1 | `packages/opencode/src/cli/cmd/run/permission.shared.ts(保留旧锚点)` × 1; `packages/tui/src/util/permission.ts` × 6 |
| `dialogs/cli-prompt.json` | 21 | 0 | 18 | 3 | `packages/opencode/src/cli/cmd/run/footer.prompt.tsx(保留旧锚点)` × 3; `packages/tui/src/mini/footer.prompt.tsx` × 18 |
| `dialogs/cli-question.json` | 6 | 0 | 4 | 2 | `packages/opencode/src/cli/cmd/run/footer.question.tsx(保留旧锚点)` × 2; `packages/tui/src/mini/footer.form.tsx` × 4 |
| `dialogs/cli-splash.json` | 3 | 0 | 3 | 0 | `packages/tui/src/mini/splash.ts` × 3 |
| `dialogs/cli-subagent.json` | 1 | 0 | 1 | 0 | `packages/tui/src/mini/footer.subagent.tsx` × 1 |
| `dialogs/dialog-agent.json` | 2 | 1 | 0 | 1 | `packages/tui/src/component/dialog-agent.tsx(保留旧锚点)` × 1 |
| `dialogs/dialog-alert.json` | 1 | 0 | 0 | 1 | `packages/tui/src/ui/dialog-alert.tsx(保留旧锚点)` × 1 |
| `dialogs/dialog-command.json` | 2 | 2 | 0 | 0 | - |
| `dialogs/dialog-export.json` | 9 | 1 | 0 | 8 | `packages/tui/src/ui/dialog-export-options.tsx(保留旧锚点)` × 8 |
| `dialogs/dialog-fork.json` | 1 | 0 | 1 | 0 | `packages/tui/src/routes/session/dialog-fork.tsx` × 1 |
| `dialogs/dialog-help.json` | 2 | 0 | 0 | 2 | `packages/tui/src/ui/dialog-help.tsx(保留旧锚点)` × 2 |
| `dialogs/dialog-mcp.json` | 7 | 0 | 0 | 7 | `packages/tui/src/component/dialog-mcp.tsx(保留旧锚点)` × 7 |
| `dialogs/dialog-message.json` | 7 | 7 | 0 | 0 | - |
| `dialogs/dialog-model.json` | 8 | 6 | 0 | 2 | `packages/tui/src/component/dialog-model.tsx(保留旧锚点)` × 2 |
| `dialogs/dialog-prompt.json` | 2 | 1 | 0 | 1 | `packages/tui/src/ui/dialog-prompt.tsx(保留旧锚点)` × 1 |
| `dialogs/dialog-provider.json` | 19 | 0 | 3 | 16 | `packages/tui/src/component/dialog-integration.tsx` × 3; `packages/tui/src/component/dialog-provider.tsx(保留旧锚点)` × 16 |
| `dialogs/dialog-rename.json` | 1 | 0 | 0 | 1 | `packages/tui/src/component/dialog-session-rename.tsx(保留旧锚点)` × 1 |
| `dialogs/dialog-select.json` | 2 | 1 | 0 | 1 | `packages/tui/src/ui/dialog-select.tsx(保留旧锚点)` × 1 |
| `dialogs/dialog-session.json` | 5 | 4 | 0 | 1 | `packages/tui/src/component/dialog-session-list.tsx(保留旧锚点)` × 1 |
| `dialogs/dialog-skill.json` | 3 | 1 | 0 | 2 | `packages/tui/src/component/dialog-skill.tsx(保留旧锚点)` × 2 |
| `dialogs/dialog-stash.json` | 8 | 7 | 0 | 1 | `packages/tui/src/component/dialog-stash.tsx(保留旧锚点)` × 1 |
| `dialogs/dialog-status.json` | 9 | 3 | 0 | 6 | `packages/tui/src/component/dialog-status.tsx(保留旧锚点)` × 6 |
| `dialogs/dialog-subagent.json` | 3 | 0 | 0 | 3 | `packages/tui/src/routes/session/dialog-subagent.tsx(保留旧锚点)` × 3 |
| `dialogs/dialog-tag.json` | 1 | 0 | 0 | 1 | `packages/tui/src/component/dialog-tag.tsx(保留旧锚点)` × 1 |
| `dialogs/dialog-theme.json` | 1 | 1 | 0 | 0 | - |
| `dialogs/dialog-timeline.json` | 1 | 1 | 0 | 0 | - |
| `dialogs/dialog-toast.json` | 1 | 0 | 0 | 1 | `packages/tui/src/ui/dialog.tsx(保留旧锚点)` × 1 |
| `routes/route-footer.json` | 2 | 0 | 0 | 2 | `packages/tui/src/routes/session/footer.tsx(保留旧锚点)` × 2 |
| `routes/route-header.json` | 4 | 0 | 0 | 4 | `packages/tui/src/routes/session/subagent-footer.tsx(保留旧锚点)` × 4 |
| `routes/route-home-page.json` | 3 | 3 | 0 | 0 | - |
| `routes/route-home.json` | 2 | 0 | 0 | 2 | `packages/tui/src/feature-plugins/home/tips.tsx(保留旧锚点)` × 2 |
| `routes/route-permission.json` | 24 | 2 | 6 | 16 | `packages/tui/src/routes/session/permission.tsx(保留旧锚点)` × 16; `packages/tui/src/util/permission.ts` × 6 |
| `routes/route-session.json` | 57 | 37 | 0 | 20 | `packages/tui/src/routes/session/index.tsx(保留旧锚点)` × 20 |
| `routes/route-sidebar.json` | 6 | 4 | 0 | 2 | `packages/tui/src/feature-plugins/sidebar/mcp.tsx(保留旧锚点)` × 2 |

## ④ 待人工确认清单(deferred)

不做猜测性改写;以下条目保留旧锚点,在 V2 门禁里继续计为未匹配。归因:

- `no-hit`:V2 全树 0 命中(疑似随功能消失,如首页 tips 99 条)
- `outside-universe`:仅命中 tui/cli 产品源码之外的文件(i18n 语言包/测试/stories/其它包),疑子串巧合
- `ambiguous`:宇宙内多候选,共识/聚类/路径相似度全部并列
- `no-consensus`:简单词(\b 边界)多候选且同规则无共识锚点(子串巧合高发,如 demo 文件/变量名/环境变量)
- `weak-evidence`:无共识、聚类≤2、与 V1 目标路径相似度<5
- `identifier-collision`:简单词在锚点文件中处于标识符/注释位置(替换会伤及代码,如 theme.background、const interrupt;V1 产物已有同类先例,V2 不新引入)

| 规则 | 条目(截断) | 原因 | 宇宙内/外命中(≤3) |
|---|---|---|---|
| `common/app-messages.json` | message: "Failed to fork session" | no-hit | - |
| `common/app-messages.json` | message: `Updating to v${version}…` | no-hit | - |
| `common/error-messages.json` | message: "The current session was deleted" | no-hit | - |
| `common/error-messages.json` | `Update Available` | no-hit | - |
| `common/error-messages.json` | title: "Update Failed" | no-hit | - |
| `common/error-messages.json` | message: "Update failed" | no-hit | - |
| `common/fatal-error.json` | opencode crashed | no-hit | - |
| `common/fatal-error.json` | () => (copied() ? "✓ Copied" : "Copy report") | no-hit | - |
| `common/local-context.json` | message: `Agent not found: ${name}` | no-hit | - |
| `common/local-context.json` | message: `Model ${model.providerID}/${model.modelID} is not  | no-hit | - |
| `common/local-context.json` | message: `Agent ${value.name}'s configured model ${value.mod | no-hit | - |
| `common/share-error.json` | message: "Failed to copy URL to clipboard" | no-hit | - |
| `common/system-prompt.json` | return (yield* (yield* Reference.Service).list()).filter((re | no-hit | - |
| `components/autocomplete.json` | <text fg={theme.textMuted}>No matching items</text> | no-hit | - |
| `components/command-panel.json` | "Connect provider" | outside-universe | `packages/app/src/runtime/i18n/en.ts` |
| `components/command-panel.json` | "Toggle MCPs" | outside-universe | `packages/app/src/runtime/i18n/en.ts` |
| `components/command-panel.json` | "Copy worktree path" | no-hit | - |
| `components/command-panel.json` | "Manage workspaces" | ambiguous | `packages/tui/src/component/prompt/index.tsx`, `packages/tui/src/config/keybind.ts` |
| `components/command-panel.json` | "Switch org" | no-hit | - |
| `components/command-panel.json` | "Disable session directory filtering" | no-hit | - |
| `components/command-panel.json` | "Enable session directory filtering" | no-hit | - |
| `components/command-panel.json` | "Disable auto-approve permissions" | no-hit | - |
| `components/command-panel.json` | "Enable auto-approve permissions" | no-hit | - |
| `components/component-prompt.json` | message: "Connect a provider to send prompts" | no-hit | - |
| `components/component-question.json` | >Confirm</ | no-hit | - |
| `components/component-question.json` | >Review</ | no-hit | - |
| `components/component-tips.json` | ● Tip{" "} | no-hit | - |
| `components/component-tips.json` | Type {highlight}@{/highlight} followed by a filename to fuzz | no-hit | - |
| `components/component-tips.json` | Start a message with {highlight}!{/highlight} to run shell c | no-hit | - |
| `components/component-tips.json` | press(shortcuts.agentCycle(), "to cycle between Build and Pl | no-hit | - |
| `components/component-tips.json` | Use {highlight}/undo{/highlight} to revert the last message  | no-hit | - |
| `components/component-tips.json` | Use {highlight}/redo{/highlight} to restore previously undon | no-hit | - |
| `components/component-tips.json` | Run {highlight}/share{/highlight} to create a public opencod | no-hit | - |
| `components/component-tips.json` | Drag and drop images or PDFs into the terminal as context | no-hit | - |
| `components/component-tips.json` | press(shortcuts.inputPaste(), "to paste images from your cli | no-hit | - |
| `components/component-tips.json` | `Use ${commandText("/editor", shortcuts.editorOpen())} to co | no-hit | - |
| `components/component-tips.json` | Run {highlight}/init{/highlight} to auto-generate project ru | no-hit | - |
| `components/component-tips.json` | `Use ${commandText("/models", shortcuts.modelList())} to swi | no-hit | - |
| `components/component-tips.json` | `Use ${commandText("/new", shortcuts.sessionNew())} to start | no-hit | - |
| `components/component-tips.json` | `Use ${commandText("/sessions", shortcuts.sessionList())} to | no-hit | - |
| `components/component-tips.json` | Run {highlight}/compact{/highlight} to summarize long sessio | no-hit | - |
| `components/component-tips.json` | `Use ${commandText("/export", shortcuts.sessionExport())} to | no-hit | - |
| `components/component-tips.json` | press(shortcuts.messagesCopy(), "to copy the assistant's las | no-hit | - |
| `components/component-tips.json` | press(shortcuts.commandList(), "to see all available actions | no-hit | - |
| `components/component-tips.json` | Run {highlight}/connect{/highlight} to add API keys for 75+  | no-hit | - |
| `components/component-tips.json` | `The leader key is ${shortcutText(shortcuts.leader())}; comb | no-hit | - |
| `components/component-tips.json` | press(shortcuts.modelCycleRecent(), "to quickly switch betwe | no-hit | - |
| `components/component-tips.json` | press(shortcuts.sessionSidebarToggle(), "in a session to sho | no-hit | - |
| `components/component-tips.json` | `Use ${shortcutText(shortcuts.messagesPageUp())}/${shortcutT | no-hit | - |
| `components/component-tips.json` | press(shortcuts.messagesFirst(), "to jump to the beginning o | no-hit | - |
| `components/component-tips.json` | press(shortcuts.messagesLast(), "to jump to the most recent  | no-hit | - |
| `components/component-tips.json` | press(shortcuts.inputNewline(), "to add newlines in your pro | no-hit | - |
| `components/component-tips.json` | press(shortcuts.inputClear(), "when typing to clear the inpu | no-hit | - |
| `components/component-tips.json` | press(shortcuts.sessionInterrupt(), "to stop the AI mid-resp | no-hit | - |
| `components/component-tips.json` | Switch to {highlight}Plan{/highlight} agent for suggestions  | no-hit | - |
| `components/component-tips.json` | Use {highlight}@agent-name{/highlight} in prompts to invoke  | no-hit | - |
| `components/component-tips.json` | for parent/child sessions | no-hit | - |
| `components/component-tips.json` | Create {highlight}opencode.json{/highlight} for server setti | no-hit | - |
| `components/component-tips.json` | Place TUI settings in {highlight}~/.config/opencode/tui.json | no-hit | - |
| `components/component-tips.json` | Add {highlight}$schema{/highlight} to your config for autoco | no-hit | - |
| `components/component-tips.json` | Configure {highlight}model{/highlight} in config to set your | no-hit | - |
| `components/component-tips.json` | Override any keybind in {highlight}tui.json{/highlight} via  | no-hit | - |
| `components/component-tips.json` | Set any keybind to {highlight}none{/highlight} to disable it | no-hit | - |
| `components/component-tips.json` | Configure local or remote MCP servers in the {highlight}mcp{ | no-hit | - |
| `components/component-tips.json` | Add {highlight}.md{/highlight} files to {highlight}.opencode | no-hit | - |
| `components/component-tips.json` | Use {highlight}$ARGUMENTS{/highlight}, {highlight}$1{/highli | no-hit | - |
| `components/component-tips.json` | Use backticks to inject shell output (e.g., {highlight}`git  | no-hit | - |
| `components/component-tips.json` | Add {highlight}.md{/highlight} files to {highlight}.opencode | no-hit | - |
| `components/component-tips.json` | Configure per-agent permissions for {highlight}edit{/highlig | no-hit | - |
| `components/component-tips.json` | Use patterns like {highlight}"git *": "allow"{/highlight} fo | no-hit | - |
| `components/component-tips.json` | Set {highlight}"rm -rf *": "deny"{/highlight} to block destr | no-hit | - |
| `components/component-tips.json` | Configure {highlight}"git push": "ask"{/highlight} to requir | no-hit | - |
| `components/component-tips.json` | Set {highlight}"formatter": true{/highlight} to enable built | no-hit | - |
| `components/component-tips.json` | Set {highlight}"formatter": false{/highlight} to disable inh | no-hit | - |
| `components/component-tips.json` | Define custom formatter commands with file extensions in con | no-hit | - |
| `components/component-tips.json` | Set {highlight}"lsp": true{/highlight} to enable built-in LS | no-hit | - |
| `components/component-tips.json` | Create {highlight}.ts{/highlight} files in {highlight}.openc | no-hit | - |
| `components/component-tips.json` | Tool definitions can invoke scripts written in Python, Go, e | no-hit | - |
| `components/component-tips.json` | Add {highlight}.ts{/highlight} files to {highlight}.opencode | no-hit | - |
| `components/component-tips.json` | Use plugins to send OS notifications when sessions complete | no-hit | - |
| `components/component-tips.json` | Create a plugin to prevent OpenCode from reading sensitive f | no-hit | - |
| `components/component-tips.json` | Use {highlight}opencode run{/highlight} for non-interactive  | no-hit | - |
| `components/component-tips.json` | Use {highlight}opencode --continue{/highlight} to resume the | no-hit | - |
| `components/component-tips.json` | Use {highlight}opencode run -f file.ts{/highlight} to attach | no-hit | - |
| `components/component-tips.json` | Use {highlight}--format json{/highlight} for machine-readabl | no-hit | - |
| `components/component-tips.json` | Run {highlight}opencode serve{/highlight} for headless API a | no-hit | - |
| `components/component-tips.json` | Use {highlight}opencode run --attach{/highlight} to connect  | no-hit | - |
| `components/component-tips.json` | Run {highlight}opencode upgrade{/highlight} to update to the | no-hit | - |
| `components/component-tips.json` | Run {highlight}opencode auth list{/highlight} to see all con | no-hit | - |
| `components/component-tips.json` | Run {highlight}opencode agent create{/highlight} for guided  | no-hit | - |
| `components/component-tips.json` | Use {highlight}/opencode{/highlight} in GitHub issues/PRs to | no-hit | - |
| `components/component-tips.json` | Run {highlight}opencode github install{/highlight} to set up | no-hit | - |
| `components/component-tips.json` | Comment {highlight}/opencode fix this{/highlight} on issues  | no-hit | - |
| `components/component-tips.json` | Comment {highlight}/oc{/highlight} on PR code lines for targ | no-hit | - |
| `components/component-tips.json` | Use {highlight}"theme": "system"{/highlight} to match your t | no-hit | - |
| `components/component-tips.json` | Create JSON theme files in {highlight}.opencode/themes/{/hig | no-hit | - |
| `components/component-tips.json` | Themes support dark/light variants for both modes | no-hit | - |
| `components/component-tips.json` | Use numeric xterm color codes 0-255 in custom theme JSON | no-hit | - |
| `components/component-tips.json` | Use {highlight}{env:VAR_NAME}{/highlight} for environment va | no-hit | - |
| `components/component-tips.json` | Use {highlight}{file:path}{/highlight} to include file conte | no-hit | - |
| `components/component-tips.json` | Use {highlight}instructions{/highlight} in config to load ad | no-hit | - |
| `components/component-tips.json` | Set agent {highlight}temperature{/highlight} from 0.0 (focus | no-hit | - |
| `components/component-tips.json` | Configure {highlight}steps{/highlight} to limit agentic iter | no-hit | - |
| `components/component-tips.json` | Set {highlight}"tools": {"bash": false}{/highlight} to disab | no-hit | - |
| `components/component-tips.json` | Set {highlight}"mcp_*": false{/highlight} to disable all too | no-hit | - |
| `components/component-tips.json` | Override global tool settings per agent configuration | no-hit | - |
| `components/component-tips.json` | Set {highlight}"share": "auto"{/highlight} to automatically  | no-hit | - |
| `components/component-tips.json` | Set {highlight}"share": "disabled"{/highlight} to prevent an | no-hit | - |
| `components/component-tips.json` | Run {highlight}/unshare{/highlight} to remove a session from | no-hit | - |
| `components/component-tips.json` | Permission {highlight}doom_loop{/highlight} prevents infinit | no-hit | - |
| `components/component-tips.json` | Permission {highlight}external_directory{/highlight} protect | no-hit | - |
| `components/component-tips.json` | Run {highlight}opencode debug config{/highlight} to troubles | no-hit | - |
| `components/component-tips.json` | Use {highlight}--print-logs{/highlight} flag to see detailed | no-hit | - |
| `components/component-tips.json` | `Use ${commandText("/timeline", shortcuts.sessionTimeline()) | no-hit | - |
| `components/component-tips.json` | press(shortcuts.messagesToggleConceal(), "to toggle code blo | no-hit | - |
| `components/component-tips.json` | `Use ${commandText("/status", shortcuts.statusView())} to se | no-hit | - |
| `components/component-tips.json` | Enable {highlight}scroll_acceleration{/highlight} in {highli | no-hit | - |
| `components/component-tips.json` | Toggle username display in chat via the command palette | no-hit | - |
| `components/component-tips.json` | Run {highlight}docker run -it --rm ghcr.io/anomalyco/opencod | no-hit | - |
| `components/component-tips.json` | Use {highlight}/connect{/highlight} with OpenCode Zen for cu | no-hit | - |
| `components/component-tips.json` | Commit your project's {highlight}AGENTS.md{/highlight} file  | no-hit | - |
| `components/component-tips.json` | Use {highlight}/review{/highlight} to review uncommitted cha | no-hit | - |
| `components/component-tips.json` | `Use ${commandText("/help", shortcuts.helpShow())} to show t | no-hit | - |
| `components/component-tips.json` | Use {highlight}/rename{/highlight} to rename the current ses | no-hit | - |
| `components/component-tips.json` | press(shortcuts.terminalSuspend(), "to suspend the terminal  | no-hit | - |
| `components/inline-tools.json` | <text fg={theme.textMuted}>{expanded() ? "Click to collapse" | no-hit | - |
| `components/inline-tools.json` | pending="Writing command…" | no-hit | - |
| `components/inline-tools.json` | pending="Preparing edit…" | no-hit | - |
| `components/inline-tools.json` | pending="Preparing patch…" | outside-universe | `packages/tui/test/cli/tui/inline-tool-wrap-snapshot.test.tsx` |
| `components/inline-tools.json` | pending="Updating todos…" | no-hit | - |
| `components/sidebar-lsp.json` | LSPs are disabled | no-hit | - |
| `components/sidebar-lsp.json` | LSPs will activate as files are read | no-hit | - |
| `dialogs/cli-error.json` | Try: \`opencode models\` to list available models | no-hit | - |
| `dialogs/cli-footer-command.json` | Skills loading | no-hit | - |
| `dialogs/cli-footer-command.json` | current | identifier-collision | `packages/cli/src/acp/event.ts`, `packages/cli/src/acp/service.ts`, `packages/cli/src/commands/commands.ts` |
| `dialogs/cli-footer-command.json` | MCP Commands | no-hit | - |
| `dialogs/cli-footer-command.json` | Project Commands | no-hit | - |
| `dialogs/cli-footer-command.json` | Skills | identifier-collision | `packages/tui/src/component/dialog-skill.tsx`, `packages/tui/src/component/prompt/index.tsx` |
| `dialogs/cli-footer-view.json` | EXIT | outside-universe | `packages/core/test/shell-scan/generated.test.ts`, `packages/desktop/src/main/remote/cli.ts` |
| `dialogs/cli-footer-view.json` | SHELL | no-consensus | `packages/cli/src/commands/handlers/uninstall.ts`, `packages/tui/src/prompt/traits.ts` |
| `dialogs/cli-footer-view.json` | BUILD | outside-universe | `packages/tui/test/mini/footer.view.test.tsx` |
| `dialogs/cli-footer-view.json` | interrupt | identifier-collision | `packages/cli/src/acp/event.ts`, `packages/cli/src/acp/service.ts`, `packages/cli/src/run/noninteractive.ts` |
| `dialogs/cli-footer-view.json` | background | identifier-collision | `packages/cli/src/acp/event.ts`, `packages/cli/src/acp/service.ts`, `packages/cli/src/commands/commands.ts` |
| `dialogs/cli-footer-view.json` | subagents | identifier-collision | `packages/cli/src/commands/handlers/stats.ts`, `packages/tui/src/feature-plugins/prompt/footer.tsx`, `packages/tui/src/mini/footer.command.tsx` |
| `dialogs/cli-footer-view.json` | cmd | ambiguous | `packages/cli/src/acp/tool.ts`, `packages/cli/src/commands/handlers/session/list.ts`, `packages/tui/src/context/keymap.tsx` |
| `dialogs/cli-permission-ui.json` | Waiting for permission event... | no-hit | - |
| `dialogs/cli-permission.json` | Allow always | outside-universe | `packages/ui/src/i18n/en.ts` |
| `dialogs/cli-prompt.json` | Run a command... "git status" | no-hit | - |
| `dialogs/cli-prompt.json` | Ask anything... "Fix a TODO in the codebase" | no-hit | - |
| `dialogs/cli-prompt.json` | browse available skills | no-hit | - |
| `dialogs/cli-question.json` | Confirm | no-consensus | `packages/tui/src/component/dialog-update.tsx`, `packages/tui/src/component/prompt/autocomplete.tsx`, `packages/tui/src/routes/session/form.tsx` |
| `dialogs/cli-question.json` | Waiting for question event... | no-hit | - |
| `dialogs/dialog-agent.json` | native | ambiguous | `packages/cli/src/framework/spec.ts`, `packages/tui/src/app.tsx`, `packages/tui/src/component/prompt/index.tsx` |
| `dialogs/dialog-alert.json` | <text fg={theme.selectedListItemText}>ok</text> | no-hit | - |
| `dialogs/dialog-export.json` | placeholder="Enter filename" | no-hit | - |
| `dialogs/dialog-export.json` | Export Options | no-hit | - |
| `dialogs/dialog-export.json` | >Filename:< | no-hit | - |
| `dialogs/dialog-export.json` | Include tool details | no-hit | - |
| `dialogs/dialog-export.json` | Include assistant metadata | no-hit | - |
| `dialogs/dialog-export.json` | Open without saving | no-hit | - |
| `dialogs/dialog-export.json` | to confirm | ambiguous | `packages/tui/src/component/dialog-integration.tsx`, `packages/tui/src/component/dialog-session-list.tsx`, `packages/tui/src/component/dialog-stash.tsx` |
| `dialogs/dialog-export.json` | for options | no-hit | - |
| `dialogs/dialog-help.json` | Press {commandShortcut()} to see all available actions and c | no-hit | - |
| `dialogs/dialog-help.json` | <text fg={theme.selectedListItemText}>ok</text> | no-hit | - |
| `dialogs/dialog-mcp.json` | title="MCPs" | no-hit | - |
| `dialogs/dialog-mcp.json` | >⋯ Loading</span> | no-hit | - |
| `dialogs/dialog-mcp.json` | >✓ Enabled</span> | no-hit | - |
| `dialogs/dialog-mcp.json` | >○ Disabled</span> | no-hit | - |
| `dialogs/dialog-mcp.json` | title: "toggle" | no-hit | - |
| `dialogs/dialog-mcp.json` | console.error("Failed to refresh MCP status: no data returne | no-hit | - |
| `dialogs/dialog-mcp.json` | console.error("Failed to toggle MCP:", error) | no-hit | - |
| `dialogs/dialog-model.json` | category: "Popular providers" | no-hit | - |
| `dialogs/dialog-model.json` | title: connected() ? "Connect provider" : "View all provider | no-hit | - |
| `dialogs/dialog-prompt.json` | <span style={{ fg: theme.textMuted }}>submit</span> | no-hit | - |
| `dialogs/dialog-provider.json` | title="Select auth method" | no-hit | - |
| `dialogs/dialog-provider.json` | <DialogSelect title="Connect a provider" | no-hit | - |
| `dialogs/dialog-provider.json` | ? "Popular" : "Providers" | no-hit | - |
| `dialogs/dialog-provider.json` | label: "API key" | outside-universe | `packages/app/e2e/utils/mock-server.ts`, `packages/app/src/providers/connect/dialog.stories.tsx`, `packages/core/src/plugin/provider/azure.ts` |
| `dialogs/dialog-provider.json` | (Recommended) | outside-universe | `packages/core/src/tool/plugin/question.ts` |
| `dialogs/dialog-provider.json` | (API key) | no-hit | - |
| `dialogs/dialog-provider.json` | (ChatGPT Plus/Pro or API key) | no-hit | - |
| `dialogs/dialog-provider.json` | <text fg={theme.error}>Invalid code</text> | no-hit | - |
| `dialogs/dialog-provider.json` | c <span style={{ fg: theme.textMuted }}>copy</span> | no-hit | - |
| `dialogs/dialog-provider.json` | Low cost subscription for everyone | outside-universe | `packages/app/src/runtime/i18n/en.ts` |
| `dialogs/dialog-provider.json` | OpenCode Zen gives you access to all the best coding models  | no-hit | - |
| `dialogs/dialog-provider.json` | Go to  | weak-evidence | `packages/tui/src/config/keybind.ts`, `packages/tui/src/config/v1/keybind.ts`, `packages/tui/src/feature-plugins/system/diff-viewer.tsx` |
| `dialogs/dialog-provider.json` | to get a key | no-hit | - |
| `dialogs/dialog-provider.json` | Custom provider | outside-universe | `packages/app/src/runtime/i18n/en.ts`, `packages/core/src/v1/config/config.ts` |
| `dialogs/dialog-provider.json` | This only stores a credential. Configure the provider in ope | no-hit | - |
| `dialogs/dialog-provider.json` | <text fg={theme.textMuted}>Waiting for authorization…</text> | no-hit | - |
| `dialogs/dialog-rename.json` | title="Rename Session" | outside-universe | `packages/tui/test/cli/tui/dialog-prompt.test.tsx` |
| `dialogs/dialog-select.json` | <text fg={theme.textMuted}>No results found</text> | no-hit | - |
| `dialogs/dialog-session.json` | `Press ${deleteHint()} again to confirm` | no-hit | - |
| `dialogs/dialog-skill.json` | category: "Skills" | no-hit | - |
| `dialogs/dialog-skill.json` | placeholder="Search skills…" | no-hit | - |
| `dialogs/dialog-stash.json` | `Press ${deleteHint()} again to confirm` | no-hit | - |
| `dialogs/dialog-status.json` | Status | identifier-collision | `packages/tui/src/component/dialog-status.tsx` |
| `dialogs/dialog-status.json` | No MCP Servers | no-hit | - |
| `dialogs/dialog-status.json` | MCP Servers | no-hit | - |
| `dialogs/dialog-status.json` | LSP Servers | no-hit | - |
| `dialogs/dialog-status.json` | No Formatters | no-hit | - |
| `dialogs/dialog-status.json` | Formatters | no-hit | - |
| `dialogs/dialog-subagent.json` | title="Subagent Actions" | no-hit | - |
| `dialogs/dialog-subagent.json` | title: "Open" | outside-universe | `packages/app/src/shell/commands/command.test.ts` |
| `dialogs/dialog-subagent.json` | the subagent's session | no-hit | - |
| `dialogs/dialog-tag.json` | title="Autocomplete" | no-hit | - |
| `dialogs/dialog-toast.json` | message: "Copied to clipboard" | ambiguous | `packages/tui/src/app.tsx`, `packages/tui/src/component/dialog-integration.tsx`, `packages/tui/src/routes/session/index.tsx` |
| `routes/route-footer.json` | Get started | outside-universe | `packages/app/src/runtime/i18n/en.ts`, `packages/console/app/src/i18n/en.ts` |
| `routes/route-footer.json` | Permission | no-consensus | `packages/tui/src/component/session-frame.tsx`, `packages/tui/src/context/permission.tsx`, `packages/tui/src/feature-plugins/system/notifications.ts` |
| `routes/route-header.json` | label: "Subagent" | outside-universe | `packages/tui/src/mini/demo.ts` |
| `routes/route-header.json` | Parent | outside-universe | `packages/app/e2e/regression/session-message-revert.spec.ts`, `packages/app/e2e/regression/session-timeline-hydration.spec.ts`, `packages/app/e2e/regression/subagent-child-navigation.spec.ts` |
| `routes/route-header.json` | Prev | outside-universe | `packages/ui/src/components/text-reveal.stories.tsx`, `packages/ui/src/components/thinking-heading.stories.tsx` |
| `routes/route-header.json` | Next | ambiguous | `packages/tui/src/app.tsx`, `packages/tui/src/component/dialog-config.tsx`, `packages/tui/src/component/dialog-experiments.tsx` |
| `routes/route-home.json` | title: props.hidden ? "Show tips" : "Hide tips" | no-hit | - |
| `routes/route-home.json` | category: "System" | ambiguous | `packages/tui/src/app.tsx`, `packages/tui/src/mini/footer.command.tsx` |
| `routes/route-permission.json` | title="Always allow" | no-hit | - |
| `routes/route-permission.json` | options={{ once: "Allow once", always: "Allow always", rejec | no-hit | - |
| `routes/route-permission.json` | "Unknown" | ambiguous | `packages/tui/src/component/devtools-bar.tsx`, `packages/tui/src/mini/tool.ts` |
| `routes/route-permission.json` | "This will allow " + props.request.permission + " until Open | no-hit | - |
| `routes/route-permission.json` | This will allow the following patterns until OpenCode is res | no-hit | - |
| `routes/route-permission.json` | options={{ confirm: "Confirm", cancel: "Cancel" }} | no-hit | - |
| `routes/route-permission.json` | <text fg={theme.text}>Reject permission</text> | no-hit | - |
| `routes/route-permission.json` | <text fg={theme.textMuted}>Tell OpenCode what to do differen | no-hit | - |
| `routes/route-permission.json` | title: `Read ${pathFormatter.format(filePath)}` | no-hit | - |
| `routes/route-permission.json` | title: `Glob "${pattern}"` | no-hit | - |
| `routes/route-permission.json` | title: `Grep "${pattern}"` | no-hit | - |
| `routes/route-permission.json` | title: `List ${pathFormatter.format(dir)}` | no-hit | - |
| `routes/route-permission.json` | title: `Edit ${pathFormatter.format(filepath)}` | no-hit | - |
| `routes/route-permission.json` | title: `Call tool ${permission}` | no-hit | - |
| `routes/route-permission.json` | title: `${Locale.titlecase(type)} Task` | no-hit | - |
| `routes/route-permission.json` | title: `Access external directory ${dir}` | no-hit | - |
| `routes/route-session.json` | title: sidebarVisible() ? "Hide sidebar" : "Show sidebar" | no-hit | - |
| `routes/route-session.json` | title: conceal() ? "Disable code concealment" : "Enable code | no-hit | - |
| `routes/route-session.json` | title: showTimestamps() ? "Hide timestamps" : "Show timestam | no-hit | - |
| `routes/route-session.json` | title: showDetails() ? "Hide tool details" : "Show tool deta | no-hit | - |
| `routes/route-session.json` | title: "Next child session" | no-hit | - |
| `routes/route-session.json` | title: "Previous child session" | no-hit | - |
| `routes/route-session.json` | message: "Connect a provider to summarize this session" | no-hit | - |
| `routes/route-session.json` | message: "Share URL copied to clipboard!" | no-hit | - |
| `routes/route-session.json` | "Failed to share session" | no-hit | - |
| `routes/route-session.json` | message: "Session unshared successfully" | no-hit | - |
| `routes/route-session.json` | "Failed to unshare session" | outside-universe | `packages/app/src/runtime/i18n/en.ts` |
| `routes/route-session.json` | message: `Session exported to ${filename}` | no-hit | - |
| `routes/route-session.json` | "Confirm Redo" | no-hit | - |
| `routes/route-session.json` | "Are you sure you want to restore the reverted messages?" | no-hit | - |
| `routes/route-session.json` | interrupted | identifier-collision | `packages/tui/src/routes/session/index.tsx` |
| `routes/route-session.json` | title=" Compaction " | no-hit | - |
| `routes/route-session.json` | title="# Todos" | no-hit | - |
| `routes/route-session.json` | message: "Failed to copy URL to clipboard" | no-hit | - |
| `routes/route-session.json` | {revert()!.reverted.length} message reverted | no-hit | - |
| `routes/route-session.json` | Skill "{stringValue(props.input.name)}" | no-hit | - |
| `routes/route-sidebar.json` | >Needs auth</Match> | no-hit | - |
| `routes/route-sidebar.json` | Needs client ID | no-hit | - |

## ⑤ 复现与审计

```bash
# 1) 重新生成 V2 资产与本报告(确定性输出,键序排序)
python3 tools/v2_anchor_migrate.py --source-dir <v2.0.12 检出> \
    --out-dir cli-go/internal/core/assets/opencode-i18n-v2 \
    --report docs/opencode-v2-anchor-migration.md

# 2) 逐条复验:apply --dry-run 对每一条 moved 条目做机械匹配复验
OPENCODE_SOURCE_DIR=<v2.0.12 检出> ./opencode-cli apply --dry-run

# 3) 逐条证据:V2 资产 config.json 的 manifest 字段(rule/key/from/to/basis)
python3 -c "import json;m=json.load(open('cli-go/internal/core/assets/opencode-i18n-v2/config.json'))['manifest'];print(len(m['entries']))"
```

V1 线未受影响:V1 词表/注入脚本/门禁阈值/工作流零改动;V1 门禁在同一 V2 工具改动后仍为 100%(见 ① 与 PR 描述)。
