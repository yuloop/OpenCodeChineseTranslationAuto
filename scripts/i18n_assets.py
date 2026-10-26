#!/usr/bin/env python3
"""汉化词表的读写与账目同步（供 autotranslate.py 使用）。

包含：资产目录探测（复刻 cli-go 的 detectLayout）、词表加载、失配计算（复刻门禁口径）、
真实门禁调用、补丁落盘，以及两处「账目」同步——
  * cli-go/internal/core/i18n_v2_test.go 里 V1 的冻结值（规则文件数 / 条目数）
  * V2 config.json 的 manifest 覆盖台账（V1 每条都要在里面有对应）
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

V1_ASSETS, V2_ASSETS = "opencode-i18n", "opencode-i18n-v2"
MAX_SOURCE_CHARS = 120_000


def log(msg: str) -> None:
    print(f"[assets] {msg}", flush=True)


def asset_dir(repo: Path, source: Path) -> Path:
    """复刻 cli-go/internal/core/build.go 的 detectLayout：V1 优先（有 packages/opencode），
    否则看 packages/cli/script/build.ts 里有没有 `--target=` 才认 V2，都不满足按 V1。"""
    assets = repo / "cli-go" / "internal" / "core" / "assets"
    if (source / "packages" / "opencode").exists():
        return assets / V1_ASSETS
    v2_build = source / "packages" / "cli" / "script" / "build.ts"
    if v2_build.is_file() and "--target=" in v2_build.read_text(encoding="utf-8", errors="replace"):
        return assets / V2_ASSETS
    return assets / V1_ASSETS


def load_configs(base: Path) -> list[dict]:
    configs = []
    for path in sorted(base.rglob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        target = data.get("file")
        if not target or not isinstance(data.get("replacements"), dict):
            continue
        configs.append({"path": path, "file": target, "data": data,
                        "identity": "--keep" in path.name})
    return configs


def file_text(source: Path, target: str) -> str | None:
    path = source / target
    if not path.is_file():
        return None
    return path.read_text(encoding="utf-8", errors="replace")[:MAX_SOURCE_CHARS]


def compute_misses(configs: list[dict], source: Path) -> list[dict]:
    """返回需要修的文件：{cfg, text, missing:[key...]}（整文件 0 命中也算）。"""
    out = []
    for cfg in configs:
        text = file_text(source, cfg["file"])
        if text is None:
            continue  # 目标文件不存在 → cli 记为 skipped，不算失败
        missing = [k for k in cfg["data"]["replacements"] if k not in text]
        if missing:
            out.append({"cfg": cfg, "text": text, "missing": missing})
    return out


def parse_gate(output: str) -> tuple[bool, str]:
    ok = "汉化质量门禁未通过" not in output
    summary = " / ".join(line.strip() for line in output.splitlines()
                         if "替换:" in line or "文件:" in line)
    return ok, summary


def run_gate(cli: str, source: Path, repo: Path) -> tuple[bool, str]:
    env = dict(os.environ, OPENCODE_SOURCE_DIR=str(source))
    proc = subprocess.run([cli, "apply", "--dry-run", "--strict", "--min-match-rate", "1"],
                          cwd=repo, env=env, capture_output=True, text=True)
    return parse_gate(proc.stdout + proc.stderr)


def contains_cjk(text: str) -> bool:
    return any("\u4e00" <= ch <= "\u9fff" for ch in text)


_CODE_START = re.compile(
    r"^(import|export|const|let|var|function|return|await|async|if|for|while|switch|case|"
    r"new|throw|console|require|type|interface|class|enum|declare|module|package|assert|"
    r"describe|test|expect|it)\b")
_PATHISH = re.compile(
    r"(^(node:|@|\./|\.\./|/|\w+://)|://|\.(tsx?|mjs|cjs|jsx?|json|css|scss|md|svg|png|ttf|woff2?|"
    r"lock|yml|yaml)$|[\\/][\w.-]+[\\/])")


def looks_like_ui_text(text: str) -> bool:
    """只收「看着像界面文案」的字面量：够长、带空格、不含代码符号、不是裸标识符/导入/路径。"""
    body = text.strip().strip("\"'`")
    if not (6 <= len(body) <= 120) or body.isidentifier():
        return False
    if not re.search(r"[A-Za-z]{2,}\s+[A-Za-z]", body):
        return False
    if re.search(r"[{}$=<>()[\]\\;|&]", body):
        return False
    if _CODE_START.match(body) or _PATHISH.search(body):
        return False
    # 没有小写字母的串多半是常量名/环境变量名
    return bool(re.search(r"[a-z]{2,}", body))


def apply_patch(entry: dict, patch: dict, max_adds: int = 0) -> tuple[dict, list[str], list[tuple[str, str]]]:
    """把补丁落到该文件的词表上，返回 (新词表, 说明, 重锚对)。逐条校验锚点真实性。"""
    cfg, text, missing = entry["cfg"], entry["text"], set(entry["missing"])
    rules = dict(cfg["data"]["replacements"])
    notes: list[str] = []
    renames: list[tuple[str, str]] = []
    for fix in patch.get("fixes") or []:
        old, new = fix.get("old"), fix.get("new")
        if old not in missing or not isinstance(new, str) or new not in text:
            notes.append(f"丢弃 fix {old!r} -> {new!r}（旧 key 不在失配集或新锚点不在源码里）")
            continue
        value = fix.get("value") if isinstance(fix.get("value"), str) and fix["value"] else rules[old]
        rules.pop(old, None)
        rules[new] = new if cfg["identity"] else value
        renames.append((old, new))
        notes.append(f"重锚 {old!r} -> {new!r}")
    for old in patch.get("drops") or []:
        if old in missing:
            rules.pop(old, None)
            notes.append(f"撤条 {old!r}")
    added = 0
    adds = patch.get("adds") or []
    if adds and max_adds <= 0:
        notes.append(f"未启用补译，忽略 {len(adds)} 条新增")
    elif adds:
        for add in adds:
            if added >= max_adds:
                notes.append(f"补译超过上限 {max_adds}，其余忽略")
                break
            key, value = add.get("key"), add.get("value")
            if cfg["identity"] or not isinstance(key, str) or key not in text or key in rules:
                notes.append(f"丢弃 add {key!r}（身份锚点/不在源码里/已存在）")
                continue
            if not looks_like_ui_text(key) or not isinstance(value, str) or not contains_cjk(value):
                notes.append(f"丢弃 add {key!r}（不像界面文案或译文不含中文）")
                continue
            rules[key] = value
            added += 1
            notes.append(f"补译 {key!r}")
    return rules, notes, renames


def write_config(cfg: dict, rules: dict) -> None:
    cfg["data"]["replacements"] = rules
    cfg["path"].write_text(json.dumps(cfg["data"], ensure_ascii=False, indent=2) + "\n",
                           encoding="utf-8")


def sync_v1_freeze(repo: Path, configs: list[dict]) -> Path | None:
    """V1 词表的（规则文件数, 条目数）变了就同步测试里的冻结值。

    TestEmbeddedV1AssetsUnchanged 把这两个数字写死了（56 / 501），自动修复只要增删条目
    就会让这个测试红；这里按实际词表改写函数体里的数字，保证 bot 提交不会打破 CI。
    """
    rules_count = len(configs)
    total = sum(len(c["data"]["replacements"]) for c in configs)
    path = repo / "cli-go" / "internal" / "core" / "i18n_v2_test.go"
    if not path.exists():
        return None
    text = path.read_text(encoding="utf-8")
    start = text.find("func TestEmbeddedV1AssetsUnchanged")
    if start < 0:
        return None
    end = text.find("\nfunc ", start + len("func TestEmbeddedV1AssetsUnchanged"))
    body = text[start:end] if end > 0 else text[start:]
    patched = re.sub(r"(if len\(configs\) != )\d+", rf"\g<1>{rules_count}", body, count=1)
    patched = re.sub(r"(if total != )\d+", rf"\g<1>{total}", patched, count=1)
    patched = re.sub(r"(V1 规则文件数应保持 )\d+", rf"\g<1>{rules_count}", patched, count=1)
    patched = re.sub(r"(V1 翻译条目数应保持 )\d+", rf"\g<1>{total}", patched, count=1)
    if patched == body:
        return None
    path.write_text(text[:start] + patched + (text[end:] if end > 0 else ""), encoding="utf-8")
    log(f"同步冻结值：V1 规则文件 {rules_count} 个、条目 {total} 条 -> {path.name}")
    return path


def sync_v2_manifest(repo: Path, renames_by_rule: dict[str, list[tuple[str, str]]],
                     added_by_rule: dict[str, list[tuple[str, str, str]]] | None = None) -> Path | None:
    """把 V1 的重锚/新增同步进 V2 config.json 的 manifest 覆盖台账。

    TestEmbeddedV2AssetsCoverEveryV1Entry 要求「V1 的每条 (规则, 原文) 在 V2 manifest 里都有
    台账」，V1 换 key 或新增条目都会红。manifest 只是覆盖台账（apply 用 anchors/*.json），
    所以只改台账、不动 V2 锚点，V2 门禁口径完全不变。
    """
    added_by_rule = added_by_rule or {}
    if not renames_by_rule and not added_by_rule:
        return None
    path = repo / "cli-go" / "internal" / "core" / "assets" / V2_ASSETS / "config.json"
    if not path.exists():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    manifest = data.setdefault("manifest", {})
    entries = manifest.setdefault("entries", [])
    updated, appended, unmatched = 0, 0, []
    for rule, renames in sorted(renames_by_rule.items()):
        for old, new in renames:
            hit = [e for e in entries if e.get("rule") == rule and e.get("key") == old]
            if not hit:
                unmatched.append(f"{rule} / {old!r}")
                continue
            for e in hit:
                e["key"] = new
            updated += len(hit)
    for rule, adds in sorted(added_by_rule.items()):
        for key, target, engine in adds:
            if any(e.get("rule") == rule and e.get("key") == key for e in entries):
                continue
            entries.append({"rule": rule, "key": key, "status": "kept",
                            "from": target, "to": target, "basis": f"auto-added-{engine}"})
            appended += 1
    if unmatched:
        log(f"V2 manifest 里没有这些 V1 条目的台账（{len(unmatched)} 条），覆盖测试会红："
            f"{'; '.join(unmatched[:3])}")
    if not updated and not appended:
        return None
    manifest.setdefault("totals", {})
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    log(f"同步 V2 manifest 台账：改键 {updated} 条、新增台账 {appended} 条")
    return path


if __name__ == "__main__":
    print(json.dumps({"assets": [V1_ASSETS, V2_ASSETS]}, ensure_ascii=False))
    sys.exit(0)
