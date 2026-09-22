# V2 汉化接入构建工作流 · 首个可下载中文 V2 Release 实战报告

- 日期:2026-09-22
- 分支:`feat/v2-release-wire`(基于 main `39caaa58e`)
- 范围:把中文**接进 V2 构建工作流**并在 `yuloop/OpenCodeChineseTranslationAuto` 发出**第一个可下载的中文 V2 Release**。只改 V2 专用文件(workflow + 本报告);**V1 线一个字都没动**。
- 结论一句话:**V2 nightly 已从 build-only 升级为「注入中文 → 门禁 → 构建 → 中文落地验证 → 打包 → 发 Release」全链路;首个 Release `v2-cn-2.0.14`(上游 `v2.0.14`)已发布,二进制 `--help`/`strings` 均实证中文在里面。**

---

## ① V1 四步怎么做的(只读核清)

V1 生产流水线 = `.github/workflows/opencode-cn-nightly.yml`(每小时跟随上游 `dev`):

| 步 | V1 做法 | 关键点 |
|---|---|---|
| 注入 | `python3 scripts/patch-build-ts.py build/upstream/packages/opencode/script/build.ts`(给 V1 build.ts 打 `OPENCODE_BUILD_TARGET` 补丁)+ `./dist/opencode-cli apply --strict --min-match-rate 1` | 门禁 100% 匹配才允许继续;`apply` 按 V1 布局选 `assets/opencode-i18n` |
| 构建 | `OPENCODE_VERSION=<上游版本> OPENCODE_BUILD_TARGET=<平台> ./dist/opencode-cli build --platform <平台> --deploy=false` | windows-x64 + linux-x64 两平台矩阵 |
| 打包 | `zip -j dist/opencode-zh-CN-<TAG>-<平台>.zip <二进制>`;release job 再 zip 翻译工具源码 + `find … \| xargs sha256sum >SHA256SUMS` | 产物 = zip + SHA256SUMS |
| 发布 | `softprops/action-gh-release@v3`:tag `v<版本>-cn-nightly-<SHA12>`、正文(上游 SHA/门禁/下载表/一键安装)、`files: dist/*`、`overwrite_files`、`prerelease: true`;发布后删旧预览 release(用 `secrets.YU_TOKEN`) | tag 每次上游新提交都不同;预览版只留最新 1 个 |

**V2 专用路径的设计取舍**(新文件优先;不共用 V1 脚本函数,V2 全部走 cli-go 原生能力):

| 步 | V2 做法(本单落地) | 与 V1 的差异/理由 |
|---|---|---|
| 注入 | `./dist/opencode-cli apply --strict --min-match-rate 1`(**不打 patch-build-ts.py**) | V2 的 `packages/cli/script/build.ts` 已内建 `--target=`,cli-go 自动探测 V2 布局并选 `assets/opencode-i18n-v2`;patch 脚本对 V2 是退役路径(试跑报告 ⑨-2) |
| 门禁 | 同口径 `--min-match-rate 1`(V2 专用 env `V2_MIN_MATCH_RATE`) | main `39caaa58e` 收口后实测 v2.0.13/v2.0.14 均 **1669/1669 = 100%**(217 文件 0 跳过 0 失败,gate-close 报告 §7.1 + 本单复测),不需要阶梯阈值 |
| 构建 | `./dist/opencode-cli build --platform linux-x64 --deploy=false` | 单平台;`OPENCODE_VERSION` 不显式设,由工具从 `packages/cli/package.json` 注入(试跑报告 ⑥-2) |
| 打包 | 裸二进制 `opencode-v2-<上游tag>-linux-x64` + `SHA256SUMS` | linux 单平台无需 zip;任务要求「Release 附二进制 + SHA256」 |
| 发布 | `softprops/action-gh-release@v3`,tag **`v2-cn-<上游版本>`**(v2.0.14 → `v2-cn-2.0.14`) | tag 按上游版本唯一(无 SHA12);正文写清上游 tag/commit + **注入的资产 commit**;不做旧 release 清理(V1 的清理逻辑不碰) |

