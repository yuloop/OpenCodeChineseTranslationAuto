# opencode V2 汉化收尾批次报告(tail)

> 依据:`docs/opencode-v2-i18n-gate-close.md` §5 待裁定清单;术语与裁定规则沿用试点报告 ④/⑧ 与 batch-rest/routes 报告。
> 基准:上游纯净 v2.0.13(`3180aab16e050128678e590afcbd2dc85c259cb7`,私有副本 `/tmp/oc-v2i18n-cov/my-v2013`);V1 检出 `f54ce31`。

## 1. 结论

- §5 清单**全部处置完毕**:实测 **350 条待译串**(§5 写 348,差异来自 keybind 实测 241 定义而非 239),处置 **348 条**(345 条按 V1 术语实证翻译 + 2 条保持原文登记 identity + 3 处发现已译勿重复),**待裁定 2 条**不硬翻。
- 全局门禁:**2016/2016 = 100%,227 个目标文件,exit 0**(收口前态 217 文件 / 1669 条)。
- V1 门禁:**497/497 = 100%,exit 0**;`go test ./...` 全绿(含 `TestEmbeddedV1AssetsUnchanged`)。
- 真 apply 对拍(两棵纯净副本):**35 个产品文件、347 处新替换**,行数守恒、35/35 文件 0 语法错误、0 占位符残留、代码位零误伤。

## 2. §5 清单落数(对 v2.0.13 源码逐条核对)

| 组别 | §5 声明 | 实测 | 处置 |
|---|---|---|---|
| devtools-bar.tsx | 25 | 25 串 + 补遗 1(`"Unknown"`) | 26 译 + 2 identity(CPU/PID) |
| session-frame.tsx | 10 | 10 串 / 8 锚点 | 8 译(两条三元整式各含 2 串) |
| session-tabs.tsx | 9 | 9 串 / 8 锚点 | 8 译(`Close tab menu`+`Tabs` 合 1 条;`Untitled session` 3 处同串) |
| reconnecting.tsx | 4 | 4 串 | 4 译 |
| config/keybind.ts | 237 未译(总 239) | **241 定义 / 2 已译 / 239 待译,去重 235 distinct** | 234 译 + 1 待裁定 |
| B 组散点 | "约 60" | **63 串 / 26 行** | 62 译(1 条已译)+ 补遗 11 |
| routes ⑧ | 9 处 13 串 | 9 处 13 串 | 13 译 |
| **合计** | **348** | **350** | **345 译 + 2 identity + 2 待裁定 + 1 已译** |

补遗边界规则(本轮自定,仅取与 §5 条目**同一 UI 构件/同构造**的可见未译串):devtools-bar `"Unknown"`(L60)、footer.view.tsx statusText 族 8 条、footer.command.tsx `display: "Settings"`、context/session-tabs-model.ts `New session`。明确跳过:`[ ]`/`[x]`、单位 `ms`/`%`/`MB`、`·`/`↻`/`✓`/`×` 等符号(非文本或已由既有身份锚点代表)。

## 3. 逐条处置(三类)

### 3.1 按 V1 术语实证翻译 — 345 条

- **V1 逐字先例**(直取 V1 词表译文):`Exit the app`→`退出应用`、`Go to parent session`→`转到父会话`、`Go to `→`前往 `、`API key`→`API密钥`、`Connect provider`→`连接提供商`、`No matching items`→`未找到匹配项`、`WebFetch ${url}`→`网页获取 ${url}`、`Compact session`→`精简会话`、`Untitled session`→`未命名会话`、`Unknown`→`未知`、`Status`→`状态`、`Connected`→`已连接`、`Shell`→`命令行`、`interrupt`→`中断`。
- **V2 既有锚点先例**(保持同一英文键的既有译法):`Toggle debug panel`→`切换调试面板`、`Unable to load terminal`、`Manage workspaces`→`管理工作空间`、`Switch to session in quick slot N`、`Ask a side question`→`顺便提问`、`Exit pending`/`Stop pending`、`Focus session pane`/`Toggle subagent picker`/`Previous terminal`、`首次绘制耗时诊断`→`首次绘制耗时`、`写入堆快照`句式→`写入调试快照`、`每轮 tokens 用量`。
- **新词裁定 1 项:pane→`窗格`**。V1/V2 均无 pane 先例;既有 `panel`→`面板` 已大量使用(`Switch to ` 系列),pane 译"面板"会混淆,故译"窗格"(`聚焦会话窗格`/`隐藏侧边栏`/`关闭终端窗格`/`新建终端`),与 session-frame.tsx 的 pane 构件语义一致。
- **which-key 11 条**:保留 `which-key` 特性名于译框内(`切换 which-key 面板`、`向上滚动 which-key` 等),与 DevTools 既有处理式一致。
- **routes ⑧ 13 串**:全部采用 routes 报告已给建议译文(`命令行`/`子智能体`/`输入`/`输出`/`命令已取消`/`附件`/`(无回答)`/`收起`/`全屏`/`运行中`/`暂无输出` 等),本批直接落地。

