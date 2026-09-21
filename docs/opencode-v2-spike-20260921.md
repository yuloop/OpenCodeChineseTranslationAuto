# opencode V2 汉化跟进 · 本地预演 Spike 报告

- 日期:2026-09-21
- 范围:只做分析 + 本地演练。未推送任何远端(origin/upstream 均未 push),未触发/修改任何 GitHub Actions,仓库既有文件零改动(仅新增 `docs/opencode-v2-spike-20260921.md` 与 `tools/v2spike_probe.py`)。
- 上游对象:`anomalyco/opencode`(upstream 远端)。

## 结论摘要(TL;DR)

1. **上游 V2 发布线已确认 = tag `v2.0.12`(2026-09-21)+ npm 包 `@opencode/cli`(latest=2.0.12)**。分支 `2.0` 是 2026-04-13 的旧探索分支(对应 v1.4.x 线),**不是** V2 发布线;`dev` 仍是 V1 线(1.18.31)。
2. V1 汉化手法(对上游源码做字符串替换)**整体仍可行**,但当前 100% 匹配门禁在 V2 上不可达:对 `v2.0.12` 仅 **154/497(31.0%)**,对 `2.0` 分支仅 **9/497(1.8%)**。
3. 三大硬断点(均已确认):① 路径映射——50 个锚点源文件中 34 个还在、21 个不在;② `scripts/patch-build-ts.py` 对 V2 直接报错(V2 的 `build.ts` 已内建 `--target=`/`--outdir=`,补丁可退役);③ 版本解析——`packages/opencode/package.json` 在 V2 已不存在,应读 `packages/cli/package.json`(=2.0.12)。
4. 配置载体变化**确认**:界面配置 `tui.json` → `cli.json`(源码 + 官方 v2.0.12 二进制双证据),且带自动迁移(`cli.config.migrate`,keybinds 改为点号命名空间)。
5. 约 **280/497(56%)** 的锚点字符串在 V2 别处仍存在(可迁移);**217/497** 彻底消失(其中首页 tips 99 条整体消失)。
6. 完整构建**未实测**:本机无 bun(V2 要求 bun@1.4.2),按任务要求未硬装重型依赖,断点已记录。

---

## ① 现状:V1 汉化构建全流程

源码依据:`.github/workflows/opencode-cn-nightly.yml`、`.github/workflows/release.yml`、`.github/workflows/ci.yml`、`.github/workflows/opencode-cn-sync.yml`、`cli-go/`、`scripts/patch-build-ts.py`。

### 1.1 全流程清单(nightly 预览版,release 正式版同构)

| # | 步骤 | 位置/文件 | 说明 |
|---|---|---|---|
| 1 | 解析上游 commit | `opencode-cn-nightly.yml` job `resolve` | `gh api repos/anomalyco/opencode/commits/dev` 取最新 SHA;**版本号从 `packages/opencode/package.json` 的 `version` 读**;发布 tag = `v<上游版本>-cn-nightly-<SHA12>`;同名 tag 已存在则跳过 |
| 2 | 拉上游源码 | `actions/checkout`(`repository: anomalyco/opencode`,`ref: <sha>`,`path: build/upstream`,`fetch-depth: 1`) | 只读检出,**不 merge**,独立构建 |
| 3 | 构建汉化工具 | `cli-go/`(Go 1.25.4) | `go build -trimpath -o ../dist/opencode-cli .` |
| 4 | 翻译门禁 | `cli-go/cmd/apply.go`、`verify.go` | `OPENCODE_SOURCE_DIR=build/upstream`;`apply --dry-run --strict --min-match-rate 1`(**要求 100% 匹配**) + `verify --dry-run`;再 `python3 scripts/patch-build-ts.py build/upstream/packages/opencode/script/build.ts` 并 grep 补丁标记 |
| 5 | 应用翻译 + 构建 | `cli-go/internal/core/i18n.go`、`build.go` | `patch-build-ts.py` 给 `build.ts` 注入 `OPENCODE_BUILD_TARGET` 单目标过滤;`opencode-cli apply --strict` 真实改写源码(CRLF 归一化;简单单词按 `\b` 边界,其余按子串;占位符两段式防相互覆盖);`opencode-cli build --platform <p> --deploy=false`:放宽 `packages/script/src/index.ts` 的 bun 版本检查 → 根目录 + `packages/opencode` 两级 `bun install` → `@opentui/core|solid` workspace symlink 修补 → `bun run script/build.ts` |
| 6 | 打包发布 | nightly `release` job | 产物 `build/upstream/packages/opencode/dist/opencode-<platform>/bin/opencode` → zip(`windows-x64`/`linux-x64`) + 汉化工具 zip(`cli-go install.ps1 install.sh README.md CHANGELOG.md scripts`) + `SHA256SUMS` → `softprops/action-gh-release`;nightly 只保留最新 1 个预览 release |
| 7 | 安装侧 | `install.sh --preview`、`install-preview.ps1` | 从本仓库 releases 找最新 `-cn-nightly` 预览 tag,装到隔离目录(`~/.opencode-i18n-preview` / `%LOCALAPPDATA%\opencode-i18n-preview`) |
| 8 | 上游同步(另一条线) | `opencode-cn-sync.yml` | 每小时把 `upstream/dev` merge 进 `main`(`--allow-unrelated-histories -X ours`,workflow 目录整体还原为 HEAD 版本),仅同步不构建 |
| 9 | 仓库 CI | `ci.yml` | `gofmt -l cli-go`、`go test`/`go vet`、`py_compile scripts/patch-build-ts.py`、翻译 JSON 全量 `json.load`、`install.sh -n`、PowerShell 语法;`automation/` 是浏览器巡检工作流(与构建无关) |

