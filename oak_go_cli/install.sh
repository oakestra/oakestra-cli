#!/bin/bash
set -e

# This script installs the oak CLI tool.
# It is intended to be run from a one-liner command:
#   curl -sSL https://raw.githubusercontent.com/oakestra/oakestra-cli/main/oak_go_cli/install.sh | bash

REPO="oakestra/oakestra-cli"
BASE_URL="https://github.com/$REPO/releases/download"

fail() {
  echo -e "Error: $1" >&2
  exit 1
}

command_exists() {
  command -v "$1" >/dev/null 2>&1
}

# Determine the operating system.
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
  OS="linux"
elif [[ "$OSTYPE" == "darwin"* ]]; then
  OS="darwin"
else
  fail "Unsupported operating system: $OSTYPE. On Windows use install.ps1 instead."
fi

# Determine the architecture.
ARCH=$(uname -m)
case $ARCH in
  x86_64)  ARCH="amd64" ;;
  arm64 | aarch64) ARCH="arm64" ;;
  *) fail "Unsupported architecture: $ARCH" ;;
esac

# Get the latest release tag from the GitHub API.
LATEST_TAG=$(curl -s "https://api.github.com/repos/$REPO/releases/latest" | grep '"tag_name":' | sed -E 's/.*"([^"]+)".*/\1/')
if [ -z "$LATEST_TAG" ]; then
  fail "Could not determine the latest release version."
fi

# Construct the download URL.
TARBALL="oak_cli_${OS}_${ARCH}.tar.gz"
DOWNLOAD_URL="$BASE_URL/$LATEST_TAG/$TARBALL"

# Create a temporary directory for the download.
TMP_DIR=$(mktemp -d)
trap 'rm -rf "$TMP_DIR"' EXIT

# Download and extract the tarball.
echo "Downloading oak CLI $LATEST_TAG for ${OS}/${ARCH} …"
curl -fL "$DOWNLOAD_URL" | tar -xz -C "$TMP_DIR"

# Install the binary.
echo "Installing oak to /usr/local/bin/oak"
if [ -w "/usr/local/bin" ]; then
  mv "$TMP_DIR/oak" "/usr/local/bin/oak"
else
  sudo mv "$TMP_DIR/oak" "/usr/local/bin/oak"
fi

# Install bundled SLA templates to ~/oak_cli/SLAs/ (will not overwrite existing files).
SLA_DIR="$HOME/oak_cli/SLAs"
mkdir -p "$SLA_DIR"
if [ -d "$TMP_DIR/SLAs" ]; then
  cp -rn "$TMP_DIR/SLAs/." "$SLA_DIR/"
  echo "SLA templates installed to $SLA_DIR"
fi

# Shell completions — best-effort, never fatal.
if command_exists zsh; then
  mkdir -p ~/.zsh/completions
  oak completion zsh > ~/.zsh/completions/_oak 2>/dev/null || true
  echo "zsh completions written to ~/.zsh/completions/_oak"
fi

if command_exists bash; then
  if [ -d "/etc/bash_completion.d" ]; then
    oak completion bash > /etc/bash_completion.d/oak 2>/dev/null || \
    sudo bash -c 'oak completion bash > /etc/bash_completion.d/oak' 2>/dev/null || true
    echo "bash completions written to /etc/bash_completion.d/oak"
  fi
fi

echo ""
echo "oak CLI $LATEST_TAG installed successfully."
echo "Run 'oak --help' to get started."