### 3.2 保持原文(identity 锚点)— 2 条

- `CPU`、`PID`(devtools-bar.tsx):技术缩写,V1 `TPS`/`OS` 同类先例;入 `--keep.json`,apply 空操作。
- 未登记但同样保持的项(与试点 ⑧ 同类,不占条目):协议/枚举值(`"reconnecting"`、`"killed"`、`"timeout"`、`=== "uri"`、`"streaming"`、`"running"` 等比较操作数)、符号与单位、`[ ]`/`[x]`。

### 3.3 待裁定 — 2 条(不硬翻)

1. **keybind.ts `"Open scrap screen"`**(L52,`app.scrap`):scrap 功能在 v2.0.13 未实现,术语歧义(scrap 可指碎片/剪贴/收藏),V1/V2 均无先例。**建议**:等功能实现后按实际 UI 文案补译。
2. **stats.tsx 星期字母数组** `["M","T","W","T","F","S","S"]`(L102):CJK 双宽字符会破坏日历列对齐,V1 无先例。**建议**:若后续要做,需同步改造列宽计算,属独立小批。

### 3.4 发现已译、勿重复登记 — 3 处

- `prompt/index.tsx` `+{…} more`:batch-component 锚点已在,译 `…更多`。
- `auth/login.ts` `hint: "recommended"`:已在,译 `hint: "推荐"`。
- `uninstall.ts` `label: "Data"/"Cache"/"State"`:已在,分别译 `数据`/`缓存`/`状态`;本轮仅补 `label: "Config"`。

## 4. 复量

### 4.1 V2 全局门禁(收口后 CLI,内嵌新资产)

```
$ OPENCODE_SOURCE_DIR=/tmp/oc-v2i18n-cov/my-v2013 opencode-cli apply --dry-run --strict --min-match-rate 1
  📁 文件: 227 成功, 0 跳过, 0 失败
  📝 替换: 2016/2016 成功 (100.0%)
exit 0
```

条目数守恒:1669 + 347(345 主条目 + 2 身份锚点)= **2016**;成功数 1669 + 347 = **2016**。227 个目标文件全部 `N/N 处替换`,无 ⚠ 无 ✗。

### 4.2 V1 门禁(证明没碰 V1)

`OPENCODE_SOURCE_DIR=/tmp/oc-v1-devhead`(V1 布局检出 `f54ce31`):**497/497 = 100.0%,0 失败,exit 0**;`go test ./...` 全绿,含 `TestEmbeddedV1AssetsUnchanged`(54 文件 497 条零改动)。

### 4.3 Tier A 覆盖账本(tools/v2_i18n_coverage.py,同一纯净树,资产目录对拍)

| 包 | covered occ | covered distinct | migratable occ | new occ |
|---|---|---|---|---|
| tui | 2053 → **2141** | 1198 → **1246** | 61 → **12** | 62 → **24** |
| cli | 107 → **111** | 102 → **106** | 4 → **0** | 6 → **6** |
| 合计 | 2160 → **2252** | 1300 → **1352** | 65 → **12** | 68 → **30** |

残差 12 migratable + 30 new(tui+cli)**全部不是未译可见串**:一是分类器盲区——已被同文件更长锚点译过的跨 JSX 边界碎片(如 `\n Image `/` more\n `/`\n Code\n `/`\n Write `/`\n Read `,门禁报告 §6 已同款记录);二是命令路由(`/btw`/`/mcps`/`/plugins`/`/connect`/`/exit`/`/update`/`/worktree`)、枚举值(`add`/`none`/`cancel`/`confirm`)、键名(`pgup/pgdn`)与布局空白(`\n    `、`│`)。本批新锚点造成的同类碎片(`Unknown plugin route: ` jsx-text)已人眼核验为中文。

## 5. 真实落地反向验证

取两棵**干净的 v2.0.13 副本**,分别用 main 资产 CLI(内嵌 217 配置)与收尾后 CLI(内嵌 227 配置)执行**真实 `apply`**(非 dry-run),`diff -r` 对拍:

