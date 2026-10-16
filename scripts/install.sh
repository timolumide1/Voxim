#!/usr/bin/env bash
# One-time install: a private Python 3.13 environment with the `voxim` command.
# Usage: bash install.sh [--screen]     (--screen also installs a browser for website demos)
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOME_DIR="${VOXIM_HOME:-$HOME/.voxim}"
VENV="$HOME_DIR/venv"
mkdir -p "$HOME_DIR"

if ! command -v uv >/dev/null 2>&1; then
  if [ -x "$HOME/.local/bin/uv" ]; then export PATH="$HOME/.local/bin:$PATH"
  elif command -v pip3 >/dev/null 2>&1 && pip3 install --user -q uv 2>/dev/null; then export PATH="$HOME/.local/bin:$PATH"
  elif command -v pip3 >/dev/null 2>&1 && pip3 install --user -q --break-system-packages uv 2>/dev/null; then export PATH="$HOME/.local/bin:$PATH"
  else curl -LsSf https://astral.sh/uv/install.sh | sh; export PATH="$HOME/.local/bin:$PATH"
  fi
fi

[ -x "$VENV/bin/python" ] || uv venv -q --python 3.13 "$VENV"
uv pip install -q --python "$VENV/bin/python" --reinstall-package voxim "$HERE"
[ "${1:-}" = "--screen" ] && uv pip install -q --python "$VENV/bin/python" playwright
"$VENV/bin/voxim" setup ${1:-}
echo
echo "Installed. The command is: $VENV/bin/voxim"
