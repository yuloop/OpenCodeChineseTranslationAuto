#!/usr/bin/env python3
"""V2 汉化覆盖账本：测量上游 V2 源码的用户可见界面串规模，并交叉 V1/V2 翻译资产。

用法：
    python3 tools/v2_i18n_coverage.py --source-dir <上游 V2 检出目录> [--json-out <路径>]

只读：不修改 V2 源码、V1/V2 翻译资产与任何仓库文件（--json-out 用 mkstemp+replace 原子写）。

测量口径（什么算「用户可见界面串」）：
    产品面分层——
      tui/cli（主宇宙）：packages/tui/src/** 与 packages/cli/src/**，
        V1 词表两个包族的 V2 后继，也是 opencode CLI/TUI 二进制的全部终端 UI 面
        （已核验：tui/cli 不 import 其它内部包，仅 @opencode-ai/pty）。
      其它包（分流计）：packages/<pkg>/** 的独立产品面（app 桌面端 / console / web /
        ui 组件库 / session-ui / theme / plugin-browser / storybook 等），
        V1/V2 资产不覆盖，只计数并单列，不进主账本。
    文件过滤（产品文件）：排除路径段 test/tests/__tests__/e2e/storybook/fixtures/
        i18n/demo/component-tests/dist/node_modules；basename 含 .test./.spec./
        .stories./.bench./.fixture./demo/.d.ts；扩展名 .ts/.tsx/.js/.jsx；跳过 >1MB 文件。
    字面量上下文（提取器 = 字符串状态机 + JSX 子解析，见 parse）：
      attr      JSX 属性名 ∈ UI_ATTRS 的字符串/模板字面量（含 name={...} 表达式内
                括号深度 0 的分支，覆盖 title={a ? "X" : "Y"}）
      prop      对象属性名 ∈ UI_PROPS 的同名字面量（表达式内括号深度 0）
      jsx-text  JSX 文本节点（标签之间的渲染文本）
      jsx-expr  JSX 子表达式容器 {cond ? "A" : "B"} 中括号深度 0 的字面量
      code      其余代码位置字面量
    两档口径：
      Tier A（主口径，用户可见核心）= attr/prop/jsx-text/jsx-expr + 自然语言过滤
      Tier B（宽口径，敏感性上界）= Tier A + code 上下文自然语言字面量
        （错误/日志/throw 等裸文案；V1 词表历来也翻此类，如 console.error 串）
    自然语言过滤：含 ≥1 ASCII 字母；排除路径/URL/导入（./、../、/ 开头、含 ://、
        含 \\）、标识符样式单 token（^[a-z][a-zA-Z0-9_]*$）、纯符号/数字/hex/颜色、
        空串、true/false/null 等；模板字面量保留 ${...} 原样；多行模板不计
        （V1 仅 1 条系统提示代码补丁属此类，非界面串）。
    去重：occurrences=逐出现次；distinct=归一化（去首尾空白、压缩连续空白）后的
        去重值——翻译工作量按 distinct 计（同串多处出现 = 1 次翻译 + N 处锚点）。

覆盖/迁移判定（与 apply 门禁同语义，复刻 i18n.go replacementMatches：
    简单词 ^[a-zA-Z0-9]+$ 按 \\b 边界，其余按子串）：
    covered      ∃ V2 资产锚点规则（目标文件=该串所在文件）键 K 命中该串
    migratable   未被覆盖，且 ∃ V1 词表键 K：K==该串，或（K 非简单词且互相包含）
                 ——V1 已有对应译文，只需在 V2 重新锚定
    fuzzy-simple 未被覆盖且 V1 无整串译文，但 ∃ V1 简单词键 K 以 \\b 命中该串
                 ——单词级模糊命中（如 Skills ⊂ "Close and reopen Skills…"），
                   需人工复核（直接锚定会产生中英混杂），单独列账
    new          以上皆无——V2 新串，必须新翻译

退出码：0=完成；2=预期内失败（参数/目录缺失）；未预期异常=traceback + 非 0。
"""

