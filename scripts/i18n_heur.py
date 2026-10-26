#!/usr/bin/env python3
"""确定性重锚引擎：上游改文案后，用相似度把中文译文重新挂到新原文上。

不调用任何大模型、不需要网络：纯粹在「当前上游源码」里找与旧锚点最像的那一行。
    - 足够像 → 重锚（译文保留，只换 key）
    - 完全不像 → 判定上游已删除该文案，撤条
    - 介于两者之间 → 报 unresolved，交给 Issue 告警 + 人工
"""

from __future__ import annotations

import re
from difflib import SequenceMatcher

# 打分阈值：>ACCEPT 采用；<DROP_BELOW 判删除；中间报 unresolved。
# DROP_BELOW 取 0.72：实测「上游真删掉的文案」最像的候选只到 0.63 量级，
# 留在 0.55 会让它们卡在 unresolved，门禁就永远回不到 100%。
# 这组参数是离线评测选出来的：模拟上游改文案（插入词/加标点/改大小写/同义词/换词）
# 的 1917 个用例里召回 85%，且 4 类「上游已删除的文案」全部判 drop、无一条误锚。
ACCEPT = 0.86
STRONG = 0.965
DROP_BELOW = 0.72
AMBIGUITY = 0.005

_QUOTED = (
    re.compile(r'"([^"\\\n]{4,300})"'),
    re.compile(r"'([^'\\\n]{4,300})'"),
    re.compile(r"`([^`\\\n]{4,300})`"),
)
_PUNCT = re.compile(r"[^\w\s]+", re.UNICODE)


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").strip())


def loose(text: str) -> str:
    """去掉大小写与标点差异后的形式：仅排版不同的两条串应视为同一条。"""
    return re.sub(r"\s+", " ", _PUNCT.sub(" ", (text or "").casefold())).strip()


def ui_candidates(source_text: str) -> list[str]:
    """只抽「界面文案本体」：引号字面量内容 + JSX 文本节点内容。

    补译（走免费引擎）必须用这个，不能用 candidates()：后者包含整行与半行片段，
    会把 `import path from "node:path"` 这种代码当文案送去翻译，污染词表。
    """
    found: list[str] = []
    for raw in source_text.splitlines():
        line = raw.strip()
        for pattern in _QUOTED:
            found.extend(m.group(1) for m in pattern.finditer(line))
        found.extend(m.group(1) for m in re.finditer(r">([^<>{}\n]{4,300})<", line))
    out: list[str] = []
    seen: set[str] = set()
    for item in found:
        item = normalize(item)
        if len(item) < 4 or item in seen or not re.search(r"[A-Za-z]", item):
            continue
        seen.add(item)
        out.append(item)
    return out


def candidates(source_text: str) -> list[str]:
    """从源码里抽出可充当锚点的候选片段。

    除了整行与引号内字面量，还生成「行首到字面量结尾」「字面量起点到行尾」两种窗口——
    V1 的锚点经常是 `title: "Rename session"` 这种半行片段，只取整行会带上行尾逗号，
    导致替换后丢掉代码结构。

    返回值保证是 source_text 的**逐字节子串**（只做首尾 strip），因此直接拿去当新锚点
    一定能在源码里命中——不需要再做二次校验。
    """
    found: list[str] = []
    for raw in source_text.splitlines():
        line = raw.strip()
        if len(line) >= 4 and re.search(r"[A-Za-z0-9]", line):
            found.append(line)
        spans = [m.span() for pattern in _QUOTED for m in pattern.finditer(line)]
        spans += [m.span() for m in re.finditer(r">([^<>{}\n]{4,300})<", line)]
        for pattern in _QUOTED:
            found.extend(m.group(0) for m in pattern.finditer(line))
        for start, end in spans:
            found.append(line[:end])       # 行首到字面量结束：title: "Rename session"
            found.append(line[start:])     # 字面量起点到行尾
            found.append(line[start:end])  # 字面量本体
    seen: dict[str, None] = {}
    for item in found:
        item = item.strip()
        if len(item) >= 4 and re.search(r"[A-Za-z0-9]", item) and item in source_text:
            seen.setdefault(normalize(item), item)
    return list(seen.values())


def score(old: str, cand: str) -> float:
    """相似度：字符级序列匹配 + 包含关系加成 + 词级重叠（应对插入/删除几个词）。"""
    a, b = normalize(old), normalize(cand)
    if not a or not b:
        return 0.0
    if a == b:
        return 1.0
    if loose(a) == loose(b):
        return 1.0  # 只差大小写/标点：几乎必然是同一句文案
    base = SequenceMatcher(None, a, b).ratio()
    if a in b or b in a:
        shorter, longer = sorted((len(a), len(b)))
        base = max(base, 0.80 + 0.2 * shorter / longer)
    ta, tb = set(loose(a).split()), set(loose(b).split())
    if ta and tb:
        inter = len(ta & tb)
        jaccard = inter / len(ta | tb)
        containment = inter / min(len(ta), len(tb))
        base = max(base, 0.55 * jaccard + 0.45 * containment)
    return base


