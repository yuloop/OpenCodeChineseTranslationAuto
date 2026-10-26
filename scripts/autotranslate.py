#!/usr/bin/env python3
"""在线修复汉化词表失配：确定性引擎默认（免费、免密钥），LLM 仅作可选兜底。

工作流用法（V1/V2 两条线通用，资产目录按上游布局自动探测）::

    python3 scripts/autotranslate.py --source build/upstream --cli ./dist/opencode-cli

退出码：0 = 门禁通过（可能没改任何文件）；1 = 修不动（workflow 据此开 Issue 告警）。

引擎：
  heur（默认）——在「当前上游源码」里用相似度给沙标的旧锚点重新找对应写法，
                 够像就重锚（译文保留）、完全不像就撤条、介于两者之间报 unresolved。
                 不联网、不花钱、结果可复现。
  llm（可选）——配置 AUTOTRANSLATE_API_KEY 后才启用，用作 heur 修不动时的兜底。

翻译（补译新增条目时才用）：scripts/free_translate.py，MyMemory → Lingva → Google gtx
→ LibreTranslate 公共实例，全部免密钥。
"""

from __future__ import annotations

import argparse
import os
import sys
import urllib.error
from pathlib import Path

import free_translate
import i18n_assets as A
import i18n_heur as H
import i18n_llm

MAX_ADDS_PER_FILE = 8
MAX_ADDS_TOTAL = 24  # 一轮里最多补译这么多条，控住免费接口调用量


def log(msg: str) -> None:
    print(f"[autotranslate] {msg}", flush=True)


def collect_adds(entry: dict, taken: set[str], limit: int) -> tuple[list[dict], list[tuple[str, str, str]]]:
    """找「源码里像界面文案、词表还没收」的字符串，用免费引擎翻译成中文。"""
    cfg, text = entry["cfg"], entry["text"]
    if cfg["identity"] or limit <= 0:
        return [], []
    rules = cfg["data"]["replacements"]
    adds: list[dict] = []
    meta: list[tuple[str, str, str]] = []
    for cand in H.ui_candidates(text):
        if len(adds) >= limit:
            break
        if cand in rules or cand in taken or not A.looks_like_ui_text(cand):
            continue
        # 已被现有锚点覆盖（某条旧 key 是它的长公共子串）就跳过，避免重复收文案
        if any(k in cand or cand in k for k in rules):
            continue
        try:
            value, engine = free_translate.translate(cand)
        except RuntimeError as exc:
            log(f"  {cfg['file']}: 翻译失败（{exc}），本轮不再补译")
            break
        if not A.contains_cjk(value):
            continue
        adds.append({"key": cand, "value": value})
        meta.append((cand, cfg["file"], engine))
        taken.add(cand)
        log(f"  {cfg['file']}: 补译 {cand!r} -> {value!r}（{engine}）")
    return adds, meta


def heur_patch(entry: dict, taken: set[str], max_adds: int) -> tuple[dict, list[str], list[dict]]:
    """确定性方案：能重锚就重锚；重锚不了的旧条，只要新文案已被免费引擎补译就撤掉旧条。

    这样「上游把整句重写了」也能自愈：旧条目撤掉，新文案由补译顶上，门禁回到 100%，
    中文覆盖率不下降。补译失败时才算 unresolved（留给 Issue 告警 + 人工）。
    """
    cfg, text, missing = entry["cfg"], entry["text"], entry["missing"]
    plan = H.plan_file(missing, text, set(cfg["data"]["replacements"]), cfg["data"]["replacements"])
    # 只有真的需要给「新文案」补译文时才调免费接口：
    # ① 有 unresolved（旧条收不掉，得让新条目顶上去）；② 撤掉的旧条最像的候选分数不低
    # （说明上游只是换了说法，那段新文案值得翻译），否则纯撤条就够了，不白烧接口配额。
    needs_adds = bool(plan["unresolved"]) or any(d.get("score", 0.0) >= 0.5 for d in plan["drop_info"])
    adds, _meta = collect_adds(entry, taken, max_adds) if needs_adds else ([], [])
    new_keys = {add["key"] for add in adds} | set(cfg["data"]["replacements"])
    notes = [f"重锚 {f['old']!r} -> {f['new']!r}" for f in plan["fixes"]]
    drops = list(plan["drops"])
    still: list[dict] = []
    for item in plan["unresolved"]:
        if item.get("new") in new_keys:
            drops.append(item["old"])
            notes.append(f"撤条 {item['old']!r}（新文案 {item['new']!r} 已补译接管）")
        else:
            still.append(item)
    notes += [f"撤条 {old!r}" for old in plan["drops"]]
    patch = {"fixes": plan["fixes"], "drops": drops, "adds": adds}
    return patch, notes, still