from __future__ import annotations

import argparse
import bisect
import json
import os
import re
import sys
import tempfile
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from v2spike_probe import (  # noqa: E402
    EXIT_EXPECTED,
    EXIT_OK,
    ExpectedError,
    is_simple_word,
    load_rules,
    matches,
)

MAX_FILE_BYTES = 1024 * 1024
SEARCH_EXTS = {".ts", ".tsx", ".js", ".jsx"}

EXCLUDED_SEGMENTS = {
    "test",
    "tests",
    "__tests__",
    "e2e",
    "storybook",
    "fixtures",
    "fixture",
    "i18n",
    "demo",
    "component-tests",
    "dist",
    "node_modules",
}
EXCLUDED_BASENAME_MARKERS = (".test.", ".spec.", ".stories.", ".bench.", ".fixture.", "demo", ".d.ts")

# JSX 属性名 / 对象属性名白名单：这些位置的字符串字面量即渲染文本。
# 依据：V1 词表键形态 + 对 v2.0.13 tui/cli 全树属性名频次调查（title×519 /
# description×193 / label×142 / category×132 / message×79 / text×52 /
# placeholder×18 / display×37 / group×258 / footer×13 等）；不含 name/id/type/
# kind/variant/mode/status/value/keywords 等标识符/枚举/搜索词位。
# footer 的产品源码取值均为键位提示（"/editor" 形态，被路径规则滤除）或徽标
# （dialog-model 的 "Free"）；"show"/"hide" 配置值仅出现在测试文件（已排除）。
UI_ATTRS = {
    "title",
    "desc",
    "description",
    "label",
    "placeholder",
    "message",
    "hint",
    "text",
    "category",
    "tooltip",
    "aria-label",
    "alt",
    "empty",
    "prompt",
    "confirm",
    "cancel",
    "ok",
    "subtitle",
    "caption",
    "notice",
    "detail",
    "details",
    "header",
    "display",
    "summary",
    "group",
    "footer",
}

PRIMARY_PACKAGES = ("tui", "cli")
PRIMARY_PREFIXES = ("packages/tui/src/", "packages/cli/src/")

TAG_NAME_RE = re.compile(r"[A-Za-z][A-Za-z0-9_.]*")

GENERIC_TAG_RE = re.compile(r"[A-Z]")


def is_generic_tag(name: str) -> bool:
    """单字母大写「标签名」是泛型参数约定（type Trace = <T>(...)，<T,>，<T extends X>），
    不是 JSX 组件；JSX 组件均为多字母 PascalCase。"""
    return GENERIC_TAG_RE.fullmatch(name) is not None
# < 之前处于表达式位置才算 JSX 标签（标识符/)/] 之后是比较或泛型）
JSX_PREFIX_CHARS = set("({[,=?:&|>;\n\r\t ")
JSX_PREFIX_KEYWORDS = ("return", "yield", "await", "typeof", "case", "in", "of")

IDENTIFIER_RE = re.compile(r"^[a-z][a-zA-Z0-9_]*$")
PURE_SYMBOL_RE = re.compile(r"^[0-9.,%+\-\s]*$")
HEX_COLOR_RE = re.compile(r"^#?[0-9a-fA-F]{3,8}$")
NON_UI_WORDS = {"true", "false", "null", "undefined", "none", "nan", "infinity"}


# ---------------------------------------------------------------------------
# 字符串状态机：记录所有字符串/模板字面量；同时产出「掩码骨架」（等长空格）
# ---------------------------------------------------------------------------


