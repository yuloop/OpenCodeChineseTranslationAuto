# V2 汉化门禁收口(gate-close):从 96.1% 到可辩护的 100%

> 基线:上游 v2.0.13 `3180aab16e050128678e590afcbd2dc85c259cb7`(私有干净检出 `/tmp/oc-v2i18n-cov/my-v2013`);
> 门禁口径与主会话完全一致:`OPENCODE_SOURCE_DIR=<v2.0.13 检出> opencode-cli apply --dry-run --strict --min-match-rate 1`。

## 1. 结论(先看这里)

| 指标 | 收口前(main `a48bd35c4`) | 收口后 | 判定 |
|---|---|---|---|
| V2 全局门禁 | **1273/1325 = 96.1%**,114 ✓ / 15 ⚠ / 0 ✗,exit 1 | **1669/1669 = 100.0%**,217 ✓ / **0 ⚠** / **0 ✗**,exit 0 | ✅ 全绿 |
| V1 门禁(V1 布局检出 `f54ce31`) | 497/497 = 100% | **497/497 = 100%**(V1 资产零改动,复跑确认) | ✅ 不回退 |
| `go test ./...`(cli-go) | ok | ok(cmd + internal/core,含 `TestEmbeddedV1AssetsUnchanged`、`TestEmbeddedV2AssetsCoverEveryV1Entry`) | ✅ |
| Tier A 覆盖(主宇宙 tui+cli) | covered 1668 occ / 1053 distinct / 109 文件 | **covered 2160 occ / 1290 distinct / 138 文件** | ✅ +492 occ |
| 真实落地(`apply` 非 dry-run)反向对拍 | — | 登记前后两棵应用树**仅 2 文件 3 处差异,且全部是既定的重锚翻译**;392 个保持原文位置与原始英文**逐字节一致**;全树 0 残留占位符 | ✅ 无附带损伤 |

**一句话**:3.9% 的门禁缺口不是"有意不翻"的条目(它们从来没进过资产),而是 **52 条过期锚点条目**;本轮把过期条目清掉、把 ⑧ 各表裁定过的"保持原文"条目以身份锚点(原文 → 原文)登记进 V2 资产,门禁到达 100% 且每一项都可逐条辩护。

## 2. 诊断修正:缺口到底是什么(与初始假设不同,先说清)

初始假设("3.9% 缺口 = ⑧ 各表的有意不翻条目")**不成立**。逐条核对四份报告的 ⑧ 裁定表与 V2 资产后确认:

- ⑧ 表里的条目(键位提示、CSS 枚举、命令 id、纯模板……)**从来不在任何锚点文件里**,因此对匹配率的贡献是 0,既不是成功也不是失败——它们不可能构成 52 条的缺口。
- 真正的缺口是 **52 条过期(stale)锚点条目**,分两处:
  1. **15 个锚点文件的目标路径在 v2.0.13 已不存在**(50 条,门禁全部计为失败并打 ⚠ 跳过):`packages-opencode-src-cli-cmd-run-footer.*`(5 个文件 18 条)、`packages-opencode-src-cli-cmd-run-permission.shared.ts`(1)、`packages-opencode-src-session-system.ts`(1)、`packages-tui-src-component-dialog-provider.tsx`(16)、`dialog-tag.tsx`(1)、`routes-session-dialog-subagent.tsx`(3)、`routes-session-dialog-footer.tsx`(2)、`routes-session-dialog-question.tsx`(2)、`routes-session-dialog-subagent-footer.tsx`(4)、`packages-opencode-src-cli-error.ts`(1)、`packages-__no_v2_location__-…-index.tsx`(1)。
  2. **`error-component.tsx` 锚点里 2 个死键**:`() => (copied() ? "✓ Copied" : "Copy report")`(v2.0.13 已改为三态 map)与 `opencode crashed`(现为 `OpenCode crashed`)。
- 删除这 15 个文件**不可能丢任何已有翻译**:门禁按配置的 `file` 字段分组替换,目标不存在的条目对任何现存文件都不生效。已逐键在 v2.0.13 全树核对:49 条键在 tui/cli/core 产品码里的"命中"全是无关位置(测试文件、`process.env.SHELL`、注释、标识符子串),唯一可见串 ` · interrupted` 已被 `index.tsx` 锚点的精确键 `<span style={{ fg: theme.text.muted }}> · interrupted</span>` 覆盖并译为 `· 已中断`。

所以收口必须同时做两件事:**(a) 清掉 52 条过期条目;(b) 把 ⑧ 裁定过的"保持原文"条目登记为身份锚点**。两者都做了,门禁才既绿又可辩护。

## 3. 本轮改动清单(只动 V2 资产,零业务代码)

| 改动 | 数量 | 说明 |
|---|---|---|
| 新增 `…--keep.json` 身份锚点文件 | **103 个 / 392 条** | 每条 `原文 → 原文`,apply 时是空操作;独立文件命名,已证锚点文件零改动,保持原文集合可独立审计 |
| 删除目标已不存在的锚点文件 | **15 个 / 50 条** | 见 §2;其中 `packages-opencode-src-cli-error.ts.json` 的 1 条先搬家再删 |
| 修改 `error-component.tsx` 锚点 | −2 死键,+3 键 | `OpenCode crashed`→`OpenCode 崩溃`;`Copy report`→`复制报告`;`Copy failed`→`复制失败`(V1 同键译法延续) |
| 修改 `util-error.ts` 锚点 | +1 键 | `Try: \`opencode models\` to list available models` → `试试:\`opencode models\` 列出可用模型`(V1 `dialogs/cli-error.json` 原键译法,v2.0.13 该串在 `packages/tui/src/util/error.ts:27`) |
| `config.json` manifest | **未改** | 清单只跟踪 V1 迁移状态;删除锚点文件不影响 `TestEmbeddedV2AssetsCoverEveryV1Entry`(该测试只要求 V1 条目在 manifest 中) |