def llm_patch(entry: dict, base_url: str, api_key: str, model: str, timeout: int) -> dict:
    reply = i18n_llm.call_llm(base_url, api_key, model, i18n_llm.build_user_prompt(entry), timeout)
    return i18n_llm.parse_patch(reply)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=".")
    ap.add_argument("--source", required=True, help="上游源码目录")
    ap.add_argument("--cli", required=True, help="opencode-cli 可执行文件")
    ap.add_argument("--engine", default="auto", choices=["auto", "heur", "llm"],
                    help="auto=先 heur，修不动的文件再试 LLM（需密钥）；heur=纯确定性免费")
    ap.add_argument("--max-rounds", type=int, default=3)
    ap.add_argument("--max-files", type=int, default=6, help="每轮最多处理几个文件")
    ap.add_argument("--timeout", type=int, default=180)
    ap.add_argument("--no-adds", action="store_true",
                    help="关闭免费补译（默认开启：上游重写整句时靠它接管被撤掉的旧条目）")
    args = ap.parse_args()
    allow_adds = not args.no_adds

    api_key = os.environ.get("AUTOTRANSLATE_API_KEY", "").strip()
    base_url = os.environ.get("AUTOTRANSLATE_BASE_URL", "https://api.deepseek.com").strip()
    model = os.environ.get("AUTOTRANSLATE_MODEL", "deepseek-chat").strip()
    llm_ready = bool(api_key) and args.engine in ("auto", "llm")
    if args.engine == "llm" and not api_key:
        log("--engine llm 需要 AUTOTRANSLATE_API_KEY，回退到 heur")
        llm_ready = False

    repo, source = Path(args.repo).resolve(), Path(args.source).resolve()
    ok, summary = A.run_gate(args.cli, source, repo)
    log(f"当前门禁：{summary or '（无输出）'} -> {'通过' if ok else '未通过'}")
    if ok:
        return 0

    base = A.asset_dir(repo, source)
    log(f"词表目录：{base}；引擎 {'heur+llm' if llm_ready else 'heur（免费/离线）'}；"
        f"补译 {'开' if allow_adds else '关'}")
    touched: set[Path] = set()
    renames_by_rule: dict[str, list[tuple[str, str]]] = {}
    added_by_rule: dict[str, list[tuple[str, str, str]]] = {}
    unresolved: list[dict] = []
    taken: set[str] = set()
    added_total = 0

    for round_no in range(1, args.max_rounds + 1):
        configs = A.load_configs(base)
        pending = A.compute_misses(configs, source)
        if not pending:
            log(f"第 {round_no} 轮：词表已全部命中，交给门禁复核")
            break
        pending.sort(key=lambda e: -len(e["missing"]))
        log(f"第 {round_no} 轮：{len(pending)} 个文件失配，本轮处理 {min(len(pending), args.max_files)} 个")
        for entry in pending[:args.max_files]:
            cfg, rel = entry["cfg"], None
            before = cfg["path"].read_text(encoding="utf-8")
            budget = max(0, min(MAX_ADDS_PER_FILE, MAX_ADDS_TOTAL - added_total)) if allow_adds else 0
            try:
                patch, notes, left = heur_patch(entry, taken, budget)
            except Exception as exc:  # noqa: BLE001 - 单文件失败不影响其它文件
                log(f"  {cfg['file']}: 确定性引擎异常（{exc}），跳过")
                continue
            if left and llm_ready:
                log(f"  {cfg['file']}: heur 仍有 {len(left)} 条 unresolved，交给 LLM 兜底")
                try:
                    extra = llm_patch(entry, base_url, api_key, model, args.timeout)
                    patch["fixes"] += extra.get("fixes") or []
                    patch["drops"] += extra.get("drops") or []
                    if allow_adds:
                        patch["adds"] += extra.get("adds") or []
                except (urllib.error.URLError, TimeoutError, ValueError, KeyError) as exc:
                    log(f"  {cfg['file']}: LLM 兜底失败（{exc}），保留 heur 结果")
            for item in left:
                unresolved.append({"file": cfg["file"], **item})
            if not patch["fixes"] and not patch["drops"] and not patch["adds"]:
                log(f"  {cfg['file']}: 无可执行改动（{len(entry['missing'])} 条失配需要人工）")
                continue
            rules, apply_notes, renames = A.apply_patch(entry, patch, max_adds=budget)
            notes = apply_notes or notes
            if renames:
                rel = cfg["path"].relative_to(base).as_posix()
                renames_by_rule.setdefault(rel, []).extend(renames)
            if allow_adds and patch.get("adds"):
                added_total += len(patch["adds"])
                rel = rel or cfg["path"].relative_to(base).as_posix()
                added_by_rule.setdefault(rel, []).extend(
                    (a["key"], cfg["file"], "free-translate") for a in patch["adds"])
            A.write_config(cfg, rules)
            touched.add(cfg["path"])
            log(f"  {cfg['file']}: {'; '.join(notes[:6])}" + (" …" if len(notes) > 6 else ""))
            still = A.compute_misses([{**cfg, "data": cfg["data"]}], source)
            if still and len(still[0]["missing"]) >= len(entry["missing"]):
                cfg["path"].write_text(before, encoding="utf-8")
                touched.discard(cfg["path"])
                rel = cfg["path"].relative_to(base).as_posix()
                renames_by_rule.pop(rel, None)
                added_by_rule.pop(rel, None)
                log(f"  {cfg['file']}: 没修好（{len(entry['missing'])} -> "
                    f"{len(still[0]['missing'])}），回滚该文件")
            else:
                log(f"  {cfg['file']}: 失配 {len(entry['missing'])} -> "
                    f"{len(still[0]['missing']) if still else 0}")
        if A.run_gate(args.cli, source, repo)[0]:
            break

    if touched and base.name == A.V1_ASSETS:
        freeze = A.sync_v1_freeze(repo, A.load_configs(base))
        if freeze:
            touched.add(freeze)
        manifest = A.sync_v2_manifest(repo, renames_by_rule, added_by_rule)
        if manifest:
            touched.add(manifest)

    ok, summary = A.run_gate(args.cli, source, repo)
    log(f"结束：{summary or '（无输出）'} -> {'通过' if ok else '未通过'}；改动文件 {len(touched)} 个")
    for item in unresolved[:12]:
        log(f"UNRESOLVED {item['file']} {item['old']!r} best={item.get('score')} second={item.get('second')}")
    for path in sorted(touched):
        print(f"CHANGED {path}", flush=True)
    print(f"UNRESOLVED_COUNT {len(unresolved)}", flush=True)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
