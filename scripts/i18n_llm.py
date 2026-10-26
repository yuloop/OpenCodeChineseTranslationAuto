#!/usr/bin/env python3
"""可选的 LLM 补丁后端（OpenAI 兼容 chat/completions）。

默认工作流不用它（免费、确定性引擎已经够用）；只有配置了 AUTOTRANSLATE_API_KEY
且引擎选 auto/llm 时才会被调用，作为「确定性算法修不动」时的兜底。
"""

from __future__ import annotations

import json
import urllib.request

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