- **仅 35 个产品文件差异**(36 个改动锚点文件中,`--keep.json` 为 identity 空操作,无差异,符合预期);每文件逐行核对,全部是既定译文,无误伤。
- **守恒校验**:35 文件行数逐一守恒;反引号守恒;引号仅 2 处 −4(`home/footer.tsx` 与 `scrollback.writer.tsx` 的复数三元整条替换,规则同 batch-rest ⑤.3),花括号/圆括号增减成对抵消。
- **tsc 5.9.3 逐文件语法解析:35/35,0 错误**。
- **占位符残留** `\x00opencode-i18n-N\x00`:新旧两树均 **0**。
- **代码位抽样**:`footer.view.tsx` 标识符 `interrupt`/`exiting`/`interruptLabel` 与协议值 `"reconnecting"` 原样;`=== "streaming"`/`=== "killed"`/`=== "uri"`/`=== "read"` 等比较左值原样;`keybind.ts` 全部绑定序列(`ctrl+-,super+z`、`{ key: "ctrl+v", preventDefault: false }` 对象形)原样,仅描述串变化。
- **最长优先验证**:`Server details unavailable`(26 字符)先于 `Server`(6)暂存,L289 得整句译文无级联;`Turn token usage (verbose)` 先于 `Turn token usage`;既有 `"interrupt"`(11)与新 `? "interrupt" : "stop"`(24)正确分流,无半截替换。

## 6. 已知限制与下一步

1. 待裁定 2 项见 §3.3,留给后续批次。
2. 上游测试 `packages/cli/test/config.test.ts:26` 断言 `description: "Exit the application"`;nightly workflow(`opencode-cn-v2-nightly.yml`)是 build-only——先检出上游再 apply,不在翻译后树上跑测试,故翻译安全。若未来改为在翻译后树上跑测试,需同步该断言。
3. Tier A migratable 残差 12 occ / 7 distinct(dialog-integration `add`、dialog-model/dialog-workspaces/prompt-index/plugins/dialog-select `none`、dialog-confirm `cancel`/`confirm`、home-footer `/plugins`、sidebar-footer `/connect`)全部是枚举值或命令路由,属"不可译"类,不需要操作。

## 7. 合规自查

- **改动范围**:`cli-go/internal/core/assets/opencode-i18n-v2/anchors/` 共 36 个文件(25 个扩写 + 10 个新建主文件 + 1 个 `--keep.json` 扩写),新增 347 条(345 主 + 2 身份);外加本报告文档。
- **未触碰**:V1 词表/脚本/门禁/workflow、`.github/`、`/root/xiangmudata_sync/opencode-v2-cn/`、上游纯净副本、门禁逻辑与阈值、`config.json` manifest(试点先例:manifest 只记 V1 迁移状态)。
- 身份锚点登记规则复核:2 条新 keep 条目均为非简单词形态之外的纯缩写词,不构成 `\x00opencode-i18n-N\x00` 占位符冲突;全量扫描本批 345 个主键,无 `opencode`/`i18n`/纯数字键。

---

## 附录 A:keybind.ts 234 条译文全表

