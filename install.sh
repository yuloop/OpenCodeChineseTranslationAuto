#!/usr/bin/env bash
set -euo pipefail

REPO="${OPENCODE_I18N_REPO:-yuloop/OpenCodeChineseTranslationAuto}"
VERSION=""
PREVIEW=""

while (($#)); do
  case "$1" in
    --version)
      VERSION="${2:?--version requires a value}"
      shift 2
      ;;
    --version=*)
      VERSION="${1#*=}"
      shift
      ;;
    --preview)
      PREVIEW=1
      shift
      ;;
    *)
      echo "Unknown argument: $1" >&2
      exit 2
      ;;
  esac
done

OS_RAW="$(uname -s)"
ARCH_RAW="$(uname -m)"
case "$OS_RAW" in
  Linux) OS="linux" ;;
  *)
    echo "Current automatic releases support Linux x64 only. Detected: $OS_RAW" >&2
    exit 1
    ;;
esac
case "$ARCH_RAW" in
  x86_64|amd64) ARCH="amd64" ;;
  *)
    echo "Current automatic releases support x86_64 only. Detected: $ARCH_RAW" >&2
    exit 1
    ;;
esac

# 解析版本：--preview 从 releases 列表找最新 -cn-nightly 预览版（prerelease==true）；
# --version 与 --preview 同时给出时：--version 指定的 tag 优先，但按预览版方式安装
resolve_preview_tag() {
  if command -v curl >/dev/null 2>&1; then
    curl -fsSL -H 'Accept: application/vnd.github+json' \
      -H 'User-Agent: opencode-i18n-installer' \
      "https://api.github.com/repos/$REPO/releases?per_page=10"
  else
    wget -qO- --header='Accept: application/vnd.github+json' \
      --header='User-Agent: opencode-i18n-installer' \
      "https://api.github.com/repos/$REPO/releases?per_page=10"
  fi
}

if [[ -n "$PREVIEW" ]]; then
  if [[ -n "$VERSION" ]]; then
    echo "同时指定 --preview 与 --version：按 --version 的 tag（$VERSION）走预览版安装。"
  else
    echo "正在查询最新预览版..."
    VERSION="$(resolve_preview_tag | sed 's/},{/}\n{/g' | awk '
      /"tag_name": *"/ && /"prerelease": *true/ {
        tag = $0
        sub(/.*"tag_name": *"/, "", tag)
        sub(/".*/, "", tag)
        if (tag ~ /-cn-nightly/) { print tag; exit }
      }
    ' || true)"
    if [[ -z "$VERSION" ]]; then
      echo "Unable to resolve the latest preview release tag." >&2
      exit 1
    fi
  fi
elif [[ -z "$VERSION" ]]; then
  if command -v curl >/dev/null 2>&1; then
    VERSION="$(curl -fsSL -H 'Accept: application/vnd.github+json' \
      -H 'User-Agent: opencode-i18n-installer' \
      "https://api.github.com/repos/$REPO/releases/latest" |
      sed -n 's/.*"tag_name":[[:space:]]*"\([^"]*\)".*/\1/p' | head -1)"
  elif command -v wget >/dev/null 2>&1; then
    VERSION="$(wget -qO- --header='Accept: application/vnd.github+json' \
      --header='User-Agent: opencode-i18n-installer' \
      "https://api.github.com/repos/$REPO/releases/latest" |
      sed -n 's/.*"tag_name":[[:space:]]*"\([^"]*\)".*/\1/p' | head -1)"
  else
    echo "curl or wget is required." >&2
    exit 1
  fi
fi

if [[ -z "$VERSION" ]]; then
  echo "Unable to resolve the latest release tag." >&2
  exit 1
fi

if [[ -n "$PREVIEW" ]]; then
  # 预览版：直接下载 TUI 本体 zip（不走管理工具），装到独立目录，与稳定版互不覆盖
  ASSET="opencode-zh-CN-${VERSION}-linux-x64.zip"
  INSTALL_DIR="$HOME/.opencode-i18n-preview"
  BIN_DIR="$INSTALL_DIR/bin"
  TARGET="$BIN_DIR/opencode"
else
  ASSET="opencode-cli-$OS-$ARCH"
  INSTALL_DIR="$HOME/.opencode-i18n"
  BIN_DIR="$INSTALL_DIR/bin"
  TARGET="$BIN_DIR/opencode-cli"
fi
BASE_URL="https://github.com/$REPO/releases/download/$VERSION"
TMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TMP_DIR"' EXIT