### 1.2 翻译资产

- 位置:`cli-go/internal/core/assets/opencode-i18n/`(Go `//go:embed` 内嵌;若项目根存在外部 `opencode-i18n/` 目录则优先用外部,本仓库未使用)。
- 规模:**54 个规则 JSON、497 条替换、50 个目标源文件**(`config.json` 为元信息:版本 6.2、`supportedCommit 1.18.9`)。
- 规则结构:`{ "file": "<相对路径>", "replacements": { "<英文原文>": "<中文>" } }`。
- 目标文件分布(V1,按路径族精确计数):`packages/opencode/src/cli/cmd/run/*`(footer.command 29 / view 15 / prompt 21 / question 6 / permission 6 / subagent 1、permission.shared 7、splash 3,共 88 条)、`packages/tui/src/**`(323 条,含 `feature-plugins/home/tips-view.tsx` 99 条)、`src/cli/cmd/tui/**`(映射到 `packages/tui/src/`,76 条)、`packages/opencode/src/cli/error.ts`(9 条)、`src/session/system.ts`(1 条,实为代码修补)。
- 路径映射逻辑(`cli-go/internal/core/i18n.go` `GetTargetFilePath`):`packages/` 前缀原样;`src/cli/cmd/tui/` → `packages/tui/src/`;其余 → `packages/opencode/`。

---

## ② V2 影响面:现有汉化手法套到上游 V2 会断在哪

### 2.1 上游分支/标签事实(读操作,确认)

```
$ git ls-remote upstream | grep -E 'refs/heads/(2\.0|dev)$'
7a6ce05d0939826aa6c8e1c481489a713b2d633f	refs/heads/2.0
70a24697ea0028e19f22712fd63059538cb4bee7	refs/heads/dev
$ git ls-remote upstream | grep -c refs/heads/   # 1851 个分支
$ git ls-remote upstream | grep -c refs/tags/    # 1119 个 tag
$ git ls-remote upstream | grep 'refs/tags/v2.0'  # v2.0.0 … v2.0.12,共 13 个
2670273ff17da96f85c5826ced57aa1b368754fa	refs/tags/v2.0.12
```

- `dev`(70a24697)= V1 线:`packages/opencode/package.json` version=1.18.31,布局与 V1 汉化当前跟踪的一致(同时有 `packages/opencode` 和 `packages/tui`)。**确认**。
- tag `v2.0.12`(2670273,commit 时间 2026-09-21)= V2 发布线。**确认**。
- 分支 `2.0`(7a6ce05,2026-04-13)= 旧探索分支,`packages/opencode/package.json` version=1.4.3(对应 tag `v1.4.3`),TUI 合回 `packages/opencode/src/cli/cmd/tui/`。**确认**。
- `v2.0.12` 既不是 `dev` 也不是 `2.0` 的祖先(各取深度 300 后 `git merge-base --is-ancestor` 均否定)→ **V2 发布线对应的上游长期分支名:待验证**(1851 个分支未逐一排查)。
- npm:`@opencode/cli` latest=**2.0.12**(V2 发布包);`opencode-ai` latest=1.18.31(V1)。`v2.0.12` **没有 GitHub Release 对象**(releases API 最新仍是 v1.18.31)。**确认**。