锚点文件总数 129 → **217**;V1 词表(54 文件 497 条)、注入脚本、门禁逻辑、`.github/`、`/root/xiangmudata_sync/opencode-v2-cn/` **零改动**。

## 4. 登记方法与三类依据

登记集 = 四份报告 ⑧ 裁定表的并集,**逐条回到 v2.0.13 源码核验**后才写入:

1. **存在性核验**:每条必须在该目标文件中按门禁匹配语义命中(简单词 `\b` 正则 / 其余子串),`tools/v2_i18n_coverage.py` 残差表中的原始值(含缩进与换行)原样取用,不做任何 whitespace 归一化猜测。
2. **冲突核验**:同目标文件下不得与任何既有锚点键同形(残差性天然保证,仍逐条断言)。
3. **安全性核验**:身份锚点是空操作;暂存按最长优先,长真实键先占位,短身份键随后原地替换,互不破坏(见 §7 的对拍实证)。

依据分三类(与任务口径一致),392 条分布:

| 依据 | 条数 | 子类 |
|---|---|---|
| **提取器误报** | 248 | 枚举值 80 · 配置键/内部 id 60 · 纯模板 32 · 状态/存储值 33 · 比较操作数 19 · 类型标注 18 · SimSem 标签 6 |
| **按 V1 先例保持原文** | 90 | 键位提示 57 · 符号 12 · 格式/技术名 10 · 单位 3 · 数字编号 5 · 命令示例 3 |
| **Tier B 代码位** | 54 | 命令 id 51 · 开发者 throw 2 · 路径模板 1 |

**全表见附录**(每条含目标文件与原文)。抽样示例:

- `esc`/`enter`/`tab next`/`pgup/pgdn scroll`/`left/right change`/`:q`/`ctrl+a`/`shift+tab`/`FILTER` — V1 全表 497 条中 0 条翻译键位提示,pilot/component 报告同结论。
- `[x]`、`▪`(`\u25aa`)、`·`(`\u00b7`)、`■`(`\u25a0`)、`› ${…}` — V1 保留的符号;`\u25aa` 等以源码中的转义序列原样登记(apply 时空操作,不改变字节)。
- `Markdown`/`JSON`/`OS`/`MCP`/`TPS`/`URLs`/`opencode.ai`/`tokens`/`TOKENS` — V1 保留的格式名/单位/域名。
- `ls -la`/`git status`/`pwd` — 命令示例(routes ⑧-②)。
- `diff.*`×20、`dialog.select.*`×7、`session.move`、`useDialog must be used within a DialogProvider` — Tier B 代码位(pilot ⑧-8.1 原表)。
- `Session not found`(cli/src/mini.ts:64 比较右操作数)、`Step interrupted`(index.tsx:1954 比较右操作数)、`The provider response ended unexpectedly.`(noninteractive.ts:471 比较右操作数)、`confirm`(ssh-askpass.ts:26 环境变量协议值)— 译了会破坏程序逻辑。
- `${root}…${separator}`、`${i() + 1}.`、`[${picked() ? "x" : " "}] `、`${ctx.sessionID}:${props.part.time.created}:${props.part.id}` — 纯模板/编号,无可译散文。

## 5. 待裁定清单(未登记,逐条给依据与建议)

以下都是**用户可见但尚未翻译**的串(翻译欠账),不属于"有意不翻",本轮一律不登记,留待后续批次裁定。V1 有对应译法的已注明(可直接沿用),没有的标注"新词,需裁定"。

**A. 成片未译组件(建议整文件批次处理)**

| 文件 | 可见串 | V1 参照 / 建议 |
|---|---|---|
| `component/devtools-bar.tsx` | `Render`/`Switch to `/`Server`/`UI`/`Theme`/`Mode`/`Status`/`Connected`/`Tools`/`Version`/`Debug overlay`/`Time to first draw`/`Turn token usage`(+`(verbose)`)/`Address`/`CPU`/`Experiments`/`Last error`/`Loop`/`Memory`/`Name`/`PID`/`Reconnect`/`Server details unavailable`/`Write debug snapshot`/`Writing debug snapshot…`(25 条) | `Status`→`状态`、`Connected`→`已连接`(V1 有);其余新词 |
| `component/session-frame.tsx` | `Hide sidebar`/`Show sidebar`/`Close terminal pane`/`Focus right pane`/`Focus session pane`/`Hide terminal pane`/`New terminal`/`Select terminal`/`Show terminal pane`/`Unable to load terminal`(10 条) | `Hide sidebar`/`Show sidebar` V1 有三元组键译法,可沿用 |
| `component/session-tabs.tsx` | `Rename`/`Untitled session`/`Close`/`Close tab menu`/`Copy session ID`/`New tab`/`Tabs`/`Session ID copied to clipboard`/`U`(idleLabel 兜底,9 条) | `Untitled session`→`未命名会话`(V1 精确键) |
| `component/reconnecting.tsx` | `Connection lost…`/`Reconnecting to the server automatically.`/`Restarting service…`/`Your session will resume automatically.`(4 条) | 新词 |
| `config/keybind.ts` | **239 条 `keybind()` 描述中 237 条未译**(帮助对话框全表) | **V1 也从未译过**(V1 无 keybind 规则文件、无任何对应键)——是长期欠账而非 V2 回归;量最大,建议单开一批 |

