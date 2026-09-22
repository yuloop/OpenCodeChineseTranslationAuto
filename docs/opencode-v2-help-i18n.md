# opencode V2 · `--help` 末批英文收口(commands.ts 行内 flag/arg 描述汉化)

- 日期:2026-09-23
- 分支:`feat/v2-help-i18n`(基于 main `c1df40d53`,PR #15 已合并)
- 性质:把上游 `packages/cli/src/commands/commands.ts` 的行内 `Flag.withDescription(...)` / `Argument.withDescription(...)` 可见串整理成 **V2 资产 replacements** 并落地;来自 `effect/unstable/cli` 库、锚定必误伤的串列入「保持英文」清单。**只改 V2 专用文件(V2 资产 + V2 nightly 工作流 + 本报告);V1 线一个字都没动。**
- 结论一句话:**commands.ts 全部 69 条 distinct(84 处)行内 flag/arg 描述已按 V1 术语译成中文并落入 V2 资产;门禁 2085/2085 = 100% 维持全绿,V1 仍 497/497 = 100%,两棵纯净树真 apply 对拍证明代码位零误伤 / 占位符残留 0 / 引号行数守恒;GLOBAL FLAGS 描述与分区标题属 `effect/unstable/cli` 库串,按设计保持英文。**

---

## ① 背景与根因(承接上一单)

上一单(`docs/opencode-v2-release.md` ⑩)实证:`--help` 新版与旧版逐字节相同、英文仍在;根因是这些串属上游 `commands.ts` 行内字面量 + `effect/unstable/cli` 库串,**不属现有 2016 条 replacement**,注入流水线结构上碰不到它们。本单收口这项工作。

上一单点名的「顶层 `--help` 13 条」= flag 说明 6 + ARGUMENTS 区 1 + GLOBAL FLAGS 6。本单不止于此:按任务要求把 `commands.ts` 里**全部**行内 flag/arg 可见串列全并落数(见 ②),逐条判定(见 ④)。

## ② 列全与落数(commands.ts 行内可见串)

以测量基准上游 `v2.0.13`(commit `3180aab16e`)为准,对 `packages/cli/src/commands/commands.ts` 全文做正则抽取(`(Flag|Argument)\.withDescription(<字符串字面量>)`):

| 维度 | 数量 |
|---|---|
| `Flag.withDescription(...)` distinct | 48 |
| `Argument.withDescription(...)` distinct | 21 |
| **distinct 合计** | **69** |
| 出现次数合计(occurrences) | 84 |

> 84 > 69 是因多条描述在多个子命令复用同一字面量,例如 `Continue the last session`(root/mini/run 各 1 次)、`Session ID to continue`(×3)、`Output format`(×3)、`Prompt to use`(×2)、`Agent to use`(×2)、`Name of the MCP server`(×3)、`Service setting or env`(×3)、`Environment variable name`(×2)、`Integration ID or name`(×2)、`Credential ID or label (...)`(×2)。按 distinct 计翻译工作量,一次译文 + N 处锚点。

**分区标题来源(已查清)**:`DESCRIPTION / USAGE / ARGUMENTS / FLAGS / GLOBAL FLAGS / SUBCOMMANDS` 六个分区标题**不在** `commands.ts`,而由 `effect/unstable/cli` 库在渲染 help 时 push(见 ③),属库串。

## ③ 库串来源实证(effect@4.0.0-rc.112)

opencode v2.0.13 的 `package.json` catalog 固定 `effect: 4.0.0-rc.112`。对该版本库源码取证:

| 可见串 | 来源文件:行 | 形态 |
|---|---|---|
| 分区标题 ×6 | `effect/dist/unstable/cli/CliOutput.js`(225/230/235/256/277/300) | `sections.push(colors.bold("DESCRIPTION"))` 等 |
| `--help, -h` Show help information | `effect/dist/unstable/cli/GlobalFlag.js:66` | `Flag.withDescription("Show help information")` |
| `--version, -v` Show version information | `GlobalFlag.js:87` | 同上 |
| `--wizard` Start wizard mode for a command | `GlobalFlag.js`(wizard setting) | 同上 |
| `--completions` Print shell completion script | `GlobalFlag.js:109` | 同上;`(choices: bash, zsh, fish, sh)` 由框架从 choice 数组自动拼接 |
| `--log-level` Sets the minimum log level | `GlobalFlag.js:130` | 同上;`(choices: all|trace|...)` 同理自动拼接 |

> `commands.ts` 全文 532 行已逐行核读:上述 11 条一条都不在其中;`packages/cli/src` 全目录亦无 `wizard` 字样(仅 `packages/core/src/util/slug.ts` 的词表数组有无关注释)。`framework/spec.ts` 仅包装 `Command.make` + `Command.withDescription`,global flags 由 effect CLI 框架自动挂载。

## ④ 逐条判定

判定谓词(与 apply 门禁同语义,见 ⑧):find-key 取**完整调用文本**(`Flag.withDescription("…")` 含前缀、引号、右括号),非简单词 → 子串匹配,命中即整串替换、保留全部代码骨架。

**判定 A — 可安全锚定,翻译并落入 V2 资产(69 条 distinct)**:全部为 `commands.ts` 行内 `Flag/Argument.withDescription(...)`。理由:
- find-key 含完整代码上下文 + 收尾 `")`,不与任何标识符/占位符/既有 `description: "…"` 键相撞;
- 无 `${...}` 模板占位符(均为普通双/单引号字面量),无占位符误伤风险;
- 复用字面量(如 `Output format` ×3)语义一致,一处译文多处落地正是所需;
- 易混对已用「收尾引号 + 括号」天然区分:`Model to use .../provider/model` vs `.../provider/model#variant`、`Configured package target` vs `Configured package target; omit...`——前者 find 串以 `model")`/`target")` 结尾,不会命中后者的 `model#variant")`/`target; omit...")`。

**判定 B — 来自上游框架、锚定必误伤,保持英文(11 条)**:即 ③ 表中 6 分区标题 + 5 条 GLOBAL FLAGS 描述。理由(三重,任一即足够):
1. **库串随依赖变动、构建时被重取**:它们位于 `node_modules/effect/...`;V2 构建 `Build()` 在编译前调用 `InstallDependencies`(`internal/core/build.go:299`,内部 `bun install`),发生在 nightly 的 apply 步骤**之后**,会依 lockfile 重取/ reconciliation `node_modules/effect`,任何对库文件的补写都会被覆盖——锚定在结构上无效。
2. **apply 无法干净指向 node_modules**:`GetTargetFilePath` 仅对 `packages/` 前缀路径原样拼接;非 `packages/` 路径会被拼成 `packages/opencode/<...>`(V1 兼容分支),node_modules 路径会被改写错位,无法作为锚点目标(且修 Go 属禁改门禁逻辑)。
3. **分区标题是通用短词**:`FLAGS` 若按 `\b` 边界锚定,会命中 `GLOBAL FLAGS` 及任意 `FLAGS`/`flags` 标识符;`USAGE`/`DESCRIPTION` 等同理,误伤面极大。

## ⑤ 保持英文清单(11 条,不硬翻)

| 串 | 类别 | 保持英文理由 |
|---|---|---|
| `DESCRIPTION` / `USAGE` / `ARGUMENTS` / `FLAGS` / `GLOBAL FLAGS` / `SUBCOMMANDS` | 分区标题 | 通用短词,`\b` 锚定会互撞(FLAGS⊂GLOBAL FLAGS)并误伤代码标识符;库串,构建时 bun install 重取 |
| `Show help information`(`--help, -h`) | GLOBAL FLAGS | `effect/unstable/cli` 库串(GlobalFlag.js),node_modules 内,构建时重取 |
| `Show version information`(`--version, -v`) | GLOBAL FLAGS | 同上 |
| `Start wizard mode for a command`(`--wizard`) | GLOBAL FLAGS | 同上(effect GlobalFlag setting) |
| `Print shell completion script`(`--completions`) | GLOBAL FLAGS | 同上;`(choices: …)` 由框架自动拼接 |
| `Sets the minimum log level`(`--log-level`) | GLOBAL FLAGS | 同上;`(choices: …)` 由框架自动拼接 |

> 另:身份锚点(键位提示/枚举值/命令 id)按既有设计保持原文,不属本单范围。

## ⑥ 译文条目表(69 条 distinct,按 V1 术语)

术语口径取自 V1 词表实证:session→会话、agent→智能体(subagent→子代理)、model→模型、provider→提供商、plugin→插件、server→服务器、configuration→配置、prompt→提示、fork→分支、attach→附加、message→消息、export→导出。标点沿用 commands.ts 既有锚点半角括号 `()` + 枚举用 `、`。技术令牌(--standalone / --no-replay / provider/model#variant / name=value / name:value / HTTP(S) / JSON / URL / ID / N)全部原样保留。

| # | 源码调用(英文,节选) | 类型 | 中文译文(节选) |
|---|---|---|---|
| 1 | `Additional allowed CORS origin (repeat for multiple origins)` | Flag | 额外允许的 CORS 来源(多个来源重复使用) |
| 2 | `Advertise an external HTTP(S) server URL in the pairing QR code` | Flag | 在配对二维码中公布外部 HTTP(S) 服务器 URL |
| 3 | `Agent to use` | Flag | 要使用的智能体 |
| 4 | `Authentication method ID` | Flag | 认证方式 ID |
| 5 | `Auto-approve permissions that are not explicitly denied` | Flag | 自动批准未被明确拒绝的权限 |
| 6 | `Connect to a server URL instead of the background service` | Flag | 连接到服务器 URL,而非后台服务 |
| 7 | `Continue the last session` | Flag | 继续上一个会话 |
| 8 | `Directory in which to import the session` | Flag | 用于导入会话的目录 |
| 9 | `Environment variable for a local server, as name=value` | Flag | 本地服务器的环境变量,格式为 name=value |
| 10 | `File to attach to the message` | Flag | 要附加到消息的文件 |
| 11 | `Filter by project ID, or use "." for the current project` | Flag | 按项目 ID 过滤,或使用 "." 表示当前项目 |
| 12 | `Fork the session before continuing` | Flag | 继续前分支会话 |
| 13 | `Fork the session when continuing` | Flag | 继续时分支会话 |
| 14 | `HTTP header for a remote server, as name=value` | Flag | 远程服务器的 HTTP 头,格式为 name=value |
| 15 | `Include built-in server plugins` | Flag | 包含内置服务器插件 |
| 16 | `Installation method to use` | Flag | 要使用的安装方式 |
| 17 | `Keep configuration files` | Flag | 保留配置文件 |
| 18 | `Keep session data and snapshots` | Flag | 保留会话数据和快照 |
| 19 | `Limit replay to the newest N messages (default: 200)` | Flag | 将重放限制为最新的 N 条消息(默认:200) |
| 20 | `Limit to N most recent sessions (default: 100)` | Flag | 限制为最近 N 个会话(默认:100) |
| 21 | `Model to use in the format provider/model` | Flag | 要使用的模型,格式为 provider/model |
| 22 | `Model to use in the format provider/model#variant` | Flag | 要使用的模型,格式为 provider/model#variant |
| 23 | `Number of rows in detailed sections` | Flag | 详细部分的行数 |
| 24 | `OpenAPI path or query parameter` | Flag | OpenAPI 路径或查询参数 |
| 25 | `Output format` | Flag | 输出格式 |
| 26 | `Output statistics as JSON` | Flag | 以 JSON 格式输出统计 |
| 27 | `Print logs to stderr (server logs require --standalone)` | Flag | 将日志打印到 stderr(服务器日志需要 --standalone) |
| 28 | `Prompt to use` | Flag | 要使用的提示 |
| 29 | `Provider form answer (key=value; repeat for multiple fields)` | Flag | 提供商表单答案(key=value;多个字段重复使用) |
| 30 | `Redact sensitive transcript and file data` | Flag | 脱敏敏感的会话记录和文件数据 |
| 31 | `Request body` | Flag | 请求体 |
| 32 | `Request header in name:value form` | Flag | 请求头,格式为 name:value |
| 33 | `Restore session history on resume and resize (disable with --no-replay)` | Flag | 在恢复和调整大小时还原会话历史(用 --no-replay 禁用) |
| 34 | `Run with a private server instead of the background service` | Flag | 使用独立服务器运行,而非后台服务 |
| 35 | `Session ID to continue` | Flag | 要继续的会话 ID |
| 36 | `Session title` | Flag | 会话标题 |
| 37 | `Show a calendar year` | Flag | 显示一个日历年 |
| 38 | `Show cost and token details` | Flag | 显示费用和令牌详情 |
| 39 | `Show every detailed section` | Flag | 显示每个详细部分 |
| 40 | `Show lifetime statistics` | Flag | 显示累计统计 |
| 41 | `Show model usage` | Flag | 显示模型使用情况 |
| 42 | `Show the last N days; 0 means today` | Flag | 显示最近 N 天;0 表示今天 |
| 43 | `Show thinking blocks` | Flag | 显示思考块 |
| 44 | `Show tool reliability` | Flag | 显示工具可靠性 |
| 45 | `Show what would be removed without removing` | Flag | 显示将被移除的内容,但不实际移除 |
| 46 | `Skip confirmation prompts` | Flag | 跳过确认提示 |
| 47 | `URL for a remote MCP server` | Flag | 远程 MCP 服务器的 URL |
| 48 | `Write to the global config instead of the project config` | Flag | 写入全局配置而非项目配置 |
| 49 | `Command and arguments for a local server, passed after --` | Argument | 本地服务器的命令和参数,在 -- 之后传递 |
| 50 | `configured package specifier` | Argument | 已配置的包指定符 |
| 51 | `Configured package target` | Argument | 已配置的包目标 |
| 52 | `Configured package target; omit to update all outdated plugins` | Argument | 已配置的包目标;省略则更新所有过期的插件 |
| 53 | `Credential ID or label (opens an account picker when omitted)` | Argument | 凭据 ID 或标签(省略时打开账号选择器) |
| 54 | `Directory to start OpenCode in` | Argument | 启动 OpenCode 的目录 |
| 55 | `Environment variable name` | Argument | 环境变量名称 |
| 56 | `Environment variable value` | Argument | 环境变量值 |
| 57 | `Integration ID or name` | Argument | 集成 ID 或名称 |
| 58 | `Integration ID, name, or well-known provider URL` | Argument | 集成 ID、名称或知名提供商 URL |
| 59 | `JSON file or URL to import` | Argument | 要导入的 JSON 文件或 URL |
| 60 | `Message to send` | Argument | 要发送的消息 |
| 61 | `Name of the MCP server` | Argument | MCP 服务器的名称 |
| 62 | `npm registry or Git package specifier` | Argument | npm registry 或 Git 包指定符 |
| 63 | `OpenAPI operation ID, or an HTTP method followed by a path` | Argument | OpenAPI 操作 ID,或 HTTP 方法加路径 |
| 64 | `Print only one path: db, home, data, config, cache, state, tmp, bin, log, repos` | Argument | 仅打印一个路径:db、home、data、config、cache、state、tmp、bin、log、repos |
| 65 | `Service setting or env` | Argument | 服务设置或环境变量 |
| 66 | `Session ID to delete` | Argument | 要删除的会话 ID |
| 67 | `Session ID to export` | Argument | 要导出的会话 ID |
| 68 | `Setting value or environment variable name` | Argument | 设置值或环境变量名称 |
| 69 | `Version to upgrade to (with or without a leading v)` | Argument | 要升级到的版本(可带或不带前导 v) |

合计新增 69 条(distinct)

## ⑦ 复量数字(全部真实运行)

**门禁(apply --dry-run --strict --min-match-rate 1,基准 v2.0.13 纯净检出)**:

| 指标 | 本单前 | 本单后 |
|---|---|---|
| V2 替换匹配 | 2016/2016 (100.0%) | **2085/2085 (100.0%)** |
| V2 文件 | 227 成功 / 0 跳过 / 0 失败 | 227 成功 / 0 跳过 / 0 失败 |
| commands.ts | 45/45 | **114/114**(45 既有 + 69 新增) |

净增 69 条 = ⑥ 表 distinct 数;门禁维持全绿(`--strict --min-match-rate 1` 通过,rc=0)。

**V1 门禁(OPENCODE_SOURCE_DIR=V1 检出 `f54ce31`,apply --strict + verify --dry-run)**:497/497 = 100%(rc=0)、verify 覆盖率 100.0%。**V1 资产零改动**,复跑确认不受影响。

**真 apply 对拍(两棵纯净 v2.0.13):A=新资产(114)、B=旧资产(45),delta = 本单 69 条**:

| 校验项 | 结果 |
|---|---|
| 行数守恒(commands.ts,新 vs 纯净) | 532 = 532 ✅ |
| 双引号守恒 | 624 = 624 ✅ |
| 单引号守恒 | 2 = 2 ✅ |
| 占位符残留(cmpA 全树扫 `\x00`) | 0 文件 / commands.ts 0 字节 ✅ |
| delta 变更行数 | 84(= 全部 withDescription 出现次数)✅ |
| 非 withDescription 行被改 | 0 ✅ |
| 代码骨架被破坏的行(前缀/引号/后缀变动) | 0 ✅ |

> 对拍逻辑:逐行 diff A/B,剥离 `withDescription(<字符串>)` 后比对代码骨架;`\b`/子串命中、占位符 `\x00opencode-i18n-N\x00` 两级 staging 全部回填,故残留恒 0。84 变更行恰好等于 84 处 withDescription,证明改动**只**落在目标串内、零附带。

## ⑧ 落地方式(锚点设计)

- 改动文件:`cli-go/internal/core/assets/opencode-i18n-v2/anchors/packages-cli-src-commands-commands.ts.json`(既有 45 条 `description:` 条目**原样保留、零改动**,追加 69 条)。
- find-key 由脚本直接从上游源码抽取构造(保留 `Flag.`/`Argument.` 前缀与引号风格),杜绝手抄错字;单引号那条(`Filter by project ID, or use "." ...`)按源码保留单引号与内层 `"."`。
- 门禁按 distinct 计 69 条全命中;复用字面量一处 key 覆盖多处 occurrence。

## ⑨ 合规自查

- **V1 铁律**:`.github/workflows/opencode-cn-nightly.yml`、`release.yml`、`scripts/patch-build-ts.py`、V1 词表 `assets/opencode-i18n/`、cli-go 全部 Go 代码**零改动**;V1 门禁复跑 497/497 = 100% 实证。
- **未改门禁逻辑与阈值**:未动 `internal/core/i18n.go` / `apply.go` / `--min-match-rate` 语义;仅追加资产条目。
- **只动 V2 工作流**:`.github/workflows/opencode-cn-v2-nightly.yml` 仅更新 Release 正文模板第 369 行过期的「约 60 散点 + 237 keybind + 25 devtools 未译」表述为当前准确状态;YAML 校验通过;4 条中文落地验证引用译文仍在资产内。
- **未推 upstream**(`upstream` remote 保持 DISABLED);未碰 `/root/xiangmudata_sync/opencode-v2-cn/`。
- 改动文件:`git diff main --stat` = V2 资产 anchors(1)+ V2 nightly 工作流(1)+ 本报告(1)。
- 文中门禁数字、对拍数字、库串来源(effect@4.0.0-rc.112 CDN 取证)均为真实运行结果。

---

## ⑩ 二进制层 `--help` 实测(合并后发布,待回填)

PR 合并后重发 V2 Release、下载二进制实测 `--help`,逐字对比「本次改动前 vs 后」,结果回填于此(含:顶层 FLAGS/ARGUMENTS 是否变中文、GLOBAL FLAGS/分区标题是否仍英文、子命令 `--help` 抽样)。