### 2.2 包结构变化(v2.0.12,确认)

- 34 个包:`ai app cli client codemode console containers core desktop effect-drizzle-sqlite enterprise function http-recorder httpapi-codegen identity latex merman plugin-browser plugin posts protocol schema script sdk server session-ui simulation stats storybook theme tui ui util web`。
- **无 `packages/opencode`**;TUI 仍在 `packages/tui`;CLI 独立为 `packages/cli`(`src/run/`、`src/commands/`、`src/ui/`、`src/config/`);构建脚本在 `packages/cli/script/build.ts`。

### 2.3 翻译锚点失效清单(对 `v2.0.12` 跑 `apply --dry-run`,确认)

门禁结果:`26 成功 / 21 跳过 / 7 失败,154/497(31.0%)`,strict 退出码 1。

**A. 目标文件不存在(21 个规则文件,跳过即全条失败):**

| 失效锚点(V1 路径) | 条数 | V2 去向(探针定位) |
|---|---|---|
| `packages/opencode/src/cli/cmd/run/footer.command.tsx` | 29 | run 输出重写为 `packages/cli/src/run/noninteractive.ts`;部分字符串散入 `packages/tui/src/component/prompt/index.tsx` |
| `.../run/footer.view.tsx` | 15 | 同上(15/15 别处仍存在) |
| `.../run/footer.prompt.tsx` | 21 | 同上(18/21 别处仍存在) |
| `.../run/footer.question.tsx` | 6 | 别处仍存在 4/6 |
| `.../run/footer.permission.tsx` | 6 | 别处仍存在 5/6 |
| `.../run/footer.subagent.tsx` | 1 | 未找到 |
| `.../run/permission.shared.ts` | 7 | 别处仍存在 7/7 |
| `.../run/splash.ts` | 3 | 别处仍存在 2/3 |
| `packages/opencode/src/cli/error.ts` | 9 | 别处仍存在 8/9(探针) |
| `src/session/system.ts` | 1 | `packages/opencode/src/session/system.ts` 已被重写为 `prompt/*.txt` 体系,锚点代码不存在 |
| `packages/tui/src/feature-plugins/home/tips-view.tsx` + `tips.tsx` | 101 | **tips 功能整体消失**(`home/` 仅剩 `footer.tsx`),0 条可迁移 |
| `packages/tui/src/component/dialog-provider.tsx` | 19 | → `packages/tui/src/component/dialog-integration.tsx` 等(8/19 别处仍存在) |
| `src/cli/cmd/tui/**` 散落 7 个文件(routes/session/question、dialog-subagent、dialog-fork-from-timeline、footer、subagent-footer,component/dialog-tag,feature-plugins/sidebar/lsp) | 19 | 多数在 `packages/tui/src/**` 别处仍存在(探针 elsewhere 计数) |

**B. 文件在但 0 匹配(7 个,strict 计失败):** `packages/tui/src/ui/dialog.tsx`、`ui/dialog-alert.tsx`、`ui/dialog-help.tsx`、`routes/session/index.tsx`、`component/dialog-session-rename.tsx`、`component/dialog-mcp.tsx`、`component/prompt/autocomplete.tsx` —— 文件被重写,原字符串键失效,需逐条更新。

> 计数说明:门禁报「21 跳过」= 上表 20 个打印出的目标 + `components/component-sidebar.json`(0 条替换,静默跳过)。

**C. 仍部分匹配(26 个文件,154 条):** 主要集中在 `packages/tui/src/routes/session/**`、`component/dialog-model|mcp|stash|status|export|command|session` 等 —— V2 TUI 大量复用 V1 组件,这是 V2 汉化可行的基础。

