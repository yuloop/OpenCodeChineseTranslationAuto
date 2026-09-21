# opencode V2 完整构建首跑通 · 实测报告

- 日期:2026-09-21~22
- 分支:`feat/oc-dsh-ocv2fork-build`(基于已合并的 cli-go V2 构建支持)
- 范围:对上游 `v2.0.12` 源码用本仓库 cli-go 工具链跑通 **linux-x64 单平台完整构建**,产出可运行二进制。只改 `cli-go/`(途中修正 2 处 bug)+ 新增本报告。未推送、未改 `.github/`、未碰翻译资产、未碰生产 4097/暂存 4098。
- 结论一句话:**V2 能在本地构建出可运行二进制(`--version` = `opencode v2.0.12`),冷构建 ~9 分钟、热构建 ~18 秒;途中修正了 2 个 V2 适配 bug(产物目录名、版本号来源),均已修并验证。**

---

## ① 目标

证明 cli-go 的 V2 构建支持(自动探测 / `--layout v2` 强制、`patch-build-ts.py` 退役路径)能在本机对上游 `v2.0.12` 产出**可运行**的 linux-x64 二进制,为后续 CI 接入 V2 变体提供实测依据(耗时/依赖/缓存点/超时预算/bun 来源/翻译门禁过渡建议)。

## ② 环境

| 项 | 值 |
|---|---|
| 宿主机 | Linux x86_64,12 核,30G RAM,`/` 余 245G,`/tmp` 为 tmpfs(16G) |
| Go | go1.26.0 linux/amd64(cli-go 工具链) |
| bun | **1.4.2**,装在用户目录 `~/.bun/bin/bun`(见 ④) |
| node / python3 | `/usr/local/bin/node`;`python3 3.14.4`(仅跑脚本/测试用) |
| 上游 | `anomalyco/opencode` tag **`v2.0.12`** = commit `2670273ff17da96f85c5826ced57aa1b368754fa` |

布局核实(克隆后):无 `packages/opencode`,有 `packages/cli/script/build.ts` 且含 `--target=`;根 `package.json` `packageManager: bun@1.4.2`。→ cli-go 自动探测判为 **V2**(构建执行行出现 `--target=opencode-linux-x64 --outdir=dist` 佐证)。

## ③ 完整命令序列(真实执行)

```bash
# 1) 装 bun@1.4.2 到用户目录(不动系统)
export BUN_INSTALL="$HOME/.bun"
curl -fsSL https://bun.sh/install | bash -s "bun-v1.4.2"
~/.bun/bin/bun --version            # → 1.4.2

# 2) 浅克隆上游 v2.0.12
git clone --depth 1 --branch v2.0.12 https://github.com/anomalyco/opencode.git /tmp/oc-src

# 3) 构建 cli-go 工具 + 自检
cd cli-go
gofmt -l . && go vet ./...          # 均干净
go test ./...                       # 全绿
go build -trimpath -o /tmp/oc-tools/opencode-cli .

# 4) 跑 V2 linux-x64 完整构建(自动探测布局;--deploy=false 不落本地 bin)
OPENCODE_SOURCE_DIR=/tmp/oc-src PATH="$HOME/.bun/bin:$PATH" \
  /tmp/oc-tools/opencode-cli build --platform linux-x64 --deploy=false
```

`patch-build-ts.py` 退役路径验证(只读):

```bash
python3 scripts/patch-build-ts.py --layout v2 /tmp/oc-src/packages/cli/script/build.ts
# → "V2 layout detected: ... skipping patch"   rc=0   (V2 不再硬打补丁)
# 不带 --layout(默认 v1)对 V2 build.ts 仍会 RuntimeError(见 ⑥),故 V2 必须显式 --layout v2 或走 Go 工具原生 --target
```

## ④ 关键日志片段

**冷构建(首次,全量下载)——工具自带的产物校验暴露了 bug(见 ⑥-1):**

```
开始编译构建...
  已应用 Bun 版本兼容性修复
正在安装依赖...
在 monorepo 根目录安装依赖: /tmp/oc-src
bun install v1.4.2 (744846f84)
Resolving dependencies
Resolved, downloaded and extracted [16]
...
bun add v1.4.2 (744846f84)                 # build.ts 内建: bun install --os=* --cpu=* @opentui/core @opencode-ai/pty
Resolved, downloaded and extracted [16]
... (vite/rolldown 构建 web UI 资源) ...
building cli-linux-x64
构建产物未找到: /tmp/oc-src/packages/cli/dist/opencode-linux-x64/bin/opencode
错误: 构建失败: 构建产物验证失败: 期望路径 .../opencode-linux-x64/bin/opencode 不存在
=== BUILD END rc=1 elapsed=545s ===
/tmp/oc-src/packages/cli/dist/cli-linux-x64/bin/opencode      # 真实产物在 cli-linux-x64,二进制已生成
```