def scan_literals(content: str) -> tuple[list[dict], str]:
    """返回 (字面量列表, 掩码骨架)。

    字面量: {value, start, end, quote}；模板字面量保留 ${...} 原样，
    插值体内的嵌套字面量另行记录（上下文 code）。骨架与原文等长，偏移一致。
    栈元素为 (state, start)：模板插值 ${} 内开/关字符串时逐层保存恢复起点。
    """
    literals: list[dict] = []
    out = list(content)
    stack: list[tuple[str, int]] = []
    state = "code"  # code | line | block | sq | dq | bt
    i = 0
    n = len(content)
    start = 0
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
                start = i + 1
                out[i] = " "
                i += 1
                continue
            if ch == "}" and stack:
                state, start = stack.pop()
                out[i] = " "
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
                out[i] = out[i + 1] = " "
                state = "code"
                i += 2
                continue
            out[i] = " "
            i += 1
            continue
        # 字符串态 sq/dq/bt
        if ch == "\\":
            out[i] = " "
            if i + 1 < n:
                out[i + 1] = " "
            i += 2
            continue
        closer = {"sq": "'", "dq": '"', "bt": "`"}[state]
        if state == "bt" and ch == "$" and nxt == "{":
            stack.append((state, start))
            state = "code"
            out[i] = out[i + 1] = " "
            i += 2
            continue
        if ch == closer:
            literals.append({"value": content[start:i], "start": start, "end": i + 1, "quote": closer})
            for k in range(start, i + 1):
                out[k] = " "
            if stack:
                state, start = stack.pop()
            else:
                state = "code"
            i += 1
            continue
        out[i] = " "
        i += 1
    return literals, "".join(out)


# ---------------------------------------------------------------------------
# JSX 子解析（在掩码骨架上做，偏移与原文一致）
# ---------------------------------------------------------------------------


def looks_like_jsx_prefix(skeleton: str, pos: int) -> bool:
    j = pos - 1
    while j >= 0 and skeleton[j] in " \t":
        j -= 1
    if j < 0:
        return True
    prev = skeleton[j]
    if prev in JSX_PREFIX_CHARS:
        return True
    for kw in JSX_PREFIX_KEYWORDS:
        k = j - len(kw) + 1
        if k >= 0 and skeleton[k : j + 1] == kw and (k == 0 or not (skeleton[k - 1].isalnum() or skeleton[k - 1] == "_")):
            return True
    return False


def is_self_closing(skeleton: str, after: int) -> bool:
    """after 为开标签 > 的下一索引；<br/> 形状返回 True。"""
    return after >= 2 and skeleton[after - 2] == "/"


def match_brace(skeleton: str, j: int, end: int) -> int:
    """j 指向 {；返回配对 } 的下一索引，未闭合返回 end。"""
    depth = 0
    while j < end:
        c = skeleton[j]
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return j + 1
        j += 1
    return end