**D. 探针量化(`tools/v2spike_probe.py`,对 `v2.0.12`):** 497 条锚点中 **280 条(56%)在 V2 `packages/` 全树别处仍存在**(换了文件,可迁移);217 条彻底消失(其中 tips 99 条)。对 `2.0` 旧分支:按「TUI 合回 `packages/opencode/src/cli/cmd/tui/」重映射后 307/497 可匹配——但该分支非发布线,仅作参考。

### 2.4 配置结构变化:tui.json → cli.json(确认)

- 源码:`packages/cli/src/config/config.ts` 读 `path.join(global.config, "cli.json")`;`packages/cli/src/config/schema.ts`:`SchemaURL = "https://opencode.ai/v2/cli.json"`。
- 二进制(v2.0.12)双证据:`strings` 可见 `https://opencode.ai/v2/cli.json`、`cli.json`、`tui.json` 并存;内置 `cli.config.migrate`:把 `<config>/tui.json` + `<state>/kv.json` 合并迁移为 `cli.json`(`$schema` 指向 v2/cli.json),keybinds 键名改为点号命名空间(如 `session_new` → `session.new`)。
- 影响面:V1 规则里 4 条教用户写 `tui.json` 的 tips 文案(在 `components/component-tips.json`,随 tips 一起消失);后续若汉化配置说明类文案,口径要改成 `cli.json`;用户既有 `tui.json` 由上游自动迁移,汉化版无需额外动作(**迁移触发条件待验证**)。

### 2.5 构建脚本涉及部分(确认)

- `scripts/patch-build-ts.py` 对 `v2.0.12` 的 `packages/cli/script/build.ts` **直接失败**:`RuntimeError: OpenCode build target declaration changed upstream`(标记 `const targets = singleFlag`、`await $\`rm -rf dist\`` 均不存在)。对 `2.0` 旧分支的 build.ts 仍能打上(证明脚本本身没坏,是上游改了)。
- V2 `build.ts` **已内建**单目标能力:`--target=<name>`(name 形如 `opencode-linux-x64`/`opencode-windows-x64`,由 `targetName()` 生成)与 `--outdir=`;产物布局不变:`<outdir>/opencode-<platform>/bin/opencode`。→ **补丁可以退役**,Go 侧 `Builder` 改为传 `--target=`。
- bun 版本:V2 要求 `bun@1.4.2`(root `packageManager`);`packages/script/src/index.ts` 的 semver 检查语句与 `PatchBunVersionCheck` 模式 1 一致,预计该修补仍可用(**待构建验证**)。

### 2.6 cli-go 工具与工作流涉及部分(确认/待验证)

| 项 | 位置 | V2 状态 |
|---|---|---|
| 路径映射 | `i18n.go GetTargetFilePath` | 确认失效:`packages/opencode` 不存在;`src/cli/cmd/tui/→packages/tui/src/` 的历史映射不再对应真实布局,需按 V2 重写 |
| 构建目录/产物路径 | `build.go`(`buildDir=packages/opencode`、`GetDistPath`) | 确认失效:应指向 `packages/cli` |
| workspace 修补 | `build.go ensureWorkspaceLinks`(`@opentui/core|solid`) | 待验证(V2 依赖 `@opentui/solid/bun-plugin`,包名可能仍相同) |
| bun 版本修补 | `build.go PatchBunVersionCheck` | 语句仍在,**待构建验证** |
| 覆盖率扫描 | `verify.go`(只走 `packages/opencode/src`) | 确认失效:V2 无此目录,扫描被跳过;口径需重定义(是否覆盖 `packages/tui`+`packages/cli`+`session-ui` 等) |
| 版本解析 | nightly/release `resolve` job(`packages/opencode/package.json`) | 确认失效:应读 `packages/cli/package.json`(=2.0.12) |
| latest release 解析 | release.yml(`gh api releases/latest`) | 确认失效:V2 无 GitHub Release;改用 tag 轮询或 npm `@opencode/cli` dist-tag |
| 门禁阈值 | `--min-match-rate 1` | 确认不可达(31%):需过渡策略(见 ⑤) |
| 新包 UI 覆盖 | `packages/session-ui`、`theme`、`app`、`plugin-browser` | **待验证**是否含面向终端用户的 UI 字符串(探针索引已覆盖 `packages/` 全树,可复跑) |

---

## ③ 本地预演:真实过程与输出

工作区:`/tmp/oc-v2spike/`(系统临时目录,`oc-` 前缀;完工已删,含失败路径)。工具链:go1.26.0、python3.14;**本机无 bun**。

### 步骤 1 — 确认上游 V2 分支/标签(读操作)

```
$ git ls-remote upstream > /tmp/oc-remote-refs.txt   # 27319 个 ref
$ grep -E 'refs/heads/(2\.0|main|dev|master)$' /tmp/oc-remote-refs.txt
7a6ce05d0939826aa6c8e1c481489a713b2d633f	refs/heads/2.0
70a24697ea0028e19f22712fd63059538cb4bee7	refs/heads/dev
$ grep refs/tags/v2.0 /tmp/oc-remote-refs.txt | tail -3
9eb6902aaf3c35ce985b67c605a775992249066b	refs/tags/v2.0.11
2670273ff17da96f85c5826ced57aa1b368754fa	refs/tags/v2.0.12
```

