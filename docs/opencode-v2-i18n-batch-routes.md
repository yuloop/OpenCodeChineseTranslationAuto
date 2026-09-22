# V2 新翻译·切片单② —— `packages/tui/src/routes/`(会话/主页路由 UI)

> 批次定位:继 B1(`tui/src/ui/`,试点 PR #7)之后的第二个 Tier A 切片。本片覆盖**会话主界面 + 主页**,
> 是 B3(`routes/session/`)+ B4(`routes/` 其余)两批的合并执行——因为 `routes/` 全族只有 22 个文件、
> 15 个含 Tier A 串,按原批次划分拆成两 PR 的边际收益低于一次做完的术语一致性收益。
>
> 基线:上游 v2.0.13 检出(commit `3180aab`),`tools/v2_i18n_coverage.py` 串级账本,
> `apply --dry-run --strict --min-match-rate 1` 门禁(口径与试点 ⑦ 完全一致)。

## ① 范围与文件清单

切片 = `packages/tui/src/routes/` 全族 22 个文件(v2.0.13 实际存在的),其中 **15 个含 Tier A 串**:

| # | 文件(v2.0.13) | Tier A occ | 本片处置 |
|---|---|---|---|
| 1 | `home.tsx` | 9 | 翻译 6,保持原文 3(命令示例) |
| 2 | `session/index.tsx` | 244 | 翻译 130 条目(含 41 条 V1 沿用键修复) |
| 3 | `session/form.tsx` | 52 | 翻译 41 |
| 4 | `session/permission.tsx` | 44 | 翻译 18 |
| 5 | `session/composer/index.tsx` | 12 | 翻译 5 |
| 6 | `session/composer/shell-tab.tsx` | 17 | 翻译 9 |
| 7 | `session/composer/subagents-tab.tsx` | 22 | 翻译 10 |
| 8 | `session/composer/terminals-tab.tsx` | 15 | 翻译 7 |
| 9 | `session/dialog-execute.tsx` | 50 | 翻译 20 |
| 10 | `session/dialog-message.tsx` | 11 | 翻译 9 |
| 11 | `session/dialog-fork.tsx` | 4 | 翻译 4 |
| 12 | `session/dialog-timeline.tsx` | 1 | 已有锚点 1/1(试点前即通过,**本片零改动**) |
| 13 | `session/location-missing.tsx` | 6 | 翻译 4 |
| 14 | `session/message-parts.tsx` | 10 | 翻译 2 |
| 15 | `session/sidebar.tsx` | 3 | **零翻译**:3 条全是 CSS position 枚举误报(见 ⑧) |

无 Tier A 串的 7 个文件(`history.ts`/`message-navigation.ts`/`render-context.tsx`/`rows.ts`/
`thinking-syntax.ts`/`grouping/`×2)不建锚点。

**锚点文件 19 个(7 修复 + 7 新建 + 5 目标不存在于 v2.0.13 而跳过),共 267 条有效条目**;
`session/index.tsx` 因 V1 迁移期双规则并存,仍用 `--dup2` 后缀文件(与试点相同的资产惯例)。
> 门禁基线说明:V2 nightly(`.github/workflows/opencode-cn-v2-nightly.yml`)把上游 `v2.0.x` tag
> 浅克隆到临时目录作 `OPENCODE_SOURCE_DIR`,**不是**本仓自带的 `packages/`(那份比 v2.0.13 旧,
> 缺 `composer/`、`form.tsx` 等 9 个文件)。故所有键按 v2.0.13 原文校验;本仓旧副本不匹配是预期。
> 5 个被跳过的锚点文件(`dialog-subagent`/`footer`/`question`/`subagent-footer`,共 11 条)目标在
> v2.0.13 已不存在,门禁记 ⚠ 跳过(非失败);其键经核对对本仓旧副本 100% 存活,未擅动。

## ② 数量总览

| 指标 | 数 |
|---|---|
| 锚点文件(目标存在于 v2.0.13) | 15(7 修改 + 7 新建 + 1 已达标未动) |
| 锚点条目 | **267**(其中 266 条为本片写入) |
| 删除死键(V1 派生键在 v2.0.13 已失效) | **41** |
| 重锚定(V1 键形状漂移,同语义换新键) | 5 |
| 新增译文键 | 203 |
| 保留并验证仍存活的 V1 键 | 64 |
| Tier A occ(切片) | 581(翻译覆盖 446,其余 135 全部裁定,见 ⑧) |

## ③ 门禁前后(同试点口径)

| 门禁 | 本片前 | 本片后 |
|---|---|---|
| **切片门禁**(routes 族 15 个有目标的锚点文件,条目计) | 64/105 = 61.0%(3 文件 ✗) | **267/267 = 100%**(15/15 ✓) |
| **全局门禁**(全 V2 资产) | 750/865 = 86.7%(失败 3,均在切片外) | **953/1027 = 92.8%**(失败仍 3,均在切片外) |
| **V1 门禁**(V1 检出 + apply --strict) | 497/497 = 100% | **497/497 = 100%**(V1 词表零改动,复跑确认) |

(全局门禁的「前」= 最新 main(含 PR #9 batch-rest 片)实测;试点报告记的 309/545 是 PR #9 之前的数,
两口径相差的 246 条全部来自 PR #9 的 cli/config 片,与本片无关。)

全局门禁残余 3 个失败文件全部在切片外,且与本片无关(试点后即为这 3 个,PR #9 后依旧):
`component/dialog-mcp.tsx`、`component/dialog-session-rename.tsx`、`component/prompt/autocomplete.tsx`
(属 B2 范围)。

**死键 41 条的分布**(V1 词条停在 v2.0.12 之前形状):

| 文件 | 死键 | 典型形态 |
|---|---|---|
| `session/index.tsx` | 24 | `theme.textMuted}` 无点形态、`pending="Preparing patch…"`/`Updating todos…`(v2.0.13 已删该 UI)、`title=" Compaction "`/`title="# Todos"`(空格/无空格漂移)、分享会话族 4 条、`title: conceal()/showDetails()/showTimestamps()/sidebarVisible() ? …`(整族 keymap 重构) |
| `session/index.tsx--dup2` | 1 | `message: "Failed to copy URL to clipboard"` |
| `session/permission.tsx` | 16 | `options={{ once: "Allow once", … }}`(选项形态重构)、`title: \`Edit ${pathFormatter.format(filepath)}\`` 族 8 条(改由 SimulationSemantics 驱动)、`title="Always allow"`(移到 `util/permission.ts`)、`<text fg={theme.textMuted}>…` |

**重锚定 5 条**(旧键死、同语义新键活,均已在 ⑥ 标注):

| 旧键(v2.0.12 形状) | 新键(v2.0.13 形状) | 译文 |
|---|---|---|
| `Skill "{stringValue(props.input.name)}"` | `Skill "{name()}"` | `技能 "{name()}"` |
| `pending="Preparing edit…"` | `"# Preparing edit…"` | `"# 正在准备编辑..."` |
| `pending="Writing command…"` | `Writing command…`(裸文本,2 处) | `正在写入命令...` |
| `{revert()!.reverted.length} message reverted` | `{props.count} message{props.count === 1 ? "" : "s"} reverted` | `{props.count} 条消息已撤销` |
| `<text fg={theme.textMuted}>Tell OpenCode what to do differently</text>` | `<text fg={theme.text.muted}>…` | `告诉 OpenCode 如何处理` |

## ④ 术语依据(全部先核 V1 词表,不自创)

术语核对来源:`cli-go/internal/core/assets/opencode-i18n/`(V1)+ 既有 V2 资产(`git grep HEAD`)。
实证如下(键 → 译文,均可在资产中 grep 到):

| 英文词 | 采用译法 | V1/V2 实证 |
|---|---|---|
| session | 会话 | V1 `New session`→`新会话` |
| prompt | 提示 | V1 `category: "Prompt"`→`category: "提示"`;V2 `Manage queued prompts`→`管理队列提示` |
| agent | 智能体 | V1 `Agent`→`智能体` |
| subagent | 子智能体 | V1 `子智能体会话`;V2 `label: "Subagent"`→`label: "子智能体"` |
| workspace | **工作空间**(非「工作区」) | V1 `Manage workspaces`→`管理工作空间` |
| permission | 权限 | V1 `Permission required`→`需要权限`(本片 permission.tsx 同键沿用) |
| thinking | 思考 | V1 `Collapse thinking`→`收起思考`(本片既有键) |
| undo/revert | 撤销 | V1 `title: "Revert"`→`title: "撤销"`、`Undo previous message`→`撤销上一条消息` |
| redo | 重做 | 本片既有键 `title: "Redo"`→`title: "重做"` |
| clipboard | 剪贴板 | V1 `Copied to clipboard`→`已复制到剪贴板` |
| sidebar | 侧边栏 | V1 `在会话中显示或隐藏侧边栏` |
| terminal | 终端 | V1 `挂起终端并返回 Shell` |
| skill | 技能 | V2 `Skills`→`技能` |
| queued prompts | 队列提示 | V2 `Manage queued prompts`→`管理队列提示` |
| compaction(名词) | 压缩 | V1 `运行 /compact 压缩接近上下文限制的长会话` |
| compact(动词) | 精简 | V1 `精简会话`(故 `Compact session`→`精简会话`、`Compaction`→`压缩` 分工) |
| Background | 后台 | V1 `"background": "后台"` |
| interrupt | 中断 | V1 `title: "Interrupt session"`→`title: "中断会话"`、`interrupt`→`中断` |
| WebFetch | 网页获取 | V1 `title: \`WebFetch ${url}\``→`title: \`网页获取 ${url}\``(逐字同族) |
| …(省略号) | ASCII 三点 `...` | V1 `Loading skill…`→`正在加载技能...` |
| Shell(专名) | **保留英文** | V1 `挂起终端并返回 Shell`;仅 `label: "Shell"`(页签名)按 V1 `Shell mode`→`命令行模式` 译「命令行」 |
| 键位提示 esc/enter/c/o | **保留英文** | V1 全表 497 条中 0 条翻译键位提示 |
| 命令示例 ls -la/git status/pwd | **保留英文** | 与键位提示同类:home.tsx 输入框 placeholder 是给用户照着输入的命令文本 |
| Previous/Next + 对象 | 上一个/下一个 + 对象 | V1 `Previous/Next autocomplete item`→`上一个/下一个自动补全项` |
| Select + 对象 | 选择 + 对象 | V1 `Select autocomplete item`→`选择自动补全项`、`Select agent`→`选择智能体` |

**无 V1 先例的新词(本片裁定,已按 V1 风格最小化发挥)**:

| 英文 | 译文 | 裁定理由 |
|---|---|---|
| tab / tabs | 标签页 | 标准 UI 术语,V1/V2 无相反译例;本片 5 处统一(上一个/下一个标签页、关闭组合面板内的 `tabs`、form 页脚 `tab`) |
| form | 表单 | 标准 UI 术语;与 dialog 族「对话框」同角色 |
| token(s) | 令牌 | 标准术语;与同行「步/缓存/总计」不冲突 |
| composer | 组合面板 | V2 新概念(多 tab 容器),无先例;「组合」取 compose 本义,「面板」对齐容器类译法,4 个 composer 子文件统一 |
| steer(动词/名词) | 插入 / 待插入 | V2 新概念(把提示插入运行中的会话);与既有「队列」对偶:`steer`→插入、`Move to queue`→加入队列、`Pending steer`→待插入 |
| kill(Shell 命令) | 终止 | 与 interrupt→「中断」区分两个不同动作 |
| subagent picker | 子智能体选择器 | 对齐 V1 `Select agent`→`选择智能体` 的「选择器」构词 |
| fullscreen | 全屏 | V1 无先例;标准术语 |
| Web Search | 网页搜索 | 名词化产品词;V1 动词形 `Searching web…`→`正在搜索网络...` 用「网络」,名词取通用产品译法「网页搜索」 |
| patch(补丁) | 补丁 / 修补 | `# Patch failed`→`# 补丁失败`(名词)、`Patching`→`正在修补`(进行态) |
| 已创建/已删除/已修改 | ← Patched 族 | `# Created`→`# 已创建`、`# Deleted`→`# 已删除`、`← Patched`→`← 已修改`;对齐 V1 完成态「已」字句式(`会话已导出`) |
| 空态句式 | **暂无…** | 对齐 V1 `No MCP Servers`→`暂无 MCP 服务器`;本片 `No preview`→`暂无预览`、`No shell commands`→`暂无 Shell 命令` |

## ⑤ 译文样例表(供人眼验收,40 条)

均为 v2.0.13 实际源码串 → 本片译文;「锚点键」为写入 V2 资产的 find 串(节选,完整见资产文件)。

| # | 原文 | 译文 | 位置(v2.0.13) | 术语依据 |
|---|---|---|---|---|
| 1 | group: "Session" | group: "会话" | index.tsx ×32 | V1 同词 |
| 2 | group: "Prompt" | group: "提示" | index.tsx keymap | V1 同词 |
| 3 | title: "Close sidebar" | title: "关闭侧边栏" | index.tsx keymap | V1「侧边栏」 |
| 4 | title: "Copy session ID" | title: "复制会话 ID" | index.tsx keymap | V1「复制」+ID 保留 |
| 5 | message: "Session ID copied to clipboard!" | message: "会话 ID 已复制到剪贴板！" | index.tsx toast | V1 同族句式 |
| 6 | title: "Toggle session scrollbar" | title: "切换会话滚动条" | index.tsx keymap | V1「切换智能体」句式 |
| 7 | title: "Show tool calls individually" / "Group related tool calls" | title: "单独显示工具调用" / "分组相关工具调用" | index.tsx 三元 keymap | 新词(见 ④) |
| 8 | title: "Previous/Next user message" | title: "上一条/下一条用户消息" | index.tsx keymap | V1「上一条消息」句式 |
| 9 | title: "Background blocking tools" | title: "将阻塞工具转到后台" | index.tsx keymap | V1「后台」 |
| 10 | message: `Session not found: ${sessionID}` | message: `未找到会话: ${sessionID}` | index.tsx toast | V1「未找到」句式 |
| 11 | message: "Nothing to undo" | message: "没有可撤销的内容" | index.tsx toast | V1「撤销」 |
| 12 | message: `${feature} is not implemented for V2 sessions yet` | message: `${feature} 尚未在 V2 会话中实现` | index.tsx toast | 新词(见 ④) |
| 13 | title="Queued prompts" | title="队列提示" | index.tsx 对话框标题 | V2「管理队列提示」 |
| 14 | footer: `${index + 1} of ${queuedPrompts().length}` | footer: `第 ${index + 1} 个，共 ${queuedPrompts().length} 个` | index.tsx 队列翻页 | 对齐 V1「第 N 个」句式 |
| 15 | footerHints={[{ title: "steer", label: "enter" }]} | footerHints={[{ title: "插入", label: "enter" }]} | index.tsx 页脚 | 新词(见 ④);`enter` 保留 |
| 16 | title="Pending steer" | title="待插入" | index.tsx 待插入条 | 新词(见 ④) |
| 17 | title: "Move to queue" | title: "加入队列" | index.tsx 操作菜单 | V2「队列」 |
| 18 | const label = action === "cancel" ? "delete" : action | const label = … ? "删除" : action === "steer" ? "插入" : "加入队列" | index.tsx 代码位 | 与 17 同键族;插值进 19 的 toast |
| 19 | title: `Failed to ${label} pending prompt` | title: `${label}队列提示失败` | index.tsx toast | 承接 18 |
| 20 | Press <span …>{value()}</span> to move running work to the background | 按 <span …>{value()}</span> 将运行中的工作转到后台 | index.tsx 后台提示 | V1「后台」;`Press`→「按」对齐 V1「按 {…} 查看…」 |
| 21 | Jump to latest ↓ | 跳转到最新 ↓ | index.tsx 跳链 | V1「跳转到」句式 |
| 22 | <span …>Tokens</span> | <span …>令牌</span> | index.tsx 用量头 | 新词(见 ④) |
| 23 | new · {cached} cached · {total} total | 新增 · {cached} 缓存 · {total} 总计 | index.tsx 用量行 | 新词(见 ④) |
| 24 | · ! {n} likely cache {bust/busts} | · ! {n} 可能缓存失效 | index.tsx 用量告警 | 新词(见 ④);`!` 保留 ASCII |
| 25 | ⚠ {s>0 ? `Retrying in ${s}s` : "Retry due"} · attempt {n} | ⚠ {s>0 ? `${s} 秒后重试` : "立即重试"} · 第 {n} 次尝试 | index.tsx 重试条 | 新词(见 ④) |
| 26 | `Switched agent from ${prev} to ${agent}` / `Switched agent to ${agent}` | `已从 ${prev} 切换到 ${agent}` / `已切换到 ${agent}` | index.tsx 切换提示 | V1「切换智能体」 |
| 27 | "Instructions updated" | "指令已更新" | index.tsx 系统提示 | 完成态「已」句式 |
| 28 | Write {path} / Read {path} | 写入 {path} / 读取 {path} | index.tsx 工具行 | V1 `Preparing write…`→`正在准备写入...` 族 |
| 29 | ↳ Loaded {filepath} | ↳ 已加载 {filepath} | index.tsx 读取结果 | 完成态「已」句式 |
| 30 | Grep "{pattern}" / Glob "{pattern}" | 搜索 "{pattern}" / 通配符 "{pattern}" | index.tsx 工具行 | V1 `Searching content…`→`正在搜索内容...` |
| 31 | >in {path} < | >在 {path} < | index.tsx 工具行 ×2 | 状语前置 |
| 32 | WebFetch {url} | 网页获取 {url} | index.tsx 工具行 | V1 逐字同族 |
| 33 | Web Search via{" "} | 通过网页搜索{" "} | index.tsx 工具行 | 新词(见 ④) |
| 34 | Asked {n} question{s} | 已提问 {n} 个问题 | index.tsx 提问工具 | 中文无复数,`{s}` 折起 |
| 35 | file.type === "add" ? "# Created" : … "← Patched" | … "# 已创建" : … "← 已修改" | index.tsx 补丁工具 | 完成态「已」句式 |
| 36 | props.part.state.status === "error" ? "# Patch failed" : "Patching" | … "# 补丁失败" : "正在修补" | index.tsx 补丁工具 | 新词(见 ④) |
| 37 | props.group ?? "Permission" | props.group ?? "权限" | permission.tsx 主对话框 | V1「权限」 |
| 38 | <text …>Tell OpenCode what to do differently</text> | <text …>告诉 OpenCode 如何处理</text> | permission.tsx 拒绝输入 | 重锚定(theme.textMuted→theme.text.muted) |
| 39 | group: "Composer" | group: "组合面板" | composer/×4 文件 | 新词(见 ④) |
| 40 | ? "Review" : `Field ${n} of ${m}` | ? "审查" : `第 ${n} 个字段，共 ${m} 个` | form.tsx 进度头 | 新词(见 ④) |

另有多条未列入上表但已同批锚定:`label: "Shell"`→`命令行`、`label: "Terminals"`→`终端`、
`label: "Subagents"`→`子智能体`、`No shell commands`→`暂无 Shell 命令`、
`Unable to load terminal`→`无法加载终端`、`Choose directory`→`选择目录`、
`title="Session recovery"`→`title="会话恢复"`、`Thinking: `→`思考中: `、`Thought`→`思考`、
form.tsx 全部 keymap title(粘贴/清除/下一个字段/上一个字段/退出/提交答案编辑/复制链接/提交表单/滚动审查/选择答案/切换答案 共 16 条)与页脚 hint(tab/select/scroll/copy/close/dismiss)、
dialog-execute 全部滚动/复制 title 与 `Waiting for code…`→`正在等待代码...`。

## ⑥ 锚点资产改动明细(只动 V2)

15 个文件(7 修复 + 7 新建 + 1 已达标未动),共 267 条条目:

| 锚点文件 | 条目 | 改动 |
|---|---|---|
| packages-tui-src-routes-home.tsx.json | 6 | 保留 3(仍存活),新增 3(更新提示族) |
| packages-tui-src-routes-session-dialog-fork.tsx.json | 4 | 保留 1,新增 3 |
| packages-tui-src-routes-session-dialog-message.tsx.json | 9 | 保留 7,新增 2(Jump to/view message in session) |
| packages-tui-src-routes-session-dialog-timeline.tsx.json | 1 | **零改动**(1/1 已达标) |
| packages-tui-src-routes-session-form.tsx.json | 41 | 保留 3,新增 38 |
| packages-tui-src-routes-session-index.tsx.json | 130 | 删 24 死键(20 纯删 + 4 重锚),保留 46,新增 84 |
| packages-tui-src-routes-session-index.tsx--dup2.json | 1 | 删 1 死键(`Failed to copy URL to clipboard`),保留 1 |
| packages-tui-src-routes-session-permission.tsx.json | 18 | 删 16 死键(15 纯删 + 1 重锚),保留 2,新增 16 |
| packages-tui-src-routes-session-composer-index.tsx.json | 5 | **新建** |
| packages-tui-src-routes-session-composer-shell-tab.tsx.json | 9 | **新建** |
| packages-tui-src-routes-session-composer-subagents-tab.tsx.json | 10 | **新建** |
| packages-tui-src-routes-session-composer-terminals-tab.tsx.json | 7 | **新建** |
| packages-tui-src-routes-session-dialog-execute.tsx.json | 20 | **新建** |
| packages-tui-src-routes-session-location-missing.tsx.json | 4 | **新建** |
| packages-tui-src-routes-session-message-parts.tsx.json | 2 | **新建** |

(以上 15 个文件的目标均存在于 v2.0.13,门禁全部实测;另有 4 个 routes 锚点文件目标在 v2.0.13 不存在被跳过,见 ①。)

**精确键(避免 `\b` 简单词误伤代码位)9 处**,与试点 dialog-confirm 同思路:

| 文件 | 裸词风险 | 精确键形态 |
|---|---|---|
| index.tsx | `group: "Session"` 32 处若用裸 `Session` 会误伤 `SessionMessageInfo`/`sessionID` 等代码位 | 整条 `group: "Session"` |
| index.tsx | `Submit`/`total`/`Output`/`Code` 会误伤 `"Submit".length` 宽度计算、`total:` 对象键、`title: "Copy output"` | 用 `Submit\n              </text>` 多行键、`output:{" "}`、`{copied() === "code" ? …}` 整式键 |
| form.tsx | `Submit`(L855 按钮)与 `Submit form`/`Submit answer edit` 同文件,长短键依赖 apply 的长键优先机制仍可能级联 | `attributes={confirm() ? TextAttributes.BOLD : undefined}\n              >\n                Submit\n              </text>` 多行精确键 |
| permission.tsx | `left`/`top`/`row`/`center` 是 border/align 枚举,裸译会改布局 | 不译(见 ⑧ 误报类) |
| index.tsx | `skill`/`Skill` 与工具名比较位混杂 | `{" skill "}`(带空格整式)、`Skill {props.message.name}`、`Skill "{name()}"` 分别锚定 |

**代码位译文 12 处(可见文本处于函数体内,提取器记 Tier B,但与已译 Tier A 串构成同一可见整体故一并锚定)**:
form.tsx `actionLabel()` 8 个返回值(submit/continue/I finished/open link/done/edit/toggle/confirm——
插值进页脚 `enter {actionLabel()}` 这一 Tier A 行)、index.tsx `label` 三元(插值进 `${label}队列提示失败` toast)、
index.tsx `dir`/`file` 标签(插值进 `{label}: {value}` 附件行)。每条都在 ⑧ 表中登记。

**真 apply 验证**(临时树实跑非 dry-run,`/tmp/oc-routes/applied`,逐行 diff 全量人眼核对):
15 个文件全部按上表替换;引号/反引号/行数守恒校验通过(唯一引号数变化是 3 处英文复数折起
`"s" : ""` 与 1 处三元展开,净 −6,与预期一致);无级联误伤(如 `Submit` 多行键未污染
`Submit form`;`group: "Session"` 32 处同译不互相破坏)。

## ⑦ 复量数字

| 门禁 | 本片前 | 本片后 |
|---|---|---|
| 切片门禁(routes 15 锚点文件,条目) | 64/105 = 61.0% | **267/267 = 100%** |
| 全局门禁(全 V2 资产,条目) | 750/865 = 86.7% | **953/1027 = 92.8%** |
| V1 门禁(V1 检出) | 497/497 = 100% | **497/497 = 100%** |

串级账本(`tools/v2_i18n_coverage.py`,同一脚本 before/after 对拍):

**主宇宙 tui 包(优先归并口径,distinct)**:

| 类 | before | after | delta |
|---|---|---|---|
| covered | 246 | 429 | **+183** |
| migratable | 140 | 112 | −28 |
| fuzzy-simple | 70 | 51 | −19 |
| new | 811 | 675 | **−136** |
| **合计** | **1267** | **1267** | 0(没有掩盖任何一条,只是分类) |

(occurrences:covered 440→758、migratable 498→398、fuzzy 83→59、new 1157→963。)

**routes 族(逐文件累计,occ;15 个含 Tier A 文件)**:

| 类 | before | after | delta |
|---|---|---|---|
| covered | 128 | 446 | **+318** |
| migratable | 127 | 27 | −100 |
| fuzzy-simple | 30 | 6 | −24 |
| new | 296 | 102 | **−194** |
| **合计** | **581** | **581** | 0 |

routes 族 `new` 从 296 → 102,**剩余 102 条 + 27 migratable + 6 fuzzy-simple = 135 occ 全部有明确处置**
(见 ⑧ 分账,无一条静默丢弃)。

## ⑧ 逐条裁定:切片 135 个未译 Tier A occ 的完整分账

| 处置 | occ | 内容 |
|---|---|---|
| **① 提取器误报(排除)** | **97** | Tier A 位置的程序化值:trait/状态比较 39(`installed`×2、`ANSWER`×2、`REJECT`、`streaming`×4、`system`/`synthetic`/`reasoning`×2、`exploration`、`agent-switched`/`model-switched`/`location-switched`、`compaction-queued`、`tool-call`、`turn-usage`、`assistant-footer`、`user`×2、`assistant`、`hide`、`always`、`task`、`shell`×5、`subagent`、`glob`/`read`/`grep`/`webfetch`/`websearch`/`execute`/`patch`);CSS/布局枚举 39(`left`×12、`top`×4、`row`×2、`column`×2、`center`×2、`flex-start`×4、`space-between`×2、`grid`×2、`absolute`×2、`relative`、`rendered`×4、`word`×2);命令 id 5(`message.jump`/`session.revert`/`message.copy`/`session.fork`/`queued_prompt.delete`);id 模板 3(`${id()}.actions`、`${id()}.action.${String(option)}`、`${ctx.sessionID}:${time}:${id}`);SimulationSemantics 标签 6(`Reject permission: ${props.action}`、`Rejection reason`、`Rejection actions`、`Confirm rejection`、`Cancel rejection`、`Permission choices`——均不渲染);`function`(typeof 比较)、`light`×2(theme 比较);用户输入数据 2(` ${skill.name} `、`"{stringValue(props.input.query)}"`) |
| **② 按规则保持原文** | **15** | 键位提示 10(`esc`×4、`esc back`、`enter`×4、`c`——V1 全表 497 条 0 条译键位提示);命令示例 3(`ls -la`/`git status`/`pwd`,home.tsx placeholder 是供用户照着输入的命令文本);数字编号 2(`${i() + 1}.`、`${rows().length + 1}.`,中英同形态) |
| **③ 分类器盲区(已译,键不含该文本片段)** | **22** | 整行/整式锚点跨 JSX 表达式边界,提取器把文本节点切碎后看到的片段:`new · `/` total`/` cached` 族、` completed`、`! Likely cache bust: `/` fewer cached tokens…`、`output:`、`Skill `/` reverted`/` or /redo to restore`/` more`/`Write `/`Read `/`↳ Loaded `/`Asked `/`WebFetch `/`Error [`、`execute`(×2)、`Code`/`Output`、` to move running work to the background`。真 apply diff 已证全部译出(见 ⑥) |
| **④ 源码比较值(译了会破坏逻辑)** | **1** | `Step interrupted`(index.tsx L1954,`props.message.error?.message === "Step interrupted"` 是**等式比较**,译即失效;且该值本就是开发者向错误串,非 UI 散文) |
| **合计** | **135** | 97 + 15 + 22 + 1,**与 ⑦ 账本剩余数一致** |

**可见但属 Tier B 代码位(本片不翻,移交 B8;提取器记 code 位故不在上面 135 内)**:

| 位置(v2.0.13) | 英文 | 可见性 | 建议译文(B8) |
|---|---|---|---|
| index.tsx L2027 `actor()` | `"Shell"` / `"Subagent"` | SessionNoticeMessageV2 标题头 | `命令行` / `子智能体` |
| index.tsx L2102 `usage()` | `in` / `out` | 令牌用量行 | `输入` / `输出` |
| index.tsx L2256-2259 ShellMessage | `Command cancelled` / `Command timed out` / `Command exited with code ${exit}` | Shell 工具错误行 | `命令已取消` / `命令已超时` / `命令退出码 ${exit}` |
| index.tsx L2386 | `attachment` | 附件名回退 | `附件` |
| index.tsx L3515 | `(no answer)` | 问题工具回退 | `(无回答)` |
| permission.tsx L498 `hint()` | `minimize` / `fullscreen` | 权限对话框页脚键位提示 | `收起` / `全屏` |
| dialog-execute.tsx L68-75 `status()` | `Receiving code…` / `Running` / `Failed` / `Completed` | 执行对话框标题 | `正在接收代码...` / `运行中` / `失败` / `已完成` |
| dialog-execute.tsx L140 | `No output` / `Waiting for output…` | 输出区空态 | `暂无输出` / `正在等待输出...` |
| composer/subagents-tab.tsx L50/L203 | `"Subagent"` / `"Running"` | 子智能体列表标签/状态 | `子智能体` / `运行中` |

## ⑨ 质量自评与已知风险

### 9.1 术语一致性

- 267 条译文全部先核 V1 词表(④ 表);无 V1 先例的 13 组新词逐个给出裁定理由,并优先复用 V2 资产已在用词(技能/队列提示/子智能体/剪贴板/确认/取消/暂无句式/后台)。
- **未发现与 V1 冲突的译法**;延续试点的「反向修正」:workspace 用资产实证的「工作空间」。
- `Shell` 一词两处理:`label: "Shell"`(页签名)→「命令行」(V1 `Shell mode`→`命令行模式`),其余专名位置保留英文(V1 `挂起终端并返回 Shell`)。

### 9.2 已知风险

1. `group: "Session"` 是 32 处批量锚点:若上游改名(如 "Sessions"),门禁立刻失败报警——期望行为(漂移检测),按 nightly 流程修键即可。同理 `group: "Composer"` 跨 4 文件 12 处、`group: "Permission"`、`group: "Form"`。
2. `Writing command…` 是裸文本键(非简单词,子串替换,2 处):若未来新增第三个 "Writing command…" 出现在**不该译的位置**会误伤;届时改精确键。
3. `? "Review" :`、`: "Compaction"}`、`props.completed ? "Thought" :` 等是「三元前半」精确键:依赖 v2.0.13 的确切源码形状,上游若重排该表达式则键失效(门禁报警,不会静默错译)。
4. 代码位译文 12 处(form actionLabel/index label/dir-file)是「与已译 Tier A 串构成同一可见整体」的例外裁决:若后续批次认为代码位应整体留给 B8,可一键回退这 12 条(互不相干,不影响其余 254 条)。
5. `通过网页搜索{" "}` 因插值顺序只能译前半(`Web Search via{X}`→`通过网页搜索 {X}`);如更喜欢「通过 {X} 网页搜索」需上游改插值顺序,非本片可解。
6. `composer`→「组合面板」为全新概念译名,V1/V2 无先例;如社区有既定译法可在全量阶段统一替换(涉及 4 文件 12 处 `group` + 4 处 title)。

### 9.3 与覆盖账本的互相验证

- 账本 ⑥ 盲区类(单词级标签处于代码/数组位)在本片实测存在且已量化:97 条 Tier A 误报 + 22 条已译盲区 + 9 条可见 Tier B。
- 账本「migratable 需人工复核」在本片再次实证:V1 派生键 105 条中 **41 条(39%)在 v2.0.13 已死**——直接迁移不可行,必须逐键对上游源码复核。这是对 B4-B7 各批的直接输入:**每批预算 30-40% 的 V1 键复核工作量**。
- 账本 ⑦ 预测 B3(`routes/session/`)~270 distinct:本片实测 routes 全族 Tier A 581 occ(去重后 distinct 更少),量级吻合;B4 的 `routes/` 其余部分实际只剩 home.tsx(已在本片做完)。

## ⑩ 跨片提示(给后续批次)

1. `permissionOptionLabel` 的 `"Always allow"`→`"始终允许"` 住在 `packages/tui/src/util/permission.ts`(切片外):现有锚点 `packages-tui-src-util-permission.ts.json` 缺这条,**util 片(B6)需补**。
2. `switchLabel`(`Switched variant to…`/`Switched model to…`)在 `packages/tui/src/util/model.ts`(切片外):model-switched 系统提示的正文在此,**B6 需补**;本片已译同一组件的 agent-switched 分支。
3. `actor()` 的 `"Shell"`/`"Subagent"` 与 `hint()` 的 `minimize`/`fullscreen` 是**可见 Tier B**,已列建议译文(⑧ 表),B8 可直接取用。
4. `session/index.tsx` 的 `--dup2` 文件现存 1 条(`Loading skill…`):与主文件同键重复(主文件也有),apply 幂等故两份都计成功;如未来清理双规则,注意同步删两份。

## ⑪ 合规自查

- 只改 V2:`git status` 仅 `cli-go/internal/core/assets/opencode-i18n-v2/anchors/` 下 14 个文件(7 改 7 增)+ 本文档;V1 词表/注入脚本/门禁/workflow/`config.json` 零改动(V1 门禁复跑 497/497 实证)。
- `config.json` 未动:试点 PR #7 先例(清单只跟踪 V1 迁移状态,新译条目不入清单;自造 status 有破坏 schema 风险)。
- 未改 `.github/`、未改产品代码、未推 upstream、未触碰 `/root/xiangmudata_sync/opencode-v2-cn/`、未越出 `packages/tui/src/routes/`(util/model.ts、util/permission.ts 只列提示未动)。
- 复现确定性:所有数字来自真实命令输出(v2.0.13 检出 + `go build` 的 cli + 仓库内资产),无硬编;266 条锚点键全部经脚本对 v2.0.13 原文逐条命中校验(0 miss)后才写入;JSON 资产均通过 `json.load` 校验。
