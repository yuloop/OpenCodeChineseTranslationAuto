#!/usr/bin/env python3
"""V2 spike 探针：量化 V1 汉化规则在上游 V2 源码上的锚点失效情况。

用法：
    python3 tools/v2spike_probe.py --source-dir <上游检出目录> [--json-out <路径>]

说明：
- 只读仓库内 assets 与 --source-dir，不修改任何仓库文件。
- V1 路径映射复刻 cli-go/internal/core/i18n.go；另按「TUI 合回
  packages/opencode/src/cli/cmd/tui/」猜一组 V2 候选路径（对应上游 2.0 探索分支布局）。
- 对每个上游检出目录，再用 packages/ 全树索引判断失效锚点的字符串是否只是换了位置
  （matched_elsewhere），以适配不同的 V2 包布局（如 v2.0.x 发布线的 packages/cli）。
- 匹配逻辑复刻 i18n.go：简单单词（^[a-zA-Z0-9]+$）按 \b 边界，其余按子串。
- 退出码：0=完成；2=预期内失败（参数/目录缺失）；未预期异常= traceback + 非 0。
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import tempfile
from pathlib import Path

# 有界集合上限，防止异常大的源码树导致内存/耗时失控
MAX_INDEX_BYTES = 200 * 1024 * 1024
MAX_FILE_BYTES = 4 * 1024 * 1024
MAX_DETAIL_FILES = 200
MAX_SAMPLES_PER_FILE = 3
SEARCH_EXTS = {".ts", ".tsx", ".js", ".jsx", ".txt", ".md"}

EXIT_OK = 0
EXIT_EXPECTED = 2


class ExpectedError(Exception):
    """预期内失败：打印到 stderr 并按约定退出码退出。"""


def repo_root() -> Path:
    # 路径从脚本自身位置推导：tools/v2spike_probe.py -> 仓库根
    return Path(__file__).resolve().parent.parent


def default_assets_dir() -> Path:
    return repo_root() / "cli-go" / "internal" / "core" / "assets" / "opencode-i18n"


def load_rules(assets_dir: Path) -> list[dict]:
    if not assets_dir.is_dir():
        raise ExpectedError(f"assets 目录不存在: {assets_dir}")
    rules: list[dict] = []
    for path in sorted(assets_dir.rglob("*.json")):
        if path.name == "config.json":
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as err:
            raise ExpectedError(f"解析规则文件失败 {path}: {err}") from err
        rules.append(
            {
                "rule": path.relative_to(assets_dir).as_posix(),
                "file": data.get("file", ""),
                "replacements": data.get("replacements", {}) or {},
            }
        )
    if not rules:
        raise ExpectedError(f"assets 目录下没有规则文件: {assets_dir}")
    return rules


def v1_target(source_dir: Path, rel: str) -> Path | None:
    # 复刻 i18n.go GetTargetFilePath
    if not rel:
        return None
    if rel.startswith("packages/"):
        return source_dir / rel
    if rel.startswith("src/cli/cmd/tui/"):
        rest = rel[len("src/cli/cmd/tui/") :]
        return source_dir / "packages" / "tui" / "src" / rest
    return source_dir / "packages" / "opencode" / rel


def v2_candidates(source_dir: Path, rel: str) -> list[Path]:
    # V2 候选路径：TUI 合回 packages/opencode/src/cli/cmd/tui/
    if not rel:
        return []
    if rel.startswith("packages/tui/src/"):
        rest = rel[len("packages/tui/src/") :]
        return [source_dir / "packages" / "opencode" / "src" / "cli" / "cmd" / "tui" / rest]
    if rel.startswith("src/cli/cmd/tui/"):
        return [source_dir / "packages" / "opencode" / rel]
    if rel.startswith("packages/"):
        return [source_dir / rel]
    return [source_dir / "packages" / "opencode" / rel]


def is_simple_word(text: str) -> bool:
    return re.fullmatch(r"[a-zA-Z0-9]+", text) is not None


def matches(content: str, find: str) -> bool:
    # 复刻 i18n.go replacementMatches（含 CRLF 归一化）
    if not find:
        return False
    find = find.replace("\r\n", "\n")
    if is_simple_word(find):
        return re.search(r"\b" + re.escape(find) + r"\b", content) is not None
    return find in content


def build_tree_index(source_dir: Path) -> tuple[str, dict[str, str]]:
    """把上游源码树拼成一个索引，用于判断失效锚点的字符串是否在别处仍存在。

    索引范围覆盖 packages/ 全树（各版本包布局不同：V1 为 packages/opencode+tui，
    V2 发布线为 packages/cli+tui+core 等），跳过 node_modules；体积超限时截断。
    """
    pkg_root = source_dir / "packages"
    if not pkg_root.is_dir():
        raise ExpectedError(f"packages 目录不存在: {pkg_root}")
    chunks: list[str] = []
    per_file: dict[str, str] = {}
    total = 0
    for path in sorted(pkg_root.rglob("*")):
        if not path.is_file() or path.suffix not in SEARCH_EXTS:
            continue
        if any(part == "node_modules" for part in path.parts):
            continue
        try:
            size = path.stat().st_size
        except OSError:
            continue
        if size > MAX_FILE_BYTES:
            continue
        if total + size > MAX_INDEX_BYTES:
            break
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        text = text.replace("\r\n", "\n")
        rel = path.relative_to(source_dir).as_posix()
        per_file[rel] = text
        chunks.append(f"\n/*=={rel}==*/\n{text}")
        total += size
    return "".join(chunks), per_file


def find_elsewhere(key: str, per_file: dict[str, str]) -> list[str]:
    hits = []
    for rel, text in per_file.items():
        if matches(text, key):
            hits.append(rel)
            if len(hits) >= MAX_SAMPLES_PER_FILE:
                break
    return hits


def atomic_write_json(payload: dict, out_path: Path) -> None:
    # 写入原子化：同目录 mkstemp（oc- 前缀，落在调用方指定路径的目录）
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix="oc-v2spike-", suffix=".json", dir=str(out_path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2)
        os.replace(tmp_name, out_path)
    except BaseException:
        try:
            os.unlink(tmp_name)
        except OSError:
            pass
        raise


def main() -> int:
    parser = argparse.ArgumentParser(description="Probe V1 i18n rules against upstream V2 source")
    parser.add_argument("--source-dir", required=True, help="上游 V2 检出目录")
    parser.add_argument("--assets-dir", default=None, help="汉化规则目录（默认仓库内 assets）")
    parser.add_argument("--json-out", default=None, help="可选：原子写入 JSON 报告的路径")
    args = parser.parse_args()

    source_dir = Path(args.source_dir).resolve()
    if not source_dir.is_dir():
        print(f"错误: --source-dir 不是目录: {source_dir}", file=sys.stderr)
        return EXIT_EXPECTED

    assets_dir = Path(args.assets_dir).resolve() if args.assets_dir else default_assets_dir()
    rules = load_rules(assets_dir)
    tree_text, per_file = build_tree_index(source_dir)

    totals = {"rules": len(rules), "replacements": 0, "v1_file_exists": 0, "v2_file_exists": 0, "matched_v2": 0, "matched_elsewhere": 0}
    details = []

    for rule in rules:
        rel = rule["file"]
        replacements = rule["replacements"]
        totals["replacements"] += len(replacements)

        v1_path = v1_target(source_dir, rel)
        v1_exists = bool(v1_path and v1_path.is_file())
        if v1_exists:
            totals["v1_file_exists"] += 1

        v2_paths = v2_candidates(source_dir, rel)
        v2_exists = any(p.is_file() for p in v2_paths)
        if v2_exists:
            totals["v2_file_exists"] += 1

        matched_v2 = 0
        matched_elsewhere = 0
        unmatched_samples = []
        elsewhere_samples = []

        if v2_exists:
            content = "\n".join(p.read_text(encoding="utf-8", errors="replace").replace("\r\n", "\n") for p in v2_paths if p.is_file())
            for key in replacements:
                if matches(content, key):
                    matched_v2 += 1
                else:
                    if len(unmatched_samples) < MAX_SAMPLES_PER_FILE:
                        unmatched_samples.append(key[:80])
                    hits = find_elsewhere(key, per_file)
                    if hits:
                        matched_elsewhere += 1
                        if len(elsewhere_samples) < MAX_SAMPLES_PER_FILE:
                            elsewhere_samples.append({"key": key[:60], "hits": hits})
        else:
            for key in replacements:
                hits = find_elsewhere(key, per_file)
                if hits:
                    matched_elsewhere += 1
                    if len(elsewhere_samples) < MAX_SAMPLES_PER_FILE:
                        elsewhere_samples.append({"key": key[:60], "hits": hits})
                elif len(unmatched_samples) < MAX_SAMPLES_PER_FILE:
                    unmatched_samples.append(key[:80])

        totals["matched_v2"] += matched_v2
        totals["matched_elsewhere"] += matched_elsewhere

        if len(details) < MAX_DETAIL_FILES:
            details.append(
                {
                    "rule": rule["rule"],
                    "file": rel,
                    "total": len(replacements),
                    "v1_target_exists": v1_exists,
                    "v2_candidate_exists": v2_exists,
                    "v2_candidate": [p.relative_to(source_dir).as_posix() for p in v2_paths],
                    "matched_v2": matched_v2,
                    "matched_elsewhere": matched_elsewhere,
                    "unmatched_samples": unmatched_samples,
                    "elsewhere_samples": elsewhere_samples,
                }
            )

    report = {
        "source_dir": str(source_dir),
        "assets_dir": str(assets_dir),
        "totals": totals,
        "details": details,
    }

    print(f"规则文件: {totals['rules']}  翻译条目: {totals['replacements']}")
    print(f"V1 映射目标存在: {totals['v1_file_exists']}/{totals['rules']}")
    print(f"V2 候选路径存在: {totals['v2_file_exists']}/{totals['rules']}")
    print(f"V2 候选路径上可匹配: {totals['matched_v2']}/{totals['replacements']}")
    print(f"锚点字符串在 V2 别处仍存在: {totals['matched_elsewhere']}/{totals['replacements']}")
    print()
    header = f"{'rule':52} {'total':>5} {'v1':>3} {'v2':>3} {'match':>5} {'else':>5}"
    print(header)
    print("-" * len(header))
    for item in details:
        print(
            f"{item['rule']:52} {item['total']:>5} "
            f"{'Y' if item['v1_target_exists'] else '-':>3} "
            f"{'Y' if item['v2_candidate_exists'] else '-':>3} "
            f"{item['matched_v2']:>5} {item['matched_elsewhere']:>5}"
        )

    if args.json_out:
        out_path = Path(args.json_out)
        atomic_write_json(report, out_path)
        print(f"\nJSON 报告已写入: {out_path}")

    return EXIT_OK


if __name__ == "__main__":
    try:
        sys.exit(main())
    except ExpectedError as err:
        print(f"错误: {err}", file=sys.stderr)
        sys.exit(EXIT_EXPECTED)