**B. 散点可见串(建议随所在切片顺手处理)**

| 文件 | 可见串 | V1 参照 / 建议 |
|---|---|---|
| `mini/footer.command.tsx` | `Compact session`/`Switch agent`/`Select agent`/`Select model`/`Shell` | V1 分别有 `精简会话`/`切换智能体`/`选择智能体`/`选择模型`/`命令行` |
| `mini/footer.view.tsx` | `group: "Model"` | V1 `模型` |
| `mini/footer.menu.tsx` | `No matching items` | V1 `未找到匹配项` |
| `mini/footer.prompt.tsx` | `title: "Paste"` | V1 `title: "Paste"`→`title: "粘贴"`(同形) |
| `mini/footer.subagent.tsx` | `stop`(窄屏 alternate label) | 新词(同文件 `interrupt`→`中断` 已译) |
| `mini/tool.ts` | `Unknown`/`WebFetch`/`WebFetch ${url}` | V1 `未知`/`网页获取`/`网页获取 ${url}` |
| `mini/stream-v2.transport.ts` | `text: "Compaction"` | V1 `压缩` |
| `mini/scrollback.writer.tsx` | ` line{s}`(L206) | 新词(复数构造) |
| `component/prompt/index.tsx` | `+N more`(L1730) | 新词 |
| `component/error-component.tsx` | `Error `/`Stack trace `/`Clipboard write failed. Try again or report the crash manually.` | 新词(同文件其余已译) |
| `component/migration-overlay.tsx` | `Data migration failed` | 新词 |
| `component/plugin-route-missing.tsx` | `Unknown plugin route: `/`go home` | 新词 |
| `component/theme-error-toast.tsx` | `Failed to load theme: ${name}` | 新词 |
| `feature-plugins/system/stats.tsx` | `title: "back"`(L152)、星期字母 `F`/`M`/`T`/`W`(L102) | 新词(日历头字母,需裁定是否中文化) |
| `feature-plugins/system/stats-data.ts` | `label: "sessions"` | 新词 |
| `feature-plugins/prompt/btw.tsx` | `" copy"`(L166)、`placeholder: "Ask anything"`(L65)、`group: "Dialog"`(L114,component 报告 ⑨ 记录在案) | 新词 |
| `feature-plugins/prompt/footer.tsx` | `agents`(L97)、`commands`(L103) | 新词 |
| `feature-plugins/home/footer.tsx` | `{failed()} plugin{...} failed` 复数构造(L67,含 ` plugin`、`s` 两个残差片段) | 新词(需按中文复数习惯重写) |
| `feature-plugins/sidebar/footer.tsx` | `Connect provider` | V1 `连接提供商` |
| `feature-plugins/system/diff-viewer.tsx` | `Go to the start of the diff`/`Go to the end of the diff`/`View`/` help`(L773) | V1 `前往 `(前缀键)/`查看 `(前缀键) |
| `util/permission.ts` | 工具标题 `read`/`Read`/`List`/`glob`/`Glob`/`Grep` | V1 `读取`/`编辑`/`列出`/`通配符`/`搜索` 同族 |
| `util/form.ts` / `auth/form.ts` | `label: "No"` | 新词(建议 `否`) |
| `auth/login.ts` | `API key`(L110)、`hint: "connected"`(L93) | V1 `API密钥`;`connected` 建议 `已连接` |
| `uninstall.ts` | `label: "Config"` | 新词(建议 `配置`) |
| `plugin/api.tsx` | `label: "Open"` | 新词(建议 `打开`) |
| `routes/session/index.tsx`、`permission.tsx`、`dialog-execute.tsx`、`composer/subagents-tab.tsx` | routes ⑧ 表"可见但属 Tier B 代码位、移交 B8"的 9 处(13 串):`"Shell"`/`"Subagent"`(L2027 标题头)、`in`/`out`(L2102 用量行)、`Command cancelled`/`Command timed out`/`Command exited with code ${exit}`(L2256-2259)、`attachment`(L2386)、`(no answer)`(L3515)、`minimize`/`fullscreen`(permission.tsx L498)、`Receiving code…`/`Running`/`Failed`/`Completed`(dialog-execute L68-75)、`No output`/`Waiting for output…`(L140)、`"Subagent"`/`"Running"`(subagents-tab L50/L203) | routes 报告已给建议译文(如 `命令行`/`子智能体`/`输入`/`输出`/`命令已取消`/`附件`/`(无回答)`/`收起`/`全屏`/`运行中`/`暂无输出`),B8 可直接沿用 |

> 另有 `packages/tui/src/routes/session/index.tsx` 的 `+N more` 族片段已在 ⑧-③ 判为"整行锚点跨 JSX 边界"的盲区(已译),不在此表。

## 6. 盲区清单(已译,仅备案,不登记)

以下残差串实际已被同文件更长锚点译过(整行/整式锚点跨 JSX 表达式或注释边界),分类器看不见,但用户看到的是中文:`\n Code\n`/`\n Output\n`/`\n execute\n`(dialog-execute.tsx)、`\n Image `(dialog-image-preview.tsx,键 `Image {index() + 1} of {props.images.length}`)、` completed\n `(form.tsx)、` more\n`(routes/session/index.tsx,键 `+{images().length - visible().length} more`→`…更多`)、routes ⑧-③ 的 22 条(index.tsx 的 `Press `/`new · `/` total`/`! Likely cache bust: `/`Skill `/`reverted` 等)、pilot ⑧-8.1 的 cancel/confirm(dialog-confirm.tsx)。**不需要任何操作**;列出以证明残差表里的"未覆盖"不等于"未翻译"。