| 描述(键) | 译文 |
|---|---|
| `Leader key for keybind combinations` | 组合快捷键的前导键 |
| `Exit the application` | 退出应用 |
| `Clear the screen in mini` | 清空 mini 屏幕 |
| `Toggle debug panel` | 切换调试面板 |
| `Toggle console` | 切换控制台 |
| `Toggle animations` | 切换动画 |
| `Toggle file context` | 切换文件上下文 |
| `Toggle diff wrapping` | 切换差异换行 |
| `Toggle paste summary` | 切换粘贴摘要 |
| `List available commands` | 列出可用命令 |
| `Open help dialog` | 打开帮助对话框 |
| `Open documentation` | 打开文档 |
| `Open settings` | 打开设置 |
| `Pair device` | 配对设备 |
| `Restart service` | 重启服务 |
| `Reload configuration` | 重新加载配置 |
| `Open diff viewer` | 打开差异查看器 |
| `Close diff viewer` | 关闭差异查看器 |
| `Move diff viewer down` | 差异查看器下移 |
| `Move diff viewer up` | 差异查看器上移 |
| `Page diff viewer down` | 差异查看器向下翻页 |
| `Page diff viewer up` | 差异查看器向上翻页 |
| `Scroll diff viewer down half a page` | 差异查看器向下滚动半页 |
| `Scroll diff viewer up half a page` | 差异查看器向上滚动半页 |
| `Go to the start of the diff` | 转到差异开头 |
| `Go to the end of the diff` | 转到差异结尾 |
| `Deprecated: file tree is mouse-controlled` | 已废弃:文件树由鼠标控制 |
| `Deprecated: keyboard navigation always controls the diff` | 已废弃:键盘导航始终控制差异 |
| `Jump to next diff hunk` | 跳转到下一个差异块 |
| `Jump to previous diff hunk` | 跳转到上一个差异块 |
| `Jump to next diff file` | 跳转到下一个差异文件 |
| `Jump to previous diff file` | 跳转到上一个差异文件 |
| `Toggle diff viewer file tree` | 切换差异查看器文件树 |
| `Toggle single patch view` | 切换单个补丁视图 |
| `Switch diff viewer source` | 切换差异查看器来源 |
| `Toggle diff viewer split or unified view` | 切换差异查看器的拆分/统一视图 |
| `Toggle selected diff file reviewed` | 切换所选差异文件的已审阅状态 |
| `Show more diff viewer shortcuts` | 显示更多差异查看器快捷键 |
| `Open external editor` | 打开外部编辑器 |
| `List available themes` | 列出可用主题 |
| `Switch between light and dark theme mode` | 在浅色和深色主题模式之间切换 |
| `Lock or unlock theme mode` | 锁定或解锁主题模式 |
| `Toggle sidebar` | 切换侧边栏 |
| `Focus session pane` | 聚焦会话窗格 |
| `Focus right pane` | 聚焦右侧窗格 |
| `Select terminal` | 选择终端 |
| `Toggle terminal pane` | 切换终端窗格 |
| `Close terminal pane` | 关闭终端窗格 |
| `Toggle session scrollbar` | 切换会话滚动条 |
| `View status` | 查看状态 |
| `View debug info` | 查看调试信息 |
| `Export session to editor` | 导出会话到编辑器 |
| `Copy session transcript` | 复制会话记录 |
| `Copy session ID` | 复制会话 ID |
| `Create a new session` | 新建会话 |
| `List all sessions` | 列出所有会话 |
| `Open recent sessions and projects` | 打开最近的会话和项目 |
| `Switch to next open session tab` | 切换到下一个打开的会话页签 |
| `Switch to previous open session tab` | 切换到上一个打开的会话页签 |
| `Go back in session tab history` | 在会话页签历史中后退 |
| `Go forward in session tab history` | 在会话页签历史中前进 |
| `Switch to next unread session tab` | 切换到下一个未读会话页签 |
| `Switch to previous unread session tab` | 切换到上一个未读会话页签 |
| `Close current session tab` | 关闭当前会话页签 |
| `Reopen last closed session tab` | 重新打开最近关闭的会话页签 |
| `Show session timeline` | 显示会话时间线 |
| `Fork session from message` | 从消息分支会话 |
| `Rename session` | 重命名会话 |
| `Delete session` | 删除会话 |
| `Share current session` | 分享当前会话 |
| `Unshare current session` | 取消分享当前会话 |
| `Interrupt current session` | 中断当前会话 |
| `Background blocking session tools` | 将阻塞会话工具转到后台 |
| `Compact the session` | 精简会话 |
| `Ask a side question` | 顺便提问 |
| `Change working directory` | 切换工作目录 |
| `Delete queued prompt` | 删除队列提示 |
| `Toggle related tool call grouping` | 切换相关工具调用分组 |
| `Toggle subagent picker` | 切换子智能体选择器 |
| `Go to next child session` | 转到下一个子会话 |
| `Go to previous child session` | 转到上一个子会话 |
| `Go to parent session` | 转到父会话 |
| `Pin or unpin session in the session list` | 在会话列表中置顶或取消置顶会话 |
| `Switch to session in quick slot 1` | 切换到快捷槽位 1 中的会话 |
| `Switch to session in quick slot 2` | 切换到快捷槽位 2 中的会话 |
| `Switch to session in quick slot 3` | 切换到快捷槽位 3 中的会话 |
| `Switch to session in quick slot 4` | 切换到快捷槽位 4 中的会话 |
| `Switch to session in quick slot 5` | 切换到快捷槽位 5 中的会话 |
| `Switch to session in quick slot 6` | 切换到快捷槽位 6 中的会话 |
| `Switch to session in quick slot 7` | 切换到快捷槽位 7 中的会话 |
| `Switch to session in quick slot 8` | 切换到快捷槽位 8 中的会话 |
| `Switch to session in quick slot 9` | 切换到快捷槽位 9 中的会话 |
| `Switch to session tab 1` | 切换到会话页签 1 |
| `Switch to session tab 2` | 切换到会话页签 2 |
| `Switch to session tab 3` | 切换到会话页签 3 |
| `Switch to session tab 4` | 切换到会话页签 4 |
| `Switch to session tab 5` | 切换到会话页签 5 |
| `Switch to session tab 6` | 切换到会话页签 6 |
| `Switch to session tab 7` | 切换到会话页签 7 |
| `Switch to session tab 8` | 切换到会话页签 8 |
| `Switch to session tab 9` | 切换到会话页签 9 |
| `Switch to session tab 10` | 切换到会话页签 10 |
| `Delete stash entry` | 删除存储条目 |
| `Open provider list from model dialog` | 从模型对话框打开提供商列表 |
| `Toggle model favorite status` | 切换模型收藏状态 |
| `List available models` | 列出可用模型 |
| `Next recently used model` | 下一个最近使用的模型 |
| `Previous recently used model` | 上一个最近使用的模型 |
| `Next favorite model` | 下一个收藏模型 |
| `Previous favorite model` | 上一个收藏模型 |
| `List MCP servers` | 列出 MCP 服务器 |
| `Connect integration` | 连接集成 |
| `List agents` | 列出智能体 |
| `Next agent` | 下一个智能体 |
| `Previous agent` | 上一个智能体 |
| `Cycle model variants` | 循环切换模型变体 |
| `List model variants` | 列出模型变体 |
| `Scroll messages up by one page` | 将消息向上滚动一页 |
| `Scroll messages down by one page` | 将消息向下滚动一页 |
| `Scroll messages up by one line` | 将消息向上滚动一行 |
| `Scroll messages down by one line` | 将消息向下滚动一行 |
| `Scroll messages up by half page` | 将消息向上滚动半页 |
| `Scroll messages down by half page` | 将消息向下滚动半页 |
| `Navigate to first message` | 跳转到第一条消息 |
| `Navigate to last message` | 跳转到最后一条消息 |
| `Navigate to next message` | 跳转到下一条消息 |
| `Navigate to previous message` | 跳转到上一条消息 |
| `Navigate to next user message` | 跳转到下一条用户消息 |
| `Navigate to previous user message` | 跳转到上一条用户消息 |
| `Navigate to last user message` | 跳转到最后一条用户消息 |
| `Copy message` | 复制消息 |
| `Undo message` | 撤销消息 |
| `Redo message` | 重做消息 |
| `Toggle thinking blocks visibility` | 切换思考块的可见性 |
| `Submit prompt` | 提交提示 |
| `Queue prompt` | 提示入队 |
| `Clear editor context` | 清空编辑器上下文 |
| `View image attachments` | 查看图片附件 |
| `Open skill selector` | 打开技能选择器 |
| `Stash prompt` | 存储提示 |
| `Pop stashed prompt` | 弹出存储的提示 |
| `List stashed prompts` | 列出存储的提示 |
| `Clear input field` | 清空输入框 |
| `Paste from clipboard` | 从剪贴板粘贴 |
| `Submit input` | 提交输入 |
| `Insert newline in input` | 在输入中插入换行 |
| `Move cursor left in input` | 在输入中向左移动光标 |
| `Move cursor right in input` | 在输入中向右移动光标 |
| `Move cursor up in input` | 在输入中向上移动光标 |
| `Move cursor down in input` | 在输入中向下移动光标 |
| `Select left in input` | 在输入中向左选择 |
| `Select right in input` | 在输入中向右选择 |
| `Select up in input` | 在输入中向上选择 |
| `Select down in input` | 在输入中向下选择 |
| `Move to start of line in input` | 在输入中移动到行首 |
| `Move to end of line in input` | 在输入中移动到行尾 |
| `Select to start of line in input` | 在输入中选择到行首 |
| `Select to end of line in input` | 在输入中选择到行尾 |
| `Move to start of visual line in input` | 在输入中移动到视觉行首 |
| `Move to end of visual line in input` | 在输入中移动到视觉行尾 |
| `Select to start of visual line in input` | 在输入中选择到视觉行首 |
| `Select to end of visual line in input` | 在输入中选择到视觉行尾 |
| `Move to start of buffer in input` | 在输入中移动到缓冲区首 |
| `Move to end of buffer in input` | 在输入中移动到缓冲区尾 |
| `Select to start of buffer in input` | 在输入中选择到缓冲区首 |
| `Select to end of buffer in input` | 在输入中选择到缓冲区尾 |
| `Delete line in input` | 在输入中删除行 |
| `Delete to end of line in input` | 在输入中删除到行尾 |
| `Delete to start of line in input` | 在输入中删除到行首 |
| `Backspace in input` | 在输入中退格 |
| `Delete character in input` | 在输入中删除字符 |
| `Undo in input` | 在输入中撤销 |
| `Redo in input` | 在输入中重做 |
| `Move word forward in input` | 在输入中按单词前移 |
| `Move word backward in input` | 在输入中按单词后移 |
| `Select word forward in input` | 在输入中按单词向前选择 |
| `Select word backward in input` | 在输入中按单词向后选择 |
| `Delete word forward in input` | 在输入中按单词向前删除 |
| `Delete word backward in input` | 在输入中按单词向后删除 |
| `Select all in input` | 在输入中全选 |
| `Previous history item` | 上一条历史项 |
| `Next history item` | 下一条历史项 |
| `Previous subagent` | 上一个子智能体 |
| `Next subagent` | 下一个子智能体 |
| `Navigate to subagent` | 跳转到子智能体 |
| `Interrupt subagent` | 中断子智能体 |
| `Previous shell` | 上一个 Shell |
| `Next shell` | 下一个 Shell |
| `View shell output` | 查看 Shell 输出 |
| `Kill shell command` | 终止 Shell 命令 |
| `Previous terminal` | 上一个终端 |
| `Next terminal` | 下一个终端 |
| `Move to previous dialog item` | 移动到上一个对话框项 |
| `Move to next dialog item` | 移动到下一个对话框项 |
| `Move up one page in dialog` | 在对话框中向上移动一页 |
| `Move down one page in dialog` | 在对话框中向下移动一页 |
| `Move to first dialog item` | 移动到第一个对话框项 |
| `Move to last dialog item` | 移动到最后一个对话框项 |
| `Submit selected dialog item` | 提交所选的对话框项 |
| `Submit dialog prompt` | 提交输入 |
| `Rename integration account` | 重命名集成账户 |
| `Delete integration account` | 删除集成账户 |
| `Generate worktree name` | 生成工作树名称 |
| `New worktree` | 新建工作树 |
| `Move session to worktree` | 移动会话到工作树 |
| `Delete worktree` | 删除工作树 |
| `Refresh worktrees` | 刷新工作树 |
| `Move to previous autocomplete item` | 移动到上一个自动补全项 |
| `Move to next autocomplete item` | 移动到下一个自动补全项 |
| `Hide autocomplete` | 隐藏自动补全 |
| `Select autocomplete item` | 选择自动补全项 |
| `Complete autocomplete item` | 确认自动补全项 |
| `Toggle permission prompt fullscreen` | 切换权限提示全屏 |
| `Toggle plugin` | 切换插件 |
| `Toggle MCP server` | 切换 MCP 服务器 |
| `View plugin error` | 查看插件错误 |
| `Install plugin from plugin dialog` | 从插件对话框安装插件 |
| `Update plugin from plugin dialog` | 从插件对话框更新插件 |
| `Check for plugin updates from plugin dialog` | 从插件对话框检查插件更新 |
| `Suspend terminal` | 挂起终端 |
| `Toggle terminal title` | 切换终端标题 |
| `Open plugin manager dialog` | 打开插件管理器对话框 |
| `Install plugin` | 安装插件 |
| `Toggle which-key panel` | 切换 which-key 面板 |
| `Switch which-key layout` | 切换 which-key 布局 |
| `Toggle which-key pending preview` | 切换 which-key 待显预览 |
| `Previous which-key group` | 上一个 which-key 分组 |
| `Next which-key group` | 下一个 which-key 分组 |
| `Scroll which-key up` | 向上滚动 which-key |
| `Scroll which-key down` | 向下滚动 which-key |
| `Page which-key up` | which-key 向上翻页 |
| `Page which-key down` | which-key 向下翻页 |
| `Jump to first which-key binding` | 跳转到第一个 which-key 绑定 |
| `Jump to last which-key binding` | 跳转到最后一个 which-key 绑定 |