无 `main`/`master` 分支;V2 = tag 线(见 2.1)。

### 步骤 2 — 浅克隆 `2.0` 分支并跑翻译干跑(先验分支,再纠偏)

```
$ git clone --depth 1 --branch 2.0 https://github.com/anomalyco/opencode.git /tmp/oc-v2spike/upstream
7a6ce05 2.0 exploration (#22335)
$ cd cli-go && go build -trimpath -o /tmp/oc-v2spike/opencode-cli .        # 成功
$ OPENCODE_SOURCE_DIR=/tmp/oc-v2spike/upstream ./opencode-cli apply --dry-run --strict --min-match-rate 1
  提示: 使用内置汉化配置
  找到 54 个配置文件
  ⚠ packages/tui/src/app.tsx 跳过: 目标文件不存在        (52 个文件同类跳过)
  ✗ src/session/system.ts 失败
  ✓ packages/opencode/src/cli/error.ts (9/9 处替换)
汉化模拟完成:
  📁 文件: 1 成功, 52 跳过, 1 失败
  📝 替换: 9/497 成功 (1.8%)
Error: 汉化质量门禁未通过: 匹配率 1.8%，要求至少 100.0%，失败文件 1
REAL_EXIT=1
```

同时确认 `2.0` 分支非发布线(commit 时间 2026-04-13;`packages/opencode/package.json`=1.4.3),转而取 `v2.0.12`:

```
$ git fetch --depth 100 origin tag v2.0.12 && git merge-base --is-ancestor v2.0.12 2.0   # 非祖先
$ git fetch --depth 300 origin +refs/heads/dev:refs/remotes/origin/dev && git merge-base --is-ancestor v2.0.12 origin/dev  # 非祖先
$ git worktree add /tmp/oc-v2spike/upstream-v2012 v2.0.12
HEAD is now at 2670273f release: v2.0.12
```

### 步骤 3 — 对 `v2.0.12` 跑翻译门禁(核心预演)

```
$ OPENCODE_SOURCE_DIR=/tmp/oc-v2spike/upstream-v2012 ./opencode-cli apply --dry-run --strict --min-match-rate 1
  ✓ packages/tui/src/app.tsx (29/39 处替换)      (26 个文件成功)
  ⚠ packages/opencode/src/cli/cmd/run/footer.command.tsx 跳过: 目标文件不存在   (21 个跳过)
  ✗ packages/tui/src/component/prompt/autocomplete.tsx 失败                  (7 个失败)
汉化模拟完成:
  📁 文件: 26 成功, 21 跳过, 7 失败
  📝 替换: 154/497 成功 (31.0%)
Error: 汉化质量门禁未通过: 匹配率 31.0%，要求至少 100.0%，失败文件 7
REAL_EXIT=1
```

```
$ OPENCODE_SOURCE_DIR=/tmp/oc-v2spike/upstream-v2012 ./opencode-cli verify --dry-run
[3/4] 模拟运行检查...
  📝 替换: 154/497 可匹配
  ⚠️ 343 条翻译在源码中找不到匹配
[4/4] 检查汉化覆盖率...
  ⚠️ 源码目录不存在，跳过覆盖率检查        # 只扫 packages/opencode/src,V2 没有
```

### 步骤 4 — 探针量化(`tools/v2spike_probe.py`,本次新增)

```
$ python3 tools/v2spike_probe.py --source-dir /tmp/oc-v2spike/upstream-v2012 --json-out /tmp/oc-v2spike/probe-v2012.json
规则文件: 54  翻译条目: 497
V1 映射目标存在: 34/54
V2 候选路径存在: 0/54            # 候选按 2.0 分支布局猜的,v2.0.12 不适用
V2 候选路径上可匹配: 0/497
锚点字符串在 V2 别处仍存在: 280/497
...
components/component-tips.json   99   -   -     0     0     # tips 整体消失
dialogs/cli-footer-view.json     15   -   -     0    15     # 全部换了文件
dialogs/dialog-provider.json     19   -   -     0     8     # → dialog-integration.tsx 等
routes/route-session.json        57   Y   -     0    39     # 多数换到 routes/session/index.tsx
```