## 7. 门禁与回归数据

### 7.1 V2 全局门禁(同一 v2.0.13 检出,同一 CLI 构建流程)

```
收口前:📁 文件: 114 成功, 15 跳过, 0 失败   📝 替换: 1273/1325 成功 (96.1%)   exit 1
收口后:📁 文件: 217 成功,  0 跳过, 0 失败   📝 替换: 1669/1669 成功 (100.0%)  exit 0
```

条目数守恒校验:1325 − 50(15 个过期文件)− 2(error-component 死键)+ 392(身份锚点)+ 3(error-component 新键)+ 1(util-error 新键)= **1669**;成功数 1273 + 392 + 3 + 1 = **1669**(52 条失败条目中 50 条随文件删除、2 条随死键删除,不再计数)。217 个目标文件**逐行全部 `N/N 处替换`**,无 ⚠ 无 ✗。条目数最多的文件:`routes/session/index.tsx` 130+31(双配置)、`app.tsx` 72、`config/index.tsx` 68、`diff-viewer.tsx` 57+34(双配置)、`mini/footer.command.tsx` 53。

### 7.2 V1 门禁(证明没碰 V1)

`OPENCODE_SOURCE_DIR=/tmp/oc-v1-devhead`(V1 布局检出 `f54ce31`)`apply --dry-run --strict --min-match-rate 1`:**497/497 = 100.0%,0 失败,exit 0**;`go test ./...` 全绿,含 `TestEmbeddedV1AssetsUnchanged`(54 文件 497 条零改动)。

### 7.3 Tier A 覆盖(tools/v2_i18n_coverage.py,同一源码树,资产目录对拍)

| 包 | covered occ | covered distinct | migratable occ | new occ |
|---|---|---|---|---|
| tui | 1579 → **2053** | 972 → **1198** | 210 → 61 | 382 → 62 |
| cli | 89 → **107** | 85 → **102** | 11 → 4 | 16 → 6 |
| 合计 | 1668 → **2160** | 1053 → **1290** | 221 → 65 | 398 → 68 |

一条身份键可覆盖多处出现(如 `left` 在 diff-viewer.tsx 命中 12 处),故 covered occ 增幅(+492)大于登记条数(392)。

## 8. 真实落地反向验证(证明身份锚点零副作用)

取两棵**干净的 v2.0.13 副本**,分别用收口前 CLI(内嵌旧资产,129 配置)与收口后 CLI(内嵌新资产,217 配置)执行**真实 `apply`**(非 dry-run):

- 两棵应用树 `diff -r`:**仅 2 个文件、3 处差异,全部是既定的重锚翻译**——
  `error-component.tsx`:`Copy report`→`复制报告`、`Copy failed`→`复制失败`、`OpenCode crashed`→`OpenCode 崩溃`;`util/error.ts`:`Try: \`opencode models\`…`→`试试:\`opencode models\`…`。
- **392 个保持原文位置逐字节核对**:以门禁匹配语义统计每个登记值在"干净树"与"应用后树"中的出现次数,391 个完全不变;唯一变化是 `error-component.tsx` 的 `failed`(7→6),原因是同文件新真实键 `Copy failed` 合法地译掉了字符串里的那一处——身份位置(`failed:` map 键)未动。
- 全树扫描 `\x00opencode-i18n-N\x00` 占位符残留:**0 处**(旧资产应用树同样 0 处)。

**过程中发现并修掉的一个真实坑(已记入已知限制)**:首轮登记把 `app.tsx` 的 `opencode`(简单词,`\b` 匹配)也登记为身份锚点,真实 apply 后该文件出现未解析占位符。原因:CLI 的暂存占位符格式是 `\x00opencode-i18n-<序号>\x00`,`\bopencode\b` 会命中占位符文本自身,把已暂存的占位符打碎导致无法回填。**修复**:改为上下文限定形式 `username: "opencode"`(非简单词 → 子串匹配,不可能命中占位符)。已全量扫描 392 条:除该条外无任何键是 `opencode`/`i18n`/纯数字(唯一能撞上占位符文本的三类形态)。**今后登记身份锚点前必须过这一项检查。**

## 9. 已知限制与下一步

1. **待裁定清单(§5)是剩余可见欠账**,共约 60 条散点 + 237 条 keybind 描述 + 25 条 devtools。门禁 100% 只意味着"资产里没有骗分条目",不等于"UI 全中文"。
2. `config.json` manifest 未随删除更新(其 `moved` 状态对已删文件呈历史记录态);若后续要精确跟踪,应在 manifest 侧单独标注,不在本轮改动。
3. keybind.ts 的 237 条描述在 V1 时代就没译过,属独立批次工作量,建议与 devtools-bar 一起作为下一批(B7)的候选。
4. 身份锚点登记规则(沉淀):只用源码原样值;简单词要检查是否会命中 `\x00opencode-i18n-N\x00`;同类集合放独立 `--keep` 文件,便于审计与回滚。
## 附录:392 条身份锚点全表

共 392 条,按依据类别分组;每条均为 `原文 -> 原文`(apply 时空操作)。

### 提取器误报·枚举值 — 80 条 / 32 个目标文件

