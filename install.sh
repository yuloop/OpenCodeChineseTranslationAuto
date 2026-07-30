#!/usr/bin/env bash
set -euo pipefail

REPO="${OPENCODE_I18N_REPO:-yuloop/OpenCodeChineseTranslationAuto}"
VERSION=""

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

if [[ -z "$VERSION" ]]; then
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

ASSET="opencode-cli-$OS-$ARCH"
BASE_URL="https://github.com/$REPO/releases/download/$VERSION"
INSTALL_DIR="$HOME/.opencode-i18n"
BIN_DIR="$INSTALL_DIR/bin"
TARGET="$BIN_DIR/opencode-cli"
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

mkdir -p "$BIN_DIR"
rm -f "$TARGET.old"
if [[ -f "$TARGET" ]]; then
  mv "$TARGET" "$TARGET.old"
fi
install -m 0755 "$TMP_DIR/$ASSET" "$TARGET"

case "$(basename "${SHELL:-bash}")" in
  zsh) RC_FILE="$HOME/.zshrc" ;;
  bash) RC_FILE="$HOME/.bashrc" ;;
  *) RC_FILE="$HOME/.profile" ;;
esac

PATH_LINE="export PATH=\"$BIN_DIR:\$PATH\""
if [[ ":$PATH:" != *":$BIN_DIR:"* ]] && ! grep -Fqx "$PATH_LINE" "$RC_FILE" 2>/dev/null; then
  printf '\n# OpenCode Chinese CLI\n%s\n' "$PATH_LINE" >>"$RC_FILE"
fi

echo "Installed: $TARGET"
echo "Restart the terminal, then run: opencode-cli"
