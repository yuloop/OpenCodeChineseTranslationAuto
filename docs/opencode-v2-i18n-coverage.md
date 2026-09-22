# opencode V2 汉化 · 覆盖账本与缺口测量报告

- 日期:2026-09-22
- 性质:**只读测量**(侦察)。未改 V1/V2 翻译资产、未改产品代码、未改 workflow、未推 upstream;未做任何翻译。
- 测量基准:上游 `anomalyco/opencode` tag **`v2.0.13`**(commit `3180aab16e050128678e590afcbd2dc85c259cb7`,测量时最新 v2.0.x);交叉基准 tag **`v2.0.12`**(commit `2670273ff17da96f85c5826ced57aa1b368754fa`,现有 V2 资产的生成基准,与 PR #4/#5 同树)。
- 交付物:本报告 + 统计脚本 `tools/v2_i18n_coverage.py`(可复现全部数字)。

## ① 结论摘要(TL;DR)

1. **要做出完整中文 V2,必须对 V2 源码做一轮新翻译——「找老锚点」路线已到顶。** 以 v2.0.13 主宇宙(packages/tui/src + packages/cli/src)计,V2 用户可见界面串去重后 **1364 条**;现有 V2 资产已覆盖 **202 条(14.8%)**,V1 词表可整串迁移(重新锚定即可)**200 条**,二者合计 **351 条(25.7%)** 即迁移路线的天花板;其余 **939 条(68.8%)** 在任何位置都没有现成译文,其中确定必须从零翻译 **683 条**、可基于 V1 近似译文改编 **240 条**、单词级模糊待人工裁定 **90 条**。
2. 条目级门禁(`apply --dry-run --strict --min-match-rate 1`)在 v2.0.12 与 v2.0.13 上均为 **252/501(50.3%)**,逐文件输出完全一致(资产零漂移);v2.0.13 相对 v2.0.12 净增 **16 条**新界面串(更新服务错误族 + 少量 UI)。
3. 工作量量级:Tier A(终端 UI 核心口径)完整汉化约 **2-3 人周**(683 新译 + 240 改编 + 90 裁定 + 锚定机械化 + 门禁口径重建);若连 Tier B(错误/日志裸文案,另计 1879 条去重)也要完整,再 **+3-4 人周**。此后每个上游小版本增量约 0.5 人天(本次实测漂移 16 条)。
4. 提取器质量:门禁命中的 252 条资产键中 **240 条(95.2%)** 能对应到提取出的 UI 串;未对应的 12 条全部属于已量化的盲区类(单词级标签处于代码/数组/footer 位置,见 ⑥)。

## ② 测量方法与复现

```bash
# 1) 获取上游源码(测量基准 v2.0.13;交叉基准 v2.0.12)
git clone --depth 1 --branch v2.0.13 https://github.com/anomalyco/opencode.git /tmp/oc-v2i18n-cov/upstream-v2013
git clone --depth 1 --branch v2.0.12 https://github.com/anomalyco/opencode.git /tmp/oc-v2i18n-cov/upstream-v2012

# 2) 字符串级覆盖账本(本单新增工具,只读)
python3 tools/v2_i18n_coverage.py --source-dir <v2 检出> [--json-out <路径>]

# 3) 条目级权威门禁(既有工具,回归对照)
cd cli-go && go build -trimpath -o /tmp/oc-v2i18n-cov/opencode-cli .
OPENCODE_SOURCE_DIR=<v2 检出> /tmp/oc-v2i18n-cov/opencode-cli apply --dry-run --strict --min-match-rate 1
OPENCODE_SOURCE_DIR=<v2 检出> /tmp/oc-v2i18n-cov/opencode-cli verify --dry-run
```

`tools/v2_i18n_coverage.py` 复用 `tools/v2spike_probe.py` 的 `load_rules / matches / is_simple_word`(与 `cli-go/internal/core/i18n.go` 的 `replacementMatches` 同语义:简单词 `^[a-zA-Z0-9]+$` 按 `\b` 边界,其余按子串;CRLF 归一化),因此脚本判「可迁移」的每一条都能被 apply 门禁机械复验。

## ③ 口径:什么算「用户可见界面串」

**产品面分层**

- **主宇宙(进账本)**:`packages/tui/src/**` + `packages/cli/src/**`。这是 V1 词表两个包族的 V2 后继,也是 opencode CLI/TUI 二进制的全部终端 UI 面——已核验 tui/cli 不 import 任何其它内部包(仅 `@opencode-ai/pty`)。
- **分流(只计数,不进主账本)**:`packages/<pkg>/**` 的独立产品面(app 桌面端 / console / web / ui 组件库 / session-ui / theme / plugin-browser / storybook 等)。V1/V2 资产不覆盖它们;是否纳入取决于产品决策,见 ⑦。

**文件过滤(产品文件)**:排除路径段 `test/tests/__tests__/e2e/storybook/fixtures/i18n/demo/component-tests/dist/node_modules`;basename 含 `.test./.spec./.stories./.bench./.fixture./demo/.d.ts`;扩展名 `.ts/.tsx/.js/.jsx`;跳过 >1MB 文件。v2.0.13 全树命中 **2512 个产品文件**(主宇宙 358,分流 2154)。

**字面量上下文(提取器 = 字符串状态机 + JSX 子解析)**:

| 上下文 | 定义 |
|---|---|
| `attr` | JSX 属性名 ∈ UI_ATTRS 的字符串/模板字面量(含 `name={a ? "X" : "Y"}` 表达式内括号深度 0 的分支) |
| `prop` | 对象属性名 ∈ UI_PROPS 的同名字面量(表达式内括号深度 0;箭头函数值 `label: () => "Restart"` 不截断) |
| `jsx-text` | JSX 文本节点(标签之间的渲染文本;含 render props/view props 里的嵌套 JSX 树,如 `emptyView={<Switch>…</Switch>}`) |
| `jsx-expr` | JSX 子表达式容器 `{cond ? "A" : "B"}` 中括号深度 0 的字面量 |
| `code` | 其余代码位置字面量 |

UI_ATTRS 白名单(title/desc/description/label/placeholder/message/hint/text/category/tooltip/aria-label/alt/empty/prompt/confirm/cancel/ok/subtitle/caption/notice/detail/details/header/display/summary/group/footer)依据:V1 词表键形态 + 对 v2.0.13 tui/cli 全树属性名频次调查(title×519 / description×193 / label×142 / category×132 / message×79 / text×52 / placeholder×18 / display×37 / group×258 / footer×13)。**不含** name/id/type/kind/variant/mode/status/value/keywords 等标识符/枚举/搜索词位。

**两档口径**:

- **Tier A(主口径,用户可见核心)** = attr/prop/jsx-text/jsx-expr 四类上下文 + 自然语言过滤。本文账本主数字。
- **Tier B(宽口径,敏感性上界)** = Tier A + code 上下文的自然语言字面量(错误/日志/throw 等裸文案;V1 词表历来也翻此类,如 `console.error` 串)。

**自然语言过滤**:含 ≥1 ASCII 字母;排除路径/URL/导入(`./`、`../`、`/` 开头、含 `://`、含 `\\`)、标识符样式单 token(`^[a-z][a-zA-Z0-9_]*$`)、纯符号/数字/hex/颜色、空串、true/false/null 等;模板字面量保留 `${...}` 原样(`${days}d ago` 的散片「d ago」有空格有字母,计);多行模板不计(V1 仅 1 条系统提示代码补丁属此类,非界面串)。

**去重口径**:`occurrences` = 逐出现次;`distinct` = 归一化(去首尾空白、压缩连续空白)后的去重值。**翻译工作量按 distinct 计**(同串多处出现 = 1 次翻译 + N 处锚点);同一个 distinct 值可能在一个文件 covered、在另一个文件 new——并集账本按「至少一处」归类,occurrence 级另列。

## ④ 规模统计(v2.0.13,按包分列)

**主宇宙(账本范围)**:

| 包 | distinct | occurrences | 涉及文件数 |
|---|---|---|---|
| packages/tui/src | 1267 | 2178 | 122 |
| packages/cli/src | 112 | 117 | 21 |
| **合计(并集去重)** | **1364** | **2295** | **143** |

**分流包(仅规模, Tier A 同口径;是否汉化属产品决策)**:

| 包 | distinct | occ | files | | 包 | distinct | occ | files |
|---|---|---|---|---|---|---|---|---|
| app | 688 | 1105 | 108 | | schema | 64 | 71 | 18 |
| core | 452 | 497 | 109 | | simulation | 22 | 24 | 5 |
| console | 426 | 769 | 61 | | plugin-browser | 20 | 20 | 4 |
| protocol | 313 | 315 | 32 | | client | 24 | 70 | 4 |
| stats | 190 | 252 | 17 | | codemode | 23 | 36 | 13 |
| session-ui | 111 | 182 | 22 | | ai | 103 | 127 | 41 |
| ui | 120 | 155 | 42 | | web | 54 | 103 | 5 |
| server | 48 | 61 | 19 | | theme/util/http-recorder/merman/latex/function/sdk | 25 | 27 | 12 |
| enterprise | 38 | 48 | 7 | | desktop | 38 | 40 | 14 |

(containers / httpapi-codegen / posts / script 四包 Tier A 为 0。)分流包合计约 2759 distinct(含跨包重复值)、3902 occ,约为主宇宙并集的 2.0 倍——若「完整中文 V2」包含桌面端/Web 端,工作量按此放大。

## ⑤ 交叉现有 V2 翻译资产:覆盖账本

判定谓词(与 apply 门禁同语义,对每个「文件 × 串」出现点):

| 类 | 判据 |
|---|---|
| `covered` | ∃ V2 资产锚点规则(目标文件 = 该串所在文件)键 K 命中该串 |
| `migratable` | 未覆盖,且 ∃ V1 词表键 K:K == 该串,或(K 非简单词且互相包含)——V1 已有译文,只需在 V2 重新锚定 |
| `fuzzy-simple` | 未覆盖且 V1 无整串译文,但 ∃ V1 简单词键 K 以 `\b` 命中该串(如 Skills ⊂ "Close and reopen Skills to try again.")——单词级模糊,直接锚定会产生中英混杂,需人工裁定 |
| `new` | 以上皆无——V2 新串,必须新翻译 |

**主宇宙账本(v2.0.13,Tier A)**:

| 类 | occurrences | distinct(至少一处归此类) | 占 distinct 比 |
|---|---|---|---|
| covered | 361 | 202 | 14.8% |
| migratable | 549 | 200 | 14.7% |
| fuzzy-simple | 103 | 90(仅此类) | 6.6% |
| new | 1282 | 939 | 68.8% |
| **合计** | **2295** | **1364** | 100% |

按 distinct 并集归并(一个值只归一次):

| 缺口处置 | 条数 | 占比 | 说明 |
|---|---|---|---|
| 全部出现点均已有现成译文(covered/migratable) | 335 | 24.6% | 零翻译工作量;其中 202 已锚定,余为锚定工作 |
| 单词级模糊待人工裁定 | 90 | 6.6% | fuzzy-simple only |
| 至少一处必须新翻译 | 939 | 68.8% | 见下方细分 |
| ——其中:确定从零新译 | 683 | 50.1% | pure-new 中无 V1 近似 |
| ——其中:可基于 V1 近似译文改编 | 240 | 17.6% | 54 高置信(归一相似度 ≥0.75)+ 186 待复核(0.6-0.75) |
| ——其中:变体混合(别处有译文、本处是改写) | 16 | 1.2% | 需逐处锚定/微调 |

**v2.0.12 交叉对照**(V2 资产生成基准):distinct 1349 / occ 2277 / files 142;covered 202、migratable 200、fuzzy-only 90 与 v2.0.13 **完全一致**,new 924(+16 漂移)。即:v2.0.12→v2.0.13 一个补丁版本只带来 16 条新串(更新服务错误族为主),账本结构稳定。

**与条目级门禁的关系(两个分母,勿混)**:门禁 252/501 的分母是 V1 派生的资产条目(含 99 条 V2 已删功能的 tips、7 个锚到 V2 不存在路径的 deferred 旧锚点、1 条无操作键);本账本 202/1364 的分母是 V2 实际需求(去重 UI 串)。门禁 50.3% 高估覆盖、串级 14.8% 低估迁移空间(它只数已锚定),合并看:迁移路线总天花板 = (covered ∪ migratable) = **351/1364 = 25.7%**。

**Tier B(宽口径,主宇宙,敏感性上界)**:covered 46 occ/46 distinct;migratable 87 occ/52 distinct;fuzzy-simple 149 occ/85 distinct;new **3007 occ / 1879 distinct**。若「完整中文」含错误/日志文案,在此基础上追加。

## ⑥ 质量校验与已知盲区

1. **召回校验**(对 v2.0.12):门禁命中的 252 条资产键中 **240 条(95.2%)** 对应到提取出的 UI 串。未对应的 12 条全部是盲区类:`"Recent"`/`"Today"`(数组元素/调用参数位)、`done`/`cancelled`/`error`/`running`(函数返回值位)、`Cancel`/`Confirm`/`Reject`(permission.ts 的 return 位)、`Session`(splash.ts 的 const 赋值位)、`placeholder={placeholderText()}`(无操作键,译文=原文,正确地不算 UI 串)。
2. **污染校验**:主宇宙(tui/cli)jsx-text 节点混入代码(含 function/const/import/=>/&& 等)为 **0**;全树残余 14 个,均在分流包且多为法律条款正文(含 "function" 等词正常散文)。提取器对 `.ts`(无 JSX)跳过 JSX 解析、对泛型(`type Trace = <T>(...)`、`<DialogSelect<Foo | Bar>>`)不误判。
3. **盲区规模(已量化,未计入)**:tui+cli 产品文件中处于 code 位置的「首字母大写单词」字面量共 **212 处**(Tier B 收紧规则的代价,多为函数返回值/数组元素位的单词标签,如上述 12 条命中键即出自此类);「小写单词」6525 处基本是代码标识符,不计入是正确的。
4. **模糊匹配判据**:可改编类的近似度用 difflib 对归一化文本(`${...}`→`X`、转小写、去符号)计算,要求归一长度 ≥10(排除对片段键的短串噪声),阈值 0.75/0.6 两档;样例:`"Waiting for permission event…" ↔ "Waiting for permission event..."`(1.00)、`"Update available" ↔ "Update Available"`(1.00)、`"No agents found" ↔ "No subagents found"`(0.91)。

## ⑦ 结论与工作量

**回答核心问题:是,必须对 V2 源码做一轮新翻译。**

- 现有 V2 资产(PR #4/#5 后)已锚定 202/1364(14.8%)条 V2 界面串;把 V1 词表里所有可整串迁移的条目重新锚定到 V2,也只把覆盖推到 **351/1364(25.7%)**——这是「不新翻一个词」的理论上限(且其中 200 条的锚定工作还需人工复核,PR #5 已证明剩余 deferred 多属无共识/弱证据/标识符碰撞)。
- **939 条(68.8%)** 必须产出新译文:683 条从零翻译、240 条基于 V1 近似译文改编、16 条变体混合;另有 90 条单词级模糊需人工裁定(直接锚定有中英混杂风险)。
- 门禁口径必须重建:100% 匹配门禁在 V2 不可达(50.3%),建议阶梯阈值或双轨(资产条目级 + 串级覆盖),否则 nightly 永远红。

**工作量量级**(速率为估计值,非实测):

| 工作项 | 量 | 估算 | 依据 |
|---|---|---|---|
| 从零新译(Tier A) | 683 条 | ~7 人天 | 带上下文人工翻译+复核,按 100 条/人天 |
| V1 近似改编 | 240 条 | ~1.5 人天 | 改编比新译快,按 150 条/人天 |
| 单词模糊裁定 | 90 条 | ~0.5 人天 | 多为确认/微调 |
| 锚定机械化(deferred→V2 位置) | 200 条值的锚点 | ~1-2 人天 | 扩展 `v2_anchor_migrate.py` 的消歧规则+人工复核 |
| 门禁口径重建 | — | ~0.5-1 人天 | 阶梯/双轨阈值 |
| **Tier A 完整合计** | — | **~2-3 人周** | |
| Tier B(错误/日志文案) | 1879 distinct | 再 +3-4 人周 | 按 500 条/人天(格式较固定) |
| 后续每个上游小版本增量 | ~16 条/版(实测) | ~0.5 人天/次 | v2.0.12→v2.0.13 实测 |

**产品面决策(需人拍板)**:分流包(app 桌面端 688 / console 426 / core 452 / protocol 313 …)合计约 3056 distinct,是主宇宙的 2.2 倍。若「完整中文 V2」只指 CLI/TUI 二进制,本账本即全貌;若含桌面端/Web/控制台,需另立测量单(同工具改 `--source-dir` 即可复算)。

## ⑧ 合规自查

- 只读:未改 V1/V2 翻译资产、未改产品代码、未改 `.github/`、未改任何 workflow;V1 门禁未动。
- 本单零翻译:未产出任何中文译文写入资产。
- 未推 upstream;未触碰 `/root/xiangmudata_sync/opencode-v2-cn/`(自保存复刻仓)。
- 新增仅两处:`tools/v2_i18n_coverage.py`(统计脚本)、`docs/opencode-v2-i18n-coverage.md`(本报告)。
- 复现确定性:脚本输出仅取决于 `--source-dir` 与仓库内资产;JSON 报告用 `mkstemp`+`os.replace` 原子写;退出码契约 0=完成 / 2=预期内失败。
- 文中所有数字来自上述命令的真实运行输出(v2.0.13 主运行 + v2.0.12 交叉运行 + go 二进制门禁),无硬编。