共 234 条


## 附录 B:其余 111 条锚点全表(键 → 译文)


**`packages/tui/src/component/devtools-bar.tsx`** (25 条)

| 锚点键 | 译文 |
|---|---|
| `Server` | 服务器 |
| `UI` | 界面 |
| `Theme` | 主题 |
| `Tools` | 工具 |
| `Experiments` | 实验功能 |
| `Render` | 渲染 |
| `label="Status"` | label="状态" |
| `"Connected"` | "已连接" |
| `label="Reconnect"` | label="重连" |
| `label="Last error"` | label="最近错误" |
| `label="Version"` | label="版本" |
| `label="Address"` | label="地址" |
| `label="Name"` | label="名称" |
| `label="Mode"` | label="模式" |
| `Server details unavailable` | 服务器详情不可用 |
| `Switch to ` | 切换到  |
| `Debug overlay` | 调试覆盖层 |
| `Time to first draw` | 首次绘制耗时 |
| `Turn token usage (verbose)` | 每轮 tokens 用量(详细) |
| `Turn token usage` | 每轮 tokens 用量 |
| `label="Loop"` | label="事件循环" |
| `label="Memory"` | label="内存" |
| `Write debug snapshot` | 写入调试快照 |
| `Writing debug snapshot…` | 正在写入调试快照... |
| `"Unknown"` | "未知" |

