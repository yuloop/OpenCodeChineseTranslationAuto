# opencode V2 汉化 · 批次报告 B2(`packages/tui/src/component/` 切片)

- 日期:2026-09-23
- 性质:**B2 切片真翻译**。只新增/修改 `cli-go/internal/core/assets/opencode-i18n-v2/` 资产(27 个 anchors 文件 + `config.json` 的 `manifest.manualNotes` 追加);未改 V1 任何文件(词表/注入脚本/门禁/workflow)、未改 `.github/`、未改产品代码、未推 upstream、未触碰 `/root/xiangmudata_sync/opencode-v2-cn/`。
- 测量基准:上游 `anomalyco/opencode` tag **`v2.0.13`**(commit `3180aab16e050128678e590afcbd2dc85c259cb7`,与覆盖账本 `docs/opencode-v2-i18n-coverage.md`、试点报告 `docs/opencode-v2-i18n-pilot.md` 同一基准);工具 `tools/v2_i18n_coverage.py`(与 `cli-go/internal/core/i18n.go` 门禁同语义)。
- 分支:`feat/v2-i18n-batch-component`;前置:`main`(`2cf2ab0a3`,rebase 基点;含试点 PR #7 的 ui/ 切片、PR #9 的 batch-rest、PR #10 的 batch-routes)。本批改动基线为 `e9fe86cd2`(PR #7 后),before/after 对拍均以该基线的资产副本为 before。

## ① 结论摘要(TL;DR)

1. **切片 = `packages/tui/src/component/` 的 `dialog-*` + `prompt/`**(29 个产品文件:23 个 `dialog-*.tsx` + `prompt/` 6 个;其中 `prompt/draft-stash.ts` 零界面串,28 个文件有锚点)。与试点 B1(`ui/`)同构度最高:都是对话框族,术语表与裁定规则(⑧)可直接复用。
2. **切片门禁 100%**:`apply --dry-run --strict --min-match-rate 1` 下,切片 28 个锚点文件 **363/363 条目全部命中**(本批前 65 条目、其中 3 个文件 ✗)。全局门禁(仅叠加本批改动,对拍基线 `e9fe86cd2`)**309/545 (56.7%) → 629/843 (74.6%)**,失败文件 **3 → 0**(原 3 个失败文件 `dialog-mcp`/`prompt/autocomplete`/`dialog-session-rename` 全在切片内,已全部修复);分支 rebase 到 `main` `2cf2ab0a3` 后(含已合入的 batch-rest/batch-routes 资产)全局门禁 **1273/1325 = 96.1%,失败文件 0**。**V1 门禁仍 497/497 = 100%**(apply --strict + verify 100.0%,V1 资产零改动)。
3. **死键规模比试点更大**:本批 27 个改动文件里 11 个是 V1 派生锚点,其中 **10 个含死键(共 22 条死键,另 2 条精确化替换、1 条恒等键清理)**,`dialog-mcp` 旧 7 条**全部**死键(v2.0.13 已整文件重写)。再次实证覆盖账本「200 条 migratable 需人工复核」的判断——V1 键直接迁移的死亡率约 33%(22/66)。
4. **本批新增 298 条锚点键(切片内 65 → 363)、22 组无 V1 先例新词**,全部先核 V1 词表再裁定(④);按试点 ⑧ 三类规则(提取器误报 / 按 V1 先例保持原文 / Tier B 代码位)逐条分账,切片 332 个 Tier A distinct **无一静默丢弃**(⑧-1)。

## ② 切片范围

| 项 | 值 |
|---|---|
| 切片 | `packages/tui/src/component/dialog-*.tsx` + `packages/tui/src/component/prompt/`(v2.0.13) |
| 产品文件 | 29 个:28 个 `.tsx`/`.ts` 有锚点 + `prompt/draft-stash.ts`(纯逻辑,零界面串,工具确认) |
| 串级口径 | Tier A(attr/prop/jsx-text/jsx-expr + 自然语言过滤),与覆盖账本/试点同口径 |
| 纳入 | 全部 Tier A distinct:covered / migratable / fuzzy-simple / new 四类都处置到位 |
| 排除(逐条说明) | Tier B(code 位:命令 id、开发者 throw、路径/模板串)——与试点一致,见 ⑧-1 |

## ③ 切片清单与条数(工具实测)

复现命令(只读):

```bash
cd cli-go && go build -trimpath -o /tmp/oc-batch/opencode-cli .   # 资产是 //go:embed 内嵌,改锚点必须重建
OPENCODE_SOURCE_DIR=<v2.0.13 检出> /tmp/oc-batch/opencode-cli apply --dry-run --strict --min-match-rate 1
python3 tools/v2_i18n_coverage.py --source-dir <v2.0.13 检出>    # 串级账本(before/after 对拍用 --assets-v2-dir 指向改动前资产副本)
```

**本批前切片账本(Tier A,多归属计口径;union 去重后合计 332)**:

| 类 | distinct |
|---|---|
| covered | 37 |
| migratable | 66 |
| fuzzy-simple | 21 |
| new | 212 |
| **合计** | **332** |

**本批后**:

| 类 | distinct | delta | 说明 |
|---|---|---|---|
| covered | 289 | **+252** | 含本批新译 + V1 迁移锚定 |
| migratable | 13 | −53 | 残余全部为保持原文或分类器盲区(⑧-1) |
| fuzzy-simple | 0 | −21 | 21 条全部裁定并锚定 |
| new | 32 | −180 | 残余全部为误报/保持原文/Tier B(⑧-1) |
| **合计** | **332** | 0 | union 不变,即**没有掩盖任何一条,只是把每一条分了类** |

## ④ 术语依据(全部先核 V1 词表,不自创)

术语核对来源:`cli-go/internal/core/assets/opencode-i18n/`(V1 词表)+ 现有 V2 资产(含试点 B1 已确立词条)。实证如下(均可在 V1 资产中 grep 到):

| 英文词 | 采用译法 | V1/V2 实证 |
|---|---|---|
| agent | 智能体 | V1 `Switch agent`→`切换智能体`;试点同 |
| session | 会话 | V1 `New session`→`新会话` |
| prompt | 提示 | V1 `category: "Prompt"`→`category: "提示"`;`Previous/Next prompt history`→`上一条/下一条提示历史` |
| workspace | **工作空间** | V1 `Manage workspaces`→`管理工作空间` |
| Stash | **存储**(非「暂存」) | V1 `title="Stash"`→`title="存储"`、`Stash pop`→`弹出存储`、`Stash list`→`存储列表` |
| Shell(模式名) | **命令行** | V1 `SHELL`→`命令行`;V2 `Exit shell mode`→`退出命令行模式` |
| model variant / variant | 模型变体 / 变体 | V1 `Switch model variant`→`切换模型变体` |
| Copy / Copy details | 复制 / 复制详情 | V1 `title: "Copy"`→`复制` |
| Restart / Update | 重新启动 / 更新 | V1 `Restart`→`重新启动`、`Update Available`→`有可用更新` |
| Current / Default / Delete | 当前 / 默认 / 删除 | V1 同键 |
| just now(相对时间) | 刚刚 | V1 `just now`→`刚刚` |
| 空态句式 | **暂无…** | V1 `No MCP Servers`→`暂无 MCP 服务器`(本批 `No worktrees available`→`暂无可用工作树`、`No experiments available`→`暂无实验功能`) |
| …加载中/搜索中 | 正在加载... / 正在搜索... | V1 `Loading skill…`→`正在加载技能...` |
| 确认类(Press … again to confirm) | 再次按 … 确认 | V1 `Press ${deleteHint()} again to confirm`→`再次按 ${deleteHint()} 确认` |
| 省略号 | ASCII 三点 `...` | V1 全表统一 |
| 键位提示(esc/enter/ctrl+d/ctrl+n/ctrl+a/shift+tab/left/right) | **保留英文** | V1 全表 497 条中 0 条翻译键位提示 |
| Markdown / JSON(格式名) | **保留英文** | V1 `save the conversation as Markdown`→`将对话保存为 Markdown` |
| TPS / OS / MCP / URL / URLs | **保留英文** | V1 `TPS`/`OS`/`MCP` 原样;V1 无 URL 译例 |

**无 V1 先例的新词(本批裁定,已按 V1 风格最小化发挥)**:

| 英文 | 译文 | 裁定理由 |
|---|---|---|
| integration / Connect an integration | 集成 / 连接集成 | V2 已把 `Connect provider` 改名为 `Connect an integration`;「集成」为插件/服务接入的标准译法 |
| Experiments(设置分类 + 弹窗) | 实验功能 | 直译;`group: "Experiments"` 同步为 `实验功能`(与试点 `group: "Dialog"`→`对话框` 同角色) |
| Pair(设备配对弹窗) | 配对 | 弹窗展示 URL + 用户名/密码供手机配对,「配对」无歧义 |
| This device | 本机 | 与 `Username`/`Password` 并列的本地信息标签 |
| Investigate error | 调查错误 | 错误详情弹窗的 i 键动作,「动词+对象」对齐 V1 句式 |
| Leader timeout | 前导键超时 | 键位设置项,「前导键」为 leader key 通译 |
| Tool grouping | 工具分组 | 设置项,直译 |
| Transcript images | 记录图片 | 会话记录(transcript)的图片,对齐 V1 `导出会话记录` 的「记录」 |
| Indicators(tab) | 指示器 | 页签状态指示(数字/图标),不用「指示灯」 |
| Window title | **终端标题** | V1 `Disable terminal title`→`禁用终端标题`(非「窗口标题」) |
| Large pastes | 大段粘贴 | 粘贴行为设置,「大段」比「大量」更贴切 |
| Color mode | 颜色模式 | 明暗主题设置,直译 |
| New session location | 新会话位置 | 会话创建位置设置 |
| Scope(tab) | 范围 | 页签分类,直译 |
| Tabs(category) | 页签 | 区别于 tab 键位提示(保留英文) |
| Alerts / Diffs / Input / Appearance / Terminal / Debug(分类名) | 提醒 / 差异 / 输入 / 外观 / 终端 / 调试 | 直译,均为分类标题 |
| Previous/Next value | 上一个值 / 下一个值 | 对齐试点 `Previous/Next item`→`上一个/下一个` 句式 |
| change(切换标签) | 切换 | 循环切换语境;V1 `change`→`更改` 用于文件更改,此处不用「更改」 |
| Queue prompt | 提示入队 | V1 `prompt.queue` 命令 id 的可见标题;「入队」为队列标准说法 |
| Background blocking tools | 后台阻塞工具 | 会话命令标题,直译 |
| Dismiss autocomplete | 关闭自动补全 | 与 V1 `Hide autocomplete`→`隐藏自动补全` 并列(关闭/隐藏分工) |
| Single patch | 单个补丁 | 差异视图设置 |

## ⑤ 批次译文样例表(供人眼验收,32 条)

均为 v2.0.13 实际源码串 → 本批译文;「锚点键」为写入 V2 资产的 find 串(节选)。

| # | 原文 | 译文 | 位置(v2.0.13) | 术语依据 |
|---|---|---|---|---|
| 1 | MCP servers | MCP 服务器 | dialog-mcp.tsx title | V1 `No MCP Servers`→`暂无 MCP 服务器` |
| 2 | Connecting … / Connected ✓ / Failed ! / Disabled ○ | 连接中... / 已连接 ✓ / 失败! / 已禁用 ○ | dialog-mcp.tsx Status() | V1「连接」词族 |
| 3 | enter to view error | 按 enter 查看错误 | dialog-mcp.tsx footer | 键位保留 |
| 4 | MCP server: ${server().name} | MCP 服务器: ${server().name} | dialog-mcp.tsx title | V1 冒号风格 |
| 5 | No MCP servers / {mcp().length} MCP server{…} | 暂无 MCP 服务器 / {mcp().length} MCP 服务器 | dialog-status.tsx | V1 空态句式 + 复数三元折叠 |
| 6 | Delete worktree? | 删除工作树? | dialog-workspaces.tsx | V1 `Copy worktree path`→`复制工作树路径` |
| 7 | Worktrees | 工作树 | dialog-workspaces.tsx 标题 ×2 | V1 同词 |
| 8 | Press {…} again to confirm | 再次按 {…} 确认 | dialog-workspaces.tsx titleView | V1 逐字同键 |
| 9 | No worktrees available | 暂无可用工作树 | dialog-workspaces.tsx 空态 | V1「暂无」句式 |
| 10 | Experiments | 实验功能 | dialog-experiments.tsx 标题 | 新词(④) |
| 11 | Previous value / Next value | 上一个值 / 下一个值 | dialog-experiments.tsx keymap | 新词(④) |
| 12 | Copy debug info | 复制调试信息 | dialog-debug.tsx keymap | V1 `Copy`→`复制` |
| 13 | label: "Version"/"Date"/"Terminal"/"Session ID"/"Model" | 版本 / 日期 / 终端 / 会话 ID / 模型 | dialog-debug.tsx 信息表 | V1 同词 |
| 14 | Share this when reporting an issue. | 报告问题时请分享此信息。 | dialog-debug.tsx 说明行 | 直译 |
| 15 | Back / Copy details / Investigate error | 返回 / 复制详情 / 调查错误 | dialog-error-details.tsx keymap | 试点「返回」+ V1「复制」+ 新词 |
| 16 | ↑/↓ scroll | ↑/↓ 滚动 | dialog-error-details.tsx footer | 直译 |
| 17 | Could not refresh {…}. | 无法刷新{…}。 | dialog-open.tsx 错误态 | 直译 |
| 18 | Search sessions and projects… | 搜索会话和项目... | dialog-open.tsx placeholder | V1「会话」+ ASCII 省略号 |
| 19 | Open | 打开 | dialog-open.tsx 标题(三元尾) | 直译 |
| 20 | Category: "Sessions"/"Projects" | 会话 / 项目 | dialog-open.tsx category | V1 `category: "Session"`→`会话` |
| 21 | Loading worktrees failed | 加载工作树失败 | dialog-open.tsx toast | 直译 |
| 22 | Update successful! A restart is required. | 更新成功!需要重新启动。 | dialog-update.tsx | V1 `Restart`→`重新启动` |
| 23 | OpenCode is already up to date. | OpenCode 已是最新版本。 | dialog-update.tsx | 直译 |
| 24 | Username / Password | 用户名 / 密码 | dialog-pair.tsx | 直译 |
| 25 | Run `opencode service set hostname 0.0.0.0` to access the service remotely. | 执行 `opencode service set hostname 0.0.0.0` 以远程访问服务。 | dialog-pair.tsx | 命令原文保留 |
| 26 | Session title / Rename session | 会话标题 / 重命名会话 | dialog-session-rename.tsx | V1「会话」+ 直译 |
| 27 | Confirm autocomplete action | 确认自动补全操作 | prompt/autocomplete.tsx keymap | V1 `Confirm`→`确认` + `Select autocomplete item`→`选择自动补全项` |
| 28 | No matching files, agents, or references | 没有匹配的文件、智能体或引用 | prompt/autocomplete.tsx 空态 | V1「智能体」 |
| 29 | Stash prompt / Stash pop / Stash list | 存储提示 / 弹出存储 / 存储列表 | prompt/index.tsx 命令 | V1 逐字同键 |
| 30 | Exit shell mode | 退出命令行模式 | prompt/index.tsx ×3 | V1 `SHELL`→`命令行` |
| 31 | Background blocking tools | 后台阻塞工具 | prompt/index.tsx 命令 | 新词(④) |
| 32 | Manage workspaces | 管理工作空间 | prompt/index.tsx 命令 title/desc | V1 逐字同键 |

另有多条未列入上表但已同批锚定:`group: "Dialog"`→`group: "对话框"`(切片 8 个文件 15 处)、`group: "Autocomplete"`→`自动补全`(7 处)、`group: "Experiments"`→`实验功能`(2 处)、`format: (value) => \`${value} ms\``→`\`${value} 毫秒\``(dialog-debug)、`labels: ["off", "on"]`→`["关", "开"]`、`? "on" : "off"`→`? "开" : "关"`(dialog-experiments/skill)、`Attachment does not exist`/`Attachment exceeds the local file limit`→`附件不存在`/`附件超出本地文件限制`(prompt/local-attachment throw)、`Shell`→`命令行`(prompt/metadata agent 标签)。

## ⑥ 锚点资产改动明细(只动 V2)

27 个文件(11 个修改 + 16 个新建)+ `dialog-theme-list` 原样保留,共 **363 条条目**(本批前同范围 65 条):

| 锚点文件 | 条目 | 改动 |
|---|---|---|
| packages-tui-src-component-dialog-config.tsx.json | 49 | **新建**:设置弹窗全部 title/desc/keywords 位 |
| packages-tui-src-component-prompt-index.tsx.json | 48 | 15 → 48:删 2 键(1 死键 + 1 恒等键),补 `category: "Session"`→会话 4 处等 |
| packages-tui-src-component-dialog-integration.tsx.json | 46 | 4 → 46:provider→integration 改名全量重锚 |
| packages-tui-src-component-dialog-open.tsx.json | 27 | **新建** |
| packages-tui-src-component-dialog-shell-output.tsx.json | 20 | **新建** |
| packages-tui-src-component-dialog-session-list.tsx.json | 17 | 5 → 17:删 1 死键,补三元对/titleView |
| packages-tui-src-component-dialog-workspaces.tsx.json | 17 | **新建** |
| packages-tui-src-component-dialog-mcp.tsx.json | 15 | 7 → 15:**旧 7 条全部死键**,按重写后的源码重锚 |
| packages-tui-src-component-prompt-autocomplete.tsx.json | 14 | 1 → 14:删 1 死键,按分类空态重锚 |
| packages-tui-src-component-dialog-update.tsx.json | 12 | **新建** |
| packages-tui-src-component-dialog-debug.tsx.json | 11 | **新建** |
| packages-tui-src-component-dialog-error-details.tsx.json | 9 | **新建** |
| packages-tui-src-component-dialog-image-preview.tsx.json | 8 | **新建** |
| packages-tui-src-component-dialog-pair.tsx.json | 8 | **新建** |
| packages-tui-src-component-dialog-stash.tsx.json | 8 | 8 → 8:`Press ${deleteHint()}` 死键按新源码重锚(`shortcuts.get("stash.delete")` 形态)+ `delete` 精确化为 `title: "delete"`,净持平 |
| packages-tui-src-component-prompt-move.tsx.json | 8 | **新建** |
| packages-tui-src-component-dialog-experiments.tsx.json | 7 | **新建** |
| packages-tui-src-component-dialog-model.tsx.json | 7 | 8 → 7:删 2 死键(integration 改名),新增 1 键重锚 `Connect an integration`/`View all integrations`;Favorites/Recent/Select model 经复核为活键,保留并翻译 |
| packages-tui-src-component-dialog-skill.tsx.json | 6 | 4 → 6:删 2 死键 |
| packages-tui-src-component-dialog-status.tsx.json | 6 | 9 → 6:删 6 键(5 死键 + `Needs authentication` 精确化为模板键),新增复数三元/空态 3 键 |
| packages-tui-src-component-dialog-worktree-name.tsx.json | 6 | **新建** |
| packages-tui-src-component-dialog-session-rename.tsx.json | 3 | 1 → 3:删 1 死键,重锚 placeholder |
| packages-tui-src-component-dialog-workspace-file-changes.tsx.json | 3 | **新建** |
| packages-tui-src-component-dialog-variant.tsx.json | 2 | **新建** |
| packages-tui-src-component-prompt-local-attachment.ts.json | 2 | **新建** |
| packages-tui-src-component-prompt-metadata.tsx.json | 2 | **新建** |
| packages-tui-src-component-dialog-agent.tsx.json | 1 | 2 → 1:删 1 死键(`native` 提取器误报) |
| packages-tui-src-component-dialog-theme-list.tsx.json | 1 | 1 → 1:原样保留 |
| **合计** | **363** | 11 改 + 16 新(键 65 → 363,+298) |

**失效锚点处理(22 条死键,逐一在 v2.0.13 源码 grep 证实不存在;另 2 条精确化替换、1 条恒等键清理)**:

| 文件 | 死键 |
|---|---|
| dialog-mcp | 旧 7 条全死(`>⋯ Loading</span>`、`>○ Disabled</span>`、`>✓ Enabled</span>`、两条 `console.error`、`title: "toggle"`、`title="MCPs"`) |
| dialog-status | `Formatters`、`LSP Servers`、`MCP Servers`、`No Formatters`、`No MCP Servers`(计数器重构) |
| dialog-model | `category: "Popular providers"`、`title: connected() ? "Connect provider" : "View all providers"`(integration 改写) |
| dialog-skill | `category: "Skills"`、`placeholder="Search skills…"` |
| dialog-stash / dialog-session-list | `` `Press ${deleteHint()} again to confirm` ``(v2.0.13 改为 `shortcuts.get("stash.delete")`/`shortcuts.get("session.delete")` 形态,已按新源码重锚) |
| dialog-session-rename | `title="Rename Session"` |
| prompt-autocomplete | `<text fg={theme.textMuted}>No matching items</text>` |
| prompt-index | `message: "Connect a provider to send prompts"`(provider→integration) |
| dialog-agent | `native`(提取器误报,源码从未存在) |

**精确化替换 2 处(旧键未死但升级为更稳的形态)**:① dialog-stash 的裸 `delete` 改锚 `title: "delete"`(裸 `delete` 是简单词,`\b` 会误伤 `stash.delete` 命令 id);② dialog-status 的裸 `Needs authentication` 改锚模板键 `` `Needs authentication: ${val().error}` ``(v2.0.13 该文案已是模板串)。另清理 1 条恒等键:prompt-index 的 `placeholder={placeholderText()}`(原为恒等映射无实义,占位串由 `Ask anything… "..."`/`Run a command… "..."` 两个模板键承接)。

**精确键/行内键(替代裸词,避免误伤代码位)**:

| 文件 | 键 | 理由 |
|---|---|---|
| dialog-stash / dialog-session-list | `title: "delete"` | 裸 `delete` 是简单词,`\b` 会误伤 `stash.delete`/`session.delete` 命令 id |
| dialog-debug | `? "✓ copied" : "copy"` | 裸 `copy` 会命中 `run: copy` 标识符与 `onMouseUp={copy}` |
| dialog-status | ` MCP server{mcp().length === 1 ? "" : "s"}` | 复数三元整键替换,避免残留英文 `s` |
| dialog-config | `format: (value) => \`${value} ms\`` | 行内模板,直改模板串 |
| dialog-workspace-file-changes | `theme.text.muted}>{item}</text>` | 三元内 `"yes"`/`"no"` 值翻译,不动外层 JSX |
| prompt/index | `? "sessions and projects" : "sessions") : "projects"}.` | 嵌套三元整键替换 |

**真 apply 验证**(临时真复制树 `cp -a` 实跑非 dry-run,切片 28 个源码文件共 443 行 diff 逐行复核):全部按上表替换,无级联误伤。重点复核项:① `dialog-config` 49 键的 keywords/values 代码位零误伤;② `dialog-mcp` 的 `MCP 服务器` 与 `MCP server: ${...}` 长短键正确分流;③ `dialog-open` 两处 `New worktree`/`new worktree`(大小写不同)分别命中且不互相污染;④ `dialog-status` 的 `暂无 MCP 服务器`(fallback)与 `{mcp().length} MCP 服务器`(复数三元)互不覆盖;⑤ `prompt/index` 48 键的 command id(`prompt.*`/`session.*`/`extmark.*`)零误伤;⑥ `dialog-debug` 的 `? "✓ copied" : "copy"` 未破坏 `run: copy`/`onMouseUp={copy}` 标识符。

**反向还原自检**:对 28 个锚点文件做「译文→原文」反向替换并与 v2.0.13 原文件比对,仅 2 处因「两个键共用一个译文」的反向歧义报差异(dialog-status 的 `暂无 MCP 服务器`、dialog-open 的两处 worktree 标题),正向 apply 结果经 diff 复核均正确。

## ⑦ 复量数字

| 门禁 | 本批前(基线 `e9fe86cd2`) | 本批后(仅叠加本批) | 最终分支(rebase 到 `main` `2cf2ab0a3`,含已合入的 batch-rest/batch-routes) |
|---|---|---|---|
| **切片门禁**(apply --dry-run --strict --min-match-rate 1,切片 28 文件) | 12 个文件 65 条:2 个全命中,7 个部分命中,**3 个 ✗**(dialog-mcp / prompt-autocomplete / dialog-session-rename) | **363/363 = 100%**(28 个文件逐行 `N/N 处替换`,0 文件 ✗) | **363/363 = 100%**(不变) |
| **全局门禁**(同命令,全资产) | 309/545 = 56.7%(失败文件 3,均在切片内) | **629/843 = 74.6%**(失败文件 **0**) | **1273/1325 = 96.1%**(失败文件 **0**) |
| **V1 门禁**(OPENCODE_SOURCE_DIR=V1 检出 `f54ce31`,apply --strict + verify --dry-run) | 497/497 = 100% | **497/497 = 100%**(零改动,复跑确认) | **497/497 = 100%**(复跑确认) |

条目级资产规模:锚点文件 67 → 83 个(仅本批),键 545 → 843 条(切片内 65 → 363 条;门禁分母即键总数,两个数字严格对应);rebase 后全资产 129 文件 / 1325 键。

串级账本(Tier A,同一脚本 before/after 对拍;before 用 `--assets-v2-dir` 指向改动前资产副本;判定口径:值归一化后按「任一处命中即计入该类」多归属计,union 为去重分母):

| 类 | 切片 before | 切片 after | 主宇宙 before | 主宇宙 after(最终分支) |
|---|---|---|---|---|
| covered | 37 | **289** | 251 | **1067** |
| migratable | 66 | 13 | 204 | 117 |
| fuzzy-simple | 21 | 0 | 82 | 7 |
| new | 212 | 32 | 882 | 232 |
| **union(分母)** | **332** | **332** | **1360** | **1360** |

迁移天花板(covered ∪ migratable):切片 103/332 = 31.0% → **302/332 = 90.9%**;主宇宙 455/1360 = 33.5% → **1184/1360 = 87.1%**(最终分支数字含已合入的 batch-rest/batch-routes 成果;仅本批贡献为主宇宙 covered 251 → 482、new 882 → 721)。(union 分母不变,再次证明没有掩盖任何一条。)

## ⑧ 质量自评

### 8.1 逐条裁定:切片 332 个 Tier A distinct 的完整分账

| 处置 | distinct | 内容 |
|---|---|---|
| **有中文译文(covered)** | 289 | 37 个本批前已覆盖 + 252 个本批产出 |
| **按规则保持原文(V1 先例)** | 12 | 键位提示 `esc`/`enter`/`ctrl+n`/`ctrl+a`/`shift+tab`/`left`/`right`(7,V1 全表 0 条先例);格式名/技术名 `Markdown`/`OS`/`MCP`/`TPS`/`URLs`(5,V1 先例保留英文) |
| **提取器误报(程序化值/枚举)** | 17 | `center`/`column`/`flex-end`/`flex-start`/`row`/`bottom`/`left`/`right`(flex/wrapMode/scroll 枚举)、`autoaccept`/`needs_auth`/`checking`/`pending`/`running`/`normal`/`default`(store/status 比较子)、`connected`/`disabled`/`failed`(dialog-status 的 `item.status.status === "…"` 比较,渲染走 Match 分支已译)、`string`(类型比较误捕) |
| **Tier B 代码位(命令 id)** | 8 | `dialog.integration.rename`、`dialog.mcp.toggle`、`model.dialog.favorite`、`model.dialog.provider`、`session.pin.toggle`、`session.rename`、`dialog.move_session.new`、`dialog.move_session.refresh` |
| **模板串/动态插值(无可译散文)** | 8 | `$${connection.name}`、`[${selected.includes(option.value) ? "x" : " "}] ${option.label}`、`${label ? \`${Locale.truncate(label, 30)} · \` : ""}${timeAgo(session.time.updated)}`、`${truncateFilePath(footer, width)}${git ? " →" : ""}`、`${reference.source.type === "git" ? … : …}`、`@${referenceMatchValue.name}`、`@${skill}`、`prompt-image-preview-${index()}` |

合计 289 + 12 + 17 + 8 + 8 = 334,其中 2 个为跨类重复值(`left`/`right` 同时出现在键位提示与 flex 枚举两类),去重后 **332**,与 union 分母一致——**没有任何一条被静默丢弃**。

### 8.2 术语一致性

全部新译文先核 V1 词表(④);26 组无 V1 先例新词逐个给出裁定理由,优先复用 V2/试点已在用词(对话框/剪贴板/确认/取消/搜索/提交/暂无句式/正在…中)。**未发现与 V1 冲突的译法**;三处「易错点」按实证纠正:① workspace 用「工作空间」而非「工作区」;② Stash 用「存储」而非「暂存」;③ Shell 模式用「命令行」而非「外壳」(V1 `SHELL`→`命令行`)。

### 8.3 已知限制(需上游或后续批次处理)

1. **dialog-config 的 10 个无 labels 设置**(Sidebar / Thinking / Markdown / Tool grouping / Mode / Layout×2 / Wrapping / Large pastes / Copy behavior / Color mode):footer 显示原始枚举值(`system`/`dark`/`light`/`rendered`/`source`…)。这是上游产品设计(程序化值按试点规则不翻),中文用户会看到英文枚举。**属上游待改进项**,不宜用锚点硬改(会把 `values` 代码位一起改坏)。
2. **dialog-config 的 `keywords` 数组**是设置项搜索索引(代码位),按试点口径不翻;因此设置弹窗的搜索功能只能按英文关键词命中。
3. **dialog-open 的紧凑相对时间**(`5m`/`2h`/`3d`):V1 用「分钟前/小时前/天前」完整词,此处为宽度受限的 footer 紧凑格式,V1 无先例,仅 `just now`→`刚刚` 按 V1 先例翻译,紧凑格式保持原样。
4. **dialog-session-list 的 `throw new Error("Location unavailable")`** 不显示给用户(searchState 用通用 message 覆盖),按 Tier B 不翻。
5. **dialog-status 的 fallback** 会显示原始 status 字符串(如 `pending`):该状态为瞬态,Switch 的 4 个分支(已连接/失败/已在配置中禁用/需要认证)均已译,fallback 无 V1 先例且属协议枚举值。

### 8.4 与覆盖账本/试点的互相验证

- 账本「migratable 需人工复核」在本批再次实证:切片 66 个 migratable 值中 22 条为死键(约 33%),且 `dialog-mcp` 旧锚点 **100% 死亡**(整文件重写)。B3-B7 批次应预留同比例复核工时。
- 试点 ⑧ 的三类裁定规则(提取器误报 / 按 V1 先例保持原文 / Tier B 代码位)在本批 332 条上完整复用,残差 45 条全部落在这三类里,无第四类。
- `group: "Dialog"`→`group: "对话框"`:v2.0.13 全源码共 42 处(ui/ 26 + component/ 15 + feature-plugins/prompt/btw.tsx 1)。试点已覆盖 ui/ 的 26 处,本批覆盖 component/ 的 15 处(8 个文件),仅剩 B5 的 btw.tsx 1 处。若上游改名(如 "Dialogs"),门禁立刻失败报警——期望行为(漂移检测),按 nightly 流程修键即可。

## ⑨ 剩余批次(接试点 ⑨,不变)

| 批次 | 范围 | 状态 |
|---|---|---|
| B1 ✅ | `tui/src/ui/` | 已完成(试点 PR #7) |
| **B2 ✅** | **`tui/src/component/dialog-*` + `component/prompt/`** | **本批:363 条目 / 切片门禁 100% / 最终分支全局 96.1% / 0 失败** |
| B3 | `tui/src/routes/session/` | 待做(~270 distinct) |
| B4 | `tui/src/mini/` + `routes/` 其余 + `app.tsx` | 待做(~239) |
| B5 | `tui/src/feature-plugins/` | 待做(~207) |
| B6 | `tui/src/component/` 其余(`command-palette.tsx`、`error-component.tsx`、`dialog-provider.tsx`、`dialog-tag.tsx`)+ `config/` + `util/` + `context/` | 待做(~175);注:`dialog-provider.tsx`/`dialog-tag.tsx` 在 v2.0.13 已不存在,其 17 条 V1 派生锚点是 deferred 死锚,B6 可顺手清 |
| B7 | `cli/src/` | 待做(~106) |
| B8 | Tier B(错误/日志裸文案) | 独立工作流,建议 Tier A 全完后再开 |

## ⑩ 合规自查

- 只改 V2:`git status` 仅 `cli-go/internal/core/assets/opencode-i18n-v2/anchors/` 下 27 个文件(11 改 16 增)+ `config.json`(仅 `manifest.manualNotes` 追加 18 条)+ 本文档;V1 词表/注入脚本/门禁/workflow 零改动(V1 门禁复跑 497/497 + verify 100.0% 实证)。
- 未改 `.github/`、未改产品代码、未推 upstream、未触碰 `/root/xiangmudata_sync/opencode-v2-cn/`;未做范围外目录(B3-B8 的串只列清单未翻)。
- `cli-go` 全部单测通过(`go test ./...`:cmd + internal/core ok),含 `TestEmbeddedV2AssetsCoverEveryV1Entry`(V1 497 条目在 V2 manifest 无丢失)与 `config.json 不作规则加载` 断言。
- 复现确定性:文中所有数字来自真实命令输出(v2.0.13 检出 + 仓库资产重建的 cli + 同一脚本 before/after 对拍),无硬编;JSON 资产均通过 `json.load` 校验。
