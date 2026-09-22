# opencode V2 汉化 · 批次剩余切片报告(`packages/tui/src/` 除 `ui/`·`component/`·`routes/` + `packages/cli/src/` 全部)

- 日期:2026-09-22
- 性质:**真翻译批次**。只新增/修改 `cli-go/internal/core/assets/opencode-i18n-v2/` 资产;未改 V1 任何文件(词表/注入脚本/门禁/workflow)、未改 `.github/`、未改产品代码、未推 upstream、未触碰 `/root/xiangmudata_sync/opencode-v2-cn/`,未触碰并行切片范围(`ui/` 试点已由 PR #7 完成,`component/`、`routes/` 另单在跑)。
- 测量基准:上游 tag **`v2.0.13`**(commit `3180aab16e050128678e590afcbd2dc85c259cb7`),与覆盖账本 `docs/opencode-v2-i18n-coverage.md` 同一基准。工具 `tools/v2_i18n_coverage.py` + 自建条目级门禁 `gate_scope.py`(复刻 `cli-go/internal/core/i18n.go` 的 `replacementMatches` 语义)。
- 分支:`feat/v2-i18n-batch-rest`。

## ① 结论摘要(TL;DR)

1. **实际范围先列清(不猜)**:`packages/tui/src/` 排除 `ui/`、`component/`、`routes/` 三个目录后的全部 + `packages/cli/src/` 全部 = **260 个产品文件**(Tier A 串 978 occurrences)。明细见 ②。
2. **范围内门禁 100%**:54 个锚点文件 **573/573 条目全部命中**(批次前 132/151,其中 app.tsx 40/54、local.tsx 3/6、mcp.tsx 4/6 失败,3 个锚点文件的目标在 v2.0.13 已不存在)。全局门禁 **747/863 = 86.6%**,3 个失败文件**全部在 `component/`**(dialog-mcp / dialog-session-rename / prompt-autocomplete),与试点后基线(309/545,同样这 3 个)完全一致——属并行切片范围,本单未新引入任何失败。**V1 门禁仍 497/497 = 100%**,V1 资产零改动。
3. **真机验证**:对 v2.0.13 私有副本实跑 `apply`(非 dry-run),859 行改动,TypeScript 解析 **0 语法错误**,且与未汉化基线的 tsc 错误谱完全一致(713×TS2307 / 88×TS2580 / 50×TS2339 / 25×TS2345 / 19×TS2741 / 4×TS2322 / 2×TS2745 / 1×TS2867——全部是无 node_modules 导致的模块解析类,非本次改动引入)。
4. **工作量**:413 条新译文(6 个并行翻译批次)+ 445 条新锚点条目 + 21 条失效锚点清理 + 3 个死锚点文件删除 + 5 条提取器误报(比较运算右操作数)停翻处置。
5. **一个必须写进方法的发现**(试点 ⑧ 的再次实证):Tier A new 里混有三类**不该翻**的串——① 比较运算右操作数(如 `error.message === "Session not found"`、`SSH_ASKPASS_PROMPT === "confirm"`),翻了会**破坏程序逻辑**;② 内部 id/状态键(`diff.next_hunk`、`needs_auth`、`shell_output`);③ 键位提示与符号(`esc`、`left/right`、`·`、`TOKENS`)。本单用 DROP 表 + 精确上下文键 + 边界审计三类手段逐条处置,审计脚本对全部 559 条目做了「比较右操作数 / 标识符内子串 / 简单词嵌入更长字面量」三项扫描,残留 0。

## ② 实际覆盖的目录清单与条数(工具实测)

复现命令(只读):

```bash
# 全局账本
python3 tools/v2_i18n_coverage.py --source-dir <v2.0.13 检出>
# 条目级门禁(范围内逐条目复验)
python3 /tmp/pilot/gate_scope.py --source-dir <v2.0.13 检出>
# 质量门禁
cd cli-go && go build -trimpath -o /tmp/pilot/opencode-cli-rest .
OPENCODE_SOURCE_DIR=<v2.0.13 检出> /tmp/pilot/opencode-cli-rest apply --dry-run --strict --min-match-rate 1
```

**范围内 Tier A 账本(occurrences,同一脚本同一基线实测)**:

| 类 | 批次前 | 批次后 | 说明 |
|---|---|---|---|
| covered | 155 | 719 | +564 occ 进入已覆盖 |
| migratable | 208 | 122 | 86 个可见标签按 V1 精确词条补锚(见 ⑥-MIGRATE) |
| fuzzy-simple | 39 | 1 | 38 条全部裁定并锚定 |
| new | 576 | 136 | 440 条已翻译锚定;残余 136 条全部有裁定(见 ⑧) |
| **合计** | **978** | **978** | 总量不变,没有掩盖任何一条 |

**锚点文件按目录分布(54 个文件 / 559 条目)**:

| 目录 | 文件数 | 锚点条目 |
|---|---|---|
| `packages/cli/src/acp/` | 2 | 4 |
| `packages/cli/src/commands/`(含 handlers/) | 7 | 67 |
| `packages/cli/src/config/` | 1 | 1 |
| `packages/cli/src/run/` | 1 | 2 |
| `packages/cli/src/services/` | 1 | 9 |
| `packages/cli/src/`(根文件:session-target.ts) | 1 | 1 |
| `packages/tui/src/`(根文件:app.tsx) | 1 | 72 |
| `packages/tui/src/config/`(含 v1/) | 4 | 86 |
| `packages/tui/src/context/` | 3 | 6 |
| `packages/tui/src/feature-plugins/`(home/prompt/sidebar/system) | 14 | 113 |
| `packages/tui/src/mini/` | 13 | 167 |
| `packages/tui/src/plugin/` | 2 | 10 |
| `packages/tui/src/util/` | 4 | 21 |

(`cli/src/mini.ts` 与 `cli/src/ssh-askpass.ts` 无锚点文件:两者唯一的 Tier A new 串均为比较运算右操作数,已按 ⑧-3 停翻。)

排除目录(逐条说明):`packages/tui/src/ui/`(PR #7 试点已完成)、`packages/tui/src/component/`、`packages/tui/src/routes/`(并行切片在跑)。`packages/{ai,app,client,core,desktop,protocol,schema,server,sdk,session-ui,stats,theme,web,...}` 不在本单范围(覆盖账本另有规划)。

## ③ 翻译批次与条数

| 批次 | 范围 | 条数 |
|---|---|---|
| cli | `packages/cli/src/` 命令描述/服务/更新器/导入导出 | 72 |
| cfg | `packages/tui/src/config/`(含 v1/、schema 注解) | 74 |
| fp | `packages/tui/src/feature-plugins/`(home/prompt/sidebar/system) | 98 |
| mini | `packages/tui/src/mini/`(footer 族/stream-v2/tool/scrollback/splash) | 85 |
| app | `packages/tui/src/app.tsx` + `context/` + `plugin/` + `util/` | 46 |
| fuzzy | 跨文件 fuzzy-simple(38 条人工裁定批) | 38 |
| **合计** | | **413** |

每条译文都经:① 子代理按统一 brief(术语表 + 省略号 ASCII 化 + ASCII 标点 + `${...}` 插值原样保留)产出;② 父代理逐批复核(跨批次同 key 译文冲突扫描 = 0);③ 锚点构造后逐条目在 v2.0.13 源码命中验证。

## ④ 术语依据(全部先核 V1 词表,不自创)

沿用试点 ④ 词表并新增以下实证(键 → 译文,均可在 V1 资产中 grep 到):

| 英文 | 译文 | 依据 |
|---|---|---|
| Agent / subagent | 智能体 / 子智能体 | V1 `dialog-agent.json`、`component-question.json` |
| Reject / Confirm / Cancel | 拒绝 / 确认 / 取消 | V1 `cli-permission.json`、`dialog-question.json` |
| Connected / Disabled(MCP 状态) | 已连接 / 已禁用 | V1 `route-sidebar.json`、`dialog-mcp.json` |
| Permission(窄终端短标签) | 权限 | V1 `route-footer.json` |
| Session / Prompt / System | 会话 / 提示 / 系统 | V1 `dialog-session.json` 等 |
| Copied to clipboard | 已复制到剪贴板 | V1 `component-selection.json` 等 |
| Waiting for permission event... | 等待权限事件... | V1 `routes/route-footer.json` |
| Shell command | Shell 命令 | V1 `cli-permission.json` |
| worktree / workspace | 工作树 / 工作空间 | V1 `dialog-session.json`、`component-sidebar.json` |
| queued prompts | 队列提示 / 排队中 | V1 `dialog-session.json`;徽标语境用「排队中」 |
| steer(Prompts steer by default) | 引导 | V2 Session Core 词汇,徽标译「引导中」 |
| patch / diff / hunk | 补丁 / 差异 / 差异块 | V1 `dialog-stash.json` 等 |
| Glob / Grep / Read / Edit / Write | 通配符 / 搜索 / 读取 / 编辑 / 写入 | V1 `dialog-help.json`、`component-tips.json` |
| transcript | 记录 | V1 `dialog-session.json`("会话记录") |
| tokens / TOKENS / MCP / OAuth / LSP / VCS→版本控制 | 保留英文(单位/协议名) | V1 先例;`VCS` 作为分组标题按「版本控制」译(同组 `Diff`→「差异」) |

保留英文(不改):OpenCode、Claude、GPT、Gemini、TUI、ACP、MCP、OAuth、LSP、JSON、Markdown、SDK、API、URL、HTTP、tmux、wayland、x11、win32、base64、shell、tokens/TOKENS(单位)、`:q`、`ctrl+a`、`esc`/`enter`/`tab` 等键位名、`…`→`...`(ASCII 三点)。

## ⑤ 锚点构造与安全审查(本单新增的方法约束)

1. **键的三种构造**:`prop:X` → `X: "value"`;`attr:X` → `X="value"`;jsx-text 用原文(保留首尾空白,内部换行折叠——JSX 会裁剪纯空白行,替换后渲染不变)。
2. **jsx-text 带空白的值**(如 home/footer.tsx 的 ` MCP\n  `、` failed\n  `、stats.tsx 的 `Your last `):译文表以归一化值为键,锚点以**原始值**构造,替换时保留首尾空白,避免间距塌陷。
3. **复数三元整条替换**:`` `Asked ${total} question${total === 1 ? "" : "s"}` `` → `` `已提问 ${total} 个问题` ``;mcp.tsx `} error${bad() > 1 ? "s" : ""}` → `} 错误`(修掉「2 错误s」)。
4. **三项边界审计**(对全部 559 条目,残留 0):
   - **比较运算右操作数**:键不能出现在 `=== "key"` / `!== "key"` / `case "key"` / `return "key"` 右侧——5 条命中全部停翻(见 ⑧-FP)。
   - **标识符内子串**:子串键的每次出现都不能紧邻单词字符——抓到 `Path: ` 会命中 `formatPath:` 类型注解(代码损坏),改用整条模板字面量 `` `Path: ${formatPath(value)}` ``。
   - **简单词嵌入更长字面量**:`\bword\b` 会命中 "Search sessions" 这类复合串——扫描 0 命中。
5. **裸简单词禁用兜底**:jsx-text 裸词(如 `Context`、`Image`)若直接做键,`\b` 语义会误伤 `Plugin.Context` 类型引用、`loadImage`/`DiffViewerImage` 标识符——一律改精确上下文键(`<b>Context</b>`、`>Image</text>`)。
6. **标签-比较同步**:stats.tsx 的 `metric.label === "best streak"` 与 stats-data.ts 的 `label: "best streak"` 必须同译,否则「天」后缀永远不显示。

## ⑥ 锚点变更明细

- **新增 42 个锚点文件,修改 12 个**(合并进既有条目),共 54 文件 559 条目(其中本单新增 445 条)。
- **删除 3 个死锚文件**(目标在 v2.0.13 已不存在):`packages-tui-src-feature-plugins-home-tips-view.tsx.json`、`packages-tui-src-feature-plugins-home-tips.tsx.json`、`packages-tui-src-feature-plugins-sidebar-lsp.tsx.json`。
- **清理 21 条失效键**(app.tsx 14: Connect provider / Copy worktree path / auto-approve×2 / session directory filtering×2 / Switch org / Toggle MCPs / `Update Available` / Failed to fork session / The current session was deleted / Update failed / `Updating to v${version}…` / Update Failed;local.tsx 3:两条 model is not valid + `Agent not found: ${name}`;mcp.tsx 3:Needs client ID / `>Needs auth</Match>` / `} error`;util/permission.ts 1:`Path: `)。失效键中 4 条以精确键重锚(`"The current session was deleted"`→当前会话已删除;`message: \`Agent not found: ${id}\``→未找到智能体; `>Sign in</Match>`→登录;`} error${bad() > 1 ? "s" : ""}`→错误)。
- **MIGRATE(V1 精确词条迁移,10 个文件)**:`"Prompt"`→提示、`"Session"`→会话、`"System"`→系统、`"Shell mode"`→命令行模式、`"Review"`→审查、`"current"`→当前、`"interrupt"`→中断、`"normal"`→普通、`"Type your own answer"`→输入自定义答案等——只迁移「V1 key 与 V2 可见值完全相同」的条目,且逐条验证在 v2.0.13 命中。
- **EXTRA(精确上下文键,18 个文件)**:分类器误分为 migratable/covered 但实际可见的单词级标签,如 MCP 状态 `>Connected</Match>`/`>Connecting</Match>`/`>Error</Match>`/`>Disabled</Match>`/`>Sign in</Match>`、页脚值 `? "on" : "off"`→开关、`"saving"`→保存中、`? "queued" : "steering"`→排队中/引导中、`busy() ? "running" : "idle"`→运行中/空闲、权限控件 `{compact() ? "reject" : "confirm"}` 等、`> scroll</span>`→滚动、`"Reject"`/`"Permission"` 窄终端短标签、`\`${activeSubagentCount()} active\``→个活跃。
- **config.json(manifest 账本)未改动**——与试点先例一致:锚点由 `LoadConfig` 扫 `anchors/` 目录加载,manifest 账本由覆盖工具维护,本单不引入重复记账。

## ⑦ 复量数字

| 门禁 | 批次前 | 批次后 |
|---|---|---|
| 范围内条目级(573 条目) | 132/151 命中,3 文件失败 | **573/573 = 100%** |
| 全局 `apply --dry-run --strict --min-match-rate 1` | 309/545 = 56.7%,5 失败(试点后 3 失败) | 747/863 = 86.6%,**3 失败(全在 `component/`,与基线一致)** |
| V1 `apply --strict` | 497/497 = 100% | **497/497 = 100%**(V1 资产零改动) |
| 真机 apply + tsc 解析 | — | 859 行改动,**0 语法错误**,错误谱与基线一致 |

## ⑧ 逐条裁定规则(三类不翻 + 处置方式)

### 8.1 保持原文(键位提示/符号/单位,约 25 个 distinct)

`esc`、`enter`、`pgup/pgdn`、`tab next`、`esc dismiss`、`esc back`、`esc close`、`left/right`、`left`、`right`、`j/k ↑/↓ scroll`、`:q`、`ctrl+a`、`right-click`、`enter queue`、`enter steer`、`left/right change`、`tab show ${...}`、`FILTER`、`·`/`■`(`\u00b7`/`\u25a0`,日历热力图字元)、`· ${props.sourceDetail}`、`· ${variant}`、`TOKENS`、`tokens`(单位)、`${input.mono ? "[O]" : "▪"} oc mini`、`${header().hint} ${props.mono ? "-" : "·"}`。

### 8.2 提取器误报(内部 id/状态键/程序化值,约 60 个 distinct)

`diff.*`(20 个命令 id:diff.up/down/first/last/help/next_hunk/previous_hunk/next_file/previous_file/page.up/page.down/half_page.up/half_page.down/toggle_view/toggle_file_tree/single_patch/switch_source/mark_reviewed/close)、`dialog.plugins.*`、`plugins.toggle`、`opencode.diffs`、`app.exit`、`diff-file-header-*`、`diff-file-row-*`、`diff-folder-row-*`、`diff-image-*`、`needs_auth`、`shell_output`、`turn_summary`、`work_spinner`、`verbosity`、`mono`、`splash`、`copy_on_select`、`thought_level`、`reasoning`(内部 kind)、`home`/`screen`/`storybook`/`tmux`/`wayland`/`win32`/`x11`/`dummy`/`grid`/`composer`/`muted`/`base64`/`absolute`/`bottom`/`center`/`column`/`stretch`/`transparent`/`modified`/`unbound`/`word`/`inactive`/`active`(枚举值)。

### 8.3 比较运算右操作数(5 条,**翻了会破坏逻辑**,已停翻并记入 DROP 表)

| 串 | 位置 | 不停翻的原因 |
|---|---|---|
| `Session not found` | `cli/src/mini.ts:64` | `error.message === "Session not found"`;错误对象由 `session-target.ts:110` 抛出,可能来自服务端,只翻一侧即失效 |
| `The provider response ended unexpectedly.` | `cli/src/run/noninteractive.ts:471` | `event.data.error.message === ...`,比对服务端推送的英文报文 |
| `confirm` | `cli/src/ssh-askpass.ts:26` | `process.env.SSH_ASKPASS_PROMPT === "confirm"`,环境变量协议值 |
| `normal` | `feature-plugins/prompt/footer.tsx:15/63` | 类型标注 `mode: "normal" \| "shell"` 与 `when={props.mode === "normal"}`,均非可见文本(可见的 `label: "normal"` 在 `mini/footer.view.tsx`,已按 V1 译「普通」) |
| `best streak`(stats.tsx 侧) | `system/stats.tsx:126` | 仅比较操作数;可见标签在 `stats-data.ts:10`,已译「最长连续天数」并**同步**比较式 |

### 8.4 纯模板/插值(无可译散文,约 30 个 distinct)

`${title} "${pattern}"`、`${title} "${query}"`、`${title} ${formatPath(value)}`、`LSP ${operation}${file ? ...}`、`${child.title}: ${projected.title}`、`${ctx.name} ${title}`、`<file name="${file.filename}">\n${content}\n</file>`、`[${block.resource.uri}]\n${block.resource.text}`、`${rows().length + 1}.`、`${new Date(...).toLocaleString()} - ${session.id.slice(-8)}`、`…${tail.slice(-1_999)}` 等。

## ⑨ 风险与遗留

1. `component/` 的 3 个失败文件(dialog-mcp / dialog-session-rename / prompt-autocomplete)属并行切片范围,本单未触碰;全局门禁 100% 需待该切片合入。
2. 共享上游检出目录 `/tmp/oc-v2i18n-cov/upstream-v2013` 曾被并行作业实跑 `apply` 污染(约 21:34 出现 62 个文件被改写后又还原),本单全部验证已改用在**私有纯净副本** `/tmp/oc-v2i18n-cov/my-v2013`(`git archive 3180aab` 导出)上进行,复核时请勿复用共享目录。
3. 未决(不影响门禁):`tokens`/`TOKENS` 作为单位保留英文,sidebar 统计行呈现中英混排(`12,345 tokens / 65% 已用`);若后续要统一,需单独立项。