## ② 改动文件(全部 V2 专用,V1 零改动)

| 文件 | 改动 |
|---|---|
| `.github/workflows/opencode-cn-v2-nightly.yml` | **唯一被改的既有文件**。build-only → 注入+门禁+构建+中文落地验证+打包+发 Release;`permissions: contents: read → write`(发 Release 所需,与 V1 同权限);新增 `resolve` job(解析上游 tag/commit/version、推导 `v2-cn-<版本>`、定时触发命中已存在 Release 则跳过) |
| `docs/opencode-v2-release.md` | 本报告(新增) |

**未碰(铁律核验)**:`.github/workflows/opencode-cn-nightly.yml`(V1 nightly)、`.github/workflows/release.yml`、`scripts/patch-build-ts.py`、`install*.ps1/sh`、V1 词表 `cli-go/internal/core/assets/opencode-i18n/`、V2 资产 `cli-go/internal/core/assets/opencode-i18n-v2/`、cli-go 全部 Go 代码 —— `git diff main --stat` 仅上表两文件。

## ③ 流程(改后的 V2 nightly)

```
schedule(每天 21:23 UTC)/ workflow_dispatch(可指定上游 tag)
  └─ resolve: 取最新 v2.0.x(或指定 tag)→ 上游 commit → packages/cli/package.json 版本
              → 发布 tag v2-cn-<版本>;定时触发时该版本 Release 已存在则跳过
  └─ build-v2(if should_build):
       checkout 本仓(cli-go+V2 资产)+ 浅克隆上游 tag
       → build cli-go 工具 → 记录注入的资产 commit(API 按 path 取最近提交)
       → 门禁: apply --dry-run --strict --min-match-rate 1 + verify --dry-run
       → 真实注入: apply --strict --min-match-rate 1(V2 资产自动选择)
       → build linux-x64(--version 须 = 上游版本)
       → 中文落地验证: 4 条已知译文 ≥3 命中 + CJK 转义序列计数
       → 打包二进制 + SHA256SUMS → upload-artifact
       → 生成 Release 正文(上游 tag/commit、资产 commit、门禁、验证证据)
       → softprops/action-gh-release 发布(tag v2-cn-<版本>,附二进制+SHA256SUMS)
```

## ④ 手动触发与产物(第一次跑通)

- **Run(手动触发,`upstream_tag=v2.0.14`,17 步全绿)**:https://github.com/yuloop/OpenCodeChineseTranslationAuto/actions/runs/35747074483
- **Release(第一个可下载的中文 V2 Release)**:https://github.com/yuloop/OpenCodeChineseTranslationAuto/releases/tag/v2-cn-2.0.14
  - 发布 tag:`v2-cn-2.0.14`(= `v2-cn-` + 上游版本 `2.0.14`);Release 名:OpenCode v2.0.14 简体中文汉化版(V2 线);非 prerelease。
- 上游基线:`anomalyco/opencode` tag `v2.0.14`(commit `08462140ec0de1e4b17d4a353d8d5827f53cf7b0`,版本 2.0.14)
- 注入的资产 commit:`7c04ca8468c69e542191009cc0b3eb03ea640973`(V2 专用资产,main 上门禁收口提交;Release 正文已写明)
- 产物名与 sha256(Release 附件实测):

  | 文件 | sha256 | 体积 |
  |---|---|---|
  | `opencode-v2-v2.0.14-linux-x64` | `f45cd366594590bb75f2d2c5f5c41df5d5ca9d4fc5165d7a849d20cc93e2f9df` | 200,844,768 B(约 191.5 MiB,numfmt 192MB) |
  | `SHA256SUMS` | — | 96 B(1 行二进制摘要) |

  > 本地同源复跑(同 tag、同资产、同工具链)对照:sha256 `f67875f3155d6462e1c835433a7e8926a82b42ef7860cbf3f48b2979cdb03cbd`、200,898,016 B;与 CI 产物体积一致(差 ~53KB)、字符串内容一致(CJK 转义序列两边均 64,147),逐字节差异来自 runner 环境(构建路径/时间戳),以 Release 附件内 `SHA256SUMS` 为权威。