**`packages/tui/src/component/session-frame.tsx`** (8 条)

| 锚点键 | 译文 |
|---|---|
| `message: "Unable to load terminal"` | message: "无法加载终端" |
| `title: "Focus session pane"` | title: "聚焦会话窗格" |
| `title: "Focus right pane"` | title: "聚焦右侧窗格" |
| `rightPane() === "sidebar" ? "Hide sidebar" : "Show sidebar"` | rightPane() === "sidebar" ? "隐藏侧边栏" : "显示侧边栏" |
| `rightPane() === "terminal" ? "Hide terminal pane" : "Show terminal pane"` | rightPane() === "terminal" ? "隐藏终端窗格" : "显示终端窗格" |
| `title: "Select terminal"` | title: "选择终端" |
| `title: "Close terminal pane"` | title: "关闭终端窗格" |
| `title: "New terminal"` | title: "新建终端" |

**`packages/tui/src/component/session-tabs.tsx`** (8 条)

| 锚点键 | 译文 |
|---|---|
| `title: "Close tab menu", group: "Tabs"` | title: "关闭页签菜单", group: "页签" |
| `title: "New tab"` | title: "新建页签" |
| `title: "Rename"` | title: "重命名" |
| `title: "Copy session ID"` | title: "复制会话 ID" |
| `message: "Session ID copied to clipboard"` | message: "会话 ID 已复制到剪贴板" |
| `title: "Close"` | title: "关闭" |
| `"Untitled session"` | "未命名会话" |
| `?? "U"` | ?? "未" |

