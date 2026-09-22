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
| 替换匹配 | 246/497 | 252/501 |
| 匹配率 | 49.5% | 50.3% |
| 文件统计 | 39 成功, 17 跳过, 6 失败 | 40 成功, 18 跳过, 5 失败 |
| strict 门禁(100%) | rc=1(49.5% < 100%) | rc=1(50.3% < 100%) |

> 条目不丢:V2 资产保留全部 497 条 V1 条目(迁移不动的保留旧锚点或隔离锚点,继续计未匹配);
> 但同一 UI 串在 V2 多处等价位置出现时会逐处锚定(见 ④-b re-anchored 行),
> 门禁分母因此可能略高于 497——上表「替换匹配」列已同时给出分子/分母,可自行折算;
> 按 V1 条目去重计的匹配条目数见 PR 描述。
> V2 门禁阈值策略(阶梯/双轨)不在本单范围,本单只交付锚点迁移与度量。

V1 线回归(同一命令,V1 门禁 `--min-match-rate 1` 不变,源码=上游 dev):

| 口径 | 改前(origin/main 二进制) | 改后(本分支二进制) |
|---|---|---|
| V1 替换匹配 | 497/497 (100.0%) rc=0 | 497/497 (100.0%) rc=0 |

## ② 条目变更统计