## ⑤ 真验证:中文真的在二进制里(三层证据)

CI 内新增了「中文落地验证」步骤(不是只看绿点):bun `--compile`(minify+bytecode)把非 ASCII 以 `\uXXXX` 转义形态嵌入模块源码(bun 1.4.2 本地实测),故验证同时接受转义形态与原始 UTF-8;4 条已知译文(与 `assets/opencode-i18n-v2/anchors` 真实译文一一对应)至少命中 3 条,并输出 CJK 转义序列总量。

**证据 1 — CI 流水线内验证(Run 日志「Verify Chinese strings landed in binary」步骤)**:

```
build/upstream/packages/cli/dist/cli-linux-x64/bin/opencode --version -> opencode v2.0.14
- 命中注入译文（bun 转义形态）: 调试与故障排查工具
- 命中注入译文（bun 转义形态）: 列出所有智能体
- 命中注入译文（bun 转义形态）: 卸载 OpenCode 并删除所有相关文件
- 命中注入译文（bun 转义形态）: OpenCode 登录
- CJK 转义序列（\u4E00-\u9FFF）出现次数: 64147
```

同 Run 的门禁步骤输出:`📁 文件: 217 成功, 0 跳过, 0 失败 / 📝 替换: 1669/1669 成功 (100.0%)`;`verify --dry-run`:`📝 替换: 1669/1669 可匹配`。

**证据 2 — 从 Release 下载二进制后实测(2026-09-22,本机 linux-x64 直接运行)**:

```
$ curl -fsLO https://github.com/yuloop/OpenCodeChineseTranslationAuto/releases/download/v2-cn-2.0.14/opencode-v2-v2.0.14-linux-x64
$ curl -fsLO https://github.com/yuloop/OpenCodeChineseTranslationAuto/releases/download/v2-cn-2.0.14/SHA256SUMS
$ sha256sum -c SHA256SUMS
opencode-v2-v2.0.14-linux-x64: OK
$ ./opencode-v2-v2.0.14-linux-x64 --version
opencode v2.0.14
$ ./opencode-v2-v2.0.14-linux-x64 --help | head -8
DESCRIPTION
  OpenCode 命令行界面

USAGE
  opencode <subcommand> [flags] [<directory>]
...
$ ./opencode-v2-v2.0.14-linux-x64 --help | grep -m6 -P '[\x{4e00}-\x{9fff}]'
  OpenCode 命令行界面
  upgrade, update    将 OpenCode 升级到最新或指定版本
  uninstall          卸载 OpenCode 并删除所有相关文件
  acp                启动 Agent Client Protocol 服务器
  api                向正在运行的服务器发送请求
  debug              调试与故障排查工具
```

二进制内已知注入译文精确命中(5/5,bun 转义形态;bun 1.4.2 会把非 ASCII 以 `\uXXXX` 嵌入,故 `strings` 看到的是转义序列而非原始汉字):

```
$ for s in '\u5217\u51FA\u6240\u6709\u667A\u80FD\u4F53' '\u767B\u5F55' '\u8C03\u8BD5\u4E0E\u6545\u969C\u6392\u67E5\u5DE5\u5177' \
           '\u7BA1\u7406\u5DE5\u4F5C\u7A7A\u95F4' '\u5378\u8F7D OpenCode \u5E76\u5220\u9664\u6240\u6709\u76F8\u5173\u6587\u4EF6'; do
    grep -aqF "$s" opencode-v2-v2.0.14-linux-x64 && echo "HIT: $s"; done
HIT: \u5217\u51FA\u6240\u6709\u667A\u80FD\u4F53        # 列出所有智能体
HIT: \u767B\u5F55                                        # 登录
HIT: \u8C03\u8BD5\u4E0E\u6545\u969C\u6392\u67E5\u5DE5\u5177  # 调试与故障排查工具
HIT: \u7BA1\u7406\u5DE5\u4F5C\u7A7A\u95F4                  # 管理工作空间
HIT: \u5378\u8F7D OpenCode \u5E76\u5220\u9664\u6240\u6709\u76F8\u5173\u6587\u4EF6  # 卸载 OpenCode 并删除所有相关文件
$ grep -ao '\\u[4-9][0-9A-Fa-f][0-9A-Fa-f][0-9A-Fa-f]' opencode-v2-v2.0.14-linux-x64 | wc -l
64147
```

