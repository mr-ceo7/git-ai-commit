#!/usr/bin/env bash
# ==============================================================================
# git-ai-commit uninstaller
# Removes git-ai-commit and gh-ai-commit from ~/.local/bin
# ==============================================================================

set -e

TARGET_BIN="${HOME}/.local/bin/git-ai-commit"
GH_BIN="${HOME}/.local/bin/gh-ai-commit"

if [ -f "${TARGET_BIN}" ]; then
    rm -f "${TARGET_BIN}"
    echo "✓ Successfully removed ${TARGET_BIN}"
else
    echo "git-ai-commit binary not found at ${TARGET_BIN}"
fi

if [ -L "${GH_BIN}" ] || [ -f "${GH_BIN}" ]; then
    rm -f "${GH_BIN}"
    echo "✓ Removed GitHub CLI alias ${GH_BIN}"
fi

if command -v gh >/dev/null 2>&1; then
    gh alias delete ai-commit 2>/dev/null || true
    echo "✓ Removed gh ai-commit alias"
fi

echo ""
echo "Note: Configuration files in ~/.config/git-ai-commit were preserved."
echo "If you wish to remove your saved API keys as well, run:"
echo "  rm -rf ~/.config/git-ai-commit"
echo ""
