#!/usr/bin/env python3
"""免费/开源翻译后端（无需 API key）。

按顺序尝试：MyMemory → Lingva → Google gtx → LibreTranslate 公共实例。
纯标准库；带磁盘缓存（跨轮复用，省免费额度）、分片、重试与引擎回退。

用法：
    python3 scripts/free_translate.py --text "Hello world"
    python3 scripts/free_translate.py --text "Hello" --engine mymemory --no-cache
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ENGINE_ORDER = ("mymemory", "lingva", "google_gtx", "libretranslate")

# 公共 LibreTranslate 实例大多要 key 或已关站，这里只留可用的；用环境变量覆盖。
LIBRETRANSLATE_URLS = [u for u in os.environ.get("I18N_LIBRETRANSLATE_URLS", "").split(",") if u.strip()]

MYMEMORY_MAX = 480  # 免费接口单次 q 上限 500 字节
TIMEOUT = 20
USER_AGENT = "opencode-cn-i18n/1.0 (+https://github.com/yuloop/OpenCodeChineseTranslationAuto)"


def log(msg: str) -> None:
    print(f"[translate] {msg}", flush=True)


def cache_dir() -> Path:
    path = Path(os.environ.get("I18N_TRANSLATE_CACHE", Path.home() / ".cache" / "opencode-cn-i18n"))
    path.mkdir(parents=True, exist_ok=True)
    return path


def _cache_key(text: str, source: str, target: str) -> str:
    return hashlib.sha256(f"{source}\x00{target}\x00{text}".encode()).hexdigest()[:32]


def _cache_read(key: str) -> str | None:
    try:
        return json.loads((cache_dir() / f"{key}.json").read_text(encoding="utf-8"))["text"]
    except (OSError, ValueError, KeyError):
        return None


def _cache_write(key: str, text: str, engine: str) -> None:
    try:
        (cache_dir() / f"{key}.json").write_text(
            json.dumps({"text": text, "engine": engine}, ensure_ascii=False), encoding="utf-8"
        )
    except OSError:
        pass


def _http(url: str, data: bytes | None = None, headers: dict | None = None) -> str:
    req = urllib.request.Request(url, data=data, headers={"User-Agent": USER_AGENT, **(headers or {})})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:  # noqa: S310 - 固定 https 目标
        return resp.read().decode("utf-8", "replace")


def _has_cjk(text: str) -> bool:
    return any("\u4e00" <= ch <= "\u9fff" for ch in text)


def _looks_translated(src: str, out: str) -> bool:
    """英文原文翻成中文时必须出现汉字；否则视为该引擎未翻译（Lingva/gtx 常见）。"""
    out = (out or "").strip()
    if not out:
        return False
    if _has_cjk(src):
        return True
    return _has_cjk(out)


def _chunks(text: str, limit: int) -> list[str]:
    """按句子边界切片，保证每片 UTF-8 字节数 ≤ limit；超长单句按字符硬切（不丢内容）。"""
    def hard_split(piece: str) -> list[str]:
        parts, buf = [], ""
        for ch in piece:
            if len((buf + ch).encode("utf-8")) > limit:
                parts.append(buf)
                buf = ch
            else:
                buf += ch
        if buf:
            parts.append(buf)
        return parts

    if len(text.encode("utf-8")) <= limit:
        return [text]
    parts: list[str] = []
    buf = ""
    for piece in re.split(r"(?<=[.!?;:])\s+", text):
        if not piece:
            continue
        if len((buf + " " + piece).encode("utf-8")) <= limit:
            buf = f"{buf} {piece}".strip()
            continue
        if buf:
            parts.append(buf)
            buf = ""
        pieces = hard_split(piece)
        parts.extend(pieces[:-1])
        buf = pieces[-1]
    if buf:
        parts.append(buf)
    return [part for part in parts if part]


def _mymemory(text: str, source: str, target: str) -> str:
    out = []
    for chunk in _chunks(text, MYMEMORY_MAX):
        url = "https://api.mymemory.translated.net/get?" + urllib.parse.urlencode(
            {"q": chunk, "langpair": f"{source}|{target}"}
        )
        payload = json.loads(_http(url))
        if payload.get("quotaFinished"):
            raise RuntimeError("mymemory 配额用尽")
        status = payload.get("responseStatus")
        if status not in (200, "200"):
            raise RuntimeError(f"mymemory 响应异常: {status} {payload.get('responseDetails')}")
        piece = (payload.get("responseData") or {}).get("translatedText") or ""
        if not piece.strip():
            raise RuntimeError("mymemory 返回空译文")
        out.append(piece.strip())
    return "".join(out)


def _lingva(text: str, source: str, target: str) -> str:
    url = f"https://lingva.ml/api/v1/{source}/{target.split('-')[0]}/{urllib.parse.quote(text, safe='')}"
    payload = json.loads(_http(url))
    return (payload.get("translation") or "").strip()


def _google_gtx(text: str, source: str, target: str) -> str:
    url = "https://translate.googleapis.com/translate_a/single?" + urllib.parse.urlencode(
        {"client": "gtx", "sl": source, "tl": target, "dt": "t", "q": text}
    )
    body = _http(url)
    if body.lstrip().startswith("<"):
        raise RuntimeError("gtx 返回验证页（被限流）")
    payload = json.loads(body)
    return "".join(seg[0] for seg in payload[0] if seg and seg[0]).strip()


def _libretranslate(text: str, source: str, target: str) -> str:
    if not LIBRETRANSLATE_URLS:
        raise RuntimeError("未配置 I18N_LIBRETRANSLATE_URLS")
    last: Exception | None = None
    for base in LIBRETRANSLATE_URLS:
        try:
            data = json.dumps(
                {"q": text, "source": source, "target": target.split("-")[0], "format": "text"}
            ).encode()
            payload = json.loads(_http(base.strip().rstrip("/") + "/translate", data, {"Content-Type": "application/json"}))
            if payload.get("translatedText"):
                return payload["translatedText"].strip()
            raise RuntimeError(payload.get("error") or "空译文")
        except Exception as exc:  # noqa: BLE001 - 逐实例回退
            last = exc
    raise RuntimeError(f"libretranslate 全部实例失败: {last}")


ENGINES = {
    "mymemory": _mymemory,
    "lingva": _lingva,
    "google_gtx": _google_gtx,
    "libretranslate": _libretranslate,
}


def translate(
    text: str,
    source: str = "en",
    target: str = "zh-CN",
    engines: tuple[str, ...] = ENGINE_ORDER,
    use_cache: bool = True,
    retries: int = 2,
) -> tuple[str, str]:
    """返回 (译文, 引擎名)；所有引擎都失败时抛 RuntimeError。"""
    text = (text or "").strip()
    if not text:
        return "", "identity"
    key = _cache_key(text, source, target)
    if use_cache:
        cached = _cache_read(key)
        if cached:
            return cached, "cache"

    errors: list[str] = []
    for engine in engines:
        fn = ENGINES.get(engine)
        if fn is None:
            continue
        for attempt in range(1, retries + 1):
            try:
                out = fn(text, source, target)
                if not _looks_translated(text, out):
                    raise RuntimeError(f"译文未变化/无汉字: {out[:40]!r}")
                if use_cache:
                    _cache_write(key, out, engine)
                return out, engine
            except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, RuntimeError, ValueError) as exc:
                errors.append(f"{engine}#{attempt}: {exc}")
                if attempt < retries:
                    time.sleep(1.5 * attempt)
    raise RuntimeError("所有免费翻译引擎都失败：" + "; ".join(errors[-6:]))


def self_test() -> int:
    """离线自测：不联网，只校验分片与「假成功」拦截逻辑（CI 用）。"""
    assert _looks_translated("Rename session", "重命名会话")
    assert not _looks_translated("Rename session", "Rename session")
    assert not _looks_translated("Rename session", "")
    chunks = _chunks("a" * 1000 + " " + "b" * 200, MYMEMORY_MAX)
    assert all(len(c.encode("utf-8")) <= MYMEMORY_MAX for c in chunks), [len(c) for c in chunks]
    assert sum(c.count("a") for c in chunks) == 1000
    assert _cache_key("x", "en", "zh-CN") == _cache_key("x", "en", "zh-CN")
    assert len(_cache_key("x", "en", "zh-CN")) == 32
    log("self-test ok")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="免费翻译后端自测")
    ap.add_argument("--self-test", action="store_true", help="离线自测（不联网）")
    ap.add_argument("--text")
    ap.add_argument("--source", default="en")
    ap.add_argument("--target", default="zh-CN")
    ap.add_argument("--engine", action="append", choices=list(ENGINES), help="限定引擎（可多次）")
    ap.add_argument("--no-cache", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        return self_test()
    if not args.text:
        ap.error("需要 --text 或 --self-test")
    engines = tuple(args.engine) if args.engine else ENGINE_ORDER
    try:
        out, engine = translate(args.text, args.source, args.target, engines, not args.no_cache)
    except RuntimeError as exc:
        log(f"失败: {exc}")
        return 1
    log(f"{engine}: {args.text!r} -> {out!r}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