**证据 3 — 注入前后对拍**:同一 v2.0.14 检出,注入前 `apply --dry-run --strict --min-match-rate 1` → `📁 文件: 217 成功, 0 跳过, 0 失败 / 📝 替换: 1669/1669 成功 (100.0%)`;真实 `apply` 后抽查 `packages/cli/src/commands/commands.ts`、`packages/cli/src/acp/service.ts` 等文件,中文译文逐行落在源码里(如 `description: "列出所有智能体"`、`label: "OpenCode 登录"`),再由 bun 编译进二进制——即 `--help` 里看到的中文确实来自本仓库 V2 资产的注入,而非上游自带。

## ⑥ 复现(任何人可查)

```bash
# 1) 触发(指定上游 tag;留空自动取最新 v2.0.x)。合并后 --ref main,
#    合并前用 --ref feat/v2-release-wire
gh workflow run opencode-cn-v2-nightly.yml \
  --repo yuloop/OpenCodeChineseTranslationAuto --ref main -f upstream_tag=v2.0.14

# 2) 下载 Release 二进制并验证中文
curl -fsLO https://github.com/yuloop/OpenCodeChineseTranslationAuto/releases/download/v2-cn-2.0.14/opencode-v2-v2.0.14-linux-x64
curl -fsLO https://github.com/yuloop/OpenCodeChineseTranslationAuto/releases/download/v2-cn-2.0.14/SHA256SUMS
sha256sum -c SHA256SUMS
chmod +x opencode-v2-v2.0.14-linux-x64
./opencode-v2-v2.0.14-linux-x64 --version        # opencode v2.0.14
./opencode-v2-v2.0.14-linux-x64 --help | head -5 # OpenCode 命令行界面
strings -a opencode-v2-v2.0.14-linux-x64 | grep -c '\\u[4-9][0-9A-Fa-f][0-9A-Fa-f][0-9A-Fa-f]'  # 数万级 CJK 转义序列
```

## ⑦ 回滚办法

| 场景 | 操作 |
|---|---|
| 撤 Release(保留代码) | GitHub Releases 页删 `v2-cn-2.0.14` + 删同名 git tag:`gh release delete v2-cn-2.0.14 --repo yuloop/OpenCodeChineseTranslationAuto --yes && gh api -X DELETE repos/yuloop/OpenCodeChineseTranslationAuto/git/refs/tags/v2-cn-2.0.14` |
| 停发(保留已发) | 删除/禁用 `.github/workflows/opencode-cn-v2-nightly.yml` 的 `schedule` 触发,或整个文件回退到 build-only 版(`git checkout 39caaa58e -- .github/workflows/opencode-cn-v2-nightly.yml`) |
| 代码整体回退 | `git revert` 本单两个 commit(workflow + 本报告);V1 线从未被改,无需回滚 |
| 资产侧问题 | V2 资产是附加式锚点文件,删除/修正对应 `anchors/*.json` 后 dispatch 重跑同一上游版本即覆盖发布(overwrite_files: true) |

**影响面**:回滚只作用于 V2 线;V1 正式版/实时预览版的流水线、脚本、词表与本单零交集,不受任何回滚操作影响。

## ⑧ 已知边界与下一步

1. **门禁 100% ≠ 界面全中文**:身份锚点(保持原文)计入匹配;仍有约 60 条散点 + 237 条 keybind 描述 + 25 条 devtools 未译(gate-close 报告 §5)。Release 正文已明示。
2. **定时触发语义**:tag 按上游版本唯一, nightly 只在「上游出新版本」或「手动 dispatch」时发布;资产更新后重发同一上游版本请用 dispatch。
3. **下一步候选**:keybind 237 条 + devtools 25 条批次翻译(B7);V2 覆盖率工具(`tools/v2_i18n_coverage.py`)接入 nightly 报告;多平台(windows-x64/darwin-arm64)矩阵扩展。