- `packages/tui/src/app.tsx` (9): `dummy` · `home` · `screen` · `storybook` · `tmux` · `wayland` · `win32` · `x11` · `word`
- `packages/tui/src/component/dialog-config.tsx` (2): `left` · `right`
- `packages/tui/src/component/dialog-experiments.tsx` (2): `left` · `right`
- `packages/tui/src/component/dialog-pair.tsx` (5): `row` · `center` · `column` · `flex-end` · `flex-start`
- `packages/tui/src/component/dialog-session-list.tsx` (1): `right`
- `packages/tui/src/component/migration-overlay.tsx` (1): `left`
- `packages/tui/src/component/prompt/index.tsx` (2): `bottom` · `left`
- `packages/tui/src/component/session-frame.tsx` (3): `absolute` · `relative` · `right`
- `packages/tui/src/component/session-tabs.tsx` (5): `absolute` · `center` · `flex-end` · `flex-start` · `vertical`
- `packages/tui/src/feature-plugins/prompt/btw.tsx` (1): `grid`
- `packages/tui/src/feature-plugins/system/diff-viewer-file-menu.tsx` (1): `absolute`
- `packages/tui/src/feature-plugins/system/diff-viewer.tsx` (2): `top` · `bottom`
- `packages/tui/src/feature-plugins/system/plugins.tsx` (1): `right`
- `packages/tui/src/feature-plugins/system/stats.tsx` (3): `row` · `center` · `column`
- `packages/tui/src/mini/footer.command.tsx` (2): `bottom` · `transparent`
- `packages/tui/src/mini/footer.form.tsx` (3): `row` · `column` · `transparent`
- `packages/tui/src/mini/footer.menu.tsx` (1): `muted`
- `packages/tui/src/mini/footer.permission.tsx` (4): `row` · `center` · `column` · `stretch`
- `packages/tui/src/mini/footer.prompt.tsx` (1): `left`
- `packages/tui/src/mini/footer.view.tsx` (3): `composer` · `left` · `transparent`
- `packages/tui/src/mini/scrollback.writer.tsx` (1): `top`
- `packages/tui/src/routes/session/composer/index.tsx` (1): `left`
- `packages/tui/src/routes/session/form.tsx` (1): `left`
- `packages/tui/src/routes/session/index.tsx` (5): `left` · `rendered` · `top` · `grid` · `word`
- `packages/tui/src/routes/session/message-parts.tsx` (3): `grid` · `left` · `rendered`
- `packages/tui/src/routes/session/permission.tsx` (6): `row` · `left` · `column` · `flex-start` · `space-between` · `center`
- `packages/tui/src/routes/session/sidebar.tsx` (2): `absolute` · `relative`
- `packages/tui/src/ui/dialog-export-options.tsx` (2): `json` · `markdown`
- `packages/tui/src/ui/dialog-select.tsx` (3): `row` · `column` · `word`
- `packages/tui/src/ui/dialog.tsx` (1): `center`
- `packages/tui/src/ui/pane-resize-handle.tsx` (1): `right`
- `packages/tui/src/ui/toast.tsx` (2): `left` · `right`

### 提取器误报·状态/存储值 — 33 条 / 17 个目标文件

- `packages/cli/src/services/update-preflight.tsx` (2): `running` · `success`
- `packages/tui/src/app.tsx` (1): `compact`
- `packages/tui/src/component/devtools-bar.tsx` (3): `connected` · `disconnected` · `high`
- `packages/tui/src/component/dialog-status.tsx` (3): `connected` · `disabled` · `failed`
- `packages/tui/src/component/dialog-update.tsx` (1): `checking`
- `packages/tui/src/component/dialog-variant.tsx` (1): `default`
- `packages/tui/src/component/prompt/index.tsx` (2): `pending` · `running`
- `packages/tui/src/context/update-notification.tsx` (1): `failed`
- `packages/tui/src/feature-plugins/sidebar/mcp.tsx` (4): `connected` · `disabled` · `failed` · `pending`
- `packages/tui/src/feature-plugins/system/diff-viewer.tsx` (2): `modified` · `unbound`
- `packages/tui/src/mini/footer.command.tsx` (1): `inactive`
- `packages/tui/src/mini/footer.subagent.tsx` (1): `running`
- `packages/tui/src/mini/stream-v2.subagent.ts` (1): `running`
- `packages/tui/src/routes/home.tsx` (1): `installed`
- `packages/tui/src/routes/session/form.tsx` (1): `ANSWER`
- `packages/tui/src/routes/session/index.tsx` (7): `streaming` · `compaction-queued` · `exploration` · `agent-switched` · `model-switched` · `location-switched` · `synthetic`
- `packages/tui/src/routes/session/permission.tsx` (1): `REJECT`

### 提取器误报·类型标注 — 18 条 / 15 个目标文件

- `packages/cli/src/acp/service.ts` (1): `prompt`
- `packages/cli/src/commands/handlers/auth/form.ts` (1): `string`
- `packages/cli/src/util/error.ts` (1): `string`
- `packages/tui/src/component/dialog-integration.tsx` (1): `string`
- `packages/tui/src/component/prompt/metadata.tsx` (1): `normal`
- `packages/tui/src/context/keymap.tsx` (1): `string`
- `packages/tui/src/editor-zed.ts` (1): `contents`
- `packages/tui/src/feature-plugins/prompt/footer.tsx` (1): `normal`
- `packages/tui/src/mini/footer.ts` (1): `string`
- `packages/tui/src/mini/form.shared.ts` (2): `message` · `string`
- `packages/tui/src/mini/stream-v2.transport.ts` (2): `message` · `string`
- `packages/tui/src/routes/session/dialog-fork.tsx` (1): `user`
- `packages/tui/src/routes/session/dialog-message.tsx` (2): `assistant` · `user`
- `packages/tui/src/routes/session/permission.tsx` (1): `function`
- `packages/tui/src/util/error.ts` (1): `string`