**热构建(修正后,缓存命中)——校验通过、版本正确:**

```
building cli-linux-x64
✓ 构建产物已验证: /tmp/oc-src/packages/cli/dist/cli-linux-x64/bin/opencode
构建完成！
=== BUILD2 END rc=0 elapsed=18s ===
$ .../dist/cli-linux-x64/bin/opencode --version
opencode v2.0.12
```

## ⑤ 耗时

| 阶段 | 冷构建(首次) | 热构建(二次,缓存命中) |
|---|---|---|
| bun 根安装(34 包 monorepo) | ~2 min | 跳过(node_modules 已在) |
| `bun add --os=* --cpu=* @opentui/core @opencode-ai/pty` | ~5 min(拉全平台原生二进制) | 缓存命中,秒级 |
| web UI 构建(vite/rolldown,PWA) | ~10 s(`✓ built in 10.35s`) | ~10 s |
| `Bun.build` 编译单目标 + 校验 | ~1–2 min | ~数秒 |
| **合计** | **545 s(~9 min)** | **18 s** |

单平台冷构建 ~9 分钟,远低于 CI 45 分钟预算(见 ⑧)。

## ⑥ 途中修正(已改 cli-go/ 并在分支体现)

**⑥-1 `GetDistPath` 对 V2 用了错误的产物子目录(阻塞工具校验)。**
上游 `packages/cli/script/build.ts` 第 121 行 `const name = target.replace(binary, "cli")`、第 141 行 `outfile: path.join(outdir, name, "bin", binary)`——`--target` 仍是 `opencode-linux-x64`,但**输出目录是 `cli-linux-x64`**(`opencode`→`cli`)。合并进仓库的 `GetDistPath`(及其单测)误按 V1 口径返回 `dist/opencode-<platform>/...`,导致二进制已生成却校验失败。spike 报告也只引用了 build.ts 前 63 行,漏看了 121 行,故结论写成"产物布局与 V1 一致"。
**修法:** `GetDistPath` 对 `LayoutV2` 返回 `dist/cli-<platform>/bin/opencode[.exe]`;更新 `TestGetDistPathV1V2`(补 windows `.exe` 用例)。验证:热构建 `✓ 构建产物已验证`。

**⑥-2 版本号不来自 git tag,而是 npm latest + patch 递增(导致 v2.0.12 源码构建出 v2.0.13)。**
上游 `packages/script/src/index.ts` 第 35–50 行:channel=`latest` 且未显式设 `OPENCODE_VERSION` 时,`fetch npm @opencode/cli/latest` 取版本再 **patch+1**。本机构建时 npm latest 仍是 `2.0.12` → 嵌入 `2.0.13`;官方发布二进制当年构建时 npm latest=2.0.12 且走显式版本,故报 `2.0.12`。
**修法:** `Build()` 在未显式设 `OPENCODE_VERSION` 时,从源码 `buildDir/package.json`(V2=`packages/cli`,V1=`packages/opencode`)读 `version` 注入 `OPENCODE_VERSION`,使 `--version` 忠实反映所构建源码。新增 `sourceVersion()` + `TestSourceVersion`。验证:修正后 `--version` = `opencode v2.0.12`。

> 首跑(未修 ⑥-2)产物 `--version` = `opencode v2.0.13`,如实记录;修正后 = `2.0.12`。两次 sha256 均留存(见 ⑦)。

## ⑦ 产物

| 文件(scratch) | 版本 | sha256 |
|---|---|---|
| `opencode`(最终交付,= 下面第二行) | v2.0.12 | `24194f9219fc29dce09412895bdb6220049176cb5e53edc1f3aea8bf14d4ec4d` |
| `opencode-v2.0.12-linux-x64` | v2.0.12 | `24194f9219fc29dce09412895bdb6220049176cb5e53edc1f3aea8bf14d4ec4d` |
| `opencode-firstrun-v2.0.13`(首跑,修 ⑥-2 前) | v2.0.13 | `6a5fcae620135f0c9df06248677745c5cbb354cd04977b4546dd26098c82f9c5` |

- 路径(构建内):`/tmp/oc-src/packages/cli/dist/cli-linux-x64/bin/opencode`(ELF x86-64,约 200 MB,bun 单文件可执行)。
- 留存目录:`/root/.hermes/cache/scratch/ocv2-i18n-build/`(含 `SHA256SUMS`);已从 scratch 独立复跑 `--version` = `opencode v2.0.12`(不依赖 /tmp)。

## ⑧ 依赖(粗略体积 / 来源)