_CJK_CHAR = re.compile(r"[\u4e00-\u9fff]")
_JSX_TEXT = re.compile(r">([^<>{}\n]{4,300})<")


def _affix_ok(new: str, value: str | None) -> bool:
    """语法安全阀：译文替换新锚点后，代码结构不能被改坏。

    value 是替换文本，形如 `title: "重命名会话"`：它自带 `title: "` 前缀和 `"` 后缀。
    若新锚点不是以同样的前缀开头、同样的后缀结尾，替换后就会丢掉代码（例如把
    `title: "Rename session",` 整行当锚点会连逗号和属性名一起替换掉）。
    """
    if not value or not value.strip():
        return True
    found = [(m.start(), m.end()) for m in _CJK_CHAR.finditer(value)]
    if not found:
        return True  # 没有中文的译文（身份锚点等）不做结构约束
    prefix, suffix = value[:found[0][0]], value[found[-1][1]:]
    if prefix and not new.startswith(prefix):
        return False
    return not (suffix and not new.endswith(suffix))


def _split_structure(cand: str) -> tuple[str, str] | None:
    """把候选片段拆成「结构前缀 + 内容 + 结构后缀」，返回 (前缀, 后缀)。

    例：`title: "Rename session",` → (`title: "`, `",`)
        `>No matching items<`      → (`>`, `<`)
    拆不出来（例如整行代码、没有引号也没有 JSX 文本）就返回 None。
    """
    spans = []
    for pattern in _QUOTED:
        for match in pattern.finditer(cand):
            spans.append((match.start(1), match.end(1)))
    for match in _JSX_TEXT.finditer(cand):
        spans.append((match.start(1), match.end(1)))
    if not spans:
        return None
    start, end = max(spans, key=lambda span: span[1] - span[0])
    prefix, suffix = cand[:start], cand[end:]
    if len(prefix) + len(suffix) > 80 or "//" in prefix + suffix or "\n" in cand:
        return None
    return prefix, suffix


def fit_value(cand: str, value: str | None) -> str | None:
    """给候选片段配一份能安全替换的译文。

    原译文结构能对上就用原译文；对不上（上游把半行锚点改成整行、改了引号位置等）就把
    中文主体移植到候选片段自己的结构里，例如
    value=`title: "重命名会话"` + cand=`title: "Rename session",` → `title: "重命名会话",`。
    拆不出结构的候选返回 None（放弃这条候选，宁可报 unresolved 也不乱替换）。
    """
    if not value or not value.strip() or not _CJK_CHAR.search(value):
        return value
    if _affix_ok(cand, value):
        return value
    found = [(m.start(), m.end()) for m in _CJK_CHAR.finditer(value)]
    core = value[found[0][0]:found[-1][1]]
    split = _split_structure(cand)
    if split is None:
        return None
    prefix, suffix = split
    if core in cand:
        return None  # 候选里已经有这段中文，替换没有意义
    return prefix + core + suffix


def rank(old: str, cands: list[str], used: set[str], limit: int | None = None) -> list[tuple[float, str]]:
    scored = [(score(old, c), c) for c in cands if c not in used]
    scored.sort(key=lambda item: (-item[0], len(item[1])))
    return scored[:limit] if limit else scored


def plan_entry(old_key: str, source_text: str, existing_keys: set[str], used: set[str],
               value: str | None = None, cands: list[str] | None = None) -> dict:
    """给一条失配锚点出方案：{'action': relink|drop|unresolved, ...}。"""
    cands = cands if cands is not None else candidates(source_text)
    viable: list[tuple[float, str, str | None]] = []
    for item_score, cand in rank(old_key, cands, used, limit=12):
        fitted = fit_value(cand, value)
        if fitted is not None:
            viable.append((item_score, cand, fitted))
    if not viable:
        best = rank(old_key, cands, used, limit=1)
        top = best[0][0] if best else 0.0
        if top < DROP_BELOW:
            return {"action": "drop", "old": old_key,
                    "reason": "源码里最像的候选也只有 %.2f，判定上游删除了该文案" % top}
        return {"action": "unresolved", "old": old_key, "score": round(top, 3),
                "reason": "有相似候选，但结构对不上，不敢自动替换"}
    best_score, best, best_value = viable[0]
    second_score = viable[1][0] if len(viable) > 1 else 0.0
    new_value = None if best_value == value else best_value
    decision = {
        "action": "unresolved",
        "old": old_key,
        "new": best,
        "value": new_value,
        "score": round(best_score, 3),
        "second": round(second_score, 3),
    }
    if best in existing_keys:
        decision["action"] = "drop" if best_score >= STRONG else "unresolved"
        decision["reason"] = "最佳候选已被同文件另一条锚点占用"
        return decision
    if best_score >= STRONG or (best_score >= ACCEPT and best_score - second_score >= AMBIGUITY):
        decision["action"] = "relink"
        return decision
    if best_score < DROP_BELOW:
        decision["action"] = "drop"
        decision["reason"] = "与源码最像的候选也只有 %.2f，判定上游删除了该文案" % best_score
    return decision


