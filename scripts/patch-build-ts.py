#!/usr/bin/env python3
"""Teach OpenCode's build script to compile one requested cross-platform target."""

from pathlib import Path
import sys


MARKER = "// [opencode-i18n] OPENCODE_BUILD_TARGET support"
TARGETS_DECLARATION = "const targets = singleFlag\n  ?"
BUILD_START = "await $`rm -rf dist`"


def patch(path: Path) -> None:
    content = path.read_text(encoding="utf-8")
    if MARKER in content:
        print(f"Build script already patched: {path}")
        return

    if TARGETS_DECLARATION not in content:
        raise RuntimeError("OpenCode build target declaration changed upstream")
    if BUILD_START not in content:
        raise RuntimeError("OpenCode build start marker changed upstream")

    replacement = f"""{MARKER}
const requestedTarget = process.env.OPENCODE_BUILD_TARGET
const targets = requestedTarget
  ? allTargets.filter((item) => {{
      const os = item.os === "win32" ? "windows" : item.os
      const target = `${{os}}-${{item.arch}}`
      return target === requestedTarget && item.avx2 !== false && item.abi === undefined
    }})
  : singleFlag
  ?"""
    content = content.replace(TARGETS_DECLARATION, replacement, 1)

    guard = """if (requestedTarget && targets.length !== 1) {
  throw new Error(`Unsupported or ambiguous OPENCODE_BUILD_TARGET: ${requestedTarget}`)
}

"""
    content = content.replace(BUILD_START, guard + BUILD_START, 1)
    path.write_text(content, encoding="utf-8")
    print(f"Patched build.ts for a single cross-platform target: {path}")


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("usage: patch-build-ts.py <path-to-build.ts>")

    path = Path(sys.argv[1])
    if not path.is_file():
        raise SystemExit(f"build script not found: {path}")
    patch(path)


if __name__ == "__main__":
    main()