| 依赖 | 体积(约) | 来源 |
|---|---|---|
| bun 缓存 `~/.bun/install/cache` | 8.5 G | npm registry(bun 包内容缓存) |
| monorepo 根 `node_modules` | 8.5 G | npm registry(workspace 依赖) |
| 浅克隆 `.git` | 80 M | github.com/anomalyco/opencode(tag v2.0.12) |
| 平台原生二进制 | 含在上两项内 | `@opentui/core`(全 os/cpu)、`@opencode-ai/pty@0.1.13`、`@parcel/watcher-linux-x64-glibc` 等 |

- 版本串来源额外依赖 **npm `@opencode/cli` latest dist-tag**(⑥-2);修正后不再依赖它(改读源码 package.json)。
- 网络:github / registry.npmjs.org / bun.sh 均直连可用,**未走代理、无 DNS/下载报错**;构建未拉 bun 自身 release 资产(`build.ts` 仅在设 `BUN_COMPILE_RELEASE` 时才下载 bun 二进制,本机未设,用系统 bun 1.4.2 编译)。

## ⑨ 断点 / 待决(非阻塞,供后续)

1. **翻译门禁(阻塞 CI 上线,不阻塞本构建):** 本单为验证构建链,**采用跳过翻译(build-only,不跑 `apply`)**,因为目标是证明 V2 能产出可运行二进制。V2 上现有翻译资产仅约 31% 可匹配(spike 报告),100% `--min-match-rate 1` 门禁不可达。**过渡策略建议(P1):** V2 线单独阈值/阶梯(如先 0.3→0.6→1.0,或按文件级 100%),并先做锚点别名迁移(spike 探针的 280/497 "别处仍存在"清单);V1 线维持 100% 不变,双轨互不阻塞。
2. **`patch-build-ts.py` 调用约定:** V2 下必须 `--layout v2`(否则 RuntimeError);但 cli-go 的 V2 路径根本不调用它(用原生 `--target`)。CI 若保留该调用点需带 `--layout v2`,或对 V2 直接删除该步 + grep 门禁。
3. **`verify` 覆盖率口径:** V2 无 `packages/opencode/src`,扫描被跳过;新基线需覆盖 `packages/tui`+`packages/cli`(+ 可能 `session-ui`/`theme`)。属 P1/P2。

## ⑩ 对 CI 的含义(V2 变体接入实测依据)

- **bun 来源与版本:** 官方脚本 `curl -fsSL https://bun.sh/install | bash -s "bun-v1.4.2"` 装用户目录即可,无需系统级改动;卸载 = `rm -rf ~/.bun` + 删 `~/.bashrc` 里 `~/.bun/bin` 的 PATH 行。CI 用同版本(bun 官方 action 亦可,需锁 1.4.2,与根 `packageManager` 一致)。
- **缓存点(热构建 18s 的关键):** 缓存 `~/.bun/install/cache` 与 monorepo 根 `node_modules`(按 lockfile 命中);这二者命中后,单平台重建从 ~9 min 降到 ~18 s。CI 用 `actions/cache` 缓存这两处 + Go build cache。
- **超时预算:** 单平台冷构建 ~9 min;多平台(12 targets)主要增量在每目标 `Bun.build` 编译与 web UI 只建一次,粗估每目标 +1–2 min,**仍远低于现有 45 min job**;建议 V2 job 超时设 ≥ 30 min 留余量。
- **版本解析(resolve 步):** 读 `packages/cli/package.json`(=2.0.12),**不要** `gh api releases/latest`(V2 无 GitHub Release);建议 tag 轮询 `v2.0.x` 或 npm `@opencode/cli` dist-tag。构建时按 ⑥-2 由工具自动注入 `OPENCODE_VERSION`,保证 `--version` = 上游 tag 版本。
- **构建传参:** Go `Builder` 已传 `--target=opencode-<platform> --outdir=dist`,`buildDir=packages/cli`;产物在 `dist/cli-<platform>/bin/opencode`(⑥-1 已修)。

## ⑪ 自查

① 路径不硬编码:源码目录经 `OPENCODE_SOURCE_DIR` 注入,产物/部署路径由 `GetOpencodeDir`/`GetBinDir` 推导;`--deploy=false` 未落任何本地 bin,更未碰生产 `~/.opencode-i18n/bin`(4097 serve 所在)。② 临时物受控:全部 `/tmp/oc-` 前缀,完工即删(含失败路径)。③ 集合有界:测试新增用例有限且确定。④ 失败路径可复现:冷构建 rc=1 的报错与产物布局可复现(⑥-1)。⑤ 文案通读。⑥ 上文命令/日志/版本/sha256 均为真实运行输出。未启动任何 serve、未产生会话、未重启服务、未 push。