download() {
  local url="$1"
  local output="$2"
  if command -v curl >/dev/null 2>&1; then
    curl -fL --retry 3 --output "$output" "$url"
  else
    wget -O "$output" "$url"
  fi
}

echo "Downloading $REPO $VERSION..."
download "$BASE_URL/$ASSET" "$TMP_DIR/$ASSET"
download "$BASE_URL/SHA256SUMS" "$TMP_DIR/SHA256SUMS"

if [[ -n "$PREVIEW" ]]; then
  # 临时 SUMS 只保留本次要安装的 zip 文件行（release 内还有其它平台压缩包）
  awk -v name="$ASSET" '$2 == name || $2 == "*" name { print }' \
    "$TMP_DIR/SHA256SUMS" >"$TMP_DIR/SHA256SUMS.preview"
  if [[ ! -s "$TMP_DIR/SHA256SUMS.preview" ]]; then
    echo "SHA256SUMS does not contain $ASSET" >&2
    exit 1
  fi
  if command -v sha256sum >/dev/null 2>&1; then
    (cd "$TMP_DIR" && sha256sum -c SHA256SUMS.preview) || {
      echo "SHA-256 verification failed." >&2
      exit 1
    }
  elif command -v shasum >/dev/null 2>&1; then
    (cd "$TMP_DIR" && shasum -a 256 -c SHA256SUMS.preview) || {
      echo "SHA-256 verification failed." >&2
      exit 1
    }
  else
    echo "sha256sum or shasum is required." >&2
    exit 1
  fi
else
  EXPECTED="$(awk -v name="$ASSET" '$2 == name || $2 == "*" name { print $1; exit }' "$TMP_DIR/SHA256SUMS")"
  if [[ ! "$EXPECTED" =~ ^[0-9a-fA-F]{64}$ ]]; then
    echo "SHA256SUMS does not contain $ASSET" >&2
    exit 1
  fi

  if command -v sha256sum >/dev/null 2>&1; then
    ACTUAL="$(sha256sum "$TMP_DIR/$ASSET" | awk '{print $1}')"
  elif command -v shasum >/dev/null 2>&1; then
    ACTUAL="$(shasum -a 256 "$TMP_DIR/$ASSET" | awk '{print $1}')"
  else
    echo "sha256sum or shasum is required." >&2
    exit 1
  fi

  if [[ "${ACTUAL,,}" != "${EXPECTED,,}" ]]; then
    echo "SHA-256 verification failed." >&2
    exit 1
  fi
fi

mkdir -p "$BIN_DIR"
rm -f "$TARGET.old"
if [[ -f "$TARGET" ]]; then
  mv "$TARGET" "$TARGET.old"
fi
if [[ -n "$PREVIEW" ]]; then
  if command -v unzip >/dev/null 2>&1; then
    unzip -qo "$TMP_DIR/$ASSET" -d "$TMP_DIR/extracted"
  elif command -v python3 >/dev/null 2>&1; then
    python3 -m zipfile -e "$TMP_DIR/$ASSET" "$TMP_DIR/extracted"
  else
    echo "unzip or python3 is required." >&2
    exit 1
  fi
  install -m 0755 "$TMP_DIR/extracted/opencode" "$TARGET"
else
  install -m 0755 "$TMP_DIR/$ASSET" "$TARGET"
fi

case "$(basename "${SHELL:-bash}")" in
  zsh) RC_FILE="$HOME/.zshrc" ;;
  bash) RC_FILE="$HOME/.bashrc" ;;
  *) RC_FILE="$HOME/.profile" ;;
esac

if [[ -n "$PREVIEW" ]]; then
  MARK="# OpenCode Chinese Preview"
else
  MARK="# OpenCode Chinese CLI"
fi
PATH_LINE="export PATH=\"$BIN_DIR:\$PATH\""
if [[ ":$PATH:" != *":$BIN_DIR:"* ]] && ! grep -Fqx "$PATH_LINE" "$RC_FILE" 2>/dev/null; then
  printf '\n%s\n%s\n' "$MARK" "$PATH_LINE" >>"$RC_FILE"
fi

echo "Installed: $TARGET"
if [[ -n "$PREVIEW" ]]; then
  echo "Restart the terminal, then run: opencode"
  echo "预览版与正式版安装目录隔离，重跑同一命令即更新。"
else
  echo "Restart the terminal, then run: opencode-cli"
fi
