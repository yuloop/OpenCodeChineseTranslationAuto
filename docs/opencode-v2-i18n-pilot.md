# opencode V2 汉化 · 试点报告(`packages/tui/src/ui/` 切片)

- 日期:2026-09-22
- 性质:**小切片真翻译试点**。只新增/修改 `cli-go/internal/core/assets/opencode-i18n-v2/` 资产;未改 V1 任何文件(词表/注入脚本/门禁/workflow)、未改 `.github/`、未改产品代码、未推 upstream、未触碰 `/root/xiangmudata_sync/opencode-v2-cn/`。
- 测量基准:上游 `anomalyco/opencode` tag **`v2.0.13`**(commit `3180aab16e050128678e590afcbd2dc85c259cb7`,与覆盖账本 `docs/opencode-v2-i18n-coverage.md` 同一基准);工具 `tools/v2_i18n_coverage.py`(复用 `tools/v2spike_probe.py` 的判定,与 `cli-go/internal/core/i18n.go` 门禁同语义)。
- 分支:`feat/v2-i18n-pilot`;PR:[yuloop/OpenCodeChineseTranslationAuto#7](https://github.com/yuloop/OpenCodeChineseTranslationAuto/pull/7)(merge commit `fed5de2d`)。

## ① 结论摘要(TL;DR)

1. **试点切片 = `packages/tui/src/ui/`**(对话框基础设施族:8 个 dialog 组件 + toast + 工作目录操作 + 路径/链接/分隔条辅助)。选它的理由:① 最小有代表——DialogSelect/Toast/Dialog 是全部终端 UI 的公共底座,会话路由、命令面板、各业务 dialog 都复用;② 用户天天看得到——帮助对话框、导出选项、各种确认框、toast;③ 条数适中——Tier A distinct 90 条,一个切片就能走完「列清单→核术语→翻译→锚定→复量→验收」全流程。
2. **切片门禁 100%**:`apply --dry-run --strict --min-match-rate 1` 下,切片 10 个锚点文件 **61/61 条目全部命中**(试点前 6/17 = 35.3%,其中 2 个文件 ✗)。全局门禁 **252/501 (50.3%) → 309/545 (56.7%)**,失败文件 5 → 3(余 3 个均在切片外:dialog-mcp / dialog-session-rename / prompt-autocomplete)。**V1 门禁仍 497/497 = 100%**(apply --strict)+ verify 100.0%,V1 资产零改动。
3. **工作量实测量级**:本试点产出 45 条新译文 + 13 条失效锚点修复 + 61 条锚点条目,单人单会话完成——验证了覆盖账本 ⑦「100 条/人天(带上下文人工翻译+复核)」的速率估计,可按此外推全量。
4. **一个必须写进方法的发现**:切片内 90 个 Tier A distinct 串中,只有 60 个是「该翻的」;其余 30 个是**提取器误报(程序化值:枚举/命令 id/trait 状态,12 条)、按 V1 先例保持原文(键位提示/格式名/符号,6 条)、Tier B 代码位(12 条)**。试点把这三类的逐条裁定规则固化了(见 ⑧),全量执行时每批都必须带同样的裁定表,否则「门禁 100%」会被误报项拖成永远不可达。

## ② 试点范围

| 项 | 值 |
|---|---|
| 切片 | `packages/tui/src/ui/`(v2.0.13) |
| 产品文件 | 21 个:13 个 `.tsx`(含 link.tsx,零界面串)+ 8 个 `.ts` 辅助文件(animation/border/layout/one-cell-motion/pane-resize/select-controller/spinner/subcell),后两类经工具确认**零界面串** |
| 串级口径 | Tier A(attr/prop/jsx-text/jsx-expr + 自然语言过滤),与覆盖账本主数字同口径 |
| 纳入 | 全部 Tier A distinct:covered / migratable / fuzzy-simple / new 四类都处置到位 |
| 排除(逐条说明) | Tier B(code 位:命令 id、开发者 throw 文案、路径模板)——试点范围外,见 ⑧-3 |

## ③ 切片清单与条数(工具实测)

复现命令(只读):

```bash
# 切片 new 串清单(复用覆盖账本工具的分类逻辑,按文件族过滤)
python3 tools/v2_i18n_coverage.py --source-dir <v2.0.13 检出>   # 全局账本
# 条目级门禁(切片 10 文件逐行输出)
cd cli-go && go build -trimpath -o /tmp/oc-pilot/opencode-cli .
OPENCODE_SOURCE_DIR=<v2.0.13 检出> /tmp/oc-pilot/opencode-cli apply --dry-run --strict --min-match-rate 1
```

**试点前切片账本(Tier A)**:

| 类 | occurrences | distinct |
|---|---|---|
| covered | 12 | 9 |
| migratable | 44 | 14 |
| fuzzy-simple | 8 | 8 |
| new | 76 | 59 |
| **合计** | **140** | **90** |

**试点后**:

| 类 | occurrences | distinct | 说明 |
|---|---|---|---|
| covered | 92 | 58 | +49 occ / +49 distinct |
| migratable | 7 | 6 | 残余均为保持原文或分类器盲区(见 ⑧) |
| fuzzy-simple | 0 | 0 | 8 条全部裁定并锚定 |
| new | 41 | 26 | 残余全部为误报/保持原文/Tier B(见 ⑧) |

distinct 合计不变(90),即:**没有掩盖任何一条,只是把每一条分了类**。

## ④ 术语依据(全部先核 V1 词表,不自创)

术语核对来源:`cli-go/internal/core/assets/opencode-i18n/`(V1 词表)+ 现有 V2 资产。实证如下(键 → 译文,均可在 V1 资产中 grep 到):

| 英文词 | 采用译法 | V1/V2 实证 |
|---|---|---|
| agent | 智能体 | V1 `Agent`→`智能体`(cli-footer-command)、`Switch agent`→`切换智能体` |
| model | 模型 | V1 `Switch model`→`切换模型` |
| tool | 工具 | V1 `Override global tool settings per agent configuration`→`…工具权限` |
| prompt | 提示 | V1 `category: "Prompt"`→`category: "提示"`、`Submit prompt`→`提交提示` |
| workspace | **工作空间**(非「工作区」) | V1 `Manage workspaces`→`管理工作空间`;V2 `config/keybind.ts` 锚点同 |
| session | 会话 | V1 `New session`→`新会话` |
| clipboard | 剪贴板 | V1 `Copied to clipboard`→`已复制到剪贴板` |
| dialog | 对话框 | V2 `to show the help dialog`→`显示帮助对话框` |
| Page up / Page down | 向上翻页 / 向下翻页 | V1 `title: "Page up"`→`title: "向上翻页"`(逐字同键) |
| Copy / Export | 复制 / 导出 | V1 `title: "Copy"`→`复制`、`Export session transcript`→`导出会话记录` |
| Confirm / Cancel | 确认 / 取消 | V1 cli-permission.json;V2 `util/permission.ts` 锚点同 |
| Search / Enter text / Enter filename | 搜索 / 输入文本 / 输入文件名 | V1 dialog-select/dialog-prompt/dialog-export |
| Include thinking | 包含思考过程 | V1 dialog-export.json 逐字同键 |
| No results found / 空态句式 | 未找到结果 / **暂无…** | V1 `No results found`→`未找到结果`;`No MCP Servers`→`暂无 MCP 服务器` |
| Markdown / JSON(格式名) | **保留英文** | V1 `save the conversation as Markdown`→`将对话保存为 Markdown`(格式名不译) |
| 省略号 | ASCII 三点 `...` | V1 `Loading skill…`→`正在加载技能...` |
| 键位提示(esc / esc/enter) | **保留英文** | V1 全表 497 条中 0 条翻译键位提示 |

**无 V1 先例的新词(本试点的裁定,已按 V1 风格最小化发挥)**:

| 英文 | 译文 | 裁定理由 |
|---|---|---|
| Back | 返回 | 标准导航词,V1 无相反译例 |
| Close / Close dialog / Close help | 关闭 / 关闭对话框 / 关闭帮助 | V2 已有 `close OpenCode`→`关闭 OpenCode`、`显示帮助对话框` |
| Dialog(keymap group 标签) | 对话框 | group 在命令面板渲染为分类标题,与 V2 `category: "Suggested"`→`"建议"` 同角色 |
| item 导航(Previous/Next/First/Last item) | 上一个 / 下一个 / 第一个 / 最后一个 | 对齐 V1 `title: "上一条消息"`→`下一条/第一条/最后一条` 句式 |
| Select item | 选择当前项 | 对齐 V1 `Select autocomplete item`→`选择自动补全项`(选择+对象) |
| section(Previous/Next section) | 上一个分组 / 下一个分组 | DialogSelect 的 section 即 category 分组 |
| dialog action / dialog option | 操作 / 选项 | 区分 footer 动作按钮与左右选项,不用「对话框操作」冗长形式 |
| Submit dialog prompt | 提交输入 | V1 的 prompt=提示指对话提示;此处是对话框文本输入,意译避免歧义 |
| Working… / processing… | 处理中... | 对齐 V1 `Loading skill…`→`正在加载技能...` 风格 |
| Export as: | 导出为: | 直译;ASCII 冒号对齐 V1 译文标点风格 |
| Export session / Session exported | 导出会话 / 会话已导出 | 词素对齐 V1 `导出会话记录`/`会话已导出到 ${filename}` |
| Sanitize sensitive data | 脱敏敏感数据 | 「脱敏」为数据安全标准术语,V1 无先例;与相邻两项保持「动词+对象」平行结构 |
| No items available | 暂无可用项 | 对齐 V1 空态「暂无」句式 |
| +N more | +N 更多 | toast 队列计数,保留 `+N` 数字前缀 |
| Working directory / Copy path / Open folder | 工作目录 / 复制路径 / 打开文件夹 | V1 `Copy worktree path`→`复制工作树路径`、`Open docs`→`打开文档` |
| in system file manager / to another working directory | 在系统文件管理器中 / 到另一个工作目录 | 状语成分,按中文语序前置 |

## ⑤ 试点译文样例表(供人眼验收,28 条)

均为 v2.0.13 实际源码串 → 本试点译文;「锚点键」为写入 V2 资产的 find 串(节选)。

| # | 原文 | 译文 | 位置(v2.0.13) | 术语依据 |
|---|---|---|---|---|
| 1 | Help | 帮助 | dialog-help.tsx 标题 | V1 同键 |
| 2 | Close help | 关闭帮助 | dialog-help.tsx keymap ×2 | V2「关闭」先例 |
| 3 | Press {…} to see all available actions and commands in any context. | 按 {…} 查看所有可用的操作和命令。 | dialog-help.tsx 说明行 | V1 同句(插值保留) |
| 4 | Close dialog | 关闭对话框 | dialog.tsx keymap ×2 | V2「对话框」 |
| 5 | Close export result | 关闭导出结果 | dialog-export-result.tsx keymap | 新词(见 ④) |
| 6 | Session exported | 会话已导出 | dialog-export-result.tsx 标题 | V1「会话已导出到」 |
| 7 | Export session | 导出会话 | dialog-export-options.tsx 标题 | V1「导出会话记录」 |
| 8 | Export as: | 导出为: | dialog-export-options.tsx | 直译 |
| 9 | Copy | 复制 | dialog-export-options.tsx 按钮 | V1 同键 |
| 10 | Export | 导出 | dialog-export-options.tsx 按钮 | V1 同词 |
| 11 | Include thinking | 包含思考过程 | dialog-export-options.tsx | V1 逐字同键 |
| 12 | Include tools | 包含工具 | dialog-export-options.tsx | V1「包含工具详情」同族 |
| 13 | Sanitize sensitive data | 脱敏敏感数据 | dialog-export-options.tsx | 新词(见 ④) |
| 14 | Previous item | 上一个 | dialog-select.tsx keymap | V1「上一条消息」句式 |
| 15 | Next item | 下一个 | dialog-select.tsx keymap | 同上 |
| 16 | First item | 第一个 | dialog-select.tsx keymap | V1「第一条消息」 |
| 17 | Last item | 最后一个 | dialog-select.tsx keymap | V1「最后一条消息」 |
| 18 | Select item | 选择当前项 | dialog-select.tsx keymap | V1「选择自动补全项」 |
| 19 | Page up | 向上翻页 | dialog-select.tsx keymap | V1 逐字同键 |
| 20 | Page down | 向下翻页 | dialog-select.tsx keymap | V1 逐字同键 |
| 21 | Back | 返回 | dialog-select/prompt.tsx keymap | 新词(见 ④) |
| 22 | Previous section / Next section | 上一个分组 / 下一个分组 | dialog-select.tsx keymap | 新词(见 ④) |
| 23 | Next dialog action / Previous dialog action | 下一个操作 / 上一个操作 | dialog-select.tsx keymap | 新词(见 ④) |
| 24 | Previous dialog option / Next dialog option | 上一个选项 / 下一个选项 | dialog-confirm.tsx keymap | 新词(见 ④) |
| 25 | Confirm alert | 确认提示 | dialog-alert.tsx keymap | V1「确认」 |
| 26 | Confirm dialog selection | 确认当前选择 | dialog-confirm.tsx keymap | V1「确认」+ 自然语序 |
| 27 | Submit dialog prompt | 提交输入 | dialog-prompt.tsx keymap | 意译(见 ④) |
| 28 | Working directory / Copy path / Open folder / Workspaces | 工作目录 / 复制路径 / 打开文件夹 / 工作空间 | working-directory-actions.tsx | V1「复制工作树路径」「管理工作空间」 |

另有多条未列入上表但已同批锚定:`in system file manager`→`在系统文件管理器中`、`to another working directory`→`到另一个工作目录`、`Path copied to clipboard`→`路径已复制到剪贴板`、`No items available`→`暂无可用项`、`Working…`/`processing…`→`处理中...`、`+N more`→`+N 更多`、`ok`→`确定`(重锚)、`submit`→`提交`(重锚)、`group: "Dialog"`→`group: "对话框"`(8 个文件 26 处)、`cancel`/`confirm` 回退标签→`取消`/`确认`(精确键)。

## ⑥ 锚点资产改动明细(只动 V2)

10 个文件(6 个修复+扩展,4 个新建),共 61 条条目:

| 锚点文件 | 条目 | 改动 |
|---|---|---|
| packages-tui-src-ui-dialog-alert.tsx.json | 3 | 删 1 死键(`theme.selectedListItemText` 形态),新增 title/ok/group |
| packages-tui-src-ui-dialog-confirm.tsx.json | 5 | **新建**:3 title + group + cancel/confirm 精确键 |
| packages-tui-src-ui-dialog-export-options.tsx.json | 10 | 删 8 死键(V1 导出对话框形态),保留 `Include thinking`,新增 9 |
| packages-tui-src-ui-dialog-export-result.tsx.json | 4 | **新建** |
| packages-tui-src-ui-dialog-help.tsx.json | 5 | 删 2 死键,新增 5 |
| packages-tui-src-ui-dialog-prompt.tsx.json | 7 | 删 1 死键(`theme.textMuted` 无点形态),保留 placeholder,新增 6 |
| packages-tui-src-ui-dialog-select.tsx.json | 16 | 删 1 死键,保留 placeholder,新增 15 |
| packages-tui-src-ui-dialog.tsx.json | 2 | **新建** |
| packages-tui-src-ui-toast.tsx.json | 2 | 保留 1,新增 1 |
| packages-tui-src-ui-working-directory-actions.tsx.json | 7 | **新建** |

**失效锚点修复(13 条死键)**:V1 派生键停在 v2.0.12 之前的源码形状上,v2.0.13 已重构——典型如 `theme.textMuted`→`theme.text.muted`(dialog-prompt/select 各 1 条)、`<text fg={theme.selectedListItemText}>ok</text>`→`<text fg={theme.text.action.primary.focused}>ok</text>`(alert/help)、V1 导出对话框整族键(`Export Options`/`Include assistant metadata`/`placeholder="Enter filename"` 等 8 条)在 v2.0.13 已不存在。**这验证了覆盖账本「200 条 migratable 需人工复核」的判断——直接迁移 V1 键有 13/17 是死的。**

**精确键 1 处(dialog-confirm 的 cancel/confirm 回退标签)**:源码是 `{Locale.titlecase(props.label?.[key] ?? key)}`,裸词 `cancel`/`confirm` 是简单词,\b 替换会误伤 `each={["cancel", "confirm"]}` 与 `store.active === "cancel"` 等代码位,故锚 `{Locale.titlecase(props.label?.[key] ?? key)}` → `{Locale.titlecase(props.label?.[key] ?? (key === "cancel" ? "取消" : "确认"))}`。这与 V1/V2 资产既有风格一致(如 `return "cancelled"`→`return "已取消"`、`title: connected() ? "Connect provider" : …`)。

**真 apply 验证**(临时树实跑非 dry-run,逐行 diff 全部符合预期):`/tmp/oc-pilot/apply-test/` 上 10 个文件全部按上表替换,无级联误伤(如 `Export session`/`Export as:`/`Export` 三处长短键按长度降序+占位符机制正确分流;`Close export result` 与 `Close` 按钮互不污染)。

## ⑦ 复量数字

| 门禁 | 试点前 | 试点后 |
|---|---|---|
| **切片门禁**(apply --dry-run --strict --min-match-rate 1,切片 10 文件) | 6/17 = 35.3%(2 文件 ✗) | **61/61 = 100%** |
| **全局门禁**(同命令,全资产) | 252/501 = 50.3%(失败文件 5) | **309/545 = 56.7%**(失败文件 3,均在切片外) |
| **V1 门禁**(OPENCODE_SOURCE_DIR=V1 检出,apply --strict + verify) | 497/497 = 100% | **497/497 = 100%**(零改动,复跑确认) |

串级账本(主宇宙 tui+cli,Tier A,同一脚本 before/after 对拍;分母 1364 与账本文档一致):

| 类 | before | after | delta |
|---|---|---|---|
| covered | 202 | 246 | **+44** |
| migratable | 149 | 144 | −5 |
| fuzzy-simple(仅此类) | 90 | 82 | −8 |
| new | 923 | 892 | **−31** |
| 迁移天花板(covered+migratable) | 351 (25.7%) | **390 (28.6%)** |

(doc ⑤ 的 migratable 200 / new 939 为「至少一处归此类」口径,与本脚本的优先归并口径差在跨类重复值;天花板 351 两口径一致。)

## ⑧ 质量自评

### 8.1 逐条裁定:切片 90 个 Tier A distinct 的完整分账

试点后残余 = migratable 6 + new 26 = **32 个 distinct,全部有明确处置**;covered 58 = 试点前已在的 9 + 新进入的 49。

| 处置 | distinct | 内容 |
|---|---|---|
| **有中文译文(covered)** | 58 | 9 个试点前已覆盖(ok/Include thinking/thinking/Enter text/span style=/submit/No results found/Search/An unknown error)+ 45 条本试点新译产出的 46 个值(`Press` 与 ` to see…` 两个文本片段由同一个整行键覆盖,故 45 译 → 46 值)+ 3 个被新键传递覆盖的值(`export`/`tools`/`x`) |
| **已译但分类器盲区** | 2 | `cancel`/`confirm`:精确键已译为 取消/确认,但串级分类器只读 find 键(不含这两个词)故不给分;真 apply diff 已证(见 ⑥) |
| **按规则保持原文** | 6 | `esc`、`esc/enter`(键位提示,V1 全表 0 条先例)、`[x]`(复选框符号,中英同形态)、`Markdown`/`JSON`(格式名,V1 先例保留英文)、`› ${…}`(affordance 符号+动态插值,无可译散文) |
| **提取器误报(排除)** | 12 | Tier A 位置的程序化值:`markdown`/`json`(For each 枚举)、`sanitize`(store 键)、`FILTER`(input trait 状态)、`word`/`column`/`row`/`center`/`left`/`right`(wrapMode/flexDirection/justifyContent/highlight 枚举;`left` 是 `truncateTitle === "left"` 被 prop 正则跨三元误捕)、`location.copy`/`location.open`(选项 value id) |
| **Tier B 代码位(试点范围外)** | 12 | `dialog.select.*`(7 条命令 id)、`dialog.prompt.submit`、`useDialog`/`useToast must be used within a …Provider`(开发者 throw)、`${root}…${separator}`(路径截断模板)、`session.move` |

合计 58 + 2 + 6 + 12 + 12 = 90,**没有任何一条被静默丢弃**;「分类器盲区」的 2 条与「保持原文」的 6 条都可在上面的锚点资产或裁定规则中找到对应处置。

### 8.2 术语一致性

全部 45 条新译文均先核 V1 词表(④ 表);无 V1 先例的 16 组新词逐个给出裁定理由,且优先复用 V2 资产已在用词(对话框/剪贴板/确认/取消/搜索/提交/暂无句式)。**未发现与 V1 冲突的译法**;唯一「反向修正」是 workspace:任务假设的「工作区」在 V1/V2 实际资产中均为「工作空间」,本试点按资产实证采用「工作空间」。

### 8.3 已知风险与后续

1. `group: "Dialog"`→`group: "对话框"` 是 8 文件 26 处的批量锚点:若上游把 group 值改名(如 "Dialogs"),门禁会立刻失败报警——这是期望行为(漂移检测),按 nightly 流程修键即可。
2. `title: "Close help"` 与裸键 `Help` 同文件:依赖 apply 的「长键优先+占位符」机制避免级联(已用真 apply 验证);若未来出现第二个独立 "Help" 串,需改精确键。
3. 「脱敏敏感数据」为新词,V1 无先例;如社区有既定译法(如「移除敏感数据」),可在全量阶段统一替换。
4. `Submit dialog prompt`→`提交输入` 是意译;若更喜欢「提交提示」可一行改键。

### 8.4 与覆盖账本的互相验证

- 账本 ⑥ 盲区类(单词级标签处于代码/数组位)在本切片实测存在且已量化:12 条 Tier A 误报 + 12 条 Tier B。
- 账本「migratable 需人工复核」在本切片实测:原 14 个 migratable 值中 2 个(cancel/confirm)需要精确键而非裸词锚定——直接套 V1 键会因 `\b` 简单词规则误伤 `each={["cancel", "confirm"]}` 等代码位导致构建失败。

## ⑨ 全量执行方案与批次划分

**剩余工作量**(试点后,主宇宙 Tier A):new 892 + migratable 144 + fuzzy 82 ≈ **1118 distinct**(族间有重复值;另每批需按本试点的裁定规则剔除提取器误报,预计真实翻译量 ~1000 条)。按覆盖账本 ⑦ 的速率(新译 100 条/人天、改编 150 条/人天、裁定 0.5 人天/90 条、锚定机械化+复核 1-2 人天) ≈ **2-3 人周**,与本试点实测(45 新译+61 条目/单人单会话)一致。

**批次划分(每批 DoD 相同:① 工具列 new 清单 ② V1 术语核对 ③ 翻译+锚定 ④ 切片门禁 N/N ⑤ 串级 covered 100%(含裁定表) ⑥ 样例表人眼验收)**:

| 批次 | 范围 | 规模(Tier A distinct,约) | 说明 |
|---|---|---|---|
| B1 ✅ | `tui/src/ui/` | 90(已完成) | 本试点;45 新译 + 61 条目 |
| B2 | `tui/src/component/dialog-*` + `component/prompt/` | ~306 | 与 ui/ 同构(都是 dialog),术语可无缝复用;含 dialog-mcp/status/model/skill/session-list 等高频对话框 |
| B3 | `tui/src/routes/session/` | ~270 | 会话主界面;账本标记的 16 条 v2.0.13 漂移新串(更新服务错误族)大部分在此 |
| B4 | `tui/src/mini/` + `routes/` 其余 + `app.tsx` | ~239 | 启动/页脚/splash,用户第一眼看到的界面 |
| B5 | `tui/src/feature-plugins/` | ~207 | 侧边栏/tips 等插件面 |
| B6 | `tui/src/component/` 其余 + `config/` + `util/` + `context/` | ~175 | 命令面板/会话页签/错误组件;config 族 Tier B 占比高(572 条中 ~500 在 code 位),本批只做 Tier A |
| B7 | `cli/src/` | ~106 | TUI 之外的 CLI 面(非交互命令输出) |
| B8 | Tier B(错误/日志裸文案) | 1879 distinct | **独立工作流**:格式较固定(500 条/人天),建议在 Tier A 全完后再开;nightly 的 V2 门禁口径重建(阶梯阈值或双轨)也应在 B8 前定稿 |

执行顺序建议 B1→B2→B3→B4→B5→B6→B7→B8;每批一个 PR(同本试点分支纪律),门禁数字逐批累加(当前 309/545 = 56.7%)。**B2 与 B1 同构度最高,建议紧接着做**,可最大化复用本试点的术语表和裁定规则。

## ⑩ 合规自查

- 只改 V2:`git status` 仅 `cli-go/internal/core/assets/opencode-i18n-v2/anchors/` 下 10 个文件(6 改 4 增)+ 本文档;V1 词表/注入脚本/门禁/workflow 零改动(V1 门禁复跑 497/497 实证)。
- 未改 `.github/`、未改产品代码、未推 upstream、未触碰 `/root/xiangmudata_sync/opencode-v2-cn/`。
- 未做全量:仅 `packages/tui/src/ui/` 一个切片;其余切片的串只列清单未翻。
- 复现确定性:文中所有数字来自真实命令输出(v2.0.13 检出 + go build 的 cli + 仓库内资产),无硬编;JSON 资产均通过 `json.load` 校验。
