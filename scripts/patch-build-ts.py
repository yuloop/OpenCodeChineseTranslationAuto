#!/usr/bin/env python3
"""Teach OpenCode's build script to compile one requested cross-platform target.

V2 upstream already supports --target= and --outdir= natively; for V2 this script
is a no-op and simply returns success so callers (including CI) can keep invoking
it unconditionally.
"""

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
    if len(sys.argv) < 2:
        raise SystemExit("usage: patch-build-ts.py [--layout v1|v2] <path-to-build.ts>")

    layout = "v1"
    argv = sys.argv[1:]
    if argv[0] == "--layout":
        if len(sys.argv) < 4:
            raise SystemExit("usage: patch-build-ts.py --layout v1|v2 <path-to-build.ts>")
        layout = sys.argv[2].lower()
        argv = sys.argv[3:]

    if layout == "v2":
        print("V2 layout detected: build.ts already supports --target=/--outdir= natively; skipping patch")
        raise SystemExit(0)

    if len(argv) != 1:
        raise SystemExit("usage: patch-build-ts.py [--layout v1|v2] <path-to-build.ts>")

    path = Path(argv[0])
    if not path.is_file():
        raise SystemExit(f"build script not found: {path}")
    patch(path)


if __name__ == "__main__":
    main()
