#!/usr/bin/env python3
"""在线修复汉化词表失配：确定性门禁判定，LLM 只负责出补丁。

工作流用法（V1/V2 两条线通用，资产目录按上游布局自动探测）::

    python3 scripts/autotranslate.py --source build/upstream --cli ./dist/opencode-cli

退出码：0 = 门禁通过（可能没改任何文件）；1 = 修不动（保持原来的失败行为）。

设计约束：
- 失配判定完全复刻 cli-go 的口径（key 作为子串是否还在目标源码里），不猜；
- 每个文件一个补丁，逐条校验「新锚点必须真的出现在源码里」，否则丢弃该条；
- 每轮改完立刻用真实门禁复核，某文件改坏了就回滚该文件；
- 不联网就什么都不做（未配置 API 密钥时直接退出 0，交给原来的门禁报错）。
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

V1_ASSETS, V2_ASSETS = "opencode-i18n", "opencode-i18n-v2"
MAX_SOURCE_CHARS = 120_000
SYSTEM_PROMPT = """你是 OpenCode TUI 简体中文汉化词表的维护器。上游重构后旧锚点会失配：
词表的 key 是「上游源码里的原文字面量片段」，必须逐字节出现在目标源码文件里；value 是中文译文。

任务：给你一个目标源码文件的全文、该文件现有词表（可能部分已失配）、以及失配的 key 清单，
输出一份 JSON 补丁。规则：

1. 每条失配 key，先在源码里找到它对应的**新写法**（同一文案改结构/改缩进后的字面量片段），
   把 key 换成新写法；value 一般沿用原译文，但若新写法的结构变了（例如 JSX 文本节点改成了
   props 的 { title: ..., key: ... }），value 也要按新结构重写，保证替换后是合法代码。
2. 找不到对应写法的（上游删了这处文案）放进 drops。
3. 源码里出现、但词表还没有的**用户可见英文文案**，可以放进 adds（只收明显的界面文案，
   不要收变量名、日志、类型名、注释）。
4. new / key 必须是源码里逐字节存在的子串（缩进、换行、引号都要一致），否则整条作废。
5. 只输出 JSON，不要解释，不要 markdown 代码块。

JSON 结构：
{"fixes": [{"old": "<失配的旧 key>", "new": "<源码里的新字面量>", "value": "<新译文，可省略=沿用原译文>"}],
 "drops": ["<上游已删除的旧 key>"],
 "adds": [{"key": "<源码里的新文案字面量>", "value": "<中文译文>"}],
 "notes": "<一句话说明这次改了什么>"}