| 分类 | 条数 | 占比 | 说明 |
|---|---|---|---|
| kept(锚点不变) | 153 | 30.8% | V1 目标路径在 V2 仍在且条目命中 |
| moved(重新锚定) | 95 | 19.1% | 唯一命中 39 条;聚类/路径消歧 56 条;人工复核逐条定位 3 条 |
| deferred(待人工确认) | 248 | 49.9% | V2 全树 0 命中 217 条;仅宇宙外命中 17 条;多候选并列 5 条;简单词无同规则共识 3 条;弱证据 1 条;标识符碰撞 5 条 |
| suppressed(判定不得应用) | 1 | 0.2% | 替换会伤及代码;锚点隔离到 V2 不存在的路径,继续计未匹配(该 V1 条目仍在分母里) |
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
| `components/command-panel.json` | 39 | 29 | 2 | 8 | `packages/tui/src/app.tsx(保留旧锚点)` × 8; `packages/tui/src/component/prompt/index.tsx` × 1; `packages/tui/src/config/v1/keybind.ts` × 1 |
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
| `dialogs/dialog-status.json` | 9 | 4 | 0 | 5 | `packages/tui/src/component/dialog-status.tsx(保留旧锚点)` × 5 |
| `dialogs/dialog-subagent.json` | 3 | 0 | 0 | 3 | `packages/tui/src/routes/session/dialog-subagent.tsx(保留旧锚点)` × 3 |
| `dialogs/dialog-tag.json` | 1 | 0 | 0 | 1 | `packages/tui/src/component/dialog-tag.tsx(保留旧锚点)` × 1 |
| `dialogs/dialog-theme.json` | 1 | 1 | 0 | 0 | - |
| `dialogs/dialog-timeline.json` | 1 | 1 | 0 | 0 | - |
| `dialogs/dialog-toast.json` | 1 | 0 | 1 | 0 | `packages/tui/src/component/dialog-integration.tsx` × 1 |
| `routes/route-footer.json` | 2 | 0 | 0 | 2 | `packages/tui/src/routes/session/footer.tsx(保留旧锚点)` × 2 |
| `routes/route-header.json` | 4 | 0 | 0 | 4 | `packages/tui/src/routes/session/subagent-footer.tsx(保留旧锚点)` × 4 |
| `routes/route-home-page.json` | 3 | 3 | 0 | 0 | - |
| `routes/route-home.json` | 2 | 0 | 1 | 1 | `packages/tui/src/app.tsx` × 1; `packages/tui/src/feature-plugins/home/tips.tsx(保留旧锚点)` × 1 |
| `routes/route-permission.json` | 24 | 2 | 6 | 16 | `packages/tui/src/routes/session/permission.tsx(保留旧锚点)` × 16; `packages/tui/src/util/permission.ts` × 6 |
| `routes/route-session.json` | 57 | 37 | 0 | 19 | `packages/tui/src/routes/session/index.tsx(保留旧锚点)` × 19 |
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
| `dialogs/dialog-status.json` | No MCP Servers | no-hit | - |
| `dialogs/dialog-status.json` | MCP Servers | no-hit | - |
| `dialogs/dialog-status.json` | LSP Servers | no-hit | - |
| `dialogs/dialog-status.json` | No Formatters | no-hit | - |
| `dialogs/dialog-status.json` | Formatters | no-hit | - |
| `dialogs/dialog-subagent.json` | title="Subagent Actions" | no-hit | - |
| `dialogs/dialog-subagent.json` | title: "Open" | outside-universe | `packages/app/src/shell/commands/command.test.ts` |
| `dialogs/dialog-subagent.json` | the subagent's session | no-hit | - |
| `dialogs/dialog-tag.json` | title="Autocomplete" | no-hit | - |
| `routes/route-footer.json` | Get started | outside-universe | `packages/app/src/runtime/i18n/en.ts`, `packages/console/app/src/i18n/en.ts` |
| `routes/route-footer.json` | Permission | no-consensus | `packages/tui/src/component/session-frame.tsx`, `packages/tui/src/context/permission.tsx`, `packages/tui/src/feature-plugins/system/notifications.ts` |
| `routes/route-header.json` | label: "Subagent" | outside-universe | `packages/tui/src/mini/demo.ts` |
| `routes/route-header.json` | Parent | outside-universe | `packages/app/e2e/regression/session-message-revert.spec.ts`, `packages/app/e2e/regression/session-timeline-hydration.spec.ts`, `packages/app/e2e/regression/subagent-child-navigation.spec.ts` |
| `routes/route-header.json` | Prev | outside-universe | `packages/ui/src/components/text-reveal.stories.tsx`, `packages/ui/src/components/thinking-heading.stories.tsx` |
| `routes/route-header.json` | Next | ambiguous | `packages/tui/src/app.tsx`, `packages/tui/src/component/dialog-config.tsx`, `packages/tui/src/component/dialog-experiments.tsx` |
| `routes/route-home.json` | title: props.hidden ? "Show tips" : "Hide tips" | no-hit | - |
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
| `routes/route-session.json` | title=" Compaction " | no-hit | - |
| `routes/route-session.json` | title="# Todos" | no-hit | - |
| `routes/route-session.json` | message: "Failed to copy URL to clipboard" | no-hit | - |
| `routes/route-session.json` | {revert()!.reverted.length} message reverted | no-hit | - |
| `routes/route-session.json` | Skill "{stringValue(props.input.name)}" | no-hit | - |
| `routes/route-sidebar.json` | >Needs auth</Match> | no-hit | - |
| `routes/route-sidebar.json` | Needs client ID | no-hit | - |

### ④-b 第二轮人工逐条复核结论(36 条:17 宇宙外 + 12 并列/无共识/弱证据 + 7 标识符碰撞)

逐条在 V2 源码定位后的处置。只对「找到确切位置且角色/语义等价」的条目补锚点;
其余保留旧锚点并在此列明所见事实,不做猜测性改写。