退出码契约已验证:缺目录 → stderr + exit 2;`py_compile` 通过。

### 步骤 5 — 构建脚本补丁检查

```
$ python3 scripts/patch-build-ts.py /tmp/oc-v2spike/upstream-v2012/packages/cli/script/build.ts
RuntimeError: OpenCode build target declaration changed upstream     # 对 v2.0.12 失败
$ python3 scripts/patch-build-ts.py /tmp/oc-v2spike/upstream/packages/opencode/script/build.ts
Patched build.ts for a single cross-platform target: ...              # 对 2.0 分支仍成功
```

V2 `build.ts` 关键片段(第 25/53-63 行):

```ts
const singleFlag = process.argv.includes("--single")
const requestedTarget = process.argv.find((arg) => arg.startsWith("--target="))?.slice("--target=".length)
const targets = requestedTarget ? allTargets.filter((item) => targetName(item) === requestedTarget) : ...
if (!targets.length) throw new Error(`Unknown build target: ${requestedTarget}`)
```

产物布局与 V1 一致:`path.join(outdir, name, "bin", binary)`(name=`opencode-<os>-<arch>`)。

### 步骤 6 — 二进制对照(只读)

```
$ /root/.hermes/cache/scratch/ocv2/opencode --version
opencode v2.0.12
$ strings .../ocv2/opencode | grep -E "^(cli|tui)\.json$"
cli.json
tui.json
# 进一步定位到 https://opencode.ai/v2/cli.json 与 cli.config.migrate 代码(见 2.4)
```

### 未跑通/断点记录

| 断点 | 缺什么 | 预估补什么 |
|---|---|---|
| 完整构建(`opencode-cli build`) | 本机无 bun;V2 要求 bun@1.4.2 | 装 bun 1.4.2 + 根/包级 `bun install`(monorepo,耗时依赖网络);`packages/cli/script/build.ts` 还会下载 `@parcel/watcher-<os>-<arch>` 与 opencode-pty 二进制 |
| `--target` 传参与 Go Builder 改造 | `build.go` 硬编码 `packages/opencode` 与 `--single` 逻辑 | 改 `buildDir=packages/cli` + 传 `--target=opencode-<platform> --outdir=dist` |
| V2 nightly 跟踪对象 | V2 发布线长期分支名未知 | 先用 tag 轮询(`v2.0.x` latest);或向上游确认发布流程 |

---

## ④ 阻塞点与未知项

**需要人/需要新决策:**

1. **V2 发布线的上游分支名未知**:`dev`=V1、`2.0`=旧探索、`v2.0.12` 无对应长期分支(深度 300 内非二者祖先)。nightly 跟分支还是跟 tag,需定。(需要人:向上游确认发布流程。)
2. **翻译门禁阈值迁移策略**:31% 距 100% 甚远,直接卡死。选项:分文件灰度 / 匹配率阶梯(如 0.6→0.8→1.0)/ 双轨(V1 线维持 100%,V2 线单独阈值)。需决策。
3. **217 条彻底失效锚点的处置**:其中首页 tips 101 条随功能消失(弃翻 or 翻到新去处);run footer 78 条大部分在 `packages/tui/src/component/prompt/index.tsx` 等别处复活(迁移即可)。弃/迁/翻需人工决策 + 翻译工作量。
4. **发布通道与 tag 命名**:上游 V2 无 GitHub Release,但本仓库自建 release 不受影响;需确认 nightly tag 模式(`v2.0.12-cn-nightly-<sha12>`)与 install 脚本预览逻辑是否原样可用(预计可用,待联调)。
5. **`cli.json` 迁移行为**:上游自动迁移 `tui.json`→`cli.json`,汉化版是否要做兼容/提示,待验证迁移触发条件后定。

**待验证(查不到,不编):**

- V2 长期分支名与发布节奏;`@opencode/cli` 与 `opencode-ai` 两包发布如何分工。
- `packages/session-ui`、`packages/theme`、`packages/app`、`packages/plugin-browser` 是否含终端 UI 字符串(探针可复跑,但需人工判定是否需要汉化)。
- bun 1.4.2 下完整构建能否在现有 45 分钟 CI job 内跑通(未实测)。
- `PatchBunVersionCheck`、`ensureWorkspaceLinks` 在 V2 的实际行为(语句还在,未构建验证)。
- `verify` 覆盖率口径重定义后,50→? 个目标文件的新基线。