"""


def log(msg: str) -> None:
    print(f"[autotranslate] {msg}", flush=True)


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
    text = path.read_text(encoding="utf-8", errors="replace")
    return text[:MAX_SOURCE_CHARS]


def compute_misses(configs: list[dict], source: Path) -> list[dict]:
    """返回需要修的文件：{config, text, missing:[key...]}（整文件 0 命中也算）。"""
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
    import subprocess
    env = dict(os.environ, OPENCODE_SOURCE_DIR=str(source))
    proc = subprocess.run([cli, "apply", "--dry-run", "--strict", "--min-match-rate", "1"],
                          cwd=repo, env=env, capture_output=True, text=True)
    return parse_gate(proc.stdout + proc.stderr)


def call_llm(base_url: str, api_key: str, model: str, user: str, timeout: int) -> str:
    body = {"model": model, "temperature": 0,
            "messages": [{"role": "system", "content": SYSTEM_PROMPT},
                         {"role": "user", "content": user}]}
    req = urllib.request.Request(
        base_url.rstrip("/") + "/chat/completions",
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"},
        method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        payload = json.loads(resp.read().decode("utf-8"))
    return payload["choices"][0]["message"]["content"]


def parse_patch(reply: str) -> dict:
    text = reply.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1] if "\n" in text else text
        text = text.rsplit("```", 1)[0]
    start, end = text.find("{"), text.rfind("}")
    if start < 0 or end <= start:
        raise ValueError("回复里没有 JSON")
    return json.loads(text[start:end + 1])


def build_user_prompt(entry: dict) -> str:
    cfg, text, missing = entry["cfg"], entry["text"], entry["missing"]
    rules = json.dumps(cfg["data"]["replacements"], ensure_ascii=False, indent=2)
    return (f"目标文件：{cfg['file']}\n"
            f"该文件是身份锚点（--keep，原文→原文，value 必须等于 key，不要翻译）：{cfg['identity']}\n\n"
            f"== 现有词表（{len(cfg['data']['replacements'])} 条，其中 {len(missing)} 条已失配）==\n{rules}\n\n"
            f"== 失配的 key（{len(missing)} 条）==\n"
            + "\n".join(f"- {json.dumps(k, ensure_ascii=False)}" for k in missing)
            + f"\n\n== 目标文件全文 ==\n{text}\n")


def looks_like_ui_text(key: str) -> bool:
    """只收「看着像界面文案」的字面量：够长、带空格或标点、不是裸标识符。"""
    if len(key.strip().strip("\"'`")) < 6:
        return False
    if key.strip().isidentifier():
        return False
    return any(ch in key for ch in " \t:?!.,()[]-—…" )


def apply_patch(entry: dict, patch: dict, max_adds: int = 15) -> tuple[dict, list[str]]:
    """把 LLM 补丁落到该文件的词表上，返回 (新词表, 说明)。逐条校验锚点真实性。"""
    cfg, text, missing = entry["cfg"], entry["text"], set(entry["missing"])
    rules = dict(cfg["data"]["replacements"])
    notes = []
    for fix in patch.get("fixes") or []:
        old, new = fix.get("old"), fix.get("new")
        if old not in missing or not isinstance(new, str) or new not in text:
            notes.append(f"丢弃 fix {old!r} -> {new!r}（旧 key 不在失配集或新锚点不在源码里）")
            continue
        value = fix.get("value") if isinstance(fix.get("value"), str) and fix["value"] else rules[old]
        rules.pop(old, None)
        rules[new] = new if cfg["identity"] else value
        notes.append(f"重锚 {old!r} -> {new!r}")
    for old in patch.get("drops") or []:
        if old in missing:
            rules.pop(old, None)
            notes.append(f"撤条 {old!r}")
    added = 0
    for add in patch.get("adds") or []:
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
    return rules, notes


def contains_cjk(text: str) -> bool:
    return any("\u4e00" <= ch <= "\u9fff" for ch in text)


def write_config(cfg: dict, rules: dict) -> None:
    cfg["data"]["replacements"] = rules
    cfg["path"].write_text(json.dumps(cfg["data"], ensure_ascii=False, indent=2) + "\n",
                           encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=".")
    ap.add_argument("--source", required=True, help="上游源码目录")
    ap.add_argument("--cli", required=True, help="opencode-cli 可执行文件")
    ap.add_argument("--max-rounds", type=int, default=3)
    ap.add_argument("--max-files", type=int, default=6, help="每轮最多处理几个文件")
    ap.add_argument("--timeout", type=int, default=180)
    args = ap.parse_args()

    api_key = os.environ.get("AUTOTRANSLATE_API_KEY", "").strip()
    base_url = os.environ.get("AUTOTRANSLATE_BASE_URL", "https://api.deepseek.com").strip()
    model = os.environ.get("AUTOTRANSLATE_MODEL", "deepseek-chat").strip()
    repo, source = Path(args.repo).resolve(), Path(args.source).resolve()

    ok, summary = run_gate(args.cli, source, repo)
    log(f"当前门禁：{summary or '（无输出）'} -> {'通过' if ok else '未通过'}")
    if ok:
        return 0
    if not api_key:
        log("未配置 AUTOTRANSLATE_API_KEY，跳过在线修复（门禁照原样报错）")
        return 1

    base = asset_dir(repo, source)
    log(f"词表目录：{base}")
    touched: set[Path] = set()

    for round_no in range(1, args.max_rounds + 1):
        configs = load_configs(base)
        pending = compute_misses(configs, source)
        if not pending:
            log(f"第 {round_no} 轮：词表已全部命中，交给门禁复核")
            break
        pending.sort(key=lambda e: -len(e["missing"]))
        log(f"第 {round_no} 轮：{len(pending)} 个文件失配，本轮处理 {min(len(pending), args.max_files)} 个")
        for entry in pending[:args.max_files]:
            cfg = entry["cfg"]
            before = cfg["path"].read_text(encoding="utf-8")
            try:
                reply = call_llm(base_url, api_key, model, build_user_prompt(entry), args.timeout)
                patch = parse_patch(reply)
            except (urllib.error.URLError, TimeoutError, ValueError, KeyError) as exc:
                log(f"  {cfg['file']}: LLM 调用/解析失败（{exc}），跳过")
                continue
            rules, notes = apply_patch(entry, patch)
            if not notes:
                log(f"  {cfg['file']}: 补丁为空，跳过")
                continue
            write_config(cfg, rules)
            touched.add(cfg["path"])
            log(f"  {cfg['file']}: {'; '.join(notes[:6])}"
                + (" …" if len(notes) > 6 else ""))
            ok, summary = run_gate(args.cli, source, repo)
            still = compute_misses([{**cfg, "data": cfg["data"]}], source)
            if still and len(still[0]["missing"]) >= len(entry["missing"]):
                cfg["path"].write_text(before, encoding="utf-8")
                touched.discard(cfg["path"])
                log(f"  {cfg['file']}: 没修好（{len(entry['missing'])} -> "
                    f"{len(still[0]['missing'])}），回滚该文件")
            else:
                log(f"  {cfg['file']}: 失配 {len(entry['missing'])} -> "
                    f"{len(still[0]['missing']) if still else 0}")
        if run_gate(args.cli, source, repo)[0]:
            break

    ok, summary = run_gate(args.cli, source, repo)
    log(f"结束：{summary or '（无输出）'} -> {'通过' if ok else '未通过'}；改动文件 {len(touched)} 个")
    for path in sorted(touched):
        print(f"CHANGED {path}", flush=True)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