### 提取器误报·配置键/内部 id — 60 条 / 24 个目标文件

- `packages/cli/src/acp/config-option.ts` (1): `thought_level`
- `packages/cli/src/config/migrate.ts` (2): `terminal` · `copy_on_select`
- `packages/tui/src/app.tsx` (3): `opencode` · `plugin` · `opencode.storybook`
- `packages/tui/src/component/devtools-bar.tsx` (4): `server` · `theme` · `tools` · `ui`
- `packages/tui/src/component/dialog-status.tsx` (1): `needs_auth`
- `packages/tui/src/component/error-component.tsx` (1): `failed`
- `packages/tui/src/component/prompt/index.tsx` (2): `autoaccept` · `prompt-image-preview-${index()}`
- `packages/tui/src/component/session-frame.tsx` (4): `panel` · `session` · `sidebar` · `terminal`
- `packages/tui/src/component/session-tabs.tsx` (1): `small-dot`
- `packages/tui/src/feature-plugins/sidebar/mcp.tsx` (1): `needs_auth`
- `packages/tui/src/feature-plugins/system/diff-viewer-image.tsx` (1): `base64`
- `packages/tui/src/feature-plugins/system/diff-viewer.tsx` (5): `auto` · `deleted` · `list` · `name` · `ref`
- `packages/tui/src/mini/footer.command.tsx` (6): `mono` · `shell_output` · `splash` · `turn_summary` · `verbosity` · `work_spinner`
- `packages/tui/src/mini/footer.prompt.tsx` (1): `mini-prompt-image-${index()}`
- `packages/tui/src/mini/footer.view.tsx` (2): `form` · `permission`
- `packages/tui/src/mini/runtime.boot.ts` (1): `show`
- `packages/tui/src/mini/scrollback.writer.tsx` (1): `content`
- `packages/tui/src/mini/stream-v2.subagent.ts` (2): `form` · `permission`
- `packages/tui/src/mini/stream-v2.transport.ts` (1): `reasoning`
- `packages/tui/src/mini/types.ts` (2): `hide` · `show`
- `packages/tui/src/mini/verbosity.ts` (2): `hide` · `show`
- `packages/tui/src/routes/session/index.tsx` (13): `reasoning` · `assistant-footer` · `turn-usage` · `tool-call` · `system` · `hide` · `glob` · `read` · `grep` · `webfetch` · `websearch` · `execute` · `patch`
- `packages/tui/src/ui/dialog-export-options.tsx` (1): `sanitize`
- `packages/tui/src/ui/working-directory-actions.tsx` (2): `location.copy` · `location.open`

### 提取器误报·纯模板 — 32 条 / 20 个目标文件

- `packages/cli/src/acp/content.ts` (2): `[${block.resource.uri}]\n${block.resource.text}` · `[${filepath}${line ? `:${line}` : ""}]\n${block.resource.text}`
- `packages/cli/src/acp/event.ts` (1): `${child.title}: ${projected.title}`
- `packages/cli/src/commands/handlers/session/export.ts` (1): `${new Date(session.time.updated).toLocaleString()} - ${session.id.slice(-8)}`
- `packages/cli/src/run/noninteractive.ts` (2): `<file name="${file.filename}">\n${content}\n</file>` · `> ${event.data.agent} · ${event.data.model.id}`
- `packages/cli/src/services/updater.ts` (1): `…${tail.slice(-1_999)}`
- `packages/tui/src/component/dialog-integration.tsx` (2): `$${connection.name}` · `[${selected.includes(option.value) ? "x" : " "}] ${option.label}`
- `packages/tui/src/component/dialog-open.tsx` (2): `${label ? `${Locale.truncate(label, 30)} · ` : ""}${timeAgo(session.time.updated)}` · `${truncateFilePath(footer, width)}${git ? " →" : ""}`
- `packages/tui/src/component/patch-diff.tsx` (1): ` ${hunk.header ?? ""}`
- `packages/tui/src/component/prompt/autocomplete.tsx` (2): ` ${reference.source.type === "git" ? reference.source.repository : reference.source.path}` · `@${referenceMatchValue.name}`
- `packages/tui/src/component/prompt/index.tsx` (1): `@${skill}`
- `packages/tui/src/feature-plugins/prompt/footer.tsx` (1): `span style=`
- `packages/tui/src/feature-plugins/system/diff-viewer-image.tsx` (1): `data:application/octet-stream;base64,${Buffer.from(bytes).toString("base64")}`
- `packages/tui/src/mini/footer.permission.tsx` (1): `span style=`
- `packages/tui/src/mini/footer.width.ts` (1): ` ${expanded ? (value.expanded ?? value.label) : value.label}`
- `packages/tui/src/mini/stream-v2.transport.ts` (1): `<file name="${file.filename}">\n${content}\n</file>`
- `packages/tui/src/mini/tool.ts` (3): `${ctx.name} ${title}` · `${suffix}${suffix ? " · " : ""}${count(matches, "match")}` · `${title} "${p.input.query}"`
- `packages/tui/src/mini/turn-summary.ts` (1): `${input.agent} · ${input.model} · ${input.duration}`
- `packages/tui/src/routes/session/index.tsx` (2): ` ${skill.name} ` · `${ctx.sessionID}:${props.part.time.created}:${props.part.id}`
- `packages/tui/src/routes/session/permission.tsx` (2): `${id()}.actions` · `${id()}.action.${String(option)}`
- `packages/tui/src/util/permission.ts` (4): `${title} "${pattern}"` · `${title} "${query}"` · `${title} ${formatPath(value)}` · `LSP ${operation}${file ? ` ${formatPath(file)}${position ? `:${position}` : ""}` : ""}`