**`packages/tui/src/component/reconnecting.tsx`** (4 条)

| 锚点键 | 译文 |
|---|---|
| `"Restarting service…"` | "正在重启服务..." |
| `"Connection lost…"` | "连接已断开..." |
| `"Your session will resume automatically."` | "会话将自动恢复。" |
| `"Reconnecting to the server automatically."` | "正在自动重新连接服务器。" |

**`packages/tui/src/mini/footer.command.tsx`** (6 条)

| 锚点键 | 译文 |
|---|---|
| `display: "Compact session"` | display: "精简会话" |
| `display: "Switch agent"` | display: "切换智能体" |
| `title="Select agent"` | title="选择智能体" |
| `title="Select model"` | title="选择模型" |
| `display: "Shell"` | display: "命令行" |
| `display: "Settings"` | display: "设置" |

**`packages/tui/src/mini/footer.view.tsx`** (9 条)

| 锚点键 | 译文 |
|---|---|
| `group: "Model"` | group: "模型" |
| `exiting() ? "exit" : "stop"` | exiting() ? "退出" : "停止" |
| `exiting() ? "Exit pending" : "Stop pending"` | exiting() ? "退出待确认" : "停止待确认" |
| ``Press ${key} again to ${exiting() ? "exit" : "interrupt"}`` | `按 ${key} 再次${exiting() ? "退出" : "中断"}` |
| ``${key} again to ${exiting() ? "exit" : "interrupt"}`` | `${key} 再次${exiting() ? "退出" : "中断"}` |
| ``${key} again: ${action}`` | `${key} 再次: ${action}` |
| `shell() ? "Shell" : ""` | shell() ? "命令行" : "" |
| `interruptLabel() ? `${interruptLabel()} stop` : "Running"` | interruptLabel() ? `${interruptLabel()} 停止` : "运行中" |
| `${interruptLabel()} interrupt` | ${interruptLabel()} 中断 |

**`packages/tui/src/mini/footer.menu.tsx`** (1 条)

| 锚点键 | 译文 |
|---|---|
| `{props.empty ?? "No matching items"}` | {props.empty ?? "未找到匹配项"} |

**`packages/tui/src/mini/footer.prompt.tsx`** (1 条)

| 锚点键 | 译文 |
|---|---|
| `title: "Paste"` | title: "粘贴" |

**`packages/tui/src/mini/footer.subagent.tsx`** (1 条)

| 锚点键 | 译文 |
|---|---|
| `? "interrupt" : "stop"` | ? "中断" : "停止" |

**`packages/tui/src/mini/tool.ts`** (2 条)

| 锚点键 | 译文 |
|---|---|
| `"Unknown"` | "未知" |
| `title: url ? `WebFetch ${url}` : "WebFetch"` | title: url ? `网页获取 ${url}` : "网页获取" |

**`packages/tui/src/mini/stream-v2.transport.ts`** (1 条)

| 锚点键 | 译文 |
|---|---|
| `text: "Compaction"` | text: "压缩" |

**`packages/tui/src/mini/scrollback.writer.tsx`** (1 条)

| 锚点键 | 译文 |
|---|---|
| `-{item.deletions ?? 0} line{item.deletions === 1 ? "" : "s"}` | -{item.deletions ?? 0} 行 |

**`packages/tui/src/component/error-component.tsx`** (3 条)

| 锚点键 | 译文 |
|---|---|
| `title=" Error "` | title=" 错误 " |
| `title=" Stack trace "` | title=" 堆栈跟踪 " |
| `"Clipboard write failed. Try again or report the crash manually."` | "剪贴板写入失败。请重试或手动报告崩溃。" |

**`packages/tui/src/component/migration-overlay.tsx`** (1 条)

| 锚点键 | 译文 |
|---|---|
| `title: "Data migration failed"` | title: "数据迁移失败" |

**`packages/tui/src/component/plugin-route-missing.tsx`** (2 条)

| 锚点键 | 译文 |
|---|---|
| `Unknown plugin route: {props.id}/{props.name}` | 未知插件路由: {props.id}/{props.name} |
| `>go home</text>` | >前往首页</text> |

**`packages/tui/src/component/theme-error-toast.tsx`** (1 条)

| 锚点键 | 译文 |
|---|---|
| `title: `Failed to load theme: ${name}`` | title: `加载主题失败: ${name}` |

**`packages/tui/src/feature-plugins/system/stats.tsx`** (1 条)

| 锚点键 | 译文 |
|---|---|
| `title: "back"` | title: "返回" |

**`packages/tui/src/feature-plugins/system/stats-data.ts`** (1 条)