def parse_jsx(skeleton: str) -> tuple[list[tuple[int, int]], list[tuple[int, int]]]:
    """返回 (文本节点区间, jsx-expr 区间)。

    文本节点: JSX 标签之间的渲染文本（含首尾空白，由调用方过滤）。
    jsx-expr: JSX 子表达式容器中括号深度 0 的区段（三元分支/直接字面量）。
    嵌套标签用栈匹配；自闭合标签不压栈；开标签属性区的 {...} 表达式
    （render props / view props，如 emptyView={<Switch>…</Switch>}）递归扫描，
    其中的 JSX 树同样提取文本节点。
    """
    texts: list[tuple[int, int]] = []
    exprs: list[tuple[int, int]] = []
    n = len(skeleton)

    def skip_open_tag(j: int, end: int) -> int:
        """j 指向标签名之后；返回开标签 > 的下一索引，未闭合返回 -1。

        先跳过泛型类型参数表（<DialogSelect<Foo | Bar> ...> 形态，Solid 常见），
        属性区的 {...} 表达式交给 scan_expr 递归（其中的 JSX 树要提文本）。
        """
        k = j
        while k < end and skeleton[k] in " \t":
            k += 1
        if k < end and skeleton[k] == "<":
            depth = 0
            while k < end:
                ch = skeleton[k]
                if ch == "<":
                    depth += 1
                elif ch == ">":
                    depth -= 1
                    if depth == 0:
                        k += 1
                        break
                elif ch == "=" and k + 1 < end and skeleton[k + 1] == ">":
                    k += 2  # 泛型里的函数类型 (x: T) => void，> 不是闭合
                    continue
                elif ch == "{":
                    k = match_brace(skeleton, k, end)
                    continue
                k += 1
            j = k
        while j < end:
            c = skeleton[j]
            if c == "{":
                k = match_brace(skeleton, j, end)
                scan_expr(j + 1, k - 1)
                j = k
                continue
            if c == ">":
                return j + 1
            j += 1
        return -1

    def scan_expr(start: int, end: int) -> None:
        j = start
        paren = 0
        seg = start
        while j < end:
            c = skeleton[j]
            if c == "(":
                if paren == 0 and j > seg:
                    exprs.append((seg, j))
                paren += 1
            elif c == ")":
                paren -= 1
                if paren == 0:
                    seg = j + 1
            elif c == "<":
                m = TAG_NAME_RE.match(skeleton, j + 1)
                if m and not is_generic_tag(m.group(0)) and looks_like_jsx_prefix(skeleton, j):
                    if paren == 0 and j > seg:
                        exprs.append((seg, j))
                    after = skip_open_tag(m.end(), end)
                    if after >= 0:
                        if is_self_closing(skeleton, after):
                            j = after
                        else:
                            j = scan_children(after, end, stop_tag=m.group(0))
                        seg = j
                        continue
            j += 1
        if end > seg:
            exprs.append((seg, end))

    def scan_children(start: int, end: int, stop_tag: str | None = None) -> int:
        j = start
        stack: list[str] = []
        while j < end:
            c = skeleton[j]
            if c == "<":
                if skeleton.startswith("</", j):
                    close = skeleton.find(">", j, end)
                    nxt = close + 1 if close >= 0 else end
                    name_m = TAG_NAME_RE.match(skeleton, j + 2)
                    name = name_m.group(0) if name_m else None
                    if stop_tag is not None and name == stop_tag and not stack:
                        return nxt
                    if stack:
                        stack.pop()
                    j = nxt
                    continue
                m = TAG_NAME_RE.match(skeleton, j + 1)
                if m and not is_generic_tag(m.group(0)) and looks_like_jsx_prefix(skeleton, j):
                    after = skip_open_tag(m.end(), end)
                    if after < 0:
                        j = m.end()
                        continue
                    if not is_self_closing(skeleton, after):
                        stack.append(m.group(0))
                    j = after
                    continue
                j += 1  # children 中的裸 <（非法 JSX 或误判）跳过
                continue
            if c == "{":
                k = match_brace(skeleton, j, end)
                scan_expr(j + 1, k - 1)
                j = k
                continue
            if c == ">":
                j += 1  # children 中的裸 > 跳过
                continue
            k = j
            while k < end and skeleton[k] not in "<{":
                k += 1
            if k > j:
                texts.append((j, k))
            j = k
        return j

    j = 0
    while j < n:
        if skeleton[j] != "<":
            j += 1
            continue
        m = TAG_NAME_RE.match(skeleton, j + 1)
        if not m or is_generic_tag(m.group(0)) or not looks_like_jsx_prefix(skeleton, j):
            j += 1
            continue
        after = skip_open_tag(m.end(), n)
        if after < 0:
            j = m.end()
            continue
        if is_self_closing(skeleton, after):
            j = after
        else:
            j = scan_children(after, n, stop_tag=m.group(0))
    return texts, exprs


