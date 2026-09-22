#!/usr/bin/env python3
"""V2 汉化锚点别名迁移：把 V1 翻译条目重新锚定到上游 V2 源码的实际位置。

用法：
    # 只分析不落盘（默认）
    python3 tools/v2_anchor_migrate.py --source-dir <上游 V2 检出目录>

    # 生成 V2 专用资产 + 迁移报告
    python3 tools/v2_anchor_migrate.py --source-dir <目录> \
        --out-dir cli-go/internal/core/assets/opencode-i18n-v2 \
        --report docs/opencode-v2-anchor-migration.md

匹配语义与门禁口径：
    - 复用 tools/v2spike_probe.py 的 load_rules / v1_target / matches / build_tree_index，
      与 cli-go/internal/core/i18n.go 的 replacementMatches 完全一致
      （简单单词 ^[a-zA-Z0-9]+$ 按 \\b 边界，其余按子串；CRLF 归一化）。
    - 因此本工具判「可迁移」的每一条，都能被 apply --dry-run 门禁机械复验。

条目分类（逐条有据，不做猜测性改写）：
    kept     条目仍在 V1 映射目标处匹配（V1 路径在 V2 树中存在且命中）——锚点不变。
    moved    条目在 V1 目标处不再匹配，但在 V2 别处仍存在——重新锚定：
              唯一命中直接迁；多候选用「同规则共识 → 聚类 → 路径相似」迭代消歧
              （共识=同规则已锚定落数），仍并列/无共识/弱证据则列入 deferred，不猜。
    deferred 0 命中（功能/字符串消失）、仅宇宙外命中、多候选无法机械消歧、
              或标识符碰撞（简单词落在代码骨架里，替换会伤及代码）——保留旧锚点，
              在门禁里继续计为未匹配（分母不变，缺口可见），并写入待确认清单。

锚点宇宙：仅 packages/tui/src/** 与 packages/cli/src/**（V1 两个包族的 V2 后继），
排除测试/stories/e2e/i18n 语言包/demo 等非产品 UI 文件——宇宙外命中属子串巧合。

产出：
    --out-dir 下生成 V2 专用资产（V1 词表零改动）：
        config.json          元信息 + 逐条迁移清单（manifest；加载器跳过该文件）
        anchors/<flat>.json  每个 V2 目标文件一条规则 {"file": <V2 相对路径>, "replacements": {...}}
    --report 生成 Markdown 迁移报告（统计 + 逐规则表 + 待确认清单）。

退出码：0=完成；2=预期内失败（参数/目录缺失）；未预期异常=traceback + 非 0。
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from v2spike_probe import (  # noqa: E402
    EXIT_EXPECTED,
    EXIT_OK,
    ExpectedError,
    build_tree_index,
    is_simple_word,
    load_rules,
    matches,
    v1_target,
)

MAX_KEY_preview = 60

# V2 锚点候选宇宙：V1 词表的目标全部落在 packages/tui 与 packages/opencode 两个包族，
# 其 V2 后继为 packages/tui 与 packages/cli（spike 报告 §2.2 确认）。
# 宇宙外命中（其它包、测试、stories、i18n 语言包等）一律不作为锚点——那是子串巧合，
# 不是「文案搬家」；此类条目列入待人工确认并保留全树命中作为线索。
ANCHOR_UNIVERSE_PREFIXES = ("packages/tui/src/", "packages/cli/src/")
NON_ANCHOR_SEGMENTS = {
    "test",
    "tests",
    "__tests__",
    "e2e",
    "storybook",
    "component-tests",
    "fixtures",
    "fixture",
    "i18n",
}
NON_ANCHOR_BASENAME_MARKERS = (".test.", ".spec.", ".stories.", ".bench.", ".fixture.", "demo")

# ---------------------------------------------------------------------------
# 人工逐条复核结论（第二轮：17 宇宙外 + 12 并列/无共识/弱证据 + 7 标识符碰撞）
#
# 只收录「在 V2 源码找到确切位置且角色/语义等价」的重新锚定；判据写进 evidence,
# 原样进入 manifest 与报告，便于人工复核。机械消歧并列的条目一律不猜。
# ---------------------------------------------------------------------------

# (规则, 条目原文) -> (V2 锚点列表, 人工判据)
MANUAL_ANCHOR_OVERRIDES: dict[tuple[str, str], tuple[list[str], str]] = {
    (
        "components/command-panel.json",
        '"Manage workspaces"',
    ): (
        [
            "packages/tui/src/component/prompt/index.tsx",
            "packages/tui/src/config/keybind.ts",
        ],
        "V1 锚点 app.tsx 是命令面板定义处；V2 该命令仍存在且同名同 id："
        "prompt/index.tsx:618 title/619 desc（palette:true, name=session.move），"
        "keybind.ts:108 是同一命令 id 的键位标签。两处均为用户可见字符串。",
    ),
    (
        "routes/route-home.json",
        'category: "System"',
    ): (
        [
            "packages/tui/src/app.tsx",
            "packages/tui/src/mini/footer.command.tsx",
        ],
        "V1 首页 tips 分类标签（tips 功能随 V2 消失）；同串在 V2 命令面板仍是 "
        "category 标签：app.tsx 22 处、mini/footer.command.tsx 3 处，"
        "与 V2 资产已译的 category:\"Suggested\"/\"Prompt\" 同角色。",
    ),
    (
        "dialogs/dialog-toast.json",
        'message: "Copied to clipboard"',
    ): (
        [
            "packages/tui/src/component/dialog-integration.tsx",
            "packages/tui/src/routes/session/index.tsx",
            "packages/tui/src/util/selection.ts",
        ],
        "V1 锚点 ui/dialog.tsx:192 的 toast 调用；V2 全宇宙 4 处均为同一 "
        "toast.show({ message: \"Copied to clipboard\", ... }) 调用，字符串与角色完全一致。"
        "app.tsx:582 那处已由 common/error-messages.json 的同名 kept 条目覆盖，此处不重复锚定。",
    ),
}

# (规则, 条目原文) -> 理由：护栏误报（JSX 文本不是标识符），保留原锚点
MANUAL_KEEP_NOTES: dict[tuple[str, str], str] = {
    (
        "dialogs/dialog-status.json",
        "Status",
    ): (
        "护栏误报：code_skeleton 只抹引号字符串，JSX 文本节点不在其列。"
        "V2 packages/tui/src/component/dialog-status.tsx:23 全文件唯一一处 "
        "\\bStatus\\b 即 <text attributes={BOLD}>Status</text> 标签，"
        "与 V1 同文件:47 同一处 UI 文本，替换安全。"
    ),
}

# (规则, 条目原文) -> 理由：不得应用（替换会伤及代码），保留在分母里计未匹配
MANUAL_SUPPRESSED: dict[tuple[str, str], str] = {
    (
        "routes/route-session.json",
        "interrupted",
    ): (
        "V2 packages/tui/src/routes/session/index.tsx:1954 起新增 "
        "`const interrupted = createMemo(...)` 及 1957/1963/1977 的 interrupted() 调用；"
        "\\b 替换会把 const 声明与调用点一起改成中文而直接构建失败。"
        "真正的 UI 串在 1978 行 ` · interrupted`（与 V1 index.tsx:1568 同），"
        "需人工改用精确键，本轮不动。"
    ),
}

# 被 suppress 的条目锚点：V2 源码树中不存在的隔离路径，使 apply 判「目标文件不存在」
# 而继续计为未匹配（分母不变，缺口可见），且绝不落入任何真实源码文件。
QUARANTINE_ANCHOR_PREFIX = "packages/__no_v2_location__/"


def quarantine_anchor(v1_rel: str) -> str:
    return QUARANTINE_ANCHOR_PREFIX + v1_rel


# 待人工确认条目的事实说明（逐条人工核对 V2 v2.0.12 源码后填写）。
# 只记录看到的事实（V2 的确切位置/改名/角色差异），不做猜测性改写。
PENDING_NOTES: dict[tuple[str, str], str] = {
    ("components/command-panel.json", '"Connect provider"'): (
        "V2 app.tsx:934 同一命令 id `provider.connect` 的标题已改名为 "
        "\"Connect an integration\"（keybind.ts:168 为 \"Connect integration\"）；"
        "V1 原文在 V2 tui/cli 产品源码 0 命中，唯一命中在 "
        "packages/app/src/runtime/i18n/en.ts:89（桌面端英文词典，另一产品面）。"
    ),
    ("components/command-panel.json", '"Toggle MCPs"'): (
        "V2 app.tsx:882 同一命令 id `mcp.list` 标题改为 \"MCP servers\"，"
        "keybind.ts:167 为 \"List MCP servers\"；产品源码 0 命中，"
        "唯一命中 packages/app/src/runtime/i18n/en.ts:132。"
    ),
    ("components/inline-tools.json", 'pending="Preparing patch…"'): (
        "V2 routes/session/index.tsx:3072 仅余 \"Preparing write…\"、3379 "
        "\"# Preparing edit…\"，补丁工具的 pending 文案已不在该文件；"
        "唯一命中是测试快照 packages/tui/test/cli/tui/inline-tool-wrap-snapshot.test.tsx:77"
        "（断言旧行为）。"
    ),
    ("dialogs/cli-footer-command.json", "current"): (
        "V2 宇宙内 105 个文件命中，但全是更长标签内的词"
        "（\"Close current session tab\"/\"Share current session\"…）或注释；"
        "V1 侧 footer.command.tsx 本身就把 current 同时用作接口字段 "
        "`current: boolean`（第 30/35/44 行），V2 不新引入该类破损。"
    ),
    ("dialogs/cli-footer-command.json", "Skills"): (
        "V2 两处 UI 面均已被更精确的键覆盖：prompt/index.tsx:580 `title: \"Skills\"` "
        "由 components/component-prompt.json 译，dialog-skill.tsx:58 `title=\"Skills\"` "
        "由 dialogs/dialog-skill.json 译；裸 \\bSkills\\b 还会命中 "
        "dialog-skill.tsx:76 \"Close and reopen Skills to try again.\"，"
        "替换后成 \"Close and reopen 技能 to try again.\"（中英混杂）。"
    ),
    ("dialogs/cli-footer-view.json", "EXIT"): (
        "V1 footer.view.tsx:388 `if (exiting()) return \"EXIT\"`；V2 mini/footer.view.tsx "
        "已无 EXIT 徽标（改用 \"Shell\"/\"normal\"/\"Running\"）。唯一命中是 bash trap 串 "
        "packages/desktop/src/main/remote/cli.ts:90 与 shell 扫描测试 generated.test.ts:90。"
    ),
    ("dialogs/cli-footer-view.json", "SHELL"): (
        "V2 mini/footer.view.tsx:412/417 用 title case 的 \"Shell\"，\\bSHELL\\b 不再命中；"
        "宇宙内两处命中分别是 uninstall.ts:151 `process.env.SHELL`（环境变量，替换即破坏）"
        "与 prompt/traits.ts:25 的 @opentui/core EditorTraits 协议值。"
    ),
    ("dialogs/cli-footer-view.json", "BUILD"): (
        "V1 footer.view.tsx:391 `shell() ? \"SHELL\" : \"BUILD\"`；V2 已无 BUILD 徽标，"
        "唯一命中是 packages/tui/test/mini/footer.view.test.tsx:517 的 "
        "`expect(frame).not.toContain(\"BUILD\")`（负向断言）。"
    ),
    ("dialogs/cli-footer-view.json", "interrupt"): (
        "V2 每个候选文件里 interrupt 都同时是代码标识符：mini/footer.view.tsx:203 "
        "`const interrupt = ...`、209 `props.state().interrupt`、1018 `interrupt={...}`；"
        "footer.prompt.tsx:1193 是命令 id \"session.interrupt\"（替换会断开键位绑定）。"
    ),
    ("dialogs/cli-footer-view.json", "background"): (
        "V2 background 在候选文件中大量是属性/标识符：footer.view.tsx:699/723/753/963 "
        "`backgroundColor=`、762 `runTheme().background`、187 `!item.background`；"
        "dialog-update.tsx:148 `backgroundColor=`；footer.width.ts:17/32/72 是联合类型字面量。"
    ),
    ("dialogs/cli-footer-view.json", "subagents"): (
        "V2 footer 已无 \"subagents\" 标签；宇宙内命中是 import 路径 "
        "composer/index.tsx:7 `./subagents-tab`、composer tab id index.tsx:1174/1359 "
        "`tab: \"subagents\"`、prop `subagents={tabs}`（index.tsx:809）以及 footer.width.ts 的联合类型字面量。"
    ),
    ("dialogs/cli-footer-view.json", "cmd"): (
        "V1 footer.view.tsx:487 `label: \"cmd\"`；V2 mini/footer.view.tsx:473 同一处已改名 "
        "`label: \"menu\"`，V1 原文在 V2 产品源码 0 命中。"
    ),
    ("dialogs/cli-permission.json", "Allow always"): (
        "V2 util/permission.ts:164 同分支返回 \"Always allow\"（语序被上游调整），"
        "V1 原文在产品源码 0 命中；唯一命中 packages/ui/src/i18n/en.ts:231（UI 库英文词典）。"
    ),
    ("dialogs/cli-question.json", "Confirm"): (
        "V2 问题表单脚 footer.form.tsx（承接了本规则另外 4 条）已无独立 \"Confirm\" 标签"
        "（改用 formConfirm 逻辑与 \"Review\"）；宇宙内唯一独立 \"Confirm\" 是 "
        "util/permission.ts:166 的权限选项标签，已由 dialogs/cli-permission.json 锚定，再锚只会重复计数。"
    ),
    ("dialogs/dialog-agent.json", "native"): (
        "V1 dialog-agent.tsx:15 `description: item.native ? \"native\" : item.description`；"
        "V2 该文件已重写为 698 字节的 DialogSelect 薄封装，无 \"native\" 串；"
        "其余宇宙内命中全部是注释。"
    ),
    ("dialogs/dialog-export.json", "to confirm"): (
        "V1 锚点 dialog-export-options.tsx:177/182 的提示语在 V2 被键位标题取代"
        "（61 \"Next export option\"/73 \"Select export option\"），V1 原文不在该文件；"
        "宇宙内其余命中分散在 6 个无关对话框，按子串替换会得到 \"Press X again 确认\" 式中英混杂串。"
    ),
    ("dialogs/dialog-provider.json", 'label: "API key"'): (
        "V2 dialog-integration.tsx 已有 `placeholder=\"API key\"`（本规则已迁），"
        "`label: \"API key\"` 在产品源码 0 命中；宇宙外命中是 app 的 mock-server/stories "
        "与 core 的 azure 插件提示词。"
    ),
    ("dialogs/dialog-provider.json", "(Recommended)"): (
        "V1 锚点 dialog-provider.tsx 在 V2 已被 dialog-integration.tsx 取代且无该串；"
        "唯一命中 packages/core/src/tool/plugin/question.ts:21 是给模型的提示词模板。"
    ),
    ("dialogs/dialog-provider.json", "Low cost subscription for everyone"): (
        "产品源码 0 命中；唯一命中 packages/app/src/runtime/i18n/en.ts:173（桌面端英文词典）。"
    ),
    ("dialogs/dialog-provider.json", "Go to "): (
        "V1 dialog-provider.tsx:378/389 `Go to <span>https://opencode.ai/zen</span> to get a key`；"
        "V2 dialog-integration.tsx 无 \"Go to\"；宇宙内命中全是无关导航标签"
        "（\"Go to the start of the diff\"/\"Go to parent session\"），"
        "子串替换会得到 \"前往 the start of the diff\"。"
    ),
    ("dialogs/dialog-provider.json", "Custom provider"): (
        "产品源码 0 命中；命中在 packages/app/src/runtime/i18n/en.ts:231 与 "
        "packages/core/src/v1/config/config.ts（桌面端词典/配置注释）。"
    ),
    ("dialogs/dialog-rename.json", 'title="Rename Session"'): (
        "V1 锚点文件在 V2 仍在，但 dialog-session-rename.tsx:15 已改为 "
        "`title=\"Rename session\"`（s 小写）；V1 原文唯一命中是 "
        "packages/tui/test/cli/tui/dialog-prompt.test.tsx:47 的测试渲染。"
    ),
    ("dialogs/dialog-subagent.json", 'title: "Open"'): (
        "V1 锚点 routes/session/dialog-subagent.tsx 在 V2 不存在；产品源码 0 命中，"
        "命中在 packages/app/src/shell/commands/command.test.ts:14（桌面端命令目录解码单测）。"
    ),
    ("routes/route-footer.json", "Get started"): (
        "V1 footer.tsx:59 `Get started <span>/connect</span>`；V2 该文件不存在，"
        "产品源码 0 命中；命中在 packages/app 与 packages/console 的英文词典。"
    ),
    ("routes/route-footer.json", "Permission"): (
        "V1 footer.tsx:65 是 `{permissions().length} Permission(s)` 计数徽标，V2 该文件不存在。"
        "宇宙内唯一独立 \"Permission\" 是 mini/footer.permission.tsx:185 "
        "`width() < 24 ? \"Permission\" : \"Permission required\"`，只替换前半会得到 "
        "`? \"权限\" : \"Permission required\"` 的中英混杂三元式。"
    ),
    ("routes/route-header.json", 'label: "Subagent"'): (
        "V1 锚点 subagent-footer.tsx 在 V2 不存在；产品源码 0 命中，"
        "唯一宇宙内命中是开发 playground packages/tui/src/mini/demo.ts:748/776（按 demo 规则排除）。"
    ),
    ("routes/route-header.json", "Parent"): (
        "V1 subagent-footer.tsx:104 导航标签；该文件在 V2 不存在，产品源码 0 命中；"
        "宇宙外命中全是 packages/app/e2e 回归用例。"
    ),
    ("routes/route-header.json", "Prev"): (
        "V1 subagent-footer.tsx:114 导航标签；V2 无该导航标签，宇宙内 0 命中，"
        "命中在 packages/ui/src/components/*.stories.tsx。"
    ),
    ("routes/route-header.json", "Next"): (
        "V1 subagent-footer.tsx:124 独立导航标签；V2 该文件不存在，宇宙内 23 处 \\bNext\\b "
        "全是复合键位标题（\"Next item\"/\"Next export option\"…），"
        "子串替换会得到 \"上一个 item\" 式中英混杂。"
    ),
    ("routes/route-permission.json", '"Unknown"'): (
        "V1 permission.tsx:287 `typeof data.subagent_type === \"string\" ? data.subagent_type : \"Unknown\"`；"
        "V2 该文件仍在但已无此回退；宇宙内命中是 devtools-bar.tsx:60 的地址回退与 "
        "mini/tool.ts:335 的工具入参回退（角色不同）。"
    ),
    ("routes/route-session.json", '"Failed to unshare session"'): (
        "V1 锚点 index.tsx 在 V2 仍在但该串已不在；产品源码 0 命中，"
        "唯一命中 packages/app/src/runtime/i18n/en.ts:644。"
    ),
}


# 人工复核判据汇总：(规则, 条目原文) -> 判据文本（由 classify_rule 填充，main 使用前清空）
MANUAL_NOTES: dict[tuple[str, str], str] = {}


def in_anchor_universe(rel: str) -> bool:
    if not rel.startswith(ANCHOR_UNIVERSE_PREFIXES):
        return False
    segments = rel.split("/")
    if any(segment in NON_ANCHOR_SEGMENTS for segment in segments):
        return False
    basename = segments[-1]
    return not any(marker in basename for marker in NON_ANCHOR_BASENAME_MARKERS)


def code_skeleton(content: str) -> str:
    """把字符串字面量与注释替换为等长空格，剩余即「代码骨架」。

    用于判断简单词键是否出现在标识符/注释位置（而非 UI 字符串位置）。
    简单词按 \\b 边界匹配，落在代码骨架里意味着替换会伤及标识符
    （V1 线上游产物即存在此类替换，如 const interrupt → const 中断；
    V2 迁移不新引入该类破损，此类条目转待人工确认）。
    """
    out = list(content)
    state = "code"  # code | line | block | sq | dq | bt
    stack: list[str] = []
    i = 0
    n = len(content)
    while i < n:
        ch = content[i]
        nxt = content[i + 1] if i + 1 < n else ""
        if state == "code":
            if ch == "/" and nxt == "/":
                state = "line"
                out[i] = out[i + 1] = " "
                i += 2
                continue
            if ch == "/" and nxt == "*":
                state = "block"
                out[i] = out[i + 1] = " "
                i += 2
                continue
            if ch in "'\"`":
                state = {"'": "sq", '"': "dq", "`": "bt"}[ch]
                out[i] = " "
                i += 1
                continue
            if ch == "}" and stack:
                out[i] = " "
                state = stack.pop()
                i += 1
                continue
            i += 1
            continue
        if state == "line":
            if ch == "\n":
                state = "code"
            else:
                out[i] = " "
            i += 1
            continue
        if state == "block":
            if ch == "*" and nxt == "/":
                state = "code"
                out[i] = out[i + 1] = " "
                i += 2
                continue
            out[i] = " "
            i += 1
            continue
        # 字符串状态：sq/dq/bt；反斜杠转义跳过；bt 中 ${ 回到代码态
        if ch == "\\":
            out[i] = " "
            if i + 1 < n:
                out[i + 1] = " "
            i += 2
            continue
        closer = {"sq": "'", "dq": '"', "bt": "`"}[state]
        if state == "bt" and ch == "$" and nxt == "{":
            out[i] = out[i + 1] = " "
            stack.append(state)
            state = "code"
            i += 2
            continue
        if ch == closer:
            out[i] = " "
            state = stack.pop() if stack else "code"
            i += 1
            continue
        out[i] = " "
        i += 1
    return "".join(out)


_skeleton_cache: dict[str, str] = {}


def identifier_collision(rel: str, per_file: dict[str, str], word: str, fallback: str = "") -> bool:
    """简单词是否在锚点文件的代码骨架（标识符/注释）里出现。"""
    if rel not in _skeleton_cache:
        _skeleton_cache[rel] = code_skeleton(per_file[rel] if rel in per_file else fallback)
    return re.search(r"\b" + re.escape(word) + r"\b", _skeleton_cache[rel]) is not None


def path_similarity(candidate: str, v1_rel: str) -> int:
    """候选文件与 V1 目标路径的相似度：公共路径段 + 同名/同目录加权。"""
    segs_a = candidate.split("/")
    segs_b = v1_rel.split("/")
    score = len(set(segs_a) & set(segs_b))
    if segs_a[-1] == segs_b[-1]:
        score += 3
    if len(segs_a) > 1 and len(segs_b) > 1 and segs_a[-2] == segs_b[-2]:
        score += 2
    return score


def flatten_name(rel: str) -> str:
    return rel.replace("/", "-")


def classify_rule(rule: dict, per_file: dict[str, str], source_dir: Path) -> dict:
    """对单条规则的全部条目分类，返回 kept/moved/deferred 明细。"""
    v1_path = v1_target(source_dir, rule["file"])
    v1_rel = v1_path.relative_to(source_dir).as_posix() if v1_path else rule["file"]
    v1_content = ""
    if v1_path and v1_path.is_file():
        v1_content = v1_path.read_text(encoding="utf-8", errors="replace").replace("\r\n", "\n")

    keys = list(rule["replacements"].keys())
    kept: list[str] = []
    failing: list[str] = []
    for key in keys:
        if v1_content and matches(v1_content, key):
            kept.append(key)
        else:
            failing.append(key)

    # 每个失效条目在 V2 全树的命中文件（宇宙内 / 宇宙外分流）
    hits: dict[str, list[str]] = {}
    outside_hits: dict[str, list[str]] = {}
    for key in failing:
        found = [rel for rel, text in per_file.items() if matches(text, key)]
        hits[key] = [rel for rel in found if in_anchor_universe(rel)]
        outside_hits[key] = [rel for rel in found if not in_anchor_universe(rel)]

    # 聚类数：本规则全部条目在各候选文件中的存在数（衡量主题聚集度）
    cluster: dict[str, int] = defaultdict(int)
    for key in keys:
        for rel in hits.get(key, []):
            cluster[rel] += 1

    moved: list[dict] = []
    deferred: list[dict] = []
    suppressed: list[dict] = []
    # 共识：同规则已锚定条目在各文件的落数（每轮迭代更新，收敛前持续用于消歧）
    consensus: dict[str, int] = defaultdict(int)
    unresolved: list[str] = []
    for key in failing:
        found = hits[key]
        if not found:
            reason = "outside-universe" if outside_hits[key] else "no-hit"
            deferred.append({"key": key, "reason": reason, "hits": outside_hits[key]})
            continue
        unresolved.append(key)

    def rank(rel: str) -> tuple[int, int, int]:
        return (consensus[rel], cluster[rel], path_similarity(rel, v1_rel))

    # 迭代到不动点：唯一命中直接锚定；多候选按 (共识→聚类→路径相似) 决胜；
    # 简单词键要求共识≥1（无共识不猜）；无共识+聚类≤2+相似度<5 属弱证据。
    # 每轮新锚定提升该文件的共识，供下一轮消歧；规则内键序固定，结果确定。
    while unresolved:
        progress = False
        remaining: list[str] = []
        for key in unresolved:
            found = hits[key]
            if len(found) == 1:
                moved.append({"key": key, "anchor": found[0], "basis": "unique-hit", "hits": found})
                consensus[found[0]] += 1
                progress = True
                continue
            scored = sorted(found, key=lambda rel: (-rank(rel)[0], -rank(rel)[1], -rank(rel)[2], rel))
            best, second = scored[0], scored[1]
            if rank(best) == rank(second):
                remaining.append(key)
                continue
            if is_simple_word(key) and consensus[best] == 0:
                remaining.append(key)
                continue
            if consensus[best] == 0 and cluster[best] <= 2 and path_similarity(best, v1_rel) < 5:
                remaining.append(key)
                continue
            basis = f"consensus={consensus[best]},cluster={cluster[best]},sim={path_similarity(best, v1_rel)}"
            moved.append({"key": key, "anchor": best, "basis": basis, "hits": found})
            consensus[best] += 1
            progress = True
        unresolved = remaining
        if not progress:
            break

    # 收敛后仍未锚定 → deferred，记录当时最佳候选作为人工确认线索
    for key in unresolved:
        found = hits[key]
        scored = sorted(found, key=lambda rel: (-rank(rel)[0], -rank(rel)[1], -rank(rel)[2], rel))
        best, second = scored[0], scored[1]
        if rank(best) == rank(second):
            reason = "ambiguous"
        elif is_simple_word(key) and consensus[best] == 0:
            reason = "no-consensus"
        else:
            reason = "weak-evidence"
        deferred.append({"key": key, "reason": reason, "hits": found})

    order = {key: index for index, key in enumerate(keys)}
    deferred.sort(key=lambda item: order[item["key"]])

    # 标识符碰撞护栏：简单词键（\b 边界）若落在锚点文件的代码骨架（标识符/注释）里，
    # 替换会伤及代码（V1 产物已有此类先例，V2 迁移不新引入）→ 转待人工确认
    kept_guarded: list[str] = []
    for key in kept:
        if is_simple_word(key) and identifier_collision(v1_rel, per_file, key, fallback=v1_content):
            deferred.append({"key": key, "reason": "identifier-collision", "hits": [v1_rel]})
        else:
            kept_guarded.append(key)
    kept = kept_guarded
    guarded_moved: list[dict] = []
    for item in moved:
        if is_simple_word(item["key"]) and identifier_collision(item["anchor"], per_file, item["key"]):
            deferred.append({"key": item["key"], "reason": "identifier-collision", "hits": item["hits"]})
        else:
            guarded_moved.append(item)
    moved = guarded_moved
    deferred.sort(key=lambda item: order[item["key"]])

    # ---- 人工逐条复核结论（见文件头部 MANUAL_* 常量）----
    # 1) 护栏误报：简单词落在 JSX 文本节点而非标识符 → 恢复 kept（锚点不变）
    revived: list[dict] = []
    still_deferred: list[dict] = []
    for item in deferred:
        note = MANUAL_KEEP_NOTES.get((rule["rule"], item["key"]))
        if note and item["reason"] == "identifier-collision":
            revived.append({"key": item["key"], "reason": item["reason"]})
            MANUAL_NOTES[(rule["rule"], item["key"])] = note
        else:
            still_deferred.append(item)
    deferred = still_deferred
    kept = sorted({*kept, *(item["key"] for item in revived)}, key=lambda key: order[key])

    # 2) 有确凿证据的重新锚定（deferred → moved，basis 记 manual-verified）
    remaining_deferred: list[dict] = []
    for item in deferred:
        override = MANUAL_ANCHOR_OVERRIDES.get((rule["rule"], item["key"]))
        if override:
            anchors, evidence = override
            moved.append(
                {
                    "key": item["key"],
                    "anchor": anchors[0],
                    "anchors": list(anchors),
                    "basis": "manual-verified",
                    "evidence": evidence,
                    "hits": anchors,
                    "original_reason": item["reason"],
                }
            )
            MANUAL_NOTES[(rule["rule"], item["key"])] = evidence
        else:
            remaining_deferred.append(item)
    deferred = remaining_deferred

    # 3) 判定不得应用：替换会伤及代码 → 隔离到 V2 不存在的路径，继续计未匹配
    final_deferred: list[dict] = []
    for item in deferred:
        reason_note = MANUAL_SUPPRESSED.get((rule["rule"], item["key"]))
        if reason_note:
            suppressed.append({"key": item["key"], "reason": reason_note, "hits": item["hits"], "original_reason": item["reason"]})
            MANUAL_NOTES[(rule["rule"], item["key"])] = reason_note
        else:
            final_deferred.append(item)
    deferred = final_deferred
    deferred.sort(key=lambda item: order[item["key"]])
    suppressed.sort(key=lambda item: order[item["key"]])

    return {
        "rule": rule["rule"],
        "v1_file": rule["file"],
        "v1_rel": v1_rel,
        "v1_exists": bool(v1_content),
        "total": len(keys),
        "kept": kept,
        "kept_manual": [item["key"] for item in revived],
        "moved": moved,
        "deferred": deferred,
        "suppressed": suppressed,
        "replacements": rule["replacements"],
    }


def build_overlay(results: list[dict]) -> tuple[dict[str, list[tuple[str, str, str]]], dict]:
    """汇总为 {V2 锚点路径: [(key, 译文, 来源规则), ...]}。

    保留全部条目（含 deferred 保留旧锚点、suppressed 隔离到 V2 不存在的路径），
    同键多译不合并——同锚点同键分块到额外规则文件，复刻 V1 对共享目标的语义
    （同键各计一次，应用时先到者胜）。V1 条目一条不丢；同一 UI 串在 V2 多处
    等价位置出现时逐处锚定，门禁键数会略多于 V1 条目数。
    """
    per_anchor: dict[str, list[tuple[str, str, str]]] = defaultdict(list)
    conflicts: list[dict] = []
    seen: dict[tuple[str, str], str] = {}
    for result in results:
        v1_rel = result["v1_rel"]
        pairs = [(key, result["replacements"][key], v1_rel) for key in result["kept"]]
        for item in result["moved"]:
            # 人工复核的多锚点：同一 UI 串在 V2 多处等价位置出现，逐处锚定
            for anchor in item.get("anchors") or [item["anchor"]]:
                pairs.append((item["key"], result["replacements"][item["key"]], anchor))
        pairs += [(item["key"], result["replacements"][item["key"]], v1_rel) for item in result["deferred"]]
        # suppressed：锚到 V2 不存在的隔离路径 → apply 判「目标文件不存在」而计未匹配
        for item in result.get("suppressed", []):
            pairs.append((item["key"], result["replacements"][item["key"]], quarantine_anchor(v1_rel)))
        for key, translation, anchor in pairs:
            identity = (anchor, key)
            if identity in seen and seen[identity] != translation:
                conflicts.append({"anchor": anchor, "key": key[:MAX_KEY_preview], "rule": result["rule"], "kept": seen[identity], "dropped": translation})
            else:
                seen[identity] = translation
            per_anchor[anchor].append((key, translation, result["rule"]))
    return per_anchor, {"conflicts": conflicts}


def write_overlay(out_dir: Path, per_anchor: dict[str, list[tuple[str, str, str]]], manifest: dict, meta: dict) -> list[str]:
    anchors_dir = out_dir / "anchors"
    anchors_dir.mkdir(parents=True, exist_ok=True)
    # 先清掉上一轮生成的锚点文件：否则重生成不幂等（旧锚点会残留并被继续加载）
    for stale in sorted(anchors_dir.glob("*.json")):
        stale.unlink()
    written: list[str] = []
    used_names: dict[str, str] = {}
    for anchor in sorted(per_anchor):
        # 同键多译/同键多规则：first-fit 分块，每块内键唯一（JSON 对象约束）
        chunks: list[dict[str, str]] = []
        for key, translation, _ in per_anchor[anchor]:
            for chunk in chunks:
                if key not in chunk:
                    chunk[key] = translation
                    break
            else:
                chunks.append({key: translation})
        name = flatten_name(anchor)
        if name in used_names and used_names[name] != anchor:
            name = f"{name}-{abs(hash(anchor)) % 10000}"
        used_names[name] = anchor
        for index, chunk in enumerate(chunks):
            if not chunk:
                continue
            replacements = {key: chunk[key] for key in sorted(chunk)}
            payload = {"file": anchor, "replacements": replacements}
            suffix = "" if index == 0 else f"--dup{index + 1}"
            path = anchors_dir / f"{name}{suffix}.json"
            path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            written.append(path.relative_to(out_dir).as_posix())
    config = dict(meta)
    config["manifest"] = manifest
    (out_dir / "config.json").write_text(json.dumps(config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    written.append("config.json")
    return written


def write_report(
    report_path: Path,
    results: list[dict],
    totals: dict[str, int],
    meta: dict,
    before: dict[str, str] | None,
    after: dict[str, str] | None,
    v1_check: list[str] | None = None,
    manual_notes: dict[tuple[str, str], str] | None = None,
) -> None:
    lines: list[str] = []
    lines.append("# opencode V2 汉化 · 锚点别名迁移报告")
    lines.append("")
    lines.append(f"- 生成方式:`python3 tools/v2_anchor_migrate.py --source-dir <v2.0.12 检出>`(只读 V2 源码与 V1 词表,V1 词表零改动)")
    lines.append(f"- 上游对象:`anomalyco/opencode` tag `v2.0.12`({meta['upstream']['commit'][:12]})")
    lines.append(f"- V1 词表:`cli-go/internal/core/assets/opencode-i18n`(版本 {meta['v1AssetsVersion']},{totals['total']} 条)")
    lines.append(f"- V2 专用资产:`cli-go/internal/core/assets/opencode-i18n-v2`(由本工具生成,加载器按 layout 自动选择)")
    lines.append("")
    lines.append("## ① 度量:改前 vs 改后(同一命令,同一 V2 源码树)")
    lines.append("")
    lines.append("```bash")
    lines.append("OPENCODE_SOURCE_DIR=<v2.0.12 检出> ./opencode-cli apply --dry-run --strict --min-match-rate 1")
    lines.append("```")
    lines.append("")
    lines.append("| 口径 | 改前(origin/main) | 改后(本分支) |")
    lines.append("|---|---|---|")
    if before and after:
        lines.append(f"| 替换匹配 | {before['replacements']} | {after['replacements']} |")
        lines.append(f"| 匹配率 | {before['rate']} | {after['rate']} |")
        lines.append(f"| 文件统计 | {before['files']} | {after['files']} |")
        lines.append(f"| strict 门禁(100%) | {before['gate']} | {after['gate']} |")
    else:
        lines.append("| 替换匹配 | (未提供 --before/--after) | (未提供) |")
    lines.append("")
    lines.append("> 条目不丢:V2 资产保留全部 "
                 f"{totals['total']} 条 V1 条目(迁移不动的保留旧锚点或隔离锚点,继续计未匹配);")
    lines.append("> 但同一 UI 串在 V2 多处等价位置出现时会逐处锚定(见 ④-b re-anchored 行),")
    lines.append("> 门禁分母因此可能略高于 "
                 f"{totals['total']}——上表「替换匹配」列已同时给出分子/分母,可自行折算;")
    lines.append("> 按 V1 条目去重计的匹配条目数见 PR 描述。")
    lines.append("> V2 门禁阈值策略(阶梯/双轨)不在本单范围,本单只交付锚点迁移与度量。")
    lines.append("")
    if v1_check:
        lines.append("V1 线回归(同一命令,V1 门禁 `--min-match-rate 1` 不变,源码=上游 dev):")
        lines.append("")
        lines.append("| 口径 | 改前(origin/main 二进制) | 改后(本分支二进制) |")
        lines.append("|---|---|---|")
        lines.append(f"| V1 替换匹配 | {v1_check[0]} | {v1_check[1]} |")
        lines.append("")
    lines.append("## ② 条目变更统计")
    lines.append("")
    lines.append("| 分类 | 条数 | 占比 | 说明 |")
    lines.append("|---|---|---|---|")
    total = totals["total"]
    lines.append(f"| kept(锚点不变) | {totals['kept']} | {totals['kept'] / total:.1%} | V1 目标路径在 V2 仍在且条目命中 |")
    lines.append(f"| moved(重新锚定) | {totals['moved']} | {totals['moved'] / total:.1%} | 唯一命中 {totals['moved_unique']} 条;聚类/路径消歧 {totals['moved_disambiguated']} 条;人工复核逐条定位 {totals['moved_manual']} 条 |")
    lines.append(f"| deferred(待人工确认) | {totals['deferred']} | {totals['deferred'] / total:.1%} | V2 全树 0 命中 {totals['deferred_no_hit']} 条;仅宇宙外命中 {totals['deferred_outside_universe']} 条;多候选并列 {totals['deferred_ambiguous']} 条;简单词无同规则共识 {totals['deferred_no_consensus']} 条;弱证据 {totals['deferred_weak_evidence']} 条;标识符碰撞 {totals['deferred_identifier_collision']} 条 |")
    lines.append(f"| suppressed(判定不得应用) | {totals['suppressed']} | {totals['suppressed'] / total:.1%} | 替换会伤及代码;锚点隔离到 V2 不存在的路径,继续计未匹配(该 V1 条目仍在分母里) |")
    lines.append(f"| **合计** | **{total}** | 100% | |")
    lines.append("")
    lines.append("## ③ 逐规则迁移表(旧位置 → 新位置 → 匹配依据)")
    lines.append("")
    lines.append("| 规则(V1) | 条数 | kept | moved | deferred | 迁移去向(新锚点: 条数) |")
    lines.append("|---|---|---|---|---|---|")
    for result in sorted(results, key=lambda item: item["rule"]):
        dest: dict[str, int] = defaultdict(int)
        for item in result["moved"]:
            dest[item["anchor"]] += 1
        for item in result["deferred"]:
            dest[f"{result['v1_rel']}(保留旧锚点)"] += 1
        dest_text = "; ".join(f"`{anchor}` × {count}" for anchor, count in sorted(dest.items())) or "-"
        lines.append(
            f"| `{result['rule']}` | {result['total']} | {len(result['kept'])} | "
            f"{len(result['moved'])} | {len(result['deferred'])} | {dest_text} |"
        )
    lines.append("")
    lines.append("## ④ 待人工确认清单(deferred)")
    lines.append("")
    lines.append("不做猜测性改写;以下条目保留旧锚点,在 V2 门禁里继续计为未匹配。归因:")
    lines.append("")
    lines.append("- `no-hit`:V2 全树 0 命中(疑似随功能消失,如首页 tips 99 条)")
    lines.append("- `outside-universe`:仅命中 tui/cli 产品源码之外的文件(i18n 语言包/测试/stories/其它包),疑子串巧合")
    lines.append("- `ambiguous`:宇宙内多候选,共识/聚类/路径相似度全部并列")
    lines.append("- `no-consensus`:简单词(\\b 边界)多候选且同规则无共识锚点(子串巧合高发,如 demo 文件/变量名/环境变量)")
    lines.append("- `weak-evidence`:无共识、聚类≤2、与 V1 目标路径相似度<5")
    lines.append("- `identifier-collision`:简单词在锚点文件中处于标识符/注释位置(替换会伤及代码,如 theme.background、const interrupt;V1 产物已有同类先例,V2 不新引入)")
    lines.append("")
    lines.append("| 规则 | 条目(截断) | 原因 | 宇宙内/外命中(≤3) |")
    lines.append("|---|---|---|---|")
    for result in sorted(results, key=lambda item: item["rule"]):
        for item in result["deferred"]:
            hits = ", ".join(f"`{hit}`" for hit in item["hits"][:3]) or "-"
            lines.append(f"| `{result['rule']}` | {_escape(item['key'][:MAX_KEY_preview])} | {item['reason']} | {hits} |")
    lines.append("")
    lines.extend(
        _manual_review_section(results, manual_notes or {})
    )
    lines.append("")
    lines.append("## ⑤ 复现与审计")
    lines.append("")
    lines.append("```bash")
    lines.append("# 1) 重新生成 V2 资产与本报告(确定性输出,键序排序)")
    lines.append("python3 tools/v2_anchor_migrate.py --source-dir <v2.0.12 检出> \\")
    lines.append("    --out-dir cli-go/internal/core/assets/opencode-i18n-v2 \\")
    lines.append("    --report docs/opencode-v2-anchor-migration.md")
    lines.append("")
    lines.append("# 2) 逐条复验:apply --dry-run 对每一条 moved 条目做机械匹配复验")
    lines.append("OPENCODE_SOURCE_DIR=<v2.0.12 检出> ./opencode-cli apply --dry-run")
    lines.append("")
    lines.append("# 3) 逐条证据:V2 资产 config.json 的 manifest 字段(rule/key/from/to/basis)")
    lines.append("python3 -c \"import json;m=json.load(open('cli-go/internal/core/assets/opencode-i18n-v2/config.json'))['manifest'];print(len(m['entries']))\"")
    lines.append("```")
    lines.append("")
    lines.append("V1 线未受影响:V1 词表/注入脚本/门禁阈值/工作流零改动;V1 门禁在同一 V2 工具改动后仍为 100%(见 ① 与 PR 描述)。")
    lines.append("")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("\n".join(lines), encoding="utf-8")


def _escape(text: str) -> str:
    return text.replace("|", "\\|").replace("\n", "\\n")


# 第二轮人工复核的目标归因集合（17 宇宙外 + 12 并列/无共识/弱证据 + 7 标识符碰撞）
MANUAL_REVIEW_REASONS = (
    "outside-universe",
    "ambiguous",
    "no-consensus",
    "weak-evidence",
    "identifier-collision",
)


def _manual_review_section(results: list[dict], manual_notes: dict[tuple[str, str], str]) -> list[str]:
    """④-b:36 条待确认条目逐条复核结论表。

    结论分四类:
      re-anchored  在 V2 找到确切位置且角色/语义等价 → 已补进 V2 锚点映射
      keep-as-is   护栏误报(JSX 文本被当成标识符)→ 保留原锚点,替换安全
      suppressed   唯一残留位置同时是代码标识符 → 不得应用,隔离锚点
      pending      给不出确凿证据 → 待人工确认,附所见事实
    """
    rows: list[tuple[str, str, str, str, str]] = []
    for result in sorted(results, key=lambda item: item["rule"]):
        rule = result["rule"]
        kept_manual = set(result.get("kept_manual", []))
        moved_manual = {item["key"]: item for item in result["moved"] if item["basis"] == "manual-verified"}
        suppressed = {item["key"]: item for item in result.get("suppressed", [])}
        deferred = {item["key"]: item for item in result["deferred"]}
        reviewed = (
            set(kept_manual)
            | set(moved_manual)
            | set(suppressed)
            | {key for key, item in deferred.items() if item["reason"] in MANUAL_REVIEW_REASONS}
        )
        for key in [k for k in result["replacements"] if k in reviewed]:
            if key in moved_manual:
                item = moved_manual[key]
                anchors = item.get("anchors") or [item["anchor"]]
                conclusion = "re-anchored(已补锚点)"
                basis = "; ".join(f"`{a}`" for a in anchors)
                note = item.get("evidence") or manual_notes.get((rule, key), "")
            elif key in suppressed:
                conclusion = "suppressed(不得应用)"
                basis = "隔离到 V2 不存在的路径,继续计未匹配"
                note = suppressed[key].get("reason") or manual_notes.get((rule, key), "")
            elif key in kept_manual:
                conclusion = "keep-as-is(护栏误报)"
                basis = f"`{result['v1_rel']}`(锚点不变)"
                note = manual_notes.get((rule, key), "")
            else:
                item = deferred[key]
                conclusion = "pending(待人工确认)"
                hits = ", ".join(f"`{h}`" for h in item["hits"][:3]) or "-"
                basis = f"原锚点 `{result['v1_rel']}`;宇宙内/外命中:{hits}"
                note = _pending_note(rule, key, item["reason"])
            rows.append((rule, key, conclusion, basis, note))
    lines = [
        "### ④-b 第二轮人工逐条复核结论(36 条:17 宇宙外 + 12 并列/无共识/弱证据 + 7 标识符碰撞)",
        "",
        "逐条在 V2 源码定位后的处置。只对「找到确切位置且角色/语义等价」的条目补锚点;",
        "其余保留旧锚点并在此列明所见事实,不做猜测性改写。",
        "",
        "| 规则 | 条目 | 结论 | 锚点/命中 | 依据 |",
        "|---|---|---|---|---|",
    ]
    for rule, key, conclusion, basis, note in rows:
        lines.append(
            f"| `{rule}` | {_escape(key[:MAX_KEY_preview])} | {conclusion} | {_escape(basis)} | {_escape(note)} |"
        )
    lines.append("")
    counts: dict[str, int] = defaultdict(int)
    for _rule, _key, conclusion, _basis, _note in rows:
        counts[conclusion] += 1
    lines.append("小计:" + ";".join(f"{name} {count} 条" for name, count in sorted(counts.items())))
    return lines


def _pending_note(rule: str, key: str, reason: str) -> str:
    """待人工确认条目的事实说明(逐条人工核对 V2 源码后填写)。"""
    return PENDING_NOTES.get((rule, key), f"原归因 {reason};V2 源码无等价 UI 位置")


def parse_rate_args(values: list[str] | None) -> dict[str, str] | None:
    if not values:
        return None
    keys = ["replacements", "rate", "files", "gate"]
    return dict(zip(keys, values))


def main() -> int:
    parser = argparse.ArgumentParser(description="Migrate V1 i18n anchors to upstream V2 locations")
    parser.add_argument("--source-dir", required=True, help="上游 V2 检出目录")
    parser.add_argument("--assets-dir", default=None, help="V1 汉化规则目录(默认仓库内 assets)")
    parser.add_argument("--out-dir", default=None, help="V2 专用资产输出目录(提供才落盘)")
    parser.add_argument("--report", default=None, help="Markdown 迁移报告输出路径")
    parser.add_argument("--before", nargs=4, default=None, metavar=("REPLACEMENTS", "RATE", "FILES", "GATE"), help="改前门禁数字")
    parser.add_argument("--after", nargs=4, default=None, metavar=("REPLACEMENTS", "RATE", "FILES", "GATE"), help="改后门禁数字")
    parser.add_argument("--v1-check", nargs=2, default=None, metavar=("BEFORE", "AFTER"), help="V1 门禁回归(改前/改后,如 '497/497 (100.0%%) rc=0')")
    args = parser.parse_args()

    source_dir = Path(args.source_dir).resolve()
    if not source_dir.is_dir():
        print(f"错误: --source-dir 不是目录: {source_dir}", file=sys.stderr)
        return EXIT_EXPECTED

    repo_root = Path(__file__).resolve().parent.parent
    assets_dir = Path(args.assets_dir).resolve() if args.assets_dir else repo_root / "cli-go" / "internal" / "core" / "assets" / "opencode-i18n"

    rules = load_rules(assets_dir)
    _, per_file = build_tree_index(source_dir)

    MANUAL_NOTES.clear()
    results = [classify_rule(rule, per_file, source_dir) for rule in rules]
    per_anchor, extra = build_overlay(results)

    totals = {
        "total": sum(result["total"] for result in results),
        "kept": sum(len(result["kept"]) for result in results),
        "moved": sum(len(result["moved"]) for result in results),
        "moved_unique": sum(1 for result in results for item in result["moved"] if item["basis"] == "unique-hit"),
        "moved_disambiguated": sum(1 for result in results for item in result["moved"] if item["basis"] != "unique-hit"),
        "moved_manual": sum(1 for result in results for item in result["moved"] if item["basis"] == "manual-verified"),
        "deferred": sum(len(result["deferred"]) for result in results),
        "deferred_no_hit": sum(1 for result in results for item in result["deferred"] if item["reason"] == "no-hit"),
        "deferred_outside_universe": sum(1 for result in results for item in result["deferred"] if item["reason"] == "outside-universe"),
        "deferred_ambiguous": sum(1 for result in results for item in result["deferred"] if item["reason"] == "ambiguous"),
        "deferred_no_consensus": sum(1 for result in results for item in result["deferred"] if item["reason"] == "no-consensus"),
        "deferred_weak_evidence": sum(1 for result in results for item in result["deferred"] if item["reason"] == "weak-evidence"),
        "deferred_identifier_collision": sum(1 for result in results for item in result["deferred"] if item["reason"] == "identifier-collision"),
        "suppressed": sum(len(result.get("suppressed", [])) for result in results),
    }

    manifest_entries = []
    for result in results:
        for key in result["kept"]:
            manifest_entries.append(
                {"rule": result["rule"], "key": key, "status": "kept", "from": result["v1_rel"], "to": result["v1_rel"], "basis": "in-place-match"}
            )
        for item in result["moved"]:
            manifest_entries.append(
                {
                    "rule": result["rule"],
                    "key": item["key"],
                    "status": "moved",
                    "from": result["v1_rel"],
                    "to": item["anchor"],
                    "anchors": item.get("anchors") or [item["anchor"]],
                    "basis": item["basis"],
                    "evidence": item.get("evidence", ""),
                }
            )
        for item in result["deferred"]:
            manifest_entries.append(
                {"rule": result["rule"], "key": item["key"], "status": "deferred", "from": result["v1_rel"], "to": result["v1_rel"], "basis": item["reason"], "hits": item["hits"][:3]}
            )
        for item in result.get("suppressed", []):
            manifest_entries.append(
                {
                    "rule": result["rule"],
                    "key": item["key"],
                    "status": "suppressed",
                    "from": result["v1_rel"],
                    "to": quarantine_anchor(result["v1_rel"]),
                    "basis": "unsafe-identifier-collision",
                    "reason": item["reason"],
                }
            )
    manifest = {"totals": totals, "entries": manifest_entries, "conflicts": extra["conflicts"], "manualNotes": {f"{r}|{k}": v for (r, k), v in sorted(MANUAL_NOTES.items())}}

    v1_config_path = assets_dir / "config.json"
    v1_version = ""
    if v1_config_path.is_file():
        v1_version = json.loads(v1_config_path.read_text(encoding="utf-8")).get("version", "")

    head = source_dir / ".git"
    commit = ""
    if head.exists():
        try:
            commit = subprocess.run(
                ["git", "-C", str(source_dir), "rev-parse", "HEAD"],
                capture_output=True,
                text=True,
                check=True,
            ).stdout.strip()
        except (OSError, subprocess.SubprocessError):
            commit = ""

    meta = {
        "name": "opencode-zh-CN-v2",
        "description": "V2 专用汉化资产:由 tools/v2_anchor_migrate.py 从 V1 词表重新锚定生成(V1 词表零改动)",
        "layout": "v2",
        "generatedBy": "tools/v2_anchor_migrate.py",
        "upstream": {"repo": "anomalyco/opencode", "tag": "v2.0.12", "commit": commit},
        "v1AssetsVersion": v1_version,
        "totals": totals,
    }

    print(f"规则文件: {len(rules)}  翻译条目: {totals['total']}")
    print(f"kept(锚点不变): {totals['kept']}")
    print(f"moved(重新锚定): {totals['moved']} (唯一命中 {totals['moved_unique']}, 消歧 {totals['moved_disambiguated']})")
    print(f"deferred(待人工确认): {totals['deferred']} "
          f"(0 命中 {totals['deferred_no_hit']}, 宇宙外 {totals['deferred_outside_universe']}, "
          f"多候选并列 {totals['deferred_ambiguous']}, 简单词无共识 {totals['deferred_no_consensus']}, "
          f"弱证据 {totals['deferred_weak_evidence']}, 标识符碰撞 {totals['deferred_identifier_collision']})")
    print(f"V2 锚点文件数: {len([anchor for anchor, entries in per_anchor.items() if entries])}")
    if extra["conflicts"]:
        print(f"⚠ 同键不同译冲突(保留首个,详见 manifest): {len(extra['conflicts'])} 处")
    print()
    header = f"{'rule':44} {'total':>5} {'kept':>5} {'moved':>6} {'defer':>6}"
    print(header)
    print("-" * len(header))
    for result in sorted(results, key=lambda item: item["rule"]):
        print(
            f"{result['rule']:44} {result['total']:>5} {len(result['kept']):>5} "
            f"{len(result['moved']):>6} {len(result['deferred']):>6}"
        )

    if args.out_dir:
        out_dir = Path(args.out_dir).resolve()
        written = write_overlay(out_dir, per_anchor, manifest, meta)
        print(f"\nV2 资产已写入: {out_dir}({len(written)} 个文件)")

    if args.report:
        write_report(
            Path(args.report).resolve(),
            results,
            totals,
            meta,
            parse_rate_args(args.before),
            parse_rate_args(args.after),
            args.v1_check,
            MANUAL_NOTES,
        )
        print(f"迁移报告已写入: {Path(args.report).resolve()}")

    return EXIT_OK


if __name__ == "__main__":
    try:
        sys.exit(main())
    except ExpectedError as err:
        print(f"错误: {err}", file=sys.stderr)
        sys.exit(EXIT_EXPECTED)
