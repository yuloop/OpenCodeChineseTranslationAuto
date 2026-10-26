#!/usr/bin/env python3
"""一条发布线的在线自愈：门禁判定 → 自动修复 → 真实 apply → 语法校验。

被 .github/workflows/opencode-cn-autoheal.yml 调用（V1 / V2 各一次）::

    python3 scripts/autoheal_line.py --line v1 --source build/upstream-v1 --cli ./dist/opencode-cli

输出（写到 stdout，末尾是关键值，workflow 直接啃）：
    OK <true|false>         门禁最终是否 100%
    HEALED <true|false>     本轮是否真的改动了词表
    SYNTAX <ok|failed|skipped|n/a>
    ISSUE_TAIL <一句话原因>  （仅在失败时）

退出码：0 = 门禁全绿；1 = 仍未全绿（需要人工看一眼，workflow 会开 Issue）。
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

import i18n_assets as A


def log(msg: str) -> None:
    print(f"[autoheal] {msg}", flush=True)


def gate(cli: str, source: Path, repo: Path) -> tuple[bool, str]:
    return A.run_gate(cli, source, repo)


def apply_for_real(cli: str, source: Path, repo: Path) -> bool:
    env = dict(os.environ, OPENCODE_SOURCE_DIR=str(source))
    proc = subprocess.run([cli, "apply", "--strict", "--min-match-rate", "1"],
                          cwd=repo, env=env, capture_output=True, text=True)
    ok = proc.returncode == 0 and "汉化质量门禁未通过" not in (proc.stdout + proc.stderr)
    log(f"真实 apply -> {'成功' if ok else '失败'}")
    return ok


def restore_source(source: Path) -> None:
    """apply 会把中文真的写进上游源码树；校验完恢复原样，避免污染后续本地复跑。"""
    subprocess.run(["git", "-C", str(source), "checkout", "--", "."], check=False)


def syntax_check(source: Path, repo: Path) -> str:
    """把词表真实落到源码后，用 bun 的 TSX 转译器校验被改动的文件。

    门禁只算子串命中，不校验语法：重锚选错片段可能让门禁 100% 而代码坏掉，
    所以提交前补这一道。环境没有 bun 时返回 skipped（不阻塞，但会在日志里留痕）。
    """
    script = repo / "scripts" / "check_applied_syntax.mjs"
    if not script.exists():
        return "skipped"
    proc = subprocess.run(["bash", "-lc", f'bun "{script}" "{source}"'],
                          capture_output=True, text=True)
    sys.stdout.write(proc.stdout)
    sys.stderr.write(proc.stderr)
    return "ok" if proc.returncode == 0 else "failed"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--line", required=True, choices=["v1", "v2"])
    ap.add_argument("--repo", default=".")
    ap.add_argument("--source", required=True)
    ap.add_argument("--cli", required=True)
    ap.add_argument("--max-files", type=int, default=4)
    ap.add_argument("--no-adds", action="store_true", help="关闭免费补译（默认开启）")
    ap.add_argument("--no-syntax", action="store_true", help="跳过语法校验（本地调试用）")
    args = ap.parse_args()

    repo, source = Path(args.repo).resolve(), Path(args.source).resolve()
    ok, summary = gate(args.cli, source, repo)
    log(f"{args.line.upper()} 当前门禁：{summary or '（无输出）'} -> {'通过' if ok else '未通过'}")
    if ok:
        print("OK true\nHEALED false\nSYNTAX n/a", flush=True)
        return 0

    log(f"{args.line.upper()} 门禁未通过，开始自动修复")
    cmd = [sys.executable, str(repo / "scripts" / "autotranslate.py"),
           "--repo", str(repo), "--source", str(source), "--cli", args.cli,
           "--max-files", str(args.max_files)]
    if args.no_adds:
        cmd.append("--no-adds")
    subprocess.run(cmd, cwd=repo, check=False)

    ok, summary = gate(args.cli, source, repo)
    log(f"{args.line.upper()} 修复后门禁：{summary or '（无输出）'} -> {'通过' if ok else '未通过'}")
    healed = subprocess.run(["git", "-C", str(repo), "diff", "--quiet", "--",
                             "cli-go/internal/core"], capture_output=True).returncode != 0
    if not ok:
        print(f"OK false\nHEALED {'true' if healed else 'false'}\nSYNTAX n/a", flush=True)
        print(f"ISSUE_TAIL {args.line.upper()} 修复后仍未达到 100%（剩余失配需人工处理）", flush=True)
        return 1

    syntax = "n/a"
    if healed and not args.no_syntax:
        if not apply_for_real(args.cli, source, repo):
            syntax = "failed"
        else:
            syntax = syntax_check(source, repo)
        restore_source(source)
        if syntax == "failed":
            # 语法坏掉的词表绝不能提交：本地回滚，保持 main 的词表原样（门禁会继续红）
            subprocess.run(["git", "-C", str(repo), "checkout", "--", "cli-go/internal/core"], check=False)
            log("语法校验失败，已回滚本轮词表改动（不提交）")
            print(f"OK false\nHEALED false\nSYNTAX failed", flush=True)
            print(f"ISSUE_TAIL {args.line.upper()} 修复后源码语法校验不通过（词表未被提交）", flush=True)
            return 1
    print(f"OK true\nHEALED {'true' if healed else 'false'}\nSYNTAX {syntax}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