---

## ⑤ 建议路线

### 5.1 分支策略

- 本仓库新建 V2 跟踪分支(短名,如 `v2-track`),`main` 继续 V1 汉化线;两者门禁与翻译资产(可先同仓共用、后拆分)互不阻塞。**不建议**直接在主线上切换(门禁会立即卡死所有发布)。
- 上游跟踪对象:V2 线先按 **tag 轮询**(`v2.0.x` 最新 tag,可经 npm `@opencode/cli` dist-tag 或 `git ls-remote --tags` 获取),长期分支名待向上游确认后再切。
- 本单未创建任何分支/工作流,以上为建议。

### 5.2 CI 改动点(按优先级)

| 优先级 | 改动 | 文件 | 说明 |
|---|---|---|---|
| P0 | 版本解析 | `opencode-cn-nightly.yml` / `release.yml` `resolve` | `packages/opencode/package.json` → `packages/cli/package.json`;`gh api releases/latest` → tag 轮询或 npm dist-tag;`UPSTREAM_BRANCH: dev` → V2 tag/分支 |
| P0 | 构建传参 | `scripts/patch-build-ts.py`(退役)、nightly/release 的 build 步、`cli-go/internal/core/build.go` | 删补丁调用与 grep 门禁;`Builder` 传 `--target=opencode-<platform> --outdir=dist`,`buildDir` 指向 `packages/cli` |
| P0 | 跑通一次完整构建 | 本地/CI | 装 bun 1.4.2,记录依赖下载与耗时,验证 45min job 预算 |
| P1 | 路径映射重写 | `cli-go/internal/core/i18n.go` | 按 V2 布局重写 `GetTargetFilePath`;`verify.go` 覆盖率扫描根目录改 `packages/`(或 tui+cli+session-ui) |
| P1 | 翻译资产迁移 | `cli-go/internal/core/assets/opencode-i18n/**` | 用探针 elsewhere 清单做别名迁移(21 个找不到的重新定位、7 个 0 匹配的更新键、tips 101 条决策弃/迁);每迁一批跑一次 `apply --dry-run` 看匹配率 |
| P1 | 门禁阈值过渡 | nightly/release V2 副本 | 迁移期用阶梯 `--min-match-rate`(或文件级 100%),达标后收回 1.0 |
| P2 | 覆盖率口径 | `verify.go` + 规则资产 | 纳入 V2 新包的终端 UI 文件,重建「已配置文件」基线 |
| P2 | `cli.json` 兼容 | 规则资产 + 安装脚本 | 验证上游迁移触发条件;配置说明类文案口径改 `cli.json` |

### 5.3 粗工作量评估

- **P0(约 1-2 人天)**:resolve 改造 + 补丁退役 + Builder 传参 + 本地 bun 构建首跑通。
- **P1(约 3-5 人天)**:`i18n.go` 映射重写;50 个目标文件别名迁移与键更新(探针半自动 + 人工复核);V2 CI 工作流变体(本单不落地)。
- **P2(约 1-2 人周)**:217 条失效锚点的新文案补翻(需人工翻译与产品决策);覆盖率口径重建;`cli.json` 迁移行为验证。
- **P3(持续)**:README/安装文档双语更新;nightly tag 命名联调;V2 后续小版本的增量跟进(预计每月 1-2 次,每次 0.5-1 人天,若锚点稳定)。

---

## 附录 A:本次交付物与自查

- 新增 `docs/opencode-v2-spike-20260921.md`(本报告)、`tools/v2spike_probe.py`(探针,`tools/` 下无既有文件被改)。
- 自查:① 探针路径从 `__file__` 推导仓库根,无硬编码;② `--json-out` 用 `mkstemp`+`os.replace` 原子写,无共享状态;③ 无死代码;④ 索引/详情集合有界(`MAX_INDEX_BYTES`/`MAX_FILE_BYTES`/`MAX_DETAIL_FILES`/`MAX_SAMPLES_PER_FILE`);⑤ 临时文件仅 `/tmp/oc-v2spike/`(oc- 前缀),完工即删(含失败路径);⑥ 退出码契约:0=完成,2=预期内失败(stderr),未预期= traceback + 非 0;⑦ 文案已通读;⑧ 上文命令输出均为真实运行片段(长输出已截断)。
- 合规确认:未 push origin/upstream;未触发/修改任何 GitHub Actions 与既有工作流;`git status` 仅有上述两个新增路径。
