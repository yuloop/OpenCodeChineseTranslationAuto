#!/usr/bin/env bun
/**
 * 把汉化词表真实 apply 到上游源码后，用 bun 的 TSX 转译器逐个校验被改动的文件。
 *
 * 为什么需要：门禁只按「锚点是否是源码子串」算匹配率，它不校验语法。如果重锚选错了
 * 片段（例如把整行 `title: "x",` 当锚点），替换后可能丢掉代码结构，门禁照样 100%，
 * 但构建会炸。这里在提交前补一道「改动文件还能不能解析」的兜底。
 *
 * 用法: bun scripts/check_applied_syntax.mjs <上游源码目录> [--limit N]
 */
import { readFileSync, existsSync } from "node:fs";
import { execFileSync } from "node:child_process";

const dir = process.argv[2];
if (!dir || !existsSync(dir)) {
  console.error(`[syntax] 源码目录不存在: ${dir}`);
  process.exit(2);
}

const exts = /\.(tsx?|jsx?|mts|cts)$/;
const changed = execFileSync("git", ["-C", dir, "status", "--porcelain"], { encoding: "utf-8" })
  .split("\n")
  .filter((line) => line.trim().length > 3)
  .map((line) => line.slice(3).trim())
  .filter((path) => exts.test(path));

if (changed.length === 0) {
  console.log("[syntax] 没有需要校验的源码文件（词表可能没动到 TSX）");
  process.exit(0);
}

const transpiler = new Bun.Transpiler({ loader: "tsx" });
const failures = [];
for (const rel of changed) {
  const file = `${dir}/${rel}`;
  try {
    transpiler.transformSync(readFileSync(file, "utf-8"));
  } catch (error) {
    failures.push({ rel, error: String(error).split("\n").slice(0, 3).join(" | ") });
  }
}

if (failures.length > 0) {
  console.error(`[syntax] ${failures.length}/${changed.length} 个改动文件语法不合法：`);
  for (const item of failures.slice(0, 10)) console.error(`  ${item.rel}: ${item.error}`);
  process.exit(1);
}
console.log(`[syntax] 改动文件 ${changed.length} 个，语法全部通过`);