### 提取器误报·比较操作数 — 19 条 / 13 个目标文件

- `packages/cli/src/mini.ts` (1): `Session not found`
- `packages/cli/src/run/noninteractive.ts` (1): `The provider response ended unexpectedly.`
- `packages/cli/src/ssh-askpass.ts` (1): `confirm`
- `packages/tui/src/app.tsx` (1): `full`
- `packages/tui/src/component/dialog-update.tsx` (1): `left`
- `packages/tui/src/component/session-tabs.tsx` (1): `numbers`
- `packages/tui/src/mini/footer.command.tsx` (2): `thinking` · `tools`
- `packages/tui/src/mini/footer.form.tsx` (1): `external`
- `packages/tui/src/mini/footer.view.tsx` (1): `show`
- `packages/tui/src/routes/session/index.tsx` (3): `shell` · `Step interrupted` · `light`
- `packages/tui/src/routes/session/permission.tsx` (4): `shell` · `subagent` · `task` · `always`
- `packages/tui/src/ui/dialog-select.tsx` (1): `left`
- `packages/tui/src/util/selection.ts` (1): `cell`

### 提取器误报·SimSem 标签 — 6 条 / 1 个目标文件

- `packages/tui/src/routes/session/permission.tsx` (6): `Reject permission: ${props.action}` · `Rejection reason` · `Rejection actions` · `Confirm rejection` · `Cancel rejection` · `Permission choices`

### V1 先例·键位提示 — 57 条 / 33 个目标文件

- `packages/tui/src/component/dialog-debug.tsx` (2): `
          esc
        ` · `enter`
- `packages/tui/src/component/dialog-error-details.tsx` (1): `
            esc
          `
- `packages/tui/src/component/dialog-image-preview.tsx` (1): `
          esc
        `
- `packages/tui/src/component/dialog-integration.tsx` (3): `
            c ` · `
            o ` · `
          esc
        `
- `packages/tui/src/component/dialog-open.tsx` (1): `ctrl+n`
- `packages/tui/src/component/dialog-pair.tsx` (1): `
          esc
        `
- `packages/tui/src/component/dialog-session-list.tsx` (1): `ctrl+a`
- `packages/tui/src/component/dialog-shell-output.tsx` (1): `
          esc
        `
- `packages/tui/src/component/dialog-status.tsx` (1): `
          esc
        `
- `packages/tui/src/component/dialog-update.tsx` (2): `
          esc
        ` · `shift+tab`
- `packages/tui/src/component/dialog-workspace-file-changes.tsx` (1): `
          esc
        `
- `packages/tui/src/component/dialog-worktree-name.tsx` (2): `
          enter ` · `
          esc
        `
- `packages/tui/src/component/prompt/index.tsx` (1): `
      esc`
- `packages/tui/src/feature-plugins/prompt/btw.tsx` (2): `
          esc
        ` · `j/k ↑/↓ scroll`
- `packages/tui/src/feature-plugins/prompt/footer.tsx` (1): `
          esc`
- `packages/tui/src/feature-plugins/system/diff-viewer.tsx` (2): `
          esc close
        ` · `right-click`
- `packages/tui/src/feature-plugins/system/plugins.tsx` (2): `ctrl+a` · `enter`
- `packages/tui/src/mini/footer.command.tsx` (6): `FILTER` · `enter queue` · `enter steer` · `esc
        ` · `left/right change` · `tab show ${active() ? "inactive" : "active"}`
- `packages/tui/src/mini/footer.form.tsx` (1): `
              esc dismiss
            `
- `packages/tui/src/mini/footer.permission.tsx` (4): `
                    enter ` · `
                    esc ` · `
                pgup/pgdn` · `left/right`
- `packages/tui/src/mini/footer.subagent.tsx` (3): `
                tab next ` · `
              pgup/pgdn scroll
            ` · `
            esc back
          `
- `packages/tui/src/mini/prompt.shared.ts` (1): `:q`
- `packages/tui/src/routes/session/composer/index.tsx` (1): `
                esc
              `
- `packages/tui/src/routes/session/dialog-execute.tsx` (2): `
          esc
        ` · `esc back`
- `packages/tui/src/routes/session/form.tsx` (3): `
              c ` · `
            enter ` · `
            esc `
- `packages/tui/src/routes/session/permission.tsx` (3): `
              enter ` · `
            enter ` · `
              esc `
- `packages/tui/src/ui/dialog-alert.tsx` (1): `
          esc
        `
- `packages/tui/src/ui/dialog-confirm.tsx` (1): `
          esc
        `
- `packages/tui/src/ui/dialog-export-options.tsx` (1): `
          esc
        `
- `packages/tui/src/ui/dialog-export-result.tsx` (1): `
          esc
        `
- `packages/tui/src/ui/dialog-help.tsx` (1): `
          esc/enter
        `
- `packages/tui/src/ui/dialog-prompt.tsx` (1): `
          esc
        `
- `packages/tui/src/ui/dialog-select.tsx` (2): `
            esc
          ` · `FILTER`

### V1 先例·符号 — 12 条 / 11 个目标文件