| 锚点键 | 译文 |
|---|---|
| `label: "sessions"` | label: "会话" |

**`packages/tui/src/feature-plugins/prompt/btw.tsx`** (3 条)

| 锚点键 | 译文 |
|---|---|
| `placeholder: "Ask anything"` | placeholder: "随便问点什么" |
| `group: "Dialog"` | group: "对话框" |
| `{copied() ? "" : " copy"}` | {copied() ? "" : " 复制"} |

**`packages/tui/src/feature-plugins/prompt/footer.tsx`** (2 条)

| 锚点键 | 译文 |
|---|---|
| `>agents</span>` | >智能体</span> |
| `>commands</span>` | >命令</span> |

**`packages/tui/src/feature-plugins/home/footer.tsx`** (1 条)

| 锚点键 | 译文 |
|---|---|
| `{failed()} plugin{failed() === 1 ? "" : "s"} failed` | {failed()} 个插件失败 |

**`packages/tui/src/feature-plugins/sidebar/footer.tsx`** (1 条)

| 锚点键 | 译文 |
|---|---|
| `>Connect provider</text>` | >连接提供商</text> |

**`packages/tui/src/feature-plugins/system/diff-viewer.tsx`** (4 条)

| 锚点键 | 译文 |
|---|---|
| `title: "View"` | title: "查看" |
| `> help</span>` | > 帮助</span> |
| `title: "Go to the start of the diff"` | title: "转到差异开头" |
| `title: "Go to the end of the diff"` | title: "转到差异结尾" |

**`packages/tui/src/util/permission.ts`** (2 条)

| 锚点键 | 译文 |
|---|---|
| `action === "read" ? "Read" : "List"` | action === "read" ? "读取" : "列出" |
| `action === "glob" ? "Glob" : "Grep"` | action === "glob" ? "通配符" : "搜索" |

**`packages/tui/src/util/form.ts`** (1 条)

| 锚点键 | 译文 |
|---|---|
| `label: "No"` | label: "否" |

**`packages/cli/src/commands/handlers/auth/form.ts`** (1 条)

| 锚点键 | 译文 |
|---|---|
| `label: "No"` | label: "否" |

**`packages/cli/src/commands/handlers/auth/login.ts`** (2 条)

| 锚点键 | 译文 |
|---|---|
| `hint: "connected"` | hint: "已连接" |
| `?? "API key"` | ?? "API密钥" |

**`packages/cli/src/commands/handlers/uninstall.ts`** (1 条)

| 锚点键 | 译文 |
|---|---|
| `label: "Config"` | label: "配置" |

**`packages/tui/src/plugin/api.tsx`** (1 条)

| 锚点键 | 译文 |
|---|---|
| `label: "Open"` | label: "打开" |

**`packages/tui/src/context/session-tabs-model.ts`** (1 条)

| 锚点键 | 译文 |
|---|---|
| `= "New session"` | = "新会话" |

**`packages/tui/src/routes/session/index.tsx`** (7 条)

| 锚点键 | 译文 |
|---|---|
| `source() === "shell" ? "Shell" : Locale.titlecase(stringValue(metadata()?.agent) ?? "Subagent")` | source() === "shell" ? "命令行" : Locale.titlecase(stringValue(metadata()?.agent) ?? "子智能体") |
| ``${Locale.number(input)} in · ${Locale.number(output)} out`` | `${Locale.number(input)} 输入 · ${Locale.number(output)} 输出` |
| `return "Command cancelled"` | return "命令已取消" |
| `return "Command timed out"` | return "命令已超时" |
| `return `Command exited with code ${props.message.exit}`` | return `命令退出码 ${props.message.exit}` |
| `file.source.type === "uri" ? file.source.uri : "attachment"` | file.source.type === "uri" ? file.source.uri : "附件" |
| `return "(no answer)"` | return "(无回答)" |

**`packages/tui/src/routes/session/permission.tsx`** (1 条)

| 锚点键 | 译文 |
|---|---|
| `store.expanded ? "minimize" : "fullscreen"` | store.expanded ? "收起" : "全屏" |

**`packages/tui/src/routes/session/dialog-execute.tsx`** (5 条)

| 锚点键 | 译文 |
|---|---|
| `return "Receiving code…"` | return "正在接收代码..." |
| `return "Running"` | return "运行中" |
| `return `Failed${duration}`` | return `失败${duration}` |
| `return `Completed${duration}`` | return `已完成${duration}` |
| `props.part.state.status === "completed" ? "No output" : "Waiting for output…"` | props.part.state.status === "completed" ? "暂无输出" : "正在等待输出..." |

**`packages/tui/src/routes/session/composer/subagents-tab.tsx`** (2 条)

| 锚点键 | 译文 |
|---|---|
| `: "Subagent",` | : "子智能体", |
| `return "Running"` | return "运行中" |