def assign_value_spans(content: str, lit_by_start: dict[int, dict], masked_flags: list[bool], names: set[str], kind: str) -> list[tuple[int, int, str]]:
    """把 UI 属性/对象属性的字面量（含 {...} 表达式内括号深度 0 分支）标记上下文。

    kind: "attr"（name=...）或 "prop"（name: ...）。只在非掩码（非字符串/注释）区域匹配。
    括号深度 0 的引号字面量即渲染值（覆盖 title="X"、title={a ? "X" : "Y"}）；
    调用参数内部的字面量（paren≥1）不计——那是代码不是界面文本。
    """
    spans: list[tuple[int, int, str]] = []
    if kind == "attr":
        pattern = re.compile(r"([A-Za-z_][A-Za-z0-9_]*)\s*=\s*")
    else:
        pattern = re.compile(r"([A-Za-z_][A-Za-z0-9_]*)\s*:\s*")
    for m in pattern.finditer(content):
        name = m.group(1)
        if name not in names:
            continue
        if masked_flags[m.start()]:
            continue
        j = m.end()
        n = len(content)
        # 跳过空白与可选 {
        while j < n and content[j] in " \t":
            j += 1
        if j < n and content[j] == "{":
            k = match_brace(content, j, n)
            region_end = k - 1
            j += 1
        else:
            # 直值区域：到括号深度 0 的 , ; 或换行为止（箭头函数参数括号不截断，
            # 覆盖 label: () => "Restart" 形态）
            region_end = j
            depth = 0
            while region_end < n:
                ch = content[region_end]
                if ch in "([{":
                    depth += 1
                elif ch in ")]}":
                    depth -= 1
                    if depth < 0:
                        break
                elif ch in ",;\n\r" and depth == 0:
                    break
                region_end += 1
        # 区域内的字面量：括号深度 0 的引号字面量即渲染值（三元分支/直接值）
        paren = 0
        while j < region_end and j < n:
            ch = content[j]
            if ch == "(":
                paren += 1
            elif ch == ")":
                paren -= 1
            elif ch in "'\"`" and paren == 0:
                lit = lit_by_start.get(j + 1)
                if lit is not None:
                    spans.append((lit["start"], lit["end"], f"{kind}:{name}"))
                    j = lit["end"]
                    continue
            j += 1
    return spans


def build_masked_flags(content: str, literals: list[dict]) -> list[bool]:
    """True = 位于字符串/注释内（属性/对象属性匹配时排除这些区域）。"""
    flags = [False] * len(content)
    for lit in literals:
        for k in range(lit["start"], lit["end"]):
            flags[k] = True
    # 注释区域
    state = "code"
    i = 0
    n = len(content)
    while i < n:
        ch = content[i]
        nxt = content[i + 1] if i + 1 < n else ""
        if state == "code":
            if ch == "/" and nxt == "/":
                flags[i] = flags[i + 1] = True
                state = "line"
                i += 2
                continue
            if ch == "/" and nxt == "*":
                flags[i] = flags[i + 1] = True
                state = "block"
                i += 2
                continue
            i += 1
            continue
        flags[i] = True
        if state == "line" and ch == "\n":
            state = "code"
        elif state == "block" and ch == "*" and nxt == "/":
            flags[i + 1] = True
            state = "code"
            i += 1
        i += 1
    return flags


def extract_occurrences(content: str, jsx: bool = True) -> list[dict]:
    """提取单文件全部候选：{value, start, context}（context 含 code）。

    jsx=False 时跳过 JSX 子解析（.ts/.js 无 JSX，其中的 <T> 多为泛型/比较，
    强行解析会把代码当文本节点）。
    """
    literals, skeleton = scan_literals(content)
    masked = build_masked_flags(content, literals)
    lit_by_start = {lit["start"]: lit for lit in literals}
    sorted_starts = sorted(lit_by_start)
    texts, exprs = parse_jsx(skeleton) if jsx else ([], [])
    spans: list[tuple[int, int, str]] = []
    spans += assign_value_spans(content, lit_by_start, masked, UI_ATTRS, "attr")
    spans += assign_value_spans(content, lit_by_start, masked, UI_ATTRS, "prop")

    occurrences: list[dict] = []
    claimed: set[int] = set()

    def claim(lit: dict, context: str) -> None:
        if lit["start"] in claimed:
            return
        claimed.add(lit["start"])
        occurrences.append({"value": lit["value"], "start": lit["start"], "context": context})

    # attr/prop：精确到字面量边界
    for start, end, context in spans:
        lit = lit_by_start.get(start)
        if lit is not None and lit["end"] == end:
            claim(lit, context)
    # jsx-expr：区段内（括号深度 0）的全部字面量
    for seg_start, seg_end in exprs:
        idx = bisect.bisect_left(sorted_starts, seg_start)
        while idx < len(sorted_starts) and sorted_starts[idx] < seg_end:
            claim(lit_by_start[sorted_starts[idx]], "jsx-expr")
            idx += 1
    for s, e in texts:
        occurrences.append({"value": content[s:e], "start": s, "context": "jsx-text"})
    for lit in literals:
        if lit["start"] not in claimed:
            occurrences.append({"value": lit["value"], "start": lit["start"], "context": "code"})
    return occurrences