- `packages/tui/src/component/devtools-bar.tsx` (1): `[x]`
- `packages/tui/src/component/one-cell-spinner.tsx` (1): `\u25aa`
- `packages/tui/src/feature-plugins/system/diff-viewer-file-tree.tsx` (1): ` · ${props.sourceDetail}`
- `packages/tui/src/feature-plugins/system/diff-viewer.tsx` (1): ` · ${props.sourceDetail}`
- `packages/tui/src/feature-plugins/system/stats.tsx` (2): `\u00b7 ` · `\u25a0 `
- `packages/tui/src/mini/footer.command.tsx` (1): `${header().hint} ${props.mono ? "-" : "·"} `
- `packages/tui/src/mini/footer.form.tsx` (1): `[${picked() ? "x" : " "}] `
- `packages/tui/src/mini/splash.ts` (1): `${input.mono ? "[O]" : "▪"} oc mini`
- `packages/tui/src/mini/variant.shared.ts` (1): ` · ${variant}`
- `packages/tui/src/ui/dialog-export-options.tsx` (1): `[x]`
- `packages/tui/src/ui/toast.tsx` (1): `› ${props.toast.action.label}`

### V1 先例·格式/技术名 — 10 条 / 8 个目标文件

- `packages/tui/src/component/dialog-config.tsx` (2): `Markdown` · `TPS`
- `packages/tui/src/component/dialog-debug.tsx` (1): `OS`
- `packages/tui/src/component/dialog-integration.tsx` (1): `MCP`
- `packages/tui/src/component/dialog-pair.tsx` (1): `URLs`
- `packages/tui/src/feature-plugins/home/footer.tsx` (1): ` MCP
            `
- `packages/tui/src/feature-plugins/sidebar/mcp.tsx` (1): `MCP`
- `packages/tui/src/feature-plugins/system/stats.tsx` (1): `opencode.ai`
- `packages/tui/src/ui/dialog-export-options.tsx` (2): `JSON` · `Markdown`

### V1 先例·单位 — 3 条 / 3 个目标文件

- `packages/tui/src/feature-plugins/sidebar/context.tsx` (1): ` tokens`
- `packages/tui/src/feature-plugins/system/stats-data.ts` (1): `tokens`
- `packages/tui/src/feature-plugins/system/stats.tsx` (1): `TOKENS`

### V1 先例·命令示例 — 3 条 / 1 个目标文件

- `packages/tui/src/routes/home.tsx` (3): `git status` · `ls -la` · `pwd`

### V1 先例·数字编号 — 5 条 / 2 个目标文件

- `packages/tui/src/mini/footer.form.tsx` (3): `${Math.min(state().field + 1, props.request.fields.length)}/${props.request.fields.length}` · `${rows().length + 1}.` · `${state().selected === rows().length ? ">" : " "}${rows().length + 1}.`
- `packages/tui/src/routes/session/form.tsx` (2): `${i() + 1}.` · `${rows().length + 1}.`

### Tier B 代码位·命令 id — 51 条 / 14 个目标文件

- `packages/tui/src/component/dialog-integration.tsx` (1): `dialog.integration.rename`
- `packages/tui/src/component/dialog-mcp.tsx` (1): `dialog.mcp.toggle`
- `packages/tui/src/component/dialog-model.tsx` (2): `model.dialog.favorite` · `model.dialog.provider`
- `packages/tui/src/component/dialog-session-list.tsx` (2): `session.pin.toggle` · `session.rename`
- `packages/tui/src/component/dialog-workspaces.tsx` (2): `dialog.move_session.new` · `dialog.move_session.refresh`
- `packages/tui/src/feature-plugins/system/diff-viewer-file-tree.tsx` (2): `diff-file-row-${row.fileIndex}` · `diff-folder-row-${row.id}`
- `packages/tui/src/feature-plugins/system/diff-viewer-image.tsx` (1): `diff-image-${props.file}`
- `packages/tui/src/feature-plugins/system/diff-viewer.tsx` (22): `app.exit` · `diff-file-header-${entry.fileIndex}` · `diff.close` · `diff.down` · `diff.first` · `diff.half_page.down` · `diff.half_page.up` · `diff.help` · `diff.last` · `diff.mark_reviewed` · `diff.next_file` · `diff.next_hunk` · `diff.page.down` · `diff.page.up` · `diff.previous_file` · `diff.previous_hunk` · `diff.single_patch` · `diff.switch_source` · `diff.toggle_file_tree` · `diff.toggle_view` · `diff.up` · `opencode.diffs`
- `packages/tui/src/feature-plugins/system/plugins.tsx` (4): `dialog.plugins.check` · `dialog.plugins.error` · `dialog.plugins.update` · `plugins.toggle`
- `packages/tui/src/routes/session/dialog-message.tsx` (4): `message.copy` · `message.jump` · `session.fork` · `session.revert`
- `packages/tui/src/routes/session/index.tsx` (1): `queued_prompt.delete`
- `packages/tui/src/ui/dialog-prompt.tsx` (1): `dialog.prompt.submit`
- `packages/tui/src/ui/dialog-select.tsx` (7): `dialog.select.prev` · `dialog.select.next` · `dialog.select.page_up` · `dialog.select.page_down` · `dialog.select.home` · `dialog.select.end` · `dialog.select.submit`
- `packages/tui/src/ui/working-directory-actions.tsx` (1): `session.move`

### Tier B 代码位·开发者 throw — 2 条 / 2 个目标文件

- `packages/tui/src/ui/dialog.tsx` (1): `useDialog must be used within a DialogProvider`
- `packages/tui/src/ui/toast.tsx` (1): `useToast must be used within a ToastProvider`

### Tier B 代码位·路径模板 — 1 条 / 1 个目标文件

- `packages/tui/src/ui/file-path.tsx` (1): `${root}…${separator}`