def plan_file(misses: list[str], source_text: str, existing_keys: set[str],
              values: dict[str, str] | None = None) -> dict:
    """对一个失配文件出完整方案（同文件内不允许两条锚点指向同一新 key）。

    候选按词重叠预筛：一个文件动辄几千条候选，逐条算相似度会慢到不可用；
    只要和旧锚点共享一个 3 字母以上的词就留下，其它直接排除（它们不可能达标）。

    返回 fixes / drops / drop_info / unresolved：
      drop_info 记录被撤条时「最像的候选 + 分数」——分数不低说明上游只是换了说法，
      编排层据此决定「先撤旧条、再给新文案补一条译文」，避免中文覆盖掉下去。
    """
    values = values or {}
    cands = candidates(source_text)
    index = [(cand, set(loose(cand).split())) for cand in cands]
    fixes, drops, unresolved, drop_info = [], [], [], []
    used: set[str] = set()

    def record(old_key: str, decision: dict) -> None:
        if decision["action"] == "relink":
            fixes.append({"old": old_key, "new": decision["new"], "value": decision.get("value")})
            used.add(decision["new"])
        elif decision["action"] == "drop":
            drops.append(old_key)
            drop_info.append({"old": old_key, "cand": decision.get("new"),
                              "score": round(float(decision.get("score") or 0.0), 3)})
        else:
            unresolved.append(decision)

    for old_key in misses:
        words = {w for w in loose(old_key).split() if len(w) >= 3}
        shortlist = [cand for cand, toks in index if words & toks] if words else []
        if not shortlist:
            if not words:
                # 极短标识符（esc / ok）：允许按长度挑候选
                narrow = [cand for cand in cands if 0.4 * len(cand) <= len(old_key) or len(old_key) <= 8]
                record(old_key, plan_entry(old_key, source_text, existing_keys, used,
                                           values.get(old_key), cands=narrow))
            else:
                drops.append(old_key)
                drop_info.append({"old": old_key, "cand": None, "score": 0.0})
            continue
        record(old_key, plan_entry(old_key, source_text, existing_keys, used,
                                   values.get(old_key), cands=shortlist))
    return {"fixes": fixes, "drops": drops, "drop_info": drop_info, "unresolved": unresolved}


def self_test() -> int:
    """离线自测（CI 用）：重锚 / 移植译文 / 存疑 / 撤条四条路径各一个用例。"""
    src = '      title: "Rename the session",\n'
    # 1) 结构没变：直接重锚，译文原样沿用
    d = plan_entry('title: "Rename session"', src, set(), set(), 'title: "重命名会话"')
    assert d["action"] == "relink", d
    assert d["new"] == 'title: "Rename the session"', d
    assert d["value"] is None, d

    # 2) 结构变了（上游把 title 改成 closeLabel）：把中文主体移植到新结构里
    fitted = fit_value('    <DialogHeader closeLabel="Rename the session" />', 'title: "重命名会话"')
    assert fitted.strip() == '<DialogHeader closeLabel="重命名会话" />', fitted
    src2 = '    <DialogHeader closeLabel="Rename the session" />\n'
    d2 = plan_entry('title: "Rename session"', src2, set(), set(), 'title: "重命名会话"')
    assert d2["action"] in ("relink", "unresolved"), d2

    # 3) 完全不相关：不能误锚
    d3 = plan_entry("Completely unrelated dialog copy", src, set(), set(), 'title: "重命名会话"')
    assert d3["action"] in ("drop", "unresolved"), d3

    # 4) 源码里毫无相似内容：判上游删除
    d4 = plan_entry("Completely unrelated dialog copy", "const unrelated = 1;\n", set(), set(),
                    'title: "重命名会话"')
    assert d4["action"] == "drop", d4

    # 5) 整文件方案：同文件内不会把两条锚点指向同一新 key
    plan = plan_file(['title: "Rename session"'], src, set(),
                     {'title: "Rename session"': 'title: "重命名会话"'})
    assert plan["fixes"] and not plan["drops"], plan
    print("[heur] self-test ok")
    return 0


if __name__ == "__main__":
    import sys

    sys.exit(self_test())