# ---------------------------------------------------------------------------
# 自然语言过滤
# ---------------------------------------------------------------------------


def is_natural_language(value: str, context: str) -> bool:
    text = value.strip()
    if not text or "\n" in text:
        return False  # 多行模板不计（代码块/提示词模板）
    if not re.search(r"[A-Za-z]", text):
        return False
    if text.startswith(("./", "../", "/", "~/")):
        return False
    if "://" in text or "\\\\" in text:
        return False
    if PURE_SYMBOL_RE.match(text) or HEX_COLOR_RE.match(text):
        return False
    if text.lower() in NON_UI_WORDS:
        return False
    if context == "code":
        # Tier B 收紧：单 token 标识符样式不算自然语言
        if IDENTIFIER_RE.match(text):
            return False
        # 模板插值 ${...} 之外的「散片」才参与判定：`${days}d ago` 的散片是
        # 「d ago」（有空格有字母，算界面串）；纯 `${x}` 散片为空，不算
        prose = re.sub(r"\$\{[^{}]*\}", " ", text)
        if " " not in prose.strip() and not re.search(r"[.,!?;:…—–]", prose):
            return False
        if re.search(r"[=;<>|&^%@#\\]", prose):
            return False
    return True


# ---------------------------------------------------------------------------
# 覆盖/迁移判定
# ---------------------------------------------------------------------------


def load_v1_entries(v1_assets_dir: Path) -> list[dict]:
    rules = load_rules(v1_assets_dir)
    return [
        {"key": key, "translation": translation, "rule": rule["rule"], "file": rule["file"]}
        for rule in rules
        for key, translation in rule["replacements"].items()
    ]


def load_v2_anchors(v2_assets_dir: Path) -> dict[str, list[dict]]:
    rules = load_rules(v2_assets_dir)
    per_file: dict[str, list[dict]] = defaultdict(list)
    for rule in rules:
        for key, translation in rule["replacements"].items():
            per_file[rule["file"]].append({"key": key, "translation": translation, "rule": rule["rule"]})
    return per_file


def key_applies(key: str, value: str) -> bool:
    """V1/V2 资产键是否命中该 UI 串（与 apply 门禁同语义）。"""
    if not key:
        return False
    if is_simple_word(key):
        return matches(value, key)
    return key == value or value in key or key in value


def classify(rel: str, value: str, v2_per_file: dict[str, list[dict]], v1_entries: list[dict]) -> str:
    for entry in v2_per_file.get(rel, []):
        if key_applies(entry["key"], value):
            return "covered"
    for entry in v1_entries:
        key = entry["key"]
        if key == value:
            return "migratable"
        if not is_simple_word(key) and (value in key or key in value):
            return "migratable"
    for entry in v1_entries:
        key = entry["key"]
        if is_simple_word(key) and key != value and matches(value, key):
            return "fuzzy-simple"
    return "new"


# ---------------------------------------------------------------------------
# 主流程
# ---------------------------------------------------------------------------