## ⑨ 合规自查

- V1 铁律:`.github/workflows/opencode-cn-nightly.yml`、`release.yml`、`scripts/patch-build-ts.py`、V1 词表、cli-go Go 代码**零改动**(`git diff main --stat` 仅 workflow + 本报告)。
- 未推 upstream(`upstream` remote 保持 DISABLED);未做范围外目录的改动;未新增任何凭据,未改仓库权限(仅本 workflow 文件内 `permissions: contents: write`,与 V1 生产流水线同权限)。
- 文中 run 链接、tag、sha256、体积、门禁数字、`--help` 输出均为真实运行结果。

---

## ⑩ 重发记录:V2 资产更新后重发同一上游版本(2026-09-22)

- 日期:2026-09-22(15:45 UTC 触发,15:47 UTC 发布完成)
- 基线:main `805030174`(PR #14 `feat/v2-i18n-tail` 已合入;V2 门禁 1669 → **2016/2016 = 100.0%**、217 → **227 文件**)
- 动机:线上 `v2-cn-2.0.14`(15:26 UTC 发布)是 PR #12 时代的**旧资产**构建;PR #14 合入后,用新资产**重发同一上游版本**(上游仍 `v2.0.14`,commit `08462140ec0d`,未变)。

### 重发机制(既有入口,零工作流改动)

`opencode-cn-v2-nightly.yml` 既有语义(①/③ 设计时已写明):

- `workflow_dispatch`:**一律构建**(`should_build=true`);「Release 已存在则跳过」只对 `schedule` 触发生效(workflow 第 122-129 行)。
- 发布步 `softprops/action-gh-release@v3` 带 `overwrite_files: true`:同名 Release `v2-cn-2.0.14` **原地覆盖更新**,二进制 + SHA256SUMS 替换为新构建。

即「重发同一上游版本」= 对同一 `upstream_tag` 再 dispatch 一次,**不需要新增 force 之类的手动输入,工作流一行未改**:

```bash
gh workflow run opencode-cn-v2-nightly.yml \
  --repo yuloop/OpenCodeChineseTranslationAuto --ref main -f upstream_tag=v2.0.14
```

### 本次重发结果

- **Run(两 job 全绿,head SHA `805030174`)**:https://github.com/yuloop/OpenCodeChineseTranslationAuto/actions/runs/35749502266
- **Release(原地更新,tag 不变)**:https://github.com/yuloop/OpenCodeChineseTranslationAuto/releases/tag/v2-cn-2.0.14
- 注入的资产 commit:`5558de61956e`(PR #14 提交,main 上最后改动 `cli-go/internal/core/assets/opencode-i18n-v2/` 的 commit;Release 正文已写明)
- 门禁(dry-run):📁 文件: **227 成功, 0 跳过, 0 失败** / 📝 替换: **2016/2016 成功 (100.0%)**(旧构建为 1669/1669、217 文件)
- 新产物(Release 附件实测,本地重新下载复核 sha256 一致):

  | 文件 | sha256 | 体积 |
  |---|---|---|
  | `opencode-v2-v2.0.14-linux-x64`(新构建) | `b23a7dddcd3826b35920629ec86ec556aad04bff95aec749027470caf22df472` | 200,852,960 B(约 192 MB) |
  | `opencode-v2-v2.0.14-linux-x64`(旧构建,15:26 发布) | `f45cd366594590bb75f2d2c5f5c41df5d5ca9d4fc5165d7a849d20cc93e2f9df` | 200,844,768 B(约 191.5 MB) |

### 中文前后对比(重点;如实报告,未美化)

同机 linux-x64 下载新旧两个二进制,`--version` 均为 `opencode v2.0.14`,逐项对比:

**`--help` 输出前后逐字节相同(diff 为空)。上一版仍是英文的项,本版依旧英文,没有变中文:**

- flag 说明:`--standalone  Run with a private server instead of the background service`、`--server string  Connect to a server URL instead of the background service`、`--auto  Auto-approve permissions that are not explicitly denied`、`--continue, -c  Continue the last session`、`--session, -s string  Session ID to continue`、`--prompt string  Prompt to use`
- GLOBAL FLAGS:`--help, -h  Show help information`、`--version, -v  Show version information`、`--wizard  Start wizard mode for a command`、`--completions …  Print shell completion script (choices: bash, zsh, fish, sh)`、`--log-level …  Sets the minimum log level (choices: …)`、`--print-logs  Print logs to stderr (server logs require --standalone)`
- 分区标题:`DESCRIPTION`、`USAGE`、`ARGUMENTS`、`FLAGS`、`GLOBAL FLAGS`、`SUBCOMMANDS`;及 `ARGUMENTS` 区 `directory string  Directory to start OpenCode in (optional)`
- 子命令 `auth/mcp/run/session --help` 同样逐一对比,全部相同。
- 旧版已译的部分(DESCRIPTION 正文「OpenCode 命令行界面」、SUBCOMMANDS 全部子命令描述)本版保持中文,无回退。

**根因(资产侧实证,非推测)**:上述英文串是上游 `packages/cli/src/commands/commands.ts` 的行内字面量(`Flag.withDescription("Run with a private server instead of the background service")` 等)与 `effect/unstable/cli` 库自带串;逐一比对 V2 资产 `anchors/*.json` 的全部 **2016 条 replacements**,这 13 条串**一条都未登记**——从来不是翻译候选,注入流水线结构上就碰不到它们。

**新资产确实进了二进制(层面对拍)**:CJK `\uXXXX` 转义序列 64,147 → **66,487**;去重后新增 **196 条**中文串、消失 0 条,全部来自 PR #14 尾批翻译,落在 **TUI 层**(`--help` 层无感):keybind 描述(「上一个/下一个收藏模型」「上一个/下一个智能体」「上一个/下一个最近使用的模型」「上一条/下一条历史项」「中断当前会话」「全屏」「关闭当前会话页签」「从消息分支会话」「停止待确认」…)、devtools-bar 标签、session-frame/session-tabs/reconnecting 串、B 组散点(「事件循环」「会话将自动恢复」「从插件对话框安装插件」…)。

一句话结论:**重发成功、新资产 2016/2016 全量落地,但任务点名的 `--help` 层英文项本版未变;要汉化它们需把对应串登记进 V2 资产(下一步)。**

### 遗留事项(下一单候选,本单未做)

1. `--help` 顶层 13 条英文串(flag 说明 + ARGUMENTS 区)+ 分区标题的汉化:需将 `commands.ts` 行内 `Flag.withDescription(...)` 与 `effect/unstable/cli` 库串登记为 V2 资产 replacements(注意库串随上游 bun 依赖变动,锚定方式待设计)。
2. Release 正文模板(`opencode-cn-v2-nightly.yml` 第 369 行「已知边界」段)仍写着「约 60 条散点 + 237 条 keybind + 25 条 devtools 未译」的 PR #12 时代数字,PR #14 已译该批,下次改动工作流时一并更新文案(本单遵守最小改动未动)。

### 合规自查(本单)

- 工作流零改动:重发全程只用既有 `workflow_dispatch` 入口;`git diff main --stat` 仅本报告一个文件,未新增任何手动输入。
- V1 铁律:`.github/workflows/opencode-cn-nightly.yml`、`release.yml`、`scripts/patch-build-ts.py`、V1 词表、cli-go Go 代码零改动。
- 未推 upstream(`upstream` remote 保持 DISABLED);未新增凭据;Release 为原地更新(未删旧发新),tag 不变。
- 文中 run 链接、sha256、体积、门禁数字、对比结论均为真实运行结果;「未变中文」部分如实呈现,未美化。