| 规则 | 条目 | 结论 | 锚点/命中 | 依据 |
|---|---|---|---|---|
| `components/command-panel.json` | "Connect provider" | pending(待人工确认) | 原锚点 `packages/tui/src/app.tsx`;宇宙内/外命中:`packages/app/src/runtime/i18n/en.ts` | V2 app.tsx:934 同一命令 id `provider.connect` 的标题已改名为 "Connect an integration"（keybind.ts:168 为 "Connect integration"）；V1 原文在 V2 tui/cli 产品源码 0 命中，唯一命中在 packages/app/src/runtime/i18n/en.ts:89（桌面端英文词典，另一产品面）。 |
| `components/command-panel.json` | "Toggle MCPs" | pending(待人工确认) | 原锚点 `packages/tui/src/app.tsx`;宇宙内/外命中:`packages/app/src/runtime/i18n/en.ts` | V2 app.tsx:882 同一命令 id `mcp.list` 标题改为 "MCP servers"，keybind.ts:167 为 "List MCP servers"；产品源码 0 命中，唯一命中 packages/app/src/runtime/i18n/en.ts:132。 |
| `components/command-panel.json` | "Manage workspaces" | re-anchored(已补锚点) | `packages/tui/src/component/prompt/index.tsx`; `packages/tui/src/config/keybind.ts` | V1 锚点 app.tsx 是命令面板定义处；V2 该命令仍存在且同名同 id：prompt/index.tsx:618 title/619 desc（palette:true, name=session.move），keybind.ts:108 是同一命令 id 的键位标签。两处均为用户可见字符串。 |
| `components/inline-tools.json` | pending="Preparing patch…" | pending(待人工确认) | 原锚点 `packages/tui/src/routes/session/index.tsx`;宇宙内/外命中:`packages/tui/test/cli/tui/inline-tool-wrap-snapshot.test.tsx` | V2 routes/session/index.tsx:3072 仅余 "Preparing write…"、3379 "# Preparing edit…"，补丁工具的 pending 文案已不在该文件；唯一命中是测试快照 packages/tui/test/cli/tui/inline-tool-wrap-snapshot.test.tsx:77（断言旧行为）。 |
| `dialogs/cli-footer-command.json` | current | pending(待人工确认) | 原锚点 `packages/opencode/src/cli/cmd/run/footer.command.tsx`;宇宙内/外命中:`packages/cli/src/acp/event.ts`, `packages/cli/src/acp/service.ts`, `packages/cli/src/commands/commands.ts` | V2 宇宙内 105 个文件命中，但全是更长标签内的词（"Close current session tab"/"Share current session"…）或注释；V1 侧 footer.command.tsx 本身就把 current 同时用作接口字段 `current: boolean`（第 30/35/44 行），V2 不新引入该类破损。 |
| `dialogs/cli-footer-command.json` | Skills | pending(待人工确认) | 原锚点 `packages/opencode/src/cli/cmd/run/footer.command.tsx`;宇宙内/外命中:`packages/tui/src/component/dialog-skill.tsx`, `packages/tui/src/component/prompt/index.tsx` | V2 两处 UI 面均已被更精确的键覆盖：prompt/index.tsx:580 `title: "Skills"` 由 components/component-prompt.json 译，dialog-skill.tsx:58 `title="Skills"` 由 dialogs/dialog-skill.json 译；裸 \bSkills\b 还会命中 dialog-skill.tsx:76 "Close and reopen Skills to try again."，替换后成 "Close and reopen 技能 to try again."（中英混杂）。 |
| `dialogs/cli-footer-view.json` | EXIT | pending(待人工确认) | 原锚点 `packages/opencode/src/cli/cmd/run/footer.view.tsx`;宇宙内/外命中:`packages/core/test/shell-scan/generated.test.ts`, `packages/desktop/src/main/remote/cli.ts` | V1 footer.view.tsx:388 `if (exiting()) return "EXIT"`；V2 mini/footer.view.tsx 已无 EXIT 徽标（改用 "Shell"/"normal"/"Running"）。唯一命中是 bash trap 串 packages/desktop/src/main/remote/cli.ts:90 与 shell 扫描测试 generated.test.ts:90。 |
| `dialogs/cli-footer-view.json` | SHELL | pending(待人工确认) | 原锚点 `packages/opencode/src/cli/cmd/run/footer.view.tsx`;宇宙内/外命中:`packages/cli/src/commands/handlers/uninstall.ts`, `packages/tui/src/prompt/traits.ts` | V2 mini/footer.view.tsx:412/417 用 title case 的 "Shell"，\bSHELL\b 不再命中；宇宙内两处命中分别是 uninstall.ts:151 `process.env.SHELL`（环境变量，替换即破坏）与 prompt/traits.ts:25 的 @opentui/core EditorTraits 协议值。 |
| `dialogs/cli-footer-view.json` | BUILD | pending(待人工确认) | 原锚点 `packages/opencode/src/cli/cmd/run/footer.view.tsx`;宇宙内/外命中:`packages/tui/test/mini/footer.view.test.tsx` | V1 footer.view.tsx:391 `shell() ? "SHELL" : "BUILD"`；V2 已无 BUILD 徽标，唯一命中是 packages/tui/test/mini/footer.view.test.tsx:517 的 `expect(frame).not.toContain("BUILD")`（负向断言）。 |
| `dialogs/cli-footer-view.json` | interrupt | pending(待人工确认) | 原锚点 `packages/opencode/src/cli/cmd/run/footer.view.tsx`;宇宙内/外命中:`packages/cli/src/acp/event.ts`, `packages/cli/src/acp/service.ts`, `packages/cli/src/run/noninteractive.ts` | V2 每个候选文件里 interrupt 都同时是代码标识符：mini/footer.view.tsx:203 `const interrupt = ...`、209 `props.state().interrupt`、1018 `interrupt={...}`；footer.prompt.tsx:1193 是命令 id "session.interrupt"（替换会断开键位绑定）。 |
| `dialogs/cli-footer-view.json` | background | pending(待人工确认) | 原锚点 `packages/opencode/src/cli/cmd/run/footer.view.tsx`;宇宙内/外命中:`packages/cli/src/acp/event.ts`, `packages/cli/src/acp/service.ts`, `packages/cli/src/commands/commands.ts` | V2 background 在候选文件中大量是属性/标识符：footer.view.tsx:699/723/753/963 `backgroundColor=`、762 `runTheme().background`、187 `!item.background`；dialog-update.tsx:148 `backgroundColor=`；footer.width.ts:17/32/72 是联合类型字面量。 |
| `dialogs/cli-footer-view.json` | subagents | pending(待人工确认) | 原锚点 `packages/opencode/src/cli/cmd/run/footer.view.tsx`;宇宙内/外命中:`packages/cli/src/commands/handlers/stats.ts`, `packages/tui/src/feature-plugins/prompt/footer.tsx`, `packages/tui/src/mini/footer.command.tsx` | V2 footer 已无 "subagents" 标签；宇宙内命中是 import 路径 composer/index.tsx:7 `./subagents-tab`、composer tab id index.tsx:1174/1359 `tab: "subagents"`、prop `subagents={tabs}`（index.tsx:809）以及 footer.width.ts 的联合类型字面量。 |
| `dialogs/cli-footer-view.json` | cmd | pending(待人工确认) | 原锚点 `packages/opencode/src/cli/cmd/run/footer.view.tsx`;宇宙内/外命中:`packages/cli/src/acp/tool.ts`, `packages/cli/src/commands/handlers/session/list.ts`, `packages/tui/src/context/keymap.tsx` | V1 footer.view.tsx:487 `label: "cmd"`；V2 mini/footer.view.tsx:473 同一处已改名 `label: "menu"`，V1 原文在 V2 产品源码 0 命中。 |
| `dialogs/cli-permission.json` | Allow always | pending(待人工确认) | 原锚点 `packages/opencode/src/cli/cmd/run/permission.shared.ts`;宇宙内/外命中:`packages/ui/src/i18n/en.ts` | V2 util/permission.ts:164 同分支返回 "Always allow"（语序被上游调整），V1 原文在产品源码 0 命中；唯一命中 packages/ui/src/i18n/en.ts:231（UI 库英文词典）。 |
| `dialogs/cli-question.json` | Confirm | pending(待人工确认) | 原锚点 `packages/opencode/src/cli/cmd/run/footer.question.tsx`;宇宙内/外命中:`packages/tui/src/component/dialog-update.tsx`, `packages/tui/src/component/prompt/autocomplete.tsx`, `packages/tui/src/routes/session/form.tsx` | V2 问题表单脚 footer.form.tsx（承接了本规则另外 4 条）已无独立 "Confirm" 标签（改用 formConfirm 逻辑与 "Review"）；宇宙内唯一独立 "Confirm" 是 util/permission.ts:166 的权限选项标签，已由 dialogs/cli-permission.json 锚定，再锚只会重复计数。 |
| `dialogs/dialog-agent.json` | native | pending(待人工确认) | 原锚点 `packages/tui/src/component/dialog-agent.tsx`;宇宙内/外命中:`packages/cli/src/framework/spec.ts`, `packages/tui/src/app.tsx`, `packages/tui/src/component/prompt/index.tsx` | V1 dialog-agent.tsx:15 `description: item.native ? "native" : item.description`；V2 该文件已重写为 698 字节的 DialogSelect 薄封装，无 "native" 串；其余宇宙内命中全部是注释。 |
| `dialogs/dialog-export.json` | to confirm | pending(待人工确认) | 原锚点 `packages/tui/src/ui/dialog-export-options.tsx`;宇宙内/外命中:`packages/tui/src/component/dialog-integration.tsx`, `packages/tui/src/component/dialog-session-list.tsx`, `packages/tui/src/component/dialog-stash.tsx` | V1 锚点 dialog-export-options.tsx:177/182 的提示语在 V2 被键位标题取代（61 "Next export option"/73 "Select export option"），V1 原文不在该文件；宇宙内其余命中分散在 6 个无关对话框，按子串替换会得到 "Press X again 确认" 式中英混杂串。 |
| `dialogs/dialog-provider.json` | label: "API key" | pending(待人工确认) | 原锚点 `packages/tui/src/component/dialog-provider.tsx`;宇宙内/外命中:`packages/app/e2e/utils/mock-server.ts`, `packages/app/src/providers/connect/dialog.stories.tsx`, `packages/core/src/plugin/provider/azure.ts` | V2 dialog-integration.tsx 已有 `placeholder="API key"`（本规则已迁），`label: "API key"` 在产品源码 0 命中；宇宙外命中是 app 的 mock-server/stories 与 core 的 azure 插件提示词。 |
| `dialogs/dialog-provider.json` | (Recommended) | pending(待人工确认) | 原锚点 `packages/tui/src/component/dialog-provider.tsx`;宇宙内/外命中:`packages/core/src/tool/plugin/question.ts` | V1 锚点 dialog-provider.tsx 在 V2 已被 dialog-integration.tsx 取代且无该串；唯一命中 packages/core/src/tool/plugin/question.ts:21 是给模型的提示词模板。 |
| `dialogs/dialog-provider.json` | Low cost subscription for everyone | pending(待人工确认) | 原锚点 `packages/tui/src/component/dialog-provider.tsx`;宇宙内/外命中:`packages/app/src/runtime/i18n/en.ts` | 产品源码 0 命中；唯一命中 packages/app/src/runtime/i18n/en.ts:173（桌面端英文词典）。 |
| `dialogs/dialog-provider.json` | Go to  | pending(待人工确认) | 原锚点 `packages/tui/src/component/dialog-provider.tsx`;宇宙内/外命中:`packages/tui/src/config/keybind.ts`, `packages/tui/src/config/v1/keybind.ts`, `packages/tui/src/feature-plugins/system/diff-viewer.tsx` | V1 dialog-provider.tsx:378/389 `Go to <span>https://opencode.ai/zen</span> to get a key`；V2 dialog-integration.tsx 无 "Go to"；宇宙内命中全是无关导航标签（"Go to the start of the diff"/"Go to parent session"），子串替换会得到 "前往 the start of the diff"。 |
| `dialogs/dialog-provider.json` | Custom provider | pending(待人工确认) | 原锚点 `packages/tui/src/component/dialog-provider.tsx`;宇宙内/外命中:`packages/app/src/runtime/i18n/en.ts`, `packages/core/src/v1/config/config.ts` | 产品源码 0 命中；命中在 packages/app/src/runtime/i18n/en.ts:231 与 packages/core/src/v1/config/config.ts（桌面端词典/配置注释）。 |
| `dialogs/dialog-rename.json` | title="Rename Session" | pending(待人工确认) | 原锚点 `packages/tui/src/component/dialog-session-rename.tsx`;宇宙内/外命中:`packages/tui/test/cli/tui/dialog-prompt.test.tsx` | V1 锚点文件在 V2 仍在，但 dialog-session-rename.tsx:15 已改为 `title="Rename session"`（s 小写）；V1 原文唯一命中是 packages/tui/test/cli/tui/dialog-prompt.test.tsx:47 的测试渲染。 |
| `dialogs/dialog-status.json` | Status | keep-as-is(护栏误报) | `packages/tui/src/component/dialog-status.tsx`(锚点不变) | 护栏误报：code_skeleton 只抹引号字符串，JSX 文本节点不在其列。V2 packages/tui/src/component/dialog-status.tsx:23 全文件唯一一处 \bStatus\b 即 <text attributes={BOLD}>Status</text> 标签，与 V1 同文件:47 同一处 UI 文本，替换安全。 |
| `dialogs/dialog-subagent.json` | title: "Open" | pending(待人工确认) | 原锚点 `packages/tui/src/routes/session/dialog-subagent.tsx`;宇宙内/外命中:`packages/app/src/shell/commands/command.test.ts` | V1 锚点 routes/session/dialog-subagent.tsx 在 V2 不存在；产品源码 0 命中，命中在 packages/app/src/shell/commands/command.test.ts:14（桌面端命令目录解码单测）。 |
| `dialogs/dialog-toast.json` | message: "Copied to clipboard" | re-anchored(已补锚点) | `packages/tui/src/component/dialog-integration.tsx`; `packages/tui/src/routes/session/index.tsx`; `packages/tui/src/util/selection.ts` | V1 锚点 ui/dialog.tsx:192 的 toast 调用；V2 全宇宙 4 处均为同一 toast.show({ message: "Copied to clipboard", ... }) 调用，字符串与角色完全一致。app.tsx:582 那处已由 common/error-messages.json 的同名 kept 条目覆盖，此处不重复锚定。 |
| `routes/route-footer.json` | Get started | pending(待人工确认) | 原锚点 `packages/tui/src/routes/session/footer.tsx`;宇宙内/外命中:`packages/app/src/runtime/i18n/en.ts`, `packages/console/app/src/i18n/en.ts` | V1 footer.tsx:59 `Get started <span>/connect</span>`；V2 该文件不存在，产品源码 0 命中；命中在 packages/app 与 packages/console 的英文词典。 |
| `routes/route-footer.json` | Permission | pending(待人工确认) | 原锚点 `packages/tui/src/routes/session/footer.tsx`;宇宙内/外命中:`packages/tui/src/component/session-frame.tsx`, `packages/tui/src/context/permission.tsx`, `packages/tui/src/feature-plugins/system/notifications.ts` | V1 footer.tsx:65 是 `{permissions().length} Permission(s)` 计数徽标，V2 该文件不存在。宇宙内唯一独立 "Permission" 是 mini/footer.permission.tsx:185 `width() < 24 ? "Permission" : "Permission required"`，只替换前半会得到 `? "权限" : "Permission required"` 的中英混杂三元式。 |
| `routes/route-header.json` | label: "Subagent" | pending(待人工确认) | 原锚点 `packages/tui/src/routes/session/subagent-footer.tsx`;宇宙内/外命中:`packages/tui/src/mini/demo.ts` | V1 锚点 subagent-footer.tsx 在 V2 不存在；产品源码 0 命中，唯一宇宙内命中是开发 playground packages/tui/src/mini/demo.ts:748/776（按 demo 规则排除）。 |
| `routes/route-header.json` | Parent | pending(待人工确认) | 原锚点 `packages/tui/src/routes/session/subagent-footer.tsx`;宇宙内/外命中:`packages/app/e2e/regression/session-message-revert.spec.ts`, `packages/app/e2e/regression/session-timeline-hydration.spec.ts`, `packages/app/e2e/regression/subagent-child-navigation.spec.ts` | V1 subagent-footer.tsx:104 导航标签；该文件在 V2 不存在，产品源码 0 命中；宇宙外命中全是 packages/app/e2e 回归用例。 |
| `routes/route-header.json` | Prev | pending(待人工确认) | 原锚点 `packages/tui/src/routes/session/subagent-footer.tsx`;宇宙内/外命中:`packages/ui/src/components/text-reveal.stories.tsx`, `packages/ui/src/components/thinking-heading.stories.tsx` | V1 subagent-footer.tsx:114 导航标签；V2 无该导航标签，宇宙内 0 命中，命中在 packages/ui/src/components/*.stories.tsx。 |
| `routes/route-header.json` | Next | pending(待人工确认) | 原锚点 `packages/tui/src/routes/session/subagent-footer.tsx`;宇宙内/外命中:`packages/tui/src/app.tsx`, `packages/tui/src/component/dialog-config.tsx`, `packages/tui/src/component/dialog-experiments.tsx` | V1 subagent-footer.tsx:124 独立导航标签；V2 该文件不存在，宇宙内 23 处 \bNext\b 全是复合键位标题（"Next item"/"Next export option"…），子串替换会得到 "上一个 item" 式中英混杂。 |
| `routes/route-home.json` | category: "System" | re-anchored(已补锚点) | `packages/tui/src/app.tsx`; `packages/tui/src/mini/footer.command.tsx` | V1 首页 tips 分类标签（tips 功能随 V2 消失）；同串在 V2 命令面板仍是 category 标签：app.tsx 22 处、mini/footer.command.tsx 3 处，与 V2 资产已译的 category:"Suggested"/"Prompt" 同角色。 |
| `routes/route-permission.json` | "Unknown" | pending(待人工确认) | 原锚点 `packages/tui/src/routes/session/permission.tsx`;宇宙内/外命中:`packages/tui/src/component/devtools-bar.tsx`, `packages/tui/src/mini/tool.ts` | V1 permission.tsx:287 `typeof data.subagent_type === "string" ? data.subagent_type : "Unknown"`；V2 该文件仍在但已无此回退；宇宙内命中是 devtools-bar.tsx:60 的地址回退与 mini/tool.ts:335 的工具入参回退（角色不同）。 |
| `routes/route-session.json` | "Failed to unshare session" | pending(待人工确认) | 原锚点 `packages/tui/src/routes/session/index.tsx`;宇宙内/外命中:`packages/app/src/runtime/i18n/en.ts` | V1 锚点 index.tsx 在 V2 仍在但该串已不在；产品源码 0 命中，唯一命中 packages/app/src/runtime/i18n/en.ts:644。 |
| `routes/route-session.json` | interrupted | suppressed(不得应用) | 隔离到 V2 不存在的路径,继续计未匹配 | V2 packages/tui/src/routes/session/index.tsx:1954 起新增 `const interrupted = createMemo(...)` 及 1957/1963/1977 的 interrupted() 调用；\b 替换会把 const 声明与调用点一起改成中文而直接构建失败。真正的 UI 串在 1978 行 ` · interrupted`（与 V1 index.tsx:1568 同），需人工改用精确键，本轮不动。 |

小计:keep-as-is(护栏误报) 1 条;pending(待人工确认) 31 条;re-anchored(已补锚点) 3 条;suppressed(不得应用) 1 条

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