def is_product_file(rel: str) -> bool:
    if not rel.startswith("packages/"):
        return False
    segments = rel.split("/")
    if any(segment in EXCLUDED_SEGMENTS for segment in segments):
        return False
    basename = segments[-1]
    return not any(marker in basename for marker in EXCLUDED_BASENAME_MARKERS)


def normalize(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip())


def main() -> int:
    parser = argparse.ArgumentParser(description="Measure V2 user-visible UI string coverage")
    parser.add_argument("--source-dir", required=True, help="上游 V2 检出目录")
    parser.add_argument("--assets-v2-dir", default=None, help="V2 汉化资产目录（默认仓库内）")
    parser.add_argument("--assets-v1-dir", default=None, help="V1 词表目录（默认仓库内）")
    parser.add_argument("--json-out", default=None, help="可选：原子写入 JSON 报告的路径")
    args = parser.parse_args()

    source_dir = Path(args.source_dir).resolve()
    if not source_dir.is_dir():
        print(f"错误: --source-dir 不是目录: {source_dir}", file=sys.stderr)
        return EXIT_EXPECTED

    repo_root = Path(__file__).resolve().parent.parent
    v2_assets_dir = Path(args.assets_v2_dir).resolve() if args.assets_v2_dir else repo_root / "cli-go" / "internal" / "core" / "assets" / "opencode-i18n-v2"
    v1_assets_dir = Path(args.assets_v1_dir).resolve() if args.assets_v1_dir else repo_root / "cli-go" / "internal" / "core" / "assets" / "opencode-i18n"
    for label, path in (("V2 资产", v2_assets_dir), ("V1 词表", v1_assets_dir)):
        if not path.is_dir():
            print(f"错误: {label}目录不存在: {path}", file=sys.stderr)
            return EXIT_EXPECTED

    v2_per_file = load_v2_anchors(v2_assets_dir)
    v1_entries = load_v1_entries(v1_assets_dir)

    pkg_root = source_dir / "packages"
    if not pkg_root.is_dir():
        raise ExpectedError(f"packages 目录不存在: {pkg_root}")
    files: list[str] = []
    for path in sorted(pkg_root.rglob("*")):
        if not path.is_file() or path.suffix not in SEARCH_EXTS:
            continue
        if any(part == "node_modules" for part in path.parts):
            continue
        try:
            if path.stat().st_size > MAX_FILE_BYTES:
                continue
        except OSError:
            continue
        rel = path.relative_to(source_dir).as_posix()
        if is_product_file(rel):
            files.append(rel)

    # stats[package][tier][class] = {occurrences, distinct:set, files:set}
    stats: dict[str, dict[str, dict[str, dict]]] = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: {"occurrences": 0, "distinct": set(), "files": set()})))
    context_counts: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    class_cache: dict[tuple[str, str], str] = {}
    total_nodes = 0

    for rel in files:
        pkg = rel.split("/")[1]
        try:
            content = (source_dir / rel).read_text(encoding="utf-8", errors="replace").replace("\r\n", "\n")
        except OSError:
            continue
        for occ in extract_occurrences(content, jsx=rel.endswith((".tsx", ".jsx"))):
            total_nodes += 1
            context = occ["context"]
            context_counts[pkg][context] += 1
            if not is_natural_language(occ["value"], context):
                continue
            cache_key = (rel, occ["value"])
            cls = class_cache.get(cache_key)
            if cls is None:
                cls = classify(rel, occ["value"], v2_per_file, v1_entries)
                class_cache[cache_key] = cls
            tier = "A" if context != "code" else "B"
            bucket = stats[pkg][tier][cls]
            bucket["occurrences"] += 1
            bucket["distinct"].add(normalize(occ["value"]))
            bucket["files"].add(rel)

    print(f"源码树: {source_dir}")
    primary_files = sum(1 for f in files if f.startswith(PRIMARY_PREFIXES))
    print(f"产品文件数: {len(files)}(主宇宙 tui/cli: {primary_files};分流: {len(files) - primary_files})")
    print(f"提取节点总数(字面量+JSX 文本,过滤前): {total_nodes}")
    print()
    header = f"{'package':16} {'tier':4} {'class':14} {'occ':>7} {'distinct':>9} {'files':>6}"
    print(header)
    print("-" * len(header))
    for pkg in sorted(stats):
        for tier in ("A", "B"):
            for cls in ("covered", "migratable", "fuzzy-simple", "new"):
                bucket = stats[pkg][tier].get(cls)
                if not bucket:
                    continue
                print(f"{pkg:16} {tier:4} {cls:14} {bucket['occurrences']:>7} {len(bucket['distinct']):>9} {len(bucket['files']):>6}")
    print("-" * len(header))
    grand: dict[str, dict[str, dict]] = defaultdict(lambda: defaultdict(lambda: {"occurrences": 0, "distinct": set(), "files": set()}))
    for pkg in stats:
        for tier in ("A", "B"):
            for cls, bucket in stats[pkg][tier].items():
                agg = grand[tier][cls]
                agg["occurrences"] += bucket["occurrences"]
                agg["distinct"] |= bucket["distinct"]
                agg["files"] |= bucket["files"]
    for tier in ("A", "B"):
        for cls in ("covered", "migratable", "fuzzy-simple", "new"):
            bucket = grand[tier].get(cls)
            if not bucket:
                continue
            print(f"{'TOTAL':16} {tier:4} {cls:14} {bucket['occurrences']:>7} {len(bucket['distinct']):>9} {len(bucket['files']):>6}")

    print()
    print("按包汇总(Tier A,用户可见核心口径):")
    for pkg in sorted(stats):
        occ_a = sum(stats[pkg]["A"][cls]["occurrences"] for cls in stats[pkg]["A"])
        dis_a = set().union(*[stats[pkg]["A"][cls]["distinct"] for cls in stats[pkg]["A"]]) if stats[pkg]["A"] else set()
        files_a = set().union(*[stats[pkg]["A"][cls]["files"] for cls in stats[pkg]["A"]]) if stats[pkg]["A"] else set()
        mark = "主宇宙" if pkg in PRIMARY_PACKAGES else "分流"
        print(f"  {pkg:16} [{mark}] distinct={len(dis_a):6} occurrences={occ_a:6} files={len(files_a):5}")

    print()
    print("上下文分布(提取节点出现次数,自然语言过滤前):")
    for pkg in sorted(context_counts):
        parts = ", ".join(f"{ctx}={cnt}" for ctx, cnt in sorted(context_counts[pkg].items(), key=lambda kv: -kv[1]))
        print(f"  {pkg:16} {parts}")

    if args.json_out:
        report = {
            "source_dir": str(source_dir),
            "files_scanned": len(files),
            "total_nodes": total_nodes,
            "packages": {
                pkg: {
                    tier: {
                        cls: {
                            "occurrences": bucket["occurrences"],
                            "distinct": sorted(bucket["distinct"]),
                            "files": sorted(bucket["files"]),
                        }
                        for cls, bucket in classes.items()
                    }
                    for tier, classes in tiers.items()
                }
                for pkg, tiers in stats.items()
            },
        }
        out_path = Path(args.json_out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp_name = tempfile.mkstemp(prefix="oc-v2cov-", suffix=".json", dir=str(out_path.parent))
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                json.dump(report, handle, ensure_ascii=False, indent=2)
            os.replace(tmp_name, out_path)
        except BaseException:
            try:
                os.unlink(tmp_name)
            except OSError:
                pass
            raise
        print(f"\nJSON 报告已写入: {out_path}")

    return EXIT_OK


if __name__ == "__main__":
    try:
        sys.exit(main())
    except ExpectedError as err:
        print(f"错误: {err}", file=sys.stderr)
        sys.exit(EXIT_EXPECTED)
